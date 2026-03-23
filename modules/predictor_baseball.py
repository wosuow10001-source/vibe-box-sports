"""
야구 예측 모듈
- Negative Binomial Distribution
- 득점 범위: 2~8점
- 분산 큼 (포아송보다 정확)
"""

import numpy as np
from scipy.stats import nbinom, poisson
from pathlib import Path


class BaseballPredictor:
    def __init__(self):
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        
        # 야구 특성
        self.avg_runs = 4.5  # MLB 평균 득점
        self.dispersion = 1.5  # 분산 파라미터
    
    def predict_match(self, home_team, away_team, home_data, away_data,
                     weather, temperature, field_condition, match_importance,
                     rest_days_home, rest_days_away, injury_data=None, coaching_data=None,
                     lineup_home=None, lineup_away=None):
        """
        야구 예측: Negative Binomial
        
        특징:
        - 득점 낮지만 분산 큼
        - 포아송보다 정확
        - 투수 영향 매우 큼
        """
        
        # 라인업 기반 팀 데이터 보강
        if lineup_home:
            home_data = self._enhance_team_data_with_lineup(home_data, lineup_home)
        if lineup_away:
            away_data = self._enhance_team_data_with_lineup(away_data, lineup_away)
        
        # 공통 피처 수치화
        from modules.predictor_soccer import SoccerPredictor
        soccer_predictor = SoccerPredictor()
        
        form_score = soccer_predictor._analyze_form(home_data, away_data)
        home_advantage = soccer_predictor._calculate_home_advantage(home_data)
        player_condition = soccer_predictor._analyze_player_condition(
            home_data, away_data, rest_days_home, rest_days_away
        )
        
        # 야구는 전술 분석 불필요 (기본값 사용)
        tactical_score = {'home': 0.5, 'away': 0.5}
        
        weather_impact = soccer_predictor._analyze_weather_impact(
            weather, temperature, field_condition
        )
        rest_impact = soccer_predictor._analyze_rest_days(rest_days_home, rest_days_away)
        injury_impact = soccer_predictor._analyze_injury_impact(injury_data)
        coaching_impact = soccer_predictor._analyze_coaching_impact(coaching_data, home_data, away_data)
        
        # 야구 특화: 기대 득점 계산
        mu_home = self._calculate_expected_runs(
            home_data, away_data, True,
            form_score['home'], home_advantage, player_condition['home'],
            tactical_score['home'], weather_impact['home'], rest_impact['home'],
            injury_impact['home'], coaching_impact['home']
        )
        
        mu_away = self._calculate_expected_runs(
            away_data, home_data, False,
            form_score['away'], 0, player_condition['away'],
            tactical_score['away'], weather_impact['away'], rest_impact['away'],
            injury_impact['away'], coaching_impact['away']
        )
        
        # Negative Binomial 파라미터 계산
        r_home, p_home = self._mu_to_nb_params(mu_home)
        r_away, p_away = self._mu_to_nb_params(mu_away)
        
        # 스코어 분포 계산
        score_distribution = self._calculate_score_distribution(
            r_home, p_home, r_away, p_away
        )
        
        home_win_prob = score_distribution['home_win_prob']
        away_win_prob = score_distribution['away_win_prob']
        most_likely_score = score_distribution['most_likely_score']
        top_3_scores = score_distribution['top_3_scores']
        
        expected_score_home = most_likely_score[0]
        expected_score_away = most_likely_score[1]
        
        # 주요 영향 요인
        key_factors = soccer_predictor._identify_key_factors(
            form_score, home_advantage, player_condition,
            tactical_score, weather_impact, rest_impact, injury_impact, coaching_impact
        )
        
        # 신뢰도
        confidence = soccer_predictor._calculate_confidence(
            home_data, away_data, home_win_prob, away_win_prob, 0
        )
        
        return {
            'home_win_prob': home_win_prob,
            'draw_prob': 0.0,  # 야구는 무승부 없음 (연장)
            'away_win_prob': away_win_prob,
            'expected_score_home': expected_score_home,
            'expected_score_away': expected_score_away,
            'top_3_scores': top_3_scores,
            'mu_home': round(mu_home, 2),
            'mu_away': round(mu_away, 2),
            'key_factors': key_factors,
            'confidence': confidence,
            'detailed_scores': {
                'form': form_score,
                'home_advantage': home_advantage,
                'player_condition': player_condition,
                'tactical': tactical_score,
                'weather': weather_impact,
                'rest': rest_impact,
                'injury': injury_impact,
                'coaching': coaching_impact
            }
        }
    
    def _calculate_expected_runs(self, team_data, opponent_data, is_home,
                                form, home_advantage, player_condition, tactical,
                                weather, rest, injury, coaching):
        """야구 기대 득점 계산 (2~8 범위)"""
        
        # 기본 득점력
        team_runs = team_data.get('avg_goals', 4.5)
        opponent_runs_allowed = opponent_data.get('avg_conceded', 4.5)
        
        # 축구 점수 범위(0-5)를 야구 범위(2-8)로 변환
        if team_runs < 10:  # 축구 데이터로 판단
            # 0-5 범위를 2-8 범위로 선형 변환
            # 2.5골(평균) → 5점(평균)
            team_runs = 2.0 + (team_runs / 5.0) * 6.0
        
        if opponent_runs_allowed < 10:
            opponent_runs_allowed = 2.0 + (opponent_runs_allowed / 5.0) * 6.0
        
        base_runs = (team_runs * 0.6 + opponent_runs_allowed * 0.4)
        
        # 팩터 계산 (최근 폼 가중치 증가)
        form_factor = 0.60 + (form * 0.80)  # 폼 영향 80% (0.6 ~ 1.4 범위)
        home_factor = 1.0 + (home_advantage * 0.15 if is_home else 0)  # 홈 15%
        condition_factor = 0.80 + (player_condition * 0.40)  # 컨디션 40%
        tactical_factor = 0.85 + (tactical * 0.30)  # 투수 vs 타자 매치업 30%
        weather_factor = 0.90 + (weather * 0.20)  # 날씨 영향 20%
        rest_factor = 0.90 + (rest * 0.20)  # 휴식 20%
        injury_factor = 0.70 + (injury * 0.30)  # 투수 부상 영향 30%
        coaching_factor = 0.85 + (coaching * 0.30)  # 코칭 30%
        
        expected_runs = (
            base_runs *
            form_factor *
            home_factor *
            condition_factor *
            tactical_factor *
            weather_factor *
            rest_factor *
            injury_factor *
            coaching_factor
        )
        
        # 범위 제한 (1.5~10)
        return max(1.5, min(10.0, expected_runs))
    
    def _mu_to_nb_params(self, mu):
        """
        평균(μ)을 Negative Binomial 파라미터 (r, p)로 변환
        
        NB(r, p): mean = r(1-p)/p, variance = r(1-p)/p^2
        """
        # 분산 = μ + μ^2 / r (overdispersion)
        r = mu / self.dispersion
        p = r / (r + mu)
        
        return r, p
    
    def _calculate_score_distribution(self, r_home, p_home, r_away, p_away, max_runs=12):
        """Negative Binomial 기반 스코어 분포 계산"""
        
        home_win_prob = 0.0
        away_win_prob = 0.0
        tie_prob = 0.0  # 동점 확률 (연장전)
        
        score_probs = {}
        
        for home_runs in range(max_runs + 1):
            for away_runs in range(max_runs + 1):
                # Negative Binomial PMF
                prob_home = nbinom.pmf(home_runs, r_home, p_home)
                prob_away = nbinom.pmf(away_runs, r_away, p_away)
                
                prob = prob_home * prob_away
                score_probs[(home_runs, away_runs)] = prob
                
                if home_runs > away_runs:
                    home_win_prob += prob
                elif home_runs < away_runs:
                    away_win_prob += prob
                else:  # 동점
                    tie_prob += prob
        
        # 정규화
        total_prob = sum(score_probs.values())
        if total_prob > 0:
            score_probs = {k: v/total_prob for k, v in score_probs.items()}
            home_win_prob /= total_prob
            away_win_prob /= total_prob
            tie_prob /= total_prob
        
        # 야구는 연장전으로 승부 결정 → 동점 확률을 승률에 재분배
        # 홈 어드밴티지 고려 (연장전에서 홈팀이 약간 유리)
        home_advantage_in_extra = 0.52  # 연장전 홈팀 승률 52%
        
        home_win_prob += tie_prob * home_advantage_in_extra
        away_win_prob += tie_prob * (1 - home_advantage_in_extra)
        
        # Top 3 스코어 (동점 제외)
        non_tie_scores = {k: v for k, v in score_probs.items() if k[0] != k[1]}
        top_scores = sorted(non_tie_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 가장 가능성 높은 스코어 (동점 아닌 것 중)
        if top_scores:
            most_likely_score = top_scores[0][0]
        else:
            # 폴백: 전체에서 선택
            all_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)
            most_likely_score = all_scores[0][0]
        
        return {
            'home_win_prob': home_win_prob,
            'away_win_prob': away_win_prob,
            'most_likely_score': most_likely_score,
            'top_3_scores': [(score, prob) for score, prob in top_scores],
            'tie_prob_before_extra': tie_prob  # 디버깅용
        }

    
    def _enhance_team_data_with_lineup(self, team_data: dict, lineup: dict) -> dict:
        """
        라인업 정보로 팀 데이터 보강
        
        Args:
            team_data: 기존 팀 데이터
            lineup: 라인업 정보 (team_strength 포함)
        
        Returns:
            보강된 팀 데이터
        """
        enhanced_data = team_data.copy()
        
        team_strength = lineup.get('team_strength', {})
        
        # 라인업 기반 능력치로 업데이트
        if team_strength:
            # 공격력 반영 (avg_goals 조정)
            attack_rating = team_strength.get('attack_rating', 70)
            if 'avg_goals' in enhanced_data:
                # 능력치 70 기준, ±30% 조정
                adjustment = (attack_rating - 70) / 70 * 0.3
                enhanced_data['avg_goals'] *= (1 + adjustment)
            
            # 수비력 반영 (avg_conceded 조정)
            defense_rating = team_strength.get('defense_rating', 70)
            if 'avg_conceded' in enhanced_data:
                # 수비력 높으면 실점 감소
                adjustment = (defense_rating - 70) / 70 * 0.3
                enhanced_data['avg_conceded'] *= (1 - adjustment)
            
            # 종합 전력 저장
            enhanced_data['lineup_overall'] = team_strength.get('overall_rating', 70)
            enhanced_data['lineup_attack'] = attack_rating
            enhanced_data['lineup_defense'] = defense_rating
        
        # 전술 정보 저장
        enhanced_data['formation'] = lineup.get('formation', '기본')
        enhanced_data['tactic'] = lineup.get('tactic', '균형형')
        
        return enhanced_data

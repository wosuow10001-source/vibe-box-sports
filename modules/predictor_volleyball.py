"""
배구 예측 모듈
- Markov Chain (세트 기반)
- 세트 승률 → 경기 승률
- 랠리 길이 반영
"""

import numpy as np
from pathlib import Path


class VolleyballPredictor:
    def __init__(self):
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        
        # 배구 특성
        self.sets_to_win = 3  # 5세트 중 3세트 승
    
    def predict_match(self, home_team, away_team, home_data, away_data,
                     weather, temperature, field_condition, match_importance,
                     rest_days_home, rest_days_away, injury_data=None, coaching_data=None,
                     lineup_home=None, lineup_away=None):
        """
        배구 예측: Markov Chain
        
        특징:
        - 점수가 아니라 세트 기반
        - 흐름 영향 큼
        - 랠리 길이 중요
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
        tactical_score = soccer_predictor._analyze_tactical_fit(home_data, away_data)
        weather_impact = soccer_predictor._analyze_weather_impact(
            weather, temperature, field_condition
        )
        rest_impact = soccer_predictor._analyze_rest_days(rest_days_home, rest_days_away)
        injury_impact = soccer_predictor._analyze_injury_impact(injury_data)
        coaching_impact = soccer_predictor._analyze_coaching_impact(coaching_data, home_data, away_data)
        
        # 배구 특화: 세트 승률 계산
        set_win_prob_home = self._calculate_set_win_probability(
            home_data, away_data, True,
            form_score['home'], home_advantage, player_condition['home'],
            tactical_score['home'], weather_impact['home'], rest_impact['home'],
            injury_impact['home'], coaching_impact['home']
        )
        
        set_win_prob_away = 1 - set_win_prob_home
        
        # 세트 승률 → 경기 승률 (5세트 중 3세트 승)
        match_probs = self._calculate_match_probability(set_win_prob_home, set_win_prob_away)
        
        home_win_prob = match_probs['home_win']
        away_win_prob = match_probs['away_win']
        
        # 예상 세트 스코어
        expected_sets = self._calculate_expected_sets(set_win_prob_home, set_win_prob_away)
        expected_score_home = expected_sets['home']
        expected_score_away = expected_sets['away']
        
        # Top 3 세트 스코어
        top_3_scores = self._generate_top_set_scores(set_win_prob_home, set_win_prob_away)
        
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
            'draw_prob': 0.0,  # 배구는 무승부 없음
            'away_win_prob': away_win_prob,
            'expected_score_home': expected_score_home,
            'expected_score_away': expected_score_away,
            'top_3_scores': top_3_scores,
            'set_win_prob_home': round(set_win_prob_home, 3),
            'set_win_prob_away': round(set_win_prob_away, 3),
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
    
    def _calculate_set_win_probability(self, team_data, opponent_data, is_home,
                                       form, home_advantage, player_condition, tactical,
                                       weather, rest, injury, coaching):
        """세트 승률 계산"""
        
        # 기본 세트 승률
        team_set_winrate = team_data.get('recent_winrate', 0.5)
        opponent_set_winrate = opponent_data.get('recent_winrate', 0.5)
        
        base_prob = team_set_winrate / (team_set_winrate + opponent_set_winrate)
        
        # 팩터 계산 (최근 폼 가중치 증가)
        form_factor = 0.6 + (form * 0.8)  # 폼 영향 80% (0.6 ~ 1.4 범위)
        home_factor = 1.0 + (home_advantage * 0.15 if is_home else 0)
        condition_factor = 0.7 + (player_condition * 0.6)
        tactical_factor = 0.8 + (tactical * 0.4)
        weather_factor = 0.95 + (weather * 0.1)  # 실내 경기라 영향 적음
        rest_factor = 0.85 + (rest * 0.3)
        injury_factor = 0.7 + (injury * 0.3)
        coaching_factor = 0.8 + (coaching * 0.4)
        
        # 종합 팩터
        total_factor = (
            form_factor *
            home_factor *
            condition_factor *
            tactical_factor *
            weather_factor *
            rest_factor *
            injury_factor *
            coaching_factor
        )
        
        # 세트 승률 조정
        adjusted_prob = base_prob * total_factor
        
        # 정규화 (0.1 ~ 0.9)
        return max(0.1, min(0.9, adjusted_prob))
    
    def _calculate_match_probability(self, p_home, p_away):
        """
        세트 승률 → 경기 승률
        5세트 중 3세트 승 (3:0, 3:1, 3:2)
        
        정확한 이항 분포 계산:
        - 3:0 → P(홈 3연승)
        - 3:1 → P(4세트 중 처음 3세트에서 홈 2승, 마지막 홈 승)
        - 3:2 → P(5세트 중 처음 4세트에서 홈 2승, 마지막 홈 승)
        """
        
        home_win = 0.0
        away_win = 0.0
        
        # 홈팀 승리 경우의 수
        # 3:0 (홈 3연승)
        prob_3_0 = p_home ** 3
        home_win += prob_3_0
        
        # 3:1 (4세트 중 처음 3세트에서 홈 2승, 4번째 홈 승)
        prob_3_1 = self._binomial_coef(3, 2) * (p_home ** 2) * (p_away ** 1) * p_home
        home_win += prob_3_1
        
        # 3:2 (5세트 중 처음 4세트에서 홈 2승, 5번째 홈 승)
        prob_3_2 = self._binomial_coef(4, 2) * (p_home ** 2) * (p_away ** 2) * p_home
        home_win += prob_3_2
        
        # 원정팀 승리 경우의 수
        # 0:3 (원정 3연승)
        prob_0_3 = p_away ** 3
        away_win += prob_0_3
        
        # 1:3 (4세트 중 처음 3세트에서 원정 2승, 4번째 원정 승)
        prob_1_3 = self._binomial_coef(3, 2) * (p_away ** 2) * (p_home ** 1) * p_away
        away_win += prob_1_3
        
        # 2:3 (5세트 중 처음 4세트에서 원정 2승, 5번째 원정 승)
        prob_2_3 = self._binomial_coef(4, 2) * (p_away ** 2) * (p_home ** 2) * p_away
        away_win += prob_2_3
        
        # 정규화 (합이 1이 되도록)
        total = home_win + away_win
        if total > 0:
            home_win /= total
            away_win /= total
        
        return {
            'home_win': home_win,
            'away_win': away_win
        }
    
    def _calculate_expected_sets(self, p_home, p_away):
        """예상 세트 스코어"""
        
        # 가장 가능성 높은 스코어
        if p_home > 0.65:
            return {'home': 3, 'away': 0}
        elif p_home > 0.55:
            return {'home': 3, 'away': 1}
        elif p_home > 0.45:
            return {'home': 3, 'away': 2}
        elif p_home > 0.35:
            return {'home': 2, 'away': 3}
        elif p_home > 0.25:
            return {'home': 1, 'away': 3}
        else:
            return {'home': 0, 'away': 3}
    
    def _generate_top_set_scores(self, p_home, p_away):
        """Top 3 세트 스코어 생성"""
        
        scores = []
        
        # 가능한 세트 스코어 (3:0, 3:1, 3:2, 2:3, 1:3, 0:3)
        possible_scores = [
            (3, 0), (3, 1), (3, 2),
            (2, 3), (1, 3), (0, 3)
        ]
        
        for home_sets, away_sets in possible_scores:
            total_sets = home_sets + away_sets
            
            if home_sets == 3:
                prob = (
                    self._binomial_coef(total_sets - 1, home_sets - 1) *
                    (p_home ** home_sets) *
                    (p_away ** away_sets)
                )
            else:
                prob = (
                    self._binomial_coef(total_sets - 1, away_sets - 1) *
                    (p_away ** away_sets) *
                    (p_home ** home_sets)
                )
            
            scores.append(((home_sets, away_sets), prob))
        
        # 확률 높은 순으로 정렬
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:3]
    
    def _binomial_coef(self, n, k):
        """이항 계수 계산"""
        if k > n or k < 0:
            return 0
        if k == 0 or k == n:
            return 1
        
        from math import factorial
        return factorial(n) // (factorial(k) * factorial(n - k))

    
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

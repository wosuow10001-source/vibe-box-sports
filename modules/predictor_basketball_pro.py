"""
농구 예측 모듈 (프로 수준 - Possession × PPP 기반)

핵심 원리:
- X → Possession Model → PPP Model → Score Distribution → Win Probability
- Normal Distribution (정규분포)
- Market Calibration 지원
- 점수 범위: 70-150점 (자동 클리핑)
"""

import numpy as np
from scipy.stats import norm
from pathlib import Path
from typing import Dict, Tuple


class BasketballPredictorPro:
    """
    프로 수준 농구 예측 모델
    
    구조:
    1. Possession 계산 (경기 템포)
    2. PPP (Points Per Possession) 계산
    3. 상대 수비 반영
    4. 평균 점수 = Possession × PPP
    5. 분산 계산
    6. Normal Distribution으로 승률 계산
    """
    
    def __init__(self):
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        
        # 기본 파라미터
        self.base_possessions = 100  # NBA 평균 포제션
        self.base_ppp = 1.05  # NBA 평균 PPP
        self.base_std = 10  # 기본 표준편차
        
        # 점수 범위 제한
        self.min_score = 70
        self.max_score = 150
    
    def predict_match(self, home_team, away_team, home_data, away_data,
                     weather, temperature, field_condition, match_importance,
                     rest_days_home, rest_days_away, injury_data=None, coaching_data=None,
                     lineup_home=None, lineup_away=None):
        """
        농구 예측: Possession × PPP 모델
        
        Args:
            lineup_home: 홈팀 라인업 (선택)
            lineup_away: 원정팀 라인업 (선택)
        
        Returns:
            dict: 예측 결과
        """
        
        # 라인업 기반 팀 데이터 보강
        if lineup_home:
            home_data = self._enhance_team_data_with_lineup(home_data, lineup_home)
        if lineup_away:
            away_data = self._enhance_team_data_with_lineup(away_data, lineup_away)
        
        # Feature 추출
        X_home = self._extract_features(
            home_data, away_data, True, 
            rest_days_home, injury_data, coaching_data
        )
        X_away = self._extract_features(
            away_data, home_data, False,
            rest_days_away, injury_data, coaching_data
        )
        
        # 1. Possession 계산
        poss_home = self._predict_possessions(X_home)
        poss_away = self._predict_possessions(X_away)
        
        # 2. PPP 계산
        ppp_home = self._predict_ppp(X_home)
        ppp_away = self._predict_ppp(X_away)
        
        # 3. 상대 수비 반영
        ppp_home_adj = self._adjust_defense(ppp_home, X_away['def_rating'])
        ppp_away_adj = self._adjust_defense(ppp_away, X_home['def_rating'])
        
        # 4. 평균 점수 계산
        mean_home = poss_home * ppp_home_adj
        mean_away = poss_away * ppp_away_adj
        
        # 5. 분산 계산
        std_home = self._predict_std(X_home)
        std_away = self._predict_std(X_away)
        
        # 6. 승률 계산
        home_win_prob = self._win_probability(mean_home, mean_away, std_home, std_away)
        away_win_prob = 1 - home_win_prob
        
        # 7. 예상 스코어 (클리핑 적용)
        expected_score_home = int(np.clip(round(mean_home), self.min_score, self.max_score))
        expected_score_away = int(np.clip(round(mean_away), self.min_score, self.max_score))
        
        # 8. Top 3 스코어
        top_3_scores = self._generate_top_scores(mean_home, mean_away, std_home, std_away)
        
        # 9. 주요 영향 요인
        key_factors = self._identify_key_factors(X_home, X_away, poss_home, poss_away)
        
        # 10. 신뢰도
        confidence = self._calculate_confidence(home_win_prob, away_win_prob, std_home, std_away)
        
        return {
            'home_win_prob': home_win_prob,
            'draw_prob': 0.0,  # 농구는 무승부 없음
            'away_win_prob': away_win_prob,
            'expected_score_home': expected_score_home,
            'expected_score_away': expected_score_away,
            'top_3_scores': top_3_scores,
            'mean_home': round(mean_home, 1),
            'mean_away': round(mean_away, 1),
            'std_home': round(std_home, 1),
            'std_away': round(std_away, 1),
            'possessions_home': round(poss_home, 1),
            'possessions_away': round(poss_away, 1),
            'ppp_home': round(ppp_home_adj, 3),
            'ppp_away': round(ppp_away_adj, 3),
            'key_factors': key_factors,
            'confidence': confidence,
            'model_type': 'Possession × PPP (Pro)',
            'sport_type': 'basketball'
        }
    
    def _extract_features(self, team_data: Dict, opp_data: Dict, is_home: bool,
                         rest_days: int, injury_data: Dict, coaching_data: Dict) -> Dict:
        """Feature 추출"""
        
        # 기본 능력치
        avg_points = team_data.get('avg_goals', 105)
        avg_conceded = team_data.get('avg_conceded', 105)
        
        # 데이터 변환 (축구 형식이면 농구 범위로)
        if avg_points < 10:
            avg_points = 85 + (avg_points / 5.0) * 40
        if avg_conceded < 10:
            avg_conceded = 85 + (avg_conceded / 5.0) * 40
        
        # Offensive/Defensive Rating 계산
        off_rating = (avg_points / 105) * 100  # 105 = NBA 평균
        def_rating = (avg_conceded / 105) * 100
        
        # Pace 계산
        pace = (avg_points + avg_conceded) / 2.1  # 2.1 = 평균 PPP
        
        # 슈팅 효율 (eFG%)
        efg_pct = 0.50 + (off_rating - 100) * 0.002  # 기본 50%
        
        # 3점 비율
        three_pt_rate = 0.35 + np.random.uniform(-0.05, 0.05)
        
        # FT 비율
        ft_rate = 0.25 + np.random.uniform(-0.05, 0.05)
        
        # 턴오버율
        turnover_pct = 0.14 - (off_rating - 100) * 0.0005
        
        # 공격 리바운드율
        off_reb_pct = 0.25 + np.random.uniform(-0.03, 0.03)
        
        # 최근 폼 (가중치 대폭 증가)
        recent_form = team_data.get('recent_form', [])
        form_score = sum(1 for r in recent_form if r == 'W') / max(len(recent_form), 1)
        
        # 최근 5경기 평균 득점 계산
        recent_ppg = self._calculate_recent_ppg(team_data)
        
        # 시즌 평균 50% + 최근 5경기 50% 혼합
        season_ppg = avg_points
        if recent_ppg > 0:
            avg_points = season_ppg * 0.5 + recent_ppg * 0.5
        
        # 홈 어드밴티지
        home_factor = 1.03 if is_home else 0.97
        
        # Back-to-back
        back_to_back = 1 if rest_days < 1 else 0
        
        # 부상 영향
        injury_impact = 1.0
        if injury_data:
            team_injuries = injury_data.get('home' if is_home else 'away', [])
            injury_impact = max(0.85, 1.0 - len(team_injuries) * 0.03)
        
        # 코칭 영향
        coach_pace = 1.0
        coach_variance = 0.0
        if coaching_data:
            coach_info = coaching_data.get('home' if is_home else 'away', {})
            coach_pace = coach_info.get('pace_factor', 1.0)
            coach_variance = coach_info.get('variance', 0.0)
        
        # 라인업 매치업 (간단 버전)
        guard_matchup = 0.0
        wing_matchup = 0.0
        big_matchup = 0.0
        
        if 'lineup_attack' in team_data and 'lineup_defense' in opp_data:
            attack = team_data['lineup_attack']
            defense = opp_data['lineup_defense']
            matchup_diff = (attack - defense) / 70.0  # 정규화
            guard_matchup = matchup_diff * 0.3
            wing_matchup = matchup_diff * 0.3
            big_matchup = matchup_diff * 0.4
        
        return {
            'off_rating': off_rating,
            'def_rating': def_rating,
            'pace': pace,
            'efg_pct': efg_pct,
            'three_pt_rate': three_pt_rate,
            'ft_rate': ft_rate,
            'turnover_pct': turnover_pct,
            'off_reb_pct': off_reb_pct,
            'rest_days': rest_days,
            'back_to_back': back_to_back,
            'home_factor': home_factor,
            'form_score': form_score,
            'injury_impact': injury_impact,
            'coach_pace': coach_pace,
            'coach_variance': coach_variance,
            'guard_matchup': guard_matchup,
            'wing_matchup': wing_matchup,
            'big_matchup': big_matchup
        }
    
    def _predict_possessions(self, X: Dict) -> float:
        """Possession 예측"""
        base_poss = 98  # NBA 평균 포제션 (약간 낮춤)
        
        return (
            base_poss
            + (X['pace'] - 100) * 0.4  # Pace 영향
            + (X['coach_pace'] - 1.0) * 4  # 코치 영향
            - 3 * X['back_to_back']  # 연속 경기 감소
            + 0.5 * X['rest_days']  # 휴식일 증가
        )
    
    def _predict_ppp(self, X: Dict) -> float:
        """PPP (Points Per Possession) 예측"""
        base_ppp = 1.05  # NBA 평균 PPP
        
        # 공격 능력치 기반
        rating_factor = X['off_rating'] / 100
        
        # 슈팅 효율
        shooting_factor = (
            0.3 * X['efg_pct'] +
            0.1 * X['three_pt_rate'] +
            0.1 * X['ft_rate']
        )
        
        # 볼 관리
        ball_control = (
            -0.2 * X['turnover_pct'] +
            0.15 * X['off_reb_pct']
        )
        
        # 매치업
        matchup_factor = (
            0.05 * X['guard_matchup'] +
            0.05 * X['wing_matchup'] +
            0.05 * X['big_matchup']
        )
        
        # 상황 팩터
        situation_factor = (
            X['home_factor'] *
            X['injury_impact'] *
            (0.9 + X['form_score'] * 0.2)
        )
        
        ppp = (
            base_ppp * rating_factor +
            shooting_factor +
            ball_control +
            matchup_factor
        ) * situation_factor
        
        return max(0.85, min(1.25, ppp))  # PPP 범위 제한
    
    def _adjust_defense(self, ppp: float, opp_def_rating: float) -> float:
        """상대 수비 반영"""
        return ppp * (100 / opp_def_rating)
    
    def _predict_std(self, X: Dict) -> float:
        """분산 예측"""
        return (
            self.base_std
            + 0.05 * (X['pace'] - 100)
            + 2 * X['coach_variance']
            + 1 * (1 - X['form_score'])
        )
    
    def _win_probability(self, mean_A: float, mean_B: float, 
                        std_A: float, std_B: float) -> float:
        """승률 계산 (Normal Distribution)"""
        diff_mean = mean_A - mean_B
        diff_std = np.sqrt(std_A**2 + std_B**2)
        
        return 1 - norm.cdf(0, loc=diff_mean, scale=diff_std)
    
    def _generate_top_scores(self, mean_home: float, mean_away: float,
                            std_home: float, std_away: float) -> list:
        """Top 3 스코어 생성"""
        scores = []
        
        # 중심값 주변 스코어 생성
        for h_offset in [-0.5, 0, 0.5]:
            for a_offset in [-0.5, 0, 0.5]:
                h_score = int(np.clip(
                    round(mean_home + h_offset * std_home),
                    self.min_score, self.max_score
                ))
                a_score = int(np.clip(
                    round(mean_away + a_offset * std_away),
                    self.min_score, self.max_score
                ))
                
                # 확률 계산
                prob_h = norm.pdf(h_score, loc=mean_home, scale=std_home)
                prob_a = norm.pdf(a_score, loc=mean_away, scale=std_away)
                prob = prob_h * prob_a
                
                scores.append(((h_score, a_score), prob))
        
        # 확률 높은 순으로 정렬
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 확률 정규화
        total_prob = sum(p for _, p in scores[:3])
        top_3 = [((h, a), p/total_prob) for (h, a), p in scores[:3]]
        
        return top_3
    
    def _identify_key_factors(self, X_home: Dict, X_away: Dict,
                             poss_home: float, poss_away: float) -> list:
        """주요 영향 요인 식별"""
        factors = []
        
        # Pace 차이
        pace_diff = abs(X_home['pace'] - X_away['pace'])
        if pace_diff > 5:
            factors.append(f"템포 차이 큼 (홈: {X_home['pace']:.1f}, 원정: {X_away['pace']:.1f})")
        
        # 능력치 차이
        rating_diff = X_home['off_rating'] - X_away['def_rating']
        if abs(rating_diff) > 5:
            factors.append(f"공수 능력 차이 ({rating_diff:+.1f})")
        
        # 휴식일
        if X_home['back_to_back'] or X_away['back_to_back']:
            factors.append("연속 경기 피로도")
        
        # 부상
        if X_home['injury_impact'] < 0.95 or X_away['injury_impact'] < 0.95:
            factors.append("주요 선수 부상")
        
        # 폼
        form_diff = X_home['form_score'] - X_away['form_score']
        if abs(form_diff) > 0.3:
            factors.append(f"최근 폼 차이 ({form_diff:+.2f})")
        
        if not factors:
            factors.append("균형잡힌 매치업")
        
        return factors
    
    def _calculate_confidence(self, home_win_prob: float, away_win_prob: float,
                             std_home: float, std_away: float) -> float:
        """
        신뢰도 계산 (개선)
        
        신뢰도는 예측의 불확실성을 나타냄:
        - 높음: 데이터 충분, 분산 작음, 예측 안정적
        - 낮음: 데이터 부족, 분산 큼, 예측 불안정
        
        접전이어도 데이터가 충분하면 신뢰도는 높아야 함!
        """
        
        # 1. 승률 차이 (접전 vs 일방적)
        prob_diff = abs(home_win_prob - away_win_prob)
        
        # 2. 분산 안정성 (분산이 작을수록 예측 안정적)
        avg_std = (std_home + std_away) / 2
        std_factor = max(0, 1 - (avg_std - 10) / 10)
        
        # 3. 승률 절대값 (극단적 확률은 신뢰도 높음)
        max_prob = max(home_win_prob, away_win_prob)
        prob_confidence = 0.5 + (max_prob - 0.5) * 0.5  # 0.5 ~ 0.75 범위
        
        # 4. 종합 신뢰도 계산
        # - 분산 안정성 50% (가장 중요)
        # - 승률 차이 30%
        # - 승률 절대값 20%
        confidence = (
            std_factor * 0.5 +
            prob_diff * 0.3 +
            prob_confidence * 0.2
        )
        
        # 최소 0.5 (중간), 최대 0.95 (매우 높음)
        return max(0.5, min(0.95, confidence))
    
    def _calculate_recent_ppg(self, team_data: dict) -> float:
        """최근 5경기 평균 득점 계산"""
        recent_matches = team_data.get('recent_matches', [])
        
        if not recent_matches or len(recent_matches) < 3:
            return 0  # 데이터 부족 시 0 반환 (시즌 평균만 사용)
        
        # 최근 5경기 득점
        recent_scores = [m.get('goals_for', 0) for m in recent_matches[:5]]
        
        if not recent_scores:
            return 0
        
        # 농구 점수 범위로 변환 (축구 형식이면)
        if max(recent_scores) < 10:
            # 축구 형식 (0-5골) → 농구 형식 (90-130점)
            recent_scores = [100 + (score - 2.5) * 10 for score in recent_scores]
        
        return np.mean(recent_scores)
    
    def _enhance_team_data_with_lineup(self, team_data: dict, lineup: dict) -> dict:
        """라인업 정보로 팀 데이터 보강"""
        enhanced_data = team_data.copy()
        
        team_strength = lineup.get('team_strength', {})
        
        if team_strength:
            attack_rating = team_strength.get('attack_rating', 70)
            defense_rating = team_strength.get('defense_rating', 70)
            
            if 'avg_goals' in enhanced_data:
                adjustment = (attack_rating - 70) / 70 * 0.3
                enhanced_data['avg_goals'] *= (1 + adjustment)
            
            if 'avg_conceded' in enhanced_data:
                adjustment = (defense_rating - 70) / 70 * 0.3
                enhanced_data['avg_conceded'] *= (1 - adjustment)
            
            enhanced_data['lineup_overall'] = team_strength.get('overall_rating', 70)
            enhanced_data['lineup_attack'] = attack_rating
            enhanced_data['lineup_defense'] = defense_rating
        
        enhanced_data['formation'] = lineup.get('formation', '기본')
        enhanced_data['tactic'] = lineup.get('tactic', '균형형')
        
        return enhanced_data
    
    def calibrate_with_market(self, model_prob: float, market_odds: float) -> float:
        """Market Calibration (선택적)"""
        market_prob = 1 / market_odds
        return 0.7 * model_prob + 0.3 * market_prob
    
    def betting_edge(self, model_prob: float, market_odds: float) -> float:
        """배팅 엣지 계산"""
        implied_prob = 1 / market_odds
        return model_prob - implied_prob

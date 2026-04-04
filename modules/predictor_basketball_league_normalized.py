"""
농구 예측 모듈 (리그 정규화 버전)

핵심 개선:
- 리그별 프로파일 (NBA, KBL)
- Pace, PPP, STD 모두 리그 기준으로 정규화
- 실제 데이터 기반 예측
- 선수 개인 능력치 반영 (PER, WS, BPM, PIE, RAPM)
"""

import numpy as np
from math import erf, exp, sqrt, pi
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from modules.advanced_player_metrics import get_advanced_metrics


# 리그 프로파일 정의 (실제 데이터 기반)
LEAGUE_PROFILES = {
    "NBA East": {
        "avg_pace": 100,        # NBA 평균 포제션
        "avg_ppp": 1.15,        # NBA 평균 PPP
        "avg_score": 115,       # NBA 평균 득점
        "std_base": 12,         # 기본 표준편차
        "min_score": 70,        # 최소 점수 (극단적 저득점 경기)
        "max_score": 160,       # 최대 점수 (극단적 고득점 경기)
        "pace_range": (95, 105),
        "ppp_range": (1.08, 1.22)
    },
    "NBA West": {
        "avg_pace": 100,
        "avg_ppp": 1.15,
        "avg_score": 115,
        "std_base": 12,
        "min_score": 70,
        "max_score": 160,
        "pace_range": (95, 105),
        "ppp_range": (1.08, 1.22)
    },
    "KBL": {
        "avg_pace": 74,         # KBL 평균 포제션 (낮음)
        "avg_ppp": 1.08,        # KBL 평균 PPP (낮음)
        "avg_score": 82,        # KBL 평균 득점 (76-88 범위)
        "std_base": 8,          # 기본 표준편차 (작음)
        "min_score": 55,        # 최소 점수 (극단적 저득점 경기)
        "max_score": 110,       # 최대 점수 (극단적 고득점 경기)
        "pace_range": (68, 80),
        "ppp_range": (1.00, 1.16)
    }
}


class BasketballPredictorLeagueNormalized:
    """
    리그 정규화 농구 예측 모델
    
    핵심 원리:
    1. 리그별 프로파일 로드
    2. Possession × PPP 계산
    3. 리그 스케일로 정규화
    4. Normal Distribution으로 승률 계산
    """
    
    def __init__(self, league: str = "NBA East"):
        self.league = league
        self.profile = LEAGUE_PROFILES.get(league, LEAGUE_PROFILES["NBA East"])
        
        # 고급 메트릭스 시스템
        league_type = "NBA" if "NBA" in league else "KBL"
        self.advanced_metrics = get_advanced_metrics(league_type)
        
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        
        print(f"농구 예측 모델 초기화: {league}")
        print(f"   평균 Pace: {self.profile['avg_pace']}")
        print(f"   평균 PPP: {self.profile['avg_ppp']}")
        print(f"   평균 득점: {self.profile['avg_score']}")
        print(f"   고급 메트릭스: PER, WS, BPM, PIE, RAPM")
    
    def predict_match(self, home_team, away_team, home_data, away_data,
                     weather, temperature, field_condition, match_importance,
                     rest_days_home, rest_days_away, injury_data=None, coaching_data=None,
                     lineup_home=None, lineup_away=None, 
                     home_players=None, away_players=None):
        """
        농구 예측: 리그 정규화 Possession × PPP 모델 + 선수 고급 메트릭스
        """
        # [STEP 5] Add Debug Logging
        print("HOME TEAM DATA:", home_data)
        print("AWAY TEAM DATA:", away_data)
        
        # KBL 전용 독립 예측 모델 (Net Rating + Logistic Regression 구조)
        if self.league == "KBL":
            return self._predict_kbl_refactored(
                home_team, away_team, home_data, away_data,
                weather, temperature, field_condition, match_importance,
                rest_days_home, rest_days_away, injury_data, coaching_data,
                lineup_home, lineup_away, home_players, away_players
            )

        # 선수 데이터 기반 팀 전력 계산
        if home_players:
            home_player_strength = self.advanced_metrics.calculate_team_strength_from_players(
                home_players, home_data
            )
            # 부상 영향 반영
            if injury_data and 'home' in injury_data:
                home_player_strength = self.advanced_metrics.apply_injury_impact(
                    home_player_strength, injury_data['home'], home_players
                )
            # 최근 폼 반영
            home_player_strength = self.advanced_metrics.apply_form_adjustment(
                home_player_strength, home_players
            )
        else:
            home_player_strength = None
        
        if away_players:
            away_player_strength = self.advanced_metrics.calculate_team_strength_from_players(
                away_players, away_data
            )
            # 부상 영향 반영
            if injury_data and 'away' in injury_data:
                away_player_strength = self.advanced_metrics.apply_injury_impact(
                    away_player_strength, injury_data['away'], away_players
                )
            # 최근 폼 반영
            away_player_strength = self.advanced_metrics.apply_form_adjustment(
                away_player_strength, away_players
            )
        else:
            away_player_strength = None
        
        # 라인업 기반 팀 데이터 보강
        if lineup_home:
            home_data = self._enhance_team_data_with_lineup(home_data, lineup_home)
        if lineup_away:
            away_data = self._enhance_team_data_with_lineup(away_data, lineup_away)
        
        # 선수 전력 데이터 통합
        if home_player_strength:
            home_data = self._integrate_player_strength(home_data, home_player_strength)
        if away_player_strength:
            away_data = self._integrate_player_strength(away_data, away_player_strength)
        
        # Feature 추출
        X_home = self._extract_features(
            home_data, away_data, True, 
            rest_days_home, injury_data, coaching_data
        )
        X_away = self._extract_features(
            away_data, home_data, False,
            rest_days_away, injury_data, coaching_data
        )
        
        # 상대 수비력 정보 추가 (핵심 개선!)
        X_home['opp_avg_conceded'] = away_data.get('opp_ppg', away_data.get('avg_conceded', self.profile['avg_score']))
        X_away['opp_avg_conceded'] = home_data.get('opp_ppg', home_data.get('avg_conceded', self.profile['avg_score']))
        
        # 득실차 정보 추가
        X_home['diff'] = home_data.get('diff', 0)
        X_away['diff'] = away_data.get('diff', 0)
        
        # 상대 순위 정보 추가 (순위 반영용)
        X_home['opp_rank'] = away_data.get('rank', 10)
        X_away['opp_rank'] = home_data.get('rank', 10)
        
        # 리그 정규화 적용
        poss_home, ppp_home = self._apply_league_context(X_home)
        poss_away, ppp_away = self._apply_league_context(X_away)
        
        # 상대 수비 반영
        ppp_home_adj = self._adjust_defense(ppp_home, X_away['def_rating'])
        ppp_away_adj = self._adjust_defense(ppp_away, X_home['def_rating'])
        
        # 평균 점수 계산
        mean_home = poss_home * ppp_home_adj
        mean_away = poss_away * ppp_away_adj
        
        # 디버깅 출력
        print(f"\n[SEARCH] 예측 디버깅 ({self.league}):")
        print(f"홈팀 ({home_team}):")
        print(f"  - PPG: {X_home['avg_points']:.1f}, OPP_PPG: {X_home['avg_conceded']:.1f}")
        print(f"  - 상대 수비력: {X_home.get('opp_avg_conceded', 0):.1f}")
        print(f"  - 득실차: {X_home.get('diff', 0):+.1f}")
        print(f"  - 시즌 승률: {X_home['season_win_pct']:.1%}, 최근10경기: {X_home['last_10_win_pct']:.1%}")
        print(f"  - 홈 팩터: {X_home['home_factor']:.3f}")
        
        # 선수 메트릭스 정보
        if 'player_metrics' in home_data:
            pm = home_data['player_metrics']
            print(f"  - 선수 전력: Overall {pm['overall_rating']:.1f}, PER {pm['weighted_per']:.1f}, BPM {pm['weighted_bpm']:.1f}")
            print(f"  - 벤치 깊이: {pm['bench_strength']:.1f}, 주요 선수: {pm['top_players_count']}명")
        
        print(f"  - Possession: {poss_home:.1f}, PPP: {ppp_home_adj:.3f}")
        print(f"  - 예상 득점: {mean_home:.1f}")
        
        print(f"원정팀 ({away_team}):")
        print(f"  - PPG: {X_away['avg_points']:.1f}, OPP_PPG: {X_away['avg_conceded']:.1f}")
        print(f"  - 상대 수비력: {X_away.get('opp_avg_conceded', 0):.1f}")
        print(f"  - 득실차: {X_away.get('diff', 0):+.1f}")
        print(f"  - 시즌 승률: {X_away['season_win_pct']:.1%}, 최근10경기: {X_away['last_10_win_pct']:.1%}")
        print(f"  - 원정 팩터: {X_away['home_factor']:.3f}")
        
        # 선수 메트릭스 정보
        if 'player_metrics' in away_data:
            pm = away_data['player_metrics']
            print(f"  - 선수 전력: Overall {pm['overall_rating']:.1f}, PER {pm['weighted_per']:.1f}, BPM {pm['weighted_bpm']:.1f}")
            print(f"  - 벤치 깊이: {pm['bench_strength']:.1f}, 주요 선수: {pm['top_players_count']}명")
        
        print(f"  - Possession: {poss_away:.1f}, PPP: {ppp_away_adj:.3f}")
        print(f"  - 예상 득점: {mean_away:.1f}\n")
        
        # 분산 계산 (리그별)
        std_home = self._predict_std(X_home)
        std_away = self._predict_std(X_away)
        
        # 승률 계산
        home_win_prob = self._win_probability(mean_home, mean_away, std_home, std_away)
        away_win_prob = 1 - home_win_prob
        
        # 예상 스코어 (리그별 범위로 클리핑)
        expected_score_home = int(np.clip(
            round(mean_home), 
            self.profile['min_score'], 
            self.profile['max_score']
        ))
        expected_score_away = int(np.clip(
            round(mean_away),
            self.profile['min_score'],
            self.profile['max_score']
        ))
        
        # Top 3 스코어
        top_3_scores = self._generate_top_scores(mean_home, mean_away, std_home, std_away)
        
        # 주요 영향 요인
        key_factors = self._identify_key_factors(X_home, X_away, poss_home, poss_away)
        
        # 신뢰도
        confidence = self._calculate_confidence(home_win_prob, away_win_prob, std_home, std_away)
        
        return {
            'home_win_prob': home_win_prob,
            'draw_prob': 0.0,
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
            'model_type': f'League-Normalized ({self.league})',
            'sport_type': 'basketball',
            'league': self.league
        }
    
    def _extract_features(self, team_data: Dict, opp_data: Dict, is_home: bool,
                         rest_days: int, injury_data: Dict, coaching_data: Dict) -> Dict:
        """Feature 추출 (실제 데이터 기반)"""
        
        # 실제 NBA 데이터 우선 사용 (ppg, opp_ppg)
        avg_points = team_data.get('ppg', team_data.get('avg_goals', self.profile['avg_score']))
        avg_conceded = team_data.get('opp_ppg', team_data.get('avg_conceded', self.profile['avg_score']))
        
        # 데이터 변환 (축구 형식이면 농구 범위로)
        if avg_points < 10:
            avg_points = self.profile['avg_score'] + (avg_points - 2.5) * 10
        if avg_conceded < 10:
            avg_conceded = self.profile['avg_score'] + (avg_conceded - 2.5) * 10
        
        # Offensive/Defensive Rating 계산 (리그 평균 기준)
        league_avg = self.profile['avg_score']
        off_rating = (avg_points / league_avg) * 100
        def_rating = (avg_conceded / league_avg) * 100
        
        # Pace 계산 (리그 평균 기준)
        pace = (avg_points + avg_conceded) / (2 * self.profile['avg_ppp'])
        
        # 슈팅 효율 (eFG%)
        efg_pct = 0.48 + (off_rating - 100) * 0.002
        
        # 3점 비율 (리그별 차이)
        if self.league == "KBL":
            three_pt_rate = 0.28 + np.random.uniform(-0.03, 0.03)  # KBL은 3점 적음
        else:
            three_pt_rate = 0.38 + np.random.uniform(-0.05, 0.05)  # NBA는 3점 많음
        
        # FT 비율
        ft_rate = 0.22 + np.random.uniform(-0.03, 0.03)
        
        # 턴오버율
        turnover_pct = 0.14 - (off_rating - 100) * 0.0005
        
        # 공격 리바운드율
        off_reb_pct = 0.25 + np.random.uniform(-0.03, 0.03)
        
        # 최근 폼
        recent_form = team_data.get('form', team_data.get('recent_form', []))
        form_score = sum(1 for r in recent_form if r == 'W') / max(len(recent_form), 1)
        
        # 최근 10경기 성적
        last_10_wins = team_data.get('last_10_wins', 0)
        last_10_losses = team_data.get('last_10_losses', 0)
        
        if last_10_wins == 0 and len(recent_form) >= 10:
            last_10_wins = sum(1 for r in recent_form[:10] if r == 'W')
            last_10_losses = sum(1 for r in recent_form[:10] if r == 'L')
        
        last_10_total = last_10_wins + last_10_losses
        last_10_win_pct = last_10_wins / max(last_10_total, 1) if last_10_total > 0 else form_score
        
        # 시즌 전체 성적
        wins = team_data.get('wins', 0)
        losses = team_data.get('losses', 0)
        total_games = wins + losses
        season_win_pct = wins / max(total_games, 1) if total_games > 0 else 0.5
        
        # 최근 5경기 평균 득점 계산
        recent_ppg = self._calculate_recent_ppg(team_data)
        
        # 시즌 평균 70% + 최근 5경기 30% 혼합
        season_ppg = avg_points
        if recent_ppg > 0:
            avg_points = season_ppg * 0.7 + recent_ppg * 0.3
        
        # 홈 어드밴티지 (실제 홈/원정 승률 반영 - 적정 수준)
        if is_home:
            home_record = team_data.get('home', '0-0')
            if '-' in home_record:
                h_wins, h_losses = map(int, home_record.split('-'))
                home_win_pct = h_wins / max(h_wins + h_losses, 1)
                if self.league == "KBL":
                    home_factor = 0.98 + (home_win_pct * 0.08)  # KBL 홈 어드밴티지
                else:
                    home_factor = 0.98 + (home_win_pct * 0.06)  # NBA 홈 어드밴티지 (완화)
            else:
                home_factor = 1.03 if self.league == "KBL" else 1.02
        else:
            away_record = team_data.get('away', '0-0')
            if '-' in away_record:
                a_wins, a_losses = map(int, away_record.split('-'))
                away_win_pct = a_wins / max(a_wins + a_losses, 1)
                if self.league == "KBL":
                    home_factor = 0.92 + (away_win_pct * 0.08)
                else:
                    home_factor = 0.94 + (away_win_pct * 0.06)  # NBA 원정 페널티 (완화)
            else:
                home_factor = 0.97 if self.league == "KBL" else 0.98
        
        # Back-to-back (피로도 증가)
        back_to_back = 1 if rest_days < 1 else 0
        back_to_back_penalty = 0.95 if back_to_back else 1.0  # 백투백 시 -5%
        
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
        
        # 라인업 매치업
        guard_matchup = 0.0
        wing_matchup = 0.0
        big_matchup = 0.0
        
        if 'lineup_attack' in team_data and 'lineup_defense' in opp_data:
            attack = team_data['lineup_attack']
            defense = opp_data['lineup_defense']
            matchup_diff = (attack - defense) / 70.0
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
            'back_to_back_penalty': back_to_back_penalty,
            'home_factor': home_factor,
            'form_score': form_score,
            'season_win_pct': season_win_pct,
            'last_10_win_pct': last_10_win_pct,
            'last_10_wins': last_10_wins,
            'last_10_losses': last_10_losses,
            'rank': team_data.get('rank', 0),
            'injury_impact': injury_impact,
            'coach_pace': coach_pace,
            'coach_variance': coach_variance,
            'guard_matchup': guard_matchup,
            'wing_matchup': wing_matchup,
            'big_matchup': big_matchup,
            'avg_points': avg_points,
            'avg_conceded': avg_conceded
        }
    
    def _apply_league_context(self, X: Dict) -> Tuple[float, float]:
        """
        리그 정규화 적용 (핵심 개선)
        
        Returns:
            (possessions, ppp) 튜플
        """
        
        # 1. 기본 Possession 계산
        base_poss = self._predict_possessions_raw(X)
        
        # 2. 기본 PPP 계산
        base_ppp = self._predict_ppp_raw(X)
        
        # 3. 리그 스케일로 정규화
        league_pace = self.profile['avg_pace']
        league_ppp = self.profile['avg_ppp']
        
        # Possession 정규화
        poss = base_poss * (league_pace / 100)
        
        # PPP 정규화
        ppp = base_ppp * (league_ppp / 1.15)
        
        # 범위 제한
        poss = np.clip(poss, self.profile['pace_range'][0], self.profile['pace_range'][1])
        ppp = np.clip(ppp, self.profile['ppp_range'][0], self.profile['ppp_range'][1])
        
        return poss, ppp
    
    def _predict_possessions_raw(self, X: Dict) -> float:
        """원시 Possession 예측 (더 보수적)"""
        base_poss = 98  # 100 → 98 (실제 경기는 더 느림)
        
        # Pace 기반 조정 (보수적)
        pace_adjustment = (X['pace'] - self.profile['avg_pace']) * 0.15
        
        # 코치 영향 (최소화)
        coach_adjustment = (X['coach_pace'] - 1.0) * 1.5
        
        # 피로도
        fatigue_adjustment = -2 * X['back_to_back']
        
        # 휴식일
        rest_adjustment = 0.15 * X['rest_days']
        
        total_poss = base_poss + pace_adjustment + coach_adjustment + fatigue_adjustment + rest_adjustment
        
        # 포제션 범위 제한: 94-102 (더 보수적)
        return max(94, min(102, total_poss))
    
    def _predict_ppp_raw(self, X: Dict) -> float:
        """원시 PPP 예측 (균형잡힌 접근 + 순위 반영)"""
        # 실제 평균 득점 기반 PPP 계산 (더 보수적)
        base_ppp = X['avg_points'] / 100 * 0.88  # 88%만 사용 (선수들이 항상 평균 내는 것 아님)
        
        # 상대 수비력 기반 조정 (적당히)
        opp_def_weakness = X.get('opp_avg_conceded', 115) / 115
        defense_adjusted_ppp = base_ppp * (0.85 + 0.15 * opp_def_weakness)
        
        # 시즌 순위 반영 (핵심 추가!)
        my_rank = X.get('rank', 10)
        opp_rank = X.get('opp_rank', 10)
        if my_rank > 0 and opp_rank > 0:
            rank_factor = 1.0 + (opp_rank - my_rank) * 0.005  # 순위 1차이당 0.5%
        else:
            rank_factor = 1.0
        
        # 공격 능력치 기반
        rating_factor = X['off_rating'] / 100
        
        # 슈팅 효율 (최소 영향)
        shooting_factor = (
            0.02 * X['efg_pct'] +
            0.01 * X['three_pt_rate'] +
            0.01 * X['ft_rate']
        )
        
        # 볼 관리 (최소 영향)
        ball_control = (
            -0.02 * X['turnover_pct'] +
            0.01 * X['off_reb_pct']
        )
        
        # 매치업 (최소 영향)
        matchup_factor = (
            0.005 * X['guard_matchup'] +
            0.005 * X['wing_matchup'] +
            0.005 * X['big_matchup']
        )
        
        # 상황 팩터 (시즌 65% + 최근 10경기 35%) - 최근 폼 가중치 증가
        combined_win_pct = X['season_win_pct'] * 0.65 + X['last_10_win_pct'] * 0.35
        
        # 득실차 반영 (완화)
        diff_factor = 1.0 + (X.get('diff', 0) / 200)
        
        situation_factor = (
            X['home_factor'] *
            X['injury_impact'] *
            rank_factor *  # 순위 반영 추가
            diff_factor *
            (0.95 + combined_win_pct * 0.03 + X['form_score'] * 0.02)
        )
        
        # 실제 PPP 92% + 모델 조정 8%
        model_adjustment = (
            shooting_factor +
            ball_control +
            matchup_factor
        ) * situation_factor
        
        ppp = defense_adjusted_ppp * 0.92 + (defense_adjusted_ppp + model_adjustment) * 0.08
        
        # [Sanity Check] 순위 기반 최소 PPP 하한선 설정 (Top-tier Protection)
        # 상위권 팀이 데이터 오류로 과소평가되는 것을 방지
        min_ppp = 1.12 if my_rank <= 3 else 1.08 if my_rank <= 7 else 1.02
        if self.league == "KBL":
            min_ppp -= 0.04 # KBL은 전반적으로 PPP가 낮음을 반영
            
        ppp = max(min_ppp, ppp)
        
        return max(0.95, min(1.22, ppp))
    
    def _adjust_defense(self, ppp: float, opp_def_rating: float) -> float:
        """상대 수비 반영"""
        return ppp * (100 / opp_def_rating)
    
    def _predict_std(self, X: Dict) -> float:
        """분산 예측 (리그별)"""
        base_std = self.profile['std_base']
        
        return (
            base_std
            + 0.04 * (X['pace'] - self.profile['avg_pace'])
            + 1.5 * X['coach_variance']
            + 0.8 * (1 - X['form_score'])
        )
    
    def _norm_pdf(self, x, mu, sigma):
        """정규분포 확률 밀도 함수 (PDF) 직접 구현"""
        if sigma == 0: return 0
        return (1 / (sigma * sqrt(2 * pi))) * exp(-0.5 * ((x - mu) / sigma) ** 2)

    def _norm_cdf(self, x, mu, sigma):
        """정규분포 누적 분포 함수 (CDF) 직접 구현"""
        if sigma == 0: return 1 if x >= mu else 0
        return 0.5 * (1 + erf((x - mu) / (sigma * sqrt(2))))

    def _win_probability(self, mean_A: float, mean_B: float, 
                        std_A: float, std_B: float) -> float:
        """승률 계산 (Normal Distribution)"""
        diff_mean = mean_A - mean_B
        diff_std = np.sqrt(std_A**2 + std_B**2)
        
        # 1 - P(X < 0) where X ~ N(diff_mean, diff_std)
        return 1 - self._norm_cdf(0, loc=diff_mean, scale=diff_std)
    
    def _generate_top_scores(self, mean_home: float, mean_away: float,
                            std_home: float, std_away: float) -> list:
        """Top 3 스코어 생성"""
        scores = []
        
        for h_offset in [-0.5, 0, 0.5]:
            for a_offset in [-0.5, 0, 0.5]:
                h_score = int(np.clip(
                    round(mean_home + h_offset * std_home),
                    self.profile['min_score'], 
                    self.profile['max_score']
                ))
                a_score = int(np.clip(
                    round(mean_away + a_offset * std_away),
                    self.profile['min_score'],
                    self.profile['max_score']
                ))
                
                prob_h = self._norm_pdf(h_score, loc=mean_home, scale=std_home)
                prob_a = self._norm_pdf(a_score, loc=mean_away, scale=std_away)
                prob = prob_h * prob_a
                
                scores.append(((h_score, a_score), prob))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        total_prob = sum(p for _, p in scores[:3])
        top_3 = [((h, a), p/total_prob) for (h, a), p in scores[:3]]
        
        return top_3
    
    def _identify_key_factors(self, X_home: Dict, X_away: Dict,
                             poss_home: float, poss_away: float) -> list:
        """주요 영향 요인 식별"""
        factors = []
        
        # 시즌 순위 정보
        home_rank = X_home.get('rank', 0)
        away_rank = X_away.get('rank', 0)
        if home_rank > 0 and away_rank > 0:
            rank_diff = away_rank - home_rank
            factors.append(f"순위: 홈 {home_rank}위 vs 원정 {away_rank}위 (차이: {rank_diff})")
        
        # 최근 10경기 성적
        if X_home.get('last_10_wins', 0) > 0 or X_away.get('last_10_wins', 0) > 0:
            home_l10 = f"{X_home.get('last_10_wins', 0)}-{X_home.get('last_10_losses', 0)}"
            away_l10 = f"{X_away.get('last_10_wins', 0)}-{X_away.get('last_10_losses', 0)}"
            home_l10_pct = X_home.get('last_10_win_pct', 0)
            away_l10_pct = X_away.get('last_10_win_pct', 0)
            factors.append(f"최근 10경기: 홈 {home_l10} ({home_l10_pct:.0%}) vs 원정 {away_l10} ({away_l10_pct:.0%})")
        
        # 시즌 승률 차이
        win_pct_diff = X_home['season_win_pct'] - X_away['season_win_pct']
        if abs(win_pct_diff) > 0.05:
            factors.append(f"시즌 승률 차이 ({X_home['season_win_pct']:.1%} vs {X_away['season_win_pct']:.1%})")
        
        # Pace 차이
        pace_diff = abs(X_home['pace'] - X_away['pace'])
        if pace_diff > 4:
            factors.append(f"템포 차이 (홈: {X_home['pace']:.1f}, 원정: {X_away['pace']:.1f})")
        
        # 능력치 차이
        rating_diff = X_home['off_rating'] - X_away['def_rating']
        if abs(rating_diff) > 5:
            factors.append(f"공수 능력 차이 ({rating_diff:+.1f})")
        
        # 실제 득점 차이
        score_diff = X_home['avg_points'] - X_away['avg_points']
        if abs(score_diff) > 3:
            factors.append(f"평균 득점 차이 ({score_diff:+.1f}점)")
        
        # 휴식일
        if X_home['back_to_back'] or X_away['back_to_back']:
            factors.append("연속 경기 피로도")
        
        # 부상
        if X_home['injury_impact'] < 0.95 or X_away['injury_impact'] < 0.95:
            factors.append("주요 선수 부상")
        
        # 최근 10경기 폼 차이
        last_10_diff = X_home['last_10_win_pct'] - X_away['last_10_win_pct']
        if abs(last_10_diff) > 0.2:
            factors.append(f"최근 10경기 폼 차이 ({last_10_diff:+.1%})")
        
        # 홈 어드밴티지
        if self.league == "KBL":
            factors.append("KBL 홈 어드밴티지 (강함)")
        
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
        std_factor = max(0, 1 - (avg_std - self.profile['std_base']) / 10)
        
        # 3. 승률 절대값 (극단적 확률은 신뢰도 높음)
        # 예: 90% vs 10% → 신뢰도 높음
        # 예: 55% vs 45% → 접전이지만 데이터 충분하면 신뢰도 높음
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
    
    def _calculate_recent_ppg(self, team_data: Dict) -> float:
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
            recent_scores = [self.profile['avg_score'] + (score - 2.5) * 10 for score in recent_scores]
        
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
    
    def _integrate_player_strength(self, team_data: dict, player_strength: dict) -> dict:
        """선수 전력을 팀 데이터에 통합"""
        integrated = team_data.copy()
        
        # 공격력 조정 (선수 offensive rating 반영)
        if 'ppg' in integrated and 'offensive_rating' in player_strength:
            league_avg = self.profile['avg_score']
            player_ortg = player_strength['offensive_rating']
            
            # 선수 능력치 기반 조정 (±15% 범위)
            ortg_factor = player_ortg / league_avg
            ortg_factor = max(0.85, min(1.15, ortg_factor))
            
            # 팀 평균 득점에 50% 반영 (나머지 50%는 기존 팀 데이터 유지)
            integrated['ppg'] = integrated['ppg'] * 0.5 + integrated['ppg'] * ortg_factor * 0.5
        
        # 수비력 조정 (선수 defensive rating 반영)
        if 'opp_ppg' in integrated and 'defensive_rating' in player_strength:
            league_avg = self.profile['avg_score']
            player_drtg = player_strength['defensive_rating']
            
            # 선수 능력치 기반 조정 (±15% 범위)
            drtg_factor = player_drtg / league_avg
            drtg_factor = max(0.85, min(1.15, drtg_factor))
            
            # 팀 평균 실점에 50% 반영
            integrated['opp_ppg'] = integrated['opp_ppg'] * 0.5 + integrated['opp_ppg'] * drtg_factor * 0.5
        
        # 선수 메트릭스 정보 추가
        integrated['player_metrics'] = {
            'overall_rating': player_strength.get('overall_rating', 15.0),
            'weighted_per': player_strength.get('weighted_per', 15.0),
            'weighted_bpm': player_strength.get('weighted_bpm', 0.0),
            'bench_strength': player_strength.get('bench_strength', 10.0),
            'top_players_count': len(player_strength.get('top_players', []))
        }
        
        return integrated

    def _predict_kbl_refactored(self, home_team, away_team, home_data, away_data,
                                weather, temperature, field_condition, match_importance,
                                rest_days_home, rest_days_away, injury_data=None, coaching_data=None,
                                lineup_home=None, lineup_away=None, home_players=None, away_players=None):
        """KBL 전용 개선된 예측 로직 (Net Rating + 가중치 블렌딩 + 로지스틱 확률)"""
        import math
        import random
        import numpy as np
        
        # scipy.stats.norm 대체 (KBL 특화)
        def kbl_norm_cdf(x, mu, sigma):
            return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))
        
        # 0. 데이터 무결성 체크 및 평균 추출
        # KBLDataFetcher에서 이미 블렌딩된 avg_points와 avg_allowed가 넘어옵니다.
        home_avg_p = home_data.get('avg_points', 82.0)
        home_avg_a = home_data.get('avg_allowed', 82.0)
        away_avg_p = away_data.get('avg_points', 82.0)
        away_avg_a = away_data.get('avg_allowed', 82.0)
        
        # 1. Net Rating 계산
        home_net = home_avg_p - home_avg_a
        away_net = away_avg_p - away_avg_a
        
        # 2. 최종 점수 차이 계산 (홈 어드밴티지 2.5 반영)
        # 사용자 요청: diff = home_net - away_net + 2.5
        total_diff = home_net - away_net + 2.5
        
        # 3. 승률 계산 (로지스틱 회귀 모델)
        # 사용자 요청: win_prob = 1 / (1 + exp(-diff / 5))
        home_win_prob = 1 / (1 + math.exp(-total_diff / 5.0))
        away_win_prob = 1 - home_win_prob
        
        # 4. 무승부 방지 (스코어 계산 전 미세 조정)
        if abs(total_diff) < 0.5:
            total_diff = random.choice([-1.5, 1.5])
            
        # 5. 예상 총 득점 계산 (KBL Pace 보정)
        # 사용자 요청: total = (home_avg + away_avg) * 0.97
        expected_total = (home_avg_p + away_avg_p) * 0.97
        
        # 6. 팀별 예상 득점 분배
        # home_score = total/2 + diff/2, away_score = total/2 - diff/2
        mean_home = expected_total / 2 + total_diff / 2
        mean_away = expected_total / 2 - total_diff / 2
        
        # 7. 현실적 범위 제한 (Clamping)
        h_score_val = max(65.0, min(100.0, float(mean_home)))
        a_score_val = max(65.0, min(100.0, float(mean_away)))
        
        # 최종 정수 점수 및 무승부 방지
        expected_score_home = int(round(h_score_val))
        expected_score_away = int(round(a_score_val))
        
        if expected_score_home == expected_score_away:
            if home_win_prob > 0.5: expected_score_home += 1
            else: expected_score_away += 1
            
        # 8. 상위 3개 스코어 분포 계산
        std_base = self.profile['std_base']
        scores = []
        for h_offset in [-0.5, 0, 0.5]:
            for a_offset in [-0.5, 0, 0.5]:
                h_s = int(np.clip(round(mean_home + h_offset * std_base), 60, 110))
                a_s = int(np.clip(round(mean_away + a_offset * std_base), 60, 110))
                prob_h = norm.pdf(h_s, loc=mean_home, scale=std_base)
                prob_a = norm.pdf(a_s, loc=mean_away, scale=std_base)
                scores.append(((h_s, a_s), prob_h * prob_a))
                
        scores.sort(key=lambda x: x[1], reverse=True)
        t_prob = sum(p for _, p in scores[:3])
        top_3_scores = [((h, a), p/t_prob) for (h, a), p in scores[:3]]
        
        # 9. 주요 요인 분석
        key_factors = [
            f"KBL 실시간 데이터 매핑: {home_avg_p:.1f} vs {away_avg_p:.1f} (팀 스탯 반영)",
            f"공수 효율 차이 (Net Rating): {home_net - away_net:+.1f}",
            "네이버 스포츠 Statistics API v2 기반 시즌 스탯 수집",
            "사용자 정의 로지스틱 회귀(Win Prob) 모델 적용"
        ]
        
        return {
            'home_win_prob': home_win_prob,
            'draw_prob': 0.0,
            'away_win_prob': away_win_prob,
            'expected_score_home': expected_score_home,
            'expected_score_away': expected_score_away,
            'top_3_scores': top_3_scores,
            'mean_home': round(mean_home, 1),
            'mean_away': round(mean_away, 1),
            'key_factors': key_factors,
            'confidence': 0.5 + abs(home_win_prob - 0.5) * 0.8,
            'model_type': 'KBL Precise Logistic V2',
            'sport_type': 'basketball',
            'league': self.league,
            'ranks': {
                'home_rank': home_data.get('rank', '-'),
                'away_rank': away_data.get('rank', '-')
            }
        }

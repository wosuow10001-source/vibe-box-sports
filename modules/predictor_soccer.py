"""
경기 예측 모듈
- Bivariate Poisson + Dixon-Coles 보정 기반 예측
- 득점 상관(λ_C) 반영으로 난타전/저득점 경기 구분
- 저득점 영역 보정으로 무승부 확률 정확도 향상
- 모든 요소 → λ → 스코어 분포 → 승률 (완전 연동)
- 고급 메트릭스 (xG, xA, PPDA) 통합
"""

import numpy as np
import pandas as pd
from math import factorial, exp
import pickle
from pathlib import Path
from modules.advanced_soccer_metrics import get_soccer_metrics
from modules.predictor_soccer_v3 import SoccerEngineV4


class SoccerPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        
        # Dixon-Coles 보정 파라미터
        self.rho = 0.1  # 득점 상관 계수 (학습 가능)
        
        # 고급 메트릭스 시스템
        self.advanced_metrics = None  # 리그별로 초기화
        
        # 리그별 보정 상수 (사용자 요청: Production-Grade Calibration)
        self.LEAGUE_CALIBRATION = {
            "EPL":        {"attack": 1.00, "draw_bias": 1.00, "home_adv": 1.12, "lambda_c": 0.30},
            "La Liga":    {"attack": 0.95, "draw_bias": 1.10, "home_adv": 1.15, "lambda_c": 0.28},
            "Serie A":    {"attack": 0.90, "draw_bias": 1.15, "home_adv": 1.10, "lambda_c": 0.20},
            "Bundesliga": {"attack": 1.10, "draw_bias": 0.95, "home_adv": 1.08, "lambda_c": 0.35},
            "K-League":   {"attack": 0.85, "draw_bias": 1.20, "home_adv": 1.08, "lambda_c": 0.25},
            "MLS":        {"attack": 1.15, "draw_bias": 0.85, "home_adv": 1.05, "lambda_c": 0.40}
        }
        
        # 가중치 설정 (사용자 요청 기반)
        self.weights = {
            'season_avg': 0.50,   # 시즌 전체 성적 50%
            'last_5_form': 0.30,  # 최근 5경기 폼 30%
            'last_10_form': 0.20, # 최근 10경기 폼 20%
            'home_advantage': 0.10,
            'player_condition': 0.10,
            'tactical_fit': 0.05,
            'weather': 0.05,
            'rest_days': 0.10,
            'injury_impact': 0.15,
            'coaching_staff': 0.05
        }
    
    def predict_match(self, league, home_team, away_team, home_data, away_data, 
                     weather, temperature, field_condition, match_importance,
                     rest_days_home, rest_days_away, injury_data=None, coaching_data=None,
                     lineup_home=None, lineup_away=None):
        """
        Bivariate Poisson Simulation 기반 경기 예측 (50,000회 시뮬레이션)
        """
        
        # 라인업 기반 팀 데이터 보강
        if lineup_home:
            home_data = self._enhance_team_data_with_lineup(home_data, lineup_home)
        if lineup_away:
            away_data = self._enhance_team_data_with_lineup(away_data, lineup_away)
        
        # ========== 1단계: 모든 요소 수치화 ==========
        form_score = self._analyze_form(home_data, away_data)
        home_advantage = self._calculate_home_advantage(home_data)
        player_condition = self._analyze_player_condition(
            home_data, away_data, rest_days_home, rest_days_away
        )
        tactical_score = self._analyze_tactical_fit(home_data, away_data)
        weather_impact = self._analyze_weather_impact(
            weather, temperature, field_condition
        )
        motivation_score = self._analyze_motivation(match_importance)
        rest_impact = self._analyze_rest_days(rest_days_home, rest_days_away)
        injury_impact = self._analyze_injury_impact(injury_data)
        coaching_impact = self._analyze_coaching_impact(coaching_data, home_data, away_data)
        
        # ========== 2단계: V3 엔진용 데이터 매핑 ==========
        # 리그 ID 정규화 (EPL, LA_LIGA, SERIE_A 등)
        league_id_map = {
            "EPL": "EPL", "La Liga": "LA_LIGA", "Serie A": "SERIE_A"
        }
        v3_league_id = league_id_map.get(league, "DEFAULT")
        
        # 피처 추출
        def extract_v3_features(team_data):
            return {
                "rank": team_data.get('rank', 10),
                "points": team_data.get('points', 0),
                "played": team_data.get('total_matches', team_data.get('played', 1)),
                "recent_form": team_data.get('recent_form', []),
                "avg_goals": team_data.get('avg_goals', 1.3),
                "avg_conceded": team_data.get('avg_conceded', 1.3),
                "goal_difference": team_data.get('goal_difference', 0),
                "points_per_game": team_data.get('points_per_game', 1.3)
            }
        
        home_features = extract_v3_features(home_data)
        away_features = extract_v3_features(away_data)
        
        # 경기 컨텍스트 매핑
        importance_map = {"일반": 0.5, "중요": 0.75, "매우중요": 1.0}
        context = {
            "importance": importance_map.get(match_importance, 0.5),
            "rest_days_home": rest_days_home,
            "rest_days_away": rest_days_away,
            "injuries_home": injury_data.get('home', []) if injury_data else [],
            "injuries_away": injury_data.get('away', []) if injury_data else [],
            "is_home": True
        }
        
        # ========== 3단계: 기대 득점 λ 계산 (폼/부상/날씨/휴식/코칭 반영) ==========
        # This was previously dead code - V4 ignored these values. Now passed as xg_override.
        lambda_home = self._calculate_expected_goals(
            league, home_data, away_data, True,
            form_score['home'], home_advantage, player_condition['home'],
            tactical_score['home'], weather_impact['home'], rest_impact['home'],
            motivation_score, injury_impact['home'], coaching_impact['home'],
            rest_days_home, rest_days_away, injury_data
        )
        lambda_away = self._calculate_expected_goals(
            league, away_data, home_data, False,
            form_score['away'], 0, player_condition['away'],
            tactical_score['away'], weather_impact['away'], rest_impact['away'],
            motivation_score, injury_impact['away'], coaching_impact['away'],
            rest_days_home, rest_days_away, injury_data
        )
        
        # ========== 4단계: V4 엔진 실행 (with enriched xG override) ==========
        engine = SoccerEngineV4()
        xg_override = {
            'home_xg': lambda_home,
            'away_xg': lambda_away
        }
        v4_res = engine.predict_match(v3_league_id, home_features, away_features, context, xg_override=xg_override)
        
        # ========== 4단계: 결과 정합성 및 UI 호환성 확보 ==========
        final_home_prob = v4_res['win_probabilities']['home']
        final_draw_prob = v4_res['win_probabilities']['draw']
        final_away_prob = v4_res['win_probabilities']['away']
        
        # 주요 영향 요인 식별
        key_factors = self._identify_key_factors(
            form_score, home_advantage, player_condition, 
            tactical_score, weather_impact, rest_impact, injury_impact, coaching_impact
        )
        
        # 베팅 인사이트
        betting_insight = self._generate_betting_insight({
            'home_win_prob': final_home_prob,
            'away_win_prob': final_away_prob,
            'over_2_5_prob': v4_res['markets']['over_2_5'],
            'btts_prob': v4_res['markets']['btts_yes']
        })
        
        # 스코어 형식 변환 (v4: score="1-0")
        top_5_scores = [((int(s['score'].split('-')[0]), int(s['score'].split('-')[1])), s['prob']) for s in v4_res['scorelines_top5']]
        
        return {
            'home_win_prob': final_home_prob,
            'draw_prob': final_draw_prob,
            'away_win_prob': final_away_prob,
            'expected_score_home': round(v4_res['expected_goals'].get('mean_home', lambda_home)),
            'expected_score_away': round(v4_res['expected_goals'].get('mean_away', lambda_away)),
            'top_3_scores': top_5_scores[:3],
            'top_5_scores': top_5_scores,
            'over_2_5_prob': v4_res['markets']['over_2_5'],
            'over_3_5_prob': v4_res['markets']['over_3_5'],
            'btts_prob': v4_res['markets']['btts_yes'],
            'double_chance': {
                '1X': final_home_prob + final_draw_prob,
                'X2': final_away_prob + final_draw_prob,
                '12': final_home_prob + final_away_prob
            },
            'lambda_home': v4_res['expected_goals']['home_xg'],
            'lambda_away': v4_res['expected_goals']['away_xg'],
            'game_state': v4_res['analysis']['game_state'],
            'upset_mode': v4_res['analysis']['upset_mode'],
            'confidence': v4_res['analysis']['confidence'],
            'summary_hints': v4_res['meta']['summary_hints'],
            'key_factors': key_factors,
            'betting_insight': betting_insight,
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

    def _run_simulation(self, lambda_home, lambda_away, lambda_c, league_name, num_sims=50000):
        """Bivariate Poisson 시뮬레이션 엔진 (50,000회)"""
        import numpy as np
        
        # 리그 보정값
        league_cal = self.LEAGUE_CALIBRATION.get(league_name, self.LEAGUE_CALIBRATION["EPL"])
        draw_bias = league_cal["draw_bias"]
        
        # Bivariate Poisson Components
        # X ~ Poisson(L1 + L3), Y ~ Poisson(L2 + L3)
        # where L3 is correlation (lambda_c)
        l1 = max(0.01, lambda_home - lambda_c)
        l2 = max(0.01, lambda_away - lambda_c)
        l3 = lambda_c
        
        # 시뮬레이션 생성
        S1 = np.random.poisson(l1, num_sims)
        S2 = np.random.poisson(l2, num_sims)
        S3 = np.random.poisson(l3, num_sims)
        
        home_scores = S1 + S3
        away_scores = S2 + S3
        
        # 무승부 보정 (Draw Bias)
        # |xG diff| < 0.3 이면 무승부 확률 인위적 보정 (사용자 요청)
        if abs(lambda_home - lambda_away) < 0.3:
            # 기존 무승부 경기 중 일부를 유지하고, 박빙 경기에서 무승부 비중 조절
            # 시뮬레이션 상에서는 점수를 강제로 맞추는 방식보다 확률 분포에 가중치를 두는 것이 정석
            # 여기서는 결과 집계 시 draw_bias를 곱하여 확률을 재계산
            pass 

        # 결과 집계
        results = []
        for h, a in zip(home_scores, away_scores):
            results.append((int(h), int(a)))
        
        home_wins = sum(1 for h, a in results if h > a)
        draws = sum(1 for h, a in results if h == a)
        away_wins = sum(1 for h, a in results if h < a)
        
        # 무승부 편향 적용 (사용자 요청: |xG diff| < 0.25 시 무승부 확률 5-10% 증가)
        if abs(lambda_home - lambda_away) < 0.25:
            draws = int(draws * draw_bias * 1.1)
            total = home_wins + draws + away_wins
            home_win_p = home_wins / total
            draw_p = draws / total
            away_win_p = away_wins / total
        else:
            total = num_sims
            home_win_p = home_wins / total
            draw_p = draws / total
            away_win_p = away_wins / total
            
        # 스코어 분포 계산
        score_counts = {}
        for r in results:
            score_counts[r] = score_counts.get(r, 0) + 1
            
        # [Decisiveness Balance] 승리 확률 최상위 팀 정합성 보정 (Winner-Aligned Score Selection)
        # 단순히 빈도수 1위가 아닌, 승리 확률이 확실히 높을 때만 해당 팀의 승리 스코어를 선택
        top_5 = sorted(score_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 결정력 보정: 승리 확률 차이가 15%p 이상일 때만 승리 스코어 강제 권장 (중위권 박빙성 존중)
        diff_prob = abs(home_win_p - away_win_p)
        favored_score = top_5[0][0]
        
        if diff_prob > 0.15: # 8%p -> 15%p로 문턱 상향 (박빙 상황 무승부 보존)
            winner_scores = []
            if home_win_p > away_win_p:
                winner_scores = sorted([(k, v) for k, v in score_counts.items() if k[0] > k[1]], key=lambda x: x[1], reverse=True)
            else:
                winner_scores = sorted([(k, v) for k, v in score_counts.items() if k[0] < k[1]], key=lambda x: x[1], reverse=True)
            
            if winner_scores:
                favored_score = winner_scores[0][0]
                
        top_5_scores = [((s[0], s[1]), s[1]/num_sims) for s in top_5]
        
        # 베팅 메트릭스
        over_2_5 = sum(1 for h, a in results if h + a > 2.5) / num_sims
        over_3_5 = sum(1 for h, a in results if h + a > 3.5) / num_sims
        btts = sum(1 for h, a in results if h > 0 and a > 0) / num_sims
        
        # 더블 찬스
        dc_1x = (home_wins + draws) / num_sims
        dc_x2 = (away_wins + draws) / num_sims
        dc_12 = (home_wins + away_wins) / num_sims
        
        return {
            'home_win_prob': home_win_p,
            'draw_prob': draw_p,
            'away_win_prob': away_win_p,
            'expected_score_home': int(favored_score[0]),
            'expected_score_away': int(favored_score[1]),
            'top_5_scores': top_5_scores,
            'over_2_5_prob': over_2_5,
            'over_3_5_prob': over_3_5,
            'btts_prob': btts,
            'double_chance': {'1X': dc_1x, 'X2': dc_x2, '12': dc_12}
        }

    def _generate_betting_insight(self, sim):
        """최적의 베팅 인사이트 추출 (EV 기준)"""
        insights = []
        if sim['home_win_prob'] > 0.65:
            insights.append(f"홈팀 승리 강력 추천 ({sim['home_win_prob']:.1%})")
        elif sim['away_win_prob'] > 0.65:
            insights.append(f"원정팀 승리 강력 추천 ({sim['away_win_prob']:.1%})")
            
        if sim['over_2_5_prob'] > 0.70:
            insights.append(f"다득점(Over 2.5) 경기 예상")
        elif sim['over_2_5_prob'] < 0.35:
            insights.append(f"저득점(Under 2.5) 경기 예상")
            
        if sim['btts_prob'] > 0.75:
            insights.append("양팀 모두 득점 가능성(BTTS) 매우 높음")
            
        return insights[0] if insights else "박빙의 경기가 예상되므로 신중한 접근 권장"
    
    def _analyze_form(self, home_data, away_data):
        """최근 폼 분석 (50% 시즌, 30% L5, 20% L10)"""
        
        def calculate_weighted_form(team_data):
            # 1. 시즌 평균 승률 (50%)
            wins = team_data.get('wins', 0)
            losses = team_data.get('losses', 0)
            draws = team_data.get('draws', 0)
            total = wins + draws + losses
            season_avg = (wins + draws * 0.5) / max(total, 1) if total > 0 else 0.5
            
            # 2. 최근 5경기 (30%)
            recent_form = team_data.get('recent_form', [])
            l5_recent = recent_form[:5]
            l5_val = sum(1 if r == 'W' else 0.5 if r == 'D' else 0 for r in l5_recent) / max(len(l5_recent), 1) if l5_recent else 0.5
            
            # 3. 최근 10경기 (20%)
            l10_recent = recent_form[:10]
            l10_val = sum(1 if r == 'W' else 0.5 if r == 'D' else 0 for r in l10_recent) / max(len(l10_recent), 1) if l10_recent else 0.5
            
            return (season_avg * self.weights['season_avg'] + 
                    l5_val * self.weights['last_5_form'] + 
                    l10_val * self.weights['last_10_form'])

        return {
            'home': calculate_weighted_form(home_data),
            'away': calculate_weighted_form(away_data)
        }
    
    def _calculate_home_advantage(self, home_data):
        """홈 어드밴티지 계산"""
        home_winrate = home_data.get('home_winrate', 0.5)
        
        # 홈 승률이 높을수록 어드밴티지 증가
        advantage = 0.1 + (home_winrate - 0.5) * 0.2
        
        return max(0.05, min(0.25, advantage))
    
    def _analyze_player_condition(self, home_data, away_data, 
                                  rest_days_home, rest_days_away):
        """선수 컨디션 분석 - 실제 선수 능력치 반영"""
        
        # 휴식일에 따른 컨디션
        optimal_rest = 4
        
        home_rest_factor = 1.0 - abs(rest_days_home - optimal_rest) * 0.05
        away_rest_factor = 1.0 - abs(rest_days_away - optimal_rest) * 0.05
        
        # 실제 선수 평균 능력치 반영
        home_player_rating = home_data.get('avg_player_rating', 7.0) / 10.0  # 0~1 범위로 정규화
        away_player_rating = away_data.get('avg_player_rating', 7.0) / 10.0
        
        # 실제 선수 컨디션 반영
        home_player_condition = home_data.get('avg_player_condition', 80) / 100.0  # 0~1 범위로 정규화
        away_player_condition = away_data.get('avg_player_condition', 80) / 100.0
        
        # 스쿼드 깊이 (부상 대응 능력)
        home_squad_depth = min(home_data.get('squad_depth', 20) / 25.0, 1.0)
        away_squad_depth = min(away_data.get('squad_depth', 20) / 25.0, 1.0)
        
        # 종합 컨디션 계산
        home_condition = (
            home_rest_factor * 0.3 +
            home_player_rating * 0.4 +
            home_player_condition * 0.2 +
            home_squad_depth * 0.1
        )
        
        away_condition = (
            away_rest_factor * 0.3 +
            away_player_rating * 0.4 +
            away_player_condition * 0.2 +
            away_squad_depth * 0.1
        )
        
        return {
            'home': max(0.3, min(1.0, home_condition)),
            'away': max(0.3, min(1.0, away_condition))
        }
        
        # 최근 경기 부하 (많이 뛸수록 피로도 증가)
        home_matches = len(home_data.get('recent_matches', []))
        away_matches = len(away_data.get('recent_matches', []))
        
        home_fatigue = max(0, 1.0 - home_matches * 0.02)
        away_fatigue = max(0, 1.0 - away_matches * 0.02)
        
        return {
            'home': (home_condition * 0.6 + home_fatigue * 0.4),
            'away': (away_condition * 0.6 + away_fatigue * 0.4)
        }
    
    def _analyze_tactical_fit(self, home_data, away_data):
        """전술적 궁합 분석"""
        
        # 점유율 기반 스타일 분석
        home_possession = home_data.get('possession_avg', 50)
        away_possession = away_data.get('possession_avg', 50)
        
        # 공격 vs 수비 성향
        home_goals = home_data.get('avg_goals', 1.5)
        home_conceded = home_data.get('avg_conceded', 1.5)
        away_goals = away_data.get('avg_goals', 1.5)
        away_conceded = away_data.get('avg_conceded', 1.5)
        
        # 공격력 vs 상대 수비력
        home_attack_vs_away_defense = home_goals / (away_conceded + 0.1)
        away_attack_vs_home_defense = away_goals / (home_conceded + 0.1)
        
        # 정규화 (ZeroDivisionError 방지)
        total = home_attack_vs_away_defense + away_attack_vs_home_defense
        
        if total == 0 or total < 0.01:
            # total이 0이거나 매우 작으면 균등 분배
            return {
                'home': 0.5,
                'away': 0.5
            }
        
        return {
            'home': home_attack_vs_away_defense / total,
            'away': away_attack_vs_home_defense / total
        }
    
    def _analyze_weather_impact(self, weather, temperature, field_condition):
        """날씨 영향 분석"""
        
        weather_scores = {
            '맑음': {'home': 0.5, 'away': 0.5},
            '흐림': {'home': 0.5, 'away': 0.5},
            '비': {'home': 0.55, 'away': 0.45},  # 홈팀이 약간 유리
            '눈': {'home': 0.6, 'away': 0.4},
            '강풍': {'home': 0.55, 'away': 0.45}
        }
        
        base_score = weather_scores.get(weather, {'home': 0.5, 'away': 0.5})
        
        # 극한 기온 영향
        if temperature < 5 or temperature > 35:
            base_score['home'] += 0.05  # 홈팀이 적응 유리
        
        # 경기장 상태
        field_scores = {
            '최상': 0,
            '양호': -0.02,
            '보통': -0.05,
            '불량': -0.1
        }
        
        field_penalty = field_scores.get(field_condition, 0)
        
        return {
            'home': max(0, base_score['home'] + field_penalty),
            'away': max(0, base_score['away'] + field_penalty)
        }
    
    def _analyze_motivation(self, match_importance):
        """경기 중요도에 따른 동기부여"""
        
        importance_scores = {
            '일반': 0.5,
            '중요': 0.7,
            '매우중요': 0.9
        }
        
        return importance_scores.get(match_importance, 0.5)
    
    def _analyze_rest_days(self, rest_days_home, rest_days_away):
        """휴식일 차이 분석"""
        
        optimal = 4
        
        home_score = 1.0 - abs(rest_days_home - optimal) * 0.05
        away_score = 1.0 - abs(rest_days_away - optimal) * 0.05
        
        return {
            'home': max(0.3, min(1.0, home_score)),
            'away': max(0.3, min(1.0, away_score))
        }
    
    def _analyze_injury_impact(self, injury_data):
        """
        부상 영향 분석
        
        Args:
            injury_data (dict): {'home': [...], 'away': [...]} 형태의 부상 정보
            
        Returns:
            dict: {'home': float, 'away': float} 부상 영향 점수 (0.0 ~ 1.0)
        """
        if not injury_data:
            return {'home': 1.0, 'away': 1.0}
        
        def calculate_team_injury_impact(injuries):
            """팀의 부상 영향 계산"""
            if not injuries:
                return 1.0
            
            # 부상 상태별 가중치
            status_weights = {
                'out': 0.15,           # 결장: 큰 영향
                'day-to-day': 0.05,    # 일일 점검: 작은 영향
                'questionable': 0.08,  # 출전 불투명: 중간 영향
                'doubtful': 0.12       # 출전 가능성 낮음: 큰 영향
            }
            
            total_impact = 0.0
            
            for injury in injuries:
                status = injury.get('status', '').lower()
                
                # 상태별 영향 계산
                impact = 0.0
                for key, weight in status_weights.items():
                    if key in status:
                        impact = weight
                        break
                
                # 포지션별 중요도
                position = injury.get('position', '').upper()
                position_multiplier = 1.0
                
                # NBA 포지션
                if 'G' in position and len(position) <= 2:  # Guard (G만 있는 경우)
                    position_multiplier = 1.2  # 가드는 플레이메이킹에 중요
                elif 'F' in position:  # Forward
                    position_multiplier = 1.1
                elif 'C' in position and len(position) <= 2:  # Center (C만 있는 경우)
                    position_multiplier = 1.15  # 센터는 수비/리바운드에 중요
                
                # 축구 포지션
                elif 'GK' in position:  # Goalkeeper
                    position_multiplier = 1.3  # 골키퍼는 매우 중요
                elif 'DF' in position or 'DEF' in position:  # Defender
                    position_multiplier = 1.1
                elif 'MF' in position or 'MID' in position:  # Midfielder
                    position_multiplier = 1.15  # 미드필더는 경기 흐름에 중요
                elif 'FW' in position or 'ST' in position or 'ATT' in position:  # Forward/Striker
                    position_multiplier = 1.2  # 공격수는 득점에 중요
                
                # MLB/KBO 포지션
                elif 'P' == position or 'SP' in position or 'RP' in position:  # Pitcher
                    position_multiplier = 1.3  # 투수는 매우 중요
                elif 'C' == position:  # Catcher (C만 있는 경우)
                    position_multiplier = 1.15  # 포수는 중요
                elif 'SS' in position or '2B' in position:  # Shortstop, Second Base
                    position_multiplier = 1.15  # 중요 내야수
                elif '1B' in position or '3B' in position:  # First Base, Third Base
                    position_multiplier = 1.1
                elif 'OF' in position or 'LF' in position or 'CF' in position or 'RF' in position:  # Outfield
                    position_multiplier = 1.1
                elif 'DH' in position:  # Designated Hitter
                    position_multiplier = 1.2  # 타격 전문
                
                # 배구 포지션
                elif 'OH' in position:  # Outside Hitter
                    position_multiplier = 1.25  # 주공격수
                elif 'MB' in position:  # Middle Blocker
                    position_multiplier = 1.2  # 블로킹 중요
                elif 'S' in position and len(position) <= 2:  # Setter
                    position_multiplier = 1.3  # 세터는 매우 중요
                elif 'OP' in position:  # Opposite
                    position_multiplier = 1.2  # 공격수
                elif 'L' in position and len(position) <= 2:  # Libero
                    position_multiplier = 1.1  # 수비 전문
                
                total_impact += impact * position_multiplier
            
            # 최종 점수 계산 (부상이 많을수록 점수 감소)
            # 최대 5명까지 영향 고려
            final_score = 1.0 - min(total_impact, 0.7)
            
            return max(0.3, final_score)  # 최소 0.3 보장
        
        home_injuries = injury_data.get('home', [])
        away_injuries = injury_data.get('away', [])
        
        return {
            'home': calculate_team_injury_impact(home_injuries),
            'away': calculate_team_injury_impact(away_injuries)
        }
    
    def _analyze_coaching_impact(self, coaching_data, home_data, away_data):
        """
        코칭스태프 영향 분석
        - 감독의 경력과 성과
        - 코칭스태프 규모
        - 팀 성적과의 상관관계
        """
        if not coaching_data:
            return {'home': 0.75, 'away': 0.75}  # 기본값
        
        def calculate_coaching_score(staff_info, team_data):
            """개별 팀의 코칭스태프 점수 계산"""
            if not staff_info or staff_info.get('head_coach') == 'Unknown':
                return 0.75  # 정보 없을 때 중립
            
            score = 0.5  # 기본 점수
            
            # 1. 코칭스태프 규모 (많을수록 유리)
            num_coaches = len(staff_info.get('assistant_coaches', []))
            if num_coaches >= 8:
                score += 0.15
            elif num_coaches >= 5:
                score += 0.10
            elif num_coaches >= 3:
                score += 0.05
            
            # 2. 팀 성적 반영 (감독의 능력 간접 평가)
            team_position = team_data.get('position', 10)
            if team_position <= 3:  # 상위권
                score += 0.25
            elif team_position <= 7:  # 중상위권
                score += 0.15
            elif team_position <= 12:  # 중위권
                score += 0.05
            
            # 3. 최근 폼 (감독의 전술 효과)
            recent_winrate = team_data.get('recent_winrate', 0.5)
            if recent_winrate >= 0.7:
                score += 0.15
            elif recent_winrate >= 0.5:
                score += 0.10
            elif recent_winrate >= 0.3:
                score += 0.05
            
            return min(1.0, max(0.3, score))  # 0.3 ~ 1.0 범위
        
        home_coaching = calculate_coaching_score(
            coaching_data.get('home'), home_data
        )
        away_coaching = calculate_coaching_score(
            coaching_data.get('away'), away_data
        )
        
        return {
            'home': home_coaching,
            'away': away_coaching
        }

    def _calculate_expected_goals(self, league, team_data, opponent_data, is_home,
                                  form, home_advantage, player_condition, tactical,
                                  weather, rest, motivation, injury, coaching,
                                  rest_days_home, rest_days_away, injury_data=None):
        """
        포아송 분포의 λ (기대 득점) 계산 (리그 보강, 순위 보정 및 동적 모디파이어 반영)
        """
        league_cal = self.LEAGUE_CALIBRATION.get(league, self.LEAGUE_CALIBRATION["EPL"])
        league_attack_f = league_cal["attack"]
        league_home_adv = league_cal["home_adv"]
        
        # ========== 1. 기본 실력 반영 (시즌 평균 + 고급 메트릭스) ==========
        team_goals = team_data.get('avg_goals', 1.5)
        opp_conceded = opponent_data.get('avg_conceded', 1.5)
        
        # xG (기대 득점) 반영: 데이터가 있으면 40% 가중치 부여
        # xG가 0.00인 경우(누락 시) 순위 기반 추정 xG 주입 (Sanity Check)
        my_rank = team_data.get('rank', 10)
        opp_rank = opponent_data.get('rank', 10)
        
        raw_xg = team_data.get('xg', team_data.get('team_xg', 0.0))
        if raw_xg <= 0.01:
            # 추정 xG: 순위가 높을수록 높은 xG 부여 (기존 1.8 -> 1.6 으로 평탄화)
            raw_xg = 1.6 - (my_rank * 0.03) 
        
        raw_xga = opponent_data.get('xga', opponent_data.get('team_xg_conceded', 0.0))
        if raw_xga <= 0.01:
            raw_xga = 1.2 + (opp_rank * 0.03)

        # [Sanity Check] 데이터 누락/오류로 인한 0.00 방지 하한선 설정
        min_stat = 1.1 if my_rank <= 5 else 0.9 if my_rank <= 12 else 0.7
        
        effective_team_goals = max(min_stat, team_goals * 0.7 + raw_xg * 0.3) # 가중치 0.6:0.4 -> 0.7:0.3 조정
        effective_opp_conceded = max(min_stat, opp_conceded * 0.7 + raw_xga * 0.3)
        
        base_lambda = (effective_team_goals + effective_opp_conceded) / 2
        base_lambda *= league_attack_f
        
        if is_home:
            base_lambda *= league_home_adv
            
        # ========== 2. 리그 순위 및 전력 차이 보정 (Balance 원복) ==========
        # 순위 차이에 의한 보정 (순위 1위 차이당 1.2% 보정 - 과한 뻥튀기 억제)
        rank_diff = opp_rank - my_rank # 내가 순위가 높으면(숫자가 작으면) 양수
        rank_bonus = 1.0 + (rank_diff * 0.012)
        
        # 전력 차가 매우 큰 경우(8위 차 이상) 점진적 보정 가속
        if abs(rank_diff) >= 8:
            rank_bonus = 1.0 + (rank_diff * 0.015) 
            
        base_lambda *= max(0.75, min(1.25, rank_bonus))
            
        # ========== 3. 동적 컨텐츠 모디파이어 (V5: 가산식 → 인플레이션 방지) ==========
        # 이전: 5개 요소를 곱셈(×1.05×1.04×1.02...) → 복리 효과로 20~50% 뻥튀기
        # 개선: 각 요소를 ±% 델타로 변환, 합산 후 ±15% 캡
        
        # 폼 반영 (form: 0~1 범위, 0.5 = 중립)
        form_delta = (form - 0.5) * 0.16          # ±8% max
        
        # 선수 컨디션 (player_condition: 0.3~1.0 범위)
        cond_delta = (player_condition - 0.65) * 0.12  # ±4% max
        
        # 전술 궁합 (tactical: 0~1 범위)
        tact_delta = (tactical - 0.5) * 0.08      # ±4% max
        
        # 날씨 영향
        weather_val = weather if isinstance(weather, (int, float)) else 0.5
        weat_delta = (weather_val - 0.5) * 0.06   # ±3% max
        
        # 코칭 영향
        coac_delta = (coaching - 0.65) * 0.06     # ±2% max
        
        # 휴식일 차이 (기존 곱셈 → 가산 델타)
        rest_delta = 0.0
        rest_diff = rest_days_home - rest_days_away
        if is_home and rest_diff >= 2:
            rest_delta = 0.03
        elif not is_home and rest_diff <= -2:
            rest_delta = 0.03
            
        # MLS 특별 모디파이어: 여행 거리
        travel_delta = 0.0
        if league == "MLS":
            travel_dist = team_data.get('travel_distance', 0)
            if travel_dist > 2000:
                travel_delta = -0.06
            elif travel_dist > 1000:
                travel_delta = -0.03

        # 날씨 템포 감쇠 (폭염/폭설)
        extreme_weather_delta = 0.0
        if weather in ['폭염', '폭설']:
            extreme_weather_delta = -0.08
            
        # 부상 영향 (키 포지션별 상세 보정)
        injury_delta = 0.0
        if injury_data:
            home_injuries = injury_data.get('home', [])
            away_injuries = injury_data.get('away', [])
            my_injuries = home_injuries if is_home else away_injuries
            opp_injuries = away_injuries if is_home else home_injuries
            
            for f_inj in my_injuries:
                if any(pos in f_inj.get('position', '').upper() for pos in ['FW', 'ST', 'ATT']):
                    injury_delta -= 0.10  # 주요 공격수 결장 시 -10%
                    break
            for d_inj in opp_injuries:
                if any(pos in d_inj.get('position', '').upper() for pos in ['DF', 'DEF', 'GK']):
                    injury_delta += 0.08  # 상대 주요 수비수 결장 시 +8%
                    break

        # 모든 델타 합산 (±15% 캡으로 인플레이션 제어)
        total_delta = (
            form_delta + cond_delta + tact_delta + 
            weat_delta + coac_delta + rest_delta + 
            travel_delta + extreme_weather_delta + injury_delta
        )
        total_delta = max(-0.15, min(0.15, total_delta))
        
        final_lambda = base_lambda * (1.0 + total_delta)
        
        # 하드 캡: V4 max_xg_cap(3.0)과 일치
        return max(0.3, min(3.5, final_lambda))

    def _predict_ml_outcome_probs(self, home_data, away_data, league, 
                                weather_impact, rest_impact, injury_impact, coaching_impact,
                                form_score, rank_diff):
        """
        Gradient Boosting 기반 승/무/패 확률 보정
        (실제 데이터 학습 전까지는 정교한 ML Heuristic 사용)
        """
        # 기본 확률 (팀간 전력차 기반)
        home_rating = home_data.get('avg_goals', 1.5) - home_data.get('avg_conceded', 1.5)
        away_rating = away_data.get('avg_goals', 1.5) - away_data.get('avg_conceded', 1.5)
        rating_diff = home_rating - away_rating
        
        # 리그별 특성 반영
        league_cal = self.LEAGUE_CALIBRATION.get(league, self.LEAGUE_CALIBRATION["EPL"])
        draw_bias = league_cal["draw_bias"]
        
        # 피처 중요 가중치 (XGBoost 시뮬레이션)
        # 1. 전력차 (Rating Diff)
        # 2. 최근 폼 (Form Diff)
        # 3. 홈 어드밴티지
        # 4. 부상/코칭
        
        h_prob = 0.33 + (rating_diff * 0.1) + ((form_score['home'] - form_score['away']) * 0.15)
        h_prob += (league_cal['home_adv'] - 1.0) * 0.5
        
        # 무승부 경향성 반영
        d_prob = 0.25 * draw_bias
        if abs(rating_diff) < 0.2:
            d_prob += 0.05
            
        a_prob = 1.0 - h_prob - d_prob
        
        # 범위 클리핑
        h_p = max(0.05, min(0.85, h_prob))
        d_p = max(0.05, min(0.45, d_prob))
        a_p = max(0.05, min(0.85, a_prob))
        
        # 정규화
        total = h_p + d_p + a_p
        return {'home': h_p/total, 'draw': d_p/total, 'away': a_p/total}

    def self_calibrate(self, league, actual_results):
        """
        시스템 자기 학습 (시즌 종료 후 또는 주기적 호출)
        league_attack_factor = actual_goals / xG 기반 보정
        """
        # TODO: 실제 경기 결과 데이터를 수집하여 LEAGUE_CALIBRATION 자동 업데이트 로직 구현
        pass

        
    def _dixon_coles_correction(self, home_goals, away_goals, lambda_home, lambda_away):
        """
        Dixon-Coles 저득점 영역 보정
        0:0, 1:0, 0:1, 1:1 스코어의 확률을 현실적으로 조정
        
        Args:
            home_goals, away_goals: 스코어
            lambda_home, lambda_away: 기대 득점
            
        Returns:
            float: 보정 계수 (1.0 = 보정 없음)
        """
        if home_goals == 0 and away_goals == 0:
            # 0:0 무승부 - 실제로는 포아송보다 적게 발생
            return 1 - lambda_home * lambda_away * self.rho
        elif home_goals == 0 and away_goals == 1:
            # 0:1 - 약간 보정
            return 1 + lambda_home * self.rho
        elif home_goals == 1 and away_goals == 0:
            # 1:0 - 약간 보정
            return 1 + lambda_away * self.rho
        elif home_goals == 1 and away_goals == 1:
            # 1:1 무승부 - 실제로는 포아송보다 많이 발생
            return 1 - self.rho
        else:
            return 1.0
    
    def _bivariate_poisson_pmf(self, home_goals, away_goals, lambda_home, lambda_away, lambda_c):
        """
        Bivariate Poisson 확률 질량 함수
        득점 상관(λ_C)을 반영하여 난타전/저득점 경기 구분
        
        Args:
            home_goals, away_goals: 스코어
            lambda_home, lambda_away: 각 팀 기대 득점
            lambda_c: 득점 상관 파라미터 (경기 템포)
            
        Returns:
            float: 해당 스코어의 확률
        """
        # 독립 포아송 성분
        lambda_home_ind = lambda_home - lambda_c
        lambda_away_ind = lambda_away - lambda_c
        
        # 음수 방지
        lambda_home_ind = max(0.01, lambda_home_ind)
        lambda_away_ind = max(0.01, lambda_away_ind)
        
        # Bivariate Poisson 확률 계산
        prob = 0.0
        min_goals = min(home_goals, away_goals)
        
        for k in range(min_goals + 1):
            term = (
                exp(-lambda_home_ind - lambda_away_ind - lambda_c) *
                (lambda_home_ind ** (home_goals - k)) / factorial(home_goals - k) *
                (lambda_away_ind ** (away_goals - k)) / factorial(away_goals - k) *
                (lambda_c ** k) / factorial(k)
            )
            prob += term
        
        # Dixon-Coles 보정 적용
        correction = self._dixon_coles_correction(home_goals, away_goals, lambda_home, lambda_away)
        prob *= correction
        
        return prob
    
    def _calculate_score_distribution(self, lambda_home, lambda_away, lambda_c, max_goals=8):
        """
        Bivariate Poisson + Dixon-Coles 보정으로 스코어 확률 분포 계산
        
        Args:
            lambda_home: 홈팀 기대 득점
            lambda_away: 원정팀 기대 득점
            lambda_c: 득점 상관 (경기 템포, 0 = 수비적, 0.3+ = 공격적)
            max_goals: 계산할 최대 골 수
            
        Returns:
            dict: 승률, 무승부율, 가장 가능성 높은 스코어, 상위 3개 스코어
        """
        
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        
        score_probs = {}
        
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                # Bivariate Poisson + Dixon-Coles 확률
                prob = self._bivariate_poisson_pmf(
                    home_goals, away_goals, 
                    lambda_home, lambda_away, lambda_c
                )
                
                score_probs[(home_goals, away_goals)] = prob
                
                # 승·무·패 확률 누적
                if home_goals > away_goals:
                    home_win_prob += prob
                elif home_goals == away_goals:
                    draw_prob += prob
                else:
                    away_win_prob += prob
        
        # 확률 정규화 (합이 1이 되도록)
        total_prob = sum(score_probs.values())
        if total_prob > 0:
            score_probs = {k: v/total_prob for k, v in score_probs.items()}
            home_win_prob /= total_prob
            draw_prob /= total_prob
            away_win_prob /= total_prob
        
        # 가장 가능성 높은 스코어 Top 3
        top_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)[:3]
        most_likely_score = top_scores[0][0]
        
        return {
            'home_win_prob': home_win_prob,
            'draw_prob': draw_prob,
            'away_win_prob': away_win_prob,
            'most_likely_score': most_likely_score,
            'top_3_scores': [(score, prob) for score, prob in top_scores],
            'score_probs': score_probs
        }
    
    def _identify_key_factors(self, form_score, home_advantage, 
                             player_condition, tactical_score, 
                             weather_impact, rest_impact, injury_impact, coaching_impact):
        """주요 영향 요인 식별"""
        
        factors = []
        
        # 폼 차이
        form_diff = abs(form_score['home'] - form_score['away'])
        if form_diff > 0.2:
            better_team = "홈팀" if form_score['home'] > form_score['away'] else "원정팀"
            factors.append(f"최근 폼: {better_team}이 우세 ({form_diff:.1%} 차이)")
        
        # 홈 어드밴티지
        if home_advantage > 0.15:
            factors.append(f"강력한 홈 어드밴티지 ({home_advantage:.1%})")
        
        # 컨디션 차이
        condition_diff = abs(player_condition['home'] - player_condition['away'])
        if condition_diff > 0.15:
            better_team = "홈팀" if player_condition['home'] > player_condition['away'] else "원정팀"
            factors.append(f"선수 컨디션: {better_team}이 우세")
        
        # 부상 영향
        if injury_impact:
            injury_diff = abs(injury_impact['home'] - injury_impact['away'])
            if injury_diff > 0.15:
                better_team = "홈팀" if injury_impact['home'] > injury_impact['away'] else "원정팀"
                worse_team = "원정팀" if injury_impact['home'] > injury_impact['away'] else "홈팀"
                factors.append(f"부상 영향: {worse_team}에 주요 선수 부상")
        
        # 코칭스태프 영향 (새로 추가)
        if coaching_impact:
            coaching_diff = abs(coaching_impact['home'] - coaching_impact['away'])
            if coaching_diff > 0.15:
                better_team = "홈팀" if coaching_impact['home'] > coaching_impact['away'] else "원정팀"
                factors.append(f"코칭스태프: {better_team}의 감독/코치진이 우세")
        
        # 전술적 궁합
        tactical_diff = abs(tactical_score['home'] - tactical_score['away'])
        if tactical_diff > 0.15:
            factors.append("전술적 궁합이 경기에 큰 영향")
        
        # 날씨
        weather_diff = abs(weather_impact['home'] - weather_impact['away'])
        if weather_diff > 0.1:
            factors.append("날씨 조건이 경기에 영향")
        
        if not factors:
            factors.append("양팀 전력이 비슷하여 접전 예상")
        
        return factors
    
    def _calculate_confidence(self, home_data, away_data, 
                             home_prob, away_prob, draw_prob):
        """예측 신뢰도 계산"""
        
        # 확률 분포가 명확할수록 신뢰도 높음
        max_prob = max(home_prob, away_prob, draw_prob)
        prob_spread = max_prob - min(home_prob, away_prob, draw_prob)
        
        # 데이터 품질 (경기 수가 많을수록 신뢰도 높음)
        home_matches = len(home_data.get('recent_matches', []))
        away_matches = len(away_data.get('recent_matches', []))
        data_quality = min(1.0, (home_matches + away_matches) / 20)
        
        # 종합 신뢰도
        confidence = (prob_spread * 0.6 + data_quality * 0.4)
        
        return min(0.95, max(0.5, confidence))
    
    def train_model(self, historical_data):
        """과거 데이터로 모델 학습"""
        
        # 특성 추출
        X = self._extract_features(historical_data)
        y = historical_data['result']  # 0: 원정승, 1: 무승부, 2: 홈승
        
        # 모델 학습
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        # 모델 저장
        self.save_model()
    
    def _extract_features(self, data):
        """특성 추출"""
        # 실제 구현 시 다양한 특성 추출
        pass
    
    def save_model(self):
        """모델 저장"""
        model_file = self.model_path / "predictor_model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)
    
    def load_model(self):
        """저장된 모델 로드"""
        model_file = self.model_path / "predictor_model.pkl"
        if model_file.exists():
            with open(model_file, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
    
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
        enhanced_data['formation'] = lineup.get('formation', '4-4-2')
        enhanced_data['tactic'] = lineup.get('tactic', '균형형')
        
        return enhanced_data
    
    def _enhance_team_data_with_advanced_metrics(self, team_data: dict, 
                                                 players: list, league: str = "K-League") -> dict:
        """
        고급 메트릭스(xG, xA, PPDA)로 팀 데이터 보강
        
        Args:
            team_data: 기존 팀 데이터
            players: 선수 리스트
            league: 리그 이름
        
        Returns:
            보강된 팀 데이터
        """
        if not players:
            return team_data
        
        # 리그별 고급 메트릭스 시스템 초기화
        if self.advanced_metrics is None or self.advanced_metrics.league != league:
            self.advanced_metrics = get_soccer_metrics(league)
        
        enhanced_data = team_data.copy()
        
        # 선수 메트릭스 기반 팀 전력 계산
        team_strength = self.advanced_metrics.calculate_team_strength_from_players(players)
        
        # xG 기반 득점력 반영
        if 'avg_goals' in enhanced_data:
            # 기존 득점과 xG 기반 득점을 혼합 (70% 기존 + 30% xG)
            xg_goals = team_strength['expected_goals']
            enhanced_data['avg_goals'] = enhanced_data['avg_goals'] * 0.7 + xg_goals * 0.3
        else:
            enhanced_data['avg_goals'] = team_strength['expected_goals']
        
        # 수비력 반영
        if 'avg_conceded' in enhanced_data:
            # 기존 실점과 xG 기반 실점을 혼합
            xg_conceded = team_strength['expected_conceded']
            enhanced_data['avg_conceded'] = enhanced_data['avg_conceded'] * 0.7 + xg_conceded * 0.3
        else:
            enhanced_data['avg_conceded'] = team_strength['expected_conceded']
        
        # 고급 메트릭스 저장
        enhanced_data['team_xg'] = team_strength['team_xg']
        enhanced_data['team_xa'] = team_strength['team_xa']
        enhanced_data['team_defensive'] = team_strength['team_defensive']
        enhanced_data['advanced_attack_rating'] = team_strength['attack_rating']
        enhanced_data['advanced_defense_rating'] = team_strength['defense_rating']
        
        return enhanced_data
    
    def load_model(self):
        """저장된 모델 로드"""
        model_file = self.model_path / "predictor_model.pkl"
        if model_file.exists():
            with open(model_file, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']

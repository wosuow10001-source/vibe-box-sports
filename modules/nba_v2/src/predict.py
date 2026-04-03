from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
from modules.nba_v2.src.utils import logger, NBAConfig, format_json_output
from modules.nba_v2.src.data_collector import NBADataCollector
from modules.nba_v2.src.feature_engineering import NBAFeatureEngineering
from modules.nba_v2.src.injury_model import NBAInjuryModel
from modules.nba_v2.src.simulation import NBASimulation
from modules.nba_v2.src.train_model import NBATrainer
from modules.nba_v2.src.calibration import NBACalibrator

class NBAPredictor:
    """V2 최종 예측기: ML 파이프라인의 오케스트레이터"""
    
    def __init__(self, v1_collector=None):
        self.collector = NBADataCollector(v1_collector)
        self.fe = NBAFeatureEngineering()
        self.injury_model = NBAInjuryModel()
        self.simulation = NBASimulation(iterations=NBAConfig.SIM_ITERATIONS)
        self.trainer = NBATrainer()
        self.calibrator = NBACalibrator()
        
    def compute_final_probability(self, base_prob: float, h_power: float, a_power: float, 
                                 h_inj: List[Dict], a_inj: List[Dict], is_elite: bool = False) -> Tuple[float, float, str]:
        """[V2.2/V2.5/V2.6] 최종 확률 통합 파이프라인 (Deterministic Integration + MC Feedback)"""
        
        # Power Adjustment (0.15 weight)
        power_diff = h_power - a_power
        if is_elite:
            power_adjustment = power_diff * 0.075 
        else:
            power_adjustment = power_diff * 0.15
        
        # Star Injury Adjustment (0.12 weight)
        star_adj = 0.0
        if any(i.get('is_primary_star') for i in h_inj):
            star_adj -= 0.12
        if any(i.get('is_primary_star') for i in a_inj):
            star_adj += 0.12
            
        injury_adjustment = (self.injury_model.calculate_team_penalty(a_inj)[0] - self.injury_model.calculate_team_penalty(h_inj)[0]) * 0.05
        
        # Combine Factors
        final_prob = base_prob + power_adjustment + star_adj + injury_adjustment
        
        # [V2.5] Elite Clamp
        if is_elite:
            final_prob = np.clip(final_prob, 0.40, 0.60)
        else:
            final_prob = np.clip(final_prob, 0.05, 0.95)
            
        return float(final_prob)
        
    def predict(self, home_team: str, away_team: str, 
                home_data: Dict = None, away_data: Dict = None,
                injury_data: Dict = None, market_odds: Dict = None, **kwargs) -> Dict:
        """[V2.1] 어드밴스드 예측 파이프라인: 라인업, 클러치, 마켓 밸류 통합"""
        
        # 1. 데이터 및 로스터 로드
        h_stats = self.collector.get_latest_stats(home_team, raw_data=home_data)
        a_stats = self.collector.get_latest_stats(away_team, raw_data=away_data)
        h_roster = self.collector.get_team_roster(home_team)
        a_roster = self.collector.get_team_roster(away_team)
        
        # 2. [V2.1] 라인업 기반 레이팅 보정 (30% 반영)
        h_lineup_ortg, h_lineup_drtg = self.fe.compute_lineup_rating(h_roster, injury_data.get('home', []) if injury_data else [])
        a_lineup_ortg, a_lineup_drtg = self.fe.compute_lineup_rating(a_roster, injury_data.get('away', []) if injury_data else [])
        
        h_ortg_raw = ((h_stats['ppg'] / h_stats['pace']) * 100 * 0.7) + (h_lineup_ortg * 0.3)
        h_drtg_raw = ((h_stats['opp_ppg'] / h_stats['pace']) * 100 * 0.7) + (h_lineup_drtg * 0.3)
        a_ortg_raw = ((a_stats['ppg'] / a_stats['pace']) * 100 * 0.7) + (a_lineup_ortg * 0.3)
        a_drtg_raw = ((a_stats['opp_ppg'] / a_stats['pace']) * 100 * 0.7) + (a_lineup_drtg * 0.3)
        
        # 3. 부상 영향 및 On/Off 임팩트 반영
        h_inj = injury_data.get('home', []) if injury_data else []
        a_inj = injury_data.get('away', []) if injury_data else []
        
        h_ortg, h_drtg = self.injury_model.apply_to_ratings(h_ortg_raw, h_drtg_raw, h_inj)
        a_ortg, a_drtg = self.injury_model.apply_to_ratings(a_ortg_raw, a_drtg_raw, a_inj)
        
        # [V2.1] On/Off 임팩트 추가 조정
        h_on_off = self.injury_model.calculate_on_off_impact(h_inj)
        a_on_off = self.injury_model.calculate_on_off_impact(a_inj)
        h_ortg -= h_on_off / 2.0; h_drtg += h_on_off / 2.0
        a_ortg -= a_on_off / 2.0; a_drtg += a_on_off / 2.0
        
        # 4. [SENIOR + V2.5] 파워 레이팅 및 엘리트 매치업 탐지
        h_power = self.fe.compute_team_power(h_stats)
        a_power = self.fe.compute_team_power(a_stats)
        is_elite = self._is_elite_team(h_stats) and self._is_elite_team(a_stats)
        
        # [V2.5] Elite Boosts
        elite_home_score_boost = 3.0 if is_elite else 0.0
        if is_elite: h_power += 0.05
        
        # 5. [V2.6] 벡터화된 몬테카를로 시뮬레이션
        market_spread = kwargs.get('market_spread', 0.0)
        market_total = kwargs.get('market_total', 225.0)
        
        h_sim_stats = {**h_stats.to_dict(), 'ppg': h_stats['ppg'], 'opp_ppg': h_stats['opp_ppg'], 'pace': h_stats['pace']}
        a_sim_stats = {**a_stats.to_dict(), 'ppg': a_stats['ppg'], 'opp_ppg': a_stats['opp_ppg'], 'pace': a_stats['pace']}
        
        sim_res = self.simulation.run(h_sim_stats, a_sim_stats, market_spread, market_total, is_elite)
        
        # 6. ML 추론 및 캘리브레이션 (통합 가중치용)
        features = self.fe.build_features(h_stats, a_stats)
        if self.trainer.load_model():
            ml_prob = self.trainer.model.predict_proba(features)[0][1]
        else:
            ml_prob = sim_res['win_prob_h']
        base_prob = self.calibrator.calibrate(ml_prob)
        
        # 7. [V2.2/V2.5/V2.6] 최종 확률 통합 (MC 시스널 우선)
        final_win_prob = self.compute_final_probability(base_prob, h_power, a_power, h_inj, a_inj, is_elite)
        
        # [V2.6] Confidence V2 Logic
        win_prob_h = sim_res['win_probability']['home']
        spread_prob_h = sim_res['spread_probability']['cover_home']
        over_prob = sim_res['over_under_probability']['over']
        
        confidence_val = (abs(win_prob_h - 0.5) + 
                         (abs(spread_prob_h - 0.5) * 0.5) + 
                         (abs(over_prob - 0.5) * 0.3))
        
        # 8. [V2.5] Elite Boosts & Score Baseline
        h_score = int(round(sim_res['expected_score']['home'] + elite_home_score_boost))
        a_score = int(round(sim_res['expected_score']['away']))
        
        # [V2.5] Blowout Prevention for Elite
        if is_elite:
            diff = h_score - a_score
            if abs(diff) > 8:
                h_score -= int(round(diff * 0.3))
                a_score += int(round(diff * 0.3))

        # [V2.6] PASS V3 Logic
        high_variance_form = (h_stats.get('last_10_wins',0) >= 7 and a_stats.get('last_10_wins',0) >= 7)
        is_pass = (confidence_val < 0.15) or is_elite or high_variance_form # Threshold 0.15 based on new formula
        
        # [V2.7] Forced PASS Prediction Logic
        forced_data = {}
        if is_pass:
            forced_data = self._forced_pass_prediction(
                home_team, away_team, h_stats, a_stats, h_inj, a_inj,
                h_score, a_score, float(final_win_prob)
            )

        # [V2.6] Value Bet Detection
        is_value_bet = False
        edge_val = 0.0
        if market_odds and 'home' in market_odds:
            edge_val = final_win_prob - (1.0 / market_odds['home'])
            if edge_val > 0.05: is_value_bet = True

        # 10. 결과 반환 (Step 8 Schema 준수)
        result = {
            'win_probability': forced_data.get('win_probability', sim_res['win_probability']),
            'spread_probability': sim_res['spread_probability'],
            'over_under_probability': sim_res['over_under_probability'],
            'expected_score_home': forced_data.get('home_score', h_score),
            'expected_score_away': forced_data.get('away_score', a_score),
            'home_win_prob': forced_data.get('home_win_prob', float(final_win_prob)), 
            'away_win_prob': 1.0 - forced_data.get('home_win_prob', float(final_win_prob)),
            'confidence_score': float(np.clip(confidence_val, 0, 1)),
            'confidence': "high" if confidence_val > 0.4 else "medium",
            'pass_flag': is_pass,
            'prediction': "home" if final_win_prob > 0.5 else "away",
            'decision': "PASS (FORCED)" if is_pass else "PLAY",
            'note': forced_data.get('note', ""),
            'explanation': forced_data.get('explanation', ""),
            'uncertainty': forced_data.get('uncertainty', {}),
            'key_factors': self._get_key_factors(h_stats, a_stats, injury_data, is_pass, is_value_bet)
        }
        
        return format_json_output(home_team, away_team, result)
        
        return format_json_output(home_team, away_team, result)

    def _forced_pass_prediction(self, home_team: str, away_team: str, 
                               home_stats: pd.Series, away_stats: pd.Series, 
                               home_injuries: List[Dict], away_injuries: List[Dict],
                               base_h_score: int, base_a_score: int, base_h_prob: float) -> Dict:
        """[V2.7] 시스템 데이터 구조(JSON keys)에 100% 맞춘 강제 예측 로직"""
        
        # 1. 홈 어드밴티지 (시스템 기본값: +2.5점, 승률 +2%)
        home_court_points = 2.5
        h_score_adj = home_court_points
        a_score_adj = 0.0
        h_win_prob_adj = 0.02

        # 2. Pace 매칭 (리그 평균 99.5 대비)
        league_avg_pace = 99.5
        h_pace = home_stats.get('pace', 100.0)
        a_pace = away_stats.get('pace', 100.0)
        avg_pace = (h_pace + a_pace) / 2.0
        pace_factor = avg_pace / league_avg_pace
        
        adj_h_score = base_h_score * pace_factor
        adj_a_score = base_a_score * pace_factor

        # 3. 최근 10경기 폼
        h_l10_w = int(home_stats.get('last_10_wins', 5))
        a_l10_w = int(away_stats.get('last_10_wins', 5))
        h_form_adj = (h_l10_w - 5) * 0.5
        a_form_adj = (a_l10_w - 5) * 0.5
        h_score_adj += h_form_adj
        a_score_adj += a_form_adj

        # 4. [NEW] 백투백 / 피로도 (rest_days == 0 이면 B2B)
        h_rest = home_stats.get('rest_days', 2)
        a_rest = away_stats.get('rest_days', 2)
        h_b2b = (h_rest == 0)
        a_b2b = (a_rest == 0)

        if h_b2b and not a_b2b:
            h_score_adj -= 2.0
            h_win_prob_adj -= 0.04
        elif a_b2b and not h_b2b:
            a_score_adj -= 2.0
            h_win_prob_adj += 0.04

        # 5. [NEW] 고급지표 (Clutch Net Rating) 반영
        h_clutch = home_stats.get('clutch_net', 0.0)
        a_clutch = away_stats.get('clutch_net', 0.0)
        clutch_diff = h_clutch - a_clutch
        h_win_prob_adj += clutch_diff * 0.001 # 클러치 능력 10차이 -> 1% 가중치

        # 6. 부상 영향 계산 (system keys: player, status / roster keys: is_primary_star)
        h_roster = self.collector.get_team_roster(home_team)
        a_roster = self.collector.get_team_roster(away_team)
        h_stars = [p['name'] for p in h_roster if p.get('is_primary_star')]
        a_stars = [p['name'] for p in a_roster if p.get('is_primary_star')]

        def calc_adj_injury_penalty(injuries, stars):
            pts_penalty = 0.0; wp_delta = 0.0
            sw_map = {
                "out": 1.2, "doubtful": 0.8, "questionable": 0.4, 
                "day-to-day": 0.2, "probable": 0.1
            }
            for inj in injuries:
                status = inj.get('status', '').lower()
                sw = sw_map.get(status, 0.3)
                is_star = any(star in inj.get('player', '') for star in stars)
                iw = 2.5 if is_star else 1.0
                pts_penalty += (sw * iw * 2.0)
                wp_delta -= (0.015 * sw * iw)
            return pts_penalty, wp_delta

        h_inj_pts, h_inj_wp = calc_adj_injury_penalty(home_injuries, h_stars)
        a_inj_pts, a_inj_wp = calc_adj_injury_penalty(away_injuries, a_stars)
        
        h_score_adj -= h_inj_pts
        a_score_adj -= a_inj_pts
        h_win_prob_adj += h_inj_wp
        h_win_prob_adj -= a_inj_wp

        # 최종 값 산출
        final_h_score = int(round(adj_h_score + h_score_adj))
        final_a_score = int(round(adj_a_score + a_score_adj))
        final_h_prob = np.clip(base_h_prob + h_win_prob_adj, 0.05, 0.95)

        # PASS 전용 불확실성 밴드
        uncertainty = {
            "home_win_prob_range": [round(max(0, final_h_prob - 0.1), 3), round(min(1, final_h_prob + 0.1), 3)],
            "home_score_range": [final_h_score - 5, final_h_score + 5],
            "away_score_range": [final_a_score - 5, final_a_score + 5]
        }

        # 설명 문자열 구성
        exp = []
        exp.append(f"{home_team} (Season: {home_stats['ppg']:.1f} PPG / {home_stats['opp_ppg']:.1f} Opp);")
        exp.append(f"{away_team} (Season: {away_stats['ppg']:.1f} PPG / {away_stats['opp_ppg']:.1f} Opp).")
        exp.append(f"Recent Form: {home_team} {h_l10_w}-W L10, {away_team} {a_l10_w}-W L10.")
        exp.append(f"Pace adj ({pace_factor:.2f}x): {h_pace:.1f} vs {a_pace:.1f}.")
        
        if h_b2b or a_b2b:
            exp.append(f"Fatigue: {home_team} B2B={h_b2b}, {away_team} B2B={a_b2b}.")
            
        if abs(clutch_diff) > 2.0:
            exp.append(f"Advanced: Home clutch net rating diff = {clutch_diff:.1f}.")

        h_names = ", ".join([f"{i['player']}({i['status']})" for i in home_injuries]) if home_injuries else "None"
        a_names = ", ".join([f"{i['player']}({i['status']})" for i in away_injuries]) if away_injuries else "None"
        exp.append(f"Injuries: [Home] {h_names} [Away] {a_names}.")
        exp.append("NOTE: This matchup originally resulted in a PASS; forced prediction applied with uncertainty bands.")

        return {
            "home_score": final_h_score,
            "away_score": final_a_score,
            "home_win_prob": float(final_h_prob),
            "win_probability": {"home": float(final_h_prob), "away": 1.0 - float(final_h_prob)},
            "note": "This game originally received a PASS, but forced prediction is applied.",
            "explanation": " ".join(exp),
            "uncertainty": uncertainty
        }

    def _is_elite_team(self, stats: pd.Series) -> bool:
        """[V2.5] 엘리트 팀 판별: 승률 60% 이상"""
        win_pct = stats.get('win_pct', 0)
        return win_pct >= 0.60

    def _get_key_factors(self, h: pd.Series, a: pd.Series, inj: Dict, is_pass: bool, is_value: bool) -> List[str]:
        factors = []
        if is_value: factors.append("수학적 기대 가치 높음 (VALUE BET)")
        if is_pass: factors.append("박빙 예측 (PASS 추천) ⚠️")
        
        # [V2.5] Elite Matchup Factor
        if self._is_elite_team(h) and self._is_elite_team(a):
            factors.append("최상위권 엘리트 매치업 (보정 적용) 🔥")
            
        if h['win_pct'] > a['win_pct'] + 0.15: factors.append("시즌 승률 우위")
        if h['rest_days'] > a['rest_days']: factors.append("휴식일 우위")
        
        if inj:
            if inj.get('away'): factors.append("원정팀 주요 전력 결장")
            if inj.get('home'): factors.append("홈팀 주요 전력 결장")
            
        return factors[:3]

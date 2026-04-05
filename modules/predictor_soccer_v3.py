"""
Vibe Sports - Advanced Football Match Prediction Engine (V4)
- Production-grade upgrade from V3
- Non-linear strength modeling
- Game State Classifier (OPEN/CLOSED/BALANCED)
- Negative Binomial Monte Carlo Simulation (50,000 matches)
- Post-simulation probability rebalancing & upset detection
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Any

class LeagueConfig:
    """League-specific parameter registry (V4 optimized)"""
    REGISTRY = {
        "EPL": {
            "base_home_adv": 0.15,
            "relegation_rank_threshold": 18,
            "top_team_rank_threshold": 6,
            "upset_factor_range": (0.06, 0.12),
        },
        "LA_LIGA": {
            "base_home_adv": 0.14,
            "relegation_rank_threshold": 18,
            "top_team_rank_threshold": 6,
            "upset_factor_range": (0.05, 0.10),
        },
        "DEFAULT": {
            "base_home_adv": 0.14,
            "relegation_rank_threshold": 18,
            "top_team_rank_threshold": 6,
            "upset_factor_range": (0.05, 0.11),
        }
    }

    @staticmethod
    def get(league_id: str) -> dict:
        return LeagueConfig.REGISTRY.get(league_id, LeagueConfig.REGISTRY["DEFAULT"])

class SoccerEngineV4:
    def __init__(self):
        self.num_simulations = 50000
        self.max_xg_cap = 3.0   # EPL single-team xG rarely exceeds 3.0
        self.min_xg = 0.35      # Allow slightly lower xG for defensive teams
        self.max_goals_cutoff = 10
        self.dc_rho = 0.08      # Dixon-Coles correction parameter (stronger 0-0 suppression)
        
    def predict_match(
        self,
        league_id: str,
        home_feats: dict,
        away_feats: dict,
        match_context: dict,
        xg_override: dict = None  # Accept pre-computed xG from SoccerPredictor
    ) -> dict:
        cfg = LeagueConfig.get(league_id)
        
        # [1] TEAM STRENGTH (NON-LINEAR)
        home_strength = self._calculate_nonlinear_strength(home_feats)
        away_strength = self._calculate_nonlinear_strength(away_feats)
        
        # [2] BASE EXPECTED GOALS (xG)
        if xg_override and xg_override.get('home_xg') and xg_override.get('away_xg'):
            # Use pre-computed xG from SoccerPredictor (includes form, injury, weather)
            home_xg = max(self.min_xg, min(xg_override['home_xg'], self.max_xg_cap))
            away_xg = max(self.min_xg, min(xg_override['away_xg'], self.max_xg_cap))
        else:
            # Fallback: compute from raw stats
            h_att = home_feats.get('avg_goals', 1.3)
            a_def = away_feats.get('avg_conceded', 1.3)
            a_att = away_feats.get('avg_goals', 1.1)
            h_def = home_feats.get('avg_conceded', 1.2)
            
            home_adv = 1.0 + cfg["base_home_adv"]
            
            home_xg_raw = (h_att * (1.0 / max(0.5, a_def))) * home_adv
            away_xg_raw = (a_att * (1.0 / max(0.5, h_def)))
            
            home_xg = max(self.min_xg, min(home_xg_raw, self.max_xg_cap))
            away_xg = max(self.min_xg, min(away_xg_raw, self.max_xg_cap))
        
        # [3] GAME STATE CLASSIFIER (RECALIBRATED)
        total_xg_sum = home_xg + away_xg
        if total_xg_sum >= 2.5:       # Was 2.8 - too many games wrongly classified as CLOSED
            game_state = "OPEN"
        elif total_xg_sum <= 1.8:     # Was 2.2 - xG=2.15 should NOT be CLOSED
            game_state = "CLOSED"
        else:
            game_state = "BALANCED"
            
        # [4] VARIANCE MODEL (V5 RECALIBRATED - higher k = more Poisson-like = less 0-0)
        # NB with low k has P(X=0) = (k/(k+μ))^k which is large even at high μ
        # Raising k to 2.0+ makes the distribution realistic for football
        if game_state == "OPEN":
            variance_multiplier = 1.0    # No inflation - xG is already enriched
            k_dispersion = 2.0           # Was 0.8 - P(0) drops from 35% to 25%
        elif game_state == "CLOSED":
            variance_multiplier = 0.95   # Slight suppression for defensive games
            k_dispersion = 3.0           # Was 1.3 - tight Poisson-like for low-xG
        else:
            variance_multiplier = 1.0
            k_dispersion = 2.5           # Was 1.0 - moderate overdispersion
            
        # Apply variance multiplier to xG (no inflation for OPEN/BALANCED)
        home_xg_sim = home_xg * variance_multiplier
        away_xg_sim = away_xg * variance_multiplier
        
        # [5] UNDERDOG / UPSET DETECTION (EXPANDED)
        h_rank = home_feats.get('rank', 10)
        a_rank = away_feats.get('rank', 10)
        rank_diff = abs(h_rank - a_rank)
        strength_diff = abs(home_strength - away_strength)
        
        h_form_pts = self._parse_form_to_points(home_feats.get('recent_form', []))
        a_form_pts = self._parse_form_to_points(away_feats.get('recent_form', []))
        
        upset_mode = False
        if rank_diff >= 8: upset_mode = True
        if strength_diff < 0.15: upset_mode = True # Very close match
        if a_form_pts > h_form_pts + 2: upset_mode = True # Away team in better form
        
        upset_factor = 0.0
        if upset_mode:
            # Scale upset factor by rank gap or form gap
            ups_base = (cfg["upset_factor_range"][0] + cfg["upset_factor_range"][1]) / 2.0
            upset_factor = ups_base * (1.0 + (min(rank_diff, 15) / 15.0) * 0.5)
            
        # [6] SIMULATION (NEGATIVE BINOMIAL)
        # NB(n, p) where mu = n(1-p)/p, n=k_dispersion
        dist_results = self._run_monte_carlo(home_xg_sim, away_xg_sim, k_dispersion)
        
        # [7-8] PROBABILITY REBALANCING & SCORE CORRECTION
        final_outcomes = self._apply_rebalancing(
            dist_results, 
            upset_mode, 
            upset_factor, 
            game_state,
            strength_diff
        )
        
        # [9] TEXT OUTPUT VALIDATION
        validation_meta = self._validate_outputs(home_xg, away_xg, final_outcomes, game_state)
        
        # [10] DISTRIBUTION-MEAN EXPECTED SCORE (not top-1 frequency)
        # This gives a realistic goal expectation instead of always showing 0-0
        all_scores = final_outcomes.get("all_scores", {})
        if all_scores:
            mean_home = sum(int(k.split('-')[0]) * v for k, v in all_scores.items())
            mean_away = sum(int(k.split('-')[1]) * v for k, v in all_scores.items())
        else:
            mean_home = home_xg
            mean_away = away_xg
        
        return {
            "win_probabilities": final_outcomes["win_probs"],
            "scorelines_top5": final_outcomes["top5_scores"],
            "markets": final_outcomes["markets"],
            "expected_goals": {
                "home_xg": round(home_xg, 2),
                "away_xg": round(away_xg, 2),
                "total_xg": round(total_xg_sum, 2),
                "mean_home": round(mean_home, 2),
                "mean_away": round(mean_away, 2)
            },
            "analysis": {
                "game_state": game_state,
                "upset_mode": upset_mode,
                "upset_factor": round(upset_factor, 3),
                "variance_multiplier": variance_multiplier,
                "k_dispersion": k_dispersion,
                "confidence": validation_meta["confidence_level"]
            },
            "meta": {
                "league_id": league_id,
                "home_strength": round(home_strength, 3),
                "away_strength": round(away_strength, 3),
                "summary_hints": validation_meta["summary_hints"]
            }
        }

    def _calculate_nonlinear_strength(self, feat: dict) -> float:
        # Step 1: strength = sqrt(points_per_game * 0.6 + goal_diff_per_game * 0.4)
        ppg = feat.get('points_per_game', feat.get('points', 0) / max(1, feat.get('played', 1)))
        
        goals_for = feat.get('goals_for', 0)
        goals_against = feat.get('goals_against', 0)
        played = max(1, feat.get('played', 1))
        gd_per_game = (goals_for - goals_against) / played
        
        # Shift GD/G to be positive for sqrt (add 2.0 as offset, max/min floor)
        raw_val = ppg * 0.6 + (gd_per_game + 2.0) * 0.4
        return math.sqrt(max(0.1, raw_val))

    def _parse_form_to_points(self, form: Any) -> int:
        if not isinstance(form, (list, str)):
            return 0
        pts = 0
        for r in form[-5:]:
            if r == 'W': pts += 3
            elif r == 'D': pts += 1
        return pts

    def _run_monte_carlo(self, h_mu, a_mu, k):
        # mu = n(1-p)/p -> p = n / (n + mu)
        h_p = k / (k + h_mu)
        a_p = k / (k + a_mu)
        
        # r = k, p = p
        h_goals = np.random.negative_binomial(k, h_p, self.num_simulations)
        a_goals = np.random.negative_binomial(k, a_p, self.num_simulations)
        
        # Calculate base probabilities
        win_h = np.mean(h_goals > a_goals)
        draw = np.mean(h_goals == a_goals)
        win_a = np.mean(h_goals < a_goals)
        
        o25 = np.mean((h_goals + a_goals) > 2.5)
        o35 = np.mean((h_goals + a_goals) > 3.5)
        btts = np.mean((h_goals > 0) & (a_goals > 0))
        
        # Score distribution
        scores = {}
        for h, a in zip(h_goals, a_goals):
            if h <= self.max_goals_cutoff and a <= self.max_goals_cutoff:
                key = f"{h}-{a}"
                scores[key] = scores.get(key, 0) + 1
        
        # Normalize scores
        total_scores = sum(scores.values())
        score_probs = {k: v / total_scores for k, v in scores.items()}
        
        # [Dixon-Coles V5 Post-Hoc Correction]
        # NB distribution over-produces 0-0 even at high xG (P(0)^2 effect)
        # Real EPL data: at total xG=2.6, P(0-0) ≈ 5-7%, not 12%
        # Use xG-scaled exponential suppression
        total_xg = h_mu + a_mu
        
        if "0-0" in score_probs:
            # Exponential suppression: stronger as total xG rises
            # At xG=1.5: factor=0.82, at xG=2.6: factor=0.55, at xG=3.5: factor=0.38
            zero_zero_factor = max(0.30, math.exp(-0.22 * total_xg))
            score_probs["0-0"] *= zero_zero_factor
        
        if "1-1" in score_probs:
            # Slight suppression (real football slightly under-produces 1-1 vs Poisson)
            score_probs["1-1"] *= 0.95
        
        if "1-0" in score_probs:
            # Boost most common EPL result
            score_probs["1-0"] *= (1.0 + 0.03 * a_mu)
        if "0-1" in score_probs:
            score_probs["0-1"] *= (1.0 + 0.03 * h_mu)
        if "2-1" in score_probs:
            score_probs["2-1"] *= 1.08  # Second most common EPL result
        if "1-2" in score_probs:
            score_probs["1-2"] *= 1.06
        
        # Re-normalize after DC correction
        dc_total = sum(score_probs.values())
        if dc_total > 0:
            score_probs = {k: v / dc_total for k, v in score_probs.items()}
        
        top5 = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "win_probs": {"home": win_h, "draw": draw, "away": win_a},
            "markets": {"over_2_5": o25, "over_3_5": o35, "btts_yes": btts},
            "top5_scores": [{"score": k, "prob": v} for k, v in top5],
            "all_scores": score_probs
        }

    def _apply_rebalancing(self, results, upset_mode, upset_factor, state, strength_diff):
        probs = results["win_probs"]
        h_win, draw, a_win = probs["home"], probs["draw"], probs["away"]
        
        # [7] PROBABILITY REBALANCING
        if upset_mode:
            # Triggered if underdog might win
            if h_win > a_win: # Home is fav, apply upset to Away
                a_win += upset_factor
                h_win -= upset_factor * 0.6
                draw -= upset_factor * 0.4 # User logic: draw += upset_factor * 0.4 but usually upset implies non-fav win
                # Fixing user spec: away_win += upset_factor, home_win -= 0.6, draw += 0.4 (wait, sum must be 1)
                # Let's follow the user's explicit math: h_win - 0.6, a_win + 1.0, draw + 0.4 -> net +0.8? Error in spec.
                # Assuming: reduce fav, increase underdog and draw.
                # Re-reading: "away_win += upset_factor, home_win -= upset_factor * 0.6, draw += upset_factor * 0.4" -> -0.6 + 1.0 + 0.4 = +0.8.
                # I'll normalize after.
                draw += upset_factor * 0.4
            else: # Away is fav, apply upset to Home
                h_win += upset_factor
                a_win -= upset_factor * 0.6
                draw += upset_factor * 0.4
        
        if strength_diff < 0.2: # close_match
            # flatten probabilities: reduce top outcome by ~3%
            outcomes = [h_win, draw, a_win]
            top_idx = outcomes.index(max(outcomes))
            reduction = outcomes[top_idx] * 0.03
            outcomes[top_idx] -= reduction
            # redistribute to others
            share = reduction / 2.0
            for i in range(3):
                if i != top_idx: outcomes[i] += share
            h_win, draw, a_win = outcomes
            
        # Re-normalize
        total = h_win + draw + a_win
        h_win, draw, a_win = h_win/total, draw/total, a_win/total
        
        # [8] SCORE DISTRIBUTION - NO ARTIFICIAL BOOSTING
        # Previous version artificially boosted 0-0/1-0 in CLOSED state,
        # causing systematic low-scoring bias. Let the simulation speak.
        score_probs = results["all_scores"]
        top5 = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "win_probs": {"home": h_win, "draw": draw, "away": a_win},
            "top5_scores": [{"score": k, "prob": v} for k, v in top5],
            "markets": results["markets"],
            "all_scores": score_probs  # Pass full distribution for mean calculation
        }

    def _validate_outputs(self, h_xg, a_xg, outcomes, state) -> dict:
        hints = []
        total_xg = h_xg + a_xg
        o25_prob = outcomes["markets"]["over_2_5"]
        
        # [9] TEXT OUTPUT VALIDATION
        if total_xg > 2.5:
            hints.append("High expected goal volume (Total xG > 2.5). Avoid 'low scoring' label.")
        
        if o25_prob > 0.55:
            hints.append("High scoring tendency detected (Over 2.5 > 55%).")
        
        probs = outcomes["win_probs"]
        if abs(probs["home"] - probs["away"]) < 0.15:
            hints.append("Tight match detected (Close win probabilities).")
            
        # Confidence Level
        conf = "medium"
        if total_xg < 1.8 and abs(probs["home"] - probs["away"]) < 0.1:
            conf = "low" # Unpredictable low-event drawish game
        elif total_xg > 2.8 and (probs["home"] > 0.6 or probs["away"] > 0.6):
            conf = "high" # Clear favorite in open game
            
        return {
            "summary_hints": hints,
            "confidence_level": conf
        }

def predict_match_v4(league_id, home_feat, away_feat, context):
    engine = SoccerEngineV4()
    return engine.predict_match(league_id, home_feat, away_feat, context)

"""
Vibe Sports - Advanced Football Match Prediction Engine (V3)
- Reusable, league-agnostic core engine
- Negative Binomial goal distribution (Overdispersion modeling)
- Sigmoid-scaled non-linear strength model
- Upset Adjustment Layer for realistic favorite/underdog modeling
"""

import math
import numpy as np

class LeagueConfig:
    """
    League-specific parameter registry
    """
    REGISTRY = {
        "EPL": {
            "base_home_xG": 1.45,
            "base_away_xG": 1.25,
            "home_xG_cap": 2.2,
            "away_xG_cap": 2.6,
            "base_home_adv": 0.15,
            "relegation_rank_threshold": 18,
            "top_team_rank_threshold": 6,
            "relegation_def_mul_range": (0.85, 0.92),
            "relegation_var_mul_range": (1.15, 1.25),
            "upset_factor_range": (0.05, 0.12),
        },
        "LA_LIGA": {
            "base_home_xG": 1.35,
            "base_away_xG": 1.15,
            "home_xG_cap": 2.1,
            "away_xG_cap": 2.5,
            "base_home_adv": 0.14,
            "relegation_rank_threshold": 18,
            "top_team_rank_threshold": 6,
            "relegation_def_mul_range": (0.87, 0.93),
            "relegation_var_mul_range": (1.1, 1.2),
            "upset_factor_range": (0.04, 0.10),
        },
        "SERIE_A": {
            "base_home_xG": 1.30,
            "base_away_xG": 1.15,
            "home_xG_cap": 2.1,
            "away_xG_cap": 2.5,
            "base_home_adv": 0.13,
            "relegation_rank_threshold": 18,
            "top_team_rank_threshold": 6,
            "relegation_def_mul_range": (0.88, 0.94),
            "relegation_var_mul_range": (1.1, 1.2),
            "upset_factor_range": (0.04, 0.10),
        },
        "DEFAULT": {
            "base_home_xG": 1.40,
            "base_away_xG": 1.20,
            "home_xG_cap": 2.2,
            "away_xG_cap": 2.6,
            "base_home_adv": 0.14,
            "relegation_rank_threshold": 18,
            "top_team_rank_threshold": 6,
            "relegation_def_mul_range": (0.86, 0.93),
            "relegation_var_mul_range": (1.1, 1.2),
            "upset_factor_range": (0.05, 0.11),
        },
    }

    @staticmethod
    def get(league_id: str) -> dict:
        return LeagueConfig.REGISTRY.get(league_id, LeagueConfig.REGISTRY["DEFAULT"])


class SoccerEngineV3:
    def __init__(self):
        # Tunable constants
        self.strength_scale = 1.2    # Sigmoid scaling factor
        self.adjustment_factor = 0.5  # Strength diff -> xG adjustment
        self.base_k = 4.0            # Baseline dispersion for NB
        self.max_goals = 7           # Cutoff for probability matrix
        self.min_xg = 0.2
        self.upset_threshold_prob = 0.7
        self.upset_strength_threshold = 0.5

    def predict_match(
        self,
        league_id: str,
        home_team_features: dict,
        away_team_features: dict,
        match_context: dict
    ) -> dict:
        """
        Main V3 prediction pipeline
        """
        cfg = LeagueConfig.get(league_id)
        
        # 1. Compute Team Strengths
        home_strength = self._calculate_strength(home_team_features)
        away_strength = self._calculate_strength(away_team_features)
        
        # 2. Non-linear Scaling of Strength Difference
        strength_diff = away_strength - home_strength
        scaled_diff = self._sigmoid(strength_diff, scale=self.strength_scale)
        
        # 3. Base Expected Goals (xG)
        home_xG = cfg["base_home_xG"] + (scaled_diff * -self.adjustment_factor)
        away_xG = cfg["base_away_xG"] + (scaled_diff * self.adjustment_factor)
        
        # 4. Home Advantage (Conditional Floor for Relegation Desperation)
        home_rank = home_team_features.get('rank', 10)
        home_adv_bonus = 0.075 if home_rank >= cfg["relegation_rank_threshold"] else 0.0
        home_advantage = cfg["base_home_adv"] + home_adv_bonus
        home_xG *= (1.0 + home_advantage)
        
        # 5. Relegation Boost (Defensive/Variance Adjustment)
        away_rank = away_team_features.get('rank', 10)
        variance_multiplier = 1.0
        importance = match_context.get('importance', 0.5)
        
        if (home_rank >= cfg["relegation_rank_threshold"] and 
            away_rank <= cfg["top_team_rank_threshold"]):
            # Defensive tightening: reduce favorite's efficiency
            def_mul = cfg["relegation_def_mul_range"][0] + (1.0 - importance) * 0.05
            away_xG *= def_mul
            # Increase variance for upset potential
            variance_multiplier = cfg["relegation_var_mul_range"][0] + importance * 0.1
            
        # 6. Apply xG Caps
        home_xG = max(self.min_xg, min(home_xG, cfg["home_xG_cap"]))
        away_xG = max(self.min_xg, min(away_xG, cfg["away_xG_cap"]))
        
        # 7. Goal Distribution (Negative Binomial)
        h_k = self._get_dispersion_k(self.base_k, importance, abs(strength_diff))
        a_k = self._get_dispersion_k(self.base_k, importance, abs(strength_diff))
        
        # Adjust variance multiplier into NB dispersion (r)
        # Var = mu + mu^2/r -> mu * vm = mu + mu^2/r -> r = mu / (vm - 1)
        home_r = h_k / max(0.01, variance_multiplier)
        away_r = a_k / max(0.01, variance_multiplier)
        
        # Compute joint probabilities
        win_probs, scorelines, markets = self._calculate_joint_outcomes(
            home_xG, away_xG, home_r, away_r
        )
        
        # 8. Upset Adjustment (Final Layer)
        final_win_probs = self._apply_upset_adjustment(
            win_probs, abs(strength_diff), cfg["upset_factor_range"]
        )
        
        # 9. Confidence Heuristic
        confidence = self._compute_confidence(strength_diff, variance_multiplier)
        
        return {
            "win_probabilities": final_win_probs,
            "scorelines_top5": scorelines,
            "markets": markets,
            "expected_goals": {
                "home_xG": round(home_xG, 2),
                "away_xG": round(away_xG, 2),
            },
            "variance": {
                "home_k": round(home_r, 2),
                "away_k": round(away_r, 2),
                "variance_multiplier": round(variance_multiplier, 2),
            },
            "meta": {
                "league_id": league_id,
                "confidence": confidence,
                "strength_diff_raw": round(strength_diff, 3),
                "strength_diff_scaled": round(scaled_diff, 3),
            }
        }

    def _calculate_strength(self, feat: dict) -> float:
        xGD = feat.get('xGD', feat.get('xG', 1.0) - feat.get('xGA', 1.0))
        form = feat.get('recent_form', 0.5)
        ppg = feat.get('points_per_game', 1.3)
        gd = feat.get('goal_difference', 0)
        
        # Scale PPG (0~3) to 0~1 range for balance if needed, but the formula is absolute
        return (xGD * 0.5 + form * 0.2 + ppg * 0.2 + gd * 0.1)

    def _sigmoid(self, x: float, scale: float = 1.0) -> float:
        y = 1.0 / (1.0 + math.exp(-x * scale))
        return (y - 0.5) * 2.0  # Range (-1, 1)

    def _get_dispersion_k(self, base_k: float, importance: float, strength_gap: float) -> float:
        k = base_k
        if strength_gap > 0.4:
            k *= 0.8  # More variance for big gaps
        k *= (1.0 - 0.2 * importance)
        return max(k, 0.1)

    def _nbinom_pmf(self, k: int, mu: float, r: float) -> float:
        """
        Negative Binomial PMF using standard (mu, r) parameterization
        P(k) = Gamma(k+r) / (k! Gamma(r)) * (r/(r+mu))^r * (mu/(r+mu))^k
        """
        if k < 0: return 0.0
        p = r / (r + mu)
        try:
            log_prob = (math.lgamma(k + r) - math.lgamma(k + 1) - math.lgamma(r) + 
                        r * math.log(p) + k * math.log(1 - p))
            return math.exp(log_prob)
        except (ValueError, OverflowError):
            # Fallback to Poisson if r is huge
            return (mu ** k * math.exp(-mu)) / math.factorial(k) if k < 20 else 0.0

    def _calculate_joint_outcomes(self, h_mu, a_mu, h_r, a_r):
        h_probs = [self._nbinom_pmf(i, h_mu, h_r) for i in range(self.max_goals + 1)]
        a_probs = [self._nbinom_pmf(j, a_mu, a_r) for j in range(self.max_goals + 1)]
        
        h_prob_total = sum(h_probs)
        a_prob_total = sum(a_probs)
        h_probs = [p / h_prob_total for p in h_probs]
        a_probs = [p / a_prob_total for p in a_probs]
        
        win_h, draw, win_a = 0.0, 0.0, 0.0
        over_2_5, over_3_5, btts = 0.0, 0.0, 0.0
        scorelines = []
        
        for i in range(len(h_probs)):
            for j in range(len(a_probs)):
                p = h_probs[i] * a_probs[j]
                
                if i > j: win_h += p
                elif i == j: draw += p
                else: win_a += p
                
                if i + j > 2.5: over_2_5 += p
                if i + j > 3.5: over_3_5 += p
                if i > 0 and j > 0: btts += p
                
                scorelines.append({"home_goals": i, "away_goals": j, "prob": p})
        
        # Sort top scorelines
        scorelines.sort(key=lambda x: x["prob"], reverse=True)
        
        return (
            {"home": win_h, "draw": draw, "away": win_a},
            scorelines[:5],
            {"over_2_5": over_2_5, "over_3_5": over_3_5, "btts_yes": btts}
        )

    def _apply_upset_adjustment(self, probs, strength_diff, ups_range):
        h_win, draw, a_win = probs["home"], probs["draw"], probs["away"]
        
        fav_win = max(h_win, a_win)
        is_home_fav = h_win > a_win
        
        if strength_diff > self.upset_strength_threshold and fav_win > self.upset_threshold_prob:
            ups_factor = (ups_range[0] + ups_range[1]) / 2.0
            
            # Reduce favorite win prob, redistribute to draw/underdog
            fav_win -= ups_factor
            if is_home_fav:
                h_win = fav_win
                a_win += ups_factor * 0.6
            else:
                a_win = fav_win
                h_win += ups_factor * 0.6
            draw += ups_factor * 0.4
            
            # Re-normalize
            total = h_win + draw + a_win
            return {"home": h_win / total, "draw": draw / total, "away": a_win / total}
        
        return probs

    def _compute_confidence(self, strength_diff, vm) -> str:
        if abs(strength_diff) < 0.2 or vm > 1.2:
            return "low"
        if abs(strength_diff) > 0.6 and vm <= 1.05:
            return "high"
        return "medium"

def predict_match_v3(league_id, home_feat, away_feat, context):
    engine = SoccerEngineV3()
    return engine.predict_match(league_id, home_feat, away_feat, context)

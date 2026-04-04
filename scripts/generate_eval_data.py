"""
Generate Dummy Football Prediction Data for Evaluation Tests
Matches spec for evaluation.py
"""

import pandas as pd
import numpy as np
import json
import random

def generate_data(num_matches=50):
    model_rows = []
    truth_rows = []
    
    leagues = ["EPL", "LA_LIGA", "SERIE_A"]
    teams = ["TeamA", "TeamB", "TeamC", "TeamD", "TeamE", "TeamF"]
    
    for i in range(num_matches):
        match_id = f"M{i:03d}"
        h_team = random.choice(teams)
        a_team = random.choice([t for t in teams if t != h_team])
        league = random.choice(leagues)
        
        # 1. Model Outputs
        # Simulate some variance
        h_p = random.uniform(0.1, 0.7)
        a_p = random.uniform(0.1, 1.0 - h_p - 0.1)
        d_p = 1.0 - h_p - a_p
        
        o25 = random.uniform(0.3, 0.8)
        o35 = o25 * random.uniform(0.4, 0.8)
        btts = random.uniform(0.4, 0.9)
        
        xg_h = random.uniform(0.5, 2.5)
        xg_a = random.uniform(0.5, 2.0)
        
        # Score distribution (Top 5 scores)
        scores = {"0-0": 0.1, "1-1": 0.15, "1-0": 0.12, "0-1": 0.08, "2-1": 0.07}
        # Add some noise to normalize
        total = sum(scores.values())
        scores = {k: v/total for k, v in scores.items()}
        
        model_rows.append({
            "match_id": match_id,
            "date": "2026-04-05",
            "league_id": league,
            "home_team": h_team,
            "away_team": a_team,
            "home_prob": h_p,
            "draw_prob": d_p,
            "away_prob": a_p,
            "over_2_5_prob": o25,
            "over_3_5_prob": o35,
            "btts_prob": btts,
            "xg_home": xg_h,
            "xg_away": xg_a,
            "confidence": random.choice(["high", "medium", "low"]),
            "scoreline_probs_json": json.dumps(scores),
            "text_summary": "박빙의 경기가 예상됩니다."
        })
        
        # 2. Ground Truth
        h_g = random.randint(0, 3)
        a_g = random.randint(0, 3)
        res = "H" if h_g > a_g else "A" if a_g > h_g else "D"
        
        truth_rows.append({
            "match_id": match_id,
            "home_goals": h_g,
            "away_goals": a_g,
            "result_1x2": res,
            "is_over_2_5": int((h_g + a_g) > 2.5),
            "is_over_3_5": int((h_g + a_g) > 3.5),
            "is_btts": int(h_g > 0 and a_g > 0)
        })
        
    pd.DataFrame(model_rows).to_csv("model_outputs.csv", index=False)
    pd.DataFrame(truth_rows).to_csv("ground_truth.csv", index=False)
    print(f"[OK] Generated {num_matches} matches in model_outputs.csv and ground_truth.csv")

if __name__ == "__main__":
    generate_data()

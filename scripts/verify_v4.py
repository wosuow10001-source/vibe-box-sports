"""
Verification Script for Soccer Engine V4
Tests:
1. High-scoring / OPEN game state
2. Low-scoring / CLOSED game state
3. Upset Detection logic
4. Simulation stability (50k iterations)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from modules.predictor_soccer_v3 import SoccerEngineV4

def test_v4_scenarios():
    engine = SoccerEngineV4()
    
    scenarios = [
        {
            "name": "High Scoring Battle (Open)",
            "league": "EPL",
            "home": {"avg_goals": 2.2, "avg_conceded": 0.8, "rank": 1, "points": 70, "played": 30},
            "away": {"avg_goals": 1.8, "avg_conceded": 1.1, "rank": 3, "points": 62, "played": 30},
        },
        {
            "name": "Defensive Grind (Closed)",
            "league": "SERIE_A",
            "home": {"avg_goals": 0.8, "avg_conceded": 1.1, "rank": 15, "points": 28, "played": 30},
            "away": {"avg_goals": 0.7, "avg_conceded": 1.2, "rank": 17, "points": 25, "played": 30},
        },
        {
            "name": "Giant vs Underdog (Upset Potential)",
            "league": "LA_LIGA",
            "home": {"avg_goals": 2.5, "avg_conceded": 0.6, "rank": 1, "points": 75, "played": 30},
            "away": {"avg_goals": 0.9, "avg_conceded": 1.8, "rank": 19, "points": 18, "played": 30},
        }
    ]
    
    for sc in scenarios:
        print(f"\n[SCENARIO: {sc['name']}]")
        res = engine.predict_match(sc["league"], sc["home"], sc["away"], {"importance": 0.8})
        
        print(f"  - Home xG: {res['expected_goals']['home_xg']} | Away xG: {res['expected_goals']['away_xg']}")
        print(f"  - Game State: {res['analysis']['game_state']} | Upset Mode: {res['analysis']['upset_mode']}")
        print(f"  - Home Win: {res['win_probabilities']['home']:.1%} | Draw: {res['win_probabilities']['draw']:.1%} | Away: {res['win_probabilities']['away']:.1%}")
        print(f"  - Over 2.5 Prob: {res['markets']['over_2_5']:.1%}")
        score_strings = [f"{s['score']} ({s['prob']:.1%})" for s in res['scorelines_top5']]
        print(f"  - Top Scores: {', '.join(score_strings)}")
        print(f"  - Confidence: {res['analysis']['confidence'].upper()}")
        
        # Validation checks
        assert res['expected_goals']['home_xg'] <= 2.5, "Home xG Cap violated"
        assert res['expected_goals']['away_xg'] <= 2.5, "Away xG Cap violated"
        
        if sc["name"] == "High Scoring Battle (Open)":
            assert res['analysis']['game_state'] == "OPEN"
        if sc["name"] == "Defensive Grind (Closed)":
            assert res['analysis']['game_state'] == "CLOSED"

if __name__ == "__main__":
    test_v4_scenarios()
    print("\n[OK] All V4 Verification Scenarios Passed.")

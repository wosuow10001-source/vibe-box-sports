import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from modules.predictor_soccer import SoccerPredictor

def test_upset_scenario():
    predictor = SoccerPredictor()
    
    # 울버햄튼 (20위) vs 리버풀 (5위) 데이터 재현
    home_data = {
        'rank': 20,
        'points': 17,
        'recent_winrate': 0.097,
        'home_winrate': 0.111,
        'avg_goals': 0.77,
        'avg_conceded': 1.8,
        'team_xg': 1.23,
        'team_xga': 2.0,
        'ppg': 0.8,
        'goal_difference': -25,
        'recent_form': ['L', 'L', 'D', 'L', 'W']
    }
    
    away_data = {
        'rank': 5,
        'points': 49,
        'recent_winrate': 0.452,
        'away_winrate': 0.384,
        'avg_goals': 1.60,
        'avg_conceded': 1.1,
        'team_xg': 1.8,
        'team_xga': 1.1,
        'ppg': 1.9,
        'goal_difference': 20,
        'recent_form': ['W', 'D', 'W', 'W', 'L']
    }
    
    print("\n=== Wolves (20th) vs Liverpool (5th) V3 Engine Test ===")
    
    res = predictor.predict_match(
        league="EPL",
        home_team="Wolves",
        away_team="Liverpool",
        home_data=home_data,
        away_data=away_data,
        weather="맑음",
        temperature=20,
        field_condition="최상",
        match_importance="일반",
        rest_days_home=3,
        rest_days_away=3
    )
    
    print(f"Home Win: {res['home_win_prob']:.1%}")
    print(f"Draw: {res['draw_prob']:.1%}")
    print(f"Away Win: {res['away_win_prob']:.1%}")
    print(f"Expected Score: {res['expected_score_home']} - {res['expected_score_away']}")
    print(f"Confidence: {res['confidence']}")
    print(f"Home xG (V3): {res['lambda_home']}")
    print(f"Away xG (V3): {res['lambda_away']}")
    print(f"Top 5 Scores:")
    for score, prob in res['top_5_scores']:
        print(f"  {score[0]}:{score[1]} ({prob:.1%})")

if __name__ == "__main__":
    test_upset_scenario()

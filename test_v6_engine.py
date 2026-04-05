
from modules.predictor_soccer import SoccerPredictor
import json

p = SoccerPredictor()
res = p.predict_match(
    'EPL', 'Arsenal', 'Man City', 
    {'team_name': 'Arsenal', 'rank': 1, 'points': 70, 'played': 30, 'avg_goals': 2.2, 'avg_conceded': 0.8, 'recent_form': ['W','W','W','W','D']},
    {'team_name': 'Man City', 'rank': 2, 'points': 68, 'played': 30, 'avg_goals': 2.3, 'avg_conceded': 1.0, 'recent_form': ['W','D','W','W','W']},
    '맑음', 20, '최상', '중요', 4, 4,
    injury_data={'home': [], 'away': []},
    coaching_data={'home': {'rating': 8}, 'away': {'rating': 9}}
)
print('V6 Ultra Prediction Result:')
print(f'Win Probs: H={res["home_win_prob"]*100:.1f}% D={res["draw_prob"]*100:.1f}% A={res["away_win_prob"]*100:.1f}%')
print(f'Expected Score: {res["expected_score_home"]} - {res["expected_score_away"]}')
print(f'Top-5 Scores: {res["top_5_scores"]}')

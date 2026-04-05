"""
V4 Engine Fix Verification Script
Newcastle vs Everton test case (actual result: 2-3)
"""
import sys
sys.path.insert(0, '.')

from modules.predictor_soccer import SoccerPredictor

def test_newcastle_everton():
    """Test the exact input from the user's report."""
    predictor = SoccerPredictor()
    
    home_data = {
        'rank': 12,
        'points': 42,
        'total_matches': 30,
        'recent_form': [],
        'avg_goals': 1.32,
        'avg_conceded': 1.3,
        'home_winrate': 0.445,
        'wins': 10, 'draws': 12, 'losses': 8,
        'goal_difference': 0,
        'points_per_game': 1.4,
        'recent_winrate': 0.387,
    }
    
    away_data = {
        'rank': 8,
        'points': 46,
        'total_matches': 30,
        'recent_form': [],
        'avg_goals': 1.48,
        'avg_conceded': 1.2,
        'away_winrate': 0.356,
        'wins': 12, 'draws': 10, 'losses': 8,
        'goal_difference': 5,
        'points_per_game': 1.53,
        'recent_winrate': 0.419,
    }
    
    injury_data = {
        'home': [{'name': 'Callum Wilson', 'status': 'Questionable', 'position': 'FW'}],
        'away': []
    }
    
    result = predictor.predict_match(
        league='EPL',
        home_team='Newcastle',
        away_team='Everton',
        home_data=home_data,
        away_data=away_data,
        weather='맑음',
        temperature=-10,
        field_condition='최상',
        match_importance='일반',
        rest_days_home=3,
        rest_days_away=3,
        injury_data=injury_data
    )
    
    print("\n" + "="*60)
    print("  NEWCASTLE vs EVERTON — V4 FIX VERIFICATION")
    print("  Actual Result: Newcastle 2 - 3 Everton")
    print("="*60)
    
    print(f"\n  Predicted Score:  {result['expected_score_home']} - {result['expected_score_away']}")
    print(f"  xG (λ):          Home {result['lambda_home']:.2f}  Away {result['lambda_away']:.2f}")
    print(f"  Total xG:         {result['lambda_home'] + result['lambda_away']:.2f}")
    print(f"  Game State:       {result['game_state']}")
    
    print(f"\n  Win Probabilities:")
    print(f"    Home:  {result['home_win_prob']*100:.1f}%")
    print(f"    Draw:  {result['draw_prob']*100:.1f}%")
    print(f"    Away:  {result['away_win_prob']*100:.1f}%")
    
    print(f"\n  Markets:")
    print(f"    Over 2.5: {result['over_2_5_prob']*100:.1f}%")
    print(f"    Over 3.5: {result['over_3_5_prob']*100:.1f}%")
    print(f"    BTTS:     {result['btts_prob']*100:.1f}%")
    
    print(f"\n  Top 5 Scorelines:")
    for i, (score, prob) in enumerate(result['top_5_scores'], 1):
        print(f"    {i}. {score[0]}-{score[1]}  ({prob*100:.1f}%)")
    
    # Assertions
    print(f"\n  === VERIFICATION CHECKS ===")
    checks = []
    
    # Check 1: Score is NOT 0-0
    is_not_00 = not (result['expected_score_home'] == 0 and result['expected_score_away'] == 0)
    checks.append(("Predicted score is NOT 0-0", is_not_00))
    
    # Check 2: Total xG > 1.5
    total_xg = result['lambda_home'] + result['lambda_away']
    checks.append((f"Total xG > 1.5 ({total_xg:.2f})", total_xg > 1.5))
    
    # Check 3: Over 2.5 > 30%
    checks.append((f"Over 2.5 > 30% ({result['over_2_5_prob']*100:.1f}%)", result['over_2_5_prob'] > 0.30))
    
    # Check 4: BTTS > 30%
    checks.append((f"BTTS > 30% ({result['btts_prob']*100:.1f}%)", result['btts_prob'] > 0.30))
    
    # Check 5: Game state is NOT CLOSED
    checks.append((f"Game state != CLOSED ({result['game_state']})", result['game_state'] != 'CLOSED'))
    
    # Check 6: Top scoreline is not 0-0
    top_score = result['top_5_scores'][0][0]
    checks.append((f"Top scoreline != 0-0 ({top_score[0]}-{top_score[1]})", top_score != (0, 0)))
    
    all_passed = True
    for desc, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"    {status}: {desc}")
        if not passed:
            all_passed = False
    
    print(f"\n  {'✅ ALL CHECKS PASSED' if all_passed else '❌ SOME CHECKS FAILED'}")
    print("="*60)
    
    return all_passed

if __name__ == '__main__':
    test_newcastle_everton()

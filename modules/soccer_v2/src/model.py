import numpy as np

def kleague_value_model(
    home_xG,
    away_xG,
    market_odds_home,
    market_odds_draw,
    market_odds_away,
    market_odds_over=1.9,
    market_odds_under=1.9,
    market_total=2.5,
    simulations=10000,
    seed=42
):
    """
    K-League Probabilistic Betting Model (Poisson-based)
    
    Args:
        home_xG (float): Expected goals for home team
        away_xG (float): Expected goals for away team
        market_odds_home (float): Market odds for Home Win
        market_odds_draw (float): Market odds for Draw
        market_odds_away (float): Market odds for Away Win
        market_odds_over (float): Market odds for Over [market_total]
        market_odds_under (float): Market odds for Under [market_total]
        market_total (float): The goal line for Over/Under markets
        simulations (int): Number of Monte Carlo iterations
        seed (int): Random seed for reproducibility
        
    Returns:
        dict: Detailed probabilities and betting recommendations
    """
    # 0. Set seed for reproducibility
    np.random.seed(seed)
    
    # 1. Simulate goals using Poisson distribution
    home_goals = np.random.poisson(home_xG, simulations)
    away_goals = np.random.poisson(away_xG, simulations)
    
    # 2. Compute Probabilities - Win/Draw/Loss
    home_win_prob = float(np.mean(home_goals > away_goals))
    draw_prob = float(np.mean(home_goals == away_goals))
    away_win_prob = float(np.mean(home_goals < away_goals))
    
    # 3. Compute Probabilities - Over/Under
    total_goals_sim = home_goals + away_goals
    if market_total is None: market_total = 2.5
    
    over_prob = float(np.mean(total_goals_sim > market_total))
    under_prob = float(np.mean(total_goals_sim <= market_total))
    
    # 4. Confidence Score
    # Formula: abs(h_win - 0.33) + abs(draw - 0.33) + abs(a_win - 0.33)
    confidence = abs(home_win_prob - 0.3333) + abs(draw_prob - 0.3333) + abs(away_win_prob - 0.3333)
    
    # 5. DRAW DETECTION SYSTEM (CRITICAL)
    # Trigger if xG difference is low AND total xG is low
    draw_focus = bool(abs(home_xG - away_xG) < 0.2 and (home_xG + away_xG) < 2.2)
    
    # 6. UNDER STRATEGY (VERY IMPORTANT)
    total_xG = home_xG + away_xG
    if total_xG < 1.8:
        under_priority = "VERY_HIGH"
    elif total_xG < 2.1:
        under_priority = "HIGH"
    else:
        under_priority = "LOW"
        
    # 7. VALUE BET SYSTEM (CORE)
    def calculate_edge(model_prob, odds, threshold):
        if not odds or odds <= 1.0:
            return {"edge": 0.0, "is_value": False}
        implied_prob = 1.0 / odds
        edge = model_prob - implied_prob
        return {
            "edge": round(float(edge), 4),
            "is_value": bool(edge > threshold)
        }

    value_bets = {
        "home_win": calculate_edge(home_win_prob, market_odds_home, 0.06),
        "draw": calculate_edge(draw_prob, market_odds_draw, 0.05),
        "away_win": calculate_edge(away_win_prob, market_odds_away, 0.06),
        "over": calculate_edge(over_prob, market_odds_over, 0.04),
        "under": calculate_edge(under_prob, market_odds_under, 0.04)
    }
    
    # 8. PASS LOGIC
    # PASS if confidence is low OR no value bets found above thresholds
    has_value = any(bet["is_value"] for bet in value_bets.values())
    decision = "PLAY" if (confidence >= 0.15 and has_value) else "PASS"
    
    # Special adjustment: if draw_focus is true, ensure draw is highlighted if edge is even slightly positive
    # (Though implementation rules said edge > 0.05, draw focus is a secondary priority)
    
    return {
        "probabilities": {
            "home_win": round(home_win_prob, 4),
            "draw": round(draw_prob, 4),
            "away_win": round(away_win_prob, 4)
        },
        "over_under": {
            "over": round(over_prob, 4),
            "under": round(under_prob, 4)
        },
        "confidence": round(confidence, 4),
        "decision": decision,
        "draw_focus": draw_focus,
        "under_priority": under_priority,
        "value_bets": value_bets
    }

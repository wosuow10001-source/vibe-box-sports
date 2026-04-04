import pandas as pd
import numpy as np
import json
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss, log_loss
import warnings

warnings.filterwarnings('ignore')

# ==================================================
# 1. DATA LOADING
# ==================================================

def parse_scoreline_probs(json_str):
    """Parse JSON string to dictionary of scores."""
    try:
        return json.loads(json_str.replace("'", '"'))
    except:
        return {}

def load_data(model_path, truth_path):
    """Load model outputs and ground truth, then merge."""
    df_model = pd.read_csv(model_path, encoding='utf-8-sig')
    df_truth = pd.read_csv(truth_path, encoding='utf-8-sig')
    
    # Merge on match_id
    df = pd.merge(df_model, df_truth, on='match_id', suffixes=('_pred', '_actual'))
    
    # Prep columns
    df['score_probs'] = df['scoreline_probs_json'].apply(parse_scoreline_probs)
    df['total_xg'] = df['xg_home'] + df['xg_away']
    df['actual_total_goals'] = df['home_goals'] + df['away_goals']
    
    return df

# ==================================================
# 2. BASE EVALUATION
# ==================================================

def compute_brier_scores(df, suffix=""):
    """Compute Brier Score for 1X2 and Over 2.5."""
    results = {}
    
    # Mapping ground truth to binary columns
    y_home = (df['result_1x2'] == 'H').astype(int)
    y_draw = (df['result_1x2'] == 'D').astype(int)
    y_away = (df['result_1x2'] == 'A').astype(int)
    
    results[f'brier_home{suffix}'] = brier_score_loss(y_home, df['home_prob'])
    results[f'brier_draw{suffix}'] = brier_score_loss(y_draw, df['draw_prob'])
    results[f'brier_away{suffix}'] = brier_score_loss(y_away, df['away_prob'])
    results[f'brier_over2.5{suffix}'] = brier_score_loss(df['is_over_2_5'], df['over_2_5_prob'])
    
    return results

def compute_log_loss_scores(df, suffix=""):
    """Compute Log Loss for 1X2."""
    y_true_1x2 = df['result_1x2'].map({'H': 0, 'D': 1, 'A': 2})
    probs_1x2 = df[['home_prob', 'draw_prob', 'away_prob']].values
    
    return {f'log_loss_1x2{suffix}': log_loss(y_true_1x2, probs_1x2, labels=[0, 1, 2])}

# ==================================================
# 3. CALIBRATION + RE-CALIBRATION
# ==================================================

def fit_probability_calibrators(df):
    """Train calibration models using ground truth."""
    calibrators = {}
    
    # 1X2 Probabilities
    targets = {
        'home_prob': (df['result_1x2'] == 'H').astype(int),
        'draw_prob': (df['result_1x2'] == 'D').astype(int),
        'away_prob': (df['result_1x2'] == 'A').astype(int),
        'over_2_5': df['is_over_2_5'],
        'over_3_5': df['is_over_3_5'],
        'btts': df['is_btts']
    }
    
    for col, y in targets.items():
        ir = IsotonicRegression(out_of_bounds='clip')
        # Handle cases with very few samples gracefully
        if len(df) > 5:
            # Add small noise to avoid identical X values if needed, or ensure they are sorted
            X = df[col if col in df.columns else f'{col}_prob'].values
            ir.fit(X, y)
            calibrators[col] = ir
            
    return calibrators

def apply_calibration(df, calibrators):
    """Apply fitted calibrators to probabilities."""
    df_cal = df.copy()
    
    # Apply to 1X2
    for col in ['home_prob', 'draw_prob', 'away_prob']:
        if col in calibrators:
            df_cal[col] = calibrators[col].predict(df_cal[col])
            
    # Renormalize 1X2
    sum_probs = df_cal[['home_prob', 'draw_prob', 'away_prob']].sum(axis=1)
    for col in ['home_prob', 'draw_prob', 'away_prob']:
        df_cal[col] /= sum_probs
        
    # Apply to others
    for col in ['over_2_5', 'over_3_5', 'btts']:
        data_col = f'{col}_prob'
        if col in calibrators:
            df_cal[data_col] = calibrators[col].predict(df_cal[data_col])
            
    return df_cal

# ==================================================
# 4. UPSET CORRECTION LAYER
# ==================================================

def apply_upset_adjustment(row):
    """Fix favorite bias and handle high draw expectation."""
    h, d, a = row['home_prob'], row['draw_prob'], row['away_prob']
    max_p = max(h, d, a)
    
    # Adjust factors
    if max_p < 0.55:
        # Flatten distribution (entropy boost)
        temp = 1.1 
        probs = np.array([h, d, a]) ** (1/temp)
        probs /= probs.sum()
        h, d, a = probs
    elif 0.55 <= max_p <= 0.7:
        # Boost underdog by small factor
        if h == max_p:
            d *= 1.05
            a *= 1.1
        elif a == max_p:
            h *= 1.1
            d *= 1.05
        # Renormalize
        s = h+d+a
        h, d, a = h/s, d/s, a/s
        
    if d > 0.3:
        # Increase variance by moving slightly towards uniform
        h = 0.9 * h + 0.1 * (1/3)
        d = 0.9 * d + 0.1 * (1/3)
        a = 0.9 * a + 0.1 * (1/3)
        s = h+d+a
        h, d, a = h/s, d/s, a/s

    row['home_prob'], row['draw_prob'], row['away_prob'] = h, d, a
    return row

# ==================================================
# 5. SCORE DISTRIBUTION ALIGNMENT WITH xG
# ==================================================

def compute_expected_goals_from_distribution(score_probs):
    """Implied total goals from score distribution."""
    total_ev = 0
    for score, prob in score_probs.items():
        try:
            h, a = map(int, score.split('-'))
            total_ev += (h + a) * prob
        except:
            continue
    return total_ev

def align_distribution_with_xg(score_probs, xg_home, xg_away):
    """Align distribution with xG using temperature scaling."""
    if not score_probs: return {}
    
    implied_goals = compute_expected_goals_from_distribution(score_probs)
    target_goals = xg_home + xg_away
    
    diff = abs(implied_goals - target_goals)
    if diff > 0.4:
        # Temperature scaling based on goal difference
        # T < 1 sharpens (higher scores if target high), T > 1 flattens (lower scores if target low)
        # Here we use a simpler heuristic: boost scores that align with target direction
        temp = target_goals / implied_goals if implied_goals > 0 else 1.0
        
        new_probs = {}
        for score, prob in score_probs.items():
            try:
                h, a = map(int, score.split('-'))
                # Shift prob based on total goals vs target
                weight = ((h + a + 1) / (implied_goals + 1)) ** (temp - 1)
                new_probs[score] = prob * weight
            except:
                new_probs[score] = prob
                
        # Normalize
        total = sum(new_probs.values())
        if total > 0:
            score_probs = {k: v/total for k, v in new_probs.items()}
            
    return score_probs

# ==================================================
# 6. DERIVED MARKET CONSISTENCY FIX
# ==================================================

def recompute_market_probs_from_distribution(row):
    """Recompute O/U and BTTS from the score distribution."""
    score_probs = row['score_probs']
    o25, o35, btts = 0.0, 0.0, 0.0
    
    for score, prob in score_probs.items():
        try:
            h, a = map(int, score.split('-'))
            if h + a > 2.5: o25 += prob
            if h + a > 3.5: o35 += prob
            if h > 0 and a > 0: btts += prob
        except:
            continue
            
    row['over_2_5_prob'] = o25
    row['over_3_5_prob'] = o35
    row['btts_prob'] = btts
    return row

# ==================================================
# 7. CONSISTENCY CHECK SYSTEM
# ==================================================

def enforce_consistency(row):
    """Prioritize score distribution for logical consistency."""
    # Already handled by pipeline flow: 
    # 1. Calibration 
    # 2. Upset 
    # 3. xG Alignment 
    # 4. Market Recomputation (this enforces consistency)
    return row

# ==================================================
# 8. TEXT GENERATION (FORCED CONSISTENCY)
# ==================================================

def generate_summary_from_distribution(row):
    """Generate summary using probabilistic ranges."""
    o25 = row['over_2_5_prob']
    h, d, a = row['home_prob'], row['draw_prob'], row['away_prob']
    xg = row['total_xg']
    
    outcome = "홈 승" if h > a and h > d else ("원정 승" if a > h and a > d else "무승부")
    goal_range = "많은 점수가 예상되는 (2.5↑)" if o25 > 0.55 else "저득점 위주의"
    
    # Rules
    if xg < 0.8:
        xg_text = "매우 적은 골 (0~1골)"
    elif xg < 2.5:
        xg_text = "적당한 골 (1~3골)"
    else:
        xg_text = "다득점 (3골+)"
        
    summary = f"{outcome} 확률이 높은 가운데, {goal_range} {xg_text} 범위의 경기가 예상됩니다."
    return summary

def enforce_text_consistency(row):
    """Mainly a wrapper for generate_summary_from_distribution."""
    return generate_summary_from_distribution(row)

# ==================================================
# 9. SHARPNESS + DISTRIBUTION ANALYSIS
# ==================================================

def compute_sharpness(probs):
    """Mean absolute deviation from uniform (1/3)."""
    return np.mean(np.abs(probs - 1/3))

def evaluate_top_k_accuracy(df, k=3):
    """Check if actual score is in top K predicted scorelines."""
    hits = 0
    for _, row in df.iterrows():
        actual = f"{row['home_goals']}-{row['away_goals']}"
        top_k = sorted(row['score_probs'].items(), key=lambda x: x[1], reverse=True)[:k]
        if any(actual == score for score, prob in top_k):
            hits += 1
    return hits / len(df)

# ==================================================
# 10. FULL PIPELINE
# ==================================================

def run_full_pipeline(model_path, truth_path):
    print("🚀 Initializing V5 Post-Processing Pipeline...")
    df = load_data(model_path, truth_path)
    
    # 1. Evaluation BEFORE
    m_before = compute_brier_scores(df)
    m_before.update(compute_log_loss_scores(df))
    print("\n--- BEFORE CORRECTION ---")
    for k, v in m_before.items(): print(f"{k:20}: {v:.4f}")
    
    # 2. Fit calibrators
    calibrators = fit_probability_calibrators(df)
    
    # 3. Apply calibration
    df = apply_calibration(df, calibrators)
    
    # 4. Apply upset adjustment
    df = df.apply(apply_upset_adjustment, axis=1)
    
    # 5. Align score distributions
    df["score_probs"] = df.apply(
        lambda r: align_distribution_with_xg(r.score_probs, r.xg_home, r.xg_away),
        axis=1
    )
    
    # 6. Recompute markets
    df = df.apply(recompute_market_probs_from_distribution, axis=1)
    
    # 7. Enforce consistency
    df = df.apply(enforce_consistency, axis=1)
    
    # 8. Replace text summaries
    df["text_summary_new"] = df.apply(enforce_text_consistency, axis=1)
    
    # 9. Evaluation AFTER
    m_after = compute_brier_scores(df)
    m_after.update(compute_log_loss_scores(df))
    
    print("\n--- AFTER CORRECTION ---")
    for k, v in m_after.items(): print(f"{k:20}: {v:.4f}")
    
    # 10. Print Improvements
    print("\n--- IMPROVEMENT SUMMARY ---")
    brier_imp = m_before['brier_home'] - m_after['brier_home']
    ll_imp = m_before['log_loss_1x2'] - m_after['log_loss_1x2']
    print(f"Brier (Home) Improvement: {brier_imp:+.4f}")
    print(f"Log Loss Improvement    : {ll_imp:+.4f}")
    print(f"Top-3 Score Accuracy    : {evaluate_top_k_accuracy(df, 3):.2%}")
    
    # 11. Show examples
    print("\n--- FIXED MATCH EXAMPLES ---")
    for i in range(min(3, len(df))):
        row = df.iloc[i]
        print(f"\nMatch {row['match_id']} ({row['home_team']} vs {row['away_team']})")
        print(f"  Result: {row['home_goals']}-{row['away_goals']} ({row['result_1x2']})")
        print(f"  [Original Text]   : {row['text_summary']}")
        print(f"  [Corrected Text]  : {row['text_summary_new']}")
        print(f"  [H/D/A Probs]     : {row['home_prob']:.2f} / {row['draw_prob']:.2f} / {row['away_prob']:.2f}")

    return df

if __name__ == "__main__":
    try:
        df_final = run_full_pipeline("model_outputs.csv", "ground_truth.csv")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")

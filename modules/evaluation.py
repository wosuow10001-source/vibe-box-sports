"""
Vibe Sports - Football Prediction Evaluation & Consistency Module
- Senior Data Engineer & ML Evaluation Tool
- Metrics: Brier Score, Log Loss, Calibration, Sharpness
- Validation: Probability consistency, Logical contradiction detection
- Post-processing: Corrected summary text generation
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple, Any
from sklearn.metrics import log_loss, brier_score_loss

def parse_scoreline_probs(json_str: str) -> Dict[Tuple[int, int], float]:
    """
    Convert JSON string {"0-0": 0.11, "1-0": 0.104} into {(0,0): 0.11, (1,0): 0.104}
    """
    try:
        raw_dict = json.loads(json_str)
        parsed = {}
        for k, v in raw_dict.items():
            # Support both "0-0" and "0:0" formats
            sep = ":" if ":" in k else "-"
            h, a = map(int, k.split(sep))
            parsed[(h, a)] = float(v)
        return parsed
    except Exception:
        return {}

def load_data(model_path: str, truth_path: str) -> pd.DataFrame:
    """
    - Load both CSVs
    - Merge on match_id
    - Parse scoreline_probs_json into dict
    - Create helper columns
    """
    df_model = pd.read_csv(model_path)
    df_truth = pd.read_csv(truth_path)
    
    df = pd.merge(df_model, df_truth, on='match_id', how='inner')
    
    # Parse distributions
    df['score_probs_dict'] = df['scoreline_probs_json'].apply(parse_scoreline_probs)
    
    # Helper columns
    df['total_xg'] = df['xg_home'] + df['xg_away']
    df['actual_total_goals'] = df['home_goals'] + df['away_goals']
    
    # One-hot encode results for metrics
    df['is_h'] = (df['result_1x2'] == 'H').astype(int)
    df['is_d'] = (df['result_1x2'] == 'D').astype(int)
    df['is_a'] = (df['result_1x2'] == 'A').astype(int)
    
    return df

def compute_brier_scores(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute Brier score for 1X2, Over/Under, BTTS
    """
    # 1X2 Multi-class Brier: mean sum of squares
    probs_1x2 = df[['home_prob', 'draw_prob', 'away_prob']].values
    actual_1x2 = df[['is_h', 'is_d', 'is_a']].values
    brier_1x2 = np.mean(np.sum((probs_1x2 - actual_1x2)**2, axis=1))
    
    scores = {
        "brier_1x2": brier_1x2,
        "brier_over_2_5": brier_score_loss(df['is_over_2_5'], df['over_2_5_prob']),
        "brier_over_3_5": brier_score_loss(df['is_over_3_5'], df['over_3_5_prob']),
        "brier_btts": brier_score_loss(df['is_btts'], df['btts_prob'])
    }
    return scores

def compute_log_loss_scores(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute log loss for same targets
    """
    actual_1x2 = df[['is_h', 'is_d', 'is_a']].values
    probs_1x2 = df[['home_prob', 'draw_prob', 'away_prob']].values
    
    scores = {
        "log_loss_1x2": log_loss(actual_1x2, probs_1x2),
        "log_loss_over_2_5": log_loss(df['is_over_2_5'], df['over_2_5_prob']),
        "log_loss_btts": log_loss(df['is_btts'], df['btts_prob'])
    }
    return scores

def calibration_curve_1x2(df: pd.DataFrame, bins: int = 10) -> pd.DataFrame:
    """
    Bucket by predicted home_prob and compute actual win rate
    """
    df['prob_bin'] = pd.cut(df['home_prob'], bins=np.linspace(0, 1, bins+1))
    
    cal_table = df.groupby('prob_bin', observed=True).agg(
        avg_pred_prob=('home_prob', 'mean'),
        actual_win_rate=('is_h', 'mean'),
        count=('match_id', 'size')
    ).reset_index()
    
    return cal_table

def compute_sharpness(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Measure how confident predictions are
    """
    max_probs = df[['home_prob', 'draw_prob', 'away_prob']].max(axis=1)
    sharpness = {
        "avg_max_prob": max_probs.mean(),
        "std_max_prob": max_probs.std(),
        "confidence_dist": df['confidence'].value_counts(normalize=True).to_dict()
    }
    return sharpness

def upset_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze favorite behavior
    """
    # Identify favorite
    probs = df[['home_prob', 'draw_prob', 'away_prob']].values
    df['fav_prob'] = np.max(probs, axis=1)
    df['is_fav_home'] = (df['home_prob'] == df['fav_prob'])
    df['is_fav_away'] = (df['away_prob'] == df['fav_prob'])
    
    # Check if favorite won
    df['fav_win'] = ((df['is_fav_home'] & df['is_h']) | 
                    (df['is_fav_away'] & df['is_a'])).astype(int)
    
    # Underdog win (fav not home/away win - draw doesn't count as underdog win in strict sense, but let's follow spec)
    df['underdog_win'] = ((df['is_fav_home'] & df['is_a']) | 
                         (df['is_fav_away'] & df['is_h'])).astype(int)
    
    # Buckets
    bins = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    df['fav_bin'] = pd.cut(df['fav_prob'], bins=bins)
    
    upset_table = df.groupby('fav_bin', observed=True).agg(
        avg_fav_prob=('fav_prob', 'mean'),
        favorite_win_rate=('fav_win', 'mean'),
        underdog_win_rate=('underdog_win', 'mean'),
        draw_rate=('is_d', 'mean'),
        count=('match_id', 'size')
    ).reset_index()
    
    return upset_table

def evaluate_score_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Hit rates for Top 3 / Top 5 scores
    """
    top3_hits = 0
    top5_hits = 0
    
    for _, row in df.iterrows():
        dist = row['score_probs_dict']
        sorted_scores = sorted(dist.items(), key=lambda x: x[1], reverse=True)
        top3 = [s[0] for s in sorted_scores[:3]]
        top5 = [s[0] for s in sorted_scores[:5]]
        
        actual = (row['home_goals'], row['away_goals'])
        if actual in top3: top3_hits += 1
        if actual in top5: top5_hits += 1
        
    n = len(df)
    return {
        "top3_hit_rate": top3_hits / n,
        "top5_hit_rate": top5_hits / n
    }

def check_consistency(row: pd.Series) -> Dict[str, Any]:
    """
    Detect logical contradictions
    """
    flags = []
    dist = row['score_probs_dict']
    
    # 1) xG vs distribution
    exp_goals = sum((k[0] + k[1]) * v for k, v in dist.items())
    if abs(row['total_xg'] - exp_goals) > 0.8:
        flags.append(f"xG Mismatch: engine_xg={row['total_xg']:.2f}, dist_xg={exp_goals:.2f}")

    # 2) Over/Under consistency
    prob_over_2_5_dist = sum(v for k, v in dist.items() if (k[0] + k[1]) > 2.5)
    if abs(row['over_2_5_prob'] - prob_over_2_5_dist) > 0.15:
        flags.append(f"Over/Under Contradiction: prob={row['over_2_5_prob']:.2f}, dist={prob_over_2_5_dist:.2f}")

    # 3) Text Contradictions
    text = str(row['text_summary']).lower()
    most_likely_score = sorted(dist.items(), key=lambda x: x[1], reverse=True)[0][0]
    
    if row['over_2_5_prob'] > 0.6 and most_likely_score == (0, 0):
        flags.append("Paradox: High Over prob but 0-0 is most likely")
        
    if row['total_xg'] > 2.7 and any(kw in text for kw in ["low scoring", "저득점", "방어적"]):
        flags.append("Text Paradox: High xG but text says low scoring")
    
    if row['total_xg'] < 1.5 and any(kw in text for kw in ["high scoring", "다득점", "난타전"]):
        flags.append("Text Paradox: Low xG but text says high scoring")

    # 4) xG sanity
    if row['xg_away'] > 2.7 or row['xg_home'] > 4.0:
        flags.append(f"Unrealistic xG: H={row['xg_home']}, A={row['xg_away']}")

    # 5) Prob sum
    p_sum = row['home_prob'] + row['draw_prob'] + row['away_prob']
    if abs(p_sum - 1.0) > 0.02:
        flags.append(f"Prob Sum Error: {p_sum:.4f}")

    return {
        "is_consistent": len(flags) == 0,
        "flags": flags
    }

def generate_summary_from_distribution(
    xg_home: float,
    xg_away: float,
    score_probs: Dict[Tuple[int, int], float],
    over_probs: Dict[str, float],
    btts_prob: float,
    win_probs: Dict[str, float],
    confidence: str
) -> Dict[str, str]:
    """
    Generate structured summary text
    """
    total_xg = xg_home + xg_away
    
    # Headline logic
    fav = max(win_probs, key=win_probs.get)
    fav_name = "홈팀" if fav == 'home' else "원정팀" if fav == 'away' else "무승부"
    
    # 1. Total Goals Summary
    if total_xg < 1.5:
        total_goals_summary = "수비 중심의 저득점 경기 가능성이 높습니다."
    elif 1.5 <= total_xg <= 2.8:
        total_goals_summary = "1~3골 사이의 박빙 양상이 예상되는 경기입니다."
    else:
        total_goals_summary = "양 팀의 활발한 공격으로 인한 다득점 가능성이 큽니다."

    # 2. Scoreline Summary
    low_prob = sum(v for k, v in score_probs.items() if (k[0] + k[1]) <= 1)
    high_prob = sum(v for k, v in score_probs.items() if (k[0] + k[1]) >= 4)
    
    if low_prob > 0.4:
         scoreline_summary = "0:0 혹은 1:0과 같은 저스코어 양상에 힘이 실립니다."
    elif high_prob > 0.25:
         scoreline_summary = "3골 이상의 고득점 스코어라인이 유력하게 관찰됩니다."
    else:
         scoreline_summary = "1:1, 2:1 등 전형적인 박빙 스코어의 확률이 가장 높습니다."

    # 3. Win Prob Summary
    max_p = win_probs[fav]
    if max_p < 0.45:
        win_prob_summary = f"{fav_name}이 근소하게 우세하나, 무승부 변수가 매우 큽니다."
    elif 0.45 <= max_p < 0.65:
        win_prob_summary = f"{fav_name}의 전력 우세가 뚜렷하며 승리 가능성이 높습니다."
    else:
        win_prob_summary = f"{fav_name}의 압도적인 우세가 점쳐지는 매치업입니다."

    if win_probs.get('away', 0) > 0.25 and fav == 'home' and max_p > 0.6:
        win_prob_summary += " 다만 원정팀의 역습으로 인한 이변 가능성도 배제할 수 없습니다."

    return {
        "headline": f"{fav_name} 우세 속 {confidence} 신뢰도 분석",
        "total_goals_summary": total_goals_summary,
        "scoreline_summary": scoreline_summary,
        "win_prob_summary": win_prob_summary
    }

def run_full_evaluation(model_path: str, truth_path: str):
    """
    Execute full pipeline and print report
    """
    df = load_data(model_path, truth_path)
    
    brier = compute_brier_scores(df)
    logloss = compute_log_loss_scores(df)
    sharpness = compute_sharpness(df)
    calibration = calibration_curve_1x2(df)
    upset = upset_analysis(df)
    dist_stats = evaluate_score_distribution(df)
    
    # Consistency loop
    consistency_results = df.apply(check_consistency, axis=1)
    df['consistent'] = [r['is_consistent'] for r in consistency_results]
    df['flags'] = [r['flags'] for r in consistency_results]
    
    inconsistent_count = len(df[~df['consistent']])
    
    print("\n" + "="*50)
    print(" FOOTBALL PREDICTION ENGINE EVALUATION REPORT")
    print("="*50)
    
    print("\n1. PERFORMANCE METRICS")
    print(f"   Brier Score (1X2):  {brier['brier_1x2']:.4f}")
    print(f"   Log Loss (1X2):     {logloss['log_loss_1x2']:.4f}")
    print(f"   Sharpness (AvgP):   {sharpness['avg_max_prob']:.2%}")
    print(f"   Top 3 Score Hit:    {dist_stats['top3_hit_rate']:.2%}")
    
    print("\n2. CALIBRATION (WIN PROBABILITY)")
    print(calibration.to_string(index=False))
    
    print("\n3. UPSET ANALYSIS")
    print(upset.to_string(index=False))
    
    print("\n4. CONSISTENCY AUDIT")
    print(f"   Inconsistent Cases: {inconsistent_count} / {len(df)} ({inconsistent_count/len(df):.1%})")
    
    if inconsistent_count > 0:
        print("\n   [Example Issues]")
        problems = df[~df['consistent']].head(3)
        for _, p in problems.iterrows():
            print(f"   - MatchID {p['match_id']}: {p['flags']}")
            
    print("\n" + "="*50)
    print(" EVALUATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    # Internal test run if files exist
    import os
    if os.path.exists("model_outputs.csv") and os.path.exists("ground_truth.csv"):
        run_full_evaluation("model_outputs.csv", "ground_truth.csv")
    else:
        print("evaluation.py loaded. Use run_full_evaluation(model_csv, truth_csv) to analyze.")

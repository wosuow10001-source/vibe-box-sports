"""
============================================================================
 V5 Post-Processing + Evaluation + Correction Pipeline
 -------------------------------------------------------
 Football Prediction Engine - Probabilistic Calibration & Consistency Layer

 This module does NOT rebuild or retrain the core prediction engine.
 It ONLY post-processes existing model outputs:
   1) Evaluates predictions against ground truth
   2) Detects weaknesses (calibration, favorite bias, low-scoring bias)
   3) Applies probabilistic corrections (Isotonic / Platt)
   4) Aligns score distributions with xG
   5) Fixes logical inconsistencies
   6) Regenerates text summaries so they ALWAYS match the numbers

 Dependencies: pandas, numpy, scikit-learn (only)
============================================================================
"""

import pandas as pd
import numpy as np
import json
import sys
import io
from typing import Dict, List, Tuple, Any, Optional
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
import warnings

warnings.filterwarnings('ignore')


# ============================================================================
# 1. DATA LOADING
# ============================================================================

def parse_scoreline_probs(json_str: str) -> Dict[Tuple[int, int], float]:
    """
    Convert scoreline_probs_json from string to dict with tuple keys.
    Input:  '{"0-0": 0.11, "1-0": 0.09, ...}'
    Output: {(0, 0): 0.11, (1, 0): 0.09, ...}
    """
    try:
        raw = json.loads(json_str.replace("'", '"'))
        parsed = {}
        for k, v in raw.items():
            sep = ":" if ":" in k else "-"
            h, a = map(int, k.split(sep))
            parsed[(h, a)] = float(v)
        return parsed
    except Exception:
        return {}


def load_data(model_path: str, truth_path: str) -> pd.DataFrame:
    """
    Load model_outputs.csv and ground_truth.csv, merge, and enrich.
    """
    # Try multiple encodings for Windows compatibility
    for enc in ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']:
        try:
            df_model = pd.read_csv(model_path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    for enc in ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']:
        try:
            df_truth = pd.read_csv(truth_path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    df = pd.merge(df_model, df_truth, on='match_id', how='inner')

    # Parse score distribution
    df['score_probs'] = df['scoreline_probs_json'].apply(parse_scoreline_probs)

    # Helper columns
    df['total_xg'] = df['xg_home'] + df['xg_away']
    df['actual_total_goals'] = df['home_goals'] + df['away_goals']

    # One-hot results for evaluation
    df['is_h'] = (df['result_1x2'] == 'H').astype(int)
    df['is_d'] = (df['result_1x2'] == 'D').astype(int)
    df['is_a'] = (df['result_1x2'] == 'A').astype(int)

    # Save originals for before/after comparison
    for col in ['home_prob', 'draw_prob', 'away_prob',
                'over_2_5_prob', 'over_3_5_prob', 'btts_prob', 'text_summary']:
        df[f'orig_{col}'] = df[col]
    df['orig_score_probs'] = df['score_probs'].copy()

    return df


# ============================================================================
# 2. BASE EVALUATION
# ============================================================================

def compute_brier_scores(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute Brier scores for 1X2 (multiclass), over_2_5, over_3_5, BTTS.
    """
    # Multiclass 1X2 Brier
    probs_1x2 = df[['home_prob', 'draw_prob', 'away_prob']].values
    actual_1x2 = df[['is_h', 'is_d', 'is_a']].values
    brier_1x2 = float(np.mean(np.sum((probs_1x2 - actual_1x2) ** 2, axis=1)))

    return {
        "brier_1x2": brier_1x2,
        "brier_home": float(brier_score_loss(df['is_h'], df['home_prob'])),
        "brier_draw": float(brier_score_loss(df['is_d'], df['draw_prob'])),
        "brier_away": float(brier_score_loss(df['is_a'], df['away_prob'])),
        "brier_over_2_5": float(brier_score_loss(df['is_over_2_5'], df['over_2_5_prob'])),
        "brier_over_3_5": float(brier_score_loss(df['is_over_3_5'], df['over_3_5_prob'])),
        "brier_btts": float(brier_score_loss(df['is_btts'], df['btts_prob'])),
    }


def compute_log_loss_scores(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute Log Loss for 1X2, over_2_5, over_3_5, BTTS.
    """
    probs_1x2 = df[['home_prob', 'draw_prob', 'away_prob']].values
    # Clip to avoid log(0)
    probs_1x2 = np.clip(probs_1x2, 1e-7, 1 - 1e-7)
    # Re-normalize after clipping
    probs_1x2 = probs_1x2 / probs_1x2.sum(axis=1, keepdims=True)

    y_1x2 = df['result_1x2'].map({'H': 0, 'D': 1, 'A': 2}).values

    def safe_binary_logloss(y_true, y_pred):
        y_pred = np.clip(y_pred, 1e-7, 1 - 1e-7)
        return float(log_loss(y_true, y_pred))

    return {
        "logloss_1x2": float(log_loss(y_1x2, probs_1x2, labels=[0, 1, 2])),
        "logloss_over_2_5": safe_binary_logloss(df['is_over_2_5'], df['over_2_5_prob']),
        "logloss_over_3_5": safe_binary_logloss(df['is_over_3_5'], df['over_3_5_prob']),
        "logloss_btts": safe_binary_logloss(df['is_btts'], df['btts_prob']),
    }


# ============================================================================
# 3. CALIBRATION + RE-CALIBRATION
# ============================================================================

def fit_probability_calibrators(
    df: pd.DataFrame,
    method: str = 'isotonic'
) -> Dict[str, Any]:
    """
    Train calibration models for 1X2 probability outputs ONLY.

    NOTE: Binary markets (over_2_5, over_3_5, btts) are NOT calibrated here
    because they will be recomputed directly from the corrected score
    distribution later in the pipeline. Calibrating them from the model's
    original (potentially inconsistent) values introduces noise.

    Args:
        df: DataFrame with model predictions and ground truth.
        method: 'isotonic' (non-parametric) or 'platt' (sigmoid/logistic).

    Returns:
        Dictionary mapping column name -> fitted calibrator.
    """
    calibrators = {}

    # Only calibrate 1X2 match outcome probabilities
    targets = {
        'home': ('home_prob', df['is_h'].values),
        'draw': ('draw_prob', df['is_d'].values),
        'away': ('away_prob', df['is_a'].values),
    }

    for name, (col, y) in targets.items():
        X = df[col].values
        if len(X) < 5:
            continue

        if method == 'isotonic':
            cal = IsotonicRegression(out_of_bounds='clip', y_min=0.01, y_max=0.99)
            cal.fit(X, y)
        else:  # platt
            cal = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000)
            cal.fit(X.reshape(-1, 1), y)

        calibrators[name] = {'model': cal, 'method': method, 'source_col': col}

    return calibrators


def apply_calibration(
    df: pd.DataFrame,
    calibrators: Dict[str, Any]
) -> pd.DataFrame:
    """
    Apply fitted calibrators. Renormalize 1X2 after calibration.
    """
    df = df.copy()

    for name in ['home', 'draw', 'away']:
        if name not in calibrators:
            continue
        info = calibrators[name]
        X = df[info['source_col']].values
        if info['method'] == 'isotonic':
            df[info['source_col']] = info['model'].predict(X)
        else:
            df[info['source_col']] = info['model'].predict_proba(X.reshape(-1, 1))[:, 1]

    # Renormalize 1X2 to sum = 1.0
    s = df[['home_prob', 'draw_prob', 'away_prob']].sum(axis=1)
    s = s.replace(0, 1)  # safety
    for col in ['home_prob', 'draw_prob', 'away_prob']:
        df[col] = df[col] / s

    # NOTE: Binary markets (O2.5, O3.5, BTTS) are NOT calibrated here.
    # They are recomputed from the corrected score distribution later.

    return df


# ============================================================================
# 4. UPSET CORRECTION LAYER (FAVORITE BIAS)
# ============================================================================

def apply_upset_adjustment(row: pd.Series) -> pd.Series:
    """
    Fix favorite bias in 1X2 probabilities.

    - If max_prob < 0.55: flatten distribution toward uniform (entropy boost)
    - If 0.55 <= max_prob <= 0.7: boost underdog slightly
    - If draw_prob > 0.30: reduce overconfidence in draw
    """
    h = float(row['home_prob'])
    d = float(row['draw_prob'])
    a = float(row['away_prob'])
    max_p = max(h, d, a)

    if max_p < 0.55:
        # Entropy boost via temperature > 1
        temperature = 1.15
        log_probs = np.log(np.clip([h, d, a], 1e-8, None))
        scaled = log_probs / temperature
        scaled -= scaled.max()  # numerical stability
        probs = np.exp(scaled)
        probs /= probs.sum()
        h, d, a = probs

    elif 0.55 <= max_p <= 0.70:
        # Identify favorite and underdogs, boost underdogs
        probs = np.array([h, d, a])
        fav_idx = np.argmax(probs)
        boost_factor = 0.08  # transfer 8% from favorite to underdogs

        transfer = probs[fav_idx] * boost_factor
        probs[fav_idx] -= transfer

        # Split transfer across non-favorites proportionally
        others_sum = probs.sum() - probs[fav_idx]
        if others_sum > 0:
            for i in range(3):
                if i != fav_idx:
                    probs[i] += transfer * (probs[i] / others_sum) if others_sum > 0 else transfer / 2

        probs /= probs.sum()
        h, d, a = probs

    # Draw too high → flatten slightly toward uniform
    if d > 0.30:
        alpha = 0.12  # blend factor toward uniform
        uniform = 1.0 / 3.0
        h = (1 - alpha) * h + alpha * uniform
        d = (1 - alpha) * d + alpha * uniform
        a = (1 - alpha) * a + alpha * uniform
        s = h + d + a
        h, d, a = h / s, d / s, a / s

    row = row.copy()
    row['home_prob'] = h
    row['draw_prob'] = d
    row['away_prob'] = a
    return row


# ============================================================================
# 5. SCORE DISTRIBUTION ALIGNMENT WITH xG
# ============================================================================

def _poisson_pmf(k: int, lam: float) -> float:
    """Poisson probability mass function (no scipy dependency)."""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    # k! via iterative multiplication to avoid large factorials
    log_p = k * np.log(lam) - lam
    for i in range(1, k + 1):
        log_p -= np.log(i)
    return np.exp(log_p)


def generate_poisson_distribution(
    xg_home: float,
    xg_away: float,
    max_goals: int = 7,
) -> Dict[Tuple[int, int], float]:
    """
    Generate a full independent-Poisson score distribution from xG.
    P(h, a) = Poisson(h | xg_home) * Poisson(a | xg_away)
    """
    dist: Dict[Tuple[int, int], float] = {}
    for h in range(max_goals):
        for a in range(max_goals):
            p = _poisson_pmf(h, xg_home) * _poisson_pmf(a, xg_away)
            if p > 1e-6:
                dist[(h, a)] = p

    total = sum(dist.values())
    if total > 0:
        dist = {k: v / total for k, v in dist.items()}
    return dist


def expand_sparse_distribution(
    score_probs: Dict[Tuple[int, int], float],
    xg_home: float,
    xg_away: float,
    blend_weight: float = 0.4,
) -> Dict[Tuple[int, int], float]:
    """
    Expand a sparse score distribution by blending with a Poisson prior.

    If the model distribution covers fewer than 10 scorelines (sparse),
    we generate a full Poisson grid from xG and blend:
        new_p = (1 - blend_weight) * model_p + blend_weight * poisson_p

    This ensures high-goal scorelines (3-2, 4-1, etc.) are represented.
    """
    if len(score_probs) >= 15:
        # Distribution is already rich enough
        return score_probs

    poisson_dist = generate_poisson_distribution(xg_home, xg_away)

    # Merge: model distribution is the anchor, Poisson fills the gaps
    all_scores = set(score_probs.keys()) | set(poisson_dist.keys())
    blended: Dict[Tuple[int, int], float] = {}

    for score in all_scores:
        model_p = score_probs.get(score, 0.0)
        poisson_p = poisson_dist.get(score, 0.0)
        blended[score] = (1 - blend_weight) * model_p + blend_weight * poisson_p

    total = sum(blended.values())
    if total > 0:
        blended = {k: v / total for k, v in blended.items()}

    return blended


def compute_expected_goals_from_distribution(
    score_probs: Dict[Tuple[int, int], float]
) -> float:
    """
    Expected total goals from score distribution.
    E[goals] = sum((h + a) * p for all (h,a) in distribution)
    """
    return sum((h + a) * p for (h, a), p in score_probs.items())


def align_distribution_with_xg(
    score_probs: Dict[Tuple[int, int], float],
    xg_home: float,
    xg_away: float,
    threshold: float = 0.4
) -> Dict[Tuple[int, int], float]:
    """
    Align scoreline distribution with xG.

    Steps:
    1) Expand sparse distributions using Poisson prior from xG
    2) If implied goals still differs from xG by >threshold, apply
       exponential tilt to shift the mean toward the target
    """
    if not score_probs:
        return score_probs

    # Step 1: Expand sparse distributions
    score_probs = expand_sparse_distribution(score_probs, xg_home, xg_away)

    # Step 2: Exponential tilt if needed
    implied = compute_expected_goals_from_distribution(score_probs)
    target = xg_home + xg_away
    diff = target - implied

    if abs(diff) <= threshold:
        return score_probs

    # lambda proportional to gap, damped to avoid over-correction
    lam = diff * 0.25

    new_probs: Dict[Tuple[int, int], float] = {}
    for (h, a), p in score_probs.items():
        total = h + a
        weight = np.exp(lam * total)
        new_probs[(h, a)] = p * weight

    total_mass = sum(new_probs.values())
    if total_mass > 0:
        new_probs = {k: v / total_mass for k, v in new_probs.items()}

    return new_probs


# ============================================================================
# 6. DERIVED MARKET CONSISTENCY (FROM DISTRIBUTION)
# ============================================================================

def recompute_market_probs_from_distribution(
    score_probs: Dict[Tuple[int, int], float]
) -> Dict[str, float]:
    """
    Recompute over/under and BTTS from score distribution.
    This OVERRIDES any previous independent model output for these markets.
    """
    o25 = sum(p for (h, a), p in score_probs.items() if h + a >= 3)
    o35 = sum(p for (h, a), p in score_probs.items() if h + a >= 4)
    btts = sum(p for (h, a), p in score_probs.items() if h >= 1 and a >= 1)

    return {
        "over_2_5_prob": o25,
        "over_3_5_prob": o35,
        "btts_prob": btts,
    }


def recompute_market_probs_for_df(df: pd.DataFrame) -> pd.DataFrame:
    """Apply market recomputation row-wise."""
    df = df.copy()
    for idx, row in df.iterrows():
        markets = recompute_market_probs_from_distribution(row['score_probs'])
        for k, v in markets.items():
            df.at[idx, k] = v
    return df


# ============================================================================
# 7. CONSISTENCY CHECK SYSTEM
# ============================================================================

def compute_distribution_metrics(
    score_probs: Dict[Tuple[int, int], float]
) -> Dict[str, float]:
    """Compute summary metrics from score distribution."""
    exp_goals = compute_expected_goals_from_distribution(score_probs)
    o25 = sum(p for (h, a), p in score_probs.items() if h + a >= 3)
    o35 = sum(p for (h, a), p in score_probs.items() if h + a >= 4)
    btts = sum(p for (h, a), p in score_probs.items() if h >= 1 and a >= 1)

    return {
        "expected_total_goals_from_dist": exp_goals,
        "over_2_5_from_dist": o25,
        "over_3_5_from_dist": o35,
        "btts_from_dist": btts,
    }


def check_consistency(row: pd.Series) -> Dict[str, Any]:
    """
    Detect logical inconsistencies for a single match row.
    Returns flag list and consistency status.
    """
    flags: List[str] = []
    dist = row['score_probs']
    metrics = compute_distribution_metrics(dist)
    exp_goals = metrics['expected_total_goals_from_dist']

    # 1) xG vs distribution
    if abs(row['total_xg'] - exp_goals) > 0.5:
        flags.append(
            f"xG Mismatch: engine_xg={row['total_xg']:.2f}, "
            f"dist_xg={exp_goals:.2f}"
        )

    # 2) Markets vs distribution
    for market in ['over_2_5', 'over_3_5']:
        col = f'{market}_prob'
        dist_val = metrics[f'{market}_from_dist']
        if abs(row[col] - dist_val) > 0.1:
            flags.append(
                f"{market} Contradiction: model={row[col]:.2f}, dist={dist_val:.2f}"
            )

    # 3) Text contradictions
    text = str(row.get('text_summary', '')).lower()

    if row['total_xg'] > 2.5 and any(
        kw in text for kw in ['0골', '저득점', 'under 2.5', 'low scoring', '방어적']
    ):
        flags.append("Text Paradox: High xG but text says low scoring")

    if row['total_xg'] < 1.5 and any(
        kw in text for kw in ['다득점', 'over', 'high scoring', '난타전']
    ):
        flags.append("Text Paradox: Low xG but text says high scoring")

    if '0골' in text and exp_goals > 0.8:
        flags.append(
            f"CRITICAL Text Bug: '0골' in text but E[goals]={exp_goals:.2f}"
        )

    # 4) Probability sanity
    p_sum = row['home_prob'] + row['draw_prob'] + row['away_prob']
    if abs(p_sum - 1.0) > 0.02:
        flags.append(f"Prob Sum Error: {p_sum:.4f}")

    return {
        "has_inconsistency": len(flags) > 0,
        "flags": flags,
        "expected_total_goals_from_dist": exp_goals,
    }


def enforce_consistency(row: pd.Series) -> pd.Series:
    """
    Enforce consistency in priority order:
    1) Align score distribution with xG
    2) Recompute market probabilities from distribution
    3) Re-check and clamp probabilities
    """
    row = row.copy()

    # 1) Re-align distribution with xG (defensive — pipeline already does this,
    #    but enforce_consistency acts as a safety net)
    row['score_probs'] = align_distribution_with_xg(
        row['score_probs'], row['xg_home'], row['xg_away'], threshold=0.4
    )

    # 2) Recompute markets from corrected distribution
    markets = recompute_market_probs_from_distribution(row['score_probs'])
    row['over_2_5_prob'] = markets['over_2_5_prob']
    row['over_3_5_prob'] = markets['over_3_5_prob']
    row['btts_prob'] = markets['btts_prob']

    # 3) Clamp and renormalize 1X2
    for col in ['home_prob', 'draw_prob', 'away_prob']:
        row[col] = max(0.01, min(0.98, float(row[col])))
    s = row['home_prob'] + row['draw_prob'] + row['away_prob']
    row['home_prob'] /= s
    row['draw_prob'] /= s
    row['away_prob'] /= s

    return row


# ============================================================================
# 8. TEXT GENERATION (FORCED CONSISTENCY)
# ============================================================================

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
    Generate a NEW, number-consistent textual summary.

    STRICT RULES:
    - NEVER say '0 goals expected' unless expected_total_goals < 0.8
    - Always talk in ranges: 0~1, 1~3, 3+
    - Use probabilistic language
    """
    total_xg = xg_home + xg_away

    # Goal band probabilities
    low_prob = sum(p for (h, a), p in score_probs.items() if h + a <= 1)
    mid_prob = sum(p for (h, a), p in score_probs.items() if 2 <= h + a <= 3)
    high_prob = sum(p for (h, a), p in score_probs.items() if h + a >= 4)

    # --- 1. Total goals summary ---
    if total_xg < 1.5:
        total_goals_summary = (
            f"xG 합산 {total_xg:.1f}골로, "
            f"저득점(0~1골) 경기 가능성이 높은 편입니다 ({low_prob:.0%})."
        )
    elif total_xg <= 2.8:
        total_goals_summary = (
            f"xG 합산 {total_xg:.1f}골로, "
            f"1~3골 사이에서 승부가 갈릴 가능성이 큽니다 ({mid_prob:.0%})."
        )
    else:
        total_goals_summary = (
            f"xG 합산 {total_xg:.1f}골로, "
            f"3골 이상 다득점 가능성도 있는 경기입니다 ({high_prob:.0%})."
        )

    # --- 2. Scoreline summary ---
    if score_probs:
        sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)
        top_score = sorted_scores[0]
        top_str = f"{top_score[0][0]}-{top_score[0][1]}"
        top_pct = f"{top_score[1]:.0%}"
        scoreline_summary = (
            f"최빈 스코어는 {top_str} ({top_pct})이나, "
            f"이는 하나의 시나리오이며 다양한 결과가 가능합니다."
        )
    else:
        scoreline_summary = "스코어 분포 데이터가 부족합니다."

    # --- 3. Win probability summary ---
    fav_key = max(win_probs, key=win_probs.get)
    fav_prob = win_probs[fav_key]
    fav_name = {"home": "홈팀", "draw": "무승부", "away": "원정팀"}[fav_key]

    if fav_prob < 0.45:
        win_prob_summary = (
            f"양 팀 전력이 백중세로, 박빙의 경기가 예상됩니다 "
            f"(최대 {fav_prob:.0%})."
        )
    elif fav_prob < 0.65:
        win_prob_summary = (
            f"{fav_name}이(가) 약간 우세합니다 ({fav_prob:.0%})."
        )
    else:
        win_prob_summary = (
            f"{fav_name}의 확실한 우세가 점쳐집니다 ({fav_prob:.0%})."
        )

    # Underdog alert
    underdog_prob = min(win_probs.get('home', 0), win_probs.get('away', 0))
    if underdog_prob > 0.25:
        win_prob_summary += (
            f" 다만 이변 가능성도 무시할 수 없습니다 ({underdog_prob:.0%})."
        )

    # --- 4. Headline ---
    conf_text = {"low": "낮은", "medium": "보통", "high": "높은"}.get(confidence, "보통")
    headline = f"[{conf_text} 신뢰도] {fav_name} 우세 | xG {total_xg:.1f}"

    return {
        "headline": headline,
        "total_goals_summary": total_goals_summary,
        "scoreline_summary": scoreline_summary,
        "win_prob_summary": win_prob_summary,
    }


def enforce_text_consistency(row: pd.Series) -> str:
    """
    ALWAYS replace text_summary with a newly generated summary.
    Old text is unreliable -> DO NOT TRUST IT.
    """
    summary_parts = generate_summary_from_distribution(
        xg_home=float(row['xg_home']),
        xg_away=float(row['xg_away']),
        score_probs=row['score_probs'],
        over_probs={
            'over_2_5': float(row['over_2_5_prob']),
            'over_3_5': float(row['over_3_5_prob']),
        },
        btts_prob=float(row['btts_prob']),
        win_probs={
            'home': float(row['home_prob']),
            'draw': float(row['draw_prob']),
            'away': float(row['away_prob']),
        },
        confidence=str(row.get('confidence', 'medium'))
    )

    # Concatenate into a single summary string
    return (
        f"{summary_parts['headline']}\n"
        f"{summary_parts['total_goals_summary']}\n"
        f"{summary_parts['scoreline_summary']}\n"
        f"{summary_parts['win_prob_summary']}"
    )


# ============================================================================
# 9. SHARPNESS + DISTRIBUTION ANALYSIS (DIAGNOSTICS)
# ============================================================================

def compute_sharpness(df: pd.DataFrame) -> Dict[str, Any]:
    """Measure how confident (sharp) predictions are."""
    max_probs = df[['home_prob', 'draw_prob', 'away_prob']].max(axis=1)
    return {
        "avg_max_prob": float(max_probs.mean()),
        "std_max_prob": float(max_probs.std()),
        "histogram": {
            "<0.4": int((max_probs < 0.4).sum()),
            "0.4-0.5": int(((max_probs >= 0.4) & (max_probs < 0.5)).sum()),
            "0.5-0.6": int(((max_probs >= 0.5) & (max_probs < 0.6)).sum()),
            "0.6-0.7": int(((max_probs >= 0.6) & (max_probs < 0.7)).sum()),
            ">0.7": int((max_probs >= 0.7).sum()),
        },
        "confidence_dist": (
            df['confidence'].value_counts(normalize=True).to_dict()
            if 'confidence' in df.columns else {}
        ),
    }


def calibration_curve_1x2(df: pd.DataFrame, bins: int = 10) -> pd.DataFrame:
    """Calibration table: predicted home win prob vs actual home win rate."""
    df_temp = df.copy()
    df_temp['prob_bin'] = pd.cut(df_temp['home_prob'], bins=np.linspace(0, 1, bins + 1))
    cal = df_temp.groupby('prob_bin', observed=True).agg(
        avg_pred=('home_prob', 'mean'),
        actual_rate=('is_h', 'mean'),
        count=('match_id', 'size'),
    ).reset_index()
    cal['gap'] = cal['avg_pred'] - cal['actual_rate']
    return cal


def upset_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze favorite vs underdog win rates by probability bucket."""
    df_temp = df.copy()
    probs = df_temp[['home_prob', 'draw_prob', 'away_prob']].values
    df_temp['fav_prob'] = np.max(probs, axis=1)
    df_temp['fav_is_home'] = (df_temp['home_prob'] == df_temp['fav_prob'])
    df_temp['fav_is_away'] = (df_temp['away_prob'] == df_temp['fav_prob'])

    df_temp['fav_won'] = (
        (df_temp['fav_is_home'] & (df_temp['result_1x2'] == 'H')) |
        (df_temp['fav_is_away'] & (df_temp['result_1x2'] == 'A'))
    ).astype(int)
    df_temp['underdog_won'] = (
        (df_temp['fav_is_home'] & (df_temp['result_1x2'] == 'A')) |
        (df_temp['fav_is_away'] & (df_temp['result_1x2'] == 'H'))
    ).astype(int)

    bins_edges = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
    df_temp['fav_bin'] = pd.cut(df_temp['fav_prob'], bins=bins_edges)

    return df_temp.groupby('fav_bin', observed=True).agg(
        avg_fav_prob=('fav_prob', 'mean'),
        fav_win_rate=('fav_won', 'mean'),
        underdog_win_rate=('underdog_won', 'mean'),
        draw_rate=('is_d', 'mean'),
        count=('match_id', 'size'),
    ).reset_index()


def evaluate_score_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check if actual scoreline appears in Top 1/3/5 of predicted distribution.
    Also computes cumulative probability of correct scores.
    """
    top1_hits = top3_hits = top5_hits = 0
    cum_probs = []

    for _, row in df.iterrows():
        dist = row['score_probs']
        if not dist:
            continue
        sorted_scores = sorted(dist.items(), key=lambda x: x[1], reverse=True)
        actual = (int(row['home_goals']), int(row['away_goals']))

        top1 = [s[0] for s in sorted_scores[:1]]
        top3 = [s[0] for s in sorted_scores[:3]]
        top5 = [s[0] for s in sorted_scores[:5]]

        if actual in top1: top1_hits += 1
        if actual in top3: top3_hits += 1
        if actual in top5: top5_hits += 1

        # Cumulative prob of actual score
        cum_probs.append(dist.get(actual, 0.0))

    n = len(df)
    return {
        "top1_hit_rate": top1_hits / n if n else 0,
        "top3_hit_rate": top3_hits / n if n else 0,
        "top5_hit_rate": top5_hits / n if n else 0,
        "avg_actual_score_prob": float(np.mean(cum_probs)) if cum_probs else 0,
    }


# ============================================================================
# 10. FULL V5 PIPELINE
# ============================================================================

def _print_metrics(label: str, brier: dict, logloss: dict, sharpness: dict):
    """Helper to print a metrics block."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Brier 1X2 (multi):   {brier['brier_1x2']:.4f}")
    print(f"    - Home:            {brier['brier_home']:.4f}")
    print(f"    - Draw:            {brier['brier_draw']:.4f}")
    print(f"    - Away:            {brier['brier_away']:.4f}")
    print(f"  Brier Over 2.5:      {brier['brier_over_2_5']:.4f}")
    print(f"  Brier Over 3.5:      {brier['brier_over_3_5']:.4f}")
    print(f"  Brier BTTS:          {brier['brier_btts']:.4f}")
    print(f"  LogLoss 1X2:         {logloss['logloss_1x2']:.4f}")
    print(f"  LogLoss Over 2.5:    {logloss['logloss_over_2_5']:.4f}")
    print(f"  LogLoss BTTS:        {logloss['logloss_btts']:.4f}")
    print(f"  Sharpness (avg max): {sharpness['avg_max_prob']:.2%}")
    print(f"  Sharpness histogram: {sharpness['histogram']}")


def run_full_pipeline(model_path: str, truth_path: str) -> pd.DataFrame:
    """
    Execute the entire V5 post-processing pipeline.
    """
    print("\n" + "#" * 60)
    print("  V5 POST-PROCESSING PIPELINE")
    print("#" * 60)

    # ── 1. Load ──
    df = load_data(model_path, truth_path)
    print(f"\nLoaded {len(df)} matches.")

    # ── 2. BEFORE evaluation ──
    b_brier = compute_brier_scores(df)
    b_ll = compute_log_loss_scores(df)
    b_sharp = compute_sharpness(df)
    b_dist = evaluate_score_distribution(df)
    _print_metrics("BEFORE CORRECTION", b_brier, b_ll, b_sharp)
    print(f"  Score Dist Top1/3/5: "
          f"{b_dist['top1_hit_rate']:.0%} / "
          f"{b_dist['top3_hit_rate']:.0%} / "
          f"{b_dist['top5_hit_rate']:.0%}")

    # Pre-correction consistency audit
    consistency_before = df.apply(check_consistency, axis=1)
    n_incon_before = sum(1 for c in consistency_before if c['has_inconsistency'])
    print(f"\n  Inconsistencies detected: {n_incon_before}/{len(df)}")

    # ── 3. Fit calibrators ──
    print("\n>> Fitting probability calibrators (Isotonic)...")
    calibrators = fit_probability_calibrators(df, method='isotonic')
    print(f"   Calibrators fitted: {list(calibrators.keys())}")

    # ── 4. Apply calibration ──
    print(">> Applying calibration...")
    df = apply_calibration(df, calibrators)

    # ── 5. Apply upset adjustment ──
    print(">> Applying upset correction (favorite bias)...")
    df = df.apply(apply_upset_adjustment, axis=1)

    # ── 6. Align score distributions with xG ──
    print(">> Aligning score distributions with xG...")
    df['score_probs'] = df.apply(
        lambda r: align_distribution_with_xg(
            r['score_probs'], r['xg_home'], r['xg_away']
        ),
        axis=1,
    )

    # ── 7. Recompute market probabilities ──
    print(">> Recomputing market probabilities from distribution...")
    df = recompute_market_probs_for_df(df)

    # ── 8. Enforce consistency ──
    print(">> Enforcing numeric consistency...")
    df = df.apply(enforce_consistency, axis=1)

    # ── 9. Replace text ──
    print(">> Regenerating text summaries...")
    df['text_summary'] = df.apply(enforce_text_consistency, axis=1)

    # ── 10. AFTER evaluation ──
    a_brier = compute_brier_scores(df)
    a_ll = compute_log_loss_scores(df)
    a_sharp = compute_sharpness(df)
    a_dist = evaluate_score_distribution(df)
    _print_metrics("AFTER CORRECTION", a_brier, a_ll, a_sharp)
    print(f"  Score Dist Top1/3/5: "
          f"{a_dist['top1_hit_rate']:.0%} / "
          f"{a_dist['top3_hit_rate']:.0%} / "
          f"{a_dist['top5_hit_rate']:.0%}")

    # Post-correction consistency audit
    consistency_after = df.apply(check_consistency, axis=1)
    n_incon_after = sum(1 for c in consistency_after if c['has_inconsistency'])
    print(f"\n  Inconsistencies remaining: {n_incon_after}/{len(df)}")

    # ── 11. Improvement summary ──
    print(f"\n{'='*60}")
    print(f"  IMPROVEMENT SUMMARY")
    print(f"{'='*60}")

    improvements = {
        "Brier 1X2":      b_brier['brier_1x2'] - a_brier['brier_1x2'],
        "Brier Home":     b_brier['brier_home'] - a_brier['brier_home'],
        "Brier Over 2.5": b_brier['brier_over_2_5'] - a_brier['brier_over_2_5'],
        "Brier BTTS":     b_brier['brier_btts'] - a_brier['brier_btts'],
        "LogLoss 1X2":    b_ll['logloss_1x2'] - a_ll['logloss_1x2'],
        "LogLoss O2.5":   b_ll['logloss_over_2_5'] - a_ll['logloss_over_2_5'],
        "Inconsistencies": n_incon_before - n_incon_after,
    }
    for k, v in improvements.items():
        arrow = "+" if v > 0 else ""
        print(f"  {k:20s}: {arrow}{v:.4f}")

    # ── 12. Upset analysis comparison ──
    print(f"\n{'='*60}")
    print(f"  UPSET ANALYSIS (AFTER)")
    print(f"{'='*60}")
    upset_df = upset_analysis(df)
    print(upset_df.to_string(index=False))

    # ── 13. Fixed match examples ──
    print(f"\n{'='*60}")
    print(f"  FIXED MATCH EXAMPLES")
    print(f"{'='*60}")

    n_examples = min(5, len(df))
    for i in range(n_examples):
        row = df.iloc[i]
        print(f"\n  Match {row['match_id']}: "
              f"{row['home_team']} vs {row['away_team']}")
        print(f"  Actual: {int(row['home_goals'])}-{int(row['away_goals'])} "
              f"({row['result_1x2']})")
        print(f"  --- ORIGINAL ---")
        print(f"    H/D/A: {row['orig_home_prob']:.2f} / "
              f"{row['orig_draw_prob']:.2f} / {row['orig_away_prob']:.2f}")
        print(f"    O2.5={row['orig_over_2_5_prob']:.2f}  "
              f"O3.5={row['orig_over_3_5_prob']:.2f}  "
              f"BTTS={row['orig_btts_prob']:.2f}")
        # Original text (may contain Korean chars)
        try:
            print(f"    Text: {row['orig_text_summary']}")
        except Exception:
            print(f"    Text: [encoding error]")
        print(f"  --- CORRECTED ---")
        print(f"    H/D/A: {row['home_prob']:.2f} / "
              f"{row['draw_prob']:.2f} / {row['away_prob']:.2f}")
        print(f"    O2.5={row['over_2_5_prob']:.2f}  "
              f"O3.5={row['over_3_5_prob']:.2f}  "
              f"BTTS={row['btts_prob']:.2f}")
        try:
            print(f"    Text: {row['text_summary']}")
        except Exception:
            print(f"    Text: [encoding error]")

    return df


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Force UTF-8 output for Windows terminals
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding='utf-8', errors='replace'
        )

    try:
        df_final = run_full_pipeline("model_outputs.csv", "ground_truth.csv")
        print(f"\nPipeline complete. {len(df_final)} matches processed.")
    except Exception as e:
        import traceback
        print(f"Pipeline failed: {e}")
        traceback.print_exc()

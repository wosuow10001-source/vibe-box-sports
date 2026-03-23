"""
유틸리티 함수들
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path


def calculate_elo_rating(team1_elo, team2_elo, result, k_factor=32):
    """
    ELO 레이팅 계산
    result: 1 (team1 승), 0.5 (무승부), 0 (team2 승)
    """
    expected1 = 1 / (1 + 10 ** ((team2_elo - team1_elo) / 400))
    expected2 = 1 - expected1
    
    new_elo1 = team1_elo + k_factor * (result - expected1)
    new_elo2 = team2_elo + k_factor * ((1 - result) - expected2)
    
    return new_elo1, new_elo2


def calculate_poisson_probability(avg_goals):
    """
    포아송 분포를 이용한 득점 확률 계산
    """
    from scipy.stats import poisson
    
    probabilities = {}
    for goals in range(0, 6):
        probabilities[goals] = poisson.pmf(goals, avg_goals)
    
    return probabilities


def calculate_expected_goals(shots, shots_on_target, big_chances):
    """
    xG (Expected Goals) 계산
    """
    # 간단한 xG 모델
    xg = (shots_on_target * 0.3) + (big_chances * 0.5) + (shots * 0.05)
    return min(xg, 5.0)  # 최대 5골로 제한


def normalize_team_name(name):
    """팀 이름 정규화"""
    # 공백 제거, 소문자 변환
    normalized = name.strip().lower()
    
    # 별칭 매핑
    aliases = {
        'fc서울': '서울',
        '울산현대': '울산',
        '전북현대': '전북',
        'lg트윈스': 'lg',
        'ssg랜더스': 'ssg',
    }
    
    return aliases.get(normalized, normalized)


def calculate_form_index(recent_results):
    """
    최근 폼 지수 계산 (0-100)
    recent_results: ['W', 'D', 'L', 'W', 'W']
    """
    if not recent_results:
        return 50
    
    points = {'W': 3, 'D': 1, 'L': 0}
    total_points = sum(points.get(r, 0) for r in recent_results)
    max_points = len(recent_results) * 3
    
    return (total_points / max_points) * 100


def calculate_momentum(recent_results):
    """
    모멘텀 계산 (최근 경기일수록 가중치 높음)
    """
    if not recent_results:
        return 0
    
    weights = [0.3, 0.25, 0.2, 0.15, 0.1]
    points = {'W': 1, 'D': 0, 'L': -1}
    
    momentum = sum(
        points.get(r, 0) * w 
        for r, w in zip(recent_results, weights[:len(recent_results)])
    )
    
    return momentum


def calculate_strength_of_schedule(opponents_ratings):
    """
    상대 전력 계산 (SOS - Strength of Schedule)
    """
    if not opponents_ratings:
        return 50
    
    return np.mean(opponents_ratings)


def calculate_rest_advantage(rest_days_home, rest_days_away):
    """
    휴식일 어드밴티지 계산
    """
    optimal_rest = 4
    
    home_penalty = abs(rest_days_home - optimal_rest) * 0.02
    away_penalty = abs(rest_days_away - optimal_rest) * 0.02
    
    advantage = away_penalty - home_penalty
    
    return advantage


def calculate_travel_fatigue(distance_km):
    """
    이동 거리에 따른 피로도
    """
    if distance_km < 100:
        return 0
    elif distance_km < 300:
        return 0.02
    elif distance_km < 500:
        return 0.05
    else:
        return 0.1


def calculate_altitude_effect(home_altitude, away_altitude):
    """
    고도 차이 영향
    """
    altitude_diff = abs(home_altitude - away_altitude)
    
    if altitude_diff < 500:
        return 0
    elif altitude_diff < 1000:
        return 0.03
    else:
        return 0.05


def calculate_weather_impact_score(weather_condition, temperature, wind_speed):
    """
    날씨 영향 점수
    """
    score = 0
    
    # 날씨 조건
    weather_penalties = {
        '맑음': 0,
        '흐림': 0.02,
        '비': 0.05,
        '눈': 0.08,
        '강풍': 0.06
    }
    score += weather_penalties.get(weather_condition, 0)
    
    # 극한 기온
    if temperature < 5 or temperature > 35:
        score += 0.03
    
    # 강풍
    if wind_speed > 10:
        score += 0.04
    
    return score


def calculate_injury_impact(injured_players, team_strength):
    """
    부상자 영향 계산
    """
    if not injured_players:
        return 0
    
    # 부상자 중요도에 따라 가중치
    impact = 0
    for player in injured_players:
        importance = player.get('importance', 0.5)  # 0-1
        impact += importance * 0.1
    
    return min(impact, 0.3)  # 최대 30% 영향


def calculate_tactical_advantage(team1_style, team2_style):
    """
    전술적 상성 계산
    """
    # 전술 상성표
    advantages = {
        ('공격형', '수비형'): 0.1,
        ('수비형', '공격형'): -0.1,
        ('점유형', '역습형'): 0.05,
        ('역습형', '점유형'): -0.05,
    }
    
    return advantages.get((team1_style, team2_style), 0)


def calculate_head_to_head_factor(h2h_results):
    """
    맞대결 기록 요인
    """
    if not h2h_results:
        return 0.5
    
    team1_wins = sum(1 for r in h2h_results if r == 'W')
    total = len(h2h_results)
    
    return team1_wins / total


def calculate_confidence_interval(probability, sample_size):
    """
    신뢰 구간 계산
    """
    import scipy.stats as stats
    
    # 95% 신뢰구간
    z_score = 1.96
    margin = z_score * np.sqrt((probability * (1 - probability)) / sample_size)
    
    lower = max(0, probability - margin)
    upper = min(1, probability + margin)
    
    return lower, upper


def format_probability(prob):
    """확률 포맷팅"""
    return f"{prob * 100:.1f}%"


def format_score(score):
    """점수 포맷팅"""
    return f"{score:.1f}"


def get_match_date_info(match_date):
    """경기 날짜 정보"""
    if isinstance(match_date, str):
        match_date = datetime.fromisoformat(match_date)
    
    return {
        'date': match_date.strftime('%Y-%m-%d'),
        'day_of_week': match_date.strftime('%A'),
        'is_weekend': match_date.weekday() >= 5,
        'days_until': (match_date - datetime.now()).days
    }


def save_prediction_history(prediction, filename='prediction_history.json'):
    """예측 기록 저장"""
    history_file = Path('data') / filename
    
    # 기존 기록 로드
    if history_file.exists():
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    # 새 예측 추가
    prediction['timestamp'] = datetime.now().isoformat()
    history.append(prediction)
    
    # 저장
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_prediction_history(filename='prediction_history.json'):
    """예측 기록 로드"""
    history_file = Path('data') / filename
    
    if not history_file.exists():
        return []
    
    with open(history_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_prediction_accuracy(history):
    """예측 정확도 계산"""
    if not history:
        return 0
    
    correct = 0
    total = 0
    
    for pred in history:
        if 'actual_result' in pred:
            predicted = pred['predicted_result']
            actual = pred['actual_result']
            
            if predicted == actual:
                correct += 1
            total += 1
    
    return (correct / total * 100) if total > 0 else 0


def generate_match_report(prediction, team1, team2):
    """경기 분석 리포트 생성"""
    report = f"""
# 경기 분석 리포트

## 매치업
{team1} vs {team2}

## 예측 결과
- 홈 승리: {format_probability(prediction['home_win_prob'])}
- 무승부: {format_probability(prediction['draw_prob'])}
- 원정 승리: {format_probability(prediction['away_win_prob'])}

## 예상 스코어
{team1} {prediction['expected_score_home']} - {prediction['expected_score_away']} {team2}

## 주요 분석 포인트
"""
    
    for factor in prediction['key_factors']:
        report += f"- {factor}\n"
    
    report += f"\n## 예측 신뢰도\n{format_probability(prediction['confidence'])}"
    
    return report


def export_to_excel(data, filename):
    """엑셀로 내보내기"""
    df = pd.DataFrame(data)
    output_file = Path('data') / filename
    df.to_excel(output_file, index=False, engine='openpyxl')
    return output_file


def import_from_csv(filename):
    """CSV에서 가져오기"""
    input_file = Path('data') / filename
    return pd.read_csv(input_file, encoding='utf-8-sig')

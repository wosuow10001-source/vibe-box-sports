"""
고급 메트릭스 사용 예제
- 축구, 야구, 배구 고급 메트릭스 계산 및 예측 통합
"""

# ============================================================
# 1. 축구 (Soccer) - xG, xA, PPDA 예제
# ============================================================

from modules.advanced_soccer_metrics import get_soccer_metrics

# K-League 메트릭스 시스템
soccer_metrics = get_soccer_metrics("K-League")

# 선수 통계 예제
player_stats = {
    'name': '손흥민',
    'position': 'FW',
    'goals': 15,
    'assists': 8,
    'shots': 80,
    'shots_on_target': 45,
    'key_passes': 20,
    'passes': 1200,
    'pass_completion': 82,
    'tackles': 15,
    'interceptions': 10
}

# 고급 메트릭스 계산
metrics = soccer_metrics.calculate_all_metrics(player_stats)
print("=== 축구 선수 메트릭스 ===")
print(f"xG (기대 득점): {metrics['xg']}")
print(f"xA (기대 어시스트): {metrics['xa']}")
print(f"xGChain (공격 기여도): {metrics['xgchain']}")
print(f"공격 평가: {metrics['attack_rating']}")
print(f"수비 평가: {metrics['defense_rating']}")
print(f"종합 평가: {metrics['overall_rating']}")
print()

# 팀 전력 계산 예제
team_players = [
    {'name': '선수1', 'position': 'FW', 'goals': 12, 'assists': 5, 'shots': 60, 'shots_on_target': 30},
    {'name': '선수2', 'position': 'MF', 'goals': 8, 'assists': 10, 'shots': 40, 'shots_on_target': 20},
    {'name': '선수3', 'position': 'DF', 'goals': 2, 'assists': 3, 'tackles': 50, 'interceptions': 40},
]

team_strength = soccer_metrics.calculate_team_strength_from_players(team_players)
print("=== 축구 팀 전력 ===")
print(f"팀 xG: {team_strength['team_xg']}")
print(f"팀 xA: {team_strength['team_xa']}")
print(f"예상 득점: {team_strength['expected_goals']}")
print(f"예상 실점: {team_strength['expected_conceded']}")
print(f"공격력: {team_strength['attack_rating']}")
print(f"수비력: {team_strength['defense_rating']}")
print()


# ============================================================
# 2. 야구 (Baseball) - OPS, wOBA, ERA+, FIP, WAR 예제
# ============================================================

from modules.advanced_baseball_metrics import get_baseball_metrics

# KBO 메트릭스 시스템
baseball_metrics = get_baseball_metrics("KBO")

# 타자 통계 예제
batter_stats = {
    'name': '김하성',
    'position': 'SS',
    'ab': 500,  # 타수
    'h': 150,   # 안타
    'bb': 60,   # 볼넷
    'hbp': 5,   # 몸에 맞는 공
    'sf': 3,    # 희생 플라이
    '1b': 100,  # 1루타
    '2b': 30,   # 2루타
    '3b': 5,    # 3루타
    'hr': 15,   # 홈런
    'sb': 20,   # 도루
    'cs': 5,    # 도루 실패
    'pa': 570   # 타석
}

# 타자 메트릭스 계산
batter_metrics = baseball_metrics.calculate_all_metrics_batter(batter_stats)
print("=== 야구 타자 메트릭스 ===")
print(f"OPS (출루율+장타율): {batter_metrics['ops']}")
print(f"wOBA (가중 출루율): {batter_metrics['woba']}")
print(f"WAR (승리 기여): {batter_metrics['war']}")
print(f"종합 평가: {batter_metrics['rating']}")
print()

# 투수 통계 예제
pitcher_stats = {
    'name': '류현진',
    'era': 3.20,  # 평균자책점
    'ip': 180,    # 이닝
    'hr': 15,     # 피홈런
    'bb': 40,     # 볼넷
    'k': 150,     # 삼진
    'park_factor': 1.0
}

# 투수 메트릭스 계산
pitcher_metrics = baseball_metrics.calculate_all_metrics_pitcher(pitcher_stats)
print("=== 야구 투수 메트릭스 ===")
print(f"ERA+ (조정 평균자책점): {pitcher_metrics['era_plus']}")
print(f"FIP (수비 무관 투구): {pitcher_metrics['fip']}")
print(f"WAR (승리 기여): {pitcher_metrics['war']}")
print(f"종합 평가: {pitcher_metrics['rating']}")
print()

# 팀 전력 계산 예제
batters = [
    {'ab': 500, 'h': 150, 'bb': 60, 'hr': 15, 'position': 'SS'},
    {'ab': 480, 'h': 140, 'bb': 50, 'hr': 20, 'position': '3B'},
    {'ab': 520, 'h': 160, 'bb': 40, 'hr': 10, 'position': 'CF'},
]

pitchers = [
    {'era': 3.20, 'ip': 180, 'hr': 15, 'bb': 40, 'k': 150},
    {'era': 3.80, 'ip': 160, 'hr': 18, 'bb': 50, 'k': 130},
]

team_strength = baseball_metrics.calculate_team_strength_from_players(batters, pitchers)
print("=== 야구 팀 전력 ===")
print(f"평균 OPS: {team_strength['avg_ops']}")
print(f"평균 wOBA: {team_strength['avg_woba']}")
print(f"평균 ERA+: {team_strength['avg_era_plus']}")
print(f"평균 FIP: {team_strength['avg_fip']}")
print(f"총 WAR: {team_strength['total_war']}")
print(f"예상 득점: {team_strength['expected_runs']}")
print(f"예상 실점: {team_strength['expected_runs_allowed']}")
print()


# ============================================================
# 3. 배구 (Volleyball) - 스파이크율, 블록, 점프, 세트 효율 예제
# ============================================================

from modules.advanced_volleyball_metrics import get_volleyball_metrics

# V-League 메트릭스 시스템
volleyball_metrics = get_volleyball_metrics("V-League")

# 선수 통계 예제 (주공격수)
player_stats = {
    'name': '김연경',
    'position': 'OH',  # Outside Hitter
    'kills': 250,
    'errors': 80,
    'attempts': 600,
    'block_solos': 20,
    'block_assists': 40,
    'digs': 150,
    'assists': 30,
    'set_attempts': 50,
    'sets_played': 80,
    'jump_height': 340,  # cm
    'receptions': 200
}

# 배구 메트릭스 계산
metrics = volleyball_metrics.calculate_all_metrics(player_stats)
print("=== 배구 선수 메트릭스 ===")
print(f"스파이크 성공률: {metrics['spike_success_rate']}")
print(f"블록 효율 (세트당): {metrics['block_efficiency']}")
print(f"디그 효율 (세트당): {metrics['dig_efficiency']}")
print(f"세트 효율: {metrics['set_efficiency']}")
print(f"점프 높이: {metrics['jump_height']} cm")
print(f"세트당 점프: {metrics['jumps_per_set']}")
print(f"점프 워크로드: {metrics['jump_workload']}")
print(f"이동 워크로드: {metrics['movement_workload']}")
print(f"피로도 계수: {metrics['fatigue_factor']}")
print(f"공격 평가: {metrics['attack_rating']}")
print(f"수비 평가: {metrics['defense_rating']}")
print()

# 팀 전력 계산 예제
team_players = [
    {'position': 'OH', 'kills': 250, 'errors': 80, 'attempts': 600, 'sets_played': 80},
    {'position': 'OH', 'kills': 220, 'errors': 70, 'attempts': 550, 'sets_played': 80},
    {'position': 'MB', 'kills': 150, 'errors': 50, 'attempts': 400, 'block_solos': 30, 'sets_played': 80},
    {'position': 'MB', 'kills': 140, 'errors': 45, 'attempts': 380, 'block_solos': 25, 'sets_played': 80},
    {'position': 'S', 'assists': 800, 'set_attempts': 1000, 'sets_played': 80},
    {'position': 'OP', 'kills': 200, 'errors': 60, 'attempts': 500, 'sets_played': 80},
    {'position': 'L', 'digs': 400, 'receptions': 500, 'sets_played': 80},
]

team_strength = volleyball_metrics.calculate_team_strength_from_players(team_players)
print("=== 배구 팀 전력 ===")
print(f"팀 스파이크 성공률: {team_strength['team_spike_rate']}")
print(f"팀 블록 효율: {team_strength['team_block_eff']}")
print(f"팀 디그 효율: {team_strength['team_dig_eff']}")
print(f"팀 세트 효율: {team_strength['team_set_eff']}")
print(f"평균 워크로드: {team_strength['avg_workload']}")
print(f"팀 피로도: {team_strength['team_fatigue']}")
print(f"공격력: {team_strength['attack_rating']}")
print(f"수비력: {team_strength['defense_rating']}")
print()


# ============================================================
# 4. 예측 모델 통합 예제
# ============================================================

print("=== 예측 모델 통합 예제 ===")
print("실제 예측 시에는 predictor의 _enhance_team_data_with_advanced_metrics 메서드를 사용합니다.")
print()
print("축구 예측:")
print("  home_data = predictor._enhance_team_data_with_advanced_metrics(")
print("      home_data, home_players, league='K-League')")
print()
print("야구 예측:")
print("  home_data = predictor._enhance_team_data_with_advanced_metrics(")
print("      home_data, batters, pitchers, league='KBO')")
print()
print("배구 예측:")
print("  home_data = predictor._enhance_team_data_with_advanced_metrics(")
print("      home_data, players, league='V-League')")
print()
print("이렇게 보강된 team_data로 predict_match()를 호출하면")
print("고급 메트릭스가 반영된 정확한 예측 결과를 얻을 수 있습니다.")

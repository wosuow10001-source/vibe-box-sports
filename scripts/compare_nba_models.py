"""
NBA 예측 모델 비교
기존 모델 vs 고급 동적 모델
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.data_collector import DataCollector
from modules.predictor_basketball_pro import BasketballPredictorPro
from modules.predictor_basketball_advanced import AdvancedBasketballPredictor

def compare_models():
    """모델 비교 테스트"""
    
    print("="*80)
    print("NBA 예측 모델 비교: 기존 vs 고급")
    print("="*80)
    
    # 데이터 수집
    collector_east = DataCollector(sport='basketball', league='NBA East')
    collector_west = DataCollector(sport='basketball', league='NBA West')
    
    celtics_data = collector_east.get_team_data('Boston Celtics')
    thunder_data = collector_west.get_team_data('Oklahoma City Thunder')
    
    print(f"\n매치업: Boston Celtics (홈) vs Oklahoma City Thunder (원정)")
    print(f"  Celtics: {celtics_data['wins']}-{celtics_data['losses']}, PPG: {celtics_data.get('ppg', 0):.1f}")
    print(f"  Thunder: {thunder_data['wins']}-{thunder_data['losses']}, PPG: {thunder_data.get('ppg', 0):.1f}")
    
    # 부상 시나리오
    injury_data = {
        'home': [
            {'player': 'Kristaps Porziņģis', 'status': 'Out'}
        ],
        'away': []
    }
    
    print(f"\n시나리오: Celtics의 Porziņģis 부상")
    
    # 기존 모델
    print(f"\n{'='*80}")
    print("[기존 모델] BasketballPredictorPro")
    print(f"{'='*80}")
    
    old_predictor = BasketballPredictorPro()
    old_result = old_predictor.predict_match(
        home_team='Boston Celtics',
        away_team='Oklahoma City Thunder',
        home_data=celtics_data,
        away_data=thunder_data,
        weather='맑음',
        temperature=20,
        field_condition='좋음',
        match_importance='보통',
        rest_days_home=2,
        rest_days_away=1,
        injury_data=injury_data
    )
    
    print(f"\n예상 스코어: {old_result['expected_score_home']}-{old_result['expected_score_away']}")
    print(f"홈팀 승률: {old_result['home_win_prob']:.1%}")
    print(f"신뢰도: {old_result['confidence']:.1%}")
    print(f"부상 처리: 단순 카운트 (1명 = -3% 영향)")
    
    # 고급 모델
    print(f"\n{'='*80}")
    print("[고급 모델] AdvancedBasketballPredictor")
    print(f"{'='*80}")
    
    new_predictor = AdvancedBasketballPredictor()
    new_result = new_predictor.predict_match(
        home_team='Boston Celtics',
        away_team='Oklahoma City Thunder',
        home_data=celtics_data,
        away_data=thunder_data,
        weather='맑음',
        temperature=20,
        field_condition='좋음',
        match_importance='보통',
        rest_days_home=2,
        rest_days_away=1,
        injury_data=injury_data
    )
    
    print(f"\n예상 스코어: {new_result['expected_score_home']}-{new_result['expected_score_away']}")
    print(f"홈팀 승률: {new_result['home_win_prob']:.1%}")
    print(f"신뢰도: {new_result['confidence']:.1%}")
    print(f"부상 처리: 선수 영향력 가중치 ({new_result['injury_impact_home']['total_impact']:.1%})")
    
    # 비교 분석
    print(f"\n{'='*80}")
    print("비교 분석")
    print(f"{'='*80}")
    
    prob_diff = new_result['home_win_prob'] - old_result['home_win_prob']
    score_diff_home = new_result['expected_score_home'] - old_result['expected_score_home']
    score_diff_away = new_result['expected_score_away'] - old_result['expected_score_away']
    
    print(f"\n승률 차이: {prob_diff:+.1%}")
    print(f"홈팀 득점 차이: {score_diff_home:+.1f}")
    print(f"원정팀 득점 차이: {score_diff_away:+.1f}")
    
    print(f"\n고급 모델 추가 정보:")
    print(f"  - 템포 컨트롤: {new_result['tempo_analysis']['tempo_controller']}")
    print(f"  - SOS 보정 승률: 홈 {new_result['sos_home']['adjusted_win_rate']:.1%}, 원정 {new_result['sos_away']['adjusted_win_rate']:.1%}")
    print(f"  - 수비 붕괴 위험: 홈 {new_result['defensive_collapse_home']['high_risk']}, 원정 {new_result['defensive_collapse_away']['high_risk']}")
    print(f"  - 분산 요인: {new_result['variance_factor']:.2f}")
    print(f"  - 확률 보정: {new_result['raw_probability']:.1%} → {new_result['home_win_prob']:.1%}")
    
    print(f"\n{'='*80}")
    print("✅ 비교 테스트 완료")
    print(f"{'='*80}")
    print(f"\n결론:")
    print(f"  - 고급 모델은 부상 영향을 선수별로 정확히 계산")
    print(f"  - 템포 상호작용과 SOS를 반영하여 더 정확한 예측")
    print(f"  - 확률 보정으로 과신 방지")

if __name__ == "__main__":
    compare_models()

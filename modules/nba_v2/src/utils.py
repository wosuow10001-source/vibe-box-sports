import os
import logging
from typing import Dict

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NBA_V2")

class NBAConfig:
    """NBA V2 시스템 설정"""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODEL_DIR = os.path.join(BASE_DIR, "models")
    
    # 상향된 NBA 베이스라인 (V1에서 배운 레슨 반영)
    LEAGUE_AVG_POINTS = 115.0
    LEAGUE_AVG_PACE = 100.0
    
    # 시뮬레이션 설정
    SIM_ITERATIONS = 5000
    
    # 패스 필터 임계값
    PASS_THRESHOLD = 0.05
    
    @classmethod
    def ensure_dirs(cls):
        """필요한 디렉토리 생성"""
        for d in [cls.DATA_DIR, cls.MODEL_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

def format_json_output(home: str, away: str, result: Dict) -> Dict:
    """사용자 요청 규격에 맞춘 JSON 출력 포맷팅 (및 UI 호환을 위한 Flat Key 유지)"""
    
    # UI 호환을 위한 기본 값 추출
    h_prob = float(result.get('home_win_prob') if result.get('home_win_prob') is not None else 0.5)
    a_prob = float(result.get('away_win_prob') if result.get('away_win_prob') is not None else 0.5)
    h_score = int(result.get('expected_score_home') if result.get('expected_score_home') is not None else 0)
    a_score = int(result.get('expected_score_away') if result.get('expected_score_away') is not None else 0)
    
    return {
        # --- 사용자 요청 신규 규격 (Nested) ---
        "home_team": home,
        "away_team": away,
        "predicted_score": {
            "home": h_score,
            "away": a_score
        } if h_score > 0 else None,
        "win_probability": {
            "home": h_prob,
            "away": a_prob
        },
        "spread_probability": result.get('spread_probability'),
        "over_under_probability": result.get('over_under_probability'),
        "sport_type": result.get('sport_type', 'basketball'),
        "confidence": result.get('confidence', 'medium'),
        "pass_flag": result.get('pass_flag', False),
        "prediction": result.get('prediction', 'PASS'),
        "note": result.get('note', ""),
        "explanation": result.get('explanation', ""),
        "uncertainty": result.get('uncertainty', {}),
        "is_value_bet": result.get('is_value_bet', False) if not result.get('pass_flag') else False,
        "value_edge": result.get('value_edge', 0.0),
        "key_factors": result.get('key_factors', []),
        
        # --- 레거시 UI(app.py) 호환을 위한 Flat Keys ---
        "home_win_prob": h_prob,
        "away_win_prob": a_prob,
        "draw_prob": 0.0,
        "expected_score_home": h_score,
        "expected_score_away": a_score,
        "confidence_score": float(result.get('confidence_score', 0.5)),
        "decision": result.get('decision', 'PLAY')
    }

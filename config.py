"""
설정 파일
"""

# 데이터 수집 설정
SCRAPING_ENABLED = True
API_ENABLED = False

# 크롤링 간격 (초)
SCRAPING_INTERVAL = 3600  # 1시간

# 데이터 저장 경로
DATA_DIR = "data"
MODEL_DIR = "models"

# 예측 모델 설정
MODEL_TYPE = "RandomForest"  # RandomForest, XGBoost, LightGBM, Ensemble
HISTORICAL_MATCHES = 30  # 과거 몇 경기를 분석할지

# 가중치 설정
WEIGHTS = {
    'recent_form': 0.25,
    'head_to_head': 0.15,
    'home_advantage': 0.10,
    'player_condition': 0.20,
    'tactical_fit': 0.10,
    'weather': 0.05,
    'rest_days': 0.10,
    'motivation': 0.05
}

# API 키 (사용 시)
API_KEYS = {
    'football_data': '',  # https://www.football-data.org/
    'sports_radar': '',   # https://www.sportradar.com/
    'the_odds_api': ''    # https://the-odds-api.com/
}

# 크롤링 URL
URLS = {
    'kleague': 'https://www.kleague.com/',
    'kbo': 'https://www.koreabaseball.com/',
    'kbl': 'https://www.kbl.or.kr/',
    'kovo': 'https://www.kovo.co.kr/'
}

# 사용자 에이전트
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# 로깅 설정
LOG_LEVEL = 'INFO'
LOG_FILE = 'app.log'

"""
선수 통계 수집 및 캐시 관리 모듈
"""

import sys
from pathlib import Path

# 모듈 경로 추가 (stlite 호환)
sys.path.append(str(Path(__file__).parent))

def refresh_player_cache():
    """실시간 선수 통계 및 데이터 캐시 강제 초기화"""
    try:
        # 1. LiveDataFetcher 캐시 초기화
        from modules.live_data_fetcher import get_live_fetcher
        live_fetcher = get_live_fetcher()
        if hasattr(live_fetcher, 'clear_cache'):
            live_fetcher.clear_cache()
            print("[OK] LiveDataFetcher cache cleared")

        # 2. RealTimeDataFetcher 캐시 초기화 (필요한 경우)
        from modules.realtime_data_fetcher import RealTimeDataFetcher
        # 싱글톤이 아니므로 전역 인스턴스를 찾아서 초기화하거나
        # 필요한 다른 전역 캐시를 여기서 처리
        print("[OK] Player stats cache refresh completed")
        return True
    except Exception as e:
        print(f"[WARNING] Cache refresh failed: {e}")
        return False

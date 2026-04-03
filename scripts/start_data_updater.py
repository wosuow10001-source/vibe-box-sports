"""
데이터 자동 업데이트 시작 스크립트

사용법:
    python scripts/start_data_updater.py

기능:
    - 선수 통계 자동 업데이트 (매일 오전 6시)
    - 부상 리포트 자동 수집 (매 시간)
    - 경기 일정 자동 업데이트 (매일 오전 7시)
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.data_update_scheduler import get_data_scheduler
import time


def main():
    """메인 함수"""
    
    print("="*60)
    print("🚀 스포츠 데이터 자동 업데이트 시스템")
    print("="*60)
    print()
    
    # 스케줄러 시작
    scheduler = get_data_scheduler()
    scheduler.start()
    
    print()
    print("스케줄러가 백그라운드에서 실행 중입니다.")
    print("종료하려면 Ctrl+C를 누르세요.")
    print()
    
    try:
        # 무한 대기
        while True:
            time.sleep(60)
            
            # 매 시간마다 상태 출력
            if time.localtime().tm_min == 0:
                status = scheduler.get_status()
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 스케줄러 상태:")
                print(f"  - 총 선수: {status['database']['total_players']}명")
                print(f"  - 부상자: {status['database']['total_injuries']}명")
                print(f"  - 24시간 내 업데이트: {status['database']['recent_updates_24h']}명")
                print()
    
    except KeyboardInterrupt:
        print("\n\n종료 중...")
        scheduler.stop()
        print("✅ 스케줄러가 정상적으로 종료되었습니다.")


if __name__ == '__main__':
    main()

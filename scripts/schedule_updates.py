"""
자동 업데이트 스케줄러
매일 오전 9시에 데이터 자동 업데이트
"""

import schedule
import time
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from daily_update import main as update_data


def scheduled_update():
    """스케줄된 업데이트 실행"""
    print(f"\n{'='*60}")
    print(f"⏰ 스케줄 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        update_data()
        print("\n✅ 스케줄 업데이트 성공")
    except Exception as e:
        print(f"\n❌ 스케줄 업데이트 실패: {e}")


def main():
    """스케줄러 메인 함수"""
    print("="*60)
    print("🤖 자동 업데이트 스케줄러 시작")
    print("="*60)
    print("📅 스케줄: 매일 오전 9시")
    print("⏸️  중지: Ctrl+C")
    print("="*60)
    
    # 매일 오전 9시 실행
    schedule.every().day.at("09:00").do(scheduled_update)
    
    # 테스트용: 매 1시간마다 실행 (주석 해제하여 사용)
    # schedule.every(1).hours.do(scheduled_update)
    
    # 즉시 한 번 실행 (선택사항)
    print("\n🔄 초기 업데이트 실행 중...")
    scheduled_update()
    
    print(f"\n⏰ 다음 업데이트: {schedule.next_run()}")
    
    # 스케줄 실행 루프
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    except KeyboardInterrupt:
        print("\n\n⏹️  스케줄러 중지됨")
        print("="*60)


if __name__ == "__main__":
    # schedule 라이브러리 설치 확인
    try:
        import schedule
    except ImportError:
        print("❌ 'schedule' 라이브러리가 설치되지 않았습니다.")
        print("📦 설치 명령: pip install schedule")
        sys.exit(1)
    
    main()

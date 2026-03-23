"""
일일 자동 데이터 업데이트 스크립트
매일 오전 9시 실행하여 NBA, MLB, KBO 등의 최신 데이터 수집
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from modules.live_data_fetcher import get_live_fetcher
from datetime import datetime
import json


def update_nba_data():
    """NBA 데이터 업데이트"""
    print("\n" + "="*60)
    print("NBA 데이터 업데이트 시작")
    print("="*60)
    
    fetcher = get_live_fetcher()
    
    # Eastern Conference
    print("\n📊 NBA Eastern Conference 업데이트 중...")
    east_data = fetcher.fetch_nba_standings("East")
    print(f"✅ Eastern Conference: {len(east_data)}개 팀 업데이트 완료")
    
    # Western Conference
    print("\n📊 NBA Western Conference 업데이트 중...")
    west_data = fetcher.fetch_nba_standings("West")
    print(f"✅ Western Conference: {len(west_data)}개 팀 업데이트 완료")
    
    # 데이터 신선도 확인
    freshness = fetcher.get_data_freshness("NBA East")
    print(f"\n📅 데이터 신선도: {freshness['status']} - {freshness['message']}")
    
    return {
        'east': east_data,
        'west': west_data,
        'updated_at': datetime.now().isoformat()
    }


def update_mlb_data():
    """MLB 데이터 업데이트 (구현 예정)"""
    print("\n" + "="*60)
    print("MLB 데이터 업데이트 (구현 예정)")
    print("="*60)
    return None


def update_kbo_data():
    """KBO 데이터 업데이트 (구현 예정)"""
    print("\n" + "="*60)
    print("KBO 데이터 업데이트 (구현 예정)")
    print("="*60)
    return None


def save_update_log(results: dict):
    """업데이트 로그 저장"""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"update_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📝 업데이트 로그 저장: {log_file}")


def main():
    """메인 업데이트 함수"""
    print("\n" + "="*60)
    print(f"🔄 일일 데이터 업데이트 시작")
    print(f"⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'updates': {}
    }
    
    # NBA 업데이트
    try:
        nba_data = update_nba_data()
        results['updates']['nba'] = {
            'status': 'success',
            'teams_updated': len(nba_data['east']) + len(nba_data['west']),
            'data': nba_data
        }
    except Exception as e:
        print(f"❌ NBA 업데이트 실패: {e}")
        results['updates']['nba'] = {
            'status': 'failed',
            'error': str(e)
        }
    
    # MLB 업데이트 (구현 예정)
    # try:
    #     mlb_data = update_mlb_data()
    #     results['updates']['mlb'] = {'status': 'success', 'data': mlb_data}
    # except Exception as e:
    #     results['updates']['mlb'] = {'status': 'failed', 'error': str(e)}
    
    # KBO 업데이트 (구현 예정)
    # try:
    #     kbo_data = update_kbo_data()
    #     results['updates']['kbo'] = {'status': 'success', 'data': kbo_data}
    # except Exception as e:
    #     results['updates']['kbo'] = {'status': 'failed', 'error': str(e)}
    
    # 로그 저장
    save_update_log(results)
    
    print("\n" + "="*60)
    print("✅ 일일 데이터 업데이트 완료")
    print("="*60)
    
    return results


if __name__ == "__main__":
    main()

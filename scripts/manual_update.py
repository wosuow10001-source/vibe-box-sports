"""
수동 데이터 업데이트 스크립트

사용법:
    # 특정 선수 업데이트
    python scripts/manual_update.py --player "Jayson Tatum" --team "Boston Celtics" --league NBA
    
    # 팀 전체 업데이트
    python scripts/manual_update.py --team "Detroit Pistons" --league NBA
    
    # 부상 리포트 업데이트
    python scripts/manual_update.py --injuries --league NBA
    
    # 경기 일정 업데이트
    python scripts/manual_update.py --schedule --team "Los Angeles Lakers" --league NBA
"""

import sys
from pathlib import Path
import argparse

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.data_update_scheduler import get_data_scheduler


def main():
    """메인 함수"""
    
    parser = argparse.ArgumentParser(description='스포츠 데이터 수동 업데이트')
    
    parser.add_argument('--player', type=str, help='선수 이름')
    parser.add_argument('--team', type=str, help='팀 이름')
    parser.add_argument('--league', type=str, choices=['NBA', 'KBL'], help='리그')
    parser.add_argument('--injuries', action='store_true', help='부상 리포트 업데이트')
    parser.add_argument('--schedule', action='store_true', help='경기 일정 업데이트')
    parser.add_argument('--all', action='store_true', help='모든 데이터 업데이트')
    
    args = parser.parse_args()
    
    scheduler = get_data_scheduler()
    
    print("="*60)
    print("🔧 스포츠 데이터 수동 업데이트")
    print("="*60)
    print()
    
    # 모든 데이터 업데이트
    if args.all:
        print("📊 모든 데이터 업데이트 시작...\n")
        scheduler.update_all_player_stats()
        scheduler.update_injury_reports()
        scheduler.update_game_schedules()
        print("\n✅ 모든 데이터 업데이트 완료!")
        return
    
    # 부상 리포트 업데이트
    if args.injuries:
        print("🏥 부상 리포트 업데이트 중...\n")
        scheduler.update_injury_reports()
        print("\n✅ 부상 리포트 업데이트 완료!")
        return
    
    # 경기 일정 업데이트
    if args.schedule:
        if not args.team or not args.league:
            print("❌ 오류: --team과 --league를 함께 지정해야 합니다.")
            return
        
        print(f"📅 {args.team} 경기 일정 업데이트 중...\n")
        scheduler.update_game_schedules()
        print("\n✅ 경기 일정 업데이트 완료!")
        return
    
    # 특정 선수 업데이트
    if args.player:
        if not args.team or not args.league:
            print("❌ 오류: --team과 --league를 함께 지정해야 합니다.")
            return
        
        print(f"👤 {args.player} 업데이트 중...\n")
        success = scheduler.manual_update_player(args.player, args.team, args.league)
        
        if success:
            print("\n✅ 선수 업데이트 완료!")
        else:
            print("\n❌ 선수 업데이트 실패!")
        return
    
    # 팀 전체 업데이트
    if args.team:
        if not args.league:
            print("❌ 오류: --league를 지정해야 합니다.")
            return
        
        print(f"🏀 {args.team} 전체 선수 업데이트 중...\n")
        updated, failed = scheduler.manual_update_team(args.team, args.league)
        
        print(f"\n✅ 팀 업데이트 완료!")
        print(f"   - 성공: {updated}명")
        print(f"   - 실패: {failed}명")
        return
    
    # 인자가 없으면 도움말 출력
    parser.print_help()


if __name__ == '__main__':
    main()

"""
데이터 자동 업데이트 스케줄러
- 선수 통계 자동 업데이트
- 부상 리포트 자동 수집
- 경기 일정 자동 업데이트
"""

import schedule
import time
from threading import Thread
from datetime import datetime, timedelta
from typing import List, Dict
from modules.realtime_data_fetcher import get_realtime_fetcher
from modules.player_stats_database import get_player_database


class DataUpdateScheduler:
    """데이터 자동 업데이트 스케줄러"""
    
    def __init__(self):
        self.fetcher = get_realtime_fetcher()
        self.db = get_player_database()
        self.running = False
        self.thread = None
        
        # 업데이트 대상 리그
        self.leagues = ['NBA', 'KBL']
        
        # 업데이트 대상 팀 (예시)
        self.nba_teams = [
            'Boston Celtics', 'Detroit Pistons', 'Los Angeles Lakers',
            'Cleveland Cavaliers', 'New York Knicks', 'Milwaukee Bucks',
            'Oklahoma City Thunder', 'Denver Nuggets'
        ]
        
        self.kbl_teams = [
            'KT 소닉붐', 'KCC 이지스', 'LG 세이커스', '삼성 썬더스'
        ]
        
        print("[OK] 데이터 업데이트 스케줄러 초기화")
    
    def start(self):
        """스케줄러 시작"""
        
        if self.running:
            print("[WARNING] 스케줄러가 이미 실행 중입니다.")
            return
        
        self.running = True
        
        # 스케줄 설정
        self._setup_schedules()
        
        # 백그라운드 스레드 시작
        self.thread = Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        print("🚀 데이터 업데이트 스케줄러 시작!")
        print("   - 선수 통계: 매일 오전 6시")
        print("   - 부상 리포트: 매 시간")
        print("   - 경기 일정: 매일 오전 7시")
    
    def _setup_schedules(self):
        """스케줄 설정"""
        
        # 선수 통계: 매일 오전 6시
        schedule.every().day.at("06:00").do(self.update_all_player_stats)
        
        # 부상 리포트: 매 시간
        schedule.every().hour.do(self.update_injury_reports)
        
        # 경기 일정: 매일 오전 7시
        schedule.every().day.at("07:00").do(self.update_game_schedules)
        
        # 경기 당일 선수 통계: 매 30분
        schedule.every(30).minutes.do(self.update_game_day_players)
        
        # 오래된 데이터 정리: 매주 일요일 오전 3시
        schedule.every().sunday.at("03:00").do(self.cleanup_old_data)
    
    def _run_scheduler(self):
        """스케줄러 실행 루프"""
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                print(f"[ERROR] 스케줄러 실행 오류: {e}")
                time.sleep(60)
    
    def stop(self):
        """스케줄러 중지"""
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        print("🛑 데이터 업데이트 스케줄러 중지")
    
    # ==================== 업데이트 작업 ====================
    
    def update_all_player_stats(self):
        """모든 선수 통계 업데이트"""
        
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 선수 통계 업데이트 시작")
        print(f"{'='*60}")
        
        total_updated = 0
        total_failed = 0
        
        # NBA 선수 업데이트
        for team in self.nba_teams:
            updated, failed = self._update_team_players(team, 'NBA')
            total_updated += updated
            total_failed += failed
        
        # KBL 선수 업데이트
        for team in self.kbl_teams:
            updated, failed = self._update_team_players(team, 'KBL')
            total_updated += updated
            total_failed += failed
        
        print(f"\n{'='*60}")
        print(f"선수 통계 업데이트 완료!")
        print(f"  - 성공: {total_updated}명")
        print(f"  - 실패: {total_failed}명")
        print(f"{'='*60}\n")
    
    def _update_team_players(self, team_name: str, league: str) -> tuple:
        """팀 선수 통계 업데이트"""
        
        print(f"\n[{team_name}] 선수 통계 업데이트 중...")
        
        updated = 0
        failed = 0
        
        # 데이터베이스에서 팀 선수 목록 가져오기
        players = self.db.get_team_players(team_name, league)
        
        if not players:
            print(f"  [WARNING] {team_name} 선수 데이터 없음 (데이터베이스)")
            return 0, 0
        
        for player in players:
            player_name = player['player_name']
            player_id = player['player_id']
            
            try:
                # 실시간 데이터 수집
                if league == 'NBA':
                    stats = self.fetcher.fetch_nba_player_stats(player_name, team_name)
                elif league == 'KBL':
                    stats = self.fetcher.fetch_kbl_player_stats(player_name, team_name)
                else:
                    continue
                
                if stats:
                    # 기존 데이터와 병합
                    stats['player_id'] = player_id
                    stats['name'] = player_name
                    stats['team'] = team_name
                    stats['league'] = league
                    stats['data_source'] = 'realtime'
                    
                    # 데이터베이스 업데이트
                    if self.db.upsert_player_stats(player_id, stats):
                        updated += 1
                        print(f"  [OK] {player_name}: {stats.get('ppg', 0):.1f} PPG")
                    else:
                        failed += 1
                else:
                    print(f"  [WARNING] {player_name}: 데이터 수집 실패")
                    failed += 1
                
                # API 요청 제한 방지
                time.sleep(1)
            
            except Exception as e:
                print(f"  [ERROR] {player_name}: {e}")
                failed += 1
        
        return updated, failed
    
    def update_injury_reports(self):
        """부상 리포트 업데이트"""
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 부상 리포트 업데이트 중...")
        
        total_injuries = 0
        
        # NBA 부상 리포트
        try:
            nba_injuries = self.fetcher.fetch_nba_injury_report()
            
            # 기존 부상 정보 초기화
            self.db.clear_injuries()
            
            for injury in nba_injuries:
                injury['league'] = 'NBA'
                injury['player_id'] = self._generate_player_id(
                    injury.get('name', ''), 
                    injury.get('team', '')
                )
                
                if self.db.upsert_injury(injury):
                    total_injuries += 1
            
            print(f"  [OK] NBA 부상 리포트: {len(nba_injuries)}명")
        
        except Exception as e:
            print(f"  [ERROR] NBA 부상 리포트 실패: {e}")
        
        # KBL 부상 리포트
        try:
            kbl_injuries = self.fetcher.fetch_kbl_injury_report()
            
            for injury in kbl_injuries:
                injury['league'] = 'KBL'
                injury['player_id'] = self._generate_player_id(
                    injury.get('name', ''),
                    injury.get('team', '')
                )
                
                if self.db.upsert_injury(injury):
                    total_injuries += 1
            
            print(f"  [OK] KBL 부상 리포트: {len(kbl_injuries)}명")
        
        except Exception as e:
            print(f"  [ERROR] KBL 부상 리포트 실패: {e}")
        
        print(f"  총 부상자: {total_injuries}명\n")
    
    def update_game_schedules(self):
        """경기 일정 업데이트"""
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 경기 일정 업데이트 중...")
        
        total_games = 0
        
        # NBA 경기 일정
        for team in self.nba_teams:
            try:
                schedule = self.fetcher.fetch_nba_team_schedule(team)
                
                for game in schedule:
                    game['team'] = team
                    game['league'] = 'NBA'
                    
                    if self.db.upsert_game(game):
                        total_games += 1
                
                print(f"  [OK] {team}: {len(schedule)}경기")
                time.sleep(2)  # API 요청 제한
            
            except Exception as e:
                print(f"  [ERROR] {team}: {e}")
        
        print(f"  총 경기: {total_games}경기\n")
    
    def update_game_day_players(self):
        """경기 당일 선수 통계 업데이트"""
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 오늘 경기가 있는 팀 찾기
        teams_playing_today = []
        
        for team in self.nba_teams:
            schedule = self.db.get_team_schedule(team, 'NBA')
            for game in schedule:
                if game['game_date'] == today:
                    teams_playing_today.append(team)
                    break
        
        if teams_playing_today:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 경기 당일 선수 업데이트")
            print(f"  오늘 경기: {', '.join(teams_playing_today)}")
            
            for team in teams_playing_today:
                self._update_team_players(team, 'NBA')
    
    def cleanup_old_data(self):
        """오래된 데이터 정리"""
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 오래된 데이터 정리 중...")
        
        # 30일 이상 된 로그 삭제
        cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
        
        try:
            self.db.conn.execute(
                'DELETE FROM update_log WHERE timestamp < ?',
                (cutoff_date,)
            )
            self.db.conn.commit()
            
            print("  [OK] 오래된 로그 삭제 완료")
        
        except Exception as e:
            print(f"  [ERROR] 데이터 정리 실패: {e}")
    
    # ==================== 수동 업데이트 ====================
    
    def manual_update_player(self, player_name: str, team_name: str, league: str):
        """선수 통계 수동 업데이트"""
        
        print(f"\n[수동 업데이트] {player_name} ({team_name})")
        
        try:
            if league == 'NBA':
                stats = self.fetcher.fetch_nba_player_stats(player_name, team_name)
            elif league == 'KBL':
                stats = self.fetcher.fetch_kbl_player_stats(player_name, team_name)
            else:
                print(f"  [ERROR] 지원하지 않는 리그: {league}")
                return False
            
            if stats:
                player_id = self._generate_player_id(player_name, team_name)
                stats['player_id'] = player_id
                stats['name'] = player_name
                stats['team'] = team_name
                stats['league'] = league
                stats['data_source'] = 'manual'
                
                if self.db.upsert_player_stats(player_id, stats):
                    print(f"  [OK] 업데이트 완료: {stats.get('ppg', 0):.1f} PPG")
                    return True
            
            print(f"  [ERROR] 데이터 수집 실패")
            return False
        
        except Exception as e:
            print(f"  [ERROR] 오류: {e}")
            return False
    
    def manual_update_team(self, team_name: str, league: str):
        """팀 전체 선수 수동 업데이트"""
        
        print(f"\n[수동 업데이트] {team_name} 전체 선수")
        
        updated, failed = self._update_team_players(team_name, league)
        
        print(f"\n  완료: {updated}명 성공, {failed}명 실패")
        return updated, failed
    
    # ==================== 유틸리티 ====================
    
    def _generate_player_id(self, player_name: str, team_name: str) -> str:
        """선수 ID 생성"""
        
        # 이름을 소문자로 변환하고 공백 제거
        name_clean = player_name.lower().replace(' ', '_')
        team_clean = team_name.lower().replace(' ', '_')
        
        return f"{name_clean}_{team_clean}"
    
    def get_status(self) -> Dict:
        """스케줄러 상태 조회"""
        
        db_stats = self.db.get_stats_summary()
        
        return {
            'running': self.running,
            'database': db_stats,
            'next_runs': {
                'player_stats': schedule.next_run(),
                'injury_report': schedule.next_run(),
                'game_schedule': schedule.next_run()
            }
        }


# 싱글톤 인스턴스
_scheduler = None

def get_data_scheduler() -> DataUpdateScheduler:
    """DataUpdateScheduler 싱글톤 반환"""
    global _scheduler
    if _scheduler is None:
        _scheduler = DataUpdateScheduler()
    return _scheduler

"""
선수 통계 데이터베이스
- SQLite 기반 선수 통계 저장
- 자동 업데이트 이력 관리
- 캐시 시스템
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json


class PlayerStatsDatabase:
    """선수 통계 데이터베이스 관리"""
    
    def __init__(self, db_path: str = "data/player_stats.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
        
        self.create_tables()
        print(f"[OK] 선수 통계 데이터베이스 초기화: {self.db_path}")
    
    def create_tables(self):
        """테이블 생성"""
        
        # 선수 통계 테이블
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                player_id TEXT PRIMARY KEY,
                player_name TEXT NOT NULL,
                team_name TEXT NOT NULL,
                league TEXT NOT NULL,
                position TEXT,
                age INTEGER,
                
                -- 기본 통계
                ppg REAL,
                rpg REAL,
                apg REAL,
                spg REAL,
                bpg REAL,
                topg REAL,
                mpg REAL,
                
                -- 슈팅 효율
                fg_pct REAL,
                three_pct REAL,
                ft_pct REAL,
                fgm REAL,
                fga REAL,
                ftm REAL,
                fta REAL,
                
                -- 고급 메트릭스 (농구)
                per REAL,
                ws REAL,
                obpm REAL,
                dbpm REAL,
                bpm REAL,
                pie REAL,
                rapm REAL,
                
                -- 고급 메트릭스 (축구)
                xg REAL,
                xa REAL,
                xgchain REAL,
                tackles INTEGER,
                interceptions INTEGER,
                defensive_contribution REAL,
                ppda REAL,
                
                -- 고급 메트릭스 (야구 - 타자)
                ops REAL,
                woba REAL,
                war_batter REAL,
                ab INTEGER,
                h INTEGER,
                bb INTEGER,
                hr INTEGER,
                
                -- 고급 메트릭스 (야구 - 투수)
                era REAL,
                era_plus REAL,
                fip REAL,
                war_pitcher REAL,
                ip REAL,
                k INTEGER,
                
                -- 고급 메트릭스 (배구)
                spike_success_rate REAL,
                block_efficiency REAL,
                dig_efficiency REAL,
                set_efficiency REAL,
                jump_workload REAL,
                movement_workload REAL,
                kills INTEGER,
                blocks INTEGER,
                digs INTEGER,
                assists_vb INTEGER,
                
                -- 최근 폼
                recent_ppg REAL,
                recent_rpg REAL,
                recent_apg REAL,
                form_factor REAL DEFAULT 1.0,
                
                -- 메타데이터
                last_updated TIMESTAMP,
                data_source TEXT,
                season TEXT DEFAULT '2025-26'
            )
        ''')
        
        # 부상 리포트 테이블
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS injury_report (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                team_name TEXT NOT NULL,
                league TEXT NOT NULL,
                injury_type TEXT,
                status TEXT,
                expected_return DATE,
                last_updated TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES player_stats(player_id)
            )
        ''')
        
        # 경기 일정 테이블
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                league TEXT NOT NULL,
                game_date DATE NOT NULL,
                opponent TEXT,
                home_away TEXT,
                result TEXT,
                pts INTEGER,
                opp_pts INTEGER,
                last_updated TIMESTAMP
            )
        ''')
        
        # 업데이트 로그 테이블
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS update_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                update_type TEXT NOT NULL,
                league TEXT,
                team_name TEXT,
                player_name TEXT,
                status TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    # ==================== 선수 통계 ====================
    
    def upsert_player_stats(self, player_id: str, stats: Dict):
        """선수 통계 삽입 또는 업데이트"""
        
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO player_stats (
                    player_id, player_name, team_name, league, position, age,
                    ppg, rpg, apg, spg, bpg, topg, mpg,
                    fg_pct, three_pct, ft_pct, fgm, fga, ftm, fta,
                    per, ws, obpm, dbpm, bpm, pie, rapm,
                    recent_ppg, recent_rpg, recent_apg, form_factor,
                    last_updated, data_source, season
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player_id,
                stats.get('name', ''),
                stats.get('team', ''),
                stats.get('league', ''),
                stats.get('position', ''),
                stats.get('age', 0),
                stats.get('ppg', 0),
                stats.get('rpg', 0),
                stats.get('apg', 0),
                stats.get('spg', 0),
                stats.get('bpg', 0),
                stats.get('topg', 0),
                stats.get('mpg', 0),
                stats.get('fg_pct', 0),
                stats.get('three_pct', 0),
                stats.get('ft_pct', 0),
                stats.get('fgm', 0),
                stats.get('fga', 0),
                stats.get('ftm', 0),
                stats.get('fta', 0),
                stats.get('per', 0),
                stats.get('ws', 0),
                stats.get('obpm', 0),
                stats.get('dbpm', 0),
                stats.get('bpm', 0),
                stats.get('pie', 0),
                stats.get('rapm', 0),
                stats.get('recent_ppg', stats.get('ppg', 0)),
                stats.get('recent_rpg', stats.get('rpg', 0)),
                stats.get('recent_apg', stats.get('apg', 0)),
                stats.get('form_factor', 1.0),
                datetime.now().isoformat(),
                stats.get('data_source', 'manual'),
                stats.get('season', '2025-26')
            ))
            
            self.conn.commit()
            
            # 로그 기록
            self.log_update('player_stats', stats.get('league'), stats.get('team'), 
                          stats.get('name'), 'success', f"Updated {stats.get('name')}")
            
            return True
        
        except Exception as e:
            print(f"[ERROR] 선수 통계 저장 실패: {e}")
            self.log_update('player_stats', stats.get('league'), stats.get('team'),
                          stats.get('name'), 'error', str(e))
            return False
    
    def get_player_stats(self, player_id: str) -> Optional[Dict]:
        """선수 통계 조회"""
        
        cursor = self.conn.execute(
            'SELECT * FROM player_stats WHERE player_id = ?',
            (player_id,)
        )
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_team_players(self, team_name: str, league: str) -> List[Dict]:
        """팀 선수 목록 조회"""
        
        cursor = self.conn.execute(
            'SELECT * FROM player_stats WHERE team_name = ? AND league = ? ORDER BY ppg DESC',
            (team_name, league)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def is_data_stale(self, player_id: str, max_age_hours: int = 24) -> bool:
        """데이터가 오래되었는지 확인"""
        
        stats = self.get_player_stats(player_id)
        if not stats:
            return True
        
        last_updated = datetime.fromisoformat(stats['last_updated'])
        age = datetime.now() - last_updated
        
        return age > timedelta(hours=max_age_hours)
    
    def get_stale_players(self, max_age_hours: int = 24) -> List[Dict]:
        """업데이트가 필요한 선수 목록"""
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        cursor = self.conn.execute(
            'SELECT * FROM player_stats WHERE last_updated < ?',
            (cutoff_time.isoformat(),)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 부상 리포트 ====================
    
    def upsert_injury(self, injury: Dict):
        """부상 정보 삽입 또는 업데이트"""
        
        try:
            # 기존 부상 정보 삭제 (최신 정보로 교체)
            self.conn.execute(
                'DELETE FROM injury_report WHERE player_id = ?',
                (injury.get('player_id', ''),)
            )
            
            # 새 부상 정보 삽입
            self.conn.execute('''
                INSERT INTO injury_report (
                    player_id, player_name, team_name, league,
                    injury_type, status, expected_return, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                injury.get('player_id', ''),
                injury.get('name', ''),
                injury.get('team', ''),
                injury.get('league', ''),
                injury.get('injury_type', ''),
                injury.get('status', ''),
                injury.get('expected_return', None),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            return True
        
        except Exception as e:
            print(f"[ERROR] 부상 정보 저장 실패: {e}")
            return False
    
    def get_team_injuries(self, team_name: str, league: str) -> List[Dict]:
        """팀 부상자 목록 조회"""
        
        cursor = self.conn.execute(
            'SELECT * FROM injury_report WHERE team_name = ? AND league = ?',
            (team_name, league)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_injuries(self, league: str = None) -> List[Dict]:
        """전체 부상자 목록 조회"""
        
        if league:
            cursor = self.conn.execute(
                'SELECT * FROM injury_report WHERE league = ?',
                (league,)
            )
        else:
            cursor = self.conn.execute('SELECT * FROM injury_report')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def clear_injuries(self, team_name: str = None):
        """부상 정보 초기화"""
        
        if team_name:
            self.conn.execute(
                'DELETE FROM injury_report WHERE team_name = ?',
                (team_name,)
            )
        else:
            self.conn.execute('DELETE FROM injury_report')
        
        self.conn.commit()
    
    # ==================== 경기 일정 ====================
    
    def upsert_game(self, game: Dict):
        """경기 일정 삽입 또는 업데이트"""
        
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO game_schedule (
                    team_name, league, game_date, opponent, home_away,
                    result, pts, opp_pts, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game.get('team', ''),
                game.get('league', ''),
                game.get('date', ''),
                game.get('opponent', ''),
                game.get('home_away', ''),
                game.get('result', ''),
                game.get('pts', 0),
                game.get('opp_pts', 0),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            return True
        
        except Exception as e:
            print(f"[ERROR] 경기 일정 저장 실패: {e}")
            return False
    
    def get_team_schedule(self, team_name: str, league: str) -> List[Dict]:
        """팀 경기 일정 조회"""
        
        cursor = self.conn.execute(
            'SELECT * FROM game_schedule WHERE team_name = ? AND league = ? ORDER BY game_date DESC',
            (team_name, league)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def detect_back_to_back(self, team_name: str, league: str, game_date: str) -> bool:
        """백투백 경기 감지"""
        
        try:
            game_dt = datetime.strptime(game_date, '%Y-%m-%d')
            prev_day = (game_dt - timedelta(days=1)).strftime('%Y-%m-%d')
            
            cursor = self.conn.execute(
                'SELECT COUNT(*) FROM game_schedule WHERE team_name = ? AND league = ? AND game_date = ?',
                (team_name, league, prev_day)
            )
            
            count = cursor.fetchone()[0]
            return count > 0
        
        except Exception as e:
            print(f"[ERROR] 백투백 감지 실패: {e}")
            return False
    
    # ==================== 로그 ====================
    
    def log_update(self, update_type: str, league: str, team_name: str,
                   player_name: str, status: str, message: str):
        """업데이트 로그 기록"""
        
        try:
            self.conn.execute('''
                INSERT INTO update_log (
                    update_type, league, team_name, player_name, status, message
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (update_type, league, team_name, player_name, status, message))
            
            self.conn.commit()
        
        except Exception as e:
            print(f"[ERROR] 로그 기록 실패: {e}")
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """최근 로그 조회"""
        
        cursor = self.conn.execute(
            'SELECT * FROM update_log ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 유틸리티 ====================
    
    def get_stats_summary(self) -> Dict:
        """데이터베이스 통계 요약"""
        
        cursor = self.conn.execute('SELECT COUNT(*) FROM player_stats')
        total_players = cursor.fetchone()[0]
        
        cursor = self.conn.execute('SELECT COUNT(*) FROM injury_report')
        total_injuries = cursor.fetchone()[0]
        
        cursor = self.conn.execute('SELECT COUNT(*) FROM game_schedule')
        total_games = cursor.fetchone()[0]
        
        cursor = self.conn.execute(
            'SELECT COUNT(*) FROM player_stats WHERE last_updated > ?',
            ((datetime.now() - timedelta(hours=24)).isoformat(),)
        )
        recent_updates = cursor.fetchone()[0]
        
        return {
            'total_players': total_players,
            'total_injuries': total_injuries,
            'total_games': total_games,
            'recent_updates_24h': recent_updates,
            'database_path': str(self.db_path)
        }
    
    def close(self):
        """데이터베이스 연결 종료"""
        self.conn.close()


# 싱글톤 인스턴스
_database = None

def get_player_database() -> PlayerStatsDatabase:
    """PlayerStatsDatabase 싱글톤 반환"""
    global _database
    if _database is None:
        _database = PlayerStatsDatabase()
    return _database

"""
실시간 데이터 수집 모듈
NBA Stats API, ESPN, Basketball-Reference 등에서 실시간 데이터 수집
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
from pathlib import Path


class LiveDataFetcher:
    """실시간 스포츠 데이터 수집"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 300  # 5분 캐시 (더 자주 업데이트)
        
        # NBA Stats API 헤더
        self.nba_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.nba.com/',
            'Accept': 'application/json'
        }
        
        # ESPN 헤더
        self.espn_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 확인"""
        if cache_key not in self.cache_timestamps:
            return False
        
        elapsed = time.time() - self.cache_timestamps[cache_key]
        return elapsed < self.cache_duration
    
    def _update_cache(self, cache_key: str, data: dict):
        """캐시 업데이트"""
        self.cache[cache_key] = data
        self.cache_timestamps[cache_key] = time.time()
    
    def fetch_nba_standings(self, conference: str = "East") -> dict:
        """
        NBA 순위표 가져오기
        
        Args:
            conference: "East" 또는 "West"
        
        Returns:
            팀별 데이터 딕셔너리
        """
        cache_key = f"nba_standings_{conference}"
        
        # 캐시 확인
        if self._is_cache_valid(cache_key):
            print(f"[OK] NBA {conference} 캐시 사용")
            return self.cache[cache_key]
        
        print(f"[FETCH] NBA {conference} 실시간 데이터 수집 중...")
        
        # 1차 시도: NBA Stats API
        try:
            data = self._fetch_from_nba_api(conference)
            if data:
                self._update_cache(cache_key, data)
                print(f"[OK] NBA Stats API 성공 ({len(data)}개 팀)")
                return data
        except Exception as e:
            print(f"[WARNING] NBA Stats API 실패: {e}")
        
        # 2차 시도: ESPN 크롤링
        try:
            data = self._fetch_from_espn(conference)
            if data:
                self._update_cache(cache_key, data)
                print(f"[OK] ESPN 크롤링 성공 ({len(data)}개 팀)")
                return data
        except Exception as e:
            print(f"[WARNING] ESPN 크롤링 실패: {e}")
        
        # 3차 시도: 로컬 데이터 (폴백)
        print(f"[WARNING] 실시간 데이터 수집 실패, 로컬 데이터 사용")
        return self._load_local_data(conference)

    def fetch_kleague_standings(self) -> dict:
        """
        K-League 1 실시간 순위표 가져오기
        
        소스: kleague.com 공식 API
        """
        cache_key = "kleague1_standings"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        print("[FETCH] K-League 1 실시간 순위 데이터 수집 중...")
        
        try:
            url = "https://www.kleague.com/record/teamRank.do"
            # Browser Audit 결과: POST 방식이며 쿼리스트링으로 파라미터 전달
            params = {
                'leagueId': '1',
                'year': '2026',
                'stadium': 'all',
                'recordType': 'rank'
            }
            
            response = requests.post(url, params=params, headers=self.espn_headers, timeout=10)
            response.raise_for_status()
            
            # JSON 데이터 파싱
            data = response.json()
            teams_data = {}
            
            # kleague.com API 응답 구조: data.teamRank
            rank_list = data.get('data', {}).get('teamRank', [])

            for item in rank_list:
                # API 필드명 매핑 (공식 JSON 데이터 기준)
                team_name_raw = item.get('teamName', '').strip()
                clean_name = self._map_kleague_team_name(team_name_raw)
                
                wins = int(item.get('winCnt', 0))
                draws = int(item.get('tieCnt', 0))
                losses = int(item.get('lossCnt', 0))
                goals_for = int(item.get('gainGoal', 0))
                goals_against = int(item.get('lossGoal', 0))
                played = int(item.get('gameCount', 0))
                
                # 실시간 폼 (game01~game05) - "승", "무", "패" 를 "W", "D", "L"로 변환
                form_map = {"승": "W", "무": "D", "패": "L"}
                raw_form = [item.get(f'game{i:02d}', '').strip() for i in range(1, 6)]
                form = [form_map[f] for f in raw_form if f in form_map]
                
                teams_data[clean_name] = {
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'played': played,
                    'goals_for': goals_for,
                    'goals_against': goals_against,
                    'points': int(item.get('gainPoint', 0)),
                    'position': int(item.get('rank', 0)),
                    'diff': int(item.get('gapCnt', 0)),
                    'win_pct': wins / played if played > 0 else 0,
                    'form': form,
                    'last_updated': datetime.now().isoformat()
                }
            
            if teams_data:
                self._update_cache(cache_key, teams_data)
                print(f"[OK] K-League 1 공식 API 성공 ({len(teams_data)}개 팀 연동)")
                return teams_data
                
        except Exception as e:
            print(f"[ERROR] K-League 1 API 수집 실패: {e}")
            
        return {}

    def _map_kleague_team_name(self, raw_name: str) -> str:
        """K-League 공식 팀명을 내부 시스템 이름으로 매핑 (2026 시즌 기준)"""
        mapping = {
            '울산': '울산', '전북': '전북', '포항': '포항', '수원FC': '수원FC', 
            '인천': '인천', '제주': '제주', '강원': '강원', '서울': '서울', 
            '광주': '광주', '대전': '대전', '김천': '김천', '부천': '부천', '안양': '안양'
        }
        for k, v in mapping.items():
            if k in raw_name:
                return v
        return raw_name

    def _fetch_from_nba_api(self, conference: str) -> dict:
        """NBA Standings API에서 데이터 가져오기 (L10, Streak 포함)"""
        try:
            url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
            response = requests.get(url, headers=self.espn_headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            teams_data = {}
            
            # ESPN Standings JSON 구조 파싱
            if 'children' in data:
                for group in data['children']:
                    # group['name']은 'Eastern Conference' 등
                    if conference not in group.get('name', ''):
                        continue
                        
                    if 'standings' in group and 'entries' in group['standings']:
                        for entry in group['standings']['entries']:
                            team_info = entry.get('team', {})
                            team_name = team_info.get('displayName')
                            
                            stats_list = entry.get('stats', [])
                            s_data = {}
                            for s in stats_list:
                                s_type = s.get('type')
                                s_name = s.get('name')
                                if s_type: s_data[s_type] = s
                                if s_name: s_data[s_name] = s
                            
                            # 데이터 추출
                            wins = int(s_data.get('wins', {}).get('value', 0))
                            losses = int(s_data.get('losses', {}).get('value', 0))
                            win_pct = s_data.get('winpercent', {}).get('value', 0.0)
                            ppg = s_data.get('avgpointsfor', {}).get('value', 0.0)
                            opp_ppg = s_data.get('avgpointsagainst', {}).get('value', 0.0)
                            diff = s_data.get('differential', {}).get('value', 0.0)
                            
                            home_record = s_data.get('home', {}).get('summary', '0-0')
                            away_record = s_data.get('road', {}).get('summary', '0-0')
                            last_10 = s_data.get('lasttengames', {}).get('summary', '')
                            streak = s_data.get('streak', {}).get('displayValue', '')
                            rank = int(s_data.get('playoffseed', {}).get('value', 0))
                            
                            teams_data[team_name] = {
                                'wins': wins,
                                'losses': losses,
                                'win_pct': win_pct,
                                'home': home_record,
                                'away': away_record,
                                'ppg': round(ppg, 1),
                                'opp_ppg': round(opp_ppg, 1),
                                'diff': round(diff, 1),
                                'last_10': last_10,
                                'streak': streak,
                                'rank': rank,
                                'form': self._parse_form_from_last_10(last_10) if last_10 else ['W'] * 5 + ['L'] * 5,
                                'last_updated': datetime.now().isoformat()
                            }
            
            if teams_data:
                print(f"[OK] ESPN Standings API 성공 ({len(teams_data)}개 팀)")
                return teams_data
        except Exception as e:
            print(f"[ERROR] ESPN API 실패: {e}")
            import traceback
            traceback.print_exc()
        
        return {}
    
    def _fetch_from_espn(self, conference: str) -> dict:
        """ESPN에서 NBA 순위표 크롤링"""
        url = "https://www.espn.com/nba/standings"
        
        response = requests.get(url, headers=self.espn_headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ESPN HTML 구조 파싱
        teams_data = {}
        
        # 순위표 테이블 찾기
        tables = soup.find_all('table', class_='Table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # 헤더 제외
                cols = row.find_all('td')
                
                if len(cols) < 4:
                    continue
                
                try:
                    team_name = cols[0].text.strip()
                    wins = int(float(cols[1].text.strip()))
                    losses = int(float(cols[2].text.strip()))
                    win_pct_str = cols[3].text.strip()
                    
                    # win_pct 파싱 (.732 또는 0.732 형태)
                    if win_pct_str.startswith('.'):
                        win_pct = float('0' + win_pct_str)
                    else:
                        win_pct = float(win_pct_str)
                    
                    teams_data[team_name] = {
                        'wins': wins,
                        'losses': losses,
                        'win_pct': win_pct,
                        'ppg': 0,  # ESPN 순위표에는 없음
                        'opp_ppg': 0,
                        'diff': 0,
                        'form': ['W'] * min(wins, 5) + ['L'] * max(0, 5 - wins),
                        'last_updated': datetime.now().isoformat()
                    }
                except (ValueError, IndexError) as e:
                    continue
        
        return teams_data
    
    def _load_local_data(self, conference: str) -> dict:
        """로컬 데이터 로드 (폴백)"""
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent / "data"))
            from real_data_2026 import NBA_2026_EAST, NBA_2026_WEST
            
            if conference == "East":
                return NBA_2026_EAST
            else:
                return NBA_2026_WEST
        except Exception as e:
            print(f"[ERROR] 로컬 데이터 로드 실패: {e}")
            return {}
    
    def fetch_team_stats(self, league: str, team_name: str) -> dict:
        """
        특정 팀의 상세 통계 가져오기
        
        Args:
            league: 리그 이름 (예: "NBA East", "MLB", "KBO")
            team_name: 팀 이름
        
        Returns:
            팀 통계 딕셔너리
        """
        cache_key = f"{league}_{team_name}"
        
        # 캐시 확인
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # 리그별 데이터 수집
        if "NBA" in league:
            conference = "East" if "East" in league else "West"
            standings = self.fetch_nba_standings(conference)
            
            if team_name in standings:
                self._update_cache(cache_key, standings[team_name])
                return standings[team_name]
        
        elif league == "MLB":
            # MLB 데이터 수집 (구현 필요)
            pass
        
        elif league == "KBO":
            # KBO 데이터 수집 (구현 필요)
            pass
        
        elif league == "K리그1":
            standings = self.fetch_kleague_standings()
            if team_name in standings:
                self._update_cache(cache_key, standings[team_name])
                return standings[team_name]
        
        # 폴백: 로컬 데이터
        return self._load_local_team_data(league, team_name)
    
    def _load_local_team_data(self, league: str, team_name: str) -> dict:
        """로컬 데이터에서 팀 통계 로드"""
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent / "data"))
            from real_data_2026 import get_team_stats
            
            return get_team_stats(league, team_name)
        except Exception as e:
            print(f"[ERROR] 로컬 팀 데이터 로드 실패: {e}")
            return {}
    
    def get_data_freshness(self, league: str) -> dict:
        """
        데이터 신선도 확인
        
        Returns:
            {
                'status': 'ok' | 'info' | 'warning' | 'error',
                'message': str,
                'last_updated': datetime,
                'days_old': int
            }
        """
        cache_key = f"{league}_standings"
        
        if cache_key not in self.cache_timestamps:
            return {
                'status': 'error',
                'message': '데이터가 없습니다.',
                'last_updated': None,
                'days_old': None
            }
        
        last_updated = datetime.fromtimestamp(self.cache_timestamps[cache_key])
        now = datetime.now()
        days_old = (now - last_updated).days
        hours_old = (now - last_updated).seconds // 3600
        
        if days_old > 3:
            status = 'warning'
            message = f'데이터가 {days_old}일 전 기준입니다. 업데이트가 필요합니다.'
        elif days_old > 1:
            status = 'info'
            message = f'데이터가 {days_old}일 전 기준입니다.'
        elif hours_old > 6:
            status = 'info'
            message = f'데이터가 {hours_old}시간 전 기준입니다.'
        else:
            status = 'ok'
            message = '최신 데이터입니다.'
        
        return {
            'status': status,
            'message': message,
            'last_updated': last_updated,
            'days_old': days_old
        }
    
    def clear_cache(self):
        """캐시 초기화"""
        self.cache = {}
        self.cache_timestamps = {}
        print("[REFRESH] 실시간 데이터 캐시 초기화 완료")


    def _parse_form_from_last_10(self, last_10_str: str) -> list:
        """'8-2' 형태의 문자열을 ['W', 'W', ...] 리스트로 변환 (정확한 순서는 알 수 없으므로 개수만 맞춰줌)"""
        try:
            if '-' in last_10_str:
                w, l = map(int, last_10_str.split('-'))
                return ['W'] * w + ['L'] * l
        except:
            pass
        return ['W'] * 5 + ['L'] * 5

# 전역 인스턴스
_live_fetcher = None

def get_live_fetcher():
    """LiveDataFetcher 싱글톤 인스턴스 반환"""
    global _live_fetcher
    if _live_fetcher is None:
        _live_fetcher = LiveDataFetcher()
    return _live_fetcher

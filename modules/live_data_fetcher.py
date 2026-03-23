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
        self.cache_duration = 3600  # 1시간 캐시
        
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
            print(f"✅ NBA {conference} 캐시 사용")
            return self.cache[cache_key]
        
        print(f"📡 NBA {conference} 실시간 데이터 수집 중...")
        
        # 1차 시도: NBA Stats API
        try:
            data = self._fetch_from_nba_api(conference)
            if data:
                self._update_cache(cache_key, data)
                print(f"✅ NBA Stats API 성공 ({len(data)}개 팀)")
                return data
        except Exception as e:
            print(f"⚠️ NBA Stats API 실패: {e}")
        
        # 2차 시도: ESPN 크롤링
        try:
            data = self._fetch_from_espn(conference)
            if data:
                self._update_cache(cache_key, data)
                print(f"✅ ESPN 크롤링 성공 ({len(data)}개 팀)")
                return data
        except Exception as e:
            print(f"⚠️ ESPN 크롤링 실패: {e}")
        
        # 3차 시도: 로컬 데이터 (폴백)
        print(f"⚠️ 실시간 데이터 수집 실패, 로컬 데이터 사용")
        return self._load_local_data(conference)
    
    def _fetch_from_nba_api(self, conference: str) -> dict:
        """NBA Stats API에서 데이터 가져오기"""
        url = "https://stats.nba.com/stats/leaguestandingsv3"
        params = {
            'LeagueID': '00',
            'Season': '2025-26',
            'SeasonType': 'Regular Season'
        }
        
        response = requests.get(url, headers=self.nba_headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        standings = data['resultSets'][0]['rowSet']
        
        teams_data = {}
        
        for team in standings:
            team_name = team[4]  # TeamName
            team_conf = team[5]  # Conference
            
            # 컨퍼런스 필터링
            if conference == "East" and team_conf != "East":
                continue
            if conference == "West" and team_conf != "West":
                continue
            
            teams_data[team_name] = {
                'wins': team[13],
                'losses': team[14],
                'win_pct': team[15],
                'home': team[16],
                'away': team[17],
                'conf': team[18],
                'ppg': team[26] if len(team) > 26 else 0,
                'opp_ppg': team[27] if len(team) > 27 else 0,
                'diff': team[28] if len(team) > 28 else 0,
                'form': ['W', 'W', 'W', 'W', 'W'],  # API에서 제공 안 함
                'last_updated': datetime.now().isoformat()
            }
        
        return teams_data
    
    def _fetch_from_espn(self, conference: str) -> dict:
        """ESPN에서 NBA 순위표 크롤링"""
        url = "https://www.espn.com/nba/standings"
        
        response = requests.get(url, headers=self.espn_headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ESPN HTML 구조 파싱 (실제 구조에 맞게 수정 필요)
        teams_data = {}
        
        # 순위표 테이블 찾기
        tables = soup.find_all('table', class_='Table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # 헤더 제외
                cols = row.find_all('td')
                
                if len(cols) < 10:
                    continue
                
                team_name = cols[0].text.strip()
                wins = int(cols[1].text.strip())
                losses = int(cols[2].text.strip())
                win_pct = float(cols[3].text.strip())
                
                teams_data[team_name] = {
                    'wins': wins,
                    'losses': losses,
                    'win_pct': win_pct,
                    'ppg': 0,  # ESPN에서 추가 파싱 필요
                    'opp_ppg': 0,
                    'diff': 0,
                    'form': ['W', 'W', 'W', 'W', 'W'],
                    'last_updated': datetime.now().isoformat()
                }
        
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
            print(f"❌ 로컬 데이터 로드 실패: {e}")
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
            print(f"❌ 로컬 팀 데이터 로드 실패: {e}")
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
        print("🔄 실시간 데이터 캐시 초기화 완료")


# 전역 인스턴스
_live_fetcher = None

def get_live_fetcher():
    """LiveDataFetcher 싱글톤 인스턴스 반환"""
    global _live_fetcher
    if _live_fetcher is None:
        _live_fetcher = LiveDataFetcher()
    return _live_fetcher

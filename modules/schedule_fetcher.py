import requests
from datetime import datetime, timedelta
import time

class ScheduleFetcher:
    """스포츠 경기 일정 수집기 (ESPN API 연동)"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1시간 캐시
        self.last_update = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 리그별 ESPN API ID 매핑
        self.league_map = {
            'EPL': 'eng.1',
            'La Liga': 'esp.1',
            'Bundesliga': 'ger.1',
            'Serie A': 'ita.1',
            'NBA': 'nba',
            'MLB': 'mlb',
            'K리그1': 'kor.1'
        }

    def _is_cache_valid(self, key):
        if key not in self.last_update:
            return False
        return (time.time() - self.last_update[key]) < self.cache_duration

    def fetch_league_schedule(self, league):
        """ESPN API에서 특정 리그의 전체 일정 가져오기"""
        espn_id = self.league_map.get(league)
        if not espn_id:
            return []
            
        cache_key = f"schedule_{espn_id}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        try:
            # ESPN Scoreboard API (간단하고 정확함)
            sport_map = {
                'nba': 'basketball/nba',
                'mlb': 'baseball/mlb',
                'eng.1': 'soccer/eng.1',
                'esp.1': 'soccer/esp.1',
                'ger.1': 'soccer/ger.1',
                'ita.1': 'soccer/ita.1',
                'kor.1': 'soccer/kor.1'
            }
            
            sport_path = sport_map.get(espn_id, f"soccer/{espn_id}")
            url = f"https://site.api.espn.com/apis/site/v2/sports/{sport_path}/scoreboard"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            events = data.get('events', [])
            matches = []
            
            for event in events:
                comp = event['competitions'][0]
                home = next(t for t in comp['competitors'] if t['homeAway'] == 'home')
                away = next(t for t in comp['competitors'] if t['homeAway'] == 'away')
                
                # 날짜 및 시간 파싱 (ISO -> KST)
                utc_dt = datetime.strptime(event['date'], "%Y-%m-%dT%H:%MZ")
                kst_dt = utc_dt + timedelta(hours=9)
                
                match = {
                    'date': kst_dt.strftime("%Y-%m-%d"),
                    'time': kst_dt.strftime("%H:%M"),
                    'home': home['team']['displayName'],
                    'away': away['team']['displayName'],
                    'venue': comp.get('venue', {}).get('fullName', 'TBD'),
                    'tv': comp.get('broadcasts', [{'names': ['N/A']}])[0]['names'][0],
                    'status': event['status']['type']['description']
                }
                matches.append(match)
            
            self.cache[cache_key] = matches
            self.last_update[cache_key] = time.time()
            return matches
            
        except Exception as e:
            print(f"[ERROR] Schedule fetch failed for {league}: {e}")
            return []

# 싱글톤 인스턴스 전역 관리
_fetcher_instance = ScheduleFetcher()

def get_schedule_fetcher():
    return _fetcher_instance

def get_upcoming_matches(league, days=7):
    """특정 리그의 다가오는 경기 목록"""
    fetcher = get_schedule_fetcher()
    all_matches = fetcher.fetch_league_schedule(league)
    
    # 오늘 이후의 경기만 필터링 (최초 필터링은 간단하게 날짜 비교)
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = [m for m in all_matches if m['date'] >= today]
    return upcoming

def get_team_next_matches(league, team_name, limit=5):
    """특정 팀의 다음 경기 목록"""
    upcoming = get_upcoming_matches(league)
    team_matches = [
        m for m in upcoming 
        if team_name.lower() in m['home'].lower() or team_name.lower() in m['away'].lower()
    ]
    return team_matches[:limit]

def get_all_upcoming_matches():
    """모든 리그의 다가오는 경기 (메인 탭용)"""
    fetcher = get_schedule_fetcher()
    results = {}
    for league in fetcher.league_map.keys():
        matches = get_upcoming_matches(league)
        if matches:
            results[league] = matches
    return results

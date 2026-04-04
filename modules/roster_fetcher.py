"""
모든 리그 선수단 정보 실시간 수집 모듈
- NBA, MLB, KBO, EPL, La Liga, Bundesliga, Serie A
- ESPN API 및 웹 크롤링 활용
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict, Optional
import time
import concurrent.futures

class RosterFetcher:
    """선수단 정보를 가져오는 클래스"""
    
    # 포지션 전체 이름 매핑
    POSITION_FULL_NAMES = {
        # NBA 포지션
        'G': 'Guard (가드)',
        'F': 'Forward (포워드)',
        'C': 'Center (센터)',
        'PG': 'Point Guard (포인트가드)',
        'SG': 'Shooting Guard (슈팅가드)',
        'SF': 'Small Forward (스몰포워드)',
        'PF': 'Power Forward (파워포워드)',
        
        # MLB 포지션
        'P': 'Pitcher (투수)',
        'SP': 'Starting Pitcher (선발투수)',
        'RP': 'Relief Pitcher (구원투수)',
        'C': 'Catcher (포수)',
        '1B': 'First Base (1루수)',
        '2B': 'Second Base (2루수)',
        '3B': 'Third Base (3루수)',
        'SS': 'Shortstop (유격수)',
        'LF': 'Left Field (좌익수)',
        'CF': 'Center Field (중견수)',
        'RF': 'Right Field (우익수)',
        'OF': 'Outfield (외야수)',
        'DH': 'Designated Hitter (지명타자)',
        'IF': 'Infield (내야수)',
        
        # 축구 포지션
        'GK': 'Goalkeeper (골키퍼)',
        'D': 'Defender (수비수)',
        'DF': 'Defender (수비수)',
        'M': 'Midfielder (미드필더)',
        'MF': 'Midfielder (미드필더)',
        'F': 'Forward (공격수)',
        'FW': 'Forward (공격수)',
        'CB': 'Center Back (중앙수비수)',
        'LB': 'Left Back (좌측수비수)',
        'RB': 'Right Back (우측수비수)',
        'LWB': 'Left Wing Back (좌측윙백)',
        'RWB': 'Right Wing Back (우측윙백)',
        'CDM': 'Defensive Midfielder (수비형미드필더)',
        'CM': 'Central Midfielder (중앙미드필더)',
        'CAM': 'Attacking Midfielder (공격형미드필더)',
        'LM': 'Left Midfielder (좌측미드필더)',
        'RM': 'Right Midfielder (우측미드필더)',
        'LW': 'Left Winger (좌측윙어)',
        'RW': 'Right Winger (우측윙어)',
        'ST': 'Striker (스트라이커)',
        
        # 배구 포지션
        'OH': 'Outside Hitter (아웃사이드히터)',
        'MB': 'Middle Blocker (미들블로커)',
        'S': 'Setter (세터)',
        'L': 'Libero (리베로)',
        'OP': 'Opposite (오포지트)',
        'RS': 'Right Side (라이트)',
        'WS': 'Wing Spiker (윙스파이커)',
    }
    
    def __init__(self, league="NBA"):
        """
        Args:
            league (str): 리그 이름
        """
        self.league = league
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # ESPN API 기본 URL
        self.espn_api_base = "https://site.api.espn.com/apis/site/v2/sports"
        
        # 리그별 ESPN 코드
        self.league_codes = {
            'NBA': 'basketball/nba',
            'MLB': 'baseball/mlb',
            'EPL': 'soccer/eng.1',
            'La Liga': 'soccer/esp.1',
            'Bundesliga': 'soccer/ger.1',
            'Serie A': 'soccer/ita.1',
            'MLS': 'soccer/usa.1'
        }
        
        # 캐시
        self.cache = {}
        self.cache_duration = 3600  # 1시간
    
    def get_position_full_name(self, position_abbr: str) -> str:
        """포지션 약어를 전체 이름으로 변환 (리그별 구분)"""
        
        # 리그별 포지션 매핑
        league_positions = {
            'NBA': {
                'G': 'Guard (가드)',
                'F': 'Forward (포워드)',
                'C': 'Center (센터)',
                'PG': 'Point Guard (포인트가드)',
                'SG': 'Shooting Guard (슈팅가드)',
                'SF': 'Small Forward (스몰포워드)',
                'PF': 'Power Forward (파워포워드)',
            },
            'MLB': {
                'P': 'Pitcher (투수)',
                'SP': 'Starting Pitcher (선발투수)',
                'RP': 'Relief Pitcher (구원투수)',
                'C': 'Catcher (포수)',
                '1B': 'First Base (1루수)',
                '2B': 'Second Base (2루수)',
                '3B': 'Third Base (3루수)',
                'SS': 'Shortstop (유격수)',
                'LF': 'Left Field (좌익수)',
                'CF': 'Center Field (중견수)',
                'RF': 'Right Field (우익수)',
                'OF': 'Outfield (외야수)',
                'DH': 'Designated Hitter (지명타자)',
                'IF': 'Infield (내야수)',
            },
            'KBO': {
                'P': 'Pitcher (투수)',
                'SP': 'Starting Pitcher (선발투수)',
                'RP': 'Relief Pitcher (구원투수)',
                'C': 'Catcher (포수)',
                '1B': 'First Base (1루수)',
                '2B': 'Second Base (2루수)',
                '3B': 'Third Base (3루수)',
                'SS': 'Shortstop (유격수)',
                'LF': 'Left Field (좌익수)',
                'CF': 'Center Field (중견수)',
                'RF': 'Right Field (우익수)',
                'OF': 'Outfield (외야수)',
                'DH': 'Designated Hitter (지명타자)',
                'IF': 'Infield (내야수)',
            },
            'EPL': {
                'GK': 'Goalkeeper (골키퍼)',
                'G': 'Goalkeeper (골키퍼)',
                'D': 'Defender (수비수)',
                'DF': 'Defender (수비수)',
                'M': 'Midfielder (미드필더)',
                'MF': 'Midfielder (미드필더)',
                'F': 'Forward (공격수)',
                'FW': 'Forward (공격수)',
                'CB': 'Center Back (중앙수비수)',
                'LB': 'Left Back (좌측수비수)',
                'RB': 'Right Back (우측수비수)',
                'LWB': 'Left Wing Back (좌측윙백)',
                'RWB': 'Right Wing Back (우측윙백)',
                'CDM': 'Defensive Midfielder (수비형미드필더)',
                'CM': 'Central Midfielder (중앙미드필더)',
                'CAM': 'Attacking Midfielder (공격형미드필더)',
                'LM': 'Left Midfielder (좌측미드필더)',
                'RM': 'Right Midfielder (우측미드필더)',
                'LW': 'Left Winger (좌측윙어)',
                'RW': 'Right Winger (우측윙어)',
                'ST': 'Striker (스트라이커)',
                'CF': 'Center Forward (중앙공격수)',
            },
            'KBL': {
                'G': 'Guard (가드)',
                'F': 'Forward (포워드)',
                'C': 'Center (센터)',
                'PG': 'Point Guard (포인트가드)',
                'SG': 'Shooting Guard (슈팅가드)',
                'SF': 'Small Forward (스몰포워드)',
                'PF': 'Power Forward (파워포워드)',
            },
            'V-리그 남자': {
                'OH': 'Outside Hitter (아웃사이드히터)',
                'MB': 'Middle Blocker (미들블로커)',
                'S': 'Setter (세터)',
                'L': 'Libero (리베로)',
                'OP': 'Opposite (오포지트)',
                'RS': 'Right Side (라이트)',
                'WS': 'Wing Spiker (윙스파이커)',
            },
            'V-리그 여자': {
                'OH': 'Outside Hitter (아웃사이드히터)',
                'MB': 'Middle Blocker (미들블로커)',
                'S': 'Setter (세터)',
                'L': 'Libero (리베로)',
                'OP': 'Opposite (오포지트)',
                'RS': 'Right Side (라이트)',
                'WS': 'Wing Spiker (윙스파이커)',
            },
            'K리그1': {
                'GK': 'Goalkeeper (골키퍼)',
                'G': 'Goalkeeper (골키퍼)',
                'D': 'Defender (수비수)',
                'DF': 'Defender (수비수)',
                'M': 'Midfielder (미드필더)',
                'MF': 'Midfielder (미드필더)',
                'F': 'Forward (공격수)',
                'FW': 'Forward (공격수)',
            },
        }
        
        # 축구 리그들 (같은 포지션 매핑 사용)
        soccer_leagues = ['La Liga', 'Bundesliga', 'Serie A']
        for league in soccer_leagues:
            league_positions[league] = league_positions['EPL']
        
        # 현재 리그의 포지션 매핑 가져오기
        positions = league_positions.get(self.league, self.POSITION_FULL_NAMES)
        
        return positions.get(position_abbr, position_abbr)
    
    def fetch_team_roster(self, team_name: str) -> List[Dict]:
        """
        팀의 선수단 정보를 가져옵니다.
        
        Args:
            team_name (str): 팀 이름
            
        Returns:
            List[Dict]: 선수 정보 리스트
        """
        cache_key = f"{self.league}_{team_name}"
        
        # 캐시 확인
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                print(f"캐시에서 {team_name} 로스터 반환")
                # 중요: 캐시된 데이터도 deep copy하여 반환!
                import copy
                return copy.deepcopy(cached_data)
        
        try:
            if self.league in ['NBA', 'MLB']:
                roster = self._fetch_espn_roster(team_name)
            elif self.league == 'KBO':
                roster = self._fetch_kbo_roster(team_name)
            elif self.league in ['K리그1', 'KBL', 'V-리그 남자', 'V-리그 여자']:
                roster = self._fetch_korean_league_roster(team_name)
            else:  # 축구 리그
                roster = self._fetch_soccer_roster(team_name)
            
            # 캐시 저장
            self.cache[cache_key] = (time.time(), roster)
            # 중요: 반환할 때도 deep copy!
            import copy
            return copy.deepcopy(roster)
            
        except Exception as e:
            print(f"선수단 정보 가져오기 실패 ({team_name}): {e}")
            return []

    
    def _fetch_espn_roster(self, team_name: str) -> List[Dict]:
        """ESPN API로 NBA/MLB 로스터 가져오기"""
        try:
            league_code = self.league_codes.get(self.league)
            
            # 1. 팀 목록 가져오기
            teams_url = f"{self.espn_api_base}/{league_code}/teams"
            response = requests.get(teams_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            teams_data = response.json()
            sports = teams_data.get("sports", [])
            if not sports:
                return []
            
            leagues = sports[0].get("leagues", [])
            if not leagues:
                return []
            
            teams = leagues[0].get("teams", [])
            
            # 2. 팀 ID 찾기
            team_id = None
            for team in teams:
                team_info = team.get("team", {})
                display_name = team_info.get("displayName", "").lower()
                short_name = team_info.get("shortDisplayName", "").lower()
                
                if team_name.lower() in display_name or team_name.lower() in short_name:
                    team_id = team_info.get("id")
                    break
            
            if not team_id:
                print(f"팀 ID를 찾을 수 없음: {team_name}")
                return []
            
            # 3. 로스터 가져오기
            roster_url = f"{self.espn_api_base}/{league_code}/teams/{team_id}/roster"
            roster_response = requests.get(roster_url, headers=self.headers, timeout=10)
            roster_response.raise_for_status()
            
            roster_data = roster_response.json()
            
            # MLB는 athletes 배열 안에 items 배열이 있음
            athletes = roster_data.get("athletes", [])
            
            # 선수 기본 데이터 수집
            basic_athletes = []
            for athlete_group in athletes:
                # MLB: items 배열에서 선수 정보 추출
                if "items" in athlete_group:
                    for athlete in athlete_group["items"]:
                        basic_athletes.append(athlete)
                # NBA: 직접 선수 정보
                else:
                    basic_athletes.append(athlete_group)
            
            players = []
            if self.league == 'NBA':
                # NBA: 선수별 통계를 병렬로 수집
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_athlete = {
                        executor.submit(self._parse_espn_player, athlete, fetch_stats=True): athlete 
                        for athlete in basic_athletes
                    }
                    for future in concurrent.futures.as_completed(future_to_athlete):
                        try:
                            player_info = future.result()
                            if player_info:
                                players.append(player_info)
                        except Exception as e:
                            print(f"선수 통계 파싱 병렬 스레드 오류: {e}")
            else:
                # 다른 리그: 기본 파싱만 수행
                for athlete in basic_athletes:
                    player_info = self._parse_espn_player(athlete, fetch_stats=False)
                    if player_info:
                        players.append(player_info)
            
            print(f"ESPN에서 {team_name} 로스터 {len(players)}명 가져옴")
            return players
            
        except Exception as e:
            print(f"ESPN 로스터 가져오기 실패: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_espn_player(self, athlete: Dict, fetch_stats: bool = False) -> Optional[Dict]:
        """ESPN 선수 데이터 파싱"""
        try:
            # 선수 이름 추출 - 여러 경로 시도
            name = "Unknown"
            if "displayName" in athlete and athlete["displayName"]:
                name = athlete["displayName"]
            elif "fullName" in athlete and athlete["fullName"]:
                name = athlete["fullName"]
            elif "athlete" in athlete:
                # 중첩된 athlete 객체에서 이름 추출
                nested = athlete["athlete"]
                if "displayName" in nested:
                    name = nested["displayName"]
                elif "fullName" in nested:
                    name = nested["fullName"]
            
            # 포지션 파싱
            position = "N/A"
            position_info = athlete.get("position", {})
            if isinstance(position_info, dict):
                position = position_info.get("abbreviation", "N/A")
            elif isinstance(position_info, str):
                position = position_info
            
            # 포지션 전체 이름 가져오기
            position_full = self.get_position_full_name(position)
            
            # athlete 객체가 중첩된 경우 처리
            athlete_data = athlete.get("athlete", athlete)
            player_id = athlete_data.get("id")
            
            # 기본 통계
            stats = {}
            if athlete_data.get("statistics"):
                stat_list = athlete_data.get("statistics", [])
                if stat_list and len(stat_list) > 0:
                    stats = stat_list[0]
            
            # NBA: fetch_stats가 True이면 개별 API 호출하여 시즌 평균 가져오기
            if self.league == 'NBA' and fetch_stats and player_id:
                try:
                    stats_url = f"https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{player_id}/stats"
                    r = requests.get(stats_url, headers=self.headers, timeout=5)
                    if r.status_code == 200:
                        player_stats_data = r.json()
                        cats = player_stats_data.get("categories", [])
                        if cats:
                            avg_stats = cats[0].get("statistics", [])
                            if avg_stats:
                                # 가장 최근 시즌 성적을 가져오기 위해 마지막 인덱스 사용
                                season_stats = avg_stats[-1].get("stats", [])
                                if season_stats and len(season_stats) >= 18:
                                    stats["points"] = float(season_stats[17])   # PTS
                                    stats["rebounds"] = float(season_stats[11]) # REB
                                    stats["assists"] = float(season_stats[12])  # AST
                except Exception as e:
                    pass  # 오류 무시
                    
            player_info = {
                "name": name,
                "position": position,
                "position_full": position_full,  # 전체 포지션 이름 추가
                "age": athlete_data.get("age", 0),
                "jersey": str(athlete_data.get("jersey", "")),
                "height": athlete_data.get("displayHeight", ""),
                "weight": athlete_data.get("displayWeight", ""),
            }
            
            # 리그별 통계 추가
            if self.league == 'NBA':
                player_info.update({
                    "ppg": float(stats.get("points", 0)) if stats.get("points") else 0.0,
                    "rpg": float(stats.get("rebounds", 0)) if stats.get("rebounds") else 0.0,
                    "apg": float(stats.get("assists", 0)) if stats.get("assists") else 0.0,
                    "rating": self._calculate_nba_rating(stats)
                })
            elif self.league == 'MLB':
                player_info.update({
                    "avg": float(stats.get("avg", 0)) if stats.get("avg") else 0.0,
                    "hr": int(stats.get("homeRuns", 0)) if stats.get("homeRuns") else 0,
                    "rbi": int(stats.get("RBIs", 0)) if stats.get("RBIs") else 0,
                    "era": float(stats.get("ERA", 0)) if stats.get("ERA") else 0.0,
                    "rating": self._calculate_mlb_rating(stats, position)
                })
            
            return player_info
            
        except Exception as e:
            print(f"선수 파싱 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

    
    def _fetch_kbo_roster(self, team_name: str) -> List[Dict]:
        """KBO 로스터 가져오기 (2026 시즌 실제 선수 명단)"""
        try:
            from data.kbo_rosters_complete_2026 import KBO_ROSTERS_2026
            import copy
            
            # 팀명 변환: "KIA 타이거즈" -> "KIA"
            short_team_name = team_name
            for key in KBO_ROSTERS_2026.keys():
                if key in team_name:
                    short_team_name = key
                    break
            
            # 원본 데이터를 깊은 복사하여 가져오기 (중요!)
            base_roster = copy.deepcopy(KBO_ROSTERS_2026.get(short_team_name, []))
        except ImportError:
            print(f"Warning: Could not import KBO roster data")
            base_roster = []
        
        # 포지션 전체 이름 추가
        for player in base_roster:
            player['position_full'] = self.get_position_full_name(player['position'])
        
        return base_roster
    
    def _fetch_korean_league_roster(self, team_name: str) -> List[Dict]:
        """한국 리그 로스터 가져오기 (2025-26 시즌 실제 선수 명단)"""
        try:
            import copy
            base_roster = []
            
            if self.league == 'K리그1':
                from data.kleague_rosters_complete_2026 import KLEAGUE_ROSTERS_2026
                print(f"[SEARCH] K리그1 로스터 검색: '{team_name}'")
                print(f"   사용 가능한 팀: {list(KLEAGUE_ROSTERS_2026.keys())[:3]}...")
                # 깊은 복사 사용
                base_roster = copy.deepcopy(KLEAGUE_ROSTERS_2026.get(team_name, []))
            elif self.league == 'KBL':
                from data.kbl_rosters_complete_2025_26 import KBL_ROSTERS_2025_26
                print(f"[SEARCH] KBL 로스터 검색: '{team_name}'")
                print(f"   사용 가능한 팀: {list(KBL_ROSTERS_2025_26.keys())}")
                # 깊은 복사 사용
                base_roster = copy.deepcopy(KBL_ROSTERS_2025_26.get(team_name, []))
                print(f"   검색 결과: {len(base_roster)}명 선수")
                if base_roster:
                    print(f"   첫 3명: {[p['name'] for p in base_roster[:3]]}")
            elif self.league == 'V-리그 남자':
                from data.vleague_rosters_complete_2025_26 import VLEAGUE_MEN_ROSTERS_2025_26
                # 깊은 복사 사용
                base_roster = copy.deepcopy(VLEAGUE_MEN_ROSTERS_2025_26.get(team_name, []))
            elif self.league == 'V-리그 여자':
                from data.vleague_rosters_complete_2025_26 import VLEAGUE_WOMEN_ROSTERS_2025_26
                # 깊은 복사 사용
                base_roster = copy.deepcopy(VLEAGUE_WOMEN_ROSTERS_2025_26.get(team_name, []))
                
        except ImportError as e:
            print(f"Warning: Could not import {self.league} roster data: {e}")
            base_roster = []
        
        # 포지션 전체 이름 추가
        for player in base_roster:
            player['position_full'] = self.get_position_full_name(player['position'])
        
        return base_roster
    
    def _fetch_soccer_roster(self, team_name: str) -> List[Dict]:
        """축구 로스터 가져오기 (ESPN API 시도)"""
        try:
            league_code = self.league_codes.get(self.league)
            
            # ESPN API로 시도
            teams_url = f"{self.espn_api_base}/{league_code}/teams"
            response = requests.get(teams_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            teams_data = response.json()
            sports = teams_data.get("sports", [])
            if not sports:
                return []
            
            leagues = sports[0].get("leagues", [])
            if not leagues:
                return []
            
            teams = leagues[0].get("teams", [])
            
            # 팀 ID 찾기 - 더 유연한 매칭
            team_id = None
            search_terms = [team_name.lower()]
            
            # 팀 이름 변형 추가
            if "inter milan" in team_name.lower():
                search_terms.extend(["inter", "internazionale"])
            elif "ac milan" in team_name.lower():
                search_terms.extend(["milan", "ac milan"])
            elif "manchester" in team_name.lower():
                search_terms.extend([team_name.lower().replace("manchester ", "")])
            
            for team in teams:
                team_info = team.get("team", {})
                display_name = team_info.get("displayName", "").lower()
                short_name = team_info.get("shortDisplayName", "").lower()
                name = team_info.get("name", "").lower()
                
                # 여러 이름 형식으로 매칭 시도
                for search_term in search_terms:
                    if (search_term in display_name or 
                        search_term in short_name or 
                        search_term in name or
                        display_name in search_term):
                        team_id = team_info.get("id")
                        break
                
                if team_id:
                    break
            
            if not team_id:
                return []
            
            # 로스터 가져오기
            roster_url = f"{self.espn_api_base}/{league_code}/teams/{team_id}/roster"
            roster_response = requests.get(roster_url, headers=self.headers, timeout=10)
            roster_response.raise_for_status()
            
            roster_data = roster_response.json()
            athletes = roster_data.get("athletes", [])
            
            players = []
            for athlete in athletes:
                player_info = self._parse_soccer_player(athlete)
                if player_info:
                    players.append(player_info)
            
            print(f"ESPN에서 {team_name} 로스터 {len(players)}명 가져옴")
            return players
            
        except Exception as e:
            print(f"축구 로스터 가져오기 실패: {e}")
            return []
    
    def _parse_soccer_player(self, athlete: Dict) -> Optional[Dict]:
        """축구 선수 데이터 파싱"""
        try:
            name = athlete.get("displayName", "Unknown")
            position_info = athlete.get("position", {})
            position = position_info.get("abbreviation", "N/A") if isinstance(position_info, dict) else "N/A"
            
            # 포지션 전체 이름 가져오기
            position_full = self.get_position_full_name(position)
            
            player_info = {
                "name": name,
                "position": position,
                "position_full": position_full,  # 전체 포지션 이름 추가
                "age": athlete.get("age", 0),
                "jersey": athlete.get("jersey", ""),
                "height": athlete.get("displayHeight", ""),
                "weight": athlete.get("displayWeight", ""),
                "goals": 0,
                "assists": 0,
                "rating": 7.0
            }
            
            return player_info
            
        except Exception as e:
            print(f"축구 선수 파싱 실패: {e}")
            return None

    
    def _calculate_nba_rating(self, stats: Dict) -> float:
        """NBA 선수 평점 계산"""
        try:
            ppg = float(stats.get("points", 0)) if stats.get("points") else 0
            rpg = float(stats.get("rebounds", 0)) if stats.get("rebounds") else 0
            apg = float(stats.get("assists", 0)) if stats.get("assists") else 0
            
            # 간단한 평점 계산
            rating = (ppg * 0.5 + rpg * 0.3 + apg * 0.4) / 3
            return min(10.0, max(5.0, rating))
        except:
            return 7.0
    
    def _calculate_mlb_rating(self, stats: Dict, position: str) -> float:
        """MLB 선수 평점 계산"""
        try:
            if 'P' in position:  # 투수
                era = float(stats.get("ERA", 4.5)) if stats.get("ERA") else 4.5
                rating = 10.0 - (era / 2)
                return min(10.0, max(5.0, rating))
            else:  # 타자
                avg = float(stats.get("avg", 0.250)) if stats.get("avg") else 0.250
                rating = avg * 30
                return min(10.0, max(5.0, rating))
        except:
            return 7.0
    
    def fetch_all_rosters(self) -> Dict[str, List[Dict]]:
        """
        리그의 모든 팀 로스터 가져오기
        
        Returns:
            Dict[str, List[Dict]]: 팀별 선수 리스트
        """
        # 주요 팀 목록
        major_teams = {
            'NBA': ['Los Angeles Lakers', 'Boston Celtics', 'Golden State Warriors', 
                   'Milwaukee Bucks', 'Phoenix Suns'],
            'MLB': ['New York Yankees', 'Los Angeles Dodgers', 'Boston Red Sox',
                   'Houston Astros', 'Atlanta Braves'],
            'KBO': ['KIA Tigers', 'Samsung Lions', 'LG Twins', 'Doosan Bears', 'KT Wiz'],
            'EPL': ['Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Manchester United'],
            'La Liga': ['Real Madrid', 'Barcelona', 'Atletico Madrid'],
            'Bundesliga': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig'],
            'Serie A': ['Inter Milan', 'AC Milan', 'Juventus']
        }
        
        teams = major_teams.get(self.league, [])
        all_rosters = {}
        
        for team in teams:
            roster = self.fetch_team_roster(team)
            if roster:
                all_rosters[team] = roster
        
        return all_rosters
    
    def get_player_info(self, player_name: str, team_name: str) -> Optional[Dict]:
        """
        특정 선수 정보 가져오기
        
        Args:
            player_name (str): 선수 이름
            team_name (str): 팀 이름
            
        Returns:
            Optional[Dict]: 선수 정보
        """
        roster = self.fetch_team_roster(team_name)
        
        for player in roster:
            if player_name.lower() in player.get('name', '').lower():
                return player
        
        return None


def get_team_roster(league: str, team_name: str) -> List[Dict]:
    """간단한 로스터 가져오기 함수"""
    fetcher = RosterFetcher(league=league)
    return fetcher.fetch_team_roster(team_name)


def refresh_roster_cache():
    """로스터 캐시 초기화"""
    fetcher = RosterFetcher()
    fetcher.cache = {}
    print("로스터 캐시 초기화 완료")


if __name__ == "__main__":
    # 테스트 코드
    print("="*70)
    print("선수단 정보 실시간 수집 테스트")
    print("="*70)
    
    test_cases = [
        ('NBA', 'Los Angeles Lakers'),
        ('MLB', 'New York Yankees'),
        ('KBO', 'KIA Tigers'),
    ]
    
    for league, team in test_cases:
        print(f"\n{league}: {team}")
        print('-'*70)
        
        fetcher = RosterFetcher(league=league)
        roster = fetcher.fetch_team_roster(team)
        
        print(f"선수 수: {len(roster)}명")
        
        if roster:
            print("\n샘플 선수 (처음 3명):")
            for player in roster[:3]:
                print(f"  - {player.get('name')} ({player.get('position')}) "
                      f"#{player.get('jersey', 'N/A')}")

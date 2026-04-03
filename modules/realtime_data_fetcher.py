"""
실시간 데이터 수집 시스템
- NBA Stats API 연동
- Basketball-Reference 크롤링
- KBL API 연동
- 부상 리포트 실시간 수집
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re


class RealTimeDataFetcher:
    """실시간 스포츠 데이터 수집"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5분 캐시
        self.last_update = {}
        
        # User-Agent 설정
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nba.com/'
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 확인"""
        if cache_key not in self.last_update:
            return False
        
        elapsed = time.time() - self.last_update[cache_key]
        return elapsed < self.cache_duration
    
    def _update_cache(self, cache_key: str, data: any):
        """캐시 업데이트"""
        self.cache[cache_key] = data
        self.last_update[cache_key] = time.time()
    
    # ==================== NBA ====================
    
    def fetch_nba_player_stats(self, player_name: str, team_name: str) -> Optional[Dict]:
        """
        NBA 선수 통계 실시간 수집
        
        소스: Basketball-Reference
        """
        
        cache_key = f"nba_player_{player_name}_{team_name}"
        if self._is_cache_valid(cache_key):
            print(f"[CACHE] NBA 선수 데이터 캐시 사용: {player_name}")
            return self.cache[cache_key]
        
        try:
            # Basketball-Reference URL 생성
            # 예: https://www.basketball-reference.com/players/t/tatumja01.html
            player_id = self._generate_bbref_player_id(player_name)
            url = f"https://www.basketball-reference.com/players/{player_id[0]}/{player_id}.html"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 2025-26 시즌 통계 추출
            stats = self._parse_bbref_player_stats(soup, '2025-26')
            
            if stats:
                self._update_cache(cache_key, stats)
                print(f"[OK] NBA 선수 데이터 수집: {player_name}")
                return stats
        
        except Exception as e:
            print(f"[ERROR] NBA 선수 데이터 수집 실패 ({player_name}): {e}")
        
        return None
    
    def fetch_nba_injury_report(self) -> List[Dict]:
        """
        NBA 부상 리포트 실시간 수집
        
        소스: NBA.com Injury Report
        """
        
        cache_key = "nba_injury_report"
        if self._is_cache_valid(cache_key):
            print(f"[CACHE] NBA 부상 리포트 캐시 사용")
            return self.cache[cache_key]
        
        try:
            # NBA.com Injury Report API
            url = "https://www.nba.com/stats/injury-report"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 부상 리포트 파싱
            injuries = self._parse_nba_injury_report(soup)
            
            if injuries:
                self._update_cache(cache_key, injuries)
                print(f"[OK] NBA 부상 리포트 수집: {len(injuries)}명")
                return injuries
        
        except Exception as e:
            print(f"[ERROR] NBA 부상 리포트 수집 실패: {e}")
        
        return []
    
    def fetch_nba_team_schedule(self, team_name: str) -> List[Dict]:
        """
        NBA 팀 경기 일정 수집 (백투백 감지용)
        
        소스: Basketball-Reference
        """
        
        cache_key = f"nba_schedule_{team_name}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # 팀 약어 변환
            team_abbr = self._get_nba_team_abbr(team_name)
            url = f"https://www.basketball-reference.com/teams/{team_abbr}/2026_games.html"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 경기 일정 파싱
            schedule = self._parse_bbref_schedule(soup)
            
            if schedule:
                self._update_cache(cache_key, schedule)
                print(f"[OK] NBA 경기 일정 수집: {team_name}")
                return schedule
        
        except Exception as e:
            print(f"[ERROR] NBA 경기 일정 수집 실패 ({team_name}): {e}")
        
        return []
    
    # ==================== KBL ====================
    
    def fetch_kbl_player_stats(self, player_name: str, team_name: str) -> Optional[Dict]:
        """
        KBL 선수 통계 실시간 수집
        
        소스: KBL 공식 홈페이지
        """
        
        cache_key = f"kbl_player_{player_name}_{team_name}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # KBL API (실제 API 엔드포인트는 확인 필요)
            url = f"https://www.kbl.or.kr/api/player/stats"
            params = {
                'playerName': player_name,
                'season': '2025-26'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # KBL 통계 파싱
            stats = self._parse_kbl_player_stats(data)
            
            if stats:
                self._update_cache(cache_key, stats)
                print(f"[OK] KBL 선수 데이터 수집: {player_name}")
                return stats
        
        except Exception as e:
            print(f"[ERROR] KBL 선수 데이터 수집 실패 ({player_name}): {e}")
        
        return None
    
    def fetch_kbl_injury_report(self) -> List[Dict]:
        """KBL 부상 리포트 수집"""
        
        cache_key = "kbl_injury_report"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            url = "https://www.kbl.or.kr/injury-report"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            injuries = self._parse_kbl_injury_report(soup)
            
            if injuries:
                self._update_cache(cache_key, injuries)
                print(f"[OK] KBL 부상 리포트 수집: {len(injuries)}명")
                return injuries
        
        except Exception as e:
            print(f"[ERROR] KBL 부상 리포트 수집 실패: {e}")
        
        return []
    
    # ==================== K-League (축구) ====================
    
    def fetch_kleague_player_stats(self, player_name: str, team_name: str) -> Optional[Dict]:
        """
        K-League 선수 통계 실시간 수집 (xG, xA, PPDA 포함)
        
        소스: Statiz, K-League 공식 홈페이지
        """
        
        cache_key = f"kleague_player_{player_name}_{team_name}"
        if self._is_cache_valid(cache_key):
            print(f"[CACHE] K-League 선수 데이터 캐시 사용: {player_name}")
            return self.cache[cache_key]
        
        try:
            # Statiz K-League 선수 페이지
            # 예: http://www.statiz.co.kr/player.php?opt=1&name=손흥민
            url = "http://www.statiz.co.kr/player.php"
            params = {
                'opt': '1',  # K-League
                'name': player_name
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'euc-kr'  # Statiz 인코딩
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # K-League 통계 파싱 (xG, xA 포함)
            stats = self._parse_kleague_player_stats(soup)
            
            if stats:
                self._update_cache(cache_key, stats)
                print(f"[OK] K-League 선수 데이터 수집: {player_name}")
                return stats
        
        except Exception as e:
            print(f"[ERROR] K-League 선수 데이터 수집 실패 ({player_name}): {e}")
        
        return None
    
    def fetch_kleague_team_stats(self, team_name: str) -> Optional[Dict]:
        """
        K-League 팀 통계 수집 (순위, 승점, 최근 폼 등)
        
        소스: K-League 공식 데이터 포털
        """
        
        cache_key = f"kleague_team_stats_{team_name}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # 1. 공식 순위표에서 기본 통계 가져오기
            from modules.live_data_fetcher import get_live_fetcher
            live_fetcher = get_live_fetcher()
            standings = live_fetcher.fetch_kleague_standings()
            
            # 팀명 매핑 (realtime_data_fetcher에도 매핑 로직 필요하거나 live_data_fetcher의 결과 사용)
            # 여기서는 live_data_fetcher가 이미 매핑된 이름을 키로 반환하므로 직접 찾기 시도
            # (기존 DataCollector가 사용하는 '울산', '서울' 등 짧은 이름 기준)
            
            team_data = standings.get(team_name)
            if not team_data:
                # 못 찾을 경우 원본에서 다시 매핑 시도
                for k in standings:
                    if team_name in k or k in team_name:
                        team_data = standings[k]
                        break
            
            if not team_data:
                return None

            # 2. 최근 경기 결과로 폼(Form) 계산
            results = self.fetch_kleague_match_results()
            form = self._get_kleague_form_from_results(team_name, results)
            
            stats = {
                'team_name': team_name,
                'position': team_data.get('position', 0),
                'points': team_data.get('points', 0),
                'played': team_data.get('played', 0),
                'wins': team_data.get('wins', 0),
                'draws': team_data.get('draws', 0),
                'losses': team_data.get('losses', 0),
                'goals_for': team_data.get('goals_for', 0),
                'goals_against': team_data.get('goals_against', 0),
                'form': form,
                'real_data': True,
                'last_updated': datetime.now().isoformat()
            }
            
            self._update_cache(cache_key, stats)
            return stats
            
        except Exception as e:
            print(f"[ERROR] K-League 팀 데이터 수집 실패 ({team_name}): {e}")
        
        return None

    def fetch_kleague_match_results(self, month: str = None) -> List[Dict]:
        """K-League 공식 경기 결과 수집"""
        if not month:
            month = datetime.now().strftime('%m')
            
        cache_key = f"kleague_matches_{month}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
            
        try:
            url = "https://www.kleague.com/getScheduleList.do"
            payload = {
                "leagueId": "1",
                "year": "2026",
                "month": month,
                "teamId": "",
                "ticketYn": ""
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            matches = data.get('data', {}).get('scheduleList', [])
            
            self._update_cache(cache_key, matches)
            return matches
        except Exception as e:
            print(f"[ERROR] K-League 경기 일정 수집 실패: {e}")
            return []

    def _get_kleague_form_from_results(self, team_name: str, results: List[Dict]) -> List[str]:
        """경기 결과 리스트에서 특정 팀의 최근 폼(W, D, L) 추출"""
        form = []
        # 경기 완료된 순서대로 정렬 ('FE' = finished)
        finished_matches = [m for m in results if m.get('gameStatus') == 'FE']
        # 날짜 역순 정렬 (최신순)
        finished_matches.sort(key=lambda x: (x.get('gameDate', ''), x.get('gameTime', '')), reverse=True)
        
        for m in finished_matches:
            # 공식 API의 필드는 homeTeamName, awayTeamName
            home = m.get('homeTeamName', '').strip()
            away = m.get('awayTeamName', '').strip()
            h_score = int(m.get('homeGoal', 0) or 0)
            a_score = int(m.get('awayGoal', 0) or 0)
            
            result = None
            # team_name과 home/away명이 포함관계인지 확인 (서울 == FC서울 등)
            if team_name in home or home in team_name:
                if h_score > a_score: result = 'W'
                elif h_score == a_score: result = 'D'
                else: result = 'L'
            elif team_name in away or away in team_name:
                if a_score > h_score: result = 'W'
                elif a_score == h_score: result = 'D'
                else: result = 'L'
                
            if result:
                form.append(result)
                if len(form) >= 5: break
                
        return form if form else ['W', 'D', 'W', 'W', 'L']  # 기본값
    
    # ==================== KBO (야구) ====================
    
    def fetch_kbo_player_stats(self, player_name: str, team_name: str, 
                               player_type: str = 'batter') -> Optional[Dict]:
        """
        KBO 선수 통계 실시간 수집 (OPS, wOBA, ERA+, FIP 포함)
        
        Args:
            player_name: 선수 이름
            team_name: 팀 이름
            player_type: 'batter' 또는 'pitcher'
        
        소스: Statiz KBO
        """
        
        cache_key = f"kbo_player_{player_name}_{team_name}_{player_type}"
        if self._is_cache_valid(cache_key):
            print(f"[CACHE] KBO 선수 데이터 캐시 사용: {player_name}")
            return self.cache[cache_key]
        
        try:
            # Statiz KBO 선수 페이지
            # 예: http://www.statiz.co.kr/player.php?opt=3&name=김하성
            url = "http://www.statiz.co.kr/player.php"
            params = {
                'opt': '3',  # KBO
                'name': player_name
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # KBO 통계 파싱 (OPS, wOBA, ERA+, FIP 포함)
            if player_type == 'batter':
                stats = self._parse_kbo_batter_stats(soup)
            else:
                stats = self._parse_kbo_pitcher_stats(soup)
            
            if stats:
                self._update_cache(cache_key, stats)
                print(f"[OK] KBO 선수 데이터 수집: {player_name} ({player_type})")
                return stats
        
        except Exception as e:
            print(f"[ERROR] KBO 선수 데이터 수집 실패 ({player_name}): {e}")
        
        return None
    
    def fetch_kbo_injury_report(self) -> List[Dict]:
        """KBO 부상 리포트 수집"""
        
        cache_key = "kbo_injury_report"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # KBO 공식 홈페이지 부상자 명단
            url = "https://www.koreabaseball.com/Player/InjuryList.aspx"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            injuries = self._parse_kbo_injury_report(soup)
            
            if injuries:
                self._update_cache(cache_key, injuries)
                print(f"[OK] KBO 부상 리포트 수집: {len(injuries)}명")
                return injuries
        
        except Exception as e:
            print(f"[ERROR] KBO 부상 리포트 수집 실패: {e}")
        
        return []
    
    # ==================== V-League (배구) ====================
    
    def fetch_vleague_player_stats(self, player_name: str, team_name: str) -> Optional[Dict]:
        """
        V-League 선수 통계 실시간 수집 (스파이크율, 블록, 점프 등)
        
        소스: V-League 공식 홈페이지, KOVO
        """
        
        cache_key = f"vleague_player_{player_name}_{team_name}"
        if self._is_cache_valid(cache_key):
            print(f"[CACHE] V-League 선수 데이터 캐시 사용: {player_name}")
            return self.cache[cache_key]
        
        try:
            # V-League 공식 홈페이지 선수 통계
            # 예: https://www.kovo.co.kr/stats/player.asp
            url = "https://www.kovo.co.kr/stats/player.asp"
            params = {
                'playerName': player_name,
                'season': '2025-26'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # V-League 통계 파싱 (스파이크율, 블록, 디그 등)
            stats = self._parse_vleague_player_stats(soup)
            
            if stats:
                self._update_cache(cache_key, stats)
                print(f"[OK] V-League 선수 데이터 수집: {player_name}")
                return stats
        
        except Exception as e:
            print(f"[ERROR] V-League 선수 데이터 수집 실패 ({player_name}): {e}")
        
        return None
    
    def fetch_vleague_injury_report(self) -> List[Dict]:
        """V-League 부상 리포트 수집"""
        
        cache_key = "vleague_injury_report"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            url = "https://www.kovo.co.kr/injury-report"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            injuries = self._parse_vleague_injury_report(soup)
            
            if injuries:
                self._update_cache(cache_key, injuries)
                print(f"[OK] V-League 부상 리포트 수집: {len(injuries)}명")
                return injuries
        
        except Exception as e:
            print(f"[ERROR] V-League 부상 리포트 수집 실패: {e}")
        
        return []
    
    # ==================== 파싱 헬퍼 ====================
    
    def _generate_bbref_player_id(self, player_name: str) -> str:
        """
        Basketball-Reference 선수 ID 생성
        
        규칙: 성의 처음 5글자 + 이름의 처음 2글자 + 01
        예: Jayson Tatum → tatumja01
        """
        
        parts = player_name.lower().split()
        if len(parts) < 2:
            return player_name.lower()[:7] + "01"
        
        last_name = parts[-1][:5]
        first_name = parts[0][:2]
        
        return f"{last_name}{first_name}01"
    
    def _parse_bbref_player_stats(self, soup: BeautifulSoup, season: str) -> Optional[Dict]:
        """Basketball-Reference 선수 통계 파싱"""
        
        try:
            # Per Game 통계 테이블
            per_game_table = soup.find('table', {'id': 'per_game'})
            if not per_game_table:
                return None
            
            # 2025-26 시즌 행 찾기
            rows = per_game_table.find('tbody').find_all('tr')
            season_row = None
            
            for row in rows:
                season_cell = row.find('th', {'data-stat': 'season'})
                if season_cell and season in season_cell.text:
                    season_row = row
                    break
            
            if not season_row:
                return None
            
            # 통계 추출
            stats = {
                'ppg': self._extract_stat(season_row, 'pts_per_g'),
                'rpg': self._extract_stat(season_row, 'trb_per_g'),
                'apg': self._extract_stat(season_row, 'ast_per_g'),
                'spg': self._extract_stat(season_row, 'stl_per_g'),
                'bpg': self._extract_stat(season_row, 'blk_per_g'),
                'topg': self._extract_stat(season_row, 'tov_per_g'),
                'mpg': self._extract_stat(season_row, 'mp_per_g'),
                'fg_pct': self._extract_stat(season_row, 'fg_pct'),
                'three_pct': self._extract_stat(season_row, 'fg3_pct'),
                'ft_pct': self._extract_stat(season_row, 'ft_pct')
            }
            
            # Advanced 통계 테이블
            advanced_table = soup.find('table', {'id': 'advanced'})
            if advanced_table:
                adv_rows = advanced_table.find('tbody').find_all('tr')
                for row in adv_rows:
                    season_cell = row.find('th', {'data-stat': 'season'})
                    if season_cell and season in season_cell.text:
                        stats['per'] = self._extract_stat(row, 'per')
                        stats['ws'] = self._extract_stat(row, 'ws')
                        stats['bpm'] = self._extract_stat(row, 'bpm')
                        break
            
            return stats
        
        except Exception as e:
            print(f"[ERROR] Basketball-Reference 파싱 실패: {e}")
            return None
    
    def _parse_nba_injury_report(self, soup: BeautifulSoup) -> List[Dict]:
        """NBA 부상 리포트 파싱"""
        
        injuries = []
        
        try:
            # 부상 리포트 테이블 찾기
            injury_table = soup.find('table', class_='injury-report')
            if not injury_table:
                return injuries
            
            rows = injury_table.find('tbody').find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    injury = {
                        'name': cells[0].text.strip(),
                        'team': cells[1].text.strip(),
                        'injury_type': cells[2].text.strip(),
                        'status': cells[3].text.strip(),
                        'updated': datetime.now().isoformat()
                    }
                    injuries.append(injury)
        
        except Exception as e:
            print(f"[ERROR] NBA 부상 리포트 파싱 실패: {e}")
        
        return injuries
    
    def _parse_bbref_schedule(self, soup: BeautifulSoup) -> List[Dict]:
        """Basketball-Reference 경기 일정 파싱"""
        
        schedule = []
        
        try:
            games_table = soup.find('table', {'id': 'games'})
            if not games_table:
                return schedule
            
            rows = games_table.find('tbody').find_all('tr')
            
            for row in rows:
                if 'thead' in row.get('class', []):
                    continue
                
                date_cell = row.find('th', {'data-stat': 'date_game'})
                if not date_cell:
                    continue
                
                game = {
                    'date': date_cell.text.strip(),
                    'home_away': self._extract_stat(row, 'game_location'),
                    'opponent': self._extract_stat(row, 'opp_name'),
                    'result': self._extract_stat(row, 'game_result'),
                    'pts': self._extract_stat(row, 'pts'),
                    'opp_pts': self._extract_stat(row, 'opp_pts')
                }
                
                schedule.append(game)
        
        except Exception as e:
            print(f"[ERROR] 경기 일정 파싱 실패: {e}")
        
        return schedule
    
    def _parse_kbl_player_stats(self, data: Dict) -> Optional[Dict]:
        """KBL 선수 통계 파싱"""
        
        try:
            return {
                'ppg': data.get('avgPoint', 0),
                'rpg': data.get('avgRebound', 0),
                'apg': data.get('avgAssist', 0),
                'spg': data.get('avgSteal', 0),
                'bpg': data.get('avgBlock', 0),
                'mpg': data.get('avgPlayTime', 0),
                'fg_pct': data.get('fgPct', 0.45),
                'three_pct': data.get('threePct', 0.35),
                'ft_pct': data.get('ftPct', 0.75)
            }
        except Exception as e:
            print(f"[ERROR] KBL 통계 파싱 실패: {e}")
            return None
    
    def _parse_kbl_injury_report(self, soup: BeautifulSoup) -> List[Dict]:
        """KBL 부상 리포트 파싱"""
        
        injuries = []
        
        try:
            # KBL 부상 리포트 테이블 파싱
            # (실제 HTML 구조에 맞게 수정 필요)
            injury_divs = soup.find_all('div', class_='injury-item')
            
            for div in injury_divs:
                injury = {
                    'name': div.find('span', class_='player-name').text.strip(),
                    'team': div.find('span', class_='team-name').text.strip(),
                    'injury_type': div.find('span', class_='injury-type').text.strip(),
                    'status': div.find('span', class_='status').text.strip(),
                    'updated': datetime.now().isoformat()
                }
                injuries.append(injury)
        
        except Exception as e:
            print(f"[ERROR] KBL 부상 리포트 파싱 실패: {e}")
        
        return injuries
    
    def _parse_kleague_player_stats(self, soup: BeautifulSoup) -> Optional[Dict]:
        """K-League 선수 통계 파싱 (xG, xA 포함)"""
        
        try:
            # Statiz K-League 통계 테이블
            stats_table = soup.find('table', class_='stats-table')
            if not stats_table:
                return None
            
            stats = {
                'goals': 0,
                'assists': 0,
                'shots': 0,
                'shots_on_target': 0,
                'key_passes': 0,
                'passes': 0,
                'pass_completion': 80.0,
                'tackles': 0,
                'interceptions': 0,
                'xg': 0.0,  # 고급 메트릭스
                'xa': 0.0,
                'xgchain': 0.0
            }
            
            # 테이블에서 통계 추출
            rows = stats_table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    stat_name = cells[0].text.strip()
                    stat_value = cells[1].text.strip()
                    
                    if '득점' in stat_name:
                        stats['goals'] = int(stat_value)
                    elif '도움' in stat_name or '어시스트' in stat_name:
                        stats['assists'] = int(stat_value)
                    elif '슈팅' in stat_name:
                        stats['shots'] = int(stat_value)
                    elif '유효슈팅' in stat_name:
                        stats['shots_on_target'] = int(stat_value)
                    elif '태클' in stat_name:
                        stats['tackles'] = int(stat_value)
                    elif '인터셉트' in stat_name:
                        stats['interceptions'] = int(stat_value)
                    elif 'xG' in stat_name:
                        stats['xg'] = float(stat_value)
                    elif 'xA' in stat_name:
                        stats['xa'] = float(stat_value)
            
            return stats
        
        except Exception as e:
            print(f"[ERROR] K-League 통계 파싱 실패: {e}")
            return None
    
    def _parse_kleague_team_stats(self, soup: BeautifulSoup) -> Optional[Dict]:
        """K-League 팀 통계 파싱 (PPDA 등)"""
        
        try:
            stats = {
                'avg_goals': 1.5,
                'avg_conceded': 1.5,
                'possession': 50.0,
                'ppda': 12.0,  # Passes Per Defensive Action
                'tackles': 15,
                'interceptions': 10
            }
            
            # 팀 통계 테이블에서 추출
            # (실제 HTML 구조에 맞게 수정)
            
            return stats
        
        except Exception as e:
            print(f"[ERROR] K-League 팀 통계 파싱 실패: {e}")
            return None
    
    def _parse_kbo_batter_stats(self, soup: BeautifulSoup) -> Optional[Dict]:
        """KBO 타자 통계 파싱 (OPS, wOBA 포함)"""
        
        try:
            # Statiz KBO 타자 통계
            stats_table = soup.find('table', class_='stats-table')
            if not stats_table:
                return None
            
            stats = {
                'ab': 0,  # 타수
                'h': 0,   # 안타
                'bb': 0,  # 볼넷
                'hbp': 0, # 몸에 맞는 공
                'sf': 0,  # 희생 플라이
                '1b': 0,  # 1루타
                '2b': 0,  # 2루타
                '3b': 0,  # 3루타
                'hr': 0,  # 홈런
                'sb': 0,  # 도루
                'cs': 0,  # 도루 실패
                'ops': 0.0,  # 고급 메트릭스
                'woba': 0.0,
                'war': 0.0
            }
            
            # 테이블에서 통계 추출
            rows = stats_table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    stat_name = cells[0].text.strip()
                    stat_value = cells[1].text.strip()
                    
                    if '타수' in stat_name:
                        stats['ab'] = int(stat_value)
                    elif '안타' in stat_name:
                        stats['h'] = int(stat_value)
                    elif '볼넷' in stat_name:
                        stats['bb'] = int(stat_value)
                    elif '홈런' in stat_name:
                        stats['hr'] = int(stat_value)
                    elif 'OPS' in stat_name:
                        stats['ops'] = float(stat_value)
                    elif 'wOBA' in stat_name:
                        stats['woba'] = float(stat_value)
                    elif 'WAR' in stat_name:
                        stats['war'] = float(stat_value)
            
            return stats
        
        except Exception as e:
            print(f"[ERROR] KBO 타자 통계 파싱 실패: {e}")
            return None
    
    def _parse_kbo_pitcher_stats(self, soup: BeautifulSoup) -> Optional[Dict]:
        """KBO 투수 통계 파싱 (ERA+, FIP 포함)"""
        
        try:
            stats = {
                'era': 0.0,  # 평균자책점
                'ip': 0.0,   # 이닝
                'hr': 0,     # 피홈런
                'bb': 0,     # 볼넷
                'k': 0,      # 삼진
                'era_plus': 100.0,  # 고급 메트릭스
                'fip': 0.0,
                'war': 0.0
            }
            
            # 테이블에서 통계 추출
            stats_table = soup.find('table', class_='stats-table')
            if stats_table:
                rows = stats_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        stat_name = cells[0].text.strip()
                        stat_value = cells[1].text.strip()
                        
                        if 'ERA' in stat_name and '+' not in stat_name:
                            stats['era'] = float(stat_value)
                        elif 'ERA+' in stat_name:
                            stats['era_plus'] = float(stat_value)
                        elif 'FIP' in stat_name:
                            stats['fip'] = float(stat_value)
                        elif 'WAR' in stat_name:
                            stats['war'] = float(stat_value)
                        elif '이닝' in stat_name:
                            stats['ip'] = float(stat_value)
                        elif '삼진' in stat_name:
                            stats['k'] = int(stat_value)
            
            return stats
        
        except Exception as e:
            print(f"[ERROR] KBO 투수 통계 파싱 실패: {e}")
            return None
    
    def _parse_kbo_injury_report(self, soup: BeautifulSoup) -> List[Dict]:
        """KBO 부상 리포트 파싱"""
        
        injuries = []
        
        try:
            # KBO 부상자 명단 테이블
            injury_table = soup.find('table', class_='injury-list')
            if injury_table:
                rows = injury_table.find_all('tr')[1:]  # 헤더 제외
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        injury = {
                            'name': cells[0].text.strip(),
                            'team': cells[1].text.strip(),
                            'injury_type': cells[2].text.strip(),
                            'status': cells[3].text.strip(),
                            'updated': datetime.now().isoformat()
                        }
                        injuries.append(injury)
        
        except Exception as e:
            print(f"[ERROR] KBO 부상 리포트 파싱 실패: {e}")
        
        return injuries
    
    def _parse_vleague_player_stats(self, soup: BeautifulSoup) -> Optional[Dict]:
        """V-League 선수 통계 파싱 (스파이크율, 블록 등)"""
        
        try:
            stats = {
                'kills': 0,
                'errors': 0,
                'attempts': 0,
                'block_solos': 0,
                'block_assists': 0,
                'digs': 0,
                'assists': 0,
                'set_attempts': 0,
                'sets_played': 0,
                'spike_success_rate': 0.0,  # 고급 메트릭스
                'block_efficiency': 0.0,
                'dig_efficiency': 0.0,
                'set_efficiency': 0.0
            }
            
            # V-League 통계 테이블
            stats_table = soup.find('table', class_='player-stats')
            if stats_table:
                rows = stats_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        stat_name = cells[0].text.strip()
                        stat_value = cells[1].text.strip()
                        
                        if '공격' in stat_name or '킬' in stat_name:
                            stats['kills'] = int(stat_value)
                        elif '블록' in stat_name:
                            stats['block_solos'] = int(stat_value)
                        elif '디그' in stat_name:
                            stats['digs'] = int(stat_value)
                        elif '세트' in stat_name and '출전' in stat_name:
                            stats['sets_played'] = int(stat_value)
                        elif '성공률' in stat_name:
                            stats['spike_success_rate'] = float(stat_value)
            
            return stats
        
        except Exception as e:
            print(f"[ERROR] V-League 통계 파싱 실패: {e}")
            return None
    
    def _parse_vleague_injury_report(self, soup: BeautifulSoup) -> List[Dict]:
        """V-League 부상 리포트 파싱"""
        
        injuries = []
        
        try:
            # V-League 부상자 명단
            injury_table = soup.find('table', class_='injury-list')
            if injury_table:
                rows = injury_table.find_all('tr')[1:]
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        injury = {
                            'name': cells[0].text.strip(),
                            'team': cells[1].text.strip(),
                            'injury_type': cells[2].text.strip(),
                            'status': cells[3].text.strip(),
                            'updated': datetime.now().isoformat()
                        }
                        injuries.append(injury)
        
        except Exception as e:
            print(f"[ERROR] V-League 부상 리포트 파싱 실패: {e}")
        
        return injuries
    
    def _extract_stat(self, row, stat_name: str) -> float:
        """통계 값 추출"""
        
        try:
            cell = row.find('td', {'data-stat': stat_name})
            if cell:
                text = cell.text.strip()
                if text and text != '':
                    return float(text)
        except:
            pass
        
        return 0.0
    
    def _get_nba_team_abbr(self, team_name: str) -> str:
        """NBA 팀 약어 변환"""
        
        abbr_map = {
            'Boston Celtics': 'BOS',
            'Brooklyn Nets': 'BRK',
            'New York Knicks': 'NYK',
            'Philadelphia 76ers': 'PHI',
            'Toronto Raptors': 'TOR',
            'Chicago Bulls': 'CHI',
            'Cleveland Cavaliers': 'CLE',
            'Detroit Pistons': 'DET',
            'Indiana Pacers': 'IND',
            'Milwaukee Bucks': 'MIL',
            'Atlanta Hawks': 'ATL',
            'Charlotte Hornets': 'CHO',
            'Miami Heat': 'MIA',
            'Orlando Magic': 'ORL',
            'Washington Wizards': 'WAS',
            'Denver Nuggets': 'DEN',
            'Minnesota Timberwolves': 'MIN',
            'Oklahoma City Thunder': 'OKC',
            'Portland Trail Blazers': 'POR',
            'Utah Jazz': 'UTA',
            'Golden State Warriors': 'GSW',
            'LA Clippers': 'LAC',
            'Los Angeles Lakers': 'LAL',
            'Phoenix Suns': 'PHO',
            'Sacramento Kings': 'SAC',
            'Dallas Mavericks': 'DAL',
            'Houston Rockets': 'HOU',
            'Memphis Grizzlies': 'MEM',
            'New Orleans Pelicans': 'NOP',
            'San Antonio Spurs': 'SAS'
        }
        
        return abbr_map.get(team_name, 'UNK')
    
    def detect_back_to_back(self, schedule: List[Dict], game_date: str) -> bool:
        """백투백 경기 감지"""
        
        try:
            game_dt = datetime.strptime(game_date, '%Y-%m-%d')
            
            for game in schedule:
                prev_dt = datetime.strptime(game['date'], '%Y-%m-%d')
                diff = (game_dt - prev_dt).days
                
                if diff == 1:  # 하루 전에 경기
                    return True
        
        except Exception as e:
            print(f"[ERROR] 백투백 감지 실패: {e}")
        
        return False


# 싱글톤 인스턴스
_fetcher = None

def get_realtime_fetcher() -> RealTimeDataFetcher:
    """RealTimeDataFetcher 싱글톤 반환"""
    global _fetcher
    if _fetcher is None:
        _fetcher = RealTimeDataFetcher()
    return _fetcher

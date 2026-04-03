"""
데이터 수집 모듈
- 팀 통계, 선수 데이터, 경기 기록 수집
- 웹 크롤링 및 API 연동
- 선수 고급 메트릭스 통합
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
from modules.player_data_loader import get_player_loader


class DataCollector:
    def __init__(self, sport, league):
        self.sport = sport
        self.league = league
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 캐시 데이터 - 초기화
        self.teams_cache = {}
        self.players_cache = {}
        self.matches_cache = {}
        
        # 캐시 타임스탬프 추적
        self.cache_timestamps = {}
        self.cache_duration = 3600  # 1시간 (초 단위)
        
        # 디버그 모드
        self.debug = False
        
        # 선수 데이터 로더
        self.player_loader = get_player_loader()
    
    def clear_cache(self):
        """캐시 초기화"""
        self.teams_cache = {}
        self.players_cache = {}
        self.matches_cache = {}
        self.cache_timestamps = {}
        if self.debug:
            print("[REFRESH] 캐시 초기화 완료")
    
    def _is_cache_expired(self, cache_key: str) -> bool:
        """캐시가 만료되었는지 확인"""
        if cache_key not in self.cache_timestamps:
            return True
        
        import time
        elapsed = time.time() - self.cache_timestamps[cache_key]
        return elapsed > self.cache_duration
    
    def _update_cache_timestamp(self, cache_key: str):
        """캐시 타임스탬프 업데이트"""
        import time
        self.cache_timestamps[cache_key] = time.time()
    
    def get_teams(self):
        """리그의 모든 팀 목록 반환"""
        if self.league in self.teams_cache:
            return self.teams_cache[self.league]
        
        # 실제 2025-26 시즌 데이터 사용
        try:
            import sys
            from pathlib import Path
            data_path = Path(__file__).parent.parent / "data"
            if str(data_path) not in sys.path:
                sys.path.insert(0, str(data_path))
            
            from real_data_2026 import get_league_data
            
            league_data = get_league_data(self.league)
            if league_data:
                teams = list(league_data.keys())
                self.teams_cache[self.league] = teams
                if self.debug:
                    print(f"[OK] {self.league} 팀 목록 로드: {len(teams)}개 팀")
                return teams
        except Exception as e:
            if self.debug:
                print(f"[WARNING] {self.league} 팀 목록 로드 실패: {e}")
                import traceback
                traceback.print_exc()
        
        # 리그별 팀 목록 (실제 2025-26 시즌)
        teams_data = {
            "La Liga": ["Barcelona", "Real Madrid", "Atletico Madrid", "Villarreal", "Real Betis", 
                       "Celta Vigo", "Real Sociedad", "Espanyol", "Getafe", "Athletic Bilbao"],
            "Bundesliga": ["Bayern Munich", "Borussia Dortmund", "TSG Hoffenheim", "VfB Stuttgart", 
                          "RB Leipzig", "Bayer Leverkusen", "Eintracht Frankfurt", "SC Freiburg"],
            "Serie A": ["Inter Milan", "AC Milan", "Napoli", "Como", "Juventus", "Roma", "Atalanta", "Bologna"],
            "EPL": ["Arsenal", "Manchester City", "Manchester United", "Aston Villa", "Liverpool", 
                   "Chelsea", "Brentford", "Everton", "Fulham", "Brighton", 
                   "Sunderland", "Newcastle", "Bournemouth", "Crystal Palace", "Leeds United", 
                   "Nottingham Forest", "Tottenham", "West Ham", "Burnley", "Wolves"],
            "NBA East": ["Boston Celtics", "Milwaukee Bucks", "New York Knicks", "Cleveland Cavaliers", 
                         "Orlando Magic", "Indiana Pacers", "Philadelphia 76ers", "Miami Heat", 
                         "Chicago Bulls", "Atlanta Hawks", "Brooklyn Nets", "Toronto Raptors", 
                         "Charlotte Hornets", "Washington Wizards", "Detroit Pistons"],
            "NBA West": ["Oklahoma City Thunder", "Denver Nuggets", "Minnesota Timberwolves", "LA Clippers",
                         "Dallas Mavericks", "Phoenix Suns", "New Orleans Pelicans", "Los Angeles Lakers",
                         "Sacramento Kings", "Golden State Warriors", "Houston Rockets", "Utah Jazz",
                         "Memphis Grizzlies", "San Antonio Spurs", "Portland Trail Blazers"],
            "MLB": ["New York Yankees", "Los Angeles Dodgers", "Boston Red Sox", "Houston Astros", 
                   "Atlanta Braves", "Philadelphia Phillies", "San Diego Padres", "New York Mets",
                   "Toronto Blue Jays", "Seattle Mariners", "Texas Rangers", "Tampa Bay Rays",
                   "Baltimore Orioles", "Minnesota Twins", "Cleveland Guardians", "Chicago White Sox",
                   "Detroit Tigers", "Kansas City Royals", "Los Angeles Angels", "Oakland Athletics",
                   "St. Louis Cardinals", "Milwaukee Brewers", "Chicago Cubs", "Cincinnati Reds",
                   "Pittsburgh Pirates", "Arizona Diamondbacks", "San Francisco Giants", "Colorado Rockies",
                   "Miami Marlins", "Washington Nationals"],
            "K리그1": ["서울", "울산", "전북", "대전", "부천", "광주", "안양", "김천", "인천", "강원", "포항", "제주"],
            "MLS": ["Inter Miami", "Columbus Crew", "FC Cincinnati", "Los Angeles FC",
                   "LA Galaxy", "Real Salt Lake", "Colorado Rapids", "Houston Dynamo",
                   "St. Louis City", "Minnesota United", "Portland Timbers", "Seattle Sounders",
                   "Austin FC", "Dallas FC", "Nashville SC", "New York Red Bulls",
                   "New York City FC", "Philadelphia Union", "Atlanta United", "Charlotte FC",
                   "Chicago Fire", "D.C. United", "CF Montréal", "New England Revolution",
                   "Orlando City", "Toronto FC", "Vancouver Whitecaps", "San Jose Earthquakes",
                   "Sporting Kansas City"],
            "KBO": ["KIA", "SSG", "LG", "두산", "KT", "롯데", "삼성", "NC", "한화", "키움"],
            "KBL": ["MOBIS", "SK", "KT", "LG", "JKJ", "SONO", "KOGAS", "DB", "SAMSUNG", "KCC"],
            "V-리그 남자": ["대한항공", "현대캐피탈", "삼성화재", "OK금융그룹", "한국전력", "우리카드", "KB손해보험"],
            "V-리그 여자": ["흥국생명", "현대건설", "GS칼텍스", "한국도로공사", "정관장", "IBK기업은행", "페퍼저축은행"],
        }
        
        teams = teams_data.get(self.league, ["팀A", "팀B", "팀C", "팀D"])
        self.teams_cache[self.league] = teams
        return teams
    
    def get_team_data(self, team_name):
        """팀의 상세 데이터 수집 - 실시간 데이터 우선, 실패 시 로컬 데이터"""
        cache_key = f"{self.league}_{team_name}"
        
        if cache_key in self.teams_cache:
            cached_data = self.teams_cache[cache_key]
            # 10분(600초) TTL 적용
            cache_time = cached_data.get('_cache_time', 0)
            if time.time() - cache_time < 600:
                return cached_data
            else:
                if self.debug:
                    print(f"[INFO] {team_name} 캐시 만료 (10분 경과) - 재수집 진행")
        
        # KBL 전용 독립 데이터 파이프라인 (웹 스크래핑 기반)
        real_stats = None
        if self.league == "KBL":
            try:
                if not hasattr(self, 'kbl_fetcher'):
                    from modules.kbl_data_fetcher import KBLDataFetcher
                    self.kbl_fetcher = KBLDataFetcher()
                    self.kbl_dataset = self.kbl_fetcher.build_team_dataset()
                
                if hasattr(self, 'kbl_dataset'):
                    norm_name = self.kbl_fetcher.normalize_team(team_name)
                    if norm_name in self.kbl_dataset:
                        real_stats = self.kbl_dataset[norm_name].copy()
                        if self.debug:
                            print(f"[OK] {team_name} (norm: {norm_name}) KBL 크롤러 데이터 로드 성공")
            except Exception as e:
                if self.debug: print(f"[WARNING] KBL 크롤러 연동 실패: {e}")
        
        # 1차 시도: 실시간 데이터 수집 (KBL이 아닌 경우 혹은 실패한 경우)
        if not real_stats:
            try:
                from modules.live_data_fetcher import get_live_fetcher
                
                live_fetcher = get_live_fetcher()
                real_stats = live_fetcher.fetch_team_stats(self.league, team_name)
                
                if real_stats and 'wins' in real_stats:
                    if self.debug:
                        print(f"[OK] {team_name} 실시간 데이터 로드 성공")
            except Exception as e:
                if self.debug:
                    print(f"[WARNING] {team_name} 실시간 데이터 수집 실패: {e}")
        
        # 2차 시도: 로컬 데이터 로드
        if not real_stats:
            try:
                import sys
                from pathlib import Path
                data_path = Path(__file__).parent.parent / "data"
                if str(data_path) not in sys.path:
                    sys.path.insert(0, str(data_path))
                
                from real_data_2026 import get_team_stats
                
                real_stats = get_team_stats(self.league, team_name)
                
                if real_stats and self.debug:
                    print(f"[OK] {team_name} 로컬 데이터 로드 성공")
            except Exception as e:
                if self.debug:
                    print(f"[WARNING] {team_name} 로컬 데이터 로드 실패: {e}")
                    import traceback
                    traceback.print_exc()
        
        # 데이터 처리
        if real_stats:
            # 선수 능력치 집계
            players = self.get_players(team_name)
            player_ratings = []
            player_conditions = []
            star_ppg_list = []
            
            for player_name in players[:15]:  # 주전 15명
                player_data = self.get_player_data(player_name, team_name)
                if player_data:
                    player_ratings.append(player_data.get('rating_avg', 7.0))
                    player_conditions.append(player_data.get('condition', 80))
                    if 'ppg' in player_data:
                        star_ppg_list.append(player_data['ppg'])
            
            avg_player_rating = np.mean(player_ratings) if player_ratings else 7.0
            avg_player_condition = np.mean(player_conditions) if player_conditions else 80
            
            star_ppg_list.sort(reverse=True)
            star_power_ppg = sum(star_ppg_list[:3]) if star_ppg_list else 0
            
            # 실제 데이터를 시스템 형식으로 변환
            # MLB 데이터 먼저 확인 (runs_for/runs_against 사용)
            if 'runs_for' in real_stats:
                total_games = real_stats['wins'] + real_stats['losses']
                avg_runs_for = real_stats['runs_for'] / total_games if total_games > 0 else 0
                avg_runs_against = real_stats['runs_against'] / total_games if total_games > 0 else 0
                
                data = {
                    'team_name': team_name,
                    'recent_winrate': real_stats.get('win_pct', real_stats['wins'] / total_games if total_games > 0 else 0),
                    'home_winrate': real_stats.get('win_pct', real_stats['wins'] / total_games if total_games > 0 else 0) * 1.1,
                    'away_winrate': real_stats.get('win_pct', real_stats['wins'] / total_games if total_games > 0 else 0) * 0.9,
                    'avg_goals': avg_runs_for,  # 야구는 runs를 goals로 매핑
                    'avg_conceded': avg_runs_against,
                    'recent_form': real_stats.get('form', ['W', 'W', 'L', 'W', 'W']),
                    'possession_avg': 50,
                    'shots_avg': avg_runs_for * 2,  # 야구는 안타 수 추정
                    'pass_accuracy': 80,
                    'recent_matches': self._generate_recent_matches(team_name, 10),
                    'real_data': True,
                    'wins': real_stats['wins'],
                    'losses': real_stats['losses'],
                    'runs_for': real_stats['runs_for'],
                    'runs_against': real_stats['runs_against'],
                    # 선수 능력치 추가
                    'avg_player_rating': avg_player_rating,
                    'avg_player_condition': avg_player_condition,
                    'squad_depth': len(players)
                }
            
            elif 'played' in real_stats and 'goals_for' in real_stats:  # 축구 데이터
                total_matches = real_stats['played']
                wins = real_stats['wins']
                draws = real_stats.get('draws', 0)
                losses = real_stats['losses']
                
                data = {
                    'team_name': team_name,
                    'recent_winrate': wins / total_matches if total_matches > 0 else 0,
                    'home_winrate': (wins / total_matches * 1.15) if total_matches > 0 else 0,
                    'away_winrate': (wins / total_matches * 0.85) if total_matches > 0 else 0,
                    'avg_goals': real_stats['goals_for'] / total_matches,
                    'avg_conceded': real_stats['goals_against'] / total_matches,
                    'xg': real_stats.get('xg', real_stats['goals_for'] / total_matches),
                    'xga': real_stats.get('xga', real_stats['goals_against'] / total_matches),
                    'ppda': real_stats.get('ppda', 12.0),
                    'travel_distance': real_stats.get('travel_distance', 0) if self.league == "MLS" else 0,
                    'recent_form': real_stats.get('form', ['W', 'W', 'W', 'D', 'L']),
                    'possession_avg': real_stats.get('possession', 50 + (real_stats['points'] / total_matches - 1.5) * 5),
                    'shots_avg': real_stats['goals_for'] / total_matches * 5,
                    'pass_accuracy': 75 + (real_stats['points'] / total_matches - 1) * 5,
                    'recent_matches': self._generate_recent_matches_from_real(real_stats),
                    'real_data': True,
                    'position': real_stats.get('position', 10),
                    'points': real_stats.get('points', 0),
                    'rank': real_stats.get('position', 10),
                    # 선수 능력치 추가
                    'avg_player_rating': avg_player_rating,
                    'avg_player_condition': avg_player_condition,
                    'squad_depth': len(players)
                }
                
            elif 'wins' in real_stats and 'losses' in real_stats:  # NBA/KBL/배구 데이터
                total_games = real_stats['wins'] + real_stats['losses']
                
                # 배구 데이터 처리 (경기당 평균 세트 수 계산)
                if 'sets_won' in real_stats:
                    avg_sets_won = real_stats['sets_won'] / total_games if total_games > 0 else 1.5
                    avg_sets_lost = real_stats['sets_lost'] / total_games if total_games > 0 else 1.5
                else:
                    # NBA/KBL 데이터
                    avg_sets_won = real_stats.get('ppg', 0)
                    avg_sets_lost = real_stats.get('opp_ppg', 0)
                
                # NBA/KBL/배구 데이터 처리
                data = {
                    'team_name': team_name,
                    'recent_winrate': real_stats.get('win_pct', real_stats['wins'] / total_games if total_games > 0 else 0),
                    'home_winrate': real_stats.get('win_pct', real_stats['wins'] / total_games if total_games > 0 else 0) * 1.1,
                    'away_winrate': real_stats.get('win_pct', real_stats['wins'] / total_games if total_games > 0 else 0) * 0.9,
                    'avg_goals': avg_sets_won,
                    'avg_conceded': avg_sets_lost,
                    'ppg': real_stats.get('ppg', avg_sets_won),  # NBA 평균 득점
                    'opp_ppg': real_stats.get('opp_ppg', avg_sets_lost),  # NBA 평균 실점
                    'recent_form': real_stats.get('form', ['W', 'W', 'L', 'W', 'W']),
                    'possession_avg': 50,
                    'shots_avg': avg_sets_won / 2 if avg_sets_won > 0 else 0,
                    'pass_accuracy': 80,
                    'recent_matches': self._generate_recent_matches(team_name, 10),
                    'real_data': True,
                    'wins': real_stats['wins'],
                    'losses': real_stats['losses'],
                    'home': real_stats.get('home', '0-0'),  # 홈 전적
                    'away': real_stats.get('away', '0-0'),  # 원정 전적
                    'diff': real_stats.get('diff', 0),  # 득실차
                    'rank': real_stats.get('rank', real_stats.get('position', 0)),  # 순위
                    'avg_points': real_stats.get('avg_points', avg_sets_won),
                    'avg_allowed': real_stats.get('avg_allowed', avg_sets_lost),
                    'win_pct': real_stats.get('win_pct', real_stats['wins'] / total_games if total_games > 0 else 0),
                    # 최근 10경기 및 스트레이크 정보 반영
                    'last_10': real_stats.get('last_10', f"{sum(1 for r in real_stats.get('form', [])[:10] if r == 'W')}-{sum(1 for r in real_stats.get('form', [])[:10] if r == 'L')}"),
                    'streak': real_stats.get('streak', ''),
                    'last_10_wins': 0,
                    'last_10_losses': 0,
                    # ... 아래에서 파싱함
                }
                
                # last_10 문자열 파싱 (예: "8-2")
                if 'last_10' in data and '-' in data['last_10']:
                    try:
                        w, l = map(int, data['last_10'].split('-'))
                        data['last_10_wins'] = w
                        data['last_10_losses'] = l
                    except:
                        data['last_10_wins'] = sum(1 for r in real_stats.get('form', [])[:10] if r == 'W')
                        data['last_10_losses'] = sum(1 for r in real_stats.get('form', [])[:10] if r == 'L')
                else:
                    data['last_10_wins'] = sum(1 for r in real_stats.get('form', [])[:10] if r == 'W')
                    data['last_10_losses'] = sum(1 for r in real_stats.get('form', [])[:10] if r == 'L')

                data.update({
                    # 캐시 시간 기록
                    '_cache_time': time.time(),
                    # 선수 능력치 추가
                    'avg_player_rating': avg_player_rating,
                    'avg_player_condition': avg_player_condition,
                    'star_power_ppg': star_power_ppg,
                    'squad_depth': len(players)
                })
                
                # 배구 추가 정보
                if 'sets_won' in real_stats:
                    data['sets_won'] = real_stats['sets_won']
                    data['sets_lost'] = real_stats['sets_lost']
            
            self.teams_cache[cache_key] = data
            if self.debug:
                print(f"FINAL DATA for {team_name}:", data)
            return data
        
        # 실제 데이터 없으면 시뮬레이션 데이터 생성
        recent_matches = self._generate_recent_matches(team_name, 10)
        
        total_matches = len(recent_matches)
        wins = sum(1 for m in recent_matches if m['result'] == 'W')
        draws = sum(1 for m in recent_matches if m['result'] == 'D')
        
        home_matches = [m for m in recent_matches if m['home']]
        home_wins = sum(1 for m in home_matches if m['result'] == 'W')
        
        away_matches = [m for m in recent_matches if not m['home']]
        away_wins = sum(1 for m in away_matches if m['result'] == 'W')
        
        data = {
            'team_name': team_name,
            'recent_winrate': wins / total_matches if total_matches > 0 else 0,
            'home_winrate': home_wins / len(home_matches) if home_matches else 0,
            'away_winrate': away_wins / len(away_matches) if away_matches else 0,
            'avg_goals': np.mean([m['goals_for'] for m in recent_matches]),
            'avg_conceded': np.mean([m['goals_against'] for m in recent_matches]),
            'recent_form': [m['result'] for m in recent_matches[:5]],
            'possession_avg': np.random.uniform(45, 60),
            'shots_avg': np.random.uniform(10, 20),
            'pass_accuracy': np.random.uniform(75, 90),
            'recent_matches': recent_matches,
            'real_data': False,
            'avg_player_rating': 7.0,
            'avg_player_condition': 80,
            'squad_depth': 20
        }
        
        self.teams_cache[cache_key] = data
        return data
    
    def _generate_recent_matches_from_real(self, real_stats):
        """실제 통계에서 최근 경기 생성"""
        matches = []
        form = real_stats.get('form', ['W', 'W', 'D', 'L', 'W'])
        
        for i, result in enumerate(form):
            if result == 'W':
                goals_for = np.random.randint(2, 5)
                goals_against = np.random.randint(0, 2)
            elif result == 'D':
                goals = np.random.randint(1, 3)
                goals_for = goals_against = goals
            else:  # L
                goals_against = np.random.randint(2, 5)
                goals_for = np.random.randint(0, 2)
            
            matches.append({
                'date': datetime.now() - timedelta(days=7*i),
                'opponent': f"상대팀{i}",
                'home': i % 2 == 0,
                'result': result,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'possession': np.random.uniform(40, 65),
                'shots': np.random.randint(8, 25),
                'shots_on_target': np.random.randint(3, 12)
            })
        
        return matches
    
    def _generate_recent_matches(self, team_name, count=10):
        """최근 경기 데이터 생성 (시뮬레이션) - 종목별 점수 범위"""
        matches = []
        results = ['W', 'D', 'L']
        weights = [0.4, 0.3, 0.3]  # 승/무/패 확률
        
        # 종목별 점수 범위 설정
        if self.sport == 'basketball':
            # 농구: 80-120점
            score_range = (80, 120)
            score_diff_range = (5, 20)
        elif self.sport == 'baseball':
            # 야구: 0-10점
            score_range = (0, 10)
            score_diff_range = (1, 5)
        elif self.sport == 'volleyball':
            # 배구: 세트 수 (0-3)
            score_range = (0, 3)
            score_diff_range = (0, 2)
        else:
            # 축구: 0-5골
            score_range = (0, 5)
            score_diff_range = (1, 3)
        
        for i in range(count):
            result = np.random.choice(results, p=weights)
            
            if self.sport == 'basketball':
                # 농구는 무승부 없음
                if result == 'D':
                    result = 'W'
                
                if result == 'W':
                    goals_for = np.random.randint(score_range[0] + 10, score_range[1])
                    goals_against = np.random.randint(score_range[0], goals_for - 5)
                else:
                    goals_against = np.random.randint(score_range[0] + 10, score_range[1])
                    goals_for = np.random.randint(score_range[0], goals_against - 5)
            
            elif self.sport == 'baseball' or self.sport == 'volleyball':
                # 야구/배구는 무승부 없음
                if result == 'D':
                    result = 'W'
                
                if result == 'W':
                    goals_for = np.random.randint(score_range[0] + 2, score_range[1])
                    goals_against = np.random.randint(score_range[0], goals_for)
                else:
                    goals_against = np.random.randint(score_range[0] + 2, score_range[1])
                    goals_for = np.random.randint(score_range[0], goals_against)
            
            else:
                # 축구
                if result == 'W':
                    goals_for = np.random.randint(1, 5)
                    goals_against = np.random.randint(0, goals_for)
                elif result == 'D':
                    goals = np.random.randint(0, 4)
                    goals_for = goals_against = goals
                else:
                    goals_against = np.random.randint(1, 5)
                    goals_for = np.random.randint(0, goals_against)
            
            matches.append({
                'date': datetime.now() - timedelta(days=7*i),
                'opponent': f"상대팀{i}",
                'home': np.random.choice([True, False]),
                'result': result,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'possession': np.random.uniform(40, 65),
                'shots': np.random.randint(8, 25),
                'shots_on_target': np.random.randint(3, 12)
            })
        
        return matches
    
    def validate_players(self, players):
        """데이터 무결성 검증 - 가짜 데이터 방지"""
        if players is None:
            return []
        if not isinstance(players, list):
            return []
        if len(players) == 0:
            return []
        return players

    def get_players(self, team_name):
        """팀의 선수 목록 반환 - RosterFetcher 우선, 실패 시 로컬 데이터"""
        if self.league == "MLS":
            use_player_data = False
        else:
            use_player_data = True
            
        if not use_player_data:
            if self.debug:
                print(f"[WARNING] No player data available for MLS - {team_name}")
            return []
            

        cache_key = f"players_{self.league}_{team_name}"
        
        # 캐시 만료 확인 (1시간)
        if cache_key in self.players_cache and not self._is_cache_expired(cache_key):
            if self.debug:
                print(f"[OK] {team_name} 선수 캐시 사용 (유효)")
            # 중요: 캐시에서 반환할 때도 deep copy!
            import copy
            return copy.deepcopy(self.players_cache[cache_key])
        
        if self.debug:
            print(f"[SEARCH] {team_name} 선수 데이터 로드 시도... (캐시 만료 또는 없음)")
        
        # 1. RosterFetcher로 실시간 선수 데이터 가져오기 시도
        try:
            from modules.roster_fetcher import RosterFetcher
            
            if self.debug:
                print(f"[FETCH] RosterFetcher로 {team_name} 선수 데이터 가져오는 중...")
            
            # NBA East/West는 NBA로 통합하여 RosterFetcher에 전달
            fetch_league = "NBA" if self.league.startswith("NBA") else self.league
            fetcher = RosterFetcher(league=fetch_league)
            real_players = fetcher.fetch_team_roster(team_name)
            
            if real_players and len(real_players) > 0:
                # 선수들을 rating 기준으로 내림차순 정렬 (최고 스탯 선수가 UI 먼저 노출되도록)
                real_players.sort(key=lambda x: x.get('rating', 0), reverse=True)
                player_names = [f"{p['name']} ({p['position']})" for p in real_players]
                # 중요: 캐시에 저장할 때도 deep copy!
                import copy
                self.players_cache[cache_key] = copy.deepcopy(player_names)
                self._update_cache_timestamp(cache_key)
                if self.debug:
                    print(f"[OK] {team_name} RosterFetcher 선수 {len(player_names)}명 로드 완료")
                    print(f"   첫 3명: {player_names[:3]}")
                return player_names
            else:
                if self.debug:
                    print(f"[WARNING] {team_name} RosterFetcher 데이터 없음, 로컬 데이터 시도...")
        except Exception as e:
            if self.debug:
                print(f"[WARNING] RosterFetcher 실패: {e}, 로컬 데이터 시도...")
        
        # 2. 로컬 로스터 데이터로 선수 데이터 가져오기 시도 (KBO, KBL, K리그, V리그)
        try:
            import sys
            from pathlib import Path
            
            # 데이터 경로 추가
            data_path = Path(__file__).parent.parent / "data"
            if str(data_path) not in sys.path:
                sys.path.insert(0, str(data_path))
            
            real_players = None
            
            # 리그별 로스터 데이터 로드
            if self.league == 'KBO':
                from kbo_rosters_complete_2026 import KBO_ROSTERS_2026
                import copy
                
                # 팀명 변환: "KIA 타이거즈" -> "KIA"
                short_team_name = team_name
                for key in KBO_ROSTERS_2026.keys():
                    if key in team_name:
                        short_team_name = key
                        break
                
                # 깊은 복사로 원본 데이터 보호
                real_players = copy.deepcopy(KBO_ROSTERS_2026.get(short_team_name, []))
                if self.debug:
                    print(f"[SEARCH] KBO 로스터 검색: '{team_name}' -> '{short_team_name}'")
            elif self.league == 'KBL':
                from kbl_rosters_complete_2025_26 import KBL_ROSTERS_2025_26
                import copy
                # 깊은 복사로 원본 데이터 보호
                real_players = copy.deepcopy(KBL_ROSTERS_2025_26.get(team_name, []))
                if self.debug:
                    print(f"[SEARCH] KBL 로스터 검색: '{team_name}'")
            elif self.league == 'K리그1':
                from kleague_rosters_complete_2026 import KLEAGUE_ROSTERS_2026
                import copy
                # 깊은 복사로 원본 데이터 보호
                real_players = copy.deepcopy(KLEAGUE_ROSTERS_2026.get(team_name, []))
                if self.debug:
                    print(f"[SEARCH] K리그1 로스터 검색: '{team_name}'")
            elif self.league == 'V-리그 남자':
                from vleague_rosters_complete_2025_26 import VLEAGUE_MEN_ROSTERS_2025_26
                import copy
                # 깊은 복사로 원본 데이터 보호
                real_players = copy.deepcopy(VLEAGUE_MEN_ROSTERS_2025_26.get(team_name, []))
            elif self.league == 'V-리그 여자':
                from vleague_rosters_complete_2025_26 import VLEAGUE_WOMEN_ROSTERS_2025_26
                import copy
                # 깊은 복사로 원본 데이터 보호
                real_players = copy.deepcopy(VLEAGUE_WOMEN_ROSTERS_2025_26.get(team_name, []))
            
            if real_players and len(real_players) > 0:
                player_names = [f"{p['name']} ({p['position']})" for p in real_players]
                # 중요: 캐시에 저장할 때도 deep copy!
                import copy
                self.players_cache[cache_key] = copy.deepcopy(player_names)
                self._update_cache_timestamp(cache_key)
                if self.debug:
                    print(f"[OK] {team_name} 로컬 로스터 {len(player_names)}명 로드 완료")
                    print(f"   첫 3명: {player_names[:3]}")
                return player_names
            else:
                if self.debug:
                    print(f"[WARNING] {team_name} 로컬 로스터 데이터 없음")
        except Exception as e:
            if self.debug:
                print(f"[ERROR] 로컬 로스터 데이터 로드 실패: {e}")
                import traceback
                traceback.print_exc()
        
        # 3. players_2026 모듈로 선수 데이터 가져오기 시도 (백업)
        try:
            import sys
            from pathlib import Path
            
            # 데이터 경로 추가
            data_path = Path(__file__).parent.parent / "data"
            if str(data_path) not in sys.path:
                sys.path.insert(0, str(data_path))
            
            # players_2026 모듈 임포트
            import players_2026
            
            # 모듈 리로드 (캐시 방지)
            import importlib
            importlib.reload(players_2026)
            
            real_players = players_2026.get_team_players(self.league, team_name)
            
            if real_players and len(real_players) > 0:
                player_names = [f"{p['name']} ({p['position']})" for p in real_players]
                # 중요: 캐시에 저장할 때도 deep copy!
                import copy
                self.players_cache[cache_key] = copy.deepcopy(player_names)
                self._update_cache_timestamp(cache_key)
                if self.debug:
                    print(f"[OK] {team_name} players_2026 선수 {len(player_names)}명 로드 완료")
                    print(f"   첫 3명: {player_names[:3]}")
                return player_names
            else:
                if self.debug:
                    print(f"[WARNING] {team_name} players_2026 선수 데이터 없음 (빈 리스트)")
        except Exception as e:
            if self.debug:
                print(f"[ERROR] players_2026 선수 데이터 로드 실패: {e}")
                import traceback
                traceback.print_exc()
        
        # 4. 데이터가 없는 경우 빈 리스트 반환 (가짜 데이터 생성 금지)
        if self.debug:
            print(f"[WARNING] No player data available for {self.league} - {team_name}")
        
        players = []
        players = self.validate_players(players)
        
        # 중요: 캐시에 저장할 때도 deep copy!
        import copy
        self.players_cache[cache_key] = copy.deepcopy(players)
        self._update_cache_timestamp(cache_key)
        return players
    
    def get_player_data(self, player_name, team_name):
        """선수 상세 데이터 - RosterFetcher 우선, 실패 시 로컬 데이터"""
        # 괄호 안의 포지션 제거
        clean_name = player_name.split(' (')[0] if '(' in player_name else player_name
        
        # 1. RosterFetcher로 실시간 선수 데이터 가져오기 시도
        try:
            from modules.roster_fetcher import RosterFetcher
            
            fetcher = RosterFetcher(league=self.league)
            real_player = fetcher.get_player_info(clean_name, team_name)
            
            if real_player:
                if self.debug:
                    print(f"[OK] {clean_name} RosterFetcher 데이터 로드 완료")
                # 실제 데이터를 시스템 형식으로 변환
                if 'ppg' in real_player:  # NBA 선수
                    return {
                        'name': real_player['name'],
                        'team': team_name,
                        'age': real_player.get('age', 25),
                        'position': real_player['position'],
                        'matches_played': 69,  # NBA 시즌 진행 중
                        'minutes_played': 2400,
                        'goals': int(real_player.get('ppg', 0)),  # PPG를 goals로
                        'assists': int(real_player.get('apg', 0)),
                        'yellow_cards': 0,
                        'red_cards': 0,
                        'rating_avg': real_player.get('rating', 7.0),
                        'condition': 85 + np.random.uniform(-10, 10),
                        'injury_status': '정상',
                        'fatigue_level': 30 + np.random.uniform(-10, 20),
                        'real_data': True,
                        'ppg': real_player.get('ppg', 0),
                        'rpg': real_player.get('rpg', 0),
                        'apg': real_player.get('apg', 0)
                    }
                elif 'avg' in real_player:  # MLB 선수
                    return {
                        'name': real_player['name'],
                        'team': team_name,
                        'age': real_player.get('age', 25),
                        'position': real_player['position'],
                        'matches_played': 140,  # MLB 시즌 진행 중
                        'minutes_played': 0,
                        'goals': real_player.get('hr', 0),  # 홈런을 goals로
                        'assists': real_player.get('rbi', 0),  # RBI를 assists로
                        'yellow_cards': 0,
                        'red_cards': 0,
                        'rating_avg': real_player.get('rating', 7.0),
                        'condition': 85 + np.random.uniform(-10, 10),
                        'injury_status': '정상',
                        'fatigue_level': 30 + np.random.uniform(-10, 20),
                        'real_data': True,
                        'avg': real_player.get('avg', 0),
                        'hr': real_player.get('hr', 0),
                        'rbi': real_player.get('rbi', 0),
                        'era': real_player.get('era', 0)
                    }
                else:  # 축구 선수
                    return {
                        'name': real_player['name'],
                        'team': team_name,
                        'age': real_player.get('age', 25),
                        'position': real_player['position'],
                        'matches_played': 28,  # 시즌 진행 중
                        'minutes_played': 2200,
                        'goals': real_player.get('goals', 0),
                        'assists': real_player.get('assists', 0),
                        'yellow_cards': np.random.randint(0, 5),
                        'red_cards': 0,
                        'rating_avg': real_player.get('rating', 7.0),
                        'condition': 85 + np.random.uniform(-10, 10),
                        'injury_status': '정상',
                        'fatigue_level': 30 + np.random.uniform(-10, 20),
                        'real_data': True
                    }
        except Exception as e:
            if self.debug:
                print(f"[WARNING] RosterFetcher 실패 ({clean_name}): {e}")
        
        # 2. 로컬 로스터 데이터에서 선수 정보 가져오기 (KBO, KBL, K리그, V리그)
        try:
            import sys
            from pathlib import Path
            
            # 데이터 경로 추가
            data_path = Path(__file__).parent.parent / "data"
            if str(data_path) not in sys.path:
                sys.path.insert(0, str(data_path))
            
            real_player = None
            
            # 리그별 로스터 데이터에서 선수 찾기
            if self.league == 'KBO':
                from kbo_rosters_complete_2026 import KBO_ROSTERS_2026
                import copy
                # 깊은 복사로 원본 데이터 보호
                team_roster = copy.deepcopy(KBO_ROSTERS_2026.get(team_name, []))
                for player in team_roster:
                    if player['name'] == clean_name:
                        real_player = player
                        break
                if self.debug:
                    if real_player:
                        print(f"[OK] {clean_name} KBO 로스터 데이터 로드 완료")
                    else:
                        print(f"[WARNING] {clean_name} KBO 로스터에서 찾을 수 없음")
            elif self.league == 'KBL':
                from kbl_rosters_complete_2025_26 import KBL_ROSTERS_2025_26
                import copy
                # 깊은 복사로 원본 데이터 보호
                team_roster = copy.deepcopy(KBL_ROSTERS_2025_26.get(team_name, []))
                for player in team_roster:
                    if player['name'] == clean_name:
                        real_player = player
                        break
            elif self.league == 'K리그1':
                from kleague_rosters_complete_2026 import KLEAGUE_ROSTERS_2026
                import copy
                # 깊은 복사로 원본 데이터 보호
                team_roster = copy.deepcopy(KLEAGUE_ROSTERS_2026.get(team_name, []))
                for player in team_roster:
                    if player['name'] == clean_name:
                        real_player = player
                        break
            elif self.league == 'V-리그 남자':
                from vleague_rosters_complete_2025_26 import VLEAGUE_MEN_ROSTERS_2025_26
                import copy
                # 깊은 복사로 원본 데이터 보호
                team_roster = copy.deepcopy(VLEAGUE_MEN_ROSTERS_2025_26.get(team_name, []))
                for player in team_roster:
                    if player['name'] == clean_name:
                        real_player = player
                        break
            elif self.league == 'V-리그 여자':
                from vleague_rosters_complete_2025_26 import VLEAGUE_WOMEN_ROSTERS_2025_26
                import copy
                # 깊은 복사로 원본 데이터 보호
                team_roster = copy.deepcopy(VLEAGUE_WOMEN_ROSTERS_2025_26.get(team_name, []))
                for player in team_roster:
                    if player['name'] == clean_name:
                        real_player = player
                        break
            
            if real_player:
                # 로스터 데이터를 시스템 형식으로 변환
                return {
                    'name': real_player['name'],
                    'team': team_name,
                    'age': real_player.get('age', 25),
                    'position': real_player['position'],
                    'matches_played': 100,  # 시즌 진행 중
                    'minutes_played': 0,
                    'goals': 0,
                    'assists': 0,
                    'yellow_cards': 0,
                    'red_cards': 0,
                    'rating_avg': real_player.get('rating', 7.0),
                    'condition': 85 + np.random.uniform(-10, 10),
                    'injury_status': '정상',
                    'fatigue_level': 30 + np.random.uniform(-10, 20),
                    'real_data': True,
                    'jersey': real_player.get('jersey', ''),
                }
        except Exception as e:
            if self.debug:
                print(f"[ERROR] 로컬 로스터 데이터 로드 실패 ({clean_name}): {e}")
                import traceback
                traceback.print_exc()
        
        # 3. players_2026 모듈로 선수 데이터 로드 시도 (백업)
        try:
            import sys
            from pathlib import Path
            data_path = Path(__file__).parent.parent / "data"
            if str(data_path) not in sys.path:
                sys.path.insert(0, str(data_path))
            
            from players_2026 import get_player_stats
            
            real_player = get_player_stats(self.league, team_name, clean_name)
            
            if real_player:
                if self.debug:
                    print(f"[OK] {clean_name} players_2026 데이터 로드 완료")
                # 실제 데이터를 시스템 형식으로 변환
                if 'ppg' in real_player:  # NBA 선수
                    return {
                        'name': real_player['name'],
                        'team': team_name,
                        'age': real_player['age'],
                        'position': real_player['position'],
                        'matches_played': 69,  # NBA 시즌 진행 중
                        'minutes_played': 2400,
                        'goals': int(real_player['ppg']),  # PPG를 goals로
                        'assists': int(real_player.get('apg', 0)),
                        'yellow_cards': 0,
                        'red_cards': 0,
                        'rating_avg': real_player['rating'],
                        'condition': 85 + np.random.uniform(-10, 10),
                        'injury_status': '정상',
                        'fatigue_level': 30 + np.random.uniform(-10, 20),
                        'real_data': True,
                        'ppg': real_player['ppg'],
                        'rpg': real_player.get('rpg', 0),
                        'apg': real_player.get('apg', 0)
                    }
                else:  # 축구 선수
                    return {
                        'name': real_player['name'],
                        'team': team_name,
                        'age': real_player['age'],
                        'position': real_player['position'],
                        'matches_played': 28,  # 시즌 진행 중
                        'minutes_played': 2200,
                        'goals': real_player['goals'],
                        'assists': real_player['assists'],
                        'yellow_cards': np.random.randint(0, 5),
                        'red_cards': 0,
                        'rating_avg': real_player['rating'],
                        'condition': 85 + np.random.uniform(-10, 10),
                        'injury_status': '정상',
                        'fatigue_level': 30 + np.random.uniform(-10, 20),
                        'real_data': True
                    }
            else:
                print(f"[WARNING] {clean_name} 로컬 데이터 없음")
        except Exception as e:
            print(f"[ERROR] 로컬 선수 데이터 로드 실패 ({player_name}): {e}")
        
        # 시뮬레이션 데이터
        print(f"[WARNING] {player_name} 시뮬레이션 데이터 사용")
        return {
            'name': player_name,
            'team': team_name,
            'age': np.random.randint(20, 35),
            'position': player_name.split()[0] if ' ' in player_name else 'MF',
            'matches_played': np.random.randint(10, 30),
            'minutes_played': np.random.randint(500, 2500),
            'goals': np.random.randint(0, 15),
            'assists': np.random.randint(0, 10),
            'yellow_cards': np.random.randint(0, 5),
            'red_cards': np.random.randint(0, 2),
            'rating_avg': np.random.uniform(6.0, 8.5),
            'condition': np.random.uniform(70, 100),
            'injury_status': np.random.choice(['정상', '경미한 부상', '회복 중'], p=[0.8, 0.15, 0.05]),
            'fatigue_level': np.random.uniform(0, 100),
            'real_data': False
        }
    
    def get_head_to_head(self, team1, team2, limit=5):
        """두 팀의 최근 맞대결 기록"""
        matches = []
        
        for i in range(limit):
            team1_score = np.random.randint(0, 4)
            team2_score = np.random.randint(0, 4)
            
            matches.append({
                'date': datetime.now() - timedelta(days=30*i),
                'home_team': team1 if i % 2 == 0 else team2,
                'away_team': team2 if i % 2 == 0 else team1,
                'home_score': team1_score if i % 2 == 0 else team2_score,
                'away_score': team2_score if i % 2 == 0 else team1_score,
                'venue': f"경기장{i}"
            })
        
        return matches
    
    def get_weather_data(self, location, date):
        """날씨 데이터 수집 (실제로는 기상청 API 사용)"""
        return {
            'temperature': np.random.uniform(10, 30),
            'humidity': np.random.uniform(40, 80),
            'wind_speed': np.random.uniform(0, 15),
            'precipitation': np.random.uniform(0, 10),
            'condition': np.random.choice(['맑음', '흐림', '비', '눈'])
        }
    
    def get_stadium_data(self, stadium_name):
        """경기장 정보"""
        return {
            'name': stadium_name,
            'capacity': np.random.randint(20000, 60000),
            'surface': np.random.choice(['천연잔디', '인조잔디', '하이브리드']),
            'altitude': np.random.randint(0, 500),
            'home_advantage': np.random.uniform(0.05, 0.15)
        }
    
    def scrape_kbo_data(self):
        """KBO 데이터 크롤링 예시"""
        try:
            # 실제 구현 시 사용
            # url = "https://www.koreabaseball.com/..."
            # response = requests.get(url)
            # soup = BeautifulSoup(response.content, 'html.parser')
            # ... 파싱 로직
            pass
        except Exception as e:
            print(f"크롤링 오류: {e}")
            return None
    
    def scrape_kleague_data(self):
        """K리그 데이터 크롤링 예시"""
        try:
            # 실제 구현 시 사용
            # url = "https://www.kleague.com/..."
            pass
        except Exception as e:
            print(f"크롤링 오류: {e}")
            return None
    
    def save_data(self, data, filename):
        """데이터 저장"""
        filepath = self.data_dir / filename
        
        if isinstance(data, pd.DataFrame):
            data.to_csv(filepath, index=False, encoding='utf-8-sig')
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def load_data(self, filename):
        """저장된 데이터 로드"""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            return None
        
        if filename.endswith('.csv'):
            return pd.read_csv(filepath, encoding='utf-8-sig')
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)

    
    def get_team_players(self, team_name: str) -> list:
        """
        팀 선수 데이터 가져오기
        
        Args:
            team_name: 팀 이름
        
        Returns:
            선수 리스트 (고급 메트릭스 포함)
        """
        
        # 캐시 확인
        cache_key = f"players_{team_name}_{self.league}"
        if cache_key in self.players_cache and not self._is_cache_expired(cache_key):
            if self.debug:
                print(f"[CACHE] 선수 데이터 캐시 사용: {team_name}")
            return self.players_cache[cache_key]
        
        # 선수 데이터 로드
        players = self.player_loader.get_team_players(team_name, self.league)
        
        if players:
            self.players_cache[cache_key] = players
            self._update_cache_timestamp(cache_key)
            
            if self.debug:
                print(f"[OK] {team_name} 선수 데이터 로드: {len(players)}명")
        else:
            if self.debug:
                print(f"[WARNING] {team_name} 선수 데이터 없음")
        
        return players
    
    def get_top_players(self, team_name: str, top_n: int = 5) -> list:
        """
        팀의 주요 선수 가져오기
        
        Args:
            team_name: 팀 이름
            top_n: 상위 N명
        
        Returns:
            주요 선수 리스트
        """
        
        return self.player_loader.get_top_players(team_name, self.league, top_n)
    
    def get_player_by_name(self, player_name: str, team_name: str = None) -> dict:
        """
        선수 이름으로 검색
        
        Args:
            player_name: 선수 이름
            team_name: 팀 이름 (선택)
        
        Returns:
            선수 정보 또는 None
        """
        
        return self.player_loader.get_player_by_name(player_name, team_name, self.league)
    
    def apply_injury_to_players(self, players: list, injury_data: dict) -> list:
        """
        부상 정보를 선수 데이터에 적용
        
        Args:
            players: 선수 리스트
            injury_data: 부상 정보 {'home': [...], 'away': [...]}
        
        Returns:
            부상 상태가 적용된 선수 리스트
        """
        
        if not injury_data:
            return players
        
        # 부상 선수 이름 추출
        injured_names = []
        for injuries in injury_data.values():
            for injury in injuries:
                injured_names.append(injury.get('name', ''))
        
        return self.player_loader.apply_injury_status(players, injured_names)

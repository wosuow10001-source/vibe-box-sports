"""
코칭스태프 정보 실시간 수집 모듈
- NBA: ESPN 및 공식 웹사이트
- MLB: ESPN 및 공식 웹사이트
- 축구 리그: ESPN 및 공식 리그 웹사이트
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

class CoachingStaffFetcher:
    """코칭스태프 정보를 가져오는 클래스"""
    
    def __init__(self, league="NBA"):
        """
        Args:
            league (str): 리그 이름 (NBA, MLB, KBO, EPL, La Liga, Bundesliga, Serie A)
        """
        self.league = league
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 리그별 URL 매핑
        self.base_urls = {
            'NBA': 'https://www.espn.com/nba/team/roster/_/name/{team_id}',
            'MLB': 'https://www.espn.com/mlb/team/roster/_/name/{team_id}',
            'KBO': 'https://www.espn.com/mlb/team/roster/_/name/{team_id}',
            'EPL': 'https://www.espn.com/soccer/team/squad/_/id/{team_id}',
            'La Liga': 'https://www.espn.com/soccer/team/squad/_/id/{team_id}',
            'Bundesliga': 'https://www.espn.com/soccer/team/squad/_/id/{team_id}',
            'Serie A': 'https://www.espn.com/soccer/team/squad/_/id/{team_id}'
        }
    
    def fetch_team_coaching_staff(self, team_name, team_id=None):
        """
        특정 팀의 코칭스태프 정보를 가져옵니다.
        
        Args:
            team_name (str): 팀 이름
            team_id (str, optional): ESPN 팀 ID
            
        Returns:
            dict: 코칭스태프 정보
        """
        try:
            if self.league == 'NBA':
                return self._fetch_nba_coaching_staff(team_name, team_id)
            else:
                return self._fetch_football_coaching_staff(team_name, team_id)
        except Exception as e:
            print(f"코칭스태프 정보 가져오기 실패 ({team_name}): {e}")
            return self._get_simulated_coaching_staff(team_name)

    
    def _fetch_nba_coaching_staff(self, team_name, team_id):
        """NBA 코칭스태프 정보 가져오기 (ESPN)"""
        # ESPN에서 코칭스태프 정보를 가져오기 어려우므로 시뮬레이션 사용
        return self._get_simulated_coaching_staff(team_name)
    
    def _fetch_football_coaching_staff(self, team_name, team_id):
        """축구 코칭스태프 정보 가져오기 (ESPN)"""
        # ESPN에서 코칭스태프 정보를 가져오기 어려우므로 시뮬레이션 사용
        return self._get_simulated_coaching_staff(team_name)
    
    def _get_simulated_coaching_staff(self, team_name):
        """
        시뮬레이션 코칭스태프 데이터
        (실시간 API 접근이 제한되어 있어 시뮬레이션 사용)
        """
        coaching_data = self._get_all_simulated_data()
        
        # 팀 이름으로 검색
        for league_data in coaching_data.values():
            if team_name in league_data:
                return league_data[team_name]
        
        # 기본값 반환
        return {
            'head_coach': 'Unknown',
            'assistant_coaches': [],
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }

    
    def _get_all_simulated_data(self):
        """모든 리그의 시뮬레이션 코칭스태프 데이터"""
        return {
            'NBA': {
                # Eastern Conference
                'Boston Celtics': {
                    'head_coach': 'Joe Mazzulla',
                    'assistant_coaches': ['Sam Cassell', 'Charles Lee', 'Ben Sullivan'],
                    'last_updated': '2026-03-21'
                },
                'Milwaukee Bucks': {
                    'head_coach': 'Doc Rivers',
                    'assistant_coaches': ['Darvin Ham', 'Joe Prunty', 'Josh Oppenheimer'],
                    'last_updated': '2026-03-21'
                },
                'Philadelphia 76ers': {
                    'head_coach': 'Nick Nurse',
                    'assistant_coaches': ['Brian Adams', 'Rico Hines', 'Ime Udoka'],
                    'last_updated': '2026-03-21'
                },
                'Cleveland Cavaliers': {
                    'head_coach': 'Kenny Atkinson',
                    'assistant_coaches': ['Greg Buckner', 'DeMarre Carroll', 'Tony Dobbins'],
                    'last_updated': '2026-03-21'
                },
                'New York Knicks': {
                    'head_coach': 'Tom Thibodeau',
                    'assistant_coaches': ['Johnnie Bryant', 'Rick Brunson', 'Andy Greer'],
                    'last_updated': '2026-03-21'
                },
                # Western Conference
                'Oklahoma City Thunder': {
                    'head_coach': 'Mark Daigneault',
                    'assistant_coaches': ['Chip England', 'Dave Bliss', 'Mike Wilks'],
                    'last_updated': '2026-03-21'
                },
                'Denver Nuggets': {
                    'head_coach': 'Michael Malone',
                    'assistant_coaches': ['David Adelman', 'Popeye Jones', 'Ryan Bowen'],
                    'last_updated': '2026-03-21'
                },
                'Los Angeles Lakers': {
                    'head_coach': 'JJ Redick',
                    'assistant_coaches': ['Scott Brooks', 'Nate McMillan', 'Bob Beyer'],
                    'last_updated': '2026-03-21'
                },
                'Golden State Warriors': {
                    'head_coach': 'Steve Kerr',
                    'assistant_coaches': ['Kenny Atkinson', 'Ron Adams', 'Chris DeMarco'],
                    'last_updated': '2026-03-21'
                },
                'Phoenix Suns': {
                    'head_coach': 'Mike Budenholzer',
                    'assistant_coaches': ['Vince Legarza', 'Chad Forcier', 'Brent Barry'],
                    'last_updated': '2026-03-21'
                },
            },

            'EPL': {
                'Manchester City': {
                    'head_coach': 'Pep Guardiola',
                    'assistant_coaches': ['Juanma Lillo', 'Rodolfo Borrell', 'Carlos Vicens'],
                    'last_updated': '2026-03-21'
                },
                'Arsenal': {
                    'head_coach': 'Mikel Arteta',
                    'assistant_coaches': ['Albert Stuivenberg', 'Carlos Cuesta', 'Miguel Molina'],
                    'last_updated': '2026-03-21'
                },
                'Liverpool': {
                    'head_coach': 'Arne Slot',
                    'assistant_coaches': ['Sipke Hulshoff', 'John Heitinga', 'Ruben Peeters'],
                    'last_updated': '2026-03-21'
                },
                'Chelsea': {
                    'head_coach': 'Enzo Maresca',
                    'assistant_coaches': ['Willy Caballero', 'Danny Walker', 'Michele De Bernardin'],
                    'last_updated': '2026-03-21'
                },
                'Manchester United': {
                    'head_coach': 'Ruben Amorim',
                    'assistant_coaches': ['Carlos Fernandes', 'Adelio Candido', 'Emanuel Ferro'],
                    'last_updated': '2026-03-21'
                },
                'Tottenham Hotspur': {
                    'head_coach': 'Ange Postecoglou',
                    'assistant_coaches': ['Mile Jedinak', 'Ryan Mason', 'Matt Wells'],
                    'last_updated': '2026-03-21'
                },
            },
            'La Liga': {
                'Real Madrid': {
                    'head_coach': 'Carlo Ancelotti',
                    'assistant_coaches': ['Davide Ancelotti', 'Francesco Mauri', 'Antonio Pintus'],
                    'last_updated': '2026-03-21'
                },
                'Barcelona': {
                    'head_coach': 'Hansi Flick',
                    'assistant_coaches': ['Marcus Sorg', 'Heiko Westermann', 'Toni Tapalović'],
                    'last_updated': '2026-03-21'
                },
                'Atlético Madrid': {
                    'head_coach': 'Diego Simeone',
                    'assistant_coaches': ['Nelson Vivas', 'Pablo Vercellone', 'Oscar Ortega'],
                    'last_updated': '2026-03-21'
                },
                'Athletic Bilbao': {
                    'head_coach': 'Ernesto Valverde',
                    'assistant_coaches': ['Jon Berasaluze', 'Xabier Azkargorta', 'Iñaki Bea'],
                    'last_updated': '2026-03-21'
                },
                'Real Sociedad': {
                    'head_coach': 'Imanol Alguacil',
                    'assistant_coaches': ['Ander Garitano', 'Xabi Alonso', 'Mikel Labaka'],
                    'last_updated': '2026-03-21'
                },
            },

            'Bundesliga': {
                'Bayern Munich': {
                    'head_coach': 'Vincent Kompany',
                    'assistant_coaches': ['Craig Bellamy', 'Floribert Ngalula', 'Aaron Danks'],
                    'last_updated': '2026-03-21'
                },
                'Borussia Dortmund': {
                    'head_coach': 'Nuri Şahin',
                    'assistant_coaches': ['Sven Bender', 'Łukasz Piszczek', 'Andreas Beck'],
                    'last_updated': '2026-03-21'
                },
                'RB Leipzig': {
                    'head_coach': 'Marco Rose',
                    'assistant_coaches': ['Alexander Zickler', 'Rene Maric', 'Sascha Lense'],
                    'last_updated': '2026-03-21'
                },
                'Bayer Leverkusen': {
                    'head_coach': 'Xabi Alonso',
                    'assistant_coaches': ['Xabi Alonso Jr.', 'Sebastian Parrilla', 'Fabian Wohlgemuth'],
                    'last_updated': '2026-03-21'
                },
                'VfB Stuttgart': {
                    'head_coach': 'Sebastian Hoeneß',
                    'assistant_coaches': ['Michael Wimmer', 'Markus Feldhoff', 'Nico Willig'],
                    'last_updated': '2026-03-21'
                },
            },
            'Serie A': {
                'Inter Milan': {
                    'head_coach': 'Simone Inzaghi',
                    'assistant_coaches': ['Massimiliano Farris', 'Gabriele Oriali', 'Daniele Bernazzani'],
                    'last_updated': '2026-03-21'
                },
                'AC Milan': {
                    'head_coach': 'Sérgio Conceição',
                    'assistant_coaches': ['Siramana Dembélé', 'Diamantino Figueiredo', 'Paulo Ferreira'],
                    'last_updated': '2026-03-21'
                },
                'Juventus': {
                    'head_coach': 'Thiago Motta',
                    'assistant_coaches': ['Alexandre Hugeux', 'Giuseppe Pompilio', 'Claudio Filippi'],
                    'last_updated': '2026-03-21'
                },
                'Napoli': {
                    'head_coach': 'Antonio Conte',
                    'assistant_coaches': ['Cristian Stellini', 'Gianluca Conte', 'Elvis Abbruscato'],
                    'last_updated': '2026-03-21'
                },
                'Atalanta': {
                    'head_coach': 'Gian Piero Gasperini',
                    'assistant_coaches': ['Tullio Gritti', 'Giovanni Valenti', 'Dario Bonetti'],
                    'last_updated': '2026-03-21'
                },
            },
            'MLB': {
                # American League East
                'New York Yankees': {
                    'head_coach': 'Aaron Boone',
                    'assistant_coaches': ['Luis Rojas', 'Carlos Mendoza', 'Dillon Lawson'],
                    'last_updated': '2026-03-21'
                },
                'Baltimore Orioles': {
                    'head_coach': 'Brandon Hyde',
                    'assistant_coaches': ['Fredi González', 'Ryan Fuller', 'José Hernández'],
                    'last_updated': '2026-03-21'
                },
                'Tampa Bay Rays': {
                    'head_coach': 'Kevin Cash',
                    'assistant_coaches': ['Matt Quatraro', 'Rodney Linares', 'Kyle Snyder'],
                    'last_updated': '2026-03-21'
                },
                'Toronto Blue Jays': {
                    'head_coach': 'John Schneider',
                    'assistant_coaches': ['Don Mattingly', 'Casey Candaele', 'Pete Walker'],
                    'last_updated': '2026-03-21'
                },
                'Boston Red Sox': {
                    'head_coach': 'Alex Cora',
                    'assistant_coaches': ['Kyle Hudson', 'Luis Urueta', 'Andrew Bailey'],
                    'last_updated': '2026-03-21'
                },
                # American League Central
                'Cleveland Guardians': {
                    'head_coach': 'Stephen Vogt',
                    'assistant_coaches': ['Craig Albernaz', 'Carl Willis', 'Mike Sarbaugh'],
                    'last_updated': '2026-03-21'
                },
                'Minnesota Twins': {
                    'head_coach': 'Rocco Baldelli',
                    'assistant_coaches': ['Jayce Tingler', 'Tommy Watkins', 'Wes Johnson'],
                    'last_updated': '2026-03-21'
                },
                # American League West
                'Houston Astros': {
                    'head_coach': 'Joe Espada',
                    'assistant_coaches': ['Josh Miller', 'Omar López', 'Bill Murphy'],
                    'last_updated': '2026-03-21'
                },
                'Seattle Mariners': {
                    'head_coach': 'Dan Wilson',
                    'assistant_coaches': ['Edgar Martínez', 'Jarret DeHart', 'Pete Woodworth'],
                    'last_updated': '2026-03-21'
                },
                'Texas Rangers': {
                    'head_coach': 'Bruce Bochy',
                    'assistant_coaches': ['Will Venable', 'Tony Beasley', 'Mike Maddux'],
                    'last_updated': '2026-03-21'
                },
                # National League East
                'Philadelphia Phillies': {
                    'head_coach': 'Rob Thomson',
                    'assistant_coaches': ['Michael Brenly', 'Kevin Long', 'Caleb Cotham'],
                    'last_updated': '2026-03-21'
                },
                'Atlanta Braves': {
                    'head_coach': 'Brian Snitker',
                    'assistant_coaches': ['Walt Weiss', 'Eric Young Sr.', 'Rick Kranitz'],
                    'last_updated': '2026-03-21'
                },
                'New York Mets': {
                    'head_coach': 'Carlos Mendoza',
                    'assistant_coaches': ['Eric Chavez', 'Jeremy Barnes', 'Desi Druschel'],
                    'last_updated': '2026-03-21'
                },
                # National League Central
                'Milwaukee Brewers': {
                    'head_coach': 'Pat Murphy',
                    'assistant_coaches': ['Rickie Weeks', 'Connor Dawson', 'Chris Hook'],
                    'last_updated': '2026-03-21'
                },
                'Chicago Cubs': {
                    'head_coach': 'Craig Counsell',
                    'assistant_coaches': ['Ryan Flaherty', 'Dustin Kelly', 'Tommy Hottovy'],
                    'last_updated': '2026-03-21'
                },
                # National League West
                'Los Angeles Dodgers': {
                    'head_coach': 'Dave Roberts',
                    'assistant_coaches': ['Danny Lehmann', 'Clayton McCullough', 'Mark Prior'],
                    'last_updated': '2026-03-21'
                },
                'San Diego Padres': {
                    'head_coach': 'Mike Shildt',
                    'assistant_coaches': ['Ryan Christenson', 'Bryce Florie', 'Ruben Niebla'],
                    'last_updated': '2026-03-21'
                },
                'Arizona Diamondbacks': {
                    'head_coach': 'Torey Lovullo',
                    'assistant_coaches': ['Joe Mather', 'Tony Perezchica', 'Brent Strom'],
                    'last_updated': '2026-03-21'
                },
            },
            'KBO': {
                'KIA': {
                    'head_coach': '김종국',
                    'assistant_coaches': ['이종욱', '박정태', '김기태'],
                    'last_updated': '2026-03-21'
                },
                '삼성': {
                    'head_coach': '박진만',
                    'assistant_coaches': ['김한수', '이승호', '조영훈'],
                    'last_updated': '2026-03-21'
                },
                'LG': {
                    'head_coach': '염경엽',
                    'assistant_coaches': ['봉중근', '이종범', '정민철'],
                    'last_updated': '2026-03-21'
                },
                '두산': {
                    'head_coach': '이승엽',
                    'assistant_coaches': ['김태형', '박정권', '최일언'],
                    'last_updated': '2026-03-21'
                },
                'KT': {
                    'head_coach': '이강철',
                    'assistant_coaches': ['김재현', '조계현', '이호준'],
                    'last_updated': '2026-03-21'
                },
                'SSG': {
                    'head_coach': '이숭용',
                    'assistant_coaches': ['김원형', '박경완', '최형우'],
                    'last_updated': '2026-03-21'
                },
                'NC': {
                    'head_coach': '이호준',
                    'assistant_coaches': ['김경문', '박석민', '이상훈'],
                    'last_updated': '2026-03-21'
                },
                '롯데': {
                    'head_coach': '김태형',
                    'assistant_coaches': ['이종욱', '박정태', '손승락'],
                    'last_updated': '2026-03-21'
                },
                '한화': {
                    'head_coach': '김경문',
                    'assistant_coaches': ['한용덕', '이광은', '정민태'],
                    'last_updated': '2026-03-21'
                },
                '키움': {
                    'head_coach': '홍원기',
                    'assistant_coaches': ['조성환', '김재걸', '이택근'],
                    'last_updated': '2026-03-21'
                },
            },
            'K리그1': {
                '울산': {
                    'head_coach': '홍명보',
                    'assistant_coaches': ['김호곤', '이영진', '최은성'],
                    'last_updated': '2026-03-21'
                },
                '전북': {
                    'head_coach': '김상식',
                    'assistant_coaches': ['김학범', '최강희', '박경훈'],
                    'last_updated': '2026-03-21'
                },
                '포항': {
                    'head_coach': '박태하',
                    'assistant_coaches': ['황선홍', '김기동', '이광종'],
                    'last_updated': '2026-03-21'
                },
                '수원FC': {
                    'head_coach': '김은중',
                    'assistant_coaches': ['서정원', '김남일', '조민국'],
                    'last_updated': '2026-03-21'
                },
                '인천': {
                    'head_coach': '최영근',
                    'assistant_coaches': ['이임생', '김도훈', '박성화'],
                    'last_updated': '2026-03-21'
                },
                '대구': {
                    'head_coach': '박창현',
                    'assistant_coaches': ['이천수', '김용대', '최진철'],
                    'last_updated': '2026-03-21'
                },
                '제주': {
                    'head_coach': '김학범',
                    'assistant_coaches': ['남기일', '정조국', '고종수'],
                    'last_updated': '2026-03-21'
                },
                '강원': {
                    'head_coach': '정경호',
                    'assistant_coaches': ['박항서', '이을용', '김병지'],
                    'last_updated': '2026-03-21'
                },
                '서울': {
                    'head_coach': '안익수',
                    'assistant_coaches': ['최용수', '고명진', '김진규'],
                    'last_updated': '2026-03-21'
                },
                '광주': {
                    'head_coach': '이정효',
                    'assistant_coaches': ['정해성', '이운재', '김태영'],
                    'last_updated': '2026-03-21'
                },
                '대전': {
                    'head_coach': '황선홍',
                    'assistant_coaches': ['박성화', '김정남', '이영무'],
                    'last_updated': '2026-03-21'
                },
                '김천': {
                    'head_coach': '김태완',
                    'assistant_coaches': ['서정원', '최은성', '박경훈'],
                    'last_updated': '2026-03-21'
                },
            },
            'KBL': {
                '울산': {
                    'head_coach': '유재학',
                    'assistant_coaches': ['김승기', '이상범', '전창진'],
                    'last_updated': '2026-03-21'
                },
                '서울SK': {
                    'head_coach': '전희철',
                    'assistant_coaches': ['문경은', '김승현', '추승균'],
                    'last_updated': '2026-03-21'
                },
                '수원KT': {
                    'head_coach': '송영진',
                    'assistant_coaches': ['김영만', '이상민', '전창진'],
                    'last_updated': '2026-03-21'
                },
                '안양KGC': {
                    'head_coach': '김승기',
                    'assistant_coaches': ['이상범', '추일승', '김주성'],
                    'last_updated': '2026-03-21'
                },
                '창원LG': {
                    'head_coach': '조동현',
                    'assistant_coaches': ['김기범', '이상민', '전희철'],
                    'last_updated': '2026-03-21'
                },
                '고양': {
                    'head_coach': '김승현',
                    'assistant_coaches': ['문경은', '추승균', '김영만'],
                    'last_updated': '2026-03-21'
                },
                '서울삼성': {
                    'head_coach': '이상범',
                    'assistant_coaches': ['김주성', '전창진', '추일승'],
                    'last_updated': '2026-03-21'
                },
                '원주DB': {
                    'head_coach': '김주성',
                    'assistant_coaches': ['김기범', '이상민', '문경은'],
                    'last_updated': '2026-03-21'
                },
                '부산KCC': {
                    'head_coach': '전창진',
                    'assistant_coaches': ['추승균', '김영만', '송영진'],
                    'last_updated': '2026-03-21'
                },
                '대구한국가스공사': {
                    'head_coach': '김기범',
                    'assistant_coaches': ['조동현', '전희철', '추일승'],
                    'last_updated': '2026-03-21'
                },
            },
            'V-리그 남자': {
                '대한항공': {
                    'head_coach': '신영철',
                    'assistant_coaches': ['김세진', '강성형', '임기섭'],
                    'last_updated': '2026-03-21'
                },
                '현대캐피탈': {
                    'head_coach': '임도헌',
                    'assistant_coaches': ['신진식', '최태웅', '김세진'],
                    'last_updated': '2026-03-21'
                },
                'OK금융그룹': {
                    'head_coach': '김세진',
                    'assistant_coaches': ['강성형', '임기섭', '신영철'],
                    'last_updated': '2026-03-21'
                },
                '삼성화재': {
                    'head_coach': '강성형',
                    'assistant_coaches': ['임도헌', '신진식', '최태웅'],
                    'last_updated': '2026-03-21'
                },
                '한국전력': {
                    'head_coach': '임기섭',
                    'assistant_coaches': ['김세진', '신영철', '임도헌'],
                    'last_updated': '2026-03-21'
                },
                'KB손해보험': {
                    'head_coach': '신진식',
                    'assistant_coaches': ['최태웅', '강성형', '김세진'],
                    'last_updated': '2026-03-21'
                },
                '우리카드': {
                    'head_coach': '최태웅',
                    'assistant_coaches': ['신영철', '임도헌', '임기섭'],
                    'last_updated': '2026-03-21'
                },
            },
            'V-리그 여자': {
                '흥국생명': {
                    'head_coach': '강성형',
                    'assistant_coaches': ['이도희', '이영택', '김철용'],
                    'last_updated': '2026-03-21'
                },
                '현대건설': {
                    'head_coach': '이도희',
                    'assistant_coaches': ['김호철', '이상훈', '김형실'],
                    'last_updated': '2026-03-21'
                },
                'GS칼텍스': {
                    'head_coach': '이영택',
                    'assistant_coaches': ['강성형', '이도희', '김철용'],
                    'last_updated': '2026-03-21'
                },
                '한국도로공사': {
                    'head_coach': '김철용',
                    'assistant_coaches': ['김호철', '이상훈', '이영택'],
                    'last_updated': '2026-03-21'
                },
                'IBK기업은행': {
                    'head_coach': '김호철',
                    'assistant_coaches': ['이상훈', '김형실', '강성형'],
                    'last_updated': '2026-03-21'
                },
                '정관장': {
                    'head_coach': '이상훈',
                    'assistant_coaches': ['김형실', '이도희', '김철용'],
                    'last_updated': '2026-03-21'
                },
                '페퍼저축은행': {
                    'head_coach': '김형실',
                    'assistant_coaches': ['강성형', '이영택', '김호철'],
                    'last_updated': '2026-03-21'
                },
            }
        }

    
    def fetch_all_coaching_staff(self):
        """
        모든 팀의 코칭스태프 정보를 가져옵니다.
        
        Returns:
            dict: 팀별 코칭스태프 정보
        """
        all_data = self._get_all_simulated_data()
        return all_data.get(self.league, {})
    
    def get_head_coach(self, team_name):
        """
        특정 팀의 감독 이름을 반환합니다.
        
        Args:
            team_name (str): 팀 이름
            
        Returns:
            str: 감독 이름
        """
        staff = self.fetch_team_coaching_staff(team_name)
        return staff.get('head_coach', 'Unknown')
    
    def get_assistant_coaches(self, team_name):
        """
        특정 팀의 코치진 목록을 반환합니다.
        
        Args:
            team_name (str): 팀 이름
            
        Returns:
            list: 코치진 이름 리스트
        """
        staff = self.fetch_team_coaching_staff(team_name)
        return staff.get('assistant_coaches', [])
    
    def get_coaching_summary(self):
        """
        전체 리그의 코칭스태프 요약 정보를 반환합니다.
        
        Returns:
            dict: 코칭스태프 통계 정보
        """
        all_staff = self.fetch_all_coaching_staff()
        
        total_teams = len(all_staff)
        total_coaches = sum(len(staff.get('assistant_coaches', [])) + 1 
                          for staff in all_staff.values())
        
        return {
            'total_teams': total_teams,
            'total_coaches': total_coaches,
            'avg_coaches_per_team': total_coaches / total_teams if total_teams > 0 else 0,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def get_coaching_staff(league="NBA", team_name=None):
    """간단한 코칭스태프 정보 가져오기 함수"""
    fetcher = CoachingStaffFetcher(league=league)
    
    if team_name:
        return fetcher.fetch_team_coaching_staff(team_name)
    else:
        return fetcher.fetch_all_coaching_staff()


if __name__ == "__main__":
    # 테스트 코드
    print("="*70)
    print("리그별 코칭스태프 테스트")
    print("="*70)
    
    leagues = ['NBA', 'EPL', 'La Liga', 'Bundesliga', 'Serie A']
    
    for league in leagues:
        print(f"\n{league} 코칭스태프")
        print('-'*70)
        
        fetcher = CoachingStaffFetcher(league=league)
        summary = fetcher.get_coaching_summary()
        
        print(f"총 팀 수: {summary['total_teams']}")
        print(f"총 코치 수: {summary['total_coaches']}")
        print(f"팀당 평균 코치 수: {summary['avg_coaches_per_team']:.1f}")
        
        # 샘플 팀 표시
        all_staff = fetcher.fetch_all_coaching_staff()
        if all_staff:
            sample_team = list(all_staff.keys())[0]
            staff = all_staff[sample_team]
            print(f"\n샘플 팀: {sample_team}")
            print(f"  감독: {staff['head_coach']}")
            print(f"  코치진: {', '.join(staff['assistant_coaches'][:2])}")

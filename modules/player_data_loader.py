"""
선수 데이터 로더
- 선수 데이터 로드
- 팀별 선수 필터링
- 선수 통계 변환
"""

from typing import Dict, List, Optional
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class PlayerDataLoader:
    """선수 데이터 로드 및 관리"""
    
    def __init__(self):
        self.players_cache = {}
        self._load_all_players()
    
    def _load_all_players(self):
        """모든 선수 데이터 로드"""
        try:
            from data.players_2026 import (
                NBA_PLAYERS,
                LA_LIGA_PLAYERS,
                BUNDESLIGA_PLAYERS,
                SERIE_A_PLAYERS,
                EPL_PLAYERS
            )
            
            self.players_cache = {
                'NBA': NBA_PLAYERS,
                'La Liga': LA_LIGA_PLAYERS,
                'Bundesliga': BUNDESLIGA_PLAYERS,
                'Serie A': SERIE_A_PLAYERS,
                'EPL': EPL_PLAYERS
            }
            
            print("[OK] Player data loaded:")
            for league, teams in self.players_cache.items():
                total_players = sum(len(players) for players in teams.values())
                print(f"   - {league}: {len(teams)} teams, {total_players} players")
        
        except ImportError as e:
            print(f"[WARNING] Player data load failed: {e}")
            self.players_cache = {}
    
    def get_team_players(self, team_name: str, league: str = None) -> List[Dict]:
        """
        팀 선수 리스트 가져오기
        
        Args:
            team_name: 팀 이름
            league: 리그 이름 (선택)
        
        Returns:
            선수 리스트
        """
        
        # 리그가 지정되지 않으면 모든 리그에서 검색
        if league:
            leagues_to_search = [league]
        else:
            leagues_to_search = list(self.players_cache.keys())
        
        for league_name in leagues_to_search:
            league_data = self.players_cache.get(league_name, {})
            
            # 정확한 팀 이름 매칭
            if team_name in league_data:
                return self._convert_player_stats(league_data[team_name], league_name)
            
            # 부분 매칭 (예: "Lakers" → "Los Angeles Lakers")
            for team, players in league_data.items():
                if team_name.lower() in team.lower() or team.lower() in team_name.lower():
                    return self._convert_player_stats(players, league_name)
        
        print(f"[WARNING] Team '{team_name}' player data not found")
        return []
    
    def _convert_player_stats(self, players: List[Dict], league: str) -> List[Dict]:
        """
        선수 통계를 표준 형식으로 변환
        
        농구: ppg, rpg, apg, spg, bpg, topg, fg_pct, three_pct, ft_pct, mpg
        축구: goals, assists, rating
        """
        
        converted = []
        
        for player in players:
            converted_player = player.copy()
            
            if league == 'NBA':
                # NBA 선수는 이미 표준 형식
                # 기본값 추가
                converted_player.setdefault('spg', 1.0)  # steals per game
                converted_player.setdefault('bpg', 0.5)  # blocks per game
                converted_player.setdefault('topg', 2.0)  # turnovers per game
                converted_player.setdefault('fg_pct', 0.45)  # field goal %
                converted_player.setdefault('three_pct', 0.35)  # 3-point %
                converted_player.setdefault('ft_pct', 0.75)  # free throw %
                converted_player.setdefault('mpg', 30.0)  # minutes per game
                
                # 필드골 성공/시도 추정
                ppg = converted_player.get('ppg', 0)
                converted_player.setdefault('fgm', ppg * 0.4)
                converted_player.setdefault('fga', ppg * 0.9)
                converted_player.setdefault('ftm', ppg * 0.2)
                converted_player.setdefault('fta', ppg * 0.25)
                
                # 최근 폼 (기본값: 시즌 평균과 동일)
                converted_player.setdefault('recent_ppg', ppg)
                converted_player.setdefault('form', 1.0)
            
            elif league in ['La Liga', 'Bundesliga', 'Serie A', 'EPL']:
                # 축구 선수는 다른 형식
                # 농구 형식으로 변환하지 않음 (축구 예측에서 사용)
                pass
            
            converted.append(converted_player)
        
        return converted
    
    def get_player_by_name(self, player_name: str, team_name: str = None, 
                          league: str = None) -> Optional[Dict]:
        """
        선수 이름으로 검색
        
        Args:
            player_name: 선수 이름
            team_name: 팀 이름 (선택)
            league: 리그 이름 (선택)
        
        Returns:
            선수 정보 또는 None
        """
        
        if team_name:
            players = self.get_team_players(team_name, league)
            for player in players:
                if player_name.lower() in player.get('name', '').lower():
                    return player
        else:
            # 모든 팀에서 검색
            leagues_to_search = [league] if league else list(self.players_cache.keys())
            
            for league_name in leagues_to_search:
                league_data = self.players_cache.get(league_name, {})
                for team, players in league_data.items():
                    for player in players:
                        if player_name.lower() in player.get('name', '').lower():
                            return self._convert_player_stats([player], league_name)[0]
        
        return None
    
    def get_top_players(self, team_name: str, league: str = None, 
                       top_n: int = 5) -> List[Dict]:
        """
        팀의 주요 선수 가져오기
        
        Args:
            team_name: 팀 이름
            league: 리그 이름 (선택)
            top_n: 상위 N명
        
        Returns:
            주요 선수 리스트
        """
        
        players = self.get_team_players(team_name, league)
        
        if not players:
            return []
        
        # NBA: ppg 기준 정렬
        if 'ppg' in players[0]:
            sorted_players = sorted(players, key=lambda p: p.get('ppg', 0), reverse=True)
        # 축구: rating 기준 정렬
        elif 'rating' in players[0]:
            sorted_players = sorted(players, key=lambda p: p.get('rating', 0), reverse=True)
        else:
            sorted_players = players
        
        return sorted_players[:top_n]
    
    def apply_injury_status(self, players: List[Dict], 
                           injured_names: List[str]) -> List[Dict]:
        """
        부상 상태 적용
        
        Args:
            players: 선수 리스트
            injured_names: 부상 선수 이름 리스트
        
        Returns:
            부상 상태가 적용된 선수 리스트
        """
        
        updated_players = []
        
        for player in players:
            player_copy = player.copy()
            
            # 부상 선수 체크
            is_injured = any(
                name.lower() in player.get('name', '').lower() 
                for name in injured_names
            )
            
            if is_injured:
                player_copy['injured'] = True
                player_copy['mpg'] = 0  # 출전 시간 0
                player_copy['form'] = 0.0  # 컨디션 0
            else:
                player_copy['injured'] = False
            
            updated_players.append(player_copy)
        
        return updated_players


# 싱글톤 인스턴스
_player_loader = None

def get_player_loader() -> PlayerDataLoader:
    """PlayerDataLoader 싱글톤 반환"""
    global _player_loader
    if _player_loader is None:
        _player_loader = PlayerDataLoader()
    return _player_loader

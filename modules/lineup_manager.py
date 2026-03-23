"""
라인업 관리 시스템
- 선발/후보 라인업 관리
- 종목별 포메이션
- 라인업 검증
"""

from typing import Dict, List, Optional
from modules.player_rating_system import get_rating_system


class LineupManager:
    """라인업 관리 및 검증"""
    
    def __init__(self):
        self.rating_system = get_rating_system()
        
        # 종목별 선발 인원
        self.starting_lineup_size = {
            'soccer': 11,
            'basketball': 5,
            'baseball': 9,  # 타자 9명 + 선발투수
            'volleyball': 6
        }
        
        # 종목별 포메이션
        self.formations = {
            'soccer': ['4-4-2', '4-3-3', '3-5-2', '4-2-3-1', '5-3-2'],
            'basketball': ['전통형', '스몰볼', '빅맨중심'],
            'baseball': ['일반', '강타', '수비중심'],
            'volleyball': ['5-1', '6-2', '4-2']
        }
    
    def create_lineup(self, players: List[Dict], sport: str, 
                     formation: Optional[str] = None,
                     tactic: str = '균형형') -> Dict:
        """
        라인업 생성
        
        Args:
            players: 전체 선수 리스트
            sport: 종목
            formation: 포메이션 (선택)
            tactic: 전술 ('공격형', '수비형', '균형형')
        
        Returns:
            {
                'starters': List[Dict],  # 선발
                'bench': List[Dict],     # 후보
                'formation': str,
                'tactic': str,
                'team_strength': Dict
            }
        """
        
        if not players:
            return self._empty_lineup(sport)
        
        # 선수 정렬 (능력치 높은 순)
        sorted_players = sorted(
            players, 
            key=lambda p: self._get_player_overall(p), 
            reverse=True
        )
        
        # 선발/후보 분리
        lineup_size = self.starting_lineup_size.get(sport, 11)
        starters = sorted_players[:lineup_size]
        bench = sorted_players[lineup_size:]
        
        # 포메이션 설정
        if not formation:
            formation = self.formations.get(sport, ['기본'])[0]
        
        # 팀 전력 계산
        team_strength = self.rating_system.calculate_team_strength(starters, sport)
        
        # 전술 적용
        team_strength = self.rating_system.apply_tactical_adjustment(
            team_strength, tactic, sport
        )
        
        return {
            'starters': starters,
            'bench': bench,
            'formation': formation,
            'tactic': tactic,
            'team_strength': team_strength,
            'total_players': len(players)
        }
    
    def validate_lineup(self, lineup: Dict, sport: str) -> Dict:
        """
        라인업 검증
        
        Returns:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str]
            }
        """
        
        errors = []
        warnings = []
        
        starters = lineup.get('starters', [])
        required_size = self.starting_lineup_size.get(sport, 11)
        
        # 인원 수 확인
        if len(starters) < required_size:
            errors.append(f"선발 인원 부족: {len(starters)}/{required_size}")
        elif len(starters) > required_size:
            errors.append(f"선발 인원 초과: {len(starters)}/{required_size}")
        
        # 포지션 검증 (종목별)
        if sport == 'soccer':
            position_count = {}
            for player in starters:
                pos = player.get('position', 'MF')
                position_count[pos] = position_count.get(pos, 0) + 1
            
            if position_count.get('GK', 0) != 1:
                errors.append(f"골키퍼는 1명이어야 함: {position_count.get('GK', 0)}명")
            
            if position_count.get('DF', 0) < 3:
                warnings.append(f"수비수가 적음: {position_count.get('DF', 0)}명")
        
        elif sport == 'baseball':
            pitcher_count = sum(1 for p in starters if p.get('position') == 'P')
            if pitcher_count < 1:
                errors.append("선발 투수가 없음")
        
        # 컨디션 경고
        low_form_players = [
            p['name'] for p in starters 
            if p.get('form', 1.0) < 0.7
        ]
        if low_form_players:
            warnings.append(f"컨디션 낮은 선수: {', '.join(low_form_players)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def compare_lineups(self, home_lineup: Dict, away_lineup: Dict, sport: str) -> Dict:
        """
        두 팀 라인업 비교
        
        Returns:
            {
                'strength_diff': float,  # 전력 차이
                'attack_diff': float,
                'defense_diff': float,
                'advantage': str  # 'home', 'away', 'balanced'
            }
        """
        
        home_strength = home_lineup.get('team_strength', {})
        away_strength = away_lineup.get('team_strength', {})
        
        strength_diff = home_strength.get('overall_rating', 70) - away_strength.get('overall_rating', 70)
        attack_diff = home_strength.get('attack_rating', 70) - away_strength.get('attack_rating', 70)
        defense_diff = home_strength.get('defense_rating', 70) - away_strength.get('defense_rating', 70)
        
        if strength_diff > 5:
            advantage = 'home'
        elif strength_diff < -5:
            advantage = 'away'
        else:
            advantage = 'balanced'
        
        return {
            'strength_diff': strength_diff,
            'attack_diff': attack_diff,
            'defense_diff': defense_diff,
            'advantage': advantage,
            'home_overall': home_strength.get('overall_rating', 70),
            'away_overall': away_strength.get('overall_rating', 70)
        }
    
    def _get_player_overall(self, player: Dict) -> float:
        """선수 종합 능력치 계산"""
        rating = player.get('rating', {})
        form = player.get('form', 1.0)
        
        # 모든 능력치 평균
        if rating:
            avg_rating = sum(rating.values()) / len(rating)
        else:
            avg_rating = 70
        
        return avg_rating * form
    
    def _empty_lineup(self, sport: str) -> Dict:
        """빈 라인업"""
        return {
            'starters': [],
            'bench': [],
            'formation': self.formations.get(sport, ['기본'])[0],
            'tactic': '균형형',
            'team_strength': {
                'overall_rating': 70.0,
                'attack_rating': 70.0,
                'defense_rating': 70.0,
                'position_strength': {}
            },
            'total_players': 0
        }
    
    def get_available_formations(self, sport: str) -> List[str]:
        """종목별 사용 가능한 포메이션"""
        return self.formations.get(sport, ['기본'])
    
    def get_tactics(self) -> List[str]:
        """사용 가능한 전술"""
        return ['공격형', '수비형', '균형형']


# 싱글톤 인스턴스
_lineup_manager = None

def get_lineup_manager() -> LineupManager:
    """LineupManager 싱글톤 반환"""
    global _lineup_manager
    if _lineup_manager is None:
        _lineup_manager = LineupManager()
    return _lineup_manager

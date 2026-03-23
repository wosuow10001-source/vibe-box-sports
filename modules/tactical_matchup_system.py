"""
전술 상성 & 포지션 매치업 시스템
- 전술 스타일 분석
- 포지션별 매치업 계산
- λ(득점)에 직접 영향
"""

from typing import Dict, List, Optional
import numpy as np


class TacticalMatchupSystem:
    """전술 상성 및 포지션 매치업 분석"""
    
    def __init__(self):
        # 전술 스타일 정의
        self.tactical_styles = {
            'soccer': {
                'tiki-taka': {'possession': 0.9, 'pressing': 0.8, 'width': 0.6, 'pace': 0.5},
                'counter-attack': {'possession': 0.3, 'pressing': 0.4, 'width': 0.7, 'pace': 0.9},
                'high-press': {'possession': 0.6, 'pressing': 0.95, 'width': 0.5, 'pace': 0.8},
                'park-bus': {'possession': 0.2, 'pressing': 0.3, 'width': 0.3, 'pace': 0.2},
                'balanced': {'possession': 0.5, 'pressing': 0.5, 'width': 0.5, 'pace': 0.5}
            },
            'basketball': {
                'fast-break': {'pace': 0.9, 'three_point': 0.7, 'inside': 0.4, 'defense': 0.6},
                'half-court': {'pace': 0.3, 'three_point': 0.5, 'inside': 0.8, 'defense': 0.7},
                'small-ball': {'pace': 0.8, 'three_point': 0.9, 'inside': 0.3, 'defense': 0.5},
                'traditional': {'pace': 0.5, 'three_point': 0.4, 'inside': 0.9, 'defense': 0.8}
            },
            'baseball': {
                'power-hitting': {'contact': 0.5, 'power': 0.9, 'speed': 0.4, 'patience': 0.6},
                'small-ball': {'contact': 0.9, 'power': 0.3, 'speed': 0.9, 'patience': 0.7},
                'balanced': {'contact': 0.7, 'power': 0.6, 'speed': 0.6, 'patience': 0.7}
            },
            'volleyball': {
                'quick-attack': {'spike_speed': 0.9, 'block': 0.6, 'serve': 0.8, 'receive': 0.6},
                'power-attack': {'spike_speed': 0.7, 'block': 0.8, 'serve': 0.7, 'receive': 0.7},
                'defensive': {'spike_speed': 0.5, 'block': 0.9, 'serve': 0.6, 'receive': 0.9}
            }
        }
        
        # 전술 상성 매트릭스 (공격 vs 수비)
        self.tactical_advantage = {
            'soccer': {
                ('tiki-taka', 'high-press'): -0.15,  # 불리
                ('tiki-taka', 'park-bus'): 0.10,     # 유리
                ('counter-attack', 'high-press'): 0.20,  # 매우 유리
                ('counter-attack', 'park-bus'): -0.10,
                ('high-press', 'tiki-taka'): 0.15,
                ('high-press', 'counter-attack'): -0.20,
            },
            'basketball': {
                ('fast-break', 'half-court'): 0.15,
                ('small-ball', 'traditional'): 0.10,
                ('traditional', 'small-ball'): -0.10,
            }
        }
    
    def analyze_tactical_matchup(self, home_style: Dict, away_style: Dict, 
                                 sport: str) -> Dict:
        """
        전술 상성 분석
        
        Args:
            home_style: 홈팀 전술 스타일 {'name': str, 'attributes': dict}
            away_style: 원정팀 전술 스타일
            sport: 종목
        
        Returns:
            {
                'home_advantage': float,  # -0.3 ~ +0.3
                'away_advantage': float,
                'interaction_score': float,  # 0 ~ 1
                'key_conflicts': list,
                'lambda_adjustment': dict  # λ 조정값
            }
        """
        
        if sport == 'soccer':
            return self._analyze_soccer_tactics(home_style, away_style)
        elif sport == 'basketball':
            return self._analyze_basketball_tactics(home_style, away_style)
        elif sport == 'baseball':
            return self._analyze_baseball_tactics(home_style, away_style)
        elif sport == 'volleyball':
            return self._analyze_volleyball_tactics(home_style, away_style)
        else:
            return self._default_matchup()
    
    def _analyze_soccer_tactics(self, home_style: Dict, away_style: Dict) -> Dict:
        """축구 전술 상성 분석"""
        
        home_name = home_style.get('name', 'balanced')
        away_name = away_style.get('name', 'balanced')
        
        home_attr = self.tactical_styles['soccer'].get(home_name, 
                     self.tactical_styles['soccer']['balanced'])
        away_attr = self.tactical_styles['soccer'].get(away_name,
                     self.tactical_styles['soccer']['balanced'])
        
        # 1. Pressing vs Build-up
        pressing_conflict = abs(home_attr['pressing'] - away_attr['pressing'])
        if home_attr['pressing'] > away_attr['pressing'] + 0.3:
            pressing_advantage = 0.15  # 홈팀 압박 유리
        elif away_attr['pressing'] > home_attr['pressing'] + 0.3:
            pressing_advantage = -0.15
        else:
            pressing_advantage = 0.0
        
        # 2. Pace Conflict
        pace_diff = home_attr['pace'] - away_attr['pace']
        if abs(pace_diff) > 0.4:
            # 템포 차이 크면 빠른 팀 유리
            pace_advantage = 0.10 if pace_diff > 0 else -0.10
        else:
            pace_advantage = 0.0
        
        # 3. Width vs Compactness
        width_conflict = home_attr['width'] - away_attr['width']
        width_advantage = width_conflict * 0.05
        
        # 4. Possession Battle
        possession_diff = home_attr['possession'] - away_attr['possession']
        possession_advantage = possession_diff * 0.08
        
        # 종합 우세
        home_advantage = (
            pressing_advantage * 0.35 +
            pace_advantage * 0.25 +
            width_advantage * 0.20 +
            possession_advantage * 0.20
        )
        
        # λ 조정 계산
        lambda_adjustment = {
            'home_attack': 1.0 + home_advantage,
            'home_defense': 1.0 - home_advantage * 0.5,
            'away_attack': 1.0 - home_advantage,
            'away_defense': 1.0 + home_advantage * 0.5
        }
        
        # 주요 충돌 지점
        key_conflicts = []
        if pressing_conflict > 0.4:
            key_conflicts.append(f"압박 강도 차이 ({pressing_conflict:.1f})")
        if abs(pace_diff) > 0.4:
            key_conflicts.append(f"템포 차이 ({abs(pace_diff):.1f})")
        if abs(possession_diff) > 0.4:
            key_conflicts.append(f"점유율 스타일 차이 ({abs(possession_diff):.1f})")
        
        return {
            'home_advantage': home_advantage,
            'away_advantage': -home_advantage,
            'interaction_score': (pressing_conflict + abs(pace_diff)) / 2,
            'key_conflicts': key_conflicts,
            'lambda_adjustment': lambda_adjustment
        }
    
    def _analyze_basketball_tactics(self, home_style: Dict, away_style: Dict) -> Dict:
        """농구 전술 상성 분석"""
        
        home_name = home_style.get('name', 'traditional')
        away_name = away_style.get('name', 'traditional')
        
        home_attr = self.tactical_styles['basketball'].get(home_name,
                     self.tactical_styles['basketball']['traditional'])
        away_attr = self.tactical_styles['basketball'].get(away_name,
                     self.tactical_styles['basketball']['traditional'])
        
        # Pace 충돌
        pace_diff = home_attr['pace'] - away_attr['pace']
        pace_advantage = pace_diff * 0.12
        
        # 3점슛 vs 내부 공격
        three_vs_inside = (home_attr['three_point'] - away_attr['inside']) * 0.08
        
        # 수비 강도
        defense_diff = home_attr['defense'] - away_attr['defense']
        defense_advantage = defense_diff * 0.10
        
        home_advantage = pace_advantage + three_vs_inside + defense_advantage
        
        lambda_adjustment = {
            'home_attack': 1.0 + home_advantage * 0.8,
            'home_defense': 1.0 - home_advantage * 0.6,
            'away_attack': 1.0 - home_advantage * 0.8,
            'away_defense': 1.0 + home_advantage * 0.6
        }
        
        key_conflicts = []
        if abs(pace_diff) > 0.3:
            key_conflicts.append(f"템포 차이 ({abs(pace_diff):.1f})")
        
        return {
            'home_advantage': home_advantage,
            'away_advantage': -home_advantage,
            'interaction_score': abs(pace_diff),
            'key_conflicts': key_conflicts,
            'lambda_adjustment': lambda_adjustment
        }
    
    def _analyze_baseball_tactics(self, home_style: Dict, away_style: Dict) -> Dict:
        """야구 전술 상성 분석"""
        
        home_name = home_style.get('name', 'balanced')
        away_name = away_style.get('name', 'balanced')
        
        home_attr = self.tactical_styles['baseball'].get(home_name,
                     self.tactical_styles['baseball']['balanced'])
        away_attr = self.tactical_styles['baseball'].get(away_name,
                     self.tactical_styles['baseball']['balanced'])
        
        # Power vs Contact
        power_diff = home_attr['power'] - away_attr['power']
        contact_diff = home_attr['contact'] - away_attr['contact']
        
        home_advantage = (power_diff * 0.08 + contact_diff * 0.06)
        
        lambda_adjustment = {
            'home_attack': 1.0 + home_advantage,
            'home_defense': 1.0,
            'away_attack': 1.0 - home_advantage,
            'away_defense': 1.0
        }
        
        return {
            'home_advantage': home_advantage,
            'away_advantage': -home_advantage,
            'interaction_score': abs(power_diff),
            'key_conflicts': [],
            'lambda_adjustment': lambda_adjustment
        }
    
    def _analyze_volleyball_tactics(self, home_style: Dict, away_style: Dict) -> Dict:
        """배구 전술 상성 분석"""
        
        home_name = home_style.get('name', 'power-attack')
        away_name = away_style.get('name', 'power-attack')
        
        home_attr = self.tactical_styles['volleyball'].get(home_name,
                     self.tactical_styles['volleyball']['power-attack'])
        away_attr = self.tactical_styles['volleyball'].get(away_name,
                     self.tactical_styles['volleyball']['power-attack'])
        
        # Spike vs Block
        spike_vs_block = home_attr['spike_speed'] - away_attr['block']
        serve_vs_receive = home_attr['serve'] - away_attr['receive']
        
        home_advantage = (spike_vs_block * 0.10 + serve_vs_receive * 0.08)
        
        lambda_adjustment = {
            'home_attack': 1.0 + home_advantage,
            'home_defense': 1.0 - home_advantage * 0.5,
            'away_attack': 1.0 - home_advantage,
            'away_defense': 1.0 + home_advantage * 0.5
        }
        
        return {
            'home_advantage': home_advantage,
            'away_advantage': -home_advantage,
            'interaction_score': abs(spike_vs_block),
            'key_conflicts': [],
            'lambda_adjustment': lambda_adjustment
        }
    
    def _default_matchup(self) -> Dict:
        """기본 매치업 (데이터 없을 때)"""
        return {
            'home_advantage': 0.0,
            'away_advantage': 0.0,
            'interaction_score': 0.5,
            'key_conflicts': [],
            'lambda_adjustment': {
                'home_attack': 1.0,
                'home_defense': 1.0,
                'away_attack': 1.0,
                'away_defense': 1.0
            }
        }
    
    def analyze_position_matchup(self, home_lineup: Dict, away_lineup: Dict, 
                                 sport: str) -> Dict:
        """
        포지션별 매치업 분석
        
        Returns:
            {
                'matchup_score': float,  # -1 ~ +1
                'position_advantages': dict,
                'key_mismatches': list,
                'lambda_impact': float  # λ 조정 계수
            }
        """
        
        if sport == 'soccer':
            return self._analyze_soccer_positions(home_lineup, away_lineup)
        elif sport == 'basketball':
            return self._analyze_basketball_positions(home_lineup, away_lineup)
        elif sport == 'baseball':
            return self._analyze_baseball_positions(home_lineup, away_lineup)
        elif sport == 'volleyball':
            return self._analyze_volleyball_positions(home_lineup, away_lineup)
        else:
            return {'matchup_score': 0.0, 'position_advantages': {}, 
                   'key_mismatches': [], 'lambda_impact': 1.0}
    
    def _analyze_soccer_positions(self, home_lineup: Dict, away_lineup: Dict) -> Dict:
        """축구 포지션 매치업"""
        
        home_starters = home_lineup.get('starters', [])
        away_starters = away_lineup.get('starters', [])
        
        # FW vs DF 매치업
        home_fw_rating = np.mean([
            p.get('rating', {}).get('shooting', 70) 
            for p in home_starters if p.get('position') == 'FW'
        ]) if any(p.get('position') == 'FW' for p in home_starters) else 70
        
        away_df_rating = np.mean([
            p.get('rating', {}).get('defending', 70)
            for p in away_starters if p.get('position') == 'DF'
        ]) if any(p.get('position') == 'DF' for p in away_starters) else 70
        
        fw_vs_df = (home_fw_rating - away_df_rating) / 100
        
        # 반대 방향
        away_fw_rating = np.mean([
            p.get('rating', {}).get('shooting', 70)
            for p in away_starters if p.get('position') == 'FW'
        ]) if any(p.get('position') == 'FW' for p in away_starters) else 70
        
        home_df_rating = np.mean([
            p.get('rating', {}).get('defending', 70)
            for p in home_starters if p.get('position') == 'DF'
        ]) if any(p.get('position') == 'DF' for p in home_starters) else 70
        
        df_vs_fw = (home_df_rating - away_fw_rating) / 100
        
        matchup_score = (fw_vs_df + df_vs_fw) / 2
        lambda_impact = 1.0 + matchup_score * 0.15
        
        key_mismatches = []
        if abs(fw_vs_df) > 0.15:
            key_mismatches.append(f"공격수 vs 수비수 매치업 ({fw_vs_df:+.2f})")
        
        return {
            'matchup_score': matchup_score,
            'position_advantages': {
                'fw_vs_df': fw_vs_df,
                'df_vs_fw': df_vs_fw
            },
            'key_mismatches': key_mismatches,
            'lambda_impact': lambda_impact
        }
    
    def _analyze_basketball_positions(self, home_lineup: Dict, away_lineup: Dict) -> Dict:
        """농구 포지션 매치업"""
        
        home_strength = home_lineup.get('team_strength', {})
        away_strength = away_lineup.get('team_strength', {})
        
        attack_diff = (home_strength.get('attack_rating', 70) - 
                      away_strength.get('defense_rating', 70)) / 100
        
        matchup_score = attack_diff
        lambda_impact = 1.0 + matchup_score * 0.12
        
        return {
            'matchup_score': matchup_score,
            'position_advantages': {'overall': attack_diff},
            'key_mismatches': [],
            'lambda_impact': lambda_impact
        }
    
    def _analyze_baseball_positions(self, home_lineup: Dict, away_lineup: Dict) -> Dict:
        """야구 포지션 매치업 (투수 vs 타자)"""
        
        home_strength = home_lineup.get('team_strength', {})
        away_strength = away_lineup.get('team_strength', {})
        
        # 홈 타자 vs 원정 투수
        home_attack = home_strength.get('attack_rating', 70)
        away_pitcher = away_strength.get('pitcher_rating', away_strength.get('defense_rating', 70))
        
        pitcher_vs_batter = (home_attack - away_pitcher) / 100
        
        matchup_score = pitcher_vs_batter
        lambda_impact = 1.0 + matchup_score * 0.20  # 야구는 투수 영향 큼
        
        key_mismatches = []
        if abs(pitcher_vs_batter) > 0.15:
            key_mismatches.append(f"투수 vs 타자 매치업 ({pitcher_vs_batter:+.2f})")
        
        return {
            'matchup_score': matchup_score,
            'position_advantages': {'pitcher_vs_batter': pitcher_vs_batter},
            'key_mismatches': key_mismatches,
            'lambda_impact': lambda_impact
        }
    
    def _analyze_volleyball_positions(self, home_lineup: Dict, away_lineup: Dict) -> Dict:
        """배구 포지션 매치업"""
        
        home_strength = home_lineup.get('team_strength', {})
        away_strength = away_lineup.get('team_strength', {})
        
        attack_diff = (home_strength.get('attack_rating', 70) -
                      away_strength.get('defense_rating', 70)) / 100
        
        matchup_score = attack_diff
        lambda_impact = 1.0 + matchup_score * 0.10
        
        return {
            'matchup_score': matchup_score,
            'position_advantages': {'overall': attack_diff},
            'key_mismatches': [],
            'lambda_impact': lambda_impact
        }


# 싱글톤 인스턴스
_tactical_system = None

def get_tactical_system() -> TacticalMatchupSystem:
    """TacticalMatchupSystem 싱글톤 반환"""
    global _tactical_system
    if _tactical_system is None:
        _tactical_system = TacticalMatchupSystem()
    return _tactical_system

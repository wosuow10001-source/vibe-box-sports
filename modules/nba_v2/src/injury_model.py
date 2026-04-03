from typing import Dict, List, Tuple
import numpy as np
from modules.nba_v2.src.utils import logger

class NBAInjuryModel:
    """V2 부상 영향 모델: 선수별 역할을 고려한 팀 전력 하향 조정"""
    
    # 가중치 설정 (사용자 가이드 준수)
    ROLE_WEIGHTS = {
        'star': 1.5,
        'starter': 1.2,
        'bench': 0.8
    }
    
    def calculate_team_penalty(self, injuries: List[Dict]) -> Tuple[float, float, float]:
        """[SENIOR PATCH] 상세 역할(Star, Playmaker, Defender)을 고려한 정밀 페널티 계산"""
        if not injuries:
            return 0.0, 0.0, 0.0
            
        off_penalty = 0.0
        def_penalty = 0.0
        max_usage_lost = 0.0
        
        for player in injuries:
            role = player.get('role', 'bench').lower()
            weight = self.ROLE_WEIGHTS.get(role, 0.8)
            
            # Impact Score = (Minutes * Usage * BPM) * RoleWeight
            # BPM baseline 0, Minutes baseline 30, Usage baseline 0.20
            min_factor = player.get('mpg', 25) / 30.0
            usage = player.get('usage', 0.20)
            bpm_factor = (player.get('bpm', 0) + 5) / 5.0 # BPM 0 -> 1.0, BPM 5 -> 2.0
            
            impact_score = (min_factor * usage * bpm_factor) * weight
            
            # [SENIOR PATCH] Multipliers for specific star roles
            if player.get('is_primary_star'): impact_score *= 1.5
            if player.get('is_primary_ball_handler'): impact_score *= 1.3
            if player.get('is_defensive_anchor'): impact_score *= 1.2
            
            off_penalty += (impact_score * 5.0)
            def_penalty += (impact_score * 3.0)
            
            if usage > max_usage_lost:
                max_usage_lost = usage
                
        return off_penalty, def_penalty, max_usage_lost

    def apply_to_ratings(self, ortg: float, drtg: float, injuries: List[Dict]) -> Tuple[float, float]:
        """조정된 ORtg, DRtg 및 하드 페널티 적용"""
        off_p, def_p, max_usage = self.calculate_team_penalty(injuries)
        
        final_ortg = ortg - off_p
        final_drtg = drtg + def_p
        
        # [SENIOR PATCH] HARD PENALTY for losing top usage player
        # Top usage is usually > 0.28
        if max_usage > 0.25:
            final_ortg -= 6
            final_drtg += 2
            
        return final_ortg, final_drtg

    def calculate_lineup_stability(self, team_roster: List[Dict], injuries: List[Dict]) -> float:
        """[V2.1] 라인업 안정성 점수 계산: 1 - (부상 주전 시간 / 전체 팀 시간)"""
        if not injuries:
            return 1.0
            
        total_team_minutes = sum(p.get('mpg', 0) for p in team_roster)
        if total_team_minutes == 0: return 1.0
        
        injured_player_names = [i.get('player') for i in injuries]
        injured_minutes = sum(p.get('mpg', 0) for p in team_roster if p.get('name') in injured_player_names)
        
        stability = 1.0 - (injured_minutes / total_team_minutes)
        return float(np.clip(stability, 0, 1))

    def calculate_on_off_impact(self, injuries: List[Dict]) -> float:
        """[V2.1] On/Off 임팩트 모델 기반 넷 레이팅 조정값 계산"""
        if not injuries:
            return 0.0
            
        total_on_off_effect = 0.0
        for player in injuries:
            # On/Off Impact: 팀이 해당 선수와 함께할 때의 NetRating - 없을 때의 NetRating
            # 데이터 수집 단계에서 가져오지 못할 경우 BPM(Box Plus-Minus)을 대용으로 사용
            on_off = player.get('on_off', player.get('bpm', 0.0) * 1.5)
            total_on_off_effect += on_off * 0.7 # 보수적 조정 (70% 반영)
            
        return total_on_off_effect

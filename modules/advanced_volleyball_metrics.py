"""
배구 고급 메트릭스 시스템
- Spike Success Rate - 스파이크 성공률
- Block Efficiency - 블로킹 효율
- Jump Height/Frequency - 점프 높이 및 빈도
- Set Efficiency - 세트 효율성
- Position-based Workload - 포지션별 워크로드
"""

import numpy as np
from typing import Dict, List, Optional


class AdvancedVolleyballMetrics:
    """배구 고급 메트릭스 계산 및 팀 능력치 변환"""
    
    def __init__(self, league: str = "V-League"):
        self.league = league
        
        # 리그별 평균값
        self.league_averages = {
            "V-League": {
                "spike_success_rate": 0.45,
                "block_per_set": 2.5,
                "dig_per_set": 12.0,
                "set_efficiency": 0.60,
                "avg_jump_height": 320,  # cm
                "avg_jumps_per_set": 25
            },
            "Serie A": {
                "spike_success_rate": 0.48,
                "block_per_set": 2.8,
                "dig_per_set": 13.0,
                "set_efficiency": 0.65,
                "avg_jump_height": 330,
                "avg_jumps_per_set": 28
            },
            "Turkish League": {
                "spike_success_rate": 0.47,
                "block_per_set": 2.7,
                "dig_per_set": 12.5,
                "set_efficiency": 0.63,
                "avg_jump_height": 325,
                "avg_jumps_per_set": 27
            }
        }
        
        self.avg = self.league_averages.get(league, self.league_averages["V-League"])
        
        # 포지션별 가중치 및 워크로드
        self.position_weights = {
            'OH': {  # Outside Hitter (주공격수)
                'spike': 0.50, 'block': 0.15, 'dig': 0.20, 'set': 0.05,
                'jump_load': 1.0, 'movement_load': 0.9
            },
            'MB': {  # Middle Blocker (미들 블로커)
                'spike': 0.30, 'block': 0.40, 'dig': 0.10, 'set': 0.05,
                'jump_load': 1.2, 'movement_load': 0.7
            },
            'S': {  # Setter (세터)
                'spike': 0.05, 'block': 0.10, 'dig': 0.15, 'set': 0.60,
                'jump_load': 0.6, 'movement_load': 1.0
            },
            'OP': {  # Opposite (라이트)
                'spike': 0.45, 'block': 0.25, 'dig': 0.15, 'set': 0.05,
                'jump_load': 1.1, 'movement_load': 0.8
            },
            'L': {  # Libero (리베로)
                'spike': 0.00, 'block': 0.00, 'dig': 0.70, 'set': 0.20,
                'jump_load': 0.1, 'movement_load': 1.2
            }
        }
    
    def calculate_spike_success_rate(self, player_stats: Dict) -> float:
        """
        스파이크 성공률 계산
        
        성공률 = (킬 - 에러) / 총 시도
        """
        
        kills = player_stats.get('kills', 0)
        errors = player_stats.get('errors', 0)
        attempts = player_stats.get('attempts', 0)
        
        if attempts > 0:
            success_rate = (kills - errors) / attempts
        else:
            success_rate = self.avg['spike_success_rate']
        
        # 0~1 범위로 제한
        success_rate = max(0.0, min(1.0, success_rate))
        
        return round(success_rate, 3)
    
    def calculate_block_efficiency(self, player_stats: Dict) -> float:
        """
        블로킹 효율 계산
        
        블록 포인트 + 블록 터치 기여도
        """
        
        block_solos = player_stats.get('block_solos', 0)
        block_assists = player_stats.get('block_assists', 0)
        sets_played = player_stats.get('sets_played', 1)
        
        # 블록 포인트 (솔로 블록 = 1점, 어시스트 = 0.5점)
        block_points = block_solos + (block_assists * 0.5)
        
        # 세트당 블록
        blocks_per_set = block_points / sets_played if sets_played > 0 else 0
        
        return round(blocks_per_set, 2)
    
    def calculate_dig_efficiency(self, player_stats: Dict) -> float:
        """
        디그 효율 계산
        
        세트당 디그 수
        """
        
        digs = player_stats.get('digs', 0)
        sets_played = player_stats.get('sets_played', 1)
        
        digs_per_set = digs / sets_played if sets_played > 0 else 0
        
        return round(digs_per_set, 2)
    
    def calculate_set_efficiency(self, player_stats: Dict) -> float:
        """
        세트 효율성 계산 (세터 전용)
        
        어시스트 / 총 세트 시도
        """
        
        assists = player_stats.get('assists', 0)
        set_attempts = player_stats.get('set_attempts', assists * 1.5)
        
        if set_attempts > 0:
            efficiency = assists / set_attempts
        else:
            efficiency = self.avg['set_efficiency']
        
        return round(efficiency, 3)
    
    def calculate_jump_workload(self, player_stats: Dict) -> Dict:
        """
        점프 워크로드 계산
        
        점프 높이, 빈도, 피로도
        """
        
        position = player_stats.get('position', 'OH')
        sets_played = player_stats.get('sets_played', 1)
        
        # 점프 높이 (cm)
        jump_height = player_stats.get('jump_height', self.avg['avg_jump_height'])
        
        # 점프 빈도 추정
        kills = player_stats.get('kills', 0)
        blocks = player_stats.get('block_solos', 0) + player_stats.get('block_assists', 0)
        
        # 포지션별 점프 빈도
        weights = self.position_weights.get(position, self.position_weights['OH'])
        estimated_jumps = (kills * 1.5 + blocks * 2) * weights['jump_load']
        
        jumps_per_set = estimated_jumps / sets_played if sets_played > 0 else 0
        
        # 워크로드 점수 (점프 높이 * 빈도)
        workload_score = (jump_height / 100) * jumps_per_set
        
        return {
            'jump_height': jump_height,
            'jumps_per_set': round(jumps_per_set, 1),
            'workload_score': round(workload_score, 2)
        }
    
    def calculate_movement_workload(self, player_stats: Dict) -> float:
        """
        이동 워크로드 계산
        
        디그, 리시브 등 이동 거리 추정
        """
        
        position = player_stats.get('position', 'OH')
        digs = player_stats.get('digs', 0)
        receptions = player_stats.get('receptions', 0)
        sets_played = player_stats.get('sets_played', 1)
        
        # 포지션별 이동 가중치
        weights = self.position_weights.get(position, self.position_weights['OH'])
        
        # 이동 거리 추정 (디그 + 리시브)
        movement_actions = (digs + receptions) * weights['movement_load']
        
        movement_per_set = movement_actions / sets_played if sets_played > 0 else 0
        
        return round(movement_per_set, 2)
    
    def calculate_all_metrics(self, player_stats: Dict) -> Dict:
        """모든 고급 메트릭스 계산"""
        
        position = player_stats.get('position', 'OH')
        
        spike_rate = self.calculate_spike_success_rate(player_stats)
        block_eff = self.calculate_block_efficiency(player_stats)
        dig_eff = self.calculate_dig_efficiency(player_stats)
        set_eff = self.calculate_set_efficiency(player_stats)
        jump_workload = self.calculate_jump_workload(player_stats)
        movement_workload = self.calculate_movement_workload(player_stats)
        
        # 포지션별 가중치
        weights = self.position_weights.get(position, self.position_weights['OH'])
        
        # 종합 평가
        attack_rating = (
            spike_rate * 100 * weights['spike'] +
            block_eff * 10 * weights['block']
        )
        
        defense_rating = (
            dig_eff * 5 * weights['dig'] +
            block_eff * 10 * weights['block']
        )
        
        playmaking_rating = set_eff * 100 * weights['set']
        
        overall_rating = attack_rating + defense_rating + playmaking_rating
        
        # 피로도 (워크로드가 높을수록 피로)
        fatigue_factor = 1.0 - min(0.3, (jump_workload['workload_score'] + movement_workload) / 200)
        
        return {
            'spike_success_rate': spike_rate,
            'block_efficiency': block_eff,
            'dig_efficiency': dig_eff,
            'set_efficiency': set_eff,
            'jump_height': jump_workload['jump_height'],
            'jumps_per_set': jump_workload['jumps_per_set'],
            'jump_workload': jump_workload['workload_score'],
            'movement_workload': movement_workload,
            'attack_rating': round(attack_rating, 2),
            'defense_rating': round(defense_rating, 2),
            'playmaking_rating': round(playmaking_rating, 2),
            'overall_rating': round(overall_rating, 2),
            'fatigue_factor': round(fatigue_factor, 3)
        }
    
    def calculate_team_strength_from_players(self, players: List[Dict]) -> Dict:
        """선수 메트릭스 기반 팀 전력 계산"""
        
        if not players:
            return self._default_team_strength()
        
        total_spike_rate = 0
        total_block_eff = 0
        total_dig_eff = 0
        total_set_eff = 0
        total_workload = 0
        
        position_count = {'OH': 0, 'MB': 0, 'S': 0, 'OP': 0, 'L': 0}
        
        attackers = []
        defenders = []
        setters = []
        
        for player in players:
            metrics = self.calculate_all_metrics(player)
            position = player.get('position', 'OH')
            
            total_spike_rate += metrics['spike_success_rate']
            total_block_eff += metrics['block_efficiency']
            total_dig_eff += metrics['dig_efficiency']
            total_set_eff += metrics['set_efficiency']
            total_workload += metrics['jump_workload'] + metrics['movement_workload']
            
            position_count[position] = position_count.get(position, 0) + 1
            
            # 역할별 분류
            if position in ['OH', 'OP']:
                attackers.append(metrics)
            if position in ['MB', 'L']:
                defenders.append(metrics)
            if position == 'S':
                setters.append(metrics)
        
        num_players = len(players)
        
        # 팀 공격력 (스파이크 성공률 + 블록)
        team_spike_rate = total_spike_rate / num_players
        team_block_eff = total_block_eff / num_players
        
        # 팀 수비력 (디그 + 블록)
        team_dig_eff = total_dig_eff / num_players
        
        # 팀 세트 효율
        team_set_eff = total_set_eff / len(setters) if setters else self.avg['set_efficiency']
        
        # 팀 워크로드 (피로도)
        avg_workload = total_workload / num_players
        team_fatigue = 1.0 - min(0.3, avg_workload / 100)
        
        return {
            'team_spike_rate': round(team_spike_rate, 3),
            'team_block_eff': round(team_block_eff, 2),
            'team_dig_eff': round(team_dig_eff, 2),
            'team_set_eff': round(team_set_eff, 3),
            'avg_workload': round(avg_workload, 2),
            'team_fatigue': round(team_fatigue, 3),
            'attack_rating': round(team_spike_rate * 100 + team_block_eff * 10, 1),
            'defense_rating': round(team_dig_eff * 5 + team_block_eff * 10, 1),
            'position_balance': position_count
        }
    
    def predict_set_win_probability(self, home_strength: Dict, 
                                    away_strength: Dict,
                                    home_advantage: float = 0.05) -> float:
        """
        세트 승률 예측
        
        Args:
            home_strength: 홈팀 전력
            away_strength: 원정팀 전력
            home_advantage: 홈 어드밴티지 (0.05 = 5% 보너스)
        
        Returns:
            홈팀 세트 승률
        """
        
        # 공격력 비교
        home_attack = home_strength['attack_rating']
        away_attack = away_strength['attack_rating']
        
        # 수비력 비교 (상대 공격을 막는 능력)
        home_defense = home_strength['defense_rating']
        away_defense = away_strength['defense_rating']
        
        # 피로도 반영
        home_fatigue = home_strength['team_fatigue']
        away_fatigue = away_strength['team_fatigue']
        
        # 종합 전력
        home_total = (home_attack * 0.5 + home_defense * 0.3 + home_fatigue * 20) * (1 + home_advantage)
        away_total = (away_attack * 0.5 + away_defense * 0.3 + away_fatigue * 20)
        
        # 승률 계산
        total = home_total + away_total
        if total > 0:
            home_prob = home_total / total
        else:
            home_prob = 0.5
        
        # 0.1 ~ 0.9 범위로 제한
        home_prob = max(0.1, min(0.9, home_prob))
        
        return round(home_prob, 3)
    
    def _default_team_strength(self) -> Dict:
        """기본 팀 전력"""
        return {
            'team_spike_rate': self.avg['spike_success_rate'],
            'team_block_eff': self.avg['block_per_set'],
            'team_dig_eff': self.avg['dig_per_set'],
            'team_set_eff': self.avg['set_efficiency'],
            'avg_workload': 50.0,
            'team_fatigue': 0.85,
            'attack_rating': 70.0,
            'defense_rating': 70.0,
            'position_balance': {'OH': 2, 'MB': 2, 'S': 1, 'OP': 1, 'L': 1}
        }


# 싱글톤 인스턴스
_metrics_volleyball = {}

def get_volleyball_metrics(league: str = "V-League") -> AdvancedVolleyballMetrics:
    """AdvancedVolleyballMetrics 싱글톤 반환"""
    global _metrics_volleyball
    
    if league not in _metrics_volleyball:
        _metrics_volleyball[league] = AdvancedVolleyballMetrics(league)
    
    return _metrics_volleyball[league]

"""
축구 고급 메트릭스 시스템
- xG (Expected Goals) - 기대 득점
- xA (Expected Assists) - 기대 어시스트
- PPDA (Passes Per Defensive Action) - 압박 강도
- xGChain, xGBuildup - 공격 기여도
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class AdvancedSoccerMetrics:
    """축구 고급 메트릭스 계산 및 팀 능력치 변환"""
    
    def __init__(self, league: str = "K-League"):
        self.league = league
        
        # 리그별 평균값
        self.league_averages = {
            "K-League": {
                "xg_per_game": 1.3,
                "xa_per_game": 1.0,
                "ppda": 12.0,
                "possession": 50.0,
                "pass_completion": 78.0
            },
            "La Liga": {
                "xg_per_game": 1.4,
                "xa_per_game": 1.1,
                "ppda": 10.5,
                "possession": 52.0,
                "pass_completion": 82.0
            },
            "EPL": {
                "xg_per_game": 1.5,
                "xa_per_game": 1.2,
                "ppda": 11.0,
                "possession": 51.0,
                "pass_completion": 80.0
            },
            "Bundesliga": {
                "xg_per_game": 1.6,
                "xa_per_game": 1.3,
                "ppda": 9.5,
                "possession": 53.0,
                "pass_completion": 81.0
            },
            "Serie A": {
                "xg_per_game": 1.3,
                "xa_per_game": 1.0,
                "ppda": 11.5,
                "possession": 50.0,
                "pass_completion": 83.0
            }
        }
        
        self.avg = self.league_averages.get(league, self.league_averages["K-League"])
        
        # 포지션별 가중치
        self.position_weights = {
            'FW': {'attack': 0.50, 'defense': 0.10},
            'MF': {'attack': 0.30, 'defense': 0.30},
            'DF': {'attack': 0.10, 'defense': 0.50},
            'GK': {'attack': 0.00, 'defense': 0.60}
        }
    
    def calculate_xg(self, player_stats: Dict) -> float:
        """
        xG (Expected Goals) 계산
        
        슈팅 위치, 각도, 상황을 고려한 기대 득점
        """
        
        # 기본 통계
        goals = player_stats.get('goals', 0)
        shots = player_stats.get('shots', 0)
        shots_on_target = player_stats.get('shots_on_target', 0)
        
        # 슈팅 효율
        if shots > 0:
            shot_accuracy = shots_on_target / shots
            conversion_rate = goals / shots
        else:
            shot_accuracy = 0.3
            conversion_rate = 0.1
        
        # xG 추정 (실제로는 각 슈팅의 위치/각도 필요)
        # 간소화: 골 수 + 슈팅 품질
        xg = goals * 0.7 + shots * conversion_rate * 0.3
        
        # 포지션 조정
        position = player_stats.get('position', 'MF')
        if position == 'FW':
            xg *= 1.2
        elif position == 'MF':
            xg *= 1.0
        elif position == 'DF':
            xg *= 0.5
        
        return round(xg, 2)
    
    def calculate_xa(self, player_stats: Dict) -> float:
        """
        xA (Expected Assists) 계산
        
        패스 품질을 고려한 기대 어시스트
        """
        
        # 기본 통계
        assists = player_stats.get('assists', 0)
        key_passes = player_stats.get('key_passes', assists * 2)
        
        # xA 추정
        # 실제로는 각 패스의 위치/상황 필요
        xa = assists * 0.8 + key_passes * 0.1
        
        # 포지션 조정
        position = player_stats.get('position', 'MF')
        if position == 'MF':
            xa *= 1.2
        elif position == 'FW':
            xa *= 1.0
        elif position == 'DF':
            xa *= 0.7
        
        return round(xa, 2)
    
    def calculate_xgchain(self, player_stats: Dict) -> float:
        """
        xGChain - 공격 빌드업 기여도
        
        선수가 관여한 공격의 총 xG
        """
        
        xg = self.calculate_xg(player_stats)
        xa = self.calculate_xa(player_stats)
        
        # 패스 기여도
        passes = player_stats.get('passes', 0)
        pass_completion = player_stats.get('pass_completion', 75) / 100
        
        # xGChain 추정
        xgchain = xg + xa + (passes * pass_completion * 0.001)
        
        return round(xgchain, 2)
    
    def calculate_ppda(self, team_stats: Dict) -> float:
        """
        PPDA (Passes Per Defensive Action) 계산
        
        상대의 패스 수 / 우리의 수비 액션
        낮을수록 압박이 강함
        """
        
        # 상대 패스 수
        opp_passes = team_stats.get('opp_passes', 400)
        
        # 우리의 수비 액션 (태클 + 인터셉트)
        tackles = team_stats.get('tackles', 15)
        interceptions = team_stats.get('interceptions', 10)
        
        defensive_actions = tackles + interceptions
        
        if defensive_actions > 0:
            ppda = opp_passes / defensive_actions
        else:
            ppda = self.avg['ppda']
        
        return round(ppda, 2)
    
    def calculate_defensive_metrics(self, player_stats: Dict) -> Dict:
        """수비 메트릭스 계산"""
        
        tackles = player_stats.get('tackles', 0)
        interceptions = player_stats.get('interceptions', 0)
        clearances = player_stats.get('clearances', 0)
        blocks = player_stats.get('blocks', 0)
        
        # 수비 기여도
        defensive_contribution = (
            tackles * 1.0 +
            interceptions * 1.2 +
            clearances * 0.8 +
            blocks * 1.5
        )
        
        return {
            'tackles': tackles,
            'interceptions': interceptions,
            'defensive_contribution': round(defensive_contribution, 2)
        }
    
    def calculate_all_metrics(self, player_stats: Dict) -> Dict:
        """모든 고급 메트릭스 계산"""
        
        xg = self.calculate_xg(player_stats)
        xa = self.calculate_xa(player_stats)
        xgchain = self.calculate_xgchain(player_stats)
        defensive = self.calculate_defensive_metrics(player_stats)
        
        # 종합 평가
        position = player_stats.get('position', 'MF')
        weights = self.position_weights.get(position, self.position_weights['MF'])
        
        attack_rating = (xg * 10 + xa * 8 + xgchain * 5) * weights['attack']
        defense_rating = defensive['defensive_contribution'] * weights['defense']
        
        overall_rating = attack_rating + defense_rating
        
        return {
            'xg': xg,
            'xa': xa,
            'xgchain': xgchain,
            'tackles': defensive['tackles'],
            'interceptions': defensive['interceptions'],
            'defensive_contribution': defensive['defensive_contribution'],
            'attack_rating': round(attack_rating, 2),
            'defense_rating': round(defense_rating, 2),
            'overall_rating': round(overall_rating, 2)
        }
    
    def calculate_team_strength_from_players(self, players: List[Dict]) -> Dict:
        """선수 메트릭스 기반 팀 전력 계산"""
        
        if not players:
            return self._default_team_strength()
        
        total_xg = 0
        total_xa = 0
        total_defensive = 0
        
        position_count = {'FW': 0, 'MF': 0, 'DF': 0, 'GK': 0}
        
        for player in players:
            metrics = self.calculate_all_metrics(player)
            
            total_xg += metrics['xg']
            total_xa += metrics['xa']
            total_defensive += metrics['defensive_contribution']
            
            position = player.get('position', 'MF')
            position_count[position] += 1
        
        # 팀 공격력 (xG + xA 기반)
        team_xg = total_xg
        team_xa = total_xa
        
        # 팀 수비력 (수비 기여도 기반)
        team_defensive = total_defensive
        
        # 득점 예상 (Poisson 모델용)
        expected_goals = team_xg * 1.1  # xG에 약간의 보정
        expected_conceded = self.avg['xg_per_game'] * 2 - (team_defensive / 20)
        
        return {
            'team_xg': round(team_xg, 2),
            'team_xa': round(team_xa, 2),
            'team_defensive': round(team_defensive, 2),
            'expected_goals': round(expected_goals, 2),
            'expected_conceded': round(max(0.5, expected_conceded), 2),
            'attack_rating': round(team_xg * 10 + team_xa * 8, 1),
            'defense_rating': round(team_defensive * 2, 1),
            'position_balance': position_count
        }
    
    def predict_match_poisson(self, home_strength: Dict, away_strength: Dict,
                             home_advantage: float = 0.3) -> Dict:
        """
        Poisson 모델 기반 경기 예측
        
        Args:
            home_strength: 홈팀 전력
            away_strength: 원정팀 전력
            home_advantage: 홈 어드밴티지 (득점 증가)
        
        Returns:
            예측 결과
        """
        
        # 예상 득점 (Poisson 분포의 lambda)
        home_lambda = home_strength['expected_goals'] + home_advantage
        away_lambda = away_strength['expected_goals']
        
        # 상대 수비력 반영
        home_lambda *= (2.0 / (1 + away_strength['defense_rating'] / 100))
        away_lambda *= (2.0 / (1 + home_strength['defense_rating'] / 100))
        
        # Poisson 분포로 득점 확률 계산
        max_goals = 6
        home_probs = [self._poisson_prob(home_lambda, k) for k in range(max_goals + 1)]
        away_probs = [self._poisson_prob(away_lambda, k) for k in range(max_goals + 1)]
        
        # 승/무/패 확률 계산
        home_win_prob = 0
        draw_prob = 0
        away_win_prob = 0
        
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                prob = home_probs[h] * away_probs[a]
                
                if h > a:
                    home_win_prob += prob
                elif h == a:
                    draw_prob += prob
                else:
                    away_win_prob += prob
        
        # 가장 가능성 높은 스코어
        most_likely_score = self._find_most_likely_score(home_probs, away_probs, max_goals)
        
        return {
            'home_win_prob': round(home_win_prob, 3),
            'draw_prob': round(draw_prob, 3),
            'away_win_prob': round(away_win_prob, 3),
            'expected_score_home': round(home_lambda, 1),
            'expected_score_away': round(away_lambda, 1),
            'most_likely_score': most_likely_score,
            'home_lambda': round(home_lambda, 2),
            'away_lambda': round(away_lambda, 2)
        }
    
    def _poisson_prob(self, lambda_val: float, k: int) -> float:
        """Poisson 확률 계산"""
        from math import exp, factorial
        return (lambda_val ** k) * exp(-lambda_val) / factorial(k)
    
    def _find_most_likely_score(self, home_probs: List[float], 
                                away_probs: List[float], max_goals: int) -> Tuple[int, int]:
        """가장 가능성 높은 스코어 찾기"""
        
        max_prob = 0
        best_score = (1, 1)
        
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                prob = home_probs[h] * away_probs[a]
                if prob > max_prob:
                    max_prob = prob
                    best_score = (h, a)
        
        return best_score
    
    def _default_team_strength(self) -> Dict:
        """기본 팀 전력"""
        return {
            'team_xg': self.avg['xg_per_game'],
            'team_xa': self.avg['xa_per_game'],
            'team_defensive': 20.0,
            'expected_goals': self.avg['xg_per_game'],
            'expected_conceded': self.avg['xg_per_game'],
            'attack_rating': 70.0,
            'defense_rating': 70.0,
            'position_balance': {'FW': 3, 'MF': 4, 'DF': 3, 'GK': 1}
        }


# 싱글톤 인스턴스
_metrics_soccer = {}

def get_soccer_metrics(league: str = "K-League") -> AdvancedSoccerMetrics:
    """AdvancedSoccerMetrics 싱글톤 반환"""
    global _metrics_soccer
    
    if league not in _metrics_soccer:
        _metrics_soccer[league] = AdvancedSoccerMetrics(league)
    
    return _metrics_soccer[league]

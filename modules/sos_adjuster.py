"""
V6 Strength of Schedule (SoS) Adjuster

핵심 원리:
  약팀 상대 xG 2.5 ≠ 강팀 상대 xG 2.5
  
  adjusted_xG = raw_xG × (league_avg_xGA / opponent_avg_xGA)
  
  예: 리그 평균 xGA = 1.3
      팀 A의 raw_xG = 2.0 (약팀 상대, opp_xGA = 2.0)
      → adjusted = 2.0 × (1.3 / 2.0) = 1.30 ← 예상보다 강한 팀이 아님
      
      팀 B의 raw_xG = 2.0 (강팀 상대, opp_xGA = 0.8)
      → adjusted = 2.0 × (1.3 / 0.8) = 3.25 ← 매우 강한 공격력
"""

from typing import Dict, Optional


class SoSAdjuster:
    """
    상대 강도 보정 (Strength of Schedule).
    팀의 raw 스탯을 상대의 수비/공격 수준에 따라 보정.
    """
    
    # 리그별 평균 경기당 득점 (2024-25 시즌 기준)
    LEAGUE_AVG_GOALS = {
        "EPL":        1.35,
        "La Liga":    1.25,
        "Serie A":    1.25,
        "Bundesliga": 1.50,
        "K리그1":     1.20,
        "MLS":        1.40,
    }
    
    def __init__(self, league: str = "EPL"):
        self.league = league
        self.league_avg = self.LEAGUE_AVG_GOALS.get(league, 1.30)
        self.team_stats: Dict[str, dict] = {}
    
    def register_team(self, team_name: str, avg_goals: float, avg_conceded: float,
                      xg: float = None, xga: float = None):
        """
        팀 등록.
        
        Args:
            avg_goals: 경기당 평균 득점
            avg_conceded: 경기당 평균 실점
            xg: 경기당 xG (있으면 xG 사용, 없으면 actual goals 사용)
            xga: 경기당 xGA
        """
        self.team_stats[team_name] = {
            'avg_goals': avg_goals,
            'avg_conceded': avg_conceded,
            'xg': xg if xg and xg > 0.01 else avg_goals,
            'xga': xga if xga and xga > 0.01 else avg_conceded
        }
    
    def adjust_attack(self, team_name: str, opponent_name: str) -> float:
        """
        상대 수비력 기반 공격력 보정.
        
        Returns:
            adjusted_xg: 보정된 기대 득점
        """
        team = self.team_stats.get(team_name)
        opponent = self.team_stats.get(opponent_name)
        
        if not team or not opponent:
            return team['xg'] if team else self.league_avg
        
        raw_xg = team['xg']
        opp_xga = opponent['xga']
        
        if opp_xga <= 0.01:
            opp_xga = self.league_avg
        
        # SoS adjustment
        adjustment_factor = self.league_avg / opp_xga
        
        # 극단적 보정 방지 (0.6x ~ 1.6x)
        adjustment_factor = max(0.6, min(1.6, adjustment_factor))
        
        adjusted = raw_xg * adjustment_factor
        return round(max(0.3, min(3.5, adjusted)), 3)
    
    def adjust_defense(self, team_name: str, opponent_name: str) -> float:
        """
        상대 공격력 기반 수비력 보정.
        
        Returns:
            adjusted_xga: 보정된 기대 실점
        """
        team = self.team_stats.get(team_name)
        opponent = self.team_stats.get(opponent_name)
        
        if not team or not opponent:
            return team['xga'] if team else self.league_avg
        
        raw_xga = team['xga']
        opp_xg = opponent['xg']
        
        if opp_xg <= 0.01:
            opp_xg = self.league_avg
        
        adjustment_factor = self.league_avg / opp_xg
        adjustment_factor = max(0.6, min(1.6, adjustment_factor))
        
        adjusted = raw_xga * adjustment_factor
        return round(max(0.3, min(3.5, adjusted)), 3)
    
    def get_adjusted_xg_pair(self, home_team: str, away_team: str) -> tuple:
        """
        두 팀간 SoS 보정된 xG 쌍 반환.
        
        Returns:
            (home_adj_xg, away_adj_xg)
        """
        home_adj_xg = self.adjust_attack(home_team, away_team)
        away_adj_xg = self.adjust_attack(away_team, home_team)
        
        return (home_adj_xg, away_adj_xg)
    
    def calculate_league_avg(self) -> float:
        """등록된 팀들로 리그 평균 재계산"""
        if not self.team_stats:
            return self.league_avg
        
        goals = [t['avg_goals'] for t in self.team_stats.values()]
        self.league_avg = sum(goals) / len(goals)
        return self.league_avg

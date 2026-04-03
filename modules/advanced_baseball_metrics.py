"""
야구 고급 메트릭스 시스템
- OPS (On-base Plus Slugging) - 출루율 + 장타율
- wOBA (Weighted On-Base Average) - 가중 출루율
- ERA+ (Adjusted ERA) - 조정 평균자책점
- FIP (Fielding Independent Pitching) - 수비 무관 투구
- WAR (Wins Above Replacement) - 대체 선수 대비 승리 기여
"""

import numpy as np
from typing import Dict, List, Optional


class AdvancedBaseballMetrics:
    """야구 고급 메트릭스 계산 및 팀 능력치 변환"""
    
    def __init__(self, league: str = "KBO"):
        self.league = league
        
        # 리그별 평균값
        self.league_averages = {
            "KBO": {
                "avg_runs": 4.8,
                "avg_era": 4.5,
                "avg_obp": 0.340,
                "avg_slg": 0.420,
                "avg_ops": 0.760,
                "avg_woba": 0.330,
                "park_factor": 1.0
            },
            "MLB": {
                "avg_runs": 4.5,
                "avg_era": 4.2,
                "avg_obp": 0.320,
                "avg_slg": 0.410,
                "avg_ops": 0.730,
                "avg_woba": 0.320,
                "park_factor": 1.0
            },
            "NPB": {
                "avg_runs": 4.3,
                "avg_era": 3.9,
                "avg_obp": 0.325,
                "avg_slg": 0.400,
                "avg_ops": 0.725,
                "avg_woba": 0.315,
                "park_factor": 1.0
            }
        }
        
        self.avg = self.league_averages.get(league, self.league_averages["KBO"])
        
        # wOBA 가중치 (2024 기준)
        self.woba_weights = {
            'bb': 0.69,  # 볼넷
            'hbp': 0.72,  # 몸에 맞는 공
            '1b': 0.88,  # 1루타
            '2b': 1.24,  # 2루타
            '3b': 1.56,  # 3루타
            'hr': 1.95   # 홈런
        }
        
        # FIP 상수 (리그 평균 ERA와 FIP를 맞추기 위한 값)
        self.fip_constant = 3.10
    
    def calculate_ops(self, batter_stats: Dict) -> float:
        """
        OPS (On-base Plus Slugging) 계산
        
        OPS = OBP + SLG
        OBP = (H + BB + HBP) / (AB + BB + HBP + SF)
        SLG = (1B + 2*2B + 3*3B + 4*HR) / AB
        """
        
        # 타석 정보
        ab = batter_stats.get('ab', 0)  # 타수
        h = batter_stats.get('h', 0)  # 안타
        bb = batter_stats.get('bb', 0)  # 볼넷
        hbp = batter_stats.get('hbp', 0)  # 몸에 맞는 공
        sf = batter_stats.get('sf', 0)  # 희생 플라이
        
        # 안타 종류
        singles = batter_stats.get('1b', h * 0.7)  # 1루타
        doubles = batter_stats.get('2b', h * 0.2)  # 2루타
        triples = batter_stats.get('3b', h * 0.02)  # 3루타
        hr = batter_stats.get('hr', h * 0.08)  # 홈런
        
        # OBP 계산
        obp_denominator = ab + bb + hbp + sf
        if obp_denominator > 0:
            obp = (h + bb + hbp) / obp_denominator
        else:
            obp = self.avg['avg_obp']
        
        # SLG 계산
        if ab > 0:
            total_bases = singles + (2 * doubles) + (3 * triples) + (4 * hr)
            slg = total_bases / ab
        else:
            slg = self.avg['avg_slg']
        
        ops = obp + slg
        
        return round(ops, 3)
    
    def calculate_woba(self, batter_stats: Dict) -> float:
        """
        wOBA (Weighted On-Base Average) 계산
        
        각 결과에 가중치를 부여한 출루율
        """
        
        # 타석 정보
        ab = batter_stats.get('ab', 0)
        bb = batter_stats.get('bb', 0)
        hbp = batter_stats.get('hbp', 0)
        sf = batter_stats.get('sf', 0)
        
        # 안타 종류
        h = batter_stats.get('h', 0)
        singles = batter_stats.get('1b', h * 0.7)
        doubles = batter_stats.get('2b', h * 0.2)
        triples = batter_stats.get('3b', h * 0.02)
        hr = batter_stats.get('hr', h * 0.08)
        
        # wOBA 계산
        numerator = (
            self.woba_weights['bb'] * bb +
            self.woba_weights['hbp'] * hbp +
            self.woba_weights['1b'] * singles +
            self.woba_weights['2b'] * doubles +
            self.woba_weights['3b'] * triples +
            self.woba_weights['hr'] * hr
        )
        
        denominator = ab + bb + sf + hbp
        
        if denominator > 0:
            woba = numerator / denominator
        else:
            woba = self.avg['avg_woba']
        
        return round(woba, 3)
    
    def calculate_era_plus(self, pitcher_stats: Dict) -> float:
        """
        ERA+ (Adjusted ERA) 계산
        
        ERA+ = 100 * (리그 평균 ERA / 투수 ERA) * 구장 보정
        100이 평균, 높을수록 좋음
        """
        
        era = pitcher_stats.get('era', self.avg['avg_era'])
        park_factor = pitcher_stats.get('park_factor', self.avg['park_factor'])
        
        if era > 0:
            era_plus = 100 * (self.avg['avg_era'] / era) * park_factor
        else:
            era_plus = 200  # ERA 0.00은 매우 우수
        
        return round(era_plus, 1)
    
    def calculate_fip(self, pitcher_stats: Dict) -> float:
        """
        FIP (Fielding Independent Pitching) 계산
        
        FIP = ((13*HR + 3*BB - 2*K) / IP) + FIP상수
        수비와 무관한 투수 능력 평가
        """
        
        hr = pitcher_stats.get('hr', 0)  # 피홈런
        bb = pitcher_stats.get('bb', 0)  # 볼넷
        k = pitcher_stats.get('k', 0)  # 삼진
        ip = pitcher_stats.get('ip', 1)  # 이닝
        
        if ip > 0:
            fip = ((13 * hr + 3 * bb - 2 * k) / ip) + self.fip_constant
        else:
            fip = self.avg['avg_era']
        
        return round(fip, 2)
    
    def calculate_war_batter(self, batter_stats: Dict) -> float:
        """
        타자 WAR (Wins Above Replacement) 계산
        
        간소화된 계산:
        WAR = (wRAA + 수비 + 주루 + 포지션 조정) / 10
        """
        
        woba = self.calculate_woba(batter_stats)
        pa = batter_stats.get('pa', batter_stats.get('ab', 0) * 1.1)  # 타석
        
        # wRAA (Weighted Runs Above Average)
        wraa = ((woba - self.avg['avg_woba']) / 1.15) * pa
        
        # 포지션 조정 (포수, 유격수 등은 가산점)
        position = batter_stats.get('position', 'OF')
        position_adjustment = {
            'C': 12.5, 'SS': 7.5, '2B': 3.0, 'CF': 2.5,
            '3B': 2.0, 'LF': -7.5, 'RF': -7.5, '1B': -12.5, 'DH': -17.5
        }
        pos_adj = position_adjustment.get(position, 0)
        
        # 수비 기여 (간소화)
        defensive_runs = batter_stats.get('defensive_runs', 0)
        
        # 주루 기여
        sb = batter_stats.get('sb', 0)  # 도루
        cs = batter_stats.get('cs', 0)  # 도루 실패
        baserunning_runs = (sb * 0.2) - (cs * 0.4)
        
        # WAR 계산
        war = (wraa + defensive_runs + baserunning_runs + pos_adj) / 10
        
        return round(war, 1)
    
    def calculate_war_pitcher(self, pitcher_stats: Dict) -> float:
        """
        투수 WAR 계산
        
        간소화된 계산:
        WAR = (리그 평균 실점 - FIP 기반 실점) * IP / 9 / 10
        """
        
        fip = self.calculate_fip(pitcher_stats)
        ip = pitcher_stats.get('ip', 0)
        
        # FIP 기반 실점
        fip_runs = fip * ip / 9
        
        # 리그 평균 실점
        league_runs = self.avg['avg_era'] * ip / 9
        
        # 대체 선수 대비 방어 실점
        runs_above_replacement = league_runs - fip_runs
        
        # WAR 계산
        war = runs_above_replacement / 10
        
        return round(war, 1)
    
    def calculate_all_metrics_batter(self, batter_stats: Dict) -> Dict:
        """타자 모든 고급 메트릭스 계산"""
        
        ops = self.calculate_ops(batter_stats)
        woba = self.calculate_woba(batter_stats)
        war = self.calculate_war_batter(batter_stats)
        
        # 종합 평가 (0-100 스케일)
        # OPS 0.900+ = 90+, 0.800 = 80, 0.700 = 70
        rating = min(100, max(50, (ops - 0.500) * 100))
        
        return {
            'ops': ops,
            'woba': woba,
            'war': war,
            'rating': round(rating, 1)
        }
    
    def calculate_all_metrics_pitcher(self, pitcher_stats: Dict) -> Dict:
        """투수 모든 고급 메트릭스 계산"""
        
        era_plus = self.calculate_era_plus(pitcher_stats)
        fip = self.calculate_fip(pitcher_stats)
        war = self.calculate_war_pitcher(pitcher_stats)
        
        # 종합 평가 (0-100 스케일)
        # ERA+ 130+ = 90+, 100 = 70, 70 = 50
        rating = min(100, max(50, (era_plus - 50) * 0.8))
        
        return {
            'era_plus': era_plus,
            'fip': fip,
            'war': war,
            'rating': round(rating, 1)
        }
    
    def calculate_team_strength_from_players(self, batters: List[Dict], 
                                            pitchers: List[Dict]) -> Dict:
        """선수 메트릭스 기반 팀 전력 계산"""
        
        if not batters and not pitchers:
            return self._default_team_strength()
        
        # 타자 전력
        total_ops = 0
        total_woba = 0
        total_war_batting = 0
        
        for batter in batters:
            metrics = self.calculate_all_metrics_batter(batter)
            total_ops += metrics['ops']
            total_woba += metrics['woba']
            total_war_batting += metrics['war']
        
        avg_ops = total_ops / len(batters) if batters else self.avg['avg_ops']
        avg_woba = total_woba / len(batters) if batters else self.avg['avg_woba']
        
        # 투수 전력
        total_era_plus = 0
        total_fip = 0
        total_war_pitching = 0
        
        for pitcher in pitchers:
            metrics = self.calculate_all_metrics_pitcher(pitcher)
            total_era_plus += metrics['era_plus']
            total_fip += metrics['fip']
            total_war_pitching += metrics['war']
        
        avg_era_plus = total_era_plus / len(pitchers) if pitchers else 100
        avg_fip = total_fip / len(pitchers) if pitchers else self.avg['avg_era']
        
        # 예상 득점/실점
        # wOBA 기반 득점 예측
        expected_runs = self.avg['avg_runs'] * (avg_woba / self.avg['avg_woba'])
        
        # FIP 기반 실점 예측
        expected_runs_allowed = avg_fip
        
        return {
            'avg_ops': round(avg_ops, 3),
            'avg_woba': round(avg_woba, 3),
            'avg_era_plus': round(avg_era_plus, 1),
            'avg_fip': round(avg_fip, 2),
            'total_war': round(total_war_batting + total_war_pitching, 1),
            'expected_runs': round(expected_runs, 2),
            'expected_runs_allowed': round(expected_runs_allowed, 2),
            'attack_rating': round(avg_ops * 100, 1),
            'defense_rating': round(avg_era_plus * 0.7, 1)
        }
    
    def _default_team_strength(self) -> Dict:
        """기본 팀 전력"""
        return {
            'avg_ops': self.avg['avg_ops'],
            'avg_woba': self.avg['avg_woba'],
            'avg_era_plus': 100,
            'avg_fip': self.avg['avg_era'],
            'total_war': 0,
            'expected_runs': self.avg['avg_runs'],
            'expected_runs_allowed': self.avg['avg_era'],
            'attack_rating': 70.0,
            'defense_rating': 70.0
        }


# 싱글톤 인스턴스
_metrics_baseball = {}

def get_baseball_metrics(league: str = "KBO") -> AdvancedBaseballMetrics:
    """AdvancedBaseballMetrics 싱글톤 반환"""
    global _metrics_baseball
    
    if league not in _metrics_baseball:
        _metrics_baseball[league] = AdvancedBaseballMetrics(league)
    
    return _metrics_baseball[league]

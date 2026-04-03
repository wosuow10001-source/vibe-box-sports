"""
고급 선수 메트릭스 시스템
- PER (Player Efficiency Rating)
- Win Shares (WS)
- Adjusted Plus-Minus (APM/RAPM)
- BPM (Box Plus-Minus)
- PIE (Player Impact Estimate)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class AdvancedPlayerMetrics:
    """NBA/KBL 선수 고급 메트릭스 계산 및 팀 능력치 변환"""
    
    def __init__(self, league: str = "NBA"):
        self.league = league
        
        # 리그별 평균값
        self.league_averages = {
            "NBA": {
                "per": 15.0,
                "pace": 100.0,
                "ortg": 115.0,  # Offensive Rating
                "drtg": 115.0,  # Defensive Rating
                "minutes_per_game": 240.0,  # 팀 총 출전 시간
                "possessions_per_game": 100.0
            },
            "KBL": {
                "per": 15.0,
                "pace": 74.0,
                "ortg": 82.0,
                "drtg": 82.0,
                "minutes_per_game": 200.0,
                "possessions_per_game": 74.0
            }
        }
        
        self.avg = self.league_averages.get(league, self.league_averages["NBA"])
    
    def calculate_per(self, player_stats: Dict) -> float:
        """
        PER (Player Efficiency Rating) 계산
        
        공식 (간소화):
        PER = (득점 + 리바운드 + 어시스트 + 스틸 + 블락 
               - 실책 - 미스샷) / 출전시간 × 정규화
        
        리그 평균: 15.0
        """
        
        # 기본 통계
        ppg = player_stats.get('ppg', 0)
        rpg = player_stats.get('rpg', 0)
        apg = player_stats.get('apg', 0)
        spg = player_stats.get('spg', 0)  # steals
        bpg = player_stats.get('bpg', 0)  # blocks
        topg = player_stats.get('topg', 2.0)  # turnovers
        
        # 슈팅 효율
        fgm = player_stats.get('fgm', ppg * 0.4)  # 필드골 성공
        fga = player_stats.get('fga', ppg * 0.9)  # 필드골 시도
        ftm = player_stats.get('ftm', ppg * 0.2)  # 자유투 성공
        fta = player_stats.get('fta', ppg * 0.25)  # 자유투 시도
        
        # 출전 시간
        mpg = player_stats.get('mpg', 30.0)
        
        # PER 계산 (간소화 버전)
        positive = (
            ppg * 1.0 +
            rpg * 0.7 +
            apg * 0.7 +
            spg * 1.0 +
            bpg * 1.0 +
            fgm * 0.3 +
            ftm * 0.2
        )
        
        negative = (
            topg * 1.0 +
            (fga - fgm) * 0.4 +
            (fta - ftm) * 0.2
        )
        
        raw_per = (positive - negative) / mpg * 48  # 48분 기준 정규화
        
        # 리그 평균으로 조정
        per = raw_per * (self.avg['per'] / 15.0)
        
        return max(0, min(40, per))  # 0-40 범위
    
    def calculate_win_shares(self, player_stats: Dict, team_stats: Dict) -> float:
        """
        Win Shares (WS) 계산
        
        WS = OWS + DWS
        - OWS (Offensive Win Shares): 공격 기여도
        - DWS (Defensive Win Shares): 수비 기여도
        """
        
        # 출전 시간 비율
        mpg = player_stats.get('mpg', 30.0)
        team_mpg = self.avg['minutes_per_game']
        minutes_ratio = mpg / team_mpg
        
        # 공격 기여도 (OWS)
        ppg = player_stats.get('ppg', 0)
        apg = player_stats.get('apg', 0)
        fg_pct = player_stats.get('fg_pct', 0.45)
        
        # 공격 효율
        offensive_rating = (ppg + apg * 2) * fg_pct * 100
        league_ortg = self.avg['ortg']
        
        ows = (offensive_rating / league_ortg - 1) * minutes_ratio * 10
        
        # 수비 기여도 (DWS)
        rpg = player_stats.get('rpg', 0)
        spg = player_stats.get('spg', 0)
        bpg = player_stats.get('bpg', 0)
        
        # 수비 효율
        defensive_rating = (rpg * 0.7 + spg * 1.5 + bpg * 1.5) * 10
        league_drtg = self.avg['drtg']
        
        dws = (defensive_rating / league_drtg) * minutes_ratio * 5
        
        ws = max(0, ows + dws)
        
        return min(20, ws)  # 시즌 최대 20 WS
    
    def calculate_bpm(self, player_stats: Dict) -> Tuple[float, float, float]:
        """
        BPM (Box Plus-Minus) 계산
        
        Returns:
            (OBPM, DBPM, BPM)
            - OBPM: Offensive BPM
            - DBPM: Defensive BPM
            - BPM: Total BPM
        """
        
        # 기본 통계
        ppg = player_stats.get('ppg', 0)
        rpg = player_stats.get('rpg', 0)
        apg = player_stats.get('apg', 0)
        spg = player_stats.get('spg', 0)
        bpg = player_stats.get('bpg', 0)
        topg = player_stats.get('topg', 2.0)
        
        # 슈팅 효율
        fg_pct = player_stats.get('fg_pct', 0.45)
        three_pct = player_stats.get('three_pct', 0.35)
        ft_pct = player_stats.get('ft_pct', 0.75)
        
        # OBPM (공격)
        obpm = (
            ppg * 0.3 +
            apg * 1.5 +
            (fg_pct - 0.45) * 20 +
            (three_pct - 0.35) * 10 +
            rpg * 0.2 -
            topg * 0.5
        )
        
        # DBPM (수비)
        dbpm = (
            rpg * 0.4 +
            spg * 2.0 +
            bpg * 2.0 -
            (ppg * 0.05)  # 공격 선수는 수비 약함
        )
        
        # Total BPM
        bpm = obpm + dbpm
        
        return (
            max(-10, min(15, obpm)),
            max(-5, min(10, dbpm)),
            max(-10, min(20, bpm))
        )
    
    def calculate_pie(self, player_stats: Dict, team_stats: Dict) -> float:
        """
        PIE (Player Impact Estimate) 계산
        
        PIE = (선수 기여도) / (팀 전체 기여도)
        
        범위: 0.0 - 1.0 (팀 내 비율)
        """
        
        # 선수 기여도
        ppg = player_stats.get('ppg', 0)
        rpg = player_stats.get('rpg', 0)
        apg = player_stats.get('apg', 0)
        spg = player_stats.get('spg', 0)
        bpg = player_stats.get('bpg', 0)
        fgm = player_stats.get('fgm', ppg * 0.4)
        ftm = player_stats.get('ftm', ppg * 0.2)
        topg = player_stats.get('topg', 2.0)
        
        player_contribution = (
            ppg + fgm + ftm - (fgm * 0.5) +
            rpg + apg + spg + bpg - topg
        )
        
        # 팀 기여도
        team_ppg = team_stats.get('ppg', self.avg['ortg'])
        team_contribution = team_ppg * 2  # 대략적인 팀 전체 기여도
        
        pie = player_contribution / max(team_contribution, 1)
        
        return max(0, min(0.5, pie))  # 0-50% 범위
    
    def calculate_rapm(self, player_stats: Dict, on_court_stats: Dict) -> float:
        """
        RAPM (Regularized Adjusted Plus-Minus) 계산
        
        실제로는 리그레션 필요하지만, 간소화 버전 사용
        
        RAPM ≈ (출전 시 팀 득실차) - (벤치 시 팀 득실차)
        """
        
        # 출전 시 득실차
        on_court_diff = on_court_stats.get('plus_minus', 0)
        
        # 출전 시간 가중치
        mpg = player_stats.get('mpg', 30.0)
        weight = mpg / 48.0
        
        # RAPM 추정
        rapm = on_court_diff * weight
        
        return max(-15, min(15, rapm))
    
    def calculate_all_metrics(self, player_stats: Dict, team_stats: Dict,
                             on_court_stats: Optional[Dict] = None) -> Dict:
        """
        모든 고급 메트릭스 계산
        
        Returns:
            {
                'per': float,
                'ws': float,
                'obpm': float,
                'dbpm': float,
                'bpm': float,
                'pie': float,
                'rapm': float,
                'composite_rating': float  # 종합 평가
            }
        """
        
        per = self.calculate_per(player_stats)
        ws = self.calculate_win_shares(player_stats, team_stats)
        obpm, dbpm, bpm = self.calculate_bpm(player_stats)
        pie = self.calculate_pie(player_stats, team_stats)
        
        if on_court_stats:
            rapm = self.calculate_rapm(player_stats, on_court_stats)
        else:
            rapm = bpm  # RAPM 데이터 없으면 BPM 사용
        
        # 종합 평가 (가중 평균)
        composite_rating = (
            per * 0.25 +
            ws * 2.0 * 0.20 +  # WS는 작은 값이므로 스케일 조정
            bpm * 0.25 +
            pie * 50 * 0.15 +  # PIE는 0-0.5 범위이므로 스케일 조정
            rapm * 0.15
        )
        
        return {
            'per': round(per, 2),
            'ws': round(ws, 2),
            'obpm': round(obpm, 2),
            'dbpm': round(dbpm, 2),
            'bpm': round(bpm, 2),
            'pie': round(pie, 3),
            'rapm': round(rapm, 2),
            'composite_rating': round(composite_rating, 2)
        }
    
    def calculate_team_strength_from_players(self, players: List[Dict], 
                                            team_stats: Dict) -> Dict:
        """
        선수 메트릭스 기반 팀 전력 계산
        
        Args:
            players: 선수 리스트 (출전 시간 포함)
            team_stats: 팀 통계
        
        Returns:
            {
                'offensive_rating': float,
                'defensive_rating': float,
                'overall_rating': float,
                'top_players': List[Dict],  # 상위 5명
                'bench_strength': float
            }
        """
        
        if not players:
            return self._default_team_strength()
        
        # 각 선수 메트릭스 계산
        player_metrics = []
        total_minutes = 0
        
        for player in players:
            mpg = player.get('mpg', 0)
            if mpg < 5:  # 출전 시간 5분 미만은 제외
                continue
            
            metrics = self.calculate_all_metrics(player, team_stats)
            metrics['name'] = player.get('name', 'Unknown')
            metrics['mpg'] = mpg
            metrics['position'] = player.get('position', 'F')
            
            player_metrics.append(metrics)
            total_minutes += mpg
        
        if not player_metrics:
            return self._default_team_strength()
        
        # 출전 시간 가중 평균
        weighted_per = 0
        weighted_bpm = 0
        weighted_obpm = 0
        weighted_dbpm = 0
        weighted_ws = 0
        
        for pm in player_metrics:
            weight = pm['mpg'] / total_minutes
            weighted_per += pm['per'] * weight
            weighted_bpm += pm['bpm'] * weight
            weighted_obpm += pm['obpm'] * weight
            weighted_dbpm += pm['dbpm'] * weight
            weighted_ws += pm['ws'] * weight
        
        # 공격/수비 레이팅 계산
        offensive_rating = self.avg['ortg'] * (1 + weighted_obpm / 100)
        defensive_rating = self.avg['drtg'] * (1 - weighted_dbpm / 100)
        
        # 종합 레이팅
        overall_rating = (
            weighted_per * 0.4 +
            weighted_bpm * 0.3 +
            weighted_ws * 2.0 * 0.3
        )
        
        # 상위 5명 (출전 시간 기준)
        top_players = sorted(player_metrics, key=lambda x: x['mpg'], reverse=True)[:5]
        
        # 벤치 전력 (6-10번째 선수)
        bench_players = sorted(player_metrics, key=lambda x: x['mpg'], reverse=True)[5:10]
        if bench_players:
            bench_strength = sum(p['composite_rating'] for p in bench_players) / len(bench_players)
        else:
            bench_strength = 10.0
        
        return {
            'offensive_rating': round(offensive_rating, 1),
            'defensive_rating': round(defensive_rating, 1),
            'overall_rating': round(overall_rating, 1),
            'weighted_per': round(weighted_per, 2),
            'weighted_bpm': round(weighted_bpm, 2),
            'weighted_ws': round(weighted_ws, 2),
            'top_players': top_players,
            'bench_strength': round(bench_strength, 1),
            'total_players': len(player_metrics)
        }
    
    def apply_injury_impact(self, team_strength: Dict, injured_players: List[Dict],
                           all_players: List[Dict]) -> Dict:
        """
        부상 선수 영향 반영
        
        Args:
            team_strength: 기본 팀 전력
            injured_players: 부상 선수 리스트
            all_players: 전체 선수 리스트
        
        Returns:
            조정된 팀 전력
        """
        
        if not injured_players:
            return team_strength
        
        adjusted = team_strength.copy()
        
        # 부상 선수 기여도 계산
        total_loss_mpg = 0
        total_loss_rating = 0
        
        for injured in injured_players:
            name = injured.get('name', '')
            
            # 해당 선수 찾기
            player = next((p for p in all_players if p.get('name') == name), None)
            if not player:
                continue
            
            mpg = player.get('mpg', 0)
            ppg = player.get('ppg', 0)
            
            total_loss_mpg += mpg
            total_loss_rating += ppg / 2  # 대략적인 영향
        
        # 출전 시간 비율로 영향 계산
        if total_loss_mpg > 0:
            impact_ratio = total_loss_mpg / self.avg['minutes_per_game']
            
            # 백업 선수가 일부 보완 (60%)
            adjusted_impact = impact_ratio * 0.4
            
            adjusted['offensive_rating'] *= (1 - adjusted_impact)
            adjusted['defensive_rating'] *= (1 + adjusted_impact * 0.5)  # 수비는 덜 영향
            adjusted['overall_rating'] *= (1 - adjusted_impact)
        
        return adjusted
    
    def apply_form_adjustment(self, team_strength: Dict, players: List[Dict],
                             recent_games: int = 10) -> Dict:
        """
        최근 폼 반영
        
        Args:
            team_strength: 기본 팀 전력
            players: 선수 리스트 (최근 경기 통계 포함)
            recent_games: 최근 N경기
        
        Returns:
            조정된 팀 전력
        """
        
        adjusted = team_strength.copy()
        
        # 주요 선수 (상위 5명) 최근 폼 계산
        top_players = sorted(players, key=lambda x: x.get('mpg', 0), reverse=True)[:5]
        
        if not top_players:
            return adjusted
        
        total_form = 0
        for player in top_players:
            # 최근 경기 평균 vs 시즌 평균
            recent_ppg = player.get('recent_ppg', player.get('ppg', 0))
            season_ppg = player.get('ppg', 0)
            
            if season_ppg > 0:
                form_ratio = recent_ppg / season_ppg
            else:
                form_ratio = 1.0
            
            total_form += form_ratio
        
        avg_form = total_form / len(top_players)
        
        # 폼 조정 (±10% 범위)
        form_adjustment = 0.9 + (avg_form - 1.0) * 0.2
        form_adjustment = max(0.9, min(1.1, form_adjustment))
        
        adjusted['offensive_rating'] *= form_adjustment
        adjusted['overall_rating'] *= form_adjustment
        
        return adjusted
    
    def _default_team_strength(self) -> Dict:
        """기본 팀 전력"""
        return {
            'offensive_rating': self.avg['ortg'],
            'defensive_rating': self.avg['drtg'],
            'overall_rating': 15.0,
            'weighted_per': 15.0,
            'weighted_bpm': 0.0,
            'weighted_ws': 0.0,
            'top_players': [],
            'bench_strength': 10.0,
            'total_players': 0
        }


# 싱글톤 인스턴스
_metrics_nba = None
_metrics_kbl = None

def get_advanced_metrics(league: str = "NBA") -> AdvancedPlayerMetrics:
    """AdvancedPlayerMetrics 싱글톤 반환"""
    global _metrics_nba, _metrics_kbl
    
    if league == "KBL":
        if _metrics_kbl is None:
            _metrics_kbl = AdvancedPlayerMetrics("KBL")
        return _metrics_kbl
    else:
        if _metrics_nba is None:
            _metrics_nba = AdvancedPlayerMetrics("NBA")
        return _metrics_nba

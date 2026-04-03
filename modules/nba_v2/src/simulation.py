import numpy as np
from typing import Dict, List, Tuple
from modules.nba_v2.src.utils import logger

class NBASimulation:
    """V2 시뮬레이션: 5,000회 몬테카를로 경기 시뮬레이션"""
    
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations
        
    def run(self, home_stats: Dict, away_stats: Dict, 
            market_spread: float = 0.0, market_total: float = 225.0,
            is_elite_game: bool = False) -> Dict:
        """
        [V2.6] 고도화된 몬테카를로 확률 시뮬레이션 (10,000회 벡터화 처리)
        """
        # 1. 기대 득점 계산 (디자인 명세 준수)
        # offense: 평균 득점, defense: 상대 허용 득점
        h_off = home_stats.get('ppg', 110.0)
        h_def = home_stats.get('opp_ppg', 110.0)
        a_off = away_stats.get('ppg', 110.0)
        a_def = away_stats.get('opp_ppg', 110.0)
        
        # 홈 어드밴티지 (HCA): +2.5점 (디자인 명세 2~3점의 중간값)
        hca = 2.5
        expected_h = (h_off + a_def) / 2.0 + hca
        expected_a = (a_off + h_def) / 2.0
        
        # 2. 동적 변동성(Standard Deviation) 계산 [10 ~ 13 범위]
        # 기본값 11.5
        std_h = 11.5
        std_a = 11.5
        
        # Pace 가중치 (빠를수록 변동성 증가)
        pace_h = home_stats.get('pace', 100.0)
        pace_a = away_stats.get('pace', 100.0)
        std_h += (pace_h - 100.0) * 0.1
        std_a += (pace_a - 100.0) * 0.1
        
        # 3PT 의존도 (3점 비중 40% 이상 시 변동성 증가)
        if home_stats.get('three_pt_rate', 0.35) > 0.40: std_h += 1.0
        if away_stats.get('three_pt_rate', 0.35) > 0.40: std_a += 1.0
        
        # 엘리트 매치업 보정 (변동성 증가)
        if is_elite_game:
            std_h += 1.0
            std_a += 1.0
            
        # 3. 벡터화된 몬테카를로 샘플링 (10,000회)
        np.random.seed(42) # 재현성을 위한 시드 고정
        scores_h = np.random.normal(expected_h, std_h, self.iterations)
        scores_a = np.random.normal(expected_a, std_a, self.iterations)
        
        # 4. 시장별 확률 계산
        win_h_mask = scores_h > scores_a
        win_prob_h = float(np.mean(win_h_mask))
        
        # 핸디캡(Spread) 커버 확률: P(home - away > spread)
        # 시뮬레이션에서는 home_score - away_score가 market_spread보다 큰 경우
        spread_cover_mask = (scores_h - scores_a) > market_spread
        spread_prob_h = float(np.mean(spread_cover_mask))
        
        # 언오버(Over/Under) 확률: P(home + away > total)
        over_mask = (scores_h + scores_a) > market_total
        over_prob = float(np.mean(over_mask))
        
        return {
            'win_probability': {
                'home': win_prob_h,
                'away': 1.0 - win_prob_h
            },
            'spread_probability': {
                'cover_home': spread_prob_h,
                'cover_away': 1.0 - spread_prob_h
            },
            'over_under_probability': {
                'over': over_prob,
                'under': 1.0 - over_prob
            },
            'expected_score': {
                'home': float(np.mean(scores_h)),
                'away': float(np.mean(scores_a))
            },
            # 레거시 호환용 필드
            'avg_h': np.mean(scores_h),
            'avg_a': np.mean(scores_a),
            'win_prob_h': win_prob_h
        }

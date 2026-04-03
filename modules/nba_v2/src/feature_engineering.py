import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
from modules.nba_v2.src.utils import NBAConfig

class NBAFeatureEngineering:
    """V2 피처 엔지니어링: ML 모델을 위한 입력 변수 생성"""
    
    def __init__(self):
        pass
        
    def build_features(self, home_stats: pd.Series, away_stats: pd.Series) -> pd.DataFrame:
        """두 팀의 스켓 데이터로부터 매치업 피처 생성"""
        
        # 1. 효율성 지표 (ORtg, DRtg)
        home_ortg = (home_stats['ppg'] / home_stats['pace']) * 100
        home_drtg = (home_stats['opp_ppg'] / home_stats['pace']) * 100
        away_ortg = (away_stats['ppg'] / away_stats['pace']) * 100
        away_drtg = (away_stats['opp_ppg'] / away_stats['pace']) * 100
        
        features = {
            # 기본 전력
            'ortg_diff': home_ortg - away_ortg,
            'drtg_diff': home_drtg - away_drtg,
            'net_rating_diff': (home_ortg - home_drtg) - (away_ortg - away_drtg),
            
            # 슈팅 및 점유율
            'efg_diff': home_stats['efg_pct'] - away_stats['efg_pct'],
            'to_diff': home_stats['to_pct'] - away_stats['to_pct'],
            'reb_diff': home_stats['reb_pct'] - away_stats['reb_pct'],
            
            # 최근 기세 및 일정
            'win_pct_diff': home_stats['win_pct'] - away_stats['win_pct'],
            'last_10_diff': (home_stats['last_10_wins'] - away_stats['last_10_wins']) / 10.0,
            'rest_edge': home_stats['rest_days'] - away_stats['rest_days'],
            'is_home_b2b': 1 if home_stats['rest_days'] < 1 else 0,
            'is_away_b2b': 1 if away_stats['rest_days'] < 1 else 0,
            
            # 매치업 특성
            'pace_conflict': abs(home_stats['pace'] - away_stats['pace']),
            'clutch_edge': home_stats['clutch_net'] - away_stats['clutch_net']
        }
        
        return pd.DataFrame([features])

    def compute_team_power(self, stats: pd.Series) -> float:
        """[SENIOR PATCH] 팀 파워 레이팅 계산: 승률(40%), NetRating(40%), 최근 폼(20%)"""
        win_rate = stats.get('win_pct', 0.5)
        
        # Net Rating 정규화 [-15, +15] -> [0, 1]
        ppg = stats.get('ppg', 115)
        opp_ppg = stats.get('opp_ppg', 115)
        pace = stats.get('pace', 100)
        net_rating = ((ppg - opp_ppg) / pace) * 100
        nr_norm = np.clip((net_rating + 15) / 30.0, 0, 1)
        
        recent_form = stats.get('last_10_wins', 5) / 10.0
        
        team_power = (win_rate * 0.4) + (nr_norm * 0.4) + (recent_form * 0.2)
        
        # 약팀 페널티 (win_rate < 0.35)
        if win_rate < 0.35:
            team_power -= 0.1
            
        return float(team_power)

    def compute_clutch_score(self, stats: pd.Series) -> float:
        """[V2.1] 클러치 점수 계산: 클러치 넷레이팅(50%), 자유투%(30%), 실책(20%)"""
        clutch_net = stats.get('clutch_net', 0.0)
        ft_pct = stats.get('ft_pct', 0.78)
        to_pct = stats.get('to_pct', 0.13)
        
        # 정규화 및 가중치 합산
        # clutch_net baseline 0, ft_pct baseline 0.78, to_pct baseline 0.13
        score = (clutch_net * 0.5) + ((ft_pct - 0.78) * 10) - ((to_pct - 0.13) * 20)
        return float(score)

    def compute_lineup_rating(self, team_roster: List[Dict], injuries: List[Dict]) -> Tuple[float, float]:
        """[V2.1] 주전 라인업(상위 5인) 기반 공격/수비 레이팅 계산"""
        injured_names = [i.get('player') for i in injuries]
        
        # 부상자를 제외한 출전 시간(MPG) 상위 5인 추출
        available_players = [p for p in team_roster if p.get('name') not in injured_names]
        starting_lineup = sorted(available_players, key=lambda x: x.get('mpg', 0), reverse=True)[:5]
        
        if not starting_lineup:
            return 115.0, 115.0 # Baseline
            
        lineup_ortg = np.mean([p.get('ortg', 115) for p in starting_lineup])
        lineup_drtg = np.mean([p.get('drtg', 115) for p in starting_lineup])
        
        return float(lineup_ortg), float(lineup_drtg)

    def prepare_training_data(self, history_df: pd.DataFrame, collector: any) -> Tuple[pd.DataFrame, pd.Series]:
        """역사적 데이터를 ML 학습용 데이터셋으로 변환 (Placeholder)"""
        # 실제 구현시에는 각 경기 시점의 팀 스탯을 조인해야 함
        # 현재는 구조적 호환성을 위해 빈 데이터셋 반환 가능성 염두
        if history_df.empty:
            return pd.DataFrame(), pd.Series()
            
        # Mocking or proper reconstruction logic here
        return pd.DataFrame(), pd.Series()

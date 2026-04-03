import pandas as pd
import os
from typing import Dict, List
from datetime import datetime
from modules.nba_v2.src.utils import logger, NBAConfig

class NBADataCollector:
    """V2 데이터 수집기: 실시간 및 역사적 데이터 통합 관리"""
    
    def __init__(self, data_collector_v1=None):
        self.v1_collector = data_collector_v1
        NBAConfig.ensure_dirs()
        self.history_path = os.path.join(NBAConfig.DATA_DIR, "match_results.csv")
        
    def get_latest_stats(self, team_name: str, raw_data: Dict = None) -> pd.Series:
        """기존 콜렉터 혹은 외부에서 전달받은 raw 데이터로부터 최신 스탯을 가져와 Pandas Series로 변환"""
        if raw_data:
            data = raw_data
        elif self.v1_collector:
            data = self.v1_collector.get_team_data(team_name)
        else:
            # Fallback (NBA Baseline)
            data = {'ppg': 115, 'opp_ppg': 115, 'pace': 100}

        
        # 기본 전처리 (NBA 스케일링)
        ppg = data.get('ppg', 115)
        opp_ppg = data.get('opp_ppg', 115)
        if ppg < 10: 
            ppg = 85 + (ppg / 5.0) * 40
            opp_ppg = 85 + (opp_ppg / 5.0) * 40
            
        return pd.Series({
            'team_name': team_name,
            'ppg': ppg,
            'opp_ppg': opp_ppg,
            'pace': data.get('pace', 100),
            'efg_pct': data.get('efg_pct', 0.53),
            'to_pct': data.get('to_pct', 0.13),
            'reb_pct': data.get('reb_pct', 0.50),
            'ft_pct': data.get('ft_pct', 0.78),
            'clutch_net': data.get('clutch_net_rating', 0.0),
            'win_pct': data.get('win_pct', 0.50),
            'last_10_wins': data.get('last_10_wins', 5),
            'rest_days': data.get('rest_days', 2)
        })

    def save_match_result(self, home: str, away: str, h_score: int, a_score: int):
        """경기 결과 저장 (향후 학습 데이터로 활용)"""
        new_row = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'home_team': home,
            'away_team': away,
            'home_score': h_score,
            'away_score': a_score,
            'winner': 'home' if h_score > a_score else 'away'
        }
        df = pd.DataFrame([new_row])
        
        if os.path.exists(self.history_path):
            df.to_csv(self.history_path, mode='a', header=False, index=False)
        else:
            df.to_csv(self.history_path, index=False)
        logger.info(f"Match result saved: {home} {h_score} - {a_score} {away}")

    def load_historical_data(self) -> pd.DataFrame:
        """학습을 위한 역사적 데이터 로드"""
        if os.path.exists(self.history_path):
            return pd.read_csv(self.history_path)
        return pd.DataFrame()

    def get_team_roster(self, team_name: str) -> List[Dict]:
        """[V2.1] 팀 로스터 및 플레이어 레벨 스탯 가져오기 (NBA 선진 분석용)"""
        # 실제 환경에서는 데이터베이스나 API에서 선수별 (MIN, ORtg, DRtg, Usage) 수집
        # 여기서는 시뮬레이션을 위해 주전급 선수의 Mock 데이터를 생성
        roster = [
            {'name': f'{team_name} Playmaker', 'mpg': 34, 'usage': 0.28, 'ortg': 118, 'drtg': 112, 'bpm': 4.5, 'is_primary_ball_handler': True},
            {'name': f'{team_name} Scorer', 'mpg': 32, 'usage': 0.32, 'ortg': 120, 'drtg': 115, 'bpm': 5.2, 'is_primary_star': True},
            {'name': f'{team_name} Wing', 'mpg': 28, 'usage': 0.18, 'ortg': 112, 'drtg': 110, 'bpm': 1.2},
            {'name': f'{team_name} Big', 'mpg': 30, 'usage': 0.15, 'ortg': 115, 'drtg': 105, 'bpm': 3.1, 'is_defensive_anchor': True},
            {'name': f'{team_name} 3&D', 'mpg': 26, 'usage': 0.12, 'ortg': 110, 'drtg': 108, 'bpm': 0.8},
            {'name': f'{team_name} Bench 1', 'mpg': 20, 'usage': 0.18, 'ortg': 105, 'drtg': 110, 'bpm': -1.2},
            {'name': f'{team_name} Bench 2', 'mpg': 18, 'usage': 0.15, 'ortg': 102, 'drtg': 112, 'bpm': -2.5},
        ]
        return roster

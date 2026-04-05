"""
V6 Feature Engine: 26-Feature Vector Generator

기존 시스템의 ~8개 피처를 26개로 확장하여 XGBoost 및 앙상블 모델에 공급.
각 피처는 학술 연구(SHAP 분석)에서 축구 예측에 높은 중요도를 보인 것들.
"""

from typing import Dict, List, Optional
from modules.form_tracker import FormTracker, form_from_wdl_list
from modules.sos_adjuster import SoSAdjuster
from modules.dixon_coles_model import DixonColesModel


class FeatureEngine:
    """
    26-Feature 벡터 생성기.
    
    입력: 홈/원정 팀 데이터 + 경기 컨텍스트
    출력: 26개 float 피처 딕셔너리
    """
    
    FEATURE_NAMES = [
        'dc_attack_home', 'dc_defense_home', 'dc_attack_away', 'dc_defense_away',
        'rank_diff', 'ppg_diff',
        'xg_home_5m', 'xga_home_5m', 'xg_away_5m', 'xga_away_5m',
        'xg_diff_home', 'xg_diff_away',
        'ema_form_home', 'ema_form_away',
        'momentum_home', 'momentum_away',
        'home_form_home', 'away_form_away',
        'ppda_home', 'ppda_away', 'possession_diff',
        'rest_days_diff', 'importance',
        'injury_impact_diff',
        'h2h_home_win_rate', 'is_derby'
    ]
    
    def __init__(self, league: str = "EPL"):
        self.league = league
        self.form_tracker = FormTracker(decay_factor=0.85)
        self.sos = SoSAdjuster(league)
        self.dc_model = DixonColesModel(league)
        
        # DC 모델 로드 시도
        self.dc_model.load()
    
    def register_teams(self, home_data: dict, away_data: dict):
        """팀 데이터를 SoS 및 DC 모델에 등록"""
        home_name = home_data.get('team_name', 'Home')
        away_name = away_data.get('team_name', 'Away')
        
        # SoS 등록
        self.sos.register_team(
            home_name,
            home_data.get('avg_goals', 1.3),
            home_data.get('avg_conceded', 1.3),
            home_data.get('xg', 0),
            home_data.get('xga', 0)
        )
        self.sos.register_team(
            away_name,
            away_data.get('avg_goals', 1.3),
            away_data.get('avg_conceded', 1.3),
            away_data.get('xg', 0),
            away_data.get('xga', 0)
        )
        
        # DC 모델 등록 (MLE 미피팅 시 휴리스틱)
        league_avg = self.sos.league_avg
        self.dc_model.estimate_from_stats(
            home_name,
            home_data.get('avg_goals', 1.3),
            home_data.get('avg_conceded', 1.3),
            league_avg
        )
        self.dc_model.estimate_from_stats(
            away_name,
            away_data.get('avg_goals', 1.3),
            away_data.get('avg_conceded', 1.3),
            league_avg
        )
    
    def extract_features(self, home_data: dict, away_data: dict,
                         match_context: dict) -> dict:
        """
        26-피처 벡터 추출.
        
        Args:
            home_data: 홈팀 데이터 (기존 형식과 호환)
            away_data: 원정팀 데이터
            match_context: {
                'rest_days_home': int, 'rest_days_away': int,
                'importance': float (0-1),
                'injury_impact_home': float, 'injury_impact_away': float,
                'is_derby': bool
            }
        
        Returns:
            dict: 26개 피처 {name: value, ...}
        """
        self.register_teams(home_data, away_data)
        
        home_name = home_data.get('team_name', 'Home')
        away_name = away_data.get('team_name', 'Away')
        
        # ===== 1. Dixon-Coles 레이팅 =====
        h_rating = self.dc_model.get_team_rating(home_name) or {'attack': 1.0, 'defense': 1.0}
        a_rating = self.dc_model.get_team_rating(away_name) or {'attack': 1.0, 'defense': 1.0}
        
        # ===== 2. 순위 & 승점 =====
        h_rank = home_data.get('rank', home_data.get('position', 10))
        a_rank = away_data.get('rank', away_data.get('position', 10))
        rank_diff = a_rank - h_rank  # 양수 = 홈팀이 랭킹 높음
        
        h_ppg = home_data.get('points_per_game', 
                              home_data.get('points', 0) / max(1, home_data.get('played', 
                              home_data.get('total_matches', 1))))
        a_ppg = away_data.get('points_per_game',
                              away_data.get('points', 0) / max(1, away_data.get('played',
                              away_data.get('total_matches', 1))))
        ppg_diff = h_ppg - a_ppg
        
        # ===== 3. xG 메트릭 =====
        h_xg = home_data.get('xg', home_data.get('avg_goals', 1.3))
        h_xga = home_data.get('xga', home_data.get('avg_conceded', 1.3))
        a_xg = away_data.get('xg', away_data.get('avg_goals', 1.3))
        a_xga = away_data.get('xga', away_data.get('avg_conceded', 1.3))
        
        # SoS 보정된 xG
        sos_h_xg, sos_a_xg = self.sos.get_adjusted_xg_pair(home_name, away_name)
        
        # ===== 4. 폼 & 모멘텀 =====
        h_form_list = home_data.get('recent_form', [])
        a_form_list = away_data.get('recent_form', [])
        
        h_results = form_from_wdl_list(h_form_list) if h_form_list else []
        a_results = form_from_wdl_list(a_form_list) if a_form_list else []
        
        h_form_features = self.form_tracker.calculate_all_form_features(h_results, is_home=True)
        a_form_features = self.form_tracker.calculate_all_form_features(a_results, is_home=False)
        
        # ===== 5. 전술 & 압박 =====
        h_ppda = home_data.get('ppda', 12.0)
        a_ppda = away_data.get('ppda', 12.0)
        h_poss = home_data.get('possession_avg', 50)
        a_poss = away_data.get('possession_avg', 50)
        
        # ===== 6. 컨텍스트 =====
        rest_diff = match_context.get('rest_days_home', 4) - match_context.get('rest_days_away', 4)
        importance = match_context.get('importance', 0.5)
        
        inj_h = match_context.get('injury_impact_home', 1.0)
        inj_a = match_context.get('injury_impact_away', 1.0)
        injury_diff = inj_h - inj_a  # 양수 = 홈팀이 부상 적음 (유리)
        
        h2h_rate = match_context.get('h2h_home_win_rate', 0.5)
        is_derby = 1.0 if match_context.get('is_derby', False) else 0.0
        
        # ===== 26-피처 벡터 =====
        features = {
            # DC 레이팅 (1-4)
            'dc_attack_home': h_rating['attack'],
            'dc_defense_home': h_rating['defense'],
            'dc_attack_away': a_rating['attack'],
            'dc_defense_away': a_rating['defense'],
            
            # 순위 & 승점 (5-6)
            'rank_diff': rank_diff,
            'ppg_diff': round(ppg_diff, 3),
            
            # xG 메트릭 (7-12) - SoS 보정
            'xg_home_5m': round(sos_h_xg, 3),
            'xga_home_5m': round(h_xga, 3),
            'xg_away_5m': round(sos_a_xg, 3),
            'xga_away_5m': round(a_xga, 3),
            'xg_diff_home': round(sos_h_xg - h_xga, 3),
            'xg_diff_away': round(sos_a_xg - a_xga, 3),
            
            # 폼 & 모멘텀 (13-18)
            'ema_form_home': h_form_features['ema_form'],
            'ema_form_away': a_form_features['ema_form'],
            'momentum_home': h_form_features['momentum'],
            'momentum_away': a_form_features['momentum'],
            'home_form_home': h_form_features['venue_form'],
            'away_form_away': a_form_features['venue_form'],
            
            # 전술 & 압박 (19-21)
            'ppda_home': h_ppda,
            'ppda_away': a_ppda,
            'possession_diff': round(h_poss - a_poss, 1),
            
            # 컨텍스트 (22-26)
            'rest_days_diff': rest_diff,
            'importance': importance,
            'injury_impact_diff': round(injury_diff, 3),
            'h2h_home_win_rate': h2h_rate,
            'is_derby': is_derby
        }
        
        return features
    
    def features_to_array(self, features: dict) -> list:
        """피처 딕셔너리를 정렬된 배열로 변환 (ML 입력용)"""
        return [features[name] for name in self.FEATURE_NAMES]
    
    def get_dc_xg(self, home_name: str, away_name: str) -> tuple:
        """DC 모델의 xG 예측값 반환"""
        return self.dc_model.predict_xg(home_name, away_name)

"""
스포츠 종목별 라우터
- 공통 피처는 공유
- 확률 모델은 종목별 완전 분리
"""

from modules.predictor_soccer import SoccerPredictor
from modules.predictor_basketball_league_normalized import BasketballPredictorLeagueNormalized
from modules.predictor_baseball import BaseballPredictor
from modules.predictor_volleyball import VolleyballPredictor


class SportRouter:
    """
    종목별 예측 모델 라우터
    
    핵심 원칙:
    - 피처는 통합, 확률 모델은 종목별 분리
    - Output 형식은 모든 종목 통일
    - 리그별 정규화 적용 (농구)
    """
    
    def __init__(self):
        self.soccer_predictor = SoccerPredictor()
        
        # 농구 예측기는 리그별로 생성
        self.basketball_predictors = {
            'NBA East': BasketballPredictorLeagueNormalized('NBA East'),
            'NBA West': BasketballPredictorLeagueNormalized('NBA West'),
            'KBL': BasketballPredictorLeagueNormalized('KBL')
        }
        
        self.baseball_predictor = BaseballPredictor()
        self.volleyball_predictor = VolleyballPredictor()
        
        # 종목별 리그 매핑
        self.sport_mapping = {
            # 축구
            'EPL': 'soccer',
            'La Liga': 'soccer',
            'Bundesliga': 'soccer',
            'Serie A': 'soccer',
            'K리그1': 'soccer',
            
            # 농구
            'NBA': 'basketball',  # 기본 NBA (컨퍼런스 미지정)
            'NBA East': 'basketball',
            'NBA West': 'basketball',
            'KBL': 'basketball',
            
            # 야구
            'MLB': 'baseball',
            'KBO': 'baseball',
            
            # 배구
            'V-리그 (남)': 'volleyball',
            'V-리그 (여)': 'volleyball'
        }
    
    def predict_match(self, league, home_team, away_team, home_data, away_data,
                     weather, temperature, field_condition, match_importance,
                     rest_days_home, rest_days_away, injury_data=None, coaching_data=None,
                     lineup_home=None, lineup_away=None):
        """
        종목별 라우팅하여 예측 실행
        
        Args:
            lineup_home (dict, optional): 홈팀 라인업
            lineup_away (dict, optional): 원정팀 라인업
        
        Returns:
            dict: 통일된 형식의 예측 결과
            {
                'home_win_prob': float,
                'draw_prob': float,  # 없는 종목은 0
                'away_win_prob': float,
                'expected_score_home': int/float,
                'expected_score_away': int/float,
                'top_3_scores': list,
                'confidence': float,
                'key_factors': list,
                'sport_type': str,
                'model_type': str
            }
        """
        
        sport = self.sport_mapping.get(league, 'soccer')
        
        if sport == 'soccer':
            return self._predict_soccer(
                home_team, away_team, home_data, away_data,
                weather, temperature, field_condition, match_importance,
                rest_days_home, rest_days_away, injury_data, coaching_data,
                lineup_home, lineup_away
            )
        
        elif sport == 'basketball':
            return self._predict_basketball(
                home_team, away_team, home_data, away_data,
                weather, temperature, field_condition, match_importance,
                rest_days_home, rest_days_away, injury_data, coaching_data,
                lineup_home, lineup_away
            )
        
        elif sport == 'baseball':
            return self._predict_baseball(
                home_team, away_team, home_data, away_data,
                weather, temperature, field_condition, match_importance,
                rest_days_home, rest_days_away, injury_data, coaching_data,
                lineup_home, lineup_away
            )
        
        elif sport == 'volleyball':
            return self._predict_volleyball(
                home_team, away_team, home_data, away_data,
                weather, temperature, field_condition, match_importance,
                rest_days_home, rest_days_away, injury_data, coaching_data,
                lineup_home, lineup_away
            )
        
        else:
            # 기본값: 축구 모델 사용
            return self._predict_soccer(
                home_team, away_team, home_data, away_data,
                weather, temperature, field_condition, match_importance,
                rest_days_home, rest_days_away, injury_data, coaching_data,
                lineup_home, lineup_away
            )
    
    def _predict_soccer(self, home_team, away_team, home_data, away_data,
                       weather, temperature, field_condition, match_importance,
                       rest_days_home, rest_days_away, injury_data, coaching_data,
                       lineup_home, lineup_away):
        """축구: Bivariate Poisson + Dixon-Coles"""
        
        result = self.soccer_predictor.predict_match(
            home_team, away_team, home_data, away_data,
            weather, temperature, field_condition, match_importance,
            rest_days_home, rest_days_away, injury_data, coaching_data,
            lineup_home, lineup_away
        )
        
        result['sport_type'] = 'soccer'
        result['model_type'] = 'Bivariate Poisson + Dixon-Coles'
        
        return result
    
    def _predict_basketball(self, home_team, away_team, home_data, away_data,
                           weather, temperature, field_condition, match_importance,
                           rest_days_home, rest_days_away, injury_data, coaching_data,
                           lineup_home, lineup_away):
        """농구: Normal Distribution (정규분포) - 리그별 정규화"""
        
        # 리그별 예측기 선택
        league = self._detect_basketball_league(home_data, away_data)
        predictor = self.basketball_predictors.get(league, self.basketball_predictors['NBA East'])
        
        result = predictor.predict_match(
            home_team, away_team, home_data, away_data,
            weather, temperature, field_condition, match_importance,
            rest_days_home, rest_days_away, injury_data, coaching_data,
            lineup_home, lineup_away
        )
        
        result['sport_type'] = 'basketball'
        result['draw_prob'] = 0.0  # 농구는 무승부 없음
        
        return result
    
    def _detect_basketball_league(self, home_data: dict, away_data: dict) -> str:
        """농구 리그 자동 감지"""
        # avg_goals로 리그 판별 (KBL: 76-88, NBA: 105-120)
        avg_home = home_data.get('avg_goals', 100)
        avg_away = away_data.get('avg_goals', 100)
        avg_score = (avg_home + avg_away) / 2
        
        if avg_score < 95:
            return 'KBL'
        else:
            return 'NBA East'  # 기본값
    
    def _predict_baseball(self, home_team, away_team, home_data, away_data,
                         weather, temperature, field_condition, match_importance,
                         rest_days_home, rest_days_away, injury_data, coaching_data,
                         lineup_home, lineup_away):
        """야구: Negative Binomial"""
        
        result = self.baseball_predictor.predict_match(
            home_team, away_team, home_data, away_data,
            weather, temperature, field_condition, match_importance,
            rest_days_home, rest_days_away, injury_data, coaching_data,
            lineup_home, lineup_away
        )
        
        result['sport_type'] = 'baseball'
        result['model_type'] = 'Negative Binomial'
        result['draw_prob'] = 0.0  # 야구는 무승부 없음 (연장)
        
        return result
    
    def _predict_volleyball(self, home_team, away_team, home_data, away_data,
                           weather, temperature, field_condition, match_importance,
                           rest_days_home, rest_days_away, injury_data, coaching_data,
                           lineup_home, lineup_away):
        """배구: Markov Chain (세트 기반)"""
        
        result = self.volleyball_predictor.predict_match(
            home_team, away_team, home_data, away_data,
            weather, temperature, field_condition, match_importance,
            rest_days_home, rest_days_away, injury_data, coaching_data,
            lineup_home, lineup_away
        )
        
        result['sport_type'] = 'volleyball'
        result['model_type'] = 'Markov Chain'
        result['draw_prob'] = 0.0  # 배구는 무승부 없음
        
        return result

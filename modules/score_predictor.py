"""
점수 예측 통합 모듈
- 각 종목별 예측기에서 상세 점수 및 승률 데이터를 추출하여 통일된 형식으로 반환
"""

from modules.predictor_soccer import SoccerPredictor
from modules.predictor_baseball import BaseballPredictor
from modules.predictor_volleyball import VolleyballPredictor
from modules.predictor_basketball_league_normalized import BasketballPredictorLeagueNormalized

class ScorePredictor:
    def __init__(self):
        self.soccer_predictor = SoccerPredictor()
        self.baseball_predictor = BaseballPredictor()
        self.volleyball_predictor = VolleyballPredictor()
        self.kbl_predictor = BasketballPredictorLeagueNormalized('KBL')
        
        # 종목별 리그 매핑 (SportRouter와 동일)
        self.sport_mapping = {
            'EPL': 'soccer', 'La Liga': 'soccer', 'Bundesliga': 'soccer', 
            'Serie A': 'soccer', 'K리그1': 'soccer', 'MLS': 'soccer',
            'KBL': 'basketball',
            'MLB': 'baseball', 'KBO': 'baseball',
            'V-리그 남자': 'volleyball', 'V-리그 여자': 'volleyball'
        }

    def predict_match_score(self, league, home_team, away_team, home_data, away_data,
                          weather='맑음', temperature=20, field_condition='최상', 
                          match_importance='일반', rest_days_home=3, rest_days_away=3,
                          injury_data=None, coaching_data=None):
        """종목별 점수 예측 실행"""
        sport = self.sport_mapping.get(league, 'soccer')
        
        if sport == 'soccer':
            res = self.soccer_predictor.predict_match(league, home_team, away_team, home_data, away_data, 
                                                    weather, temperature, field_condition, match_importance,
                                                    rest_days_home, rest_days_away, injury_data, coaching_data)
            return {
                'home_score': int(round(res['expected_score_home'])),
                'away_score': int(round(res['expected_score_away'])),
                'total_goals': int(round(res['expected_score_home'] + res['expected_score_away'])),
                'home_win_probability': int(res['home_win_prob'] * 100),
                'away_win_probability': int(res['away_win_prob'] * 100),
                'draw_probability': int(res['draw_prob'] * 100),
                'confidence': res['confidence'],
                'key_factors': res['key_factors']
            }
        
        elif sport == 'baseball':
            res = self.baseball_predictor.predict_match(home_team, away_team, home_data, away_data,
                                                      weather, temperature, field_condition, match_importance,
                                                      rest_days_home, rest_days_away, injury_data, coaching_data)
            return {
                'home_score': int(round(res['expected_score_home'])),
                'away_score': int(round(res['expected_score_away'])),
                'total_goals': int(round(res['expected_score_home'] + res['expected_score_away'])),
                'home_win_probability': int(res['home_win_prob'] * 100),
                'away_win_probability': int(res['away_win_prob'] * 100),
                'confidence': res['confidence'],
                'key_factors': res['key_factors']
            }
            
        elif sport == 'volleyball':
            res = self.volleyball_predictor.predict_match(home_team, away_team, home_data, away_data,
                                                        weather, temperature, field_condition, match_importance,
                                                        rest_days_home, rest_days_away, injury_data, coaching_data)
            return {
                'home_score': int(round(res['expected_score_home'])),
                'away_score': int(round(res['expected_score_away'])),
                'total_goals': int(round(res['expected_score_home'] + res['expected_score_away'])),
                'home_win_probability': int(res['home_win_prob'] * 100),
                'away_win_probability': int(res['away_win_prob'] * 100),
                'confidence': res['confidence'],
                'key_factors': res['key_factors']
            }
            
        elif sport == 'basketball' and league == 'KBL':
            res = self.kbl_predictor.predict_match(home_team, away_team, home_data, away_data,
                                                 weather, temperature, field_condition, match_importance,
                                                 rest_days_home, rest_days_away, injury_data, coaching_data)
            return {
                'home_score': int(round(res['expected_score_home'])),
                'away_score': int(round(res['expected_score_away'])),
                'total_points': int(round(res['expected_score_home'] + res['expected_score_away'])),
                'home_win_probability': int(res['home_win_prob'] * 100),
                'away_win_probability': int(res['away_win_prob'] * 100),
                'confidence': res['confidence'],
                'key_factors': res['key_factors']
            }
            
        # 기본값 (축구)
        return self.predict_match_score(league, home_team, away_team, home_data, away_data,
                                      weather, temperature, field_condition, match_importance,
                                      rest_days_home, rest_days_away, injury_data, coaching_data)

    def get_prediction_explanation(self, prediction_res):
        """예측 근거 텍스트 생성"""
        explanation = "### 🔍 예측 근거 분석\n\n"
        
        # 신뢰도 기반 요약
        conf = prediction_res.get('confidence', '중간')
        explanation += f"**신뢰도 분석:** 본 예측의 신뢰도는 **{conf}** 수준입니다. "
        
        if conf == '높음':
            explanation += "데이터의 일관성이 높고 팀 간 전력 차이가 뚜렷하게 분석되었습니다.\n\n"
        elif conf == '낮음':
            explanation += "최근 변동성이 크거나 부상자 등 불확실 요소가 많아 주의가 필요합니다.\n\n"
        else:
            explanation += "평균적인 데이터 안정성을 보이고 있습니다.\n\n"
            
        # 주요 요인 나열
        explanation += "**주요 영향 요인:**\n"
        for factor in prediction_res.get('key_factors', []):
            explanation += f"- {factor}\n"
            
        if not prediction_res.get('key_factors'):
            explanation += "- 특이사항 없음\n"
            
        return explanation

def get_score_predictor():
    return ScorePredictor()

"""
점수 예측 모듈 (sport_router 통합 버전)

변경사항:
- 독립적인 점수 계산 로직 제거
- sport_router의 결과를 포맷팅하는 래퍼로 변경
- 승률과 점수가 수학적으로 완벽히 연동됨
"""

from typing import Dict, List
from modules.sport_router import SportRouter


class ScorePredictor:
    """
    점수 예측 클래스 (sport_router 래퍼)
    
    목적: sport_router의 예측 결과를 기존 UI 형식으로 변환
    """
    
    def __init__(self):
        self.router = SportRouter()
    
    def predict_match_score(self, league: str, home_team: str, away_team: str,
                           home_data: Dict, away_data: Dict,
                           weather: str = "맑음", temperature: int = 20,
                           field_condition: str = "좋음", match_importance: str = "보통",
                           rest_days_home: int = 3, rest_days_away: int = 3,
                           injury_data: Dict = None, coaching_data: Dict = None,
                           lineup_home: Dict = None, lineup_away: Dict = None) -> Dict:
        """
        경기 점수 예측 (sport_router 기반)
        
        Args:
            lineup_home: 홈팀 라인업 (선택)
            lineup_away: 원정팀 라인업 (선택)
        
        Returns:
            dict: UI 표시용 형식
            {
                'home_score': int,
                'away_score': int,
                'home_win_probability': float,  # 0-100
                'away_win_probability': float,
                'draw_probability': float,  # 축구만
                'total_points': int,  # 농구
                'total_goals': int,  # 축구/야구/배구
                'spread': float,
                'confidence': str,
                'key_factors': list
            }
        """
        
        # sport_router로 예측 실행
        result = self.router.predict_match(
            league=league,
            home_team=home_team,
            away_team=away_team,
            home_data=home_data,
            away_data=away_data,
            weather=weather,
            temperature=temperature,
            field_condition=field_condition,
            match_importance=match_importance,
            rest_days_home=rest_days_home,
            rest_days_away=rest_days_away,
            injury_data=injury_data,
            coaching_data=coaching_data,
            lineup_home=lineup_home,
            lineup_away=lineup_away
        )
        
        # UI 형식으로 변환
        home_score = int(round(result['expected_score_home']))
        away_score = int(round(result['expected_score_away']))
        
        # 승률을 0-100 범위로 변환
        home_win_prob = round(result['home_win_prob'] * 100, 1)
        away_win_prob = round(result['away_win_prob'] * 100, 1)
        draw_prob = round(result['draw_prob'] * 100, 1)
        
        # 신뢰도 레벨 계산
        confidence = self._calculate_confidence_level(result['confidence'])
        
        # 종목별 추가 정보
        sport_type = result.get('sport_type', 'soccer')
        
        prediction = {
            'home_score': home_score,
            'away_score': away_score,
            'home_win_probability': home_win_prob,
            'away_win_probability': away_win_prob,
            'confidence': confidence,
            'key_factors': result['key_factors'],
            'sport_type': sport_type,
            'model_type': result.get('model_type', 'Unknown')
        }
        
        # 축구만 무승부 확률 포함
        if sport_type == 'soccer':
            prediction['draw_probability'] = draw_prob
            prediction['total_goals'] = home_score + away_score
        
        # 농구는 total_points
        if sport_type == 'basketball':
            prediction['total_points'] = home_score + away_score
        
        # 야구/배구는 total_goals
        if sport_type in ['baseball', 'volleyball']:
            prediction['total_goals'] = home_score + away_score
        
        # 점수 차이
        prediction['spread'] = abs(home_score - away_score)
        
        return prediction
    
    def _calculate_confidence_level(self, confidence: float) -> str:
        """신뢰도 수치를 레벨로 변환"""
        if confidence >= 0.75:
            return "높음"
        elif confidence >= 0.55:
            return "중간"
        else:
            return "낮음"
    
    def get_prediction_explanation(self, prediction: Dict) -> str:
        """예측 근거 설명 생성"""
        
        explanation = f"### 예측 모델: {prediction.get('model_type', 'Unknown')}\n\n"
        
        explanation += "#### 주요 영향 요인\n"
        for i, factor in enumerate(prediction['key_factors'], 1):
            explanation += f"{i}. {factor}\n"
        
        explanation += f"\n#### 신뢰도: {prediction['confidence']}\n"
        
        if prediction['confidence'] == "높음":
            explanation += "- 데이터 품질이 우수하고 예측 모델의 확신도가 높습니다.\n"
        elif prediction['confidence'] == "중간":
            explanation += "- 일부 불확실성이 있지만 합리적인 예측입니다.\n"
        else:
            explanation += "- 데이터 부족 또는 경기 변수가 많아 불확실성이 높습니다.\n"
        
        return explanation


# 싱글톤 인스턴스
_predictor_instance = None


def get_score_predictor() -> ScorePredictor:
    """ScorePredictor 싱글톤 인스턴스 반환"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = ScorePredictor()
    return _predictor_instance


def predict_match_score(league: str, home_team: str, away_team: str,
                       home_data: Dict, away_data: Dict) -> Dict:
    """편의 함수: 기본 파라미터로 예측 실행"""
    predictor = get_score_predictor()
    return predictor.predict_match_score(
        league=league,
        home_team=home_team,
        away_team=away_team,
        home_data=home_data,
        away_data=away_data
    )

from modules.nba_v2.src.utils import logger

class NBAPaceModel:
    """V2 페이스 모델: 소유권(Possessions) 기반 득점 예측"""
    
    def __init__(self):
        pass
        
    def predict_possessions(self, pace_a: float, pace_b: float) -> float:
        """경기 전체 예상 소유권 계산"""
        # 기본: 두 팀 페이스의 평균
        base_poss = (pace_a + pace_b) / 2.0
        
        # 상대적 페이스 억제 효과 (수비팀이 느릴 경우 보정)
        # 예: 한 팀이 매우 느리면 전체 경기도 느려지는 경향 반영
        slow_team_factor = min(pace_a, pace_b) / 100.0
        return base_poss * (0.95 if slow_team_factor < 0.95 else 1.0)
        
    def calculate_expected_score(self, possessions: float, ortg: float, opp_drtg: float) -> float:
        """소유권 당 득점 효율을 반영한 최종 점수 계산"""
        # 100 소유권 당 득점(ORtg)과 상대의 수비 효율(DRtg) 상호작용
        # 리그 평균 115 기준 상대적 효율성 계산
        league_avg = 115.0
        def_adj = opp_drtg / league_avg
        
        # 기대 득점 = (소유권 * (ORtg / 100)) * (상대 수비 보정)
        # 수비 보정: 상대 DRtg가 평균보다 높으면(안 좋으면) 득점 증가
        efficiency = (ortg / 100.0) * (def_adj if def_adj > 1.0 else (1.0 - (1.0 - def_adj) * 0.5))
        return possessions * efficiency

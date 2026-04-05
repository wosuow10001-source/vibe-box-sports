"""
V6 Form Tracker: EMA (Exponential Moving Average) 폼 + 모멘텀 감지

기존 문제: W/D/L 단순 집계 → 골차, 상대강도 무시
개선: 지수이동평균으로 최근 경기에 가중치, 골차 반영, 모멘텀 추세 감지
"""

import numpy as np
from typing import List, Dict, Optional


class FormTracker:
    """
    EMA 기반 폼 추적 + 모멘텀 감지.
    
    점수 체계:
      W: 3점 + 골차 보너스 (max 1.5)
      D: 1점
      L: 0점 - 골차 페널티 (max -1.0)
    
    EMA: S_t = λ × X_t + (1-λ) × S_{t-1}
    λ = 0.85 (매우 최근 편향)
    """
    
    def __init__(self, decay_factor: float = 0.85):
        self.decay_factor = decay_factor
    
    def calculate_form_score(self, results: List[dict]) -> float:
        """
        EMA 폼 점수 계산.
        
        Args:
            results: [{'result': 'W'/'D'/'L', 'goals_for': int, 'goals_against': int, 
                       'opponent_rank': int (optional)}, ...]
                     최근 경기가 앞에 오도록 정렬
        
        Returns:
            float: 0-1 범위의 폼 점수 (0.5 = 평균)
        """
        if not results:
            return 0.5
        
        scores = []
        for r in results[:10]:  # 최근 10경기
            base = self._result_to_score(r)
            
            # 골차 보너스/페널티
            gf = r.get('goals_for', 0)
            ga = r.get('goals_against', 0)
            gd = gf - ga
            
            if gd > 0:
                base += min(1.5, gd * 0.3)  # 골차당 +0.3 (max 1.5)
            elif gd < 0:
                base += max(-1.0, gd * 0.2)  # 골차당 -0.2 (max -1.0)
            
            # 상대 강도 보정 (순위 기반)
            opp_rank = r.get('opponent_rank', 10)
            if opp_rank <= 5:
                base *= 1.15  # 강팀 상대 결과 15% 가중
            elif opp_rank >= 16:
                base *= 0.90  # 약팀 상대 결과 10% 감소
            
            scores.append(base)
        
        # EMA 계산
        ema = scores[0]
        for i in range(1, len(scores)):
            ema = self.decay_factor * ema + (1 - self.decay_factor) * scores[i]
        
        # 0-1 범위로 정규화 (max 가능 점수 ≈ 5.2, min ≈ -1.0)
        normalized = (ema + 1.0) / 6.2
        return max(0.0, min(1.0, normalized))
    
    def calculate_momentum(self, results: List[dict]) -> float:
        """
        모멘텀 계산: 최근 3경기 vs 이전 7경기 폼 차이.
        
        Returns:
            float: -1 ~ +1 범위 (양수 = 상승세, 음수 = 하락세)
        """
        if len(results) < 5:
            return 0.0
        
        recent_3 = results[:3]
        prev_7 = results[3:10]
        
        recent_score = self._simple_form_score(recent_3)
        prev_score = self._simple_form_score(prev_7) if prev_7 else 0.5
        
        momentum = recent_score - prev_score
        return max(-1.0, min(1.0, momentum * 2.0))  # 스케일링 후 클리핑
    
    def calculate_venue_form(self, results: List[dict], is_home: bool) -> float:
        """
        홈/원정 별도 폼 계산.
        
        Args:
            results: 전체 최근 경기 목록
            is_home: True면 홈 경기만, False면 원정 경기만 필터
        """
        filtered = [r for r in results if r.get('is_home', True) == is_home]
        if not filtered:
            return 0.5
        return self.calculate_form_score(filtered[:5])
    
    def calculate_all_form_features(self, results: List[dict], is_home: bool = True) -> dict:
        """
        모든 폼 관련 피처 한번에 계산.
        
        Returns:
            {
                'ema_form': float,       # EMA 폼 (0-1)
                'momentum': float,       # 모멘텀 (-1 ~ +1)
                'venue_form': float,     # 홈/원정 폼 (0-1)
                'clean_sheet_rate': float,  # 무실점 비율
                'scoring_rate': float       # 경기당 득점
            }
        """
        ema_form = self.calculate_form_score(results)
        momentum = self.calculate_momentum(results)
        venue_form = self.calculate_venue_form(results, is_home)
        
        # 무실점 비율
        recent = results[:10]
        clean_sheets = sum(1 for r in recent if r.get('goals_against', 0) == 0)
        clean_sheet_rate = clean_sheets / max(1, len(recent))
        
        # 경기당 평균 득점
        goals = [r.get('goals_for', 0) for r in recent]
        scoring_rate = np.mean(goals) if goals else 1.0
        
        return {
            'ema_form': round(ema_form, 4),
            'momentum': round(momentum, 4),
            'venue_form': round(venue_form, 4),
            'clean_sheet_rate': round(clean_sheet_rate, 4),
            'scoring_rate': round(scoring_rate, 4)
        }
    
    def _result_to_score(self, r: dict) -> float:
        """W/D/L 결과를 점수로 변환"""
        result = r.get('result', 'D')
        if result == 'W':
            return 3.0
        elif result == 'D':
            return 1.0
        else:
            return 0.0
    
    def _simple_form_score(self, results: List[dict]) -> float:
        """간단한 폼 점수 (0-1 범위)"""
        if not results:
            return 0.5
        total = sum(self._result_to_score(r) for r in results)
        return total / (3.0 * len(results))


def form_from_wdl_list(form_list: List[str]) -> List[dict]:
    """
    기존 시스템의 ['W', 'D', 'L', ...] 형식을 FormTracker 입력으로 변환.
    골차 정보가 없으므로 기본값 사용.
    """
    results = []
    for i, r in enumerate(form_list):
        if r == 'W':
            results.append({'result': 'W', 'goals_for': 2, 'goals_against': 0})
        elif r == 'D':
            results.append({'result': 'D', 'goals_for': 1, 'goals_against': 1})
        else:
            results.append({'result': 'L', 'goals_for': 0, 'goals_against': 2})
    return results

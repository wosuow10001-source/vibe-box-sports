"""
선수 개개인 능력치 시스템
- 종목별 능력치 정의
- 팀 전력 집계
- 포지션별 가중치
"""

from typing import Dict, List, Optional
import numpy as np


class PlayerRatingSystem:
    """선수 능력치 → 팀 전력 변환 시스템"""
    
    def __init__(self):
        # 종목별 포지션 가중치
        self.position_weights = {
            'soccer': {
                'GK': 0.15,   # 골키퍼
                'DF': 0.25,   # 수비수
                'MF': 0.30,   # 미드필더
                'FW': 0.30    # 공격수
            },
            'basketball': {
                'PG': 0.22,   # 포인트가드
                'SG': 0.20,   # 슈팅가드
                'SF': 0.20,   # 스몰포워드
                'PF': 0.19,   # 파워포워드
                'C': 0.19     # 센터
            },
            'baseball': {
                'P': 0.40,    # 투수 (가장 중요)
                'C': 0.10,    # 포수
                'IF': 0.25,   # 내야수
                'OF': 0.25    # 외야수
            },
            'volleyball': {
                'S': 0.25,    # 세터
                'OH': 0.25,   # 아웃사이드 히터
                'MB': 0.20,   # 미들 블로커
                'OP': 0.20,   # 오포짓
                'L': 0.10     # 리베로
            }
        }
    
    def calculate_team_strength(self, lineup: List[Dict], sport: str) -> Dict:
        """
        선발 라인업 기반 팀 전력 계산
        
        Args:
            lineup: 선수 리스트 [{'name': str, 'position': str, 'rating': dict, 'form': float}, ...]
            sport: 'soccer', 'basketball', 'baseball', 'volleyball'
        
        Returns:
            {
                'overall_rating': float,  # 종합 전력 (0-100)
                'attack_rating': float,   # 공격력
                'defense_rating': float,  # 수비력
                'position_strength': dict # 포지션별 전력
            }
        """
        
        if not lineup:
            return self._default_strength()
        
        if sport == 'soccer':
            return self._calculate_soccer_strength(lineup)
        elif sport == 'basketball':
            return self._calculate_basketball_strength(lineup)
        elif sport == 'baseball':
            return self._calculate_baseball_strength(lineup)
        elif sport == 'volleyball':
            return self._calculate_volleyball_strength(lineup)
        else:
            return self._default_strength()
    
    def _calculate_soccer_strength(self, lineup: List[Dict]) -> Dict:
        """축구 팀 전력 계산"""
        
        total_rating = 0
        attack_rating = 0
        defense_rating = 0
        position_count = {'GK': 0, 'DF': 0, 'MF': 0, 'FW': 0}
        
        for player in lineup:
            pos = player.get('position', 'MF')
            rating = player.get('rating', {})
            form = player.get('form', 1.0)  # 컨디션 (0.5-1.5)
            
            # 포지션별 능력치
            if pos == 'GK':
                player_rating = (
                    rating.get('goalkeeping', 70) * 0.6 +
                    rating.get('reflexes', 70) * 0.4
                )
                defense_rating += player_rating * form
            elif pos == 'DF':
                player_rating = (
                    rating.get('defending', 70) * 0.5 +
                    rating.get('physical', 70) * 0.3 +
                    rating.get('pace', 70) * 0.2
                )
                defense_rating += player_rating * form * 0.8
                attack_rating += rating.get('passing', 60) * form * 0.2
            elif pos == 'MF':
                player_rating = (
                    rating.get('passing', 70) * 0.4 +
                    rating.get('dribbling', 70) * 0.3 +
                    rating.get('vision', 70) * 0.3
                )
                attack_rating += player_rating * form * 0.5
                defense_rating += rating.get('defending', 60) * form * 0.3
            elif pos == 'FW':
                player_rating = (
                    rating.get('shooting', 70) * 0.5 +
                    rating.get('pace', 70) * 0.3 +
                    rating.get('dribbling', 70) * 0.2
                )
                attack_rating += player_rating * form
            
            total_rating += player_rating * form * self.position_weights['soccer'].get(pos, 0.2)
            position_count[pos] += 1
        
        # 정규화
        num_players = len(lineup)
        if num_players > 0:
            overall = total_rating / num_players
            attack = attack_rating / max(position_count['MF'] + position_count['FW'], 1)
            defense = defense_rating / max(position_count['GK'] + position_count['DF'], 1)
        else:
            overall = attack = defense = 70
        
        return {
            'overall_rating': min(100, max(50, overall)),
            'attack_rating': min(100, max(50, attack)),
            'defense_rating': min(100, max(50, defense)),
            'position_strength': position_count
        }
    
    def _calculate_basketball_strength(self, lineup: List[Dict]) -> Dict:
        """농구 팀 전력 계산"""
        
        total_rating = 0
        attack_rating = 0
        defense_rating = 0
        
        for player in lineup:
            rating = player.get('rating', {})
            form = player.get('form', 1.0)
            
            # 농구 능력치
            player_rating = (
                rating.get('scoring', 70) * 0.3 +
                rating.get('rebounding', 70) * 0.2 +
                rating.get('assists', 70) * 0.2 +
                rating.get('defense', 70) * 0.2 +
                rating.get('athleticism', 70) * 0.1
            )
            
            attack_rating += (rating.get('scoring', 70) + rating.get('assists', 70)) / 2 * form
            defense_rating += (rating.get('defense', 70) + rating.get('rebounding', 70)) / 2 * form
            total_rating += player_rating * form
        
        num_players = len(lineup)
        if num_players > 0:
            overall = total_rating / num_players
            attack = attack_rating / num_players
            defense = defense_rating / num_players
        else:
            overall = attack = defense = 70
        
        return {
            'overall_rating': min(100, max(50, overall)),
            'attack_rating': min(100, max(50, attack)),
            'defense_rating': min(100, max(50, defense)),
            'position_strength': {}
        }
    
    def _calculate_baseball_strength(self, lineup: List[Dict]) -> Dict:
        """야구 팀 전력 계산"""
        
        total_rating = 0
        attack_rating = 0  # 타격
        defense_rating = 0  # 투수력
        
        pitcher_rating = 0
        batter_rating = 0
        pitcher_count = 0
        batter_count = 0
        
        for player in lineup:
            pos = player.get('position', 'IF')
            rating = player.get('rating', {})
            form = player.get('form', 1.0)
            
            if pos == 'P':
                # 투수
                player_rating = (
                    rating.get('velocity', 70) * 0.3 +
                    rating.get('control', 70) * 0.3 +
                    rating.get('breaking_ball', 70) * 0.4
                )
                pitcher_rating += player_rating * form
                pitcher_count += 1
                defense_rating += player_rating * form
            else:
                # 타자
                player_rating = (
                    rating.get('contact', 70) * 0.3 +
                    rating.get('power', 70) * 0.3 +
                    rating.get('eye', 70) * 0.2 +
                    rating.get('speed', 70) * 0.2
                )
                batter_rating += player_rating * form
                batter_count += 1
                attack_rating += player_rating * form
            
            total_rating += player_rating * form
        
        num_players = len(lineup)
        if num_players > 0:
            overall = total_rating / num_players
            attack = attack_rating / max(batter_count, 1)
            defense = defense_rating / max(pitcher_count, 1)
        else:
            overall = attack = defense = 70
        
        return {
            'overall_rating': min(100, max(50, overall)),
            'attack_rating': min(100, max(50, attack)),
            'defense_rating': min(100, max(50, defense)),
            'pitcher_rating': defense,
            'position_strength': {'P': pitcher_count, 'batters': batter_count}
        }
    
    def _calculate_volleyball_strength(self, lineup: List[Dict]) -> Dict:
        """배구 팀 전력 계산"""
        
        total_rating = 0
        attack_rating = 0
        defense_rating = 0
        
        for player in lineup:
            pos = player.get('position', 'OH')
            rating = player.get('rating', {})
            form = player.get('form', 1.0)
            
            # 배구 능력치
            player_rating = (
                rating.get('spike', 70) * 0.3 +
                rating.get('block', 70) * 0.2 +
                rating.get('serve', 70) * 0.2 +
                rating.get('receive', 70) * 0.2 +
                rating.get('setting', 70) * 0.1
            )
            
            attack_rating += (rating.get('spike', 70) + rating.get('serve', 70)) / 2 * form
            defense_rating += (rating.get('block', 70) + rating.get('receive', 70)) / 2 * form
            total_rating += player_rating * form * self.position_weights['volleyball'].get(pos, 0.2)
        
        num_players = len(lineup)
        if num_players > 0:
            overall = total_rating / num_players
            attack = attack_rating / num_players
            defense = defense_rating / num_players
        else:
            overall = attack = defense = 70
        
        return {
            'overall_rating': min(100, max(50, overall)),
            'attack_rating': min(100, max(50, attack)),
            'defense_rating': min(100, max(50, defense)),
            'position_strength': {}
        }
    
    def _default_strength(self) -> Dict:
        """기본 전력 (데이터 없을 때)"""
        return {
            'overall_rating': 70.0,
            'attack_rating': 70.0,
            'defense_rating': 70.0,
            'position_strength': {}
        }
    
    def apply_tactical_adjustment(self, strength: Dict, tactic: str, sport: str) -> Dict:
        """
        전술에 따른 전력 조정
        
        Args:
            strength: 기본 전력
            tactic: '공격형', '수비형', '균형형'
            sport: 종목
        
        Returns:
            조정된 전력
        """
        
        adjusted = strength.copy()
        
        if tactic == '공격형':
            adjusted['attack_rating'] *= 1.15
            adjusted['defense_rating'] *= 0.90
        elif tactic == '수비형':
            adjusted['attack_rating'] *= 0.90
            adjusted['defense_rating'] *= 1.15
        # 균형형은 조정 없음
        
        # 범위 제한
        adjusted['attack_rating'] = min(100, max(50, adjusted['attack_rating']))
        adjusted['defense_rating'] = min(100, max(50, adjusted['defense_rating']))
        
        return adjusted


# 싱글톤 인스턴스
_rating_system = None

def get_rating_system() -> PlayerRatingSystem:
    """PlayerRatingSystem 싱글톤 반환"""
    global _rating_system
    if _rating_system is None:
        _rating_system = PlayerRatingSystem()
    return _rating_system

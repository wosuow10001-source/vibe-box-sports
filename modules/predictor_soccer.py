"""
경기 예측 모듈
- Bivariate Poisson + Dixon-Coles 보정 기반 예측
- 득점 상관(λ_C) 반영으로 난타전/저득점 경기 구분
- 저득점 영역 보정으로 무승부 확률 정확도 향상
- 모든 요소 → λ → 스코어 분포 → 승률 (완전 연동)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from scipy.stats import poisson
from scipy.special import factorial
import pickle
from pathlib import Path


class SoccerPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        
        # Dixon-Coles 보정 파라미터
        self.rho = 0.1  # 득점 상관 계수 (학습 가능)
        
        # 가중치 설정 (λ 계산용) - 최근 폼 가중치 대폭 증가
        self.weights = {
            'recent_form': 0.40,  # 22% → 40% (최근 경기력이 가장 중요)
            'head_to_head': 0.10,
            'home_advantage': 0.10,
            'player_condition': 0.12,
            'tactical_fit': 0.08,
            'weather': 0.04,
            'rest_days': 0.06,
            'motivation': 0.04,
            'injury_impact': 0.03,
            'coaching_staff': 0.03
        }
    
    def predict_match(self, home_team, away_team, home_data, away_data, 
                     weather, temperature, field_condition, match_importance,
                     rest_days_home, rest_days_away, injury_data=None, coaching_data=None,
                     lineup_home=None, lineup_away=None):
        """
        Bivariate Poisson + Dixon-Coles 기반 경기 예측
        
        1단계: 모든 요소를 수치화 (피처 엔지니어링)
        2단계: 기대 득점 λ_A, λ_B 계산
        3단계: 득점 상관 λ_C 계산 (경기 템포)
        4단계: Bivariate Poisson + Dixon-Coles로 스코어 분포 계산
        5단계: 스코어 분포에서 승률 도출
        
        Args:
            injury_data (dict, optional): {'home': [...], 'away': [...]} 형태의 부상 정보
            coaching_data (dict, optional): {'home': {...}, 'away': {...}} 형태의 코칭스태프 정보
            lineup_home (dict, optional): 홈팀 라인업 정보
            lineup_away (dict, optional): 원정팀 라인업 정보
        """
        
        # 라인업 기반 팀 데이터 보강
        if lineup_home:
            home_data = self._enhance_team_data_with_lineup(home_data, lineup_home)
        if lineup_away:
            away_data = self._enhance_team_data_with_lineup(away_data, lineup_away)
        
        # ========== 1단계: 모든 요소 수치화 ==========
        
        # 1. 최근 폼 분석
        form_score = self._analyze_form(home_data, away_data)
        
        # 2. 홈 어드밴티지
        home_advantage = self._calculate_home_advantage(home_data)
        
        # 3. 선수 컨디션 (능력치, 컨디션, 스쿼드 깊이)
        player_condition = self._analyze_player_condition(
            home_data, away_data, rest_days_home, rest_days_away
        )
        
        # 4. 전술적 궁합
        tactical_score = self._analyze_tactical_fit(home_data, away_data)
        
        # 5. 날씨 영향
        weather_impact = self._analyze_weather_impact(
            weather, temperature, field_condition
        )
        
        # 6. 경기 중요도 (동기부여)
        motivation_score = self._analyze_motivation(match_importance)
        
        # 7. 휴식일 영향
        rest_impact = self._analyze_rest_days(rest_days_home, rest_days_away)
        
        # 8. 부상 영향 분석
        injury_impact = self._analyze_injury_impact(injury_data)
        
        # 9. 코칭스태프 영향 분석
        coaching_impact = self._analyze_coaching_impact(coaching_data, home_data, away_data)
        
        # ========== 2단계: 기대 득점 λ 계산 ==========
        
        # 각 팀의 기대 득점(λ) 계산 - 모든 요소가 여기에 직접 반영
        lambda_home = self._calculate_expected_goals(
            team_data=home_data,
            opponent_data=away_data,
            is_home=True,
            form=form_score['home'],
            home_advantage=home_advantage,
            player_condition=player_condition['home'],
            tactical=tactical_score['home'],
            weather=weather_impact['home'],
            rest=rest_impact['home'],
            motivation=motivation_score,
            injury=injury_impact['home'],
            coaching=coaching_impact['home']
        )
        
        lambda_away = self._calculate_expected_goals(
            team_data=away_data,
            opponent_data=home_data,
            is_home=False,
            form=form_score['away'],
            home_advantage=0,  # 원정팀은 홈 어드밴티지 없음
            player_condition=player_condition['away'],
            tactical=tactical_score['away'],
            weather=weather_impact['away'],
            rest=rest_impact['away'],
            motivation=motivation_score,
            injury=injury_impact['away'],
            coaching=coaching_impact['away']
        )
        
        # ========== 3단계: 득점 상관(λ_C) 계산 ==========
        
        # 경기 템포 계산 (공격적 vs 수비적 경기)
        # 양팀 모두 공격적이면 λ_C 증가 (난타전)
        # 양팀 모두 수비적이면 λ_C 감소 (저득점 경기)
        avg_lambda = (lambda_home + lambda_away) / 2
        
        # 전술적 성향 반영
        home_attacking = home_data.get('avg_goals', 1.5) / (home_data.get('avg_conceded', 1.5) + 0.1)
        away_attacking = away_data.get('avg_goals', 1.5) / (away_data.get('avg_conceded', 1.5) + 0.1)
        
        # λ_C: 0 ~ 0.5 범위 (0 = 수비적, 0.5 = 매우 공격적)
        if home_attacking > 1.2 and away_attacking > 1.2:
            # 양팀 모두 공격적 → 난타전
            lambda_c = min(0.5, avg_lambda * 0.25)
        elif home_attacking < 0.8 and away_attacking < 0.8:
            # 양팀 모두 수비적 → 저득점
            lambda_c = max(0.0, avg_lambda * 0.05)
        else:
            # 중간
            lambda_c = avg_lambda * 0.15
        
        # 경기 중요도가 높으면 λ_C 감소 (신중한 경기)
        if motivation_score > 0.7:
            lambda_c *= 0.7
        
        # ========== 4단계: Bivariate Poisson + Dixon-Coles로 스코어 분포 계산 ==========
        
        score_distribution = self._calculate_score_distribution(lambda_home, lambda_away, lambda_c)
        
        # 승·무·패 확률 (스코어 분포에서 도출)
        home_win_prob = score_distribution['home_win_prob']
        draw_prob = score_distribution['draw_prob']
        away_win_prob = score_distribution['away_win_prob']
        
        # 가장 가능성 높은 스코어
        most_likely_score = score_distribution['most_likely_score']
        expected_score_home = most_likely_score[0]
        expected_score_away = most_likely_score[1]
        
        # 상위 3개 가능 스코어
        top_3_scores = score_distribution['top_3_scores']
        
        # 주요 영향 요인
        key_factors = self._identify_key_factors(
            form_score, home_advantage, player_condition, 
            tactical_score, weather_impact, rest_impact, injury_impact, coaching_impact
        )
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(
            home_data, away_data, home_win_prob, away_win_prob, draw_prob
        )
        
        return {
            'home_win_prob': home_win_prob,
            'draw_prob': draw_prob,
            'away_win_prob': away_win_prob,
            'expected_score_home': expected_score_home,
            'expected_score_away': expected_score_away,
            'top_3_scores': top_3_scores,  # 상위 3개 가능 스코어
            'lambda_home': round(lambda_home, 2),  # 디버깅용
            'lambda_away': round(lambda_away, 2),  # 디버깅용
            'lambda_c': round(lambda_c, 2),  # 득점 상관 (경기 템포)
            'key_factors': key_factors,
            'confidence': confidence,
            'detailed_scores': {
                'form': form_score,
                'home_advantage': home_advantage,
                'player_condition': player_condition,
                'tactical': tactical_score,
                'weather': weather_impact,
                'rest': rest_impact,
                'injury': injury_impact,
                'coaching': coaching_impact
            }
        }
    
    def _analyze_form(self, home_data, away_data):
        """최근 폼 분석"""
        home_form = home_data.get('recent_winrate', 0.5)
        away_form = away_data.get('recent_winrate', 0.5)
        
        # 최근 5경기 결과 가중치 (최근일수록 높음)
        home_recent = home_data.get('recent_form', [])
        away_recent = away_data.get('recent_form', [])
        
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        
        home_weighted = sum(
            (1 if r == 'W' else 0.5 if r == 'D' else 0) * w 
            for r, w in zip(home_recent, weights)
        ) if home_recent else 0.5
        
        away_weighted = sum(
            (1 if r == 'W' else 0.5 if r == 'D' else 0) * w 
            for r, w in zip(away_recent, weights)
        ) if away_recent else 0.5
        
        return {
            'home': (home_form * 0.6 + home_weighted * 0.4),
            'away': (away_form * 0.6 + away_weighted * 0.4)
        }
    
    def _calculate_home_advantage(self, home_data):
        """홈 어드밴티지 계산"""
        home_winrate = home_data.get('home_winrate', 0.5)
        
        # 홈 승률이 높을수록 어드밴티지 증가
        advantage = 0.1 + (home_winrate - 0.5) * 0.2
        
        return max(0.05, min(0.25, advantage))
    
    def _analyze_player_condition(self, home_data, away_data, 
                                  rest_days_home, rest_days_away):
        """선수 컨디션 분석 - 실제 선수 능력치 반영"""
        
        # 휴식일에 따른 컨디션
        optimal_rest = 4
        
        home_rest_factor = 1.0 - abs(rest_days_home - optimal_rest) * 0.05
        away_rest_factor = 1.0 - abs(rest_days_away - optimal_rest) * 0.05
        
        # 실제 선수 평균 능력치 반영
        home_player_rating = home_data.get('avg_player_rating', 7.0) / 10.0  # 0~1 범위로 정규화
        away_player_rating = away_data.get('avg_player_rating', 7.0) / 10.0
        
        # 실제 선수 컨디션 반영
        home_player_condition = home_data.get('avg_player_condition', 80) / 100.0  # 0~1 범위로 정규화
        away_player_condition = away_data.get('avg_player_condition', 80) / 100.0
        
        # 스쿼드 깊이 (부상 대응 능력)
        home_squad_depth = min(home_data.get('squad_depth', 20) / 25.0, 1.0)
        away_squad_depth = min(away_data.get('squad_depth', 20) / 25.0, 1.0)
        
        # 종합 컨디션 계산
        home_condition = (
            home_rest_factor * 0.3 +
            home_player_rating * 0.4 +
            home_player_condition * 0.2 +
            home_squad_depth * 0.1
        )
        
        away_condition = (
            away_rest_factor * 0.3 +
            away_player_rating * 0.4 +
            away_player_condition * 0.2 +
            away_squad_depth * 0.1
        )
        
        return {
            'home': max(0.3, min(1.0, home_condition)),
            'away': max(0.3, min(1.0, away_condition))
        }
        
        # 최근 경기 부하 (많이 뛸수록 피로도 증가)
        home_matches = len(home_data.get('recent_matches', []))
        away_matches = len(away_data.get('recent_matches', []))
        
        home_fatigue = max(0, 1.0 - home_matches * 0.02)
        away_fatigue = max(0, 1.0 - away_matches * 0.02)
        
        return {
            'home': (home_condition * 0.6 + home_fatigue * 0.4),
            'away': (away_condition * 0.6 + away_fatigue * 0.4)
        }
    
    def _analyze_tactical_fit(self, home_data, away_data):
        """전술적 궁합 분석"""
        
        # 점유율 기반 스타일 분석
        home_possession = home_data.get('possession_avg', 50)
        away_possession = away_data.get('possession_avg', 50)
        
        # 공격 vs 수비 성향
        home_goals = home_data.get('avg_goals', 1.5)
        home_conceded = home_data.get('avg_conceded', 1.5)
        away_goals = away_data.get('avg_goals', 1.5)
        away_conceded = away_data.get('avg_conceded', 1.5)
        
        # 공격력 vs 상대 수비력
        home_attack_vs_away_defense = home_goals / (away_conceded + 0.1)
        away_attack_vs_home_defense = away_goals / (home_conceded + 0.1)
        
        # 정규화 (ZeroDivisionError 방지)
        total = home_attack_vs_away_defense + away_attack_vs_home_defense
        
        if total == 0 or total < 0.01:
            # total이 0이거나 매우 작으면 균등 분배
            return {
                'home': 0.5,
                'away': 0.5
            }
        
        return {
            'home': home_attack_vs_away_defense / total,
            'away': away_attack_vs_home_defense / total
        }
    
    def _analyze_weather_impact(self, weather, temperature, field_condition):
        """날씨 영향 분석"""
        
        weather_scores = {
            '맑음': {'home': 0.5, 'away': 0.5},
            '흐림': {'home': 0.5, 'away': 0.5},
            '비': {'home': 0.55, 'away': 0.45},  # 홈팀이 약간 유리
            '눈': {'home': 0.6, 'away': 0.4},
            '강풍': {'home': 0.55, 'away': 0.45}
        }
        
        base_score = weather_scores.get(weather, {'home': 0.5, 'away': 0.5})
        
        # 극한 기온 영향
        if temperature < 5 or temperature > 35:
            base_score['home'] += 0.05  # 홈팀이 적응 유리
        
        # 경기장 상태
        field_scores = {
            '최상': 0,
            '양호': -0.02,
            '보통': -0.05,
            '불량': -0.1
        }
        
        field_penalty = field_scores.get(field_condition, 0)
        
        return {
            'home': max(0, base_score['home'] + field_penalty),
            'away': max(0, base_score['away'] + field_penalty)
        }
    
    def _analyze_motivation(self, match_importance):
        """경기 중요도에 따른 동기부여"""
        
        importance_scores = {
            '일반': 0.5,
            '중요': 0.7,
            '매우중요': 0.9
        }
        
        return importance_scores.get(match_importance, 0.5)
    
    def _analyze_rest_days(self, rest_days_home, rest_days_away):
        """휴식일 차이 분석"""
        
        optimal = 4
        
        home_score = 1.0 - abs(rest_days_home - optimal) * 0.05
        away_score = 1.0 - abs(rest_days_away - optimal) * 0.05
        
        return {
            'home': max(0.3, min(1.0, home_score)),
            'away': max(0.3, min(1.0, away_score))
        }
    
    def _analyze_injury_impact(self, injury_data):
        """
        부상 영향 분석
        
        Args:
            injury_data (dict): {'home': [...], 'away': [...]} 형태의 부상 정보
            
        Returns:
            dict: {'home': float, 'away': float} 부상 영향 점수 (0.0 ~ 1.0)
        """
        if not injury_data:
            return {'home': 1.0, 'away': 1.0}
        
        def calculate_team_injury_impact(injuries):
            """팀의 부상 영향 계산"""
            if not injuries:
                return 1.0
            
            # 부상 상태별 가중치
            status_weights = {
                'out': 0.15,           # 결장: 큰 영향
                'day-to-day': 0.05,    # 일일 점검: 작은 영향
                'questionable': 0.08,  # 출전 불투명: 중간 영향
                'doubtful': 0.12       # 출전 가능성 낮음: 큰 영향
            }
            
            total_impact = 0.0
            
            for injury in injuries:
                status = injury.get('status', '').lower()
                
                # 상태별 영향 계산
                impact = 0.0
                for key, weight in status_weights.items():
                    if key in status:
                        impact = weight
                        break
                
                # 포지션별 중요도
                position = injury.get('position', '').upper()
                position_multiplier = 1.0
                
                # NBA 포지션
                if 'G' in position and len(position) <= 2:  # Guard (G만 있는 경우)
                    position_multiplier = 1.2  # 가드는 플레이메이킹에 중요
                elif 'F' in position:  # Forward
                    position_multiplier = 1.1
                elif 'C' in position and len(position) <= 2:  # Center (C만 있는 경우)
                    position_multiplier = 1.15  # 센터는 수비/리바운드에 중요
                
                # 축구 포지션
                elif 'GK' in position:  # Goalkeeper
                    position_multiplier = 1.3  # 골키퍼는 매우 중요
                elif 'DF' in position or 'DEF' in position:  # Defender
                    position_multiplier = 1.1
                elif 'MF' in position or 'MID' in position:  # Midfielder
                    position_multiplier = 1.15  # 미드필더는 경기 흐름에 중요
                elif 'FW' in position or 'ST' in position or 'ATT' in position:  # Forward/Striker
                    position_multiplier = 1.2  # 공격수는 득점에 중요
                
                # MLB/KBO 포지션
                elif 'P' == position or 'SP' in position or 'RP' in position:  # Pitcher
                    position_multiplier = 1.3  # 투수는 매우 중요
                elif 'C' == position:  # Catcher (C만 있는 경우)
                    position_multiplier = 1.15  # 포수는 중요
                elif 'SS' in position or '2B' in position:  # Shortstop, Second Base
                    position_multiplier = 1.15  # 중요 내야수
                elif '1B' in position or '3B' in position:  # First Base, Third Base
                    position_multiplier = 1.1
                elif 'OF' in position or 'LF' in position or 'CF' in position or 'RF' in position:  # Outfield
                    position_multiplier = 1.1
                elif 'DH' in position:  # Designated Hitter
                    position_multiplier = 1.2  # 타격 전문
                
                # 배구 포지션
                elif 'OH' in position:  # Outside Hitter
                    position_multiplier = 1.25  # 주공격수
                elif 'MB' in position:  # Middle Blocker
                    position_multiplier = 1.2  # 블로킹 중요
                elif 'S' in position and len(position) <= 2:  # Setter
                    position_multiplier = 1.3  # 세터는 매우 중요
                elif 'OP' in position:  # Opposite
                    position_multiplier = 1.2  # 공격수
                elif 'L' in position and len(position) <= 2:  # Libero
                    position_multiplier = 1.1  # 수비 전문
                
                total_impact += impact * position_multiplier
            
            # 최종 점수 계산 (부상이 많을수록 점수 감소)
            # 최대 5명까지 영향 고려
            final_score = 1.0 - min(total_impact, 0.7)
            
            return max(0.3, final_score)  # 최소 0.3 보장
        
        home_injuries = injury_data.get('home', [])
        away_injuries = injury_data.get('away', [])
        
        return {
            'home': calculate_team_injury_impact(home_injuries),
            'away': calculate_team_injury_impact(away_injuries)
        }
    
    def _analyze_coaching_impact(self, coaching_data, home_data, away_data):
        """
        코칭스태프 영향 분석
        - 감독의 경력과 성과
        - 코칭스태프 규모
        - 팀 성적과의 상관관계
        """
        if not coaching_data:
            return {'home': 0.75, 'away': 0.75}  # 기본값
        
        def calculate_coaching_score(staff_info, team_data):
            """개별 팀의 코칭스태프 점수 계산"""
            if not staff_info or staff_info.get('head_coach') == 'Unknown':
                return 0.75  # 정보 없을 때 중립
            
            score = 0.5  # 기본 점수
            
            # 1. 코칭스태프 규모 (많을수록 유리)
            num_coaches = len(staff_info.get('assistant_coaches', []))
            if num_coaches >= 8:
                score += 0.15
            elif num_coaches >= 5:
                score += 0.10
            elif num_coaches >= 3:
                score += 0.05
            
            # 2. 팀 성적 반영 (감독의 능력 간접 평가)
            team_position = team_data.get('position', 10)
            if team_position <= 3:  # 상위권
                score += 0.25
            elif team_position <= 7:  # 중상위권
                score += 0.15
            elif team_position <= 12:  # 중위권
                score += 0.05
            
            # 3. 최근 폼 (감독의 전술 효과)
            recent_winrate = team_data.get('recent_winrate', 0.5)
            if recent_winrate >= 0.7:
                score += 0.15
            elif recent_winrate >= 0.5:
                score += 0.10
            elif recent_winrate >= 0.3:
                score += 0.05
            
            return min(1.0, max(0.3, score))  # 0.3 ~ 1.0 범위
        
        home_coaching = calculate_coaching_score(
            coaching_data.get('home'), home_data
        )
        away_coaching = calculate_coaching_score(
            coaching_data.get('away'), away_data
        )
        
        return {
            'home': home_coaching,
            'away': away_coaching
        }
        total = home_score + away_score
        
        return {
            'home': home_score / total,
            'away': away_score / total
        }
    
    def _calculate_expected_goals(self, team_data, opponent_data, is_home,
                                  form, home_advantage, player_condition, tactical,
                                  weather, rest, motivation, injury, coaching):
        """
        포아송 분포의 λ (기대 득점) 계산
        모든 요소가 여기에 직접 반영되어 승률과 점수가 자동으로 비례
        
        Returns:
            float: 기대 득점 λ (0.0 ~ 5.0 범위)
        """
        
        # ========== 기본 공격력 (실제 데이터) ==========
        team_avg_goals = team_data.get('avg_goals', 1.5)
        opponent_avg_conceded = opponent_data.get('avg_conceded', 1.5)
        
        # 기본 λ: 팀 공격력과 상대 수비력의 평균
        base_lambda = (team_avg_goals + opponent_avg_conceded) / 2
        
        # ========== 모든 요소를 곱셈 팩터로 변환 (0.5 ~ 2.0 범위) ==========
        
        # 1. 최근 폼 (0.6 ~ 1.4) - 가중치 증가
        form_factor = 0.6 + (form * 0.8)
        
        # 2. 홈 어드밴티지 (홈팀만, 1.0 ~ 1.3)
        home_factor = 1.0 + (home_advantage if is_home else 0)
        
        # 3. 선수 컨디션 (능력치+컨디션+스쿼드, 0.7 ~ 1.3)
        condition_factor = 0.7 + (player_condition * 0.6)
        
        # 4. 전술적 궁합 (0.8 ~ 1.2)
        tactical_factor = 0.8 + (tactical * 0.4)
        
        # 5. 날씨 영향 (0.9 ~ 1.1)
        weather_factor = 0.9 + (weather * 0.2)
        
        # 6. 휴식일 (0.85 ~ 1.15)
        rest_factor = 0.85 + (rest * 0.3)
        
        # 7. 동기부여 (0.9 ~ 1.1)
        motivation_factor = 0.9 + (motivation * 0.2)
        
        # 8. 부상 영향 (0.6 ~ 1.0, 부상 많으면 감소)
        injury_factor = 0.6 + (injury * 0.4)
        
        # 9. 코칭스태프 (0.8 ~ 1.2)
        coaching_factor = 0.8 + (coaching * 0.4)
        
        # ========== 최종 λ 계산 ==========
        lambda_value = (
            base_lambda *
            form_factor *
            home_factor *
            condition_factor *
            tactical_factor *
            weather_factor *
            rest_factor *
            motivation_factor *
            injury_factor *
            coaching_factor
        )
        
        # λ 범위 제한 (0.3 ~ 5.0)
        lambda_value = max(0.3, min(5.0, lambda_value))
        
        return lambda_value
    
    def _dixon_coles_correction(self, home_goals, away_goals, lambda_home, lambda_away):
        """
        Dixon-Coles 저득점 영역 보정
        0:0, 1:0, 0:1, 1:1 스코어의 확률을 현실적으로 조정
        
        Args:
            home_goals, away_goals: 스코어
            lambda_home, lambda_away: 기대 득점
            
        Returns:
            float: 보정 계수 (1.0 = 보정 없음)
        """
        if home_goals == 0 and away_goals == 0:
            # 0:0 무승부 - 실제로는 포아송보다 적게 발생
            return 1 - lambda_home * lambda_away * self.rho
        elif home_goals == 0 and away_goals == 1:
            # 0:1 - 약간 보정
            return 1 + lambda_home * self.rho
        elif home_goals == 1 and away_goals == 0:
            # 1:0 - 약간 보정
            return 1 + lambda_away * self.rho
        elif home_goals == 1 and away_goals == 1:
            # 1:1 무승부 - 실제로는 포아송보다 많이 발생
            return 1 - self.rho
        else:
            return 1.0
    
    def _bivariate_poisson_pmf(self, home_goals, away_goals, lambda_home, lambda_away, lambda_c):
        """
        Bivariate Poisson 확률 질량 함수
        득점 상관(λ_C)을 반영하여 난타전/저득점 경기 구분
        
        Args:
            home_goals, away_goals: 스코어
            lambda_home, lambda_away: 각 팀 기대 득점
            lambda_c: 득점 상관 파라미터 (경기 템포)
            
        Returns:
            float: 해당 스코어의 확률
        """
        # 독립 포아송 성분
        lambda_home_ind = lambda_home - lambda_c
        lambda_away_ind = lambda_away - lambda_c
        
        # 음수 방지
        lambda_home_ind = max(0.01, lambda_home_ind)
        lambda_away_ind = max(0.01, lambda_away_ind)
        
        # Bivariate Poisson 확률 계산
        prob = 0.0
        min_goals = min(home_goals, away_goals)
        
        for k in range(min_goals + 1):
            term = (
                np.exp(-lambda_home_ind - lambda_away_ind - lambda_c) *
                (lambda_home_ind ** (home_goals - k)) / factorial(home_goals - k) *
                (lambda_away_ind ** (away_goals - k)) / factorial(away_goals - k) *
                (lambda_c ** k) / factorial(k)
            )
            prob += term
        
        # Dixon-Coles 보정 적용
        correction = self._dixon_coles_correction(home_goals, away_goals, lambda_home, lambda_away)
        prob *= correction
        
        return prob
    
    def _calculate_score_distribution(self, lambda_home, lambda_away, lambda_c, max_goals=8):
        """
        Bivariate Poisson + Dixon-Coles 보정으로 스코어 확률 분포 계산
        
        Args:
            lambda_home: 홈팀 기대 득점
            lambda_away: 원정팀 기대 득점
            lambda_c: 득점 상관 (경기 템포, 0 = 수비적, 0.3+ = 공격적)
            max_goals: 계산할 최대 골 수
            
        Returns:
            dict: 승률, 무승부율, 가장 가능성 높은 스코어, 상위 3개 스코어
        """
        
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        
        score_probs = {}
        
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                # Bivariate Poisson + Dixon-Coles 확률
                prob = self._bivariate_poisson_pmf(
                    home_goals, away_goals, 
                    lambda_home, lambda_away, lambda_c
                )
                
                score_probs[(home_goals, away_goals)] = prob
                
                # 승·무·패 확률 누적
                if home_goals > away_goals:
                    home_win_prob += prob
                elif home_goals == away_goals:
                    draw_prob += prob
                else:
                    away_win_prob += prob
        
        # 확률 정규화 (합이 1이 되도록)
        total_prob = sum(score_probs.values())
        if total_prob > 0:
            score_probs = {k: v/total_prob for k, v in score_probs.items()}
            home_win_prob /= total_prob
            draw_prob /= total_prob
            away_win_prob /= total_prob
        
        # 가장 가능성 높은 스코어 Top 3
        top_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)[:3]
        most_likely_score = top_scores[0][0]
        
        return {
            'home_win_prob': home_win_prob,
            'draw_prob': draw_prob,
            'away_win_prob': away_win_prob,
            'most_likely_score': most_likely_score,
            'top_3_scores': [(score, prob) for score, prob in top_scores],
            'score_probs': score_probs
        }
    
    def _identify_key_factors(self, form_score, home_advantage, 
                             player_condition, tactical_score, 
                             weather_impact, rest_impact, injury_impact, coaching_impact):
        """주요 영향 요인 식별"""
        
        factors = []
        
        # 폼 차이
        form_diff = abs(form_score['home'] - form_score['away'])
        if form_diff > 0.2:
            better_team = "홈팀" if form_score['home'] > form_score['away'] else "원정팀"
            factors.append(f"최근 폼: {better_team}이 우세 ({form_diff:.1%} 차이)")
        
        # 홈 어드밴티지
        if home_advantage > 0.15:
            factors.append(f"강력한 홈 어드밴티지 ({home_advantage:.1%})")
        
        # 컨디션 차이
        condition_diff = abs(player_condition['home'] - player_condition['away'])
        if condition_diff > 0.15:
            better_team = "홈팀" if player_condition['home'] > player_condition['away'] else "원정팀"
            factors.append(f"선수 컨디션: {better_team}이 우세")
        
        # 부상 영향
        if injury_impact:
            injury_diff = abs(injury_impact['home'] - injury_impact['away'])
            if injury_diff > 0.15:
                better_team = "홈팀" if injury_impact['home'] > injury_impact['away'] else "원정팀"
                worse_team = "원정팀" if injury_impact['home'] > injury_impact['away'] else "홈팀"
                factors.append(f"부상 영향: {worse_team}에 주요 선수 부상")
        
        # 코칭스태프 영향 (새로 추가)
        if coaching_impact:
            coaching_diff = abs(coaching_impact['home'] - coaching_impact['away'])
            if coaching_diff > 0.15:
                better_team = "홈팀" if coaching_impact['home'] > coaching_impact['away'] else "원정팀"
                factors.append(f"코칭스태프: {better_team}의 감독/코치진이 우세")
        
        # 전술적 궁합
        tactical_diff = abs(tactical_score['home'] - tactical_score['away'])
        if tactical_diff > 0.15:
            factors.append("전술적 궁합이 경기에 큰 영향")
        
        # 날씨
        weather_diff = abs(weather_impact['home'] - weather_impact['away'])
        if weather_diff > 0.1:
            factors.append("날씨 조건이 경기에 영향")
        
        if not factors:
            factors.append("양팀 전력이 비슷하여 접전 예상")
        
        return factors
    
    def _calculate_confidence(self, home_data, away_data, 
                             home_prob, away_prob, draw_prob):
        """예측 신뢰도 계산"""
        
        # 확률 분포가 명확할수록 신뢰도 높음
        max_prob = max(home_prob, away_prob, draw_prob)
        prob_spread = max_prob - min(home_prob, away_prob, draw_prob)
        
        # 데이터 품질 (경기 수가 많을수록 신뢰도 높음)
        home_matches = len(home_data.get('recent_matches', []))
        away_matches = len(away_data.get('recent_matches', []))
        data_quality = min(1.0, (home_matches + away_matches) / 20)
        
        # 종합 신뢰도
        confidence = (prob_spread * 0.6 + data_quality * 0.4)
        
        return min(0.95, max(0.5, confidence))
    
    def train_model(self, historical_data):
        """과거 데이터로 모델 학습"""
        
        # 특성 추출
        X = self._extract_features(historical_data)
        y = historical_data['result']  # 0: 원정승, 1: 무승부, 2: 홈승
        
        # 모델 학습
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        # 모델 저장
        self.save_model()
    
    def _extract_features(self, data):
        """특성 추출"""
        # 실제 구현 시 다양한 특성 추출
        pass
    
    def save_model(self):
        """모델 저장"""
        model_file = self.model_path / "predictor_model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)
    
    def load_model(self):
        """저장된 모델 로드"""
        model_file = self.model_path / "predictor_model.pkl"
        if model_file.exists():
            with open(model_file, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
    
    def _enhance_team_data_with_lineup(self, team_data: dict, lineup: dict) -> dict:
        """
        라인업 정보로 팀 데이터 보강
        
        Args:
            team_data: 기존 팀 데이터
            lineup: 라인업 정보 (team_strength 포함)
        
        Returns:
            보강된 팀 데이터
        """
        enhanced_data = team_data.copy()
        
        team_strength = lineup.get('team_strength', {})
        
        # 라인업 기반 능력치로 업데이트
        if team_strength:
            # 공격력 반영 (avg_goals 조정)
            attack_rating = team_strength.get('attack_rating', 70)
            if 'avg_goals' in enhanced_data:
                # 능력치 70 기준, ±30% 조정
                adjustment = (attack_rating - 70) / 70 * 0.3
                enhanced_data['avg_goals'] *= (1 + adjustment)
            
            # 수비력 반영 (avg_conceded 조정)
            defense_rating = team_strength.get('defense_rating', 70)
            if 'avg_conceded' in enhanced_data:
                # 수비력 높으면 실점 감소
                adjustment = (defense_rating - 70) / 70 * 0.3
                enhanced_data['avg_conceded'] *= (1 - adjustment)
            
            # 종합 전력 저장
            enhanced_data['lineup_overall'] = team_strength.get('overall_rating', 70)
            enhanced_data['lineup_attack'] = attack_rating
            enhanced_data['lineup_defense'] = defense_rating
        
        # 전술 정보 저장
        enhanced_data['formation'] = lineup.get('formation', '4-4-2')
        enhanced_data['tactic'] = lineup.get('tactic', '균형형')
        
        return enhanced_data
    
    def load_model(self):
        """저장된 모델 로드"""
        model_file = self.model_path / "predictor_model.pkl"
        if model_file.exists():
            with open(model_file, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']

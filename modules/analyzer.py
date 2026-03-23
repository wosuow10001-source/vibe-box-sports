"""
성능 분석 모듈
- 팀 및 선수 심층 분석
- 강점/약점 파악
- 트렌드 분석
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class PerformanceAnalyzer:
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_team(self, team_name, data_collector):
        """팀 종합 분석"""
        
        team_data = data_collector.get_team_data(team_name)
        
        if not team_data:
            return None
        
        # 최근 경기 폼 차트
        form_chart = self._create_form_chart(team_data['recent_matches'])
        
        # 강점 분석
        strengths = self._identify_strengths(team_data)
        
        # 약점 분석
        weaknesses = self._identify_weaknesses(team_data)
        
        # 공격/수비 밸런스
        balance = self._analyze_balance(team_data)
        
        # 홈/원정 차이
        home_away_diff = self._analyze_home_away_difference(team_data)
        
        return {
            'team_name': team_name,
            'form_chart': form_chart,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'balance': balance,
            'home_away_diff': home_away_diff,
            'overall_rating': self._calculate_overall_rating(team_data)
        }
    
    def _create_form_chart(self, matches):
        """최근 경기 폼 차트 생성"""
        
        if not matches:
            return pd.DataFrame()
        
        dates = [m['date'] for m in matches]
        
        # 누적 승점
        points = []
        cumulative = 0
        
        for m in matches:
            if m['result'] == 'W':
                cumulative += 3
            elif m['result'] == 'D':
                cumulative += 1
            points.append(cumulative)
        
        # 득점/실점
        goals_for = [m['goals_for'] for m in matches]
        goals_against = [m['goals_against'] for m in matches]
        
        df = pd.DataFrame({
            '날짜': dates,
            '누적승점': points,
            '득점': goals_for,
            '실점': goals_against
        })
        
        return df
    
    def _identify_strengths(self, team_data):
        """강점 식별"""
        
        strengths = []
        
        # 높은 승률
        if team_data['recent_winrate'] > 0.6:
            strengths.append(f"우수한 최근 성적 (승률 {team_data['recent_winrate']:.1%})")
        
        # 강력한 공격력
        if team_data['avg_goals'] > 2.0:
            strengths.append(f"강력한 공격력 (경기당 {team_data['avg_goals']:.2f}골)")
        
        # 견고한 수비
        if team_data['avg_conceded'] < 1.0:
            strengths.append(f"견고한 수비 (경기당 {team_data['avg_conceded']:.2f}실점)")
        
        # 높은 점유율
        if team_data['possession_avg'] > 55:
            strengths.append(f"높은 점유율 ({team_data['possession_avg']:.1f}%)")
        
        # 패스 정확도
        if team_data['pass_accuracy'] > 85:
            strengths.append(f"정확한 패스 ({team_data['pass_accuracy']:.1f}%)")
        
        # 홈 강세
        if team_data['home_winrate'] > 0.7:
            strengths.append(f"강력한 홈 전적 (홈 승률 {team_data['home_winrate']:.1%})")
        
        if not strengths:
            strengths.append("균형잡힌 팀 구성")
        
        return strengths
    
    def _identify_weaknesses(self, team_data):
        """약점 식별"""
        
        weaknesses = []
        
        # 낮은 승률
        if team_data['recent_winrate'] < 0.3:
            weaknesses.append(f"부진한 최근 성적 (승률 {team_data['recent_winrate']:.1%})")
        
        # 약한 공격력
        if team_data['avg_goals'] < 1.0:
            weaknesses.append(f"부족한 득점력 (경기당 {team_data['avg_goals']:.2f}골)")
        
        # 취약한 수비
        if team_data['avg_conceded'] > 2.0:
            weaknesses.append(f"취약한 수비 (경기당 {team_data['avg_conceded']:.2f}실점)")
        
        # 낮은 점유율
        if team_data['possession_avg'] < 45:
            weaknesses.append(f"낮은 점유율 ({team_data['possession_avg']:.1f}%)")
        
        # 원정 약세
        if team_data['away_winrate'] < 0.3:
            weaknesses.append(f"원정 경기 부진 (원정 승률 {team_data['away_winrate']:.1%})")
        
        # 최근 연패
        recent_form = team_data.get('recent_form', [])
        if len(recent_form) >= 3 and all(r == 'L' for r in recent_form[:3]):
            weaknesses.append("최근 3연패로 팀 분위기 저조")
        
        if not weaknesses:
            weaknesses.append("특별한 약점 없음")
        
        return weaknesses
    
    def _analyze_balance(self, team_data):
        """공격/수비 밸런스 분석"""
        
        goals_for = team_data['avg_goals']
        goals_against = team_data['avg_conceded']
        
        goal_diff = goals_for - goals_against
        
        if goal_diff > 1.0:
            style = "공격형"
        elif goal_diff < -1.0:
            style = "수비형"
        else:
            style = "균형형"
        
        return {
            'style': style,
            'goal_difference': goal_diff,
            'attack_rating': min(10, goals_for * 3),
            'defense_rating': max(0, 10 - goals_against * 3)
        }
    
    def _analyze_home_away_difference(self, team_data):
        """홈/원정 차이 분석"""
        
        home_wr = team_data['home_winrate']
        away_wr = team_data['away_winrate']
        
        diff = home_wr - away_wr
        
        if diff > 0.3:
            tendency = "강한 홈 팀"
        elif diff < -0.1:
            tendency = "원정에서 더 강함"
        else:
            tendency = "홈/원정 차이 적음"
        
        return {
            'tendency': tendency,
            'home_winrate': home_wr,
            'away_winrate': away_wr,
            'difference': diff
        }
    
    def _calculate_overall_rating(self, team_data):
        """종합 평점 계산 (0-10)"""
        
        # 승률 (40%)
        winrate_score = team_data['recent_winrate'] * 10 * 0.4
        
        # 득실차 (30%)
        goal_diff = team_data['avg_goals'] - team_data['avg_conceded']
        goal_diff_score = min(10, max(0, (goal_diff + 2) * 2.5)) * 0.3
        
        # 점유율 (15%)
        possession_score = (team_data['possession_avg'] / 10) * 0.15
        
        # 패스 정확도 (15%)
        pass_score = (team_data['pass_accuracy'] / 10) * 0.15
        
        total = winrate_score + goal_diff_score + possession_score + pass_score
        
        return round(total, 1)
    
    def analyze_player(self, player_name, data_collector):
        """선수 개별 분석"""
        
        # 선수가 속한 팀 찾기 (간단히 첫 번째 팀으로 가정)
        teams = data_collector.get_teams()
        team_name = teams[0] if teams else "Unknown"
        
        player_data = data_collector.get_player_data(player_name, team_name)
        
        if not player_data:
            return None
        
        # 컨디션 지수
        condition_index = self._calculate_condition_index(player_data)
        
        # 최근 평점
        recent_rating = player_data['rating_avg']
        
        # 부상 위험도
        injury_risk = self._assess_injury_risk(player_data)
        
        # 퍼포먼스 트렌드
        performance_trend = self._create_performance_trend(player_data)
        
        return {
            'player_name': player_name,
            'condition_index': condition_index,
            'recent_rating': recent_rating,
            'injury_risk': injury_risk,
            'performance_trend': performance_trend,
            'key_stats': self._extract_key_stats(player_data)
        }
    
    def _calculate_condition_index(self, player_data):
        """컨디션 지수 계산 (0-10)"""
        
        base_condition = player_data['condition'] / 10
        
        # 부상 상태 반영
        injury_penalty = {
            '정상': 0,
            '경미한 부상': -2,
            '회복 중': -3
        }
        
        penalty = injury_penalty.get(player_data['injury_status'], 0)
        
        # 피로도 반영
        fatigue_penalty = player_data['fatigue_level'] / 20
        
        condition = base_condition + penalty - fatigue_penalty
        
        return max(0, min(10, condition))
    
    def _assess_injury_risk(self, player_data):
        """부상 위험도 평가"""
        
        if player_data['injury_status'] != '정상':
            return "높음"
        
        # 나이와 출전 시간 고려
        age = player_data['age']
        minutes = player_data['minutes_played']
        
        if age > 32 and minutes > 2000:
            return "중간"
        elif minutes > 2500:
            return "중간"
        else:
            return "낮음"
    
    def _create_performance_trend(self, player_data):
        """퍼포먼스 트렌드 생성"""
        
        # 시뮬레이션 데이터
        matches = player_data['matches_played']
        
        ratings = []
        for i in range(min(10, matches)):
            # 평균 평점 주변으로 변동
            rating = player_data['rating_avg'] + np.random.uniform(-0.5, 0.5)
            ratings.append(max(5.0, min(10.0, rating)))
        
        df = pd.DataFrame({
            '경기': range(1, len(ratings) + 1),
            '평점': ratings
        })
        
        return df
    
    def _extract_key_stats(self, player_data):
        """주요 통계 추출"""
        
        return {
            '출전 경기': player_data['matches_played'],
            '출전 시간': player_data['minutes_played'],
            '골': player_data['goals'],
            '도움': player_data['assists'],
            '경고': player_data['yellow_cards'],
            '퇴장': player_data['red_cards'],
            '평균 평점': player_data['rating_avg']
        }
    
    def compare_teams(self, team1_data, team2_data):
        """두 팀 비교 분석"""
        
        comparison = {
            '최근 폼': {
                'team1': team1_data['recent_winrate'],
                'team2': team2_data['recent_winrate'],
                'advantage': 'team1' if team1_data['recent_winrate'] > team2_data['recent_winrate'] else 'team2'
            },
            '공격력': {
                'team1': team1_data['avg_goals'],
                'team2': team2_data['avg_goals'],
                'advantage': 'team1' if team1_data['avg_goals'] > team2_data['avg_goals'] else 'team2'
            },
            '수비력': {
                'team1': team1_data['avg_conceded'],
                'team2': team2_data['avg_conceded'],
                'advantage': 'team1' if team1_data['avg_conceded'] < team2_data['avg_conceded'] else 'team2'
            },
            '점유율': {
                'team1': team1_data['possession_avg'],
                'team2': team2_data['possession_avg'],
                'advantage': 'team1' if team1_data['possession_avg'] > team2_data['possession_avg'] else 'team2'
            }
        }
        
        return comparison
    
    def analyze_tactical_matchup(self, team1_data, team2_data):
        """전술적 매치업 분석"""
        
        # 팀 스타일 파악
        team1_style = self._determine_team_style(team1_data)
        team2_style = self._determine_team_style(team2_data)
        
        # 궁합 분석
        matchup_analysis = self._analyze_style_matchup(team1_style, team2_style)
        
        return {
            'team1_style': team1_style,
            'team2_style': team2_style,
            'matchup': matchup_analysis
        }
    
    def _determine_team_style(self, team_data):
        """팀 스타일 판단"""
        
        possession = team_data['possession_avg']
        goals = team_data['avg_goals']
        
        if possession > 55 and goals > 2:
            return "공격적 점유형"
        elif possession > 55:
            return "점유형"
        elif goals > 2:
            return "역습형"
        else:
            return "수비형"
    
    def _analyze_style_matchup(self, style1, style2):
        """스타일 궁합 분석"""
        
        matchups = {
            ("공격적 점유형", "수비형"): "팀1 유리 - 점유율 우위",
            ("역습형", "공격적 점유형"): "팀2 유리 - 역습 기회 많음",
            ("점유형", "역습형"): "균형 - 스타일 대비",
        }
        
        key = (style1, style2)
        return matchups.get(key, "균형잡힌 매치업")

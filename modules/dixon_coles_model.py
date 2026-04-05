"""
Dixon-Coles Time-Weighted Attack/Defense Rating Model (V6)

학술 기반: Dixon & Coles (1997) "Modelling Association Football Scores"
핵심 원리:
  λ_home = α_home × β_away × γ  (홈팀 기대골)
  μ_away = α_away × β_home       (원정팀 기대골)
  
  α = 공격력 (높을수록 강함)
  β = 수비력 (높을수록 약함, 즉 실점 많음)
  γ = 홈 어드밴티지
  ρ = 저득점 상관 보정 (DC correction)
  
시간 감쇄: φ(t) = exp(-ξ × t_days)
제약조건: mean(α) = 1 (과적합 방지)
"""

import numpy as np
from scipy.optimize import minimize
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
import json
import os
from pathlib import Path


class DixonColesModel:
    """
    Time-weighted Dixon-Coles attack/defense rating system.
    Estimates per-team attack (α) and defense (β) via Maximum Likelihood.
    """
    
    # 리그별 기본 파라미터
    LEAGUE_DEFAULTS = {
        "EPL":        {"home_adv": 1.15, "avg_goals": 1.35, "rho": -0.05},
        "La Liga":    {"home_adv": 1.18, "avg_goals": 1.25, "rho": -0.04},
        "Serie A":    {"home_adv": 1.12, "avg_goals": 1.20, "rho": -0.06},
        "Bundesliga": {"home_adv": 1.10, "avg_goals": 1.45, "rho": -0.03},
        "K리그1":     {"home_adv": 1.12, "avg_goals": 1.15, "rho": -0.04},
        "MLS":        {"home_adv": 1.08, "avg_goals": 1.40, "rho": -0.03},
        "DEFAULT":    {"home_adv": 1.12, "avg_goals": 1.30, "rho": -0.05},
    }
    
    def __init__(self, league: str = "EPL", xi: float = 0.0018):
        """
        Args:
            league: 리그 이름
            xi: 시간 감쇄 계수 (일별). 0.0018 ≈ 반감기 ~385일 (약 1시즌)
        """
        self.league = league
        self.xi = xi
        self.teams: Dict[str, dict] = {}  # {team: {'attack': α, 'defense': β}}
        self.home_advantage: float = 1.0
        self.rho: float = 0.0
        self.fitted: bool = False
        self.model_path = Path("models") / "dixon_coles"
        self.model_path.mkdir(parents=True, exist_ok=True)
        
    def _dc_tau(self, x: int, y: int, lam: float, mu: float, rho: float) -> float:
        """Dixon-Coles τ 보정 함수 (저득점 영역)"""
        if x == 0 and y == 0:
            return 1 - lam * mu * rho
        elif x == 0 and y == 1:
            return 1 + lam * rho
        elif x == 1 and y == 0:
            return 1 + mu * rho
        elif x == 1 and y == 1:
            return 1 - rho
        else:
            return 1.0
    
    def _poisson_pmf(self, k: int, lam: float) -> float:
        """포아송 PMF (수치 안정)"""
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        log_pmf = k * np.log(lam) - lam - sum(np.log(i) for i in range(1, k + 1))
        return np.exp(log_pmf)
    
    def _match_log_likelihood(self, x: int, y: int, lam: float, mu: float, rho: float) -> float:
        """단일 경기의 로그 우도"""
        tau = self._dc_tau(x, y, lam, mu, rho)
        if tau <= 0:
            tau = 1e-10
        
        p_home = self._poisson_pmf(x, lam)
        p_away = self._poisson_pmf(y, mu)
        
        prob = tau * p_home * p_away
        if prob <= 0:
            return -30.0  # log(~0)
        return np.log(prob)
    
    def _time_weight(self, match_date: datetime, ref_date: datetime) -> float:
        """시간 감쇄 가중치: φ(t) = exp(-ξ × t_days)"""
        days_ago = (ref_date - match_date).days
        if days_ago < 0:
            days_ago = 0
        return np.exp(-self.xi * days_ago)
    
    def fit(self, matches: List[dict], ref_date: datetime = None):
        """
        과거 경기 데이터로 팀 레이팅 추정 (MLE).
        
        Args:
            matches: [{'date': datetime, 'home': str, 'away': str, 
                       'home_goals': int, 'away_goals': int}, ...]
            ref_date: 기준일 (기본: 오늘)
        """
        if ref_date is None:
            ref_date = datetime.now()
        
        if len(matches) < 20:
            print(f"[DC] 경기 수 부족 ({len(matches)}), 휴리스틱 모드 사용")
            self._fit_heuristic(matches)
            return
        
        # 팀 인덱스 생성
        all_teams = set()
        for m in matches:
            all_teams.add(m['home'])
            all_teams.add(m['away'])
        
        team_list = sorted(all_teams)
        n_teams = len(team_list)
        team_idx = {t: i for i, t in enumerate(team_list)}
        
        # 파라미터 벡터: [attack_1, ..., attack_n, defense_1, ..., defense_n, home_adv, rho]
        # 총 2n + 2 개
        n_params = 2 * n_teams + 2
        
        # 초기값
        x0 = np.ones(n_params)
        x0[-2] = 1.15  # home advantage
        x0[-1] = -0.05  # rho
        
        # 시간 가중치 미리 계산
        weights = [self._time_weight(m['date'], ref_date) for m in matches]
        
        def neg_log_likelihood(params):
            """음의 로그 우도 (최소화 대상)"""
            attacks = params[:n_teams]
            defenses = params[n_teams:2*n_teams]
            gamma = params[-2]
            rho = params[-1]
            
            # 제약: mean(attack) = 1
            attacks = attacks / np.mean(attacks)
            
            ll = 0.0
            for i, m in enumerate(matches):
                h_idx = team_idx[m['home']]
                a_idx = team_idx[m['away']]
                
                lam = max(0.01, attacks[h_idx] * defenses[a_idx] * gamma)
                mu = max(0.01, attacks[a_idx] * defenses[h_idx])
                
                ll += weights[i] * self._match_log_likelihood(
                    m['home_goals'], m['away_goals'], lam, mu, rho
                )
            
            # L2 정규화 (과적합 방지)
            reg = 0.001 * (np.sum((attacks - 1.0)**2) + np.sum((defenses - 1.0)**2))
            
            return -ll + reg
        
        # 최적화
        bounds = [(0.1, 5.0)] * n_teams + [(0.1, 5.0)] * n_teams + [(0.8, 1.5)] + [(-0.3, 0.1)]
        
        try:
            result = minimize(
                neg_log_likelihood, 
                x0, 
                method='L-BFGS-B',
                bounds=bounds,
                options={'maxiter': 1000, 'ftol': 1e-8}
            )
            
            if result.success or result.fun < neg_log_likelihood(x0):
                attacks = result.x[:n_teams]
                defenses = result.x[n_teams:2*n_teams]
                attacks = attacks / np.mean(attacks)  # 정규화
                
                self.home_advantage = result.x[-2]
                self.rho = result.x[-1]
                
                for team, idx in team_idx.items():
                    self.teams[team] = {
                        'attack': float(attacks[idx]),
                        'defense': float(defenses[idx])
                    }
                
                self.fitted = True
                print(f"[DC] MLE 피팅 완료: {n_teams}팀, {len(matches)}경기")
                print(f"     홈 어드밴티지: {self.home_advantage:.3f}, ρ: {self.rho:.4f}")
            else:
                print(f"[DC] MLE 수렴 실패, 휴리스틱 모드 사용")
                self._fit_heuristic(matches)
                
        except Exception as e:
            print(f"[DC] MLE 최적화 오류: {e}, 휴리스틱 모드 사용")
            self._fit_heuristic(matches)
    
    def _fit_heuristic(self, matches: List[dict] = None):
        """
        충분한 데이터가 없을 때 현재 시즌 통계로 휴리스틱 레이팅 생성.
        α_team = team_avg_goals / league_avg_goals
        β_team = team_avg_conceded / league_avg_goals
        """
        defaults = self.LEAGUE_DEFAULTS.get(self.league, self.LEAGUE_DEFAULTS["DEFAULT"])
        self.home_advantage = defaults["home_adv"]
        self.rho = defaults["rho"]
        self.fitted = True
    
    def estimate_from_stats(self, team_name: str, avg_goals: float, avg_conceded: float,
                            league_avg_goals: float = 1.35):
        """
        시즌 통계로 팀 레이팅 추정 (MLE 데이터 없을 때).
        
        Args:
            team_name: 팀명
            avg_goals: 경기당 평균 득점
            avg_conceded: 경기당 평균 실점
            league_avg_goals: 리그 평균 경기당 득점
        """
        if league_avg_goals <= 0:
            league_avg_goals = 1.35
            
        attack = max(0.3, avg_goals / league_avg_goals)
        defense = max(0.3, avg_conceded / league_avg_goals)
        
        self.teams[team_name] = {
            'attack': round(attack, 4),
            'defense': round(defense, 4)
        }
        
        if not self.fitted:
            defaults = self.LEAGUE_DEFAULTS.get(self.league, self.LEAGUE_DEFAULTS["DEFAULT"])
            self.home_advantage = defaults["home_adv"]
            self.rho = defaults["rho"]
            self.fitted = True
    
    def predict_xg(self, home_team: str, away_team: str) -> Tuple[float, float]:
        """
        두 팀간 기대골(xG) 계산.
        
        Returns:
            (home_xg, away_xg)
        """
        if home_team not in self.teams or away_team not in self.teams:
            # 등록되지 않은 팀은 평균 강도로 처리
            defaults = self.LEAGUE_DEFAULTS.get(self.league, self.LEAGUE_DEFAULTS["DEFAULT"])
            avg = defaults["avg_goals"]
            return (avg * self.home_advantage, avg)
        
        alpha_h = self.teams[home_team]['attack']
        beta_a = self.teams[away_team]['defense']
        alpha_a = self.teams[away_team]['attack']
        beta_h = self.teams[home_team]['defense']
        
        home_xg = alpha_h * beta_a * self.home_advantage
        away_xg = alpha_a * beta_h
        
        # 현실적 범위 클리핑
        home_xg = max(0.3, min(3.5, home_xg))
        away_xg = max(0.3, min(3.0, away_xg))
        
        return (round(home_xg, 3), round(away_xg, 3))
    
    def predict_score_probs(self, home_team: str, away_team: str, 
                            max_goals: int = 7) -> dict:
        """
        DC 모델로 전체 스코어라인 확률 분포 계산.
        
        Returns:
            {
                'home_win': float, 'draw': float, 'away_win': float,
                'score_probs': {(h, a): prob, ...},
                'over_2_5': float, 'btts': float,
                'home_xg': float, 'away_xg': float
            }
        """
        home_xg, away_xg = self.predict_xg(home_team, away_team)
        
        score_probs = {}
        home_win = 0.0
        draw = 0.0
        away_win = 0.0
        over_2_5 = 0.0
        btts = 0.0
        
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                p_h = self._poisson_pmf(h, home_xg)
                p_a = self._poisson_pmf(a, away_xg)
                tau = self._dc_tau(h, a, home_xg, away_xg, self.rho)
                
                prob = tau * p_h * p_a
                score_probs[(h, a)] = prob
                
                if h > a:
                    home_win += prob
                elif h == a:
                    draw += prob
                else:
                    away_win += prob
                
                if h + a > 2.5:
                    over_2_5 += prob
                if h > 0 and a > 0:
                    btts += prob
        
        # 정규화
        total = home_win + draw + away_win
        if total > 0:
            home_win /= total
            draw /= total
            away_win /= total
        
        return {
            'home_win': home_win,
            'draw': draw,
            'away_win': away_win,
            'score_probs': score_probs,
            'over_2_5': over_2_5,
            'btts': btts,
            'home_xg': home_xg,
            'away_xg': away_xg
        }
    
    def get_team_rating(self, team_name: str) -> Optional[dict]:
        """팀 레이팅 조회"""
        return self.teams.get(team_name)
    
    def save(self, filename: str = None):
        """모델 저장"""
        if filename is None:
            filename = f"dc_model_{self.league.replace(' ', '_')}.json"
        
        filepath = self.model_path / filename
        data = {
            'league': self.league,
            'xi': self.xi,
            'home_advantage': self.home_advantage,
            'rho': self.rho,
            'teams': self.teams,
            'fitted': self.fitted,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, filename: str = None) -> bool:
        """모델 로드"""
        if filename is None:
            filename = f"dc_model_{self.league.replace(' ', '_')}.json"
        
        filepath = self.model_path / filename
        if not filepath.exists():
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.league = data['league']
            self.xi = data['xi']
            self.home_advantage = data['home_advantage']
            self.rho = data['rho']
            self.teams = data['teams']
            self.fitted = data['fitted']
            return True
        except Exception:
            return False


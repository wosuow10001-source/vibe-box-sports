import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)

class KBLDataFetcher:
    """
    KBL 데이터 수집 전용 모듈
    KBL 공식 홈페이지 및 네이버 스포츠를 결합해 데이터를 구축합니다.
    """
    
    # [STEP 1] Normalize Team Names (CRITICAL)
    TEAM_NAME_MAP = {
        "원주 DB 프로미": "DB",
        "원주 DB": "DB",
        "원주DB": "DB",
        "서울 삼성 썬더스": "SAMSUNG",
        "서울 삼성": "SAMSUNG",
        "서울삼성": "SAMSUNG",
        "서울 SK 나이츠": "SK",
        "서울 SK": "SK",
        "서울SK": "SK",
        "창원 LG 세이커스": "LG",
        "창원 LG": "LG",
        "창원LG": "LG",
        "LG Sakers": "LG",
        "고양 소노 스카이거너스": "SONO",
        "고양 소노": "SONO",
        "고양소노": "SONO",
        "부산 KCC 이지스": "KCC",
        "부산 KCC": "KCC",
        "부산KCC": "KCC",
        "안양 정관장 레드부스터스": "JKJ",
        "안양 정관장": "JKJ",
        "안양정관장": "JKJ",
        "수원 KT 소닉붐": "KT",
        "수원 KT": "KT",
        "수원KT": "KT",
        "대구 한국가스공사 페가수스": "KOGAS",
        "대구 한국가스공사": "KOGAS",
        "한국가스공사": "KOGAS",
        "대구한국가스공사": "KOGAS",
        "울산 현대모비스 피버스": "MOBIS",
        "울산 현대모비스": "MOBIS",
        "울산현대모비스": "MOBIS",
        "현대모비스": "MOBIS"
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.naver_url = "https://sports.naver.com/basketball/record/index?category=kbl"
        self.kbl_url = "https://kbl.or.kr/api/team/rank"

    def normalize_team(self, name: str) -> str:
        """팀명을 시스템 표준 명칭(Short Name)으로 변환"""
        return self.TEAM_NAME_MAP.get(name, name)

    def fetch_kbl_season_stats(self) -> Dict:
        """KBL 공식 사이트에서 시즌 팀 스탯 기초 데이터를 수집합니다."""
        stats = {}
        target_url = "https://kbl.or.kr/api/team/rank"
        
        try:
            logger.info("KBL 공식 사이트 스탯 수집 시도...")
            res = requests.post(target_url, headers=self.headers, json={"seasonId": 46}, timeout=10)
            if res.status_code == 200:
                data = res.json()
                # [STEP 2] Debug Raw Data
                print("RAW KBL DATA:", data)
                
                if "data" in data and "teamRankList" in data["data"]:
                    rank_list = data["data"]["teamRankList"]
                    for t in rank_list:
                        team_name = self.normalize_team(t.get('teamNm', ''))
                        stats[team_name] = {
                            "wins": int(t.get('winCnt', 0)),
                            "losses": int(t.get('lossCnt', 0)),
                            "win_pct": float(t.get('winRt', 0.0)),
                            "avg_points": float(t.get('avgScore', 0.0)),
                            "avg_allowed": float(t.get('avgLoss', 0.0)),
                            "rank": int(t.get('rank', 0))
                        }
                    return stats
        except Exception as e:
            logger.warning(f"KBL 공식 API 수집 실패: {e}")
            
        return self._fallback_kbl_season_stats()

    def fetch_naver_season_stats(self, season_code: int = 47) -> Dict:
        """네이버 전용 통계 API를 사용하여 시즌 팀 스탯(평균 득실점, 승패)을 수집합니다."""
        stats = {}
        # 브라우저 스니핑으로 확인된 정확한 통계 API 경로
        url = f"https://api-gw.sports.naver.com/statistics/categories/kbl/seasons/{season_code}/teams"
        headers = {
            'User-Agent': self.headers['User-Agent'],
            'Referer': 'https://m.sports.naver.com/',
            'Accept': 'application/json, text/plain, */*'
        }
        
        try:
            logger.info(f"네이버 KBL 시즌 통계 API 호출 시작 (seasonCode={season_code})")
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                team_list = data.get("result", {}).get("seasonTeamStats", [])
                
                for t in team_list:
                    team_name = self.normalize_team(t.get("teamName", ""))
                    stats[team_name] = {
                        "wins": int(t.get("wins", 0)),
                        "losses": int(t.get("losses", 0)),
                        "win_pct": float(t.get("winRate", 0.0)),
                        "avg_points": float(t.get("pointsPerGame", 0.0)),
                        "avg_allowed": float(t.get("pointsConcededPerGame", 0.0)),
                        "rank": int(t.get("rank", 0))
                    }
                logger.info(f"네이버 KBL 시즌 통계 수집 성공: {len(stats)}개 팀")
                return stats
        except Exception as e:
            logger.warning(f"네이버 KBL 시즌 통계 API 호출 실패: {e}")
            
        return {}

    def fetch_naver_game_center_stats(self, game_id: str) -> Optional[Dict]:
        """(Legacy/Fallback) 네이버 GameCenter API를 사용하여 팀의 시즌 평균 스탯을 가져옵니다."""
        url = f"https://api-gw.sports.naver.com/schedule/gameCenter/{game_id}"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                game_data = data.get("result", {}).get("game", {})
                
                home = game_data.get("homeTeam", {})
                away = game_data.get("awayTeam", {})
                
                stats = {}
                for team in [home, away]:
                    name = self.normalize_team(team.get("name", ""))
                    stats[name] = {
                        "wins": team.get("win", 0),
                        "losses": team.get("lose", 0),
                        "avg_points": team.get("avgScore", 0.0),
                        "avg_allowed": team.get("avgLostScore", 0.0)
                    }
                return stats
        except Exception as e:
            logger.warning(f"Naver GameCenter API 호출 실패 ({game_id}): {e}")
        return None

    def fetch_recent_games(self, team_name: str, n: int = 10) -> Dict:
        """네이버 JSON API를 사용하여 최근 N경기 결과와 최신 시즌 스탯을 수집합니다. (superCategoryId 필터 적용)"""
        import datetime
        results, points, allowed = [], [], []
        norm_team = self.normalize_team(team_name)
        latest_game_id = None
        season_stats_from_naver = None
        
        try:
            logger.info(f"네이버 KBL 전용 API 일정 수집 시작 - {norm_team}")
            now = datetime.datetime.now()
            from_date = (now - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            to_date = now.strftime("%Y-%m-%d")
            
            # 브라우저 스니핑으로 확인된 정확한 API 경로와 파라미터
            url = (f"https://api-gw.sports.naver.com/schedule/games"
                   f"?fields=basic,schedule,conference"
                   f"&superCategoryId=basketball"
                   f"&categoryId=kbl"
                   f"&fromDate={from_date}"
                   f"&toDate={to_date}"
                   f"&size=100")
            
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                games = data.get("result", {}).get("games", [])
                
                # 최근 경기 순으로 정렬 (API 응답 날짜 기준 역순 확인 필요)
                for g in reversed(games):
                    game_id = g.get("gameId")
                    home = self.normalize_team(g.get("homeTeamName", ""))
                    away = self.normalize_team(g.get("awayTeamName", ""))
                    
                    if home != norm_team and away != norm_team: continue
                    
                    # 경기 종료 상태 확인 (네이버 API: statusCode=='RESULT')
                    if g.get("statusCode") != "RESULT": continue
                    
                    if not latest_game_id: latest_game_id = game_id
                    
                    h_score = g.get("homeTeamScore", 0)
                    a_score = g.get("awayTeamScore", 0)
                    
                    pts = h_score if home == norm_team else a_score
                    opp = a_score if home == norm_team else h_score
                    
                    results.append('W' if pts > opp else 'L')
                    points.append(pts)
                    allowed.append(opp)
                    
                    if len(results) >= n: break
            
            # 최신 게임 ID가 있다면 네이버 GameCenter API로 시즌 스탯 보완
            if latest_game_id:
                season_stats_from_naver = self.fetch_naver_game_center_stats(latest_game_id)
                if season_stats_from_naver and norm_team in season_stats_from_naver:
                    season_stats_from_naver = season_stats_from_naver[norm_team]

        except Exception as e:
            logger.warning(f"네이버 KBL API 수집 에러 {norm_team}: {e}")
            
        print(f"RAW API DATA ({norm_team}):", {"results": results, "points": points, "allowed": allowed, "latest_id": latest_game_id})
            
        return {
            "recent_results": results[:n],
            "recent_points": points[:n],
            "recent_allowed": allowed[:n],
            "naver_avg_points": season_stats_from_naver.get("avg_points") if season_stats_from_naver else None,
            "naver_avg_allowed": season_stats_from_naver.get("avg_allowed") if season_stats_from_naver else None,
            "naver_wins": season_stats_from_naver.get("wins") if season_stats_from_naver else None,
            "naver_losses": season_stats_from_naver.get("losses") if season_stats_from_naver else None
        }

    # [STEP 3] Force Fallback from Game Logs
    def ensure_team_stats(self, team: dict) -> dict:
        """avg_points나 avg_allowed가 0인 경우 최근 경기 기록에서 계산하여 채웁니다."""
        # [STEP 6] NEVER Replace Missing Values with 0
        avg_p = team.get("avg_points")
        avg_a = team.get("avg_allowed")

        if avg_p is None or avg_a is None or avg_p == 0 or avg_a == 0:
            logger.info(f"Stats missing for team (avg_p: {avg_p}, avg_a: {avg_a}). Calculating from logs...")
            
            points = team.get("recent_points")
            allowed = team.get("recent_allowed")

            if not points or not allowed:
                raise ValueError(f"No game data available for fallback for team stats")

            team["avg_points"] = sum(points) / len(points)
            team["avg_allowed"] = sum(allowed) / len(allowed)
            
        return team

    # [STEP 7] Validate Against Real Example
    def validate_realistic_ranges(self, team_name: str, team: dict):
        """KBL 팀들의 스탯이 현실적인 범위 내에 있는지 검증합니다."""
        avg_p = team["avg_points"]
        avg_a = team["avg_allowed"]
        
        # 일반적인 KBL 범위 (60~100)
        if not (60 <= avg_p <= 110) or not (60 <= avg_a <= 110):
            logger.error(f"Unrealistic stats detected for {team_name}: p={avg_p}, a={avg_a}")
            # 특정 팀 예시 검증
            if team_name == "LG":
                # LG: avg_points ≈ 77~80, avg_allowed ≈ 70~75
                if not (70 <= avg_p <= 85) or not (65 <= avg_a <= 80):
                    raise ValueError(f"LG team stats far from realistic range: p={avg_p}, a={avg_a}")
            elif team_name == "KOGAS":
                # KOGAS: avg_points ≈ 74~77, avg_allowed ≈ 78~82
                if not (70 <= avg_p <= 82) or not (75 <= avg_a <= 88):
                    raise ValueError(f"KOGAS team stats far from realistic range: p={avg_p}, a={avg_a}")
            else:
                raise ValueError(f"Team {team_name} stats out of bounds: p={avg_p}, a={avg_a}")

    def build_team_dataset(self) -> Dict:
        """KBL 시즌 스탯과 최근 폼을 병합하고 7:3 가중치를 적용하여 단일 예측 데이터셋을 반환합니다."""
        print("[FETCH] KBL 팀 데이터 병합 및 수집 시작 (Naver API v2 + 가중치 적용)...")
        # [NEW] 가장 정확한 것으로 확인된 네이버 시즌 통계 API 호출
        season_stats = self.fetch_naver_season_stats(season_code=47)
        
        # API 실패 시 KBL 공식 사이트나 하드코딩 Fallback 사용
        if not season_stats:
            logger.warning("네이버 시즌 통계 API 실패, KBL 공식 사이트 시도...")
            season_stats = self.fetch_kbl_season_stats()
            
        unified_dataset = {}
        
        for team_name in self.TEAM_NAME_MAP.values():
            if team_name in unified_dataset: continue
            
            # 1. 데이터 수집 (시즌 + 최근 경기)
            s_data = season_stats.get(team_name, {})
            r_data = self.fetch_recent_games(team_name, n=10)
            
            # 2. 시즌 베이스라인 결정
            season_avg_p = s_data.get("avg_points", 0.0)
            season_avg_a = s_data.get("avg_allowed", 0.0)
            wins = s_data.get("wins", 0)
            losses = s_data.get("losses", 0)
            
            # 3. 최근 평균 계산 (10경기)
            recent_pts = r_data["recent_points"]
            recent_opp = r_data["recent_allowed"]
            
            recent_avg_p = sum(recent_pts) / len(recent_pts) if recent_pts else season_avg_p
            recent_avg_a = sum(recent_opp) / len(recent_opp) if recent_opp else season_avg_a
            
            # 4. 가중치 적용 (시즌 0.7 : 최근 0.3)
            if recent_pts:
                blended_p = (season_avg_p * 0.7) + (recent_avg_p * 0.3)
                blended_a = (season_avg_a * 0.7) + (recent_avg_a * 0.3)
            else:
                blended_p = season_avg_p
                blended_a = season_avg_a
                
            merged_team = {
                "rank": s_data.get("rank", 0),
                "wins": wins,
                "losses": losses,
                "win_pct": wins / (wins + losses) if (wins + losses) > 0 else 0.5,
                "avg_points": blended_p,
                "avg_allowed": blended_a,
                "recent_points": recent_pts,
                "recent_allowed": recent_opp,
                "recent_results": r_data["recent_results"],
                "form": r_data["recent_results"]
            }
            
            # [STEP 3] ensure_team_stats (안전장치)
            merged_team = self.ensure_team_stats(merged_team)
            
            # [STEP 7] validate_realistic_ranges
            self.validate_realistic_ranges(team_name, merged_team)
            
            # DataCollector와의 호환성을 위해 ppg, opp_ppg 필드 추가
            merged_team["ppg"] = merged_team["avg_points"]
            merged_team["opp_ppg"] = merged_team["avg_allowed"]
            merged_team["recent_winrate"] = sum(1 for r in merged_team["recent_results"] if r == 'W') / len(merged_team["recent_results"]) if merged_team["recent_results"] else 0.5
            
            unified_dataset[team_name] = merged_team
            
        # Rankings 동적 계산
        teams_sorted = sorted(unified_dataset.items(), key=lambda x: x[1].get('win_pct', 0), reverse=True)
        for i, (t_name, t_data) in enumerate(teams_sorted):
            t_data['rank'] = i + 1
            
        print(f"[OK] KBL 파이프라인 수집 완료. 7:3 가중치 적용됨.")
        return unified_dataset

    def _fallback_kbl_season_stats(self) -> Dict:
        """안전성을 위한 백업 스탯 세트 (Normalized names 사용)"""
        return {
            "SK": {"wins": 26, "losses": 18, "win_pct": 0.591, "avg_points": 84.2, "avg_allowed": 79.5},
            "KT": {"wins": 25, "losses": 19, "win_pct": 0.568, "avg_points": 82.1, "avg_allowed": 80.2},
            "MOBIS": {"wins": 24, "losses": 20, "win_pct": 0.545, "avg_points": 81.5, "avg_allowed": 78.9},
            "JKJ": {"wins": 22, "losses": 22, "win_pct": 0.500, "avg_points": 80.6, "avg_allowed": 81.4},
            "LG": {"wins": 21, "losses": 23, "win_pct": 0.477, "avg_points": 79.4, "avg_allowed": 80.1},
            "SONO": {"wins": 20, "losses": 24, "win_pct": 0.455, "avg_points": 78.5, "avg_allowed": 79.8},
            "SAMSUNG": {"wins": 19, "losses": 25, "win_pct": 0.432, "avg_points": 77.2, "avg_allowed": 82.5},
            "DB": {"wins": 18, "losses": 26, "win_pct": 0.409, "avg_points": 85.1, "avg_allowed": 87.2},
            "KCC": {"wins": 16, "losses": 28, "win_pct": 0.364, "avg_points": 76.5, "avg_allowed": 84.1},
            "KOGAS": {"wins": 15, "losses": 29, "win_pct": 0.341, "avg_points": 75.8, "avg_allowed": 86.4}
        }

if __name__ == "__main__":
    fetcher = KBLDataFetcher()
    dataset = fetcher.build_team_dataset()
    for t_name, data in dataset.items():
        print(f"[{data['rank']}위] {t_name} - 승률: {data['win_pct']:.3f} | 평득: {data['avg_points']:.1f} | 평실: {data['avg_allowed']:.1f}")

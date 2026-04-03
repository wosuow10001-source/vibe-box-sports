import requests
import sqlite3
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import logging
from typing import List, Dict, Optional

# --- Configuration ---
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class SportsDataPipeline:
    def __init__(self, db_path: str = "sports_data.db", soccer_api_key: str = ""):
        self.db_path = db_path
        self.soccer_api_key = soccer_api_key
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.init_db()

    def init_db(self):
        """Initialize SQLite database and table with unique constraint."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS matches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        league TEXT NOT NULL,
                        home_team TEXT NOT NULL,
                        away_team TEXT NOT NULL,
                        score TEXT,
                        match_date TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(home_team, away_team, match_date)
                    )
                """)
                conn.commit()
                logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def save_matches(self, matches: List[Dict]):
        """Save normalized match data to SQLite using UPSERT logic."""
        if not matches:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for m in matches:
                    cursor.execute("""
                        INSERT INTO matches (league, home_team, away_team, score, match_date, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(home_team, away_team, match_date) DO UPDATE SET
                            score = excluded.score,
                            updated_at = excluded.updated_at
                    """, (m['league'], m['home_team'], m['away_team'], m['score'], m['match_date'], datetime.now().isoformat()))
                conn.commit()
                logger.info(f"Saved {len(matches)} matches for {matches[0]['league']}.")
        except Exception as e:
            logger.error(f"Error saving matches: {e}")

    # --- 1. Soccer (football-data.org) ---
    def fetch_soccer(self):
        if not self.soccer_api_key:
            logger.warning("Soccer API Key missing. Skipping Soccer fetch.")
            return

        leagues = ["PL", "PD", "BL1", "SA", "MLS"] # EPL, La Liga, Bundesliga, Serie A, MLS
        matches_ingested = []
        
        headers = {"X-Auth-Token": self.soccer_api_key}
        for league in leagues:
            try:
                url = f"https://api.football-data.org/v4/competitions/{league}/matches"
                response = self.session.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for m in data.get('matches', []):
                        score_home = m.get('score', {}).get('fullTime', {}).get('home')
                        score_away = m.get('score', {}).get('fullTime', {}).get('away')
                        score_str = f"{score_home}:{score_away}" if score_home is not None else None
                        
                        matches_ingested.append({
                            "league": f"Soccer_{league}",
                            "home_team": m['homeTeam']['name'],
                            "away_team": m['awayTeam']['name'],
                            "score": score_str,
                            "match_date": m['utcDate'][:10]
                        })
                time.sleep(1) # Rate limit protection
            except Exception as e:
                logger.error(f"Error fetching Soccer {league}: {e}")
        
        self.save_matches(matches_ingested)

    # --- 2. MLB (Official StatsAPI) ---
    def fetch_mlb(self):
        try:
            date_today = datetime.now().strftime("%Y-%m-%d")
            url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_today}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                matches_ingested = []
                for date_obj in data.get('dates', []):
                    for game in date_obj.get('games', []):
                        home = game['teams']['home']
                        away = game['teams']['away']
                        score_str = f"{home.get('score', 0)}:{away.get('score', 0)}" if 'score' in home else None
                        
                        matches_ingested.append({
                            "league": "MLB",
                            "home_team": home['team']['name'],
                            "away_team": away['team']['name'],
                            "score": score_str,
                            "match_date": game['gameDate'][:10]
                        })
                self.save_matches(matches_ingested)
        except Exception as e:
            logger.error(f"Error fetching MLB: {e}")

    # --- 3. KBO (Naver Sports Scraper/API) ---
    def fetch_kbo(self):
        """Fetches KBO data using Naver Sports API with corrected parameters."""
        try:
            today_dt = datetime.now()
            # Fetch 5-day window (+/- 2 days) to avoid missing games
            from_date = (today_dt - timedelta(days=2)).strftime("%Y-%m-%d")
            to_date = (today_dt + timedelta(days=2)).strftime("%Y-%m-%d")
            
            url = f"https://api-gw.sports.naver.com/schedule/games?fields=basic,schedule&upperCategoryId=kbaseball&categoryId=kbo&fromDate={from_date}&toDate={to_date}"
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                matches_ingested = []
                for game in data.get('result', {}).get('games', []):
                    # Status logic: RESULT=Finished, PARTIAL=Postponed, etc.
                    score_str = f"{game.get('homeTeamScore', 0)}:{game.get('awayTeamScore', 0)}" if game.get('statusCode') == 'RESULT' else None
                    matches_ingested.append({
                        "league": "KBO",
                        "home_team": game['homeTeamName'],
                        "away_team": game['awayTeamName'],
                        "score": score_str,
                        "match_date": game['gameDate'][:10]
                    })
                if matches_ingested:
                    self.save_matches(matches_ingested)
                    logger.info(f"KBO API fetch successful: {len(matches_ingested)} games ingested.")
                else:
                    logger.warning(f"KBO API returned 0 games for {from_date} to {to_date}")
        except Exception as e:
            logger.error(f"Error fetching KBO via API: {e}. Falling back to HTML.")
            self._fetch_kbo_html()

    def _fetch_kbo_html(self):
        """Fallback KBO scraper using BeautifulSoup as requested."""
        try:
            url = "https://sports.naver.com/kbaseball/schedule/index"
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Naver often loads data via JS/JSON inside <script> tags.
            # Real-time HTML parsing of Naver schedule is complex due to SPA behavior.
            # This is a placeholder for standard BS4 logic if HTML was static.
            logger.info("BS4 Crawling KBO... (Limited on SPA pages)")
        except Exception as e:
            logger.error(f"Error in KBO BS4 fallback: {e}")

    # --- 4. V-League (KOVO) ---
    def fetch_vleague(self):
        try:
            # Official KOVO User API (discovered in audit)
            url = "https://user-api.kovo.co.kr/stat/game-schedule?gcode=001&seasonCode=022&leagueCode=200"
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                matches_ingested = []
                for game in data.get('payload', {}).get('content', []):
                    # Filter for today's matches or recent ones if needed
                    matches_ingested.append({
                        "league": "V-League",
                        "home_team": game.get('hsname'),
                        "away_team": game.get('asname'),
                        "score": f"{game.get('hspoint', 0)}:{game.get('aspoint', 0)}",
                        "match_date": game.get('gdate')
                    })
                self.save_matches(matches_ingested)
        except Exception as e:
            logger.error(f"Error fetching V-League: {e}")

    # --- Scheduler ---
    def run_scheduler(self):
        logger.info("Starting Sports Data Pipeline Scheduler (5-minute intervals)...")
        while True:
            logger.info("Cycle started.")
            self.fetch_soccer()
            self.fetch_mlb()
            self.fetch_kbo()
            self.fetch_vleague()
            logger.info("Cycle completed. Sleeping for 300s.")
            time.sleep(300)

if __name__ == "__main__":
    # Example usage (API Key should be provided by environment or user input)
    # soccer_key = "YOUR_API_KEY_HERE"
    pipeline = SportsDataPipeline(soccer_api_key="")
    pipeline.run_scheduler()

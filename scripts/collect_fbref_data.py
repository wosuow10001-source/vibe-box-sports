"""
V6 Data Collector: FBref Historical Match Results
Usage: python scripts/collect_fbref_data.py --league EPL --season 2024-2025
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
from pathlib import Path
import argparse
from datetime import datetime

class FBrefCollector:
    def __init__(self):
        self.base_url = "https://fbref.com"
        self.data_dir = Path("data/historical")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def fetch_match_results(self, league_id, season_str):
        """
        Fetch results and xG for a specific league and season.
        league_id: e.g., '9' for EPL
        season_str: e.g., '2024-2025'
        """
        url = f"{self.base_url}/en/comps/{league_id}/schedule/{season_str}-Scores-and-Fixtures"
        print(f"[FETCH] Scraping match results from: {url}")
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch data: {response.status_code}")
            return None

        # Parse table
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'sched_all'})
        if not table:
            print("[ERROR] Match results table not found.")
            return None

        df = pd.read_html(str(table))[0]
        
        # Data Cleaning
        # Filter out rows that are not matches (headers)
        df = df[df['Date'].notna()]
        df = df[df['Home'] != 'Home'] # Header filter
        
        # Select important columns
        cols = ['Date', 'Home', 'Away', 'Score', 'xG', 'xG.1']
        df = df[cols].copy()
        
        # Parse score
        def parse_score(score_str):
            if pd.isna(score_str) or '–' not in score_str:
                return None, None
            try:
                parts = score_str.split('–')
                return int(parts[0]), int(parts[1])
            except:
                return None, None

        df['home_goals'], df['away_goals'] = zip(*df['Score'].apply(parse_score))
        df = df.dropna(subset=['home_goals']).reset_index(drop=True)
        
        # Save to CSV
        output_file = self.data_dir / f"{league_id}_{season_str}.csv"
        df.to_csv(output_file, index=False)
        print(f"[OK] Saved {len(df)} matches to {output_file}")
        return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", default="9", help="League ID (9 for EPL)")
    parser.add_argument("--season", default="2024-2025", help="Season (e.g., 2024-2025)")
    args = parser.parse_args()
    
    collector = FBrefCollector()
    collector.fetch_match_results(args.league, args.season)

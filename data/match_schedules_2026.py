"""
2025-26 시즌 경기 일정 데이터
2026년 3월 20일 기준 - 다가오는 경기 일정
"""

from datetime import datetime

# NBA 경기 일정 (2026년 3월 21일 - 3월 27일)
NBA_SCHEDULE = {
    "2026-03-21": [
        {"home": "Boston Celtics", "away": "Miami Heat", "time": "19:30", "venue": "TD Garden", "tv": "ESPN"},
        {"home": "New York Knicks", "away": "Philadelphia 76ers", "time": "19:30", "venue": "Madison Square Garden", "tv": "TNT"},
        {"home": "Milwaukee Bucks", "away": "Chicago Bulls", "time": "20:00", "venue": "Fiserv Forum", "tv": "NBA TV"},
        {"home": "Denver Nuggets", "away": "Phoenix Suns", "time": "21:00", "venue": "Ball Arena", "tv": "ESPN"},
        {"home": "Los Angeles Lakers", "away": "Golden State Warriors", "time": "22:30", "venue": "Crypto.com Arena", "tv": "ABC"},
    ],
    "2026-03-22": [
        {"home": "Detroit Pistons", "away": "Cleveland Cavaliers", "time": "15:00", "venue": "Little Caesars Arena", "tv": "NBC"},
        {"home": "Toronto Raptors", "away": "Charlotte Hornets", "time": "19:00", "venue": "Scotiabank Arena", "tv": "TSN"},
        {"home": "Oklahoma City Thunder", "away": "San Antonio Spurs", "time": "20:00", "venue": "Paycom Center", "tv": "TNT"},
        {"home": "Dallas Mavericks", "away": "Houston Rockets", "time": "20:30", "venue": "American Airlines Center", "tv": "ESPN"},
        {"home": "Portland Trail Blazers", "away": "LA Clippers", "time": "22:00", "venue": "Moda Center", "tv": "Prime Video"},
    ],
    "2026-03-23": [
        {"home": "Atlanta Hawks", "away": "Orlando Magic", "time": "19:00", "venue": "State Farm Arena", "tv": "NBA TV"},
        {"home": "Washington Wizards", "away": "Brooklyn Nets", "time": "19:00", "venue": "Capital One Arena", "tv": "NBC Sports"},
        {"home": "Minnesota Timberwolves", "away": "Memphis Grizzlies", "time": "20:00", "venue": "Target Center", "tv": "ESPN"},
        {"home": "Sacramento Kings", "away": "Utah Jazz", "time": "22:00", "venue": "Golden 1 Center", "tv": "NBA TV"},
    ],
    "2026-03-24": [
        {"home": "Indiana Pacers", "away": "New Orleans Pelicans", "time": "19:00", "venue": "Gainbridge Fieldhouse", "tv": "Bally Sports"},
        {"home": "Phoenix Suns", "away": "Los Angeles Lakers", "time": "21:30", "venue": "Footprint Center", "tv": "TNT"},
    ],
}

# EPL 경기 일정 (2026년 3월 21일 - 3월 22일, Matchweek 32)
EPL_SCHEDULE = {
    "2026-03-21": [
        {"home": "Arsenal", "away": "Manchester City", "time": "12:30", "venue": "Emirates Stadium", "tv": "Sky Sports"},
        {"home": "Liverpool", "away": "Chelsea", "time": "15:00", "venue": "Anfield", "tv": "Sky Sports"},
        {"home": "Brighton", "away": "Sunderland", "time": "15:00", "venue": "Amex Stadium", "tv": "Sky Sports"},
        {"home": "Aston Villa", "away": "Newcastle", "time": "15:00", "venue": "Villa Park", "tv": "Sky Sports"},
        {"home": "Fulham", "away": "Brentford", "time": "15:00", "venue": "Craven Cottage", "tv": "Sky Sports"},
        {"home": "Tottenham", "away": "Manchester United", "time": "17:30", "venue": "Tottenham Hotspur Stadium", "tv": "Sky Sports"},
    ],
    "2026-03-22": [
        {"home": "West Ham", "away": "Everton", "time": "14:00", "venue": "London Stadium", "tv": "Sky Sports"},
        {"home": "Crystal Palace", "away": "Bournemouth", "time": "14:00", "venue": "Selhurst Park", "tv": "Sky Sports"},
        {"home": "Nottingham Forest", "away": "Leeds United", "time": "16:30", "venue": "City Ground", "tv": "Sky Sports"},
        {"home": "Wolverhampton", "away": "Burnley", "time": "16:30", "venue": "Molineux Stadium", "tv": "Sky Sports"},
    ],
}

# La Liga 경기 일정 (2026년 3월 21일 - 3월 22일, Matchweek 29)
LA_LIGA_SCHEDULE = {
    "2026-03-21": [
        {"home": "Barcelona", "away": "Atletico Madrid", "time": "21:00", "venue": "Camp Nou", "tv": "LaLiga TV"},
        {"home": "Real Betis", "away": "Villarreal", "time": "16:15", "venue": "Benito Villamarín", "tv": "LaLiga TV"},
        {"home": "Celta Vigo", "away": "Real Sociedad", "time": "14:00", "venue": "Balaídos", "tv": "LaLiga TV"},
        {"home": "Espanyol", "away": "Oviedo", "time": "14:00", "venue": "RCDE Stadium", "tv": "LaLiga TV"},
        {"home": "Getafe", "away": "Valencia", "time": "18:30", "venue": "Coliseum Alfonso Pérez", "tv": "LaLiga TV"},
    ],
    "2026-03-22": [
        {"home": "Real Madrid", "away": "Sevilla", "time": "21:00", "venue": "Santiago Bernabéu", "tv": "LaLiga TV"},
        {"home": "Athletic Bilbao", "away": "Osasuna", "time": "16:15", "venue": "San Mamés", "tv": "LaLiga TV"},
        {"home": "Girona", "away": "Rayo Vallecano", "time": "14:00", "venue": "Estadi Montilivi", "tv": "LaLiga TV"},
        {"home": "Mallorca", "away": "Deportivo Alaves", "time": "14:00", "venue": "Son Moix", "tv": "LaLiga TV"},
        {"home": "Elche", "away": "Levante", "time": "18:30", "venue": "Martínez Valero", "tv": "LaLiga TV"},
    ],
}

# Bundesliga 경기 일정 (2026년 3월 21일 - 3월 22일, Matchweek 27)
BUNDESLIGA_SCHEDULE = {
    "2026-03-21": [
        {"home": "Bayern Munich", "away": "Borussia Dortmund", "time": "18:30", "venue": "Allianz Arena", "tv": "Sky Sports"},
        {"home": "RB Leipzig", "away": "Bayer Leverkusen", "time": "15:30", "venue": "Red Bull Arena", "tv": "Sky Sports"},
        {"home": "TSG Hoffenheim", "away": "VfB Stuttgart", "time": "15:30", "venue": "PreZero Arena", "tv": "Sky Sports"},
        {"home": "Eintracht Frankfurt", "away": "SC Freiburg", "time": "15:30", "venue": "Deutsche Bank Park", "tv": "Sky Sports"},
        {"home": "1. FC Köln", "away": "Borussia Mönchengladbach", "time": "15:30", "venue": "RheinEnergieStadion", "tv": "Sky Sports"},
    ],
    "2026-03-22": [
        {"home": "1. FC Union Berlin", "away": "FC Augsburg", "time": "15:30", "venue": "Stadion An der Alten Försterei", "tv": "Sky Sports"},
        {"home": "Hamburger SV", "away": "Mainz 05", "time": "17:30", "venue": "Volksparkstadion", "tv": "Sky Sports"},
        {"home": "Werder Bremen", "away": "FC St. Pauli", "time": "15:30", "venue": "Weserstadion", "tv": "Sky Sports"},
        {"home": "VfL Wolfsburg", "away": "1. FC Heidenheim", "time": "15:30", "venue": "Volkswagen Arena", "tv": "Sky Sports"},
    ],
}

# Serie A 경기 일정 (2026년 3월 21일 - 3월 22일, Matchweek 30)
SERIE_A_SCHEDULE = {
    "2026-03-21": [
        {"home": "Inter Milan", "away": "Napoli", "time": "20:45", "venue": "San Siro", "tv": "DAZN"},
        {"home": "AC Milan", "away": "Juventus", "time": "18:00", "venue": "San Siro", "tv": "DAZN"},
        {"home": "Roma", "away": "Atalanta", "time": "15:00", "venue": "Stadio Olimpico", "tv": "DAZN"},
        {"home": "Lazio", "away": "Bologna", "time": "15:00", "venue": "Stadio Olimpico", "tv": "DAZN"},
        {"home": "Como", "away": "Sassuolo", "time": "12:30", "venue": "Stadio Giuseppe Sinigaglia", "tv": "DAZN"},
    ],
    "2026-03-22": [
        {"home": "Fiorentina", "away": "Udinese", "time": "15:00", "venue": "Stadio Artemio Franchi", "tv": "DAZN"},
        {"home": "Torino", "away": "Parma", "time": "15:00", "venue": "Stadio Olimpico Grande Torino", "tv": "DAZN"},
        {"home": "Genoa", "away": "Cagliari", "time": "18:00", "venue": "Stadio Luigi Ferraris", "tv": "DAZN"},
        {"home": "Lecce", "away": "Cremonese", "time": "12:30", "venue": "Stadio Via del Mare", "tv": "DAZN"},
        {"home": "Pisa", "away": "Hellas Verona", "time": "20:45", "venue": "Arena Garibaldi", "tv": "DAZN"},
    ],
}

def get_upcoming_matches(league, days=7):
    """
    특정 리그의 다가오는 경기 반환
    
    Args:
        league: 리그 이름 ("NBA", "EPL", "La Liga", "Bundesliga", "Serie A")
        days: 앞으로 며칠간의 경기를 가져올지 (기본값: 7일)
    
    Returns:
        list: 경기 일정 리스트
    """
    schedules = {
        "NBA": NBA_SCHEDULE,
        "EPL": EPL_SCHEDULE,
        "La Liga": LA_LIGA_SCHEDULE,
        "Bundesliga": BUNDESLIGA_SCHEDULE,
        "Serie A": SERIE_A_SCHEDULE,
    }
    
    league_schedule = schedules.get(league, {})
    all_matches = []
    
    for date, matches in league_schedule.items():
        for match in matches:
            match_info = match.copy()
            match_info['date'] = date
            all_matches.append(match_info)
    
    return all_matches

def get_team_next_matches(league, team_name, limit=5):
    """
    특정 팀의 다음 경기 반환
    
    Args:
        league: 리그 이름
        team_name: 팀 이름
        limit: 반환할 경기 수 (기본값: 5)
    
    Returns:
        list: 팀의 다음 경기 리스트
    """
    all_matches = get_upcoming_matches(league)
    team_matches = []
    
    for match in all_matches:
        if match['home'] == team_name or match['away'] == team_name:
            team_matches.append(match)
            if len(team_matches) >= limit:
                break
    
    return team_matches

def get_matches_by_date(date_str):
    """
    특정 날짜의 모든 리그 경기 반환
    
    Args:
        date_str: 날짜 문자열 (형식: "YYYY-MM-DD")
    
    Returns:
        dict: 리그별 경기 딕셔너리
    """
    all_schedules = {
        "NBA": NBA_SCHEDULE.get(date_str, []),
        "EPL": EPL_SCHEDULE.get(date_str, []),
        "La Liga": LA_LIGA_SCHEDULE.get(date_str, []),
        "Bundesliga": BUNDESLIGA_SCHEDULE.get(date_str, []),
        "Serie A": SERIE_A_SCHEDULE.get(date_str, []),
    }
    
    return {league: matches for league, matches in all_schedules.items() if matches}

def get_all_upcoming_matches():
    """
    모든 리그의 다가오는 경기 반환
    
    Returns:
        dict: 리그별 경기 딕셔너리
    """
    return {
        "NBA": get_upcoming_matches("NBA"),
        "EPL": get_upcoming_matches("EPL"),
        "La Liga": get_upcoming_matches("La Liga"),
        "Bundesliga": get_upcoming_matches("Bundesliga"),
        "Serie A": get_upcoming_matches("Serie A"),
    }

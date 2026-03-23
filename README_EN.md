# 🏆 Personal Sports Match Prediction System

A comprehensive system that analyzes various factors including player condition, tactics, and stadium conditions to predict match outcomes.

## Key Features

### 1. Match Prediction
- Home/Away team selection and data analysis
- Weather, temperature, and field condition consideration
- Rest days and match importance factors
- Win/Draw/Loss probability calculation
- Expected score prediction

### 2. Analysis Factors

#### Team Analysis
- Recent match form (weighted last 5 games)
- Home/Away win rates
- Average goals scored/conceded
- Possession and pass accuracy
- Automatic strength/weakness identification

#### Player Analysis
- Individual player condition index
- Recent match ratings
- Injury risk assessment
- Fatigue analysis
- Performance trends

#### Match Conditions
- Weather impact (Clear/Cloudy/Rain/Snow/Windy)
- Temperature (-10°C ~ 40°C)
- Field condition (Excellent/Good/Fair/Poor)
- Match importance (Regular/Important/Very Important)
- Rest days (0~30 days)

### 3. Prediction Algorithm

Comprehensive analysis based on weighted factors:

- Recent form (25%)
- Player condition (20%)
- Head-to-head record (15%)
- Home advantage (10%)
- Tactical matchup (10%)
- Rest days impact (10%)
- Weather impact (5%)
- Motivation (5%)

## Installation

### 1. Prerequisites
- Python 3.8 or higher

### 2. Install Packages

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
streamlit run app_en.py
```

Opens automatically in browser (default: http://localhost:8501)

## Project Structure

```
.
├── app_en.py                  # Main application (English)
├── requirements.txt           # Required packages
├── modules/
│   ├── __init__.py
│   ├── data_collector.py     # Data collection module
│   ├── predictor.py          # Prediction module
│   └── analyzer.py           # Analysis module
├── data/                     # Data storage (auto-created)
└── models/                   # Model storage (auto-created)
```

## Supported Leagues

### Soccer
- K League 1, K League 2
- EPL (English Premier League)
- La Liga (Spain)
- Bundesliga (Germany)
- Serie A (Italy)
- Champions League

### Baseball
- KBO (Korea)
- MLB (USA)
- NPB (Japan)
- CPBL (Taiwan)

### Basketball
- KBL (Korea)
- NBA (USA)
- EuroLeague

### Volleyball
- V-League Men
- V-League Women

## How to Use

### 1. Match Prediction

1. Select sport and league from sidebar
2. Select home and away teams
3. Enter match conditions (weather, temperature, field condition, etc.)
4. Click "Run Prediction" button
5. Check results:
   - Win/Draw/Loss probabilities
   - Expected score
   - Key influencing factors
   - Prediction confidence

### 2. Team Analysis

1. Select "Team Analysis" tab
2. Choose team to analyze
3. Click "Run Team Analysis"
4. Review results:
   - Recent form chart
   - Strengths/Weaknesses
   - Attack/Defense balance

### 3. Player Analysis

1. Select "Player Analysis" tab
2. Choose team then player
3. Click "Run Player Analysis"
4. Review results:
   - Condition index
   - Recent ratings
   - Injury risk
   - Performance trend

## Data Collection Extension

To collect real data, implement crawling functions in `modules/data_collector.py`:

```python
def scrape_kbo_data(self):
    """KBO data crawling"""
    url = "https://www.koreabaseball.com/..."
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Add parsing logic
```

### Recommended Data Sources

- K League: https://www.kleague.com/
- KBO: https://www.koreabaseball.com/
- FootyStats: https://footystats.org/ (CSV download)
- Public Data Portal: https://www.data.go.kr/

## Important Notes

⚠️ This system is a personal analysis tool.

- Predictions are for reference only and not 100% accurate
- Sports matches have many unpredictable variables
- Users are responsible for their own investment decisions
- Commercial use prohibited
- Distribution prohibited

## Improvement Directions

1. Implement real data crawling
2. Train machine learning models (after accumulating historical data)
3. Add more leagues
4. Real-time data updates
5. Automatic injury list collection
6. Add manager tactical analysis

## License

Personal project - Non-commercial use only

## Contact

Personal project - No support provided

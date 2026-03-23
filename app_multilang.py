"""
다국어 지원 스포츠 경기 예측 시스템
지원 언어: 한국어, 영어, 일본어, 중국어(간체), 스페인어
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from modules.data_collector import DataCollector
from modules.predictor import MatchPredictor
from modules.analyzer import PerformanceAnalyzer
from modules.score_predictor import get_score_predictor
from modules.injury_fetcher import InjuryFetcher
from modules.coaching_staff_fetcher import CoachingStaffFetcher
from modules.translator import get_translator

# 세션 상태 초기화
if 'language' not in st.session_state:
    st.session_state.language = 'ko'  # 기본 언어: 한국어

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.collector_cache = {}

# 번역기 초기화
translator = get_translator(st.session_state.language)
t = translator.get

# 페이지 설정
st.set_page_config(
    page_title="VIBE BOX Sports MatchSignal",
    page_icon="📡",
    layout="wide"
)

# 제목
st.title(t('app_title'))
st.caption(t('app_caption'))

# 커피 후원 버튼 (오른쪽 상단)
col_title, col_coffee = st.columns([4, 1])
with col_coffee:
    # 후원 버튼 클릭 상태 관리
    if 'show_qr' not in st.session_state:
        st.session_state.show_qr = False
    
    # 커스텀 버튼 스타일
    st.markdown("""
    <style>
    /* 커피 후원 버튼만 노란색 - 특정 컨테이너 내부 */
    [data-testid="column"]:last-child div.stButton > button:first-child {
        background-color: #FFDD00 !important;
        color: #000000 !important;
        font-weight: bold;
        border: 2px solid #000000 !important;
    }
    [data-testid="column"]:last-child div.stButton > button:first-child:hover {
        background-color: #FFE84D !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 노란색 버튼
    if st.button(t('support_coffee'), key="coffee_support"):
        st.session_state.show_qr = not st.session_state.show_qr
    
    st.caption(t('support_message'))
    
    # QR 코드 표시
    if st.session_state.show_qr:
        try:
            import qrcode
            from io import BytesIO
            import base64
            
            # QR 코드 생성
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data('https://qr.kakaopay.com/FHucxWATA')
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 이미지를 base64로 변환
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-top: 10px;'>
                <h4 style='color: #333;'>☕ {t('support_coffee')}</h4>
                <p style='color: #666; font-size: 14px;'>{t('support_message')}</p>
                <img src='data:image/png;base64,{img_str}' style='width: 200px; height: 200px; margin: 10px 0;'>
                <br>
                <a href='https://qr.kakaopay.com/FHucxWATA' target='_blank' style='
                    display: inline-block;
                    background-color: #FEE500;
                    color: #000000;
                    padding: 12px 24px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    margin: 10px 0;
                '>
                    📱 KakaoPay Support
                </a>
                <p style='color: #999; font-size: 12px; margin-top: 10px;'>
                    Click the button above on mobile
                </p>
            </div>
            """, unsafe_allow_html=True)
        except ImportError:
            # qrcode 라이브러리가 없는 경우
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-top: 10px;'>
                <h4 style='color: #333;'>☕ {t('support_coffee')}</h4>
                <p style='color: #666; font-size: 14px;'>{t('support_message')}</p>
                <a href='https://qr.kakaopay.com/FHucxWATA' target='_blank' style='
                    display: inline-block;
                    background-color: #FEE500;
                    color: #000000;
                    padding: 12px 24px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    margin: 10px 0;
                '>
                    📱 KakaoPay Support
                </a>
                <p style='color: #999; font-size: 12px; margin-top: 10px;'>
                    Click the button above on mobile
                </p>
            </div>
            """, unsafe_allow_html=True)

# 실시간 데이터 안내
col1, col2 = st.columns([3, 1])
with col1:
    st.info(t('realtime_data_notice'))
with col2:
    if st.button(t('info_button')):
        st.info("""
        **Real-time Data Sources:**
        - Player Stats: ESPN API
        - Match Schedule: ESPN API
        - Updates: Auto-refresh every hour
        """)

# 사이드바 - 언어 선택
st.sidebar.header(t('language'))
available_languages = translator.get_available_languages()
selected_language = st.sidebar.selectbox(
    t('language'),
    options=list(available_languages.keys()),
    format_func=lambda x: available_languages[x],
    index=list(available_languages.keys()).index(st.session_state.language)
)

# 언어 변경 시 페이지 새로고침
if selected_language != st.session_state.language:
    st.session_state.language = selected_language
    st.rerun()

# 데이터 새로고침 버튼
if st.sidebar.button(t('refresh_data')):
    st.session_state.collector_cache = {}
    try:
        from modules.player_stats_fetcher import refresh_player_cache
        from modules.schedule_fetcher import get_schedule_fetcher
        refresh_player_cache()
        fetcher = get_schedule_fetcher()
        fetcher.cache = {}
        st.sidebar.success(t('cache_cleared'))
    except Exception as e:
        st.sidebar.warning(f"⚠️ {e}")
    st.rerun()

# 사이드바 광고 공간 1
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0;'>
    <h4 style='color: white; margin: 0; font-size: 14px;'>📢 {t('ad_space')}</h4>
    <p style='color: white; margin: 5px 0; font-size: 11px;'>{t('sponsor_message')}</p>
    <p style='color: #e0e0e0; font-size: 10px;'>300 x 250 px</p>
</div>
""", unsafe_allow_html=True)

# 리그 선택
leagues = {
    t('soccer'): ["EPL", "La Liga", "Bundesliga", "Serie A", "K리그1"],
    t('baseball'): ["MLB", "KBO"],
    t('basketball'): ["NBA", "KBL"],
    t('volleyball'): ["V-리그 남자", "V-리그 여자"]
}

sport = st.sidebar.selectbox(t('sport'), list(leagues.keys()))
league = st.sidebar.selectbox(t('league'), leagues[sport])

# 사이드바 광고 공간 2
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
            padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0;'>
    <h4 style='color: white; margin: 0; font-size: 14px;'>📢 {t('ad_space')}</h4>
    <p style='color: white; margin: 5px 0; font-size: 11px;'>{t('sponsor_message')}</p>
    <p style='color: #e0e0e0; font-size: 10px;'>300 x 250 px</p>
</div>
""", unsafe_allow_html=True)

# NBA 컨퍼런스 필터
nba_conference = None
if league == "NBA":
    nba_conference = st.sidebar.radio(
        "Conference",
        ["All", "East", "West"],
        horizontal=True
    )

# 데이터 수집기 초기화
if league == "NBA":
    collector_key_east = f"{sport}_NBA East"
    collector_key_west = f"{sport}_NBA West"
    
    if collector_key_east not in st.session_state.collector_cache:
        st.session_state.collector_cache[collector_key_east] = DataCollector(sport, "NBA East")
    
    if collector_key_west not in st.session_state.collector_cache:
        st.session_state.collector_cache[collector_key_west] = DataCollector(sport, "NBA West")
    
    collector_east = st.session_state.collector_cache[collector_key_east]
    collector_west = st.session_state.collector_cache[collector_key_west]
    collector = collector_east
else:
    collector_key = f"{sport}_{league}"
    if collector_key not in st.session_state.collector_cache:
        st.session_state.collector_cache[collector_key] = DataCollector(sport, league)
    
    collector = st.session_state.collector_cache[collector_key]

analyzer = PerformanceAnalyzer()
predictor = MatchPredictor()
score_predictor = get_score_predictor()

# NBA 팀 목록 통합 함수
def get_all_teams():
    if league == "NBA":
        teams_east = collector_east.get_teams()
        teams_west = collector_west.get_teams()
        all_teams = teams_east + teams_west
        
        if nba_conference == "East":
            return teams_east
        elif nba_conference == "West":
            return teams_west
        else:
            return all_teams
    else:
        return collector.get_teams()

def get_team_data_nba(team_name):
    if league == "NBA":
        if team_name in collector_east.get_teams():
            return collector_east.get_team_data(team_name)
        elif team_name in collector_west.get_teams():
            return collector_west.get_team_data(team_name)
    return collector.get_team_data(team_name)

def get_players_nba(team_name):
    if league == "NBA":
        if team_name in collector_east.get_teams():
            return collector_east.get_players(team_name)
        elif team_name in collector_west.get_teams():
            return collector_west.get_players(team_name)
    return collector.get_players(team_name)

def get_player_data_nba(player_name, team_name):
    if league == "NBA":
        if team_name in collector_east.get_teams():
            return collector_east.get_player_data(player_name, team_name)
        elif team_name in collector_west.get_teams():
            return collector_west.get_player_data(player_name, team_name)
    return collector.get_player_data(player_name, team_name)

# 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    t('tab_match_prediction'),
    t('tab_team_analysis'),
    t('tab_player_analysis'),
    t('tab_schedule'),
    t('tab_injury_report'),
    t('tab_coaching_staff'),
    t('tab_settings')
])

# 탭 1: 경기 예측
with tab1:
    st.header(t('tab_match_prediction'))
    
    # 광고 공간 1 (상단)
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h3 style='color: white; margin: 0;'>📢 {t('ad_space')} 1</h3>
            <p style='color: white; margin: 10px 0;'>{t('sponsor_message')}</p>
            <p style='color: #e0e0e0; font-size: 12px;'>728 x 90 px</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t('home_team'))
        home_team = st.selectbox(t('team_select'), get_all_teams(), key="home")
        home_data = get_team_data_nba(home_team)
        
        if home_data:
            if home_data.get('real_data'):
                st.success(t('real_data'))
                if 'position' in home_data:
                    st.metric(t('league_rank'), f"{home_data['position']}")
                if 'points' in home_data:
                    st.metric(t('points'), f"{home_data['points']}")
            else:
                st.warning(t('simulated_data'))
            
            st.metric(t('recent_winrate'), f"{home_data.get('recent_winrate', 0):.1%}")
            st.metric(t('home_winrate'), f"{home_data.get('home_winrate', 0):.1%}")
            st.metric(t('avg_goals'), f"{home_data.get('avg_goals', 0):.2f}")
    
    with col2:
        st.subheader(t('away_team'))
        away_team = st.selectbox(t('team_select'), get_all_teams(), key="away")
        away_data = get_team_data_nba(away_team)
        
        if away_data:
            if away_data.get('real_data'):
                st.success(t('real_data'))
                if 'position' in away_data:
                    st.metric(t('league_rank'), f"{away_data['position']}")
                if 'points' in away_data:
                    st.metric(t('points'), f"{away_data['points']}")
            else:
                st.warning(t('simulated_data'))
            
            st.metric(t('recent_winrate'), f"{away_data.get('recent_winrate', 0):.1%}")
            st.metric(t('away_winrate'), f"{away_data.get('away_winrate', 0):.1%}")
            st.metric(t('avg_goals'), f"{away_data.get('avg_goals', 0):.2f}")
    
    # 경기 조건
    st.subheader(t('match_conditions'))
    col3, col4, col5 = st.columns(3)
    
    with col3:
        weather_options = {
            t('sunny'): '맑음',
            t('cloudy'): '흐림',
            t('rainy'): '비',
            t('snowy'): '눈',
            t('windy'): '강풍'
        }
        weather_display = st.selectbox(t('weather'), list(weather_options.keys()))
        weather = weather_options[weather_display]
        temperature = st.slider(t('temperature'), -10, 40, 20)
    
    with col4:
        field_options = {
            t('excellent'): '최상',
            t('good'): '양호',
            t('average'): '보통',
            t('poor'): '불량'
        }
        field_display = st.selectbox(t('field_condition'), list(field_options.keys()))
        field_condition = field_options[field_display]
        
        importance_options = {
            t('normal'): '일반',
            t('important'): '중요',
            t('very_important'): '매우중요'
        }
        importance_display = st.selectbox(t('match_importance'), list(importance_options.keys()))
        match_importance = importance_options[importance_display]
    
    with col5:
        rest_days_home = st.number_input(f"{t('home_team')} {t('rest_days')}", 0, 30, 3)
        rest_days_away = st.number_input(f"{t('away_team')} {t('rest_days')}", 0, 30, 3)
    
    # 광고 공간 2 (중간)
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;'>
            <h3 style='color: white; margin: 0;'>📢 {t('ad_space')} 2</h3>
            <p style='color: white; margin: 10px 0;'>{t('sponsor_message')}</p>
            <p style='color: #e0e0e0; font-size: 12px;'>728 x 90 px</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button(t('run_prediction'), type="primary", use_container_width=True):
        with st.spinner(t('loading')):
            # 부상 정보 수집
            injury_data = None
            injury_league_map = {
                "NBA": "NBA", "MLB": "MLB", "KBO": "KBO",
                "EPL": "EPL", "La Liga": "La Liga",
                "Bundesliga": "Bundesliga", "Serie A": "Serie A"
            }
            
            injury_league = injury_league_map.get(league, None)
            
            if injury_league:
                try:
                    injury_fetcher = InjuryFetcher(league=injury_league)
                    home_injuries = injury_fetcher.get_team_injuries(home_team)
                    away_injuries = injury_fetcher.get_team_injuries(away_team)
                    
                    injury_data = {
                        'home': home_injuries,
                        'away': away_injuries
                    }
                    
                    if home_injuries or away_injuries:
                        st.info(t('injury_info'))
                        
                        col_inj1, col_inj2 = st.columns(2)
                        
                        with col_inj1:
                            if home_injuries:
                                st.warning(f"**{home_team}** {t('injured_players')}: {len(home_injuries)}")
                                for inj in home_injuries[:3]:
                                    st.caption(f"• {inj['player']} ({inj['position']}): {inj['status']}")
                        
                        with col_inj2:
                            if away_injuries:
                                st.warning(f"**{away_team}** {t('injured_players')}: {len(away_injuries)}")
                                for inj in away_injuries[:3]:
                                    st.caption(f"• {inj['player']} ({inj['position']}): {inj['status']}")
                except Exception as e:
                    pass
            
            # 예측 실행
            prediction = predictor.predict_match(
                home_team=home_team,
                away_team=away_team,
                home_data=home_data,
                away_data=away_data,
                weather=weather,
                temperature=temperature,
                field_condition=field_condition,
                match_importance=match_importance,
                rest_days_home=rest_days_home,
                rest_days_away=rest_days_away,
                injury_data=injury_data
            )
            
            # 결과 표시
            st.success(t('prediction_complete'))
            
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                st.metric(
                    t('home_win_prob'),
                    f"{prediction['home_win_prob']:.1%}",
                    delta=f"{prediction['home_win_prob'] - 0.33:.1%}"
                )
            
            with col_r2:
                st.metric(
                    t('draw_prob'),
                    f"{prediction['draw_prob']:.1%}",
                    delta=f"{prediction['draw_prob'] - 0.33:.1%}"
                )
            
            with col_r3:
                st.metric(
                    t('away_win_prob'),
                    f"{prediction['away_win_prob']:.1%}",
                    delta=f"{prediction['away_win_prob'] - 0.33:.1%}"
                )
            
            # 예상 스코어
            st.subheader(t('expected_score'))
            st.write(f"**{home_team} {prediction['expected_score_home']:.1f} - {prediction['expected_score_away']:.1f} {away_team}**")
            
            # 신뢰도
            st.subheader(t('confidence'))
            confidence = prediction['confidence']
            st.progress(confidence)
            st.write(f"{t('confidence')}: {confidence:.1%}")
            
            # 광고 공간 3 (하단)
            with st.container():
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;'>
                    <h3 style='color: white; margin: 0;'>📢 {t('ad_space')} 3</h3>
                    <p style='color: white; margin: 10px 0;'>{t('sponsor_message')}</p>
                    <p style='color: #e0e0e0; font-size: 12px;'>728 x 90 px</p>
                </div>
                """, unsafe_allow_html=True)

# 탭 2: 팀 분석
with tab2:
    st.header(t('team_analysis_title'))
    
    # 광고 공간 4 (상단)
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h3 style='color: white; margin: 0;'>📢 {t('ad_space')} 4</h3>
            <p style='color: white; margin: 10px 0;'>{t('sponsor_message')}</p>
            <p style='color: #e0e0e0; font-size: 12px;'>728 x 90 px</p>
        </div>
        """, unsafe_allow_html=True)
    
    selected_team = st.selectbox(t('select_team'), get_all_teams(), key="team_analysis")
    
    if st.button(t('run_team_analysis')):
        team_analysis = analyzer.analyze_team(selected_team, collector)
        
        # 코칭스태프 정보 추가
        coaching_league_map = {
            "NBA": "NBA",
            "MLB": "MLB",
            "KBO": "KBO",
            "EPL": "EPL",
            "La Liga": "La Liga",
            "Bundesliga": "Bundesliga",
            "Serie A": "Serie A"
        }
        coaching_league = coaching_league_map.get(league, None)
        
        if coaching_league:
            try:
                coaching_fetcher = CoachingStaffFetcher(league=coaching_league)
                team_staff = coaching_fetcher.fetch_team_coaching_staff(selected_team)
                
                if team_staff and team_staff.get('head_coach') != 'Unknown':
                    st.subheader(t('tab_coaching_staff'))
                    
                    col_coach1, col_coach2 = st.columns(2)
                    
                    with col_coach1:
                        st.info(f"**{t('head_coach')}:** {team_staff['head_coach']}")
                    
                    with col_coach2:
                        st.info(f"**{t('coaching_staff_count')}:** {len(team_staff['assistant_coaches'])}{t('players')}")
                    
                    with st.expander(t('coaching_details')):
                        for i, coach in enumerate(team_staff['assistant_coaches'], 1):
                            st.write(f"{i}. {coach}")
            except Exception as e:
                st.caption(f"{t('error_occurred')}: {e}")
        
        # 최근 폼
        st.subheader(f"📊 {t('recent_form')}")
        st.line_chart(team_analysis['form_chart'])
        
        # 강점/약점
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.subheader(f"💪 {t('strengths')}")
            for strength in team_analysis['strengths']:
                st.success(strength)
        
        with col_t2:
            st.subheader(f"⚠️ {t('weaknesses')}")
            for weakness in team_analysis['weaknesses']:
                st.warning(weakness)

# 탭 3: 선수 분석
with tab3:
    st.header(t('player_analysis'))
    
    # 광고 공간 5 (상단)
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h3 style='color: white; margin: 0;'>📢 {t('ad_space')} 5</h3>
            <p style='color: white; margin: 10px 0;'>{t('sponsor_message')}</p>
            <p style='color: #e0e0e0; font-size: 12px;'>728 x 90 px</p>
        </div>
        """, unsafe_allow_html=True)
    
    col_team, col_refresh = st.columns([4, 1])
    
    with col_team:
        team_for_players = st.selectbox(t('team_select'), get_all_teams(), key="player_team")
    
    with col_refresh:
        st.write("")
        if st.button(t('refresh_roster'), key="refresh_roster"):
            if league == "NBA":
                if team_for_players in collector_east.get_teams():
                    collector_east.clear_cache()
                elif team_for_players in collector_west.get_teams():
                    collector_west.clear_cache()
            else:
                collector.clear_cache()
            st.success(t('roster_cache_cleared'))
            st.rerun()
    
    players = get_players_nba(team_for_players)
    selected_player = st.selectbox(t('select_player'), players)
    
    if st.button(t('run_analysis')):
        player_data = get_player_data_nba(selected_player, team_for_players)
        
        if player_data.get('real_data'):
            st.success(t('real_data'))
            
            st.subheader(f"📊 {player_data['name']} - {player_data['position']}")
            
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            
            with col_p1:
                st.metric(t('age'), f"{player_data['age']}")
                st.metric(t('matches_played'), player_data['matches_played'])
            
            with col_p2:
                if 'ppg' in player_data:
                    st.metric("PPG", f"{player_data['ppg']:.1f}")
                    st.metric("RPG", f"{player_data.get('rpg', 0):.1f}")
                else:
                    st.metric(t('goals'), player_data['goals'])
                    st.metric(t('assists'), player_data['assists'])
            
            with col_p3:
                st.metric(t('rating'), f"{player_data['rating_avg']:.2f}/10")
                st.metric(t('condition'), f"{player_data['condition']:.1f}/100")
            
            with col_p4:
                st.metric(t('injury_status'), player_data['injury_status'])
                st.metric(t('fatigue'), f"{player_data['fatigue_level']:.1f}/100")
        else:
            st.warning(t('simulated_data'))

# 탭 4: 경기 일정
with tab4:
    st.header(t('schedule_title'))
    
    # 광고 공간 6 (상단)
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h3 style='color: #333; margin: 0;'>📢 {t('ad_space')} 6</h3>
            <p style='color: #555; margin: 10px 0;'>{t('sponsor_message')}</p>
            <p style='color: #777; font-size: 12px;'>728 x 90 px</p>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        from modules.schedule_fetcher import (
            get_upcoming_matches, 
            get_team_next_matches, 
            get_all_upcoming_matches
        )
        
        st.info(f"📡 {t('realtime_data_notice')}")
        
        # 일정 보기 모드 선택
        schedule_mode = st.radio(
            t('schedule_mode'),
            [t('all_schedules'), t('league_schedule'), t('team_schedule')],
            horizontal=True
        )
        
        if schedule_mode == t('all_schedules'):
            st.subheader(f"🌍 {t('all_leagues_upcoming')}")
            
            with st.spinner(f"{t('fetching_data')}..."):
                all_matches = get_all_upcoming_matches()
            
            for league_name, matches in all_matches.items():
                if matches:
                    with st.expander(f"⚽ {league_name} ({len(matches)}{t('matches')})", expanded=True):
                        for match in matches[:10]:
                            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                            
                            with col1:
                                st.write(f"**{match['date']}**")
                                st.caption(match['time'])
                            
                            with col2:
                                st.write(f"🏠 **{match['home']}** vs 🛫 **{match['away']}**")
                            
                            with col3:
                                st.caption(f"📍 {match['venue']}")
                            
                            with col4:
                                st.caption(f"📺 {match['tv']}")
                            
                            st.divider()
        
        elif schedule_mode == t('league_schedule'):
            st.subheader(f"🏆 {t('league_schedule')}")
            
            league_map = {
                "EPL": "EPL",
                "La Liga": "La Liga",
                "Bundesliga": "Bundesliga",
                "Serie A": "Serie A",
                "NBA East": "NBA",
                "NBA West": "NBA"
            }
            
            schedule_league = league_map.get(league, league)
            
            with st.spinner(f"{t('fetching_data')}..."):
                matches = get_upcoming_matches(schedule_league, days=7)
            
            if matches:
                st.info(f"📊 {schedule_league} - {t('upcoming_matches')} {len(matches)}{t('matches')}")
                
                matches_by_date = {}
                for match in matches:
                    date = match['date']
                    if date not in matches_by_date:
                        matches_by_date[date] = []
                    matches_by_date[date].append(match)
                
                for date, day_matches in sorted(matches_by_date.items()):
                    st.subheader(f"📅 {date}")
                    
                    for match in day_matches:
                        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                        
                        with col1:
                            st.write(f"**{match['time']}**")
                        
                        with col2:
                            st.write(f"🏠 **{match['home']}** vs 🛫 **{match['away']}**")
                        
                        with col3:
                            st.caption(f"📍 {match['venue']}")
                        
                        with col4:
                            st.caption(f"📺 {match['tv']}")
                        
                        st.divider()
            else:
                st.warning(f"⚠️ {t('no_data_available')}")
        
        elif schedule_mode == t('team_schedule'):
            st.subheader(f"👥 {t('next_matches')}")
            
            schedule_team = st.selectbox(t('team_select'), get_all_teams(), key="schedule_team")
            
            league_map = {
                "EPL": "EPL",
                "La Liga": "La Liga",
                "Bundesliga": "Bundesliga",
                "Serie A": "Serie A",
                "NBA East": "NBA",
                "NBA West": "NBA"
            }
            
            schedule_league = league_map.get(league, league)
            
            with st.spinner(f"{t('fetching_data')}..."):
                team_matches = get_team_next_matches(schedule_league, schedule_team, limit=5)
            
            if team_matches:
                st.success(f"✅ {schedule_team} {t('next_matches')} {len(team_matches)}{t('matches')}")
                
                for idx, match in enumerate(team_matches, 1):
                    with st.container():
                        st.subheader(f"{t('matches')} {idx}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**{t('match_date')}:** {match['date']}")
                            st.write(f"**{t('match_time')}:** {match['time']}")
                            st.write(f"**{t('venue')}:** {match['venue']}")
                            st.write(f"**{t('tv_broadcast')}:** {match['tv']}")
                        
                        with col2:
                            if schedule_team.lower() in match['home'].lower():
                                st.info(f"🏠 **{t('home_match')}**")
                                st.write(f"**{t('opponent')}:** {match['away']}")
                            else:
                                st.warning(f"🛫 **{t('away_match')}**")
                                st.write(f"**{t('opponent')}:** {match['home']}")
                        
                        if st.button(f"🎯 {t('predict_score')}", key=f"predict_{idx}"):
                            try:
                                home_data = get_team_data_nba(match['home'])
                                away_data = get_team_data_nba(match['away'])
                                
                                if home_data and away_data:
                                    score_pred = score_predictor.predict_match_score(
                                        league=schedule_league,
                                        home_team=match['home'],
                                        away_team=match['away'],
                                        home_data=home_data,
                                        away_data=away_data
                                    )
                                    
                                    st.success(f"**{t('expected_score')}: {match['home']} {score_pred['home_score']} - {score_pred['away_score']} {match['away']}**")
                                    st.write(f"{t('win_rate')}: {match['home']} {score_pred['home_win_probability']}% vs {match['away']} {score_pred['away_win_probability']}%")
                                    if 'draw_probability' in score_pred:
                                        st.write(f"{t('draw')}: {score_pred['draw_probability']}%")
                                    st.caption(f"{t('confidence')}: {score_pred['confidence']}")
                                else:
                                    st.warning(f"⚠️ {t('no_data_available')}")
                            except Exception as e:
                                st.error(f"{t('error_occurred')}: {str(e)}")
                        
                        st.divider()
            else:
                st.warning(f"⚠️ {t('no_data_available')}")
    
    except ImportError as e:
        st.error(f"❌ {t('error_occurred')}: {e}")
    except Exception as e:
        st.error(f"❌ {t('error_occurred')}: {str(e)}")

# 탭 5: 부상 리포트
with tab5:
    st.header(t('injury_report_title'))
    
    # 광고 공간 7 (상단)
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h3 style='color: #333; margin: 0;'>📢 {t('ad_space')} 7</h3>
            <p style='color: #555; margin: 10px 0;'>{t('sponsor_message')}</p>
            <p style='color: #777; font-size: 12px;'>728 x 90 px</p>
        </div>
        """, unsafe_allow_html=True)
    
    injury_league_map = {
        "NBA": "NBA",
        "MLB": "MLB",
        "KBO": "KBO",
        "EPL": "EPL",
        "La Liga": "La Liga",
        "Bundesliga": "Bundesliga",
        "Serie A": "Serie A"
    }
    
    injury_league = injury_league_map.get(league, None)
    
    if not injury_league:
        st.warning(f"⚠️ {t('injury_report_title')} {', '.join(injury_league_map.keys())}")
    else:
        injury_fetcher = InjuryFetcher(league=injury_league)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if injury_league in ["NBA", "MLB"]:
                st.info(f"📡 {t('realtime_injury_info')} - ESPN Injury Report")
            else:
                st.info(f"📊 {t('injury_info')}")
        
        with col2:
            if st.button(f"🔄 {t('refresh_data')}"):
                st.rerun()
        
        try:
            summary = injury_fetcher.get_injury_summary()
            
            st.subheader(f"📊 {t('injury_summary')}")
            
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            
            with col_s1:
                st.metric(t('total_injured'), f"{summary['total_injured_players']}{t('players')}")
            
            with col_s2:
                st.metric(t('out'), f"{summary['out']}{t('players')}", delta=None, delta_color="inverse")
            
            with col_s3:
                st.metric(t('day_to_day'), f"{summary['day_to_day']}{t('players')}")
            
            with col_s4:
                st.metric(t('questionable'), f"{summary['questionable']}{t('players')}")
            
            st.caption(f"{t('last_updated')}: {summary['last_updated']}")
            
            st.subheader(f"{'🏀' if injury_league == 'NBA' else '⚾' if injury_league in ['MLB', 'KBO'] else '⚽'} {t('team_injuries')}")
            
            selected_team = st.selectbox(
                t('team_select'),
                [t('all_teams')] + get_all_teams(),
                key="injury_team_select"
            )
            
            all_injuries = injury_fetcher.fetch_all_injuries()
            
            if selected_team == t('all_teams'):
                for team_name, injuries in all_injuries.items():
                    if injuries:
                        with st.expander(f"**{team_name}** ({len(injuries)}{t('players')})", expanded=False):
                            for injury in injuries:
                                status_color = {
                                    'out': '🔴',
                                    'day-to-day': '🟡',
                                    'questionable': '🟠',
                                    'doubtful': '🟠'
                                }
                                
                                status_lower = injury['status'].lower()
                                icon = '🔴'
                                for key, value in status_color.items():
                                    if key in status_lower:
                                        icon = value
                                        break
                                
                                st.write(f"{icon} **{injury['player']}** ({injury['position']})")
                                st.write(f"   {t('injury_status')}: {injury['status']}")
                                st.write(f"   {t('injury_description')}: {injury['description']}")
                                st.write(f"   {t('expected_return')}: {injury['date']}")
                                st.divider()
            else:
                team_injuries = injury_fetcher.get_team_injuries(selected_team)
                
                if team_injuries:
                    st.write(f"**{selected_team}** {t('injured_players')}: {len(team_injuries)}{t('players')}")
                    
                    for injury in team_injuries:
                        status_color = {
                            'out': '🔴',
                            'day-to-day': '🟡',
                            'questionable': '🟠',
                            'doubtful': '🟠'
                        }
                        
                        status_lower = injury['status'].lower()
                        icon = '🔴'
                        for key, value in status_color.items():
                            if key in status_lower:
                                icon = value
                                break
                        
                        col_inj1, col_inj2 = st.columns([1, 3])
                        
                        with col_inj1:
                            st.write(f"### {icon}")
                            st.write(f"**{injury['player']}**")
                            st.write(f"{injury['position']}")
                        
                        with col_inj2:
                            st.write(f"**{t('injury_status')}:** {injury['status']}")
                            st.write(f"**{t('injury_description')}:** {injury['description']}")
                            st.write(f"**{t('expected_return')}:** {injury['date']}")
                        
                        st.divider()
                else:
                    st.success(f"✅ {selected_team} {t('no_injuries')}!")
            
            st.subheader(f"🔍 {t('player_search')}")
            
            player_search = st.text_input(t('player_name_input'), placeholder=f"{'LeBron James' if injury_league == 'NBA' else 'Shohei Ohtani' if injury_league == 'MLB' else '양현종' if injury_league == 'KBO' else 'Kevin De Bruyne'}")
            
            if player_search:
                player_injury = injury_fetcher.get_player_status(player_search)
                
                if player_injury:
                    st.warning(f"⚠️ {player_search} {t('player_injured')}")
                    
                    col_p1, col_p2 = st.columns(2)
                    
                    with col_p1:
                        st.write(f"**{t('position')}:** {player_injury['position']}")
                        st.write(f"**{t('injury_status')}:** {player_injury['status']}")
                    
                    with col_p2:
                        st.write(f"**{t('injury_description')}:** {player_injury['description']}")
                        st.write(f"**{t('expected_return')}:** {player_injury['date']}")
                else:
                    st.success(f"✅ {player_search} {t('player_healthy')}!")
            
        except Exception as e:
            st.error(f"❌ {t('error_occurred')}: {e}")

# 탭 6: 코칭스태프
with tab6:
    st.header(t('coaching_staff_title'))
    
    # 광고 공간 8 (상단)
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h3 style='color: #333; margin: 0;'>📢 {t('ad_space')} 8</h3>
            <p style='color: #555; margin: 10px 0;'>{t('sponsor_message')}</p>
            <p style='color: #777; font-size: 12px;'>728 x 90 px</p>
        </div>
        """, unsafe_allow_html=True)
    
    coaching_league_map = {
        "NBA": "NBA",
        "MLB": "MLB",
        "KBO": "KBO",
        "EPL": "EPL",
        "La Liga": "La Liga",
        "Bundesliga": "Bundesliga",
        "Serie A": "Serie A"
    }
    
    coaching_league = coaching_league_map.get(league, None)
    
    if not coaching_league:
        st.warning(f"⚠️ {t('coaching_staff_title')} {', '.join(coaching_league_map.keys())}")
    else:
        coaching_fetcher = CoachingStaffFetcher(league=coaching_league)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"📊 {t('coaching_info')}")
        
        with col2:
            if st.button(f"🔄 {t('refresh_data')}", key="coaching_refresh"):
                st.rerun()
        
        with st.spinner(f"{t('fetching_data')}..."):
            try:
                summary = coaching_fetcher.get_coaching_summary()
                
                st.subheader(f"📊 {t('coaching_summary')}")
                
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    st.metric(t('total_teams'), f"{summary['total_teams']}{t('teams')}")
                
                with col_s2:
                    st.metric(t('total_coaches'), f"{summary['total_coaches']}{t('players')}")
                
                with col_s3:
                    st.metric(t('avg_coaches'), f"{summary['avg_coaches_per_team']:.1f}{t('players')}")
                
                st.caption(f"{t('last_updated')}: {summary['last_updated']}")
                
                st.subheader(f"{'🏀' if coaching_league == 'NBA' else '⚾' if coaching_league in ['MLB', 'KBO'] else '⚽'} {t('coaching_staff_title')}")
                
                selected_team = st.selectbox(
                    t('team_select'),
                    [t('all_teams')] + get_all_teams(),
                    key="coaching_team_select"
                )
                
                all_coaching = coaching_fetcher.fetch_all_coaching_staff()
                
                if selected_team == t('all_teams'):
                    for team_name, staff in all_coaching.items():
                        with st.expander(f"**{team_name}**", expanded=False):
                            col_c1, col_c2 = st.columns([1, 2])
                            
                            with col_c1:
                                st.write(f"### 👨‍💼 {t('head_coach')}")
                                st.write(f"**{staff['head_coach']}**")
                            
                            with col_c2:
                                st.write(f"### 👥 {t('assistant_coaches')}")
                                for i, coach in enumerate(staff['assistant_coaches'], 1):
                                    st.write(f"{i}. {coach}")
                            
                            st.caption(f"{t('last_updated')}: {staff['last_updated']}")
                else:
                    team_staff = coaching_fetcher.fetch_team_coaching_staff(selected_team)
                    
                    if team_staff and team_staff.get('head_coach') != 'Unknown':
                        st.write(f"## {selected_team}")
                        
                        col_t1, col_t2 = st.columns(2)
                        
                        with col_t1:
                            st.subheader(f"👨‍💼 {t('head_coach')}")
                            st.markdown(f"""
                            <div style='text-align: center; padding: 30px; background-color: #f0f2f6; border-radius: 10px;'>
                                <h2 style='color: #1f77b4; margin: 0;'>{team_staff['head_coach']}</h2>
                                <p style='color: #666; margin-top: 10px;'>{t('head_coach')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_t2:
                            st.subheader(f"👥 {t('assistant_coaches')}")
                            st.write(f"**{len(team_staff['assistant_coaches'])}{t('players')}**")
                            
                            for i, coach in enumerate(team_staff['assistant_coaches'], 1):
                                st.write(f"{i}. {coach}")
                        
                        st.divider()
                        st.caption(f"{t('last_updated')}: {team_staff['last_updated']}")
                    else:
                        st.warning(f"⚠️ {t('no_data_available')}")
                
                st.subheader(f"🔍 {t('coach_search')}")
                
                coach_search = st.text_input(t('coach_name_input'), placeholder=f"{'Steve Kerr' if coaching_league == 'NBA' else 'Aaron Boone' if coaching_league == 'MLB' else '김종국' if coaching_league == 'KBO' else 'Pep Guardiola'}")
                
                if coach_search:
                    found_teams = []
                    for team_name, staff in all_coaching.items():
                        if coach_search.lower() in staff['head_coach'].lower():
                            found_teams.append((team_name, staff))
                    
                    if found_teams:
                        st.success(f"✅ {len(found_teams)}{t('teams')} '{coach_search}' {t('coach_found')}")
                        
                        for team_name, staff in found_teams:
                            with st.container():
                                col_f1, col_f2 = st.columns([1, 2])
                                
                                with col_f1:
                                    st.write(f"**{t('team_select')}:** {team_name}")
                                    st.write(f"**{t('head_coach')}:** {staff['head_coach']}")
                                
                                with col_f2:
                                    st.write(f"**{t('assistant_coaches')}:** {', '.join(staff['assistant_coaches'][:3])}")
                                
                                st.divider()
                    else:
                        st.warning(f"⚠️ '{coach_search}' {t('coach_not_found')}")
                
            except Exception as e:
                st.error(f"❌ {t('error_occurred')}: {e}")

# 탭 7: 설정
with tab7:
    st.header(t('tab_settings'))
    
    st.subheader(t('language'))
    st.write(f"**{t('language')}:** {available_languages[st.session_state.language]}")
    
    st.info(f"""
    **{t('supported_languages')}:**
    - 한국어 (Korean)
    - English
    - 日本語 (Japanese)
    - 中文 (Chinese)
    - Español (Spanish)
    """)
    
    st.write("---")
    st.caption("📡 VIBE BOX Sports MatchSignal - Real-time Sports Match Prediction & Analysis Platform")
    st.caption(f"v2.0 - Multilingual Edition | {st.session_state.language.upper()}")

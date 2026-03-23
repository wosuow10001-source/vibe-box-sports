import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="VIBE BOX Sports MatchSignal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from modules.data_collector import DataCollector
from modules.sport_router import SportRouter
from modules.analyzer import PerformanceAnalyzer
from modules.score_predictor import get_score_predictor
from modules.injury_fetcher import InjuryFetcher
from modules.coaching_staff_fetcher import CoachingStaffFetcher

# Streamlit 세션 상태 초기화
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.collector_cache = {}
    print("🔄 앱 초기화 완료")

# 언어 설정 초기화
if 'language' not in st.session_state:
    st.session_state.language = 'ko'

# 번역기 초기화
from modules.translator import get_translator
translator = get_translator(st.session_state.language)
t = translator.get

# 다크 테마 + 네온 옐로우 강조 스타일 (Wellness Website)
st.markdown("""
<style>
    /* Streamlit 상단 헤더 바 - 진한 녹색 */
    header[data-testid="stHeader"] {
        background-color: #1a4d2e !important;
    }
    
    /* 전체 배경 - 다크 그레이 */
    .stApp {
        background: #3a3a3a;
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* 헤더 스타일 - 네온 옐로우 (다크 배경에 대비) */
    h1 {
        color: #CCFF00 !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 0.3rem !important;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: #CCFF00 !important;
        font-weight: 600 !important;
    }
    
    h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* 메인 콘텐츠 영역 텍스트 - 화이트 */
    .main p,
    .main span,
    .main div {
        color: #ffffff !important;
    }
    
    /* 캡션 스타일 */
    .stApp > header + div p {
        color: #CCFF00 !important;
        text-align: center;
        font-size: 1rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* 탭 스타일 - 블랙 배경 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #1a1a1a;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 8px;
        color: #ffffff;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 20px;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2a2a2a;
        color: #CCFF00;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a4d2e !important;
        color: #CCFF00 !important;
    }
    
    /* 카드 스타일 - 다크 박스 */
    .stMetric {
        background: #2a2a2a;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #4a4a4a;
        transition: all 0.2s ease;
    }
    
    .stMetric:hover {
        border-color: #CCFF00;
        box-shadow: 0 4px 12px rgba(204, 255, 0, 0.3);
    }
    
    .stMetric label {
        color: #CCFF00 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.875rem !important;
        font-weight: 700 !important;
    }
    
    /* 버튼 스타일 - 다크 버튼 */
    .stButton > button {
        background: #2a2a2a;
        color: #ffffff;
        border: 2px solid #CCFF00;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(204, 255, 0, 0.2);
    }
    
    .stButton > button:hover {
        background: #CCFF00;
        color: #1a1a1a;
        border: 2px solid #CCFF00;
        box-shadow: 0 4px 12px rgba(204, 255, 0, 0.4);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary 버튼 (예측 실행) - 네온 옐로우 배경에 검정 텍스트 */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: #CCFF00 !important;
        color: #000000 !important;
        border: 2px solid #CCFF00 !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: #b3e600 !important;
        color: #000000 !important;
        border: 2px solid #b3e600 !important;
    }
    
    /* Primary 버튼 텍스트 강제 검정색 */
    .stButton > button[kind="primary"] p,
    .stButton > button[data-testid="baseButton-primary"] p,
    .stButton > button[kind="primary"] span,
    .stButton > button[data-testid="baseButton-primary"] span,
    .stButton > button[kind="primary"] div,
    .stButton > button[data-testid="baseButton-primary"] div {
        color: #000000 !important;
    }
    
    /* 셀렉트박스 스타일 */
    .stSelectbox > div > div {
        background-color: #2a2a2a;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #CCFF00;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
    }
    
    /* 슬라이더 스타일 */
    .stSlider > div > div > div {
        background: #CCFF00;
    }
    
    .stSlider label {
        color: #ffffff !important;
    }
    
    /* 라디오 버튼 스타일 */
    .stRadio > div {
        background-color: #2a2a2a;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #4a4a4a;
    }
    
    .stRadio label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* 라디오 버튼 선택 시 - 어두운 녹색 배경 */
    .stRadio > div[role="radiogroup"] > label > div[data-baseweb="radio"] > div:first-child {
        background-color: #1a4d2e !important;
    }
    
    /* 셀렉트박스 드롭다운 메뉴 배경 - 다크 그레이 */
    .stSelectbox [data-baseweb="popover"] {
        background-color: #2a2a2a !important;
    }
    
    .stSelectbox [data-baseweb="popover"] > div {
        background-color: #2a2a2a !important;
    }
    
    /* 셀렉트박스 드롭다운 리스트 배경 */
    .stSelectbox ul[role="listbox"] {
        background-color: #2a2a2a !important;
    }
    
    /* 셀렉트박스 드롭다운 옵션들 - 다크 배경에 화이트 텍스트 */
    .stSelectbox [role="option"] {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }
    
    .stSelectbox li[role="option"] {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="menu"] li {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="menu"] {
        background-color: #2a2a2a !important;
    }
    
    /* 셀렉트박스 선택된 옵션 - 어두운 녹색 */
    .stSelectbox [data-baseweb="select"] [aria-selected="true"],
    .stSelectbox [role="option"][aria-selected="true"] {
        background-color: #1a4d2e !important;
        color: #CCFF00 !important;
    }
    
    /* 셀렉트박스 드롭다운 옵션 호버 */
    .stSelectbox [data-baseweb="select"] li:hover,
    .stSelectbox [role="option"]:hover {
        background-color: #3a3a3a !important;
        color: #CCFF00 !important;
    }
    
    /* 모든 div 요소 강제 스타일 */
    [data-baseweb="popover"] [data-baseweb="menu"] > ul > li {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }
    
    /* 인포 박스 스타일 */
    .stAlert {
        background: rgba(204, 255, 0, 0.1);
        border: 1px solid rgba(204, 255, 0, 0.3);
        border-radius: 8px;
        color: #ffffff;
    }
    
    /* 성공 메시지 */
    .stSuccess {
        background: rgba(204, 255, 0, 0.15);
        border: 1px solid rgba(204, 255, 0, 0.4);
        color: #CCFF00;
    }
    
    /* 경고 메시지 */
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        color: #ffc107;
    }
    
    /* 에러 메시지 */
    .stError {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid rgba(244, 67, 54, 0.3);
        color: #ff6b6b;
    }
    
    /* 사이드바 스타일 - 블랙 */
    [data-testid="stSidebar"] {
        background: #1a1a1a;
        border-right: 1px solid #2a2a2a;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #CCFF00 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* 구분선 */
    hr {
        border-color: #4a4a4a !important;
        margin: 1.5rem 0 !important;
    }
    
    /* 텍스트 입력 */
    .stTextInput > div > div > input {
        background-color: #2a2a2a;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #CCFF00;
        box-shadow: 0 0 0 1px #CCFF00;
    }
    
    .stTextInput label {
        color: #ffffff !important;
    }
    
    /* 넘버 입력 - 다크 배경 */
    .stNumberInput > div > div > input {
        background-color: #2a2a2a;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        color: #ffffff;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #CCFF00;
        box-shadow: 0 0 0 1px #CCFF00;
    }
    
    .stNumberInput label {
        color: #ffffff !important;
    }
    
    /* 익스팬더 */
    .streamlit-expanderHeader {
        background-color: #2a2a2a;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #3a3a3a;
        border-color: #CCFF00;
    }
    
    /* 프로그레스 바 */
    .stProgress > div > div > div {
        background: #CCFF00;
        border-radius: 8px;
    }
    
    /* 데이터프레임 */
    .dataframe {
        background-color: #2a2a2a !important;
        border: 1px solid #4a4a4a !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    /* 차트 배경 */
    .js-plotly-plot {
        background-color: #2a2a2a !important;
        border-radius: 12px !important;
        border: 1px solid #4a4a4a !important;
    }
    
    /* 캡션 텍스트 */
    .stCaption {
        color: #cccccc !important;
    }
    
    /* 스크롤바 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2a2a2a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #CCFF00;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #b3e600;
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.875rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            font-size: 0.875rem;
            padding: 0 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 헤더 및 커피 버튼 (오른쪽 상단)
col_header, col_coffee = st.columns([5, 1])

with col_header:
    st.markdown("""
    <div style='padding: 10px 0;'>
        <h1 style='margin: 0; color: #CCFF00;'>⚡ VIBE BOX Sports MatchSignal</h1>
        <p style='color: #CCFF00; font-size: 0.95rem; margin-top: 5px;'>전문 스포츠 경기 예측 플랫폼</p>
    </div>
    """, unsafe_allow_html=True)

with col_coffee:
    # 후원 버튼 클릭 상태 관리
    if 'show_qr' not in st.session_state:
        st.session_state.show_qr = False
    
    # 커피 후원 버튼 스타일
    st.markdown("""
    <style>
    /* 커피 후원 버튼 - 황금색 배경, 검정 텍스트 */
    div[data-testid="column"]:nth-child(2) .stButton > button {
        background-color: #FFD700 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 8px 16px !important;
        border-radius: 6px !important;
        border: 2px solid #FFD700 !important;
        box-shadow: 0 2px 6px rgba(255, 215, 0, 0.3) !important;
        margin-top: 10px !important;
    }
    div[data-testid="column"]:nth-child(2) .stButton > button:hover {
        background-color: #FFC700 !important;
        color: #000000 !important;
        border: 2px solid #FFC700 !important;
        box-shadow: 0 3px 8px rgba(255, 215, 0, 0.4) !important;
    }
    /* 커피 버튼 텍스트 강제 검정색 */
    div[data-testid="column"]:nth-child(2) .stButton > button p {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 커피 버튼
    if st.button("☕ 커피 한 잔 후원하기", key="coffee_support"):
        st.session_state.show_qr = not st.session_state.show_qr
    
    # 후원 안내 메시지
    st.markdown("""
    <p style='color: #cccccc; font-size: 0.75rem; text-align: center; margin-top: 5px; line-height: 1.4;'>
        후원금은 서비스 개발 및<br>운영 비용으로 사용됩니다 🙏
    </p>
    """, unsafe_allow_html=True)

# QR 코드 모달 표시
if st.session_state.show_qr:
    st.markdown("""
    <div style='background-color: #2a2a2a; padding: 20px; border-radius: 12px; 
                border: 1px solid #CCFF00; margin: 10px 0; text-align: center;'>
        <h4 style='color: #CCFF00; margin: 0 0 10px 0;'>☕ 커피 한 잔 후원하기</h4>
        <p style='color: #ffffff; font-size: 0.875rem; margin-bottom: 15px;'>
            개발자를 응원해주세요!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        # QR 코드 생성
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data('https://qr.kakaopay.com/FHucxWATA')
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 이미지를 base64로 변환
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown(f"""
        <div style='text-align: center; margin: 10px 0;'>
            <img src='data:image/png;base64,{img_str}' 
                 style='width: 150px; height: 150px; border-radius: 8px;'>
            <br><br>
            <a href='https://qr.kakaopay.com/FHucxWATA' target='_blank' 
               style='display: inline-block; background-color: #FEE500; color: #1a1a1a;
                      padding: 10px 20px; border-radius: 6px; text-decoration: none;
                      font-weight: 600; font-size: 0.9rem;'>
                📱 KakaoPay로 후원하기
            </a>
        </div>
        """, unsafe_allow_html=True)
    except ImportError:
        st.markdown("""
        <div style='text-align: center; margin: 10px 0;'>
            <a href='https://qr.kakaopay.com/FHucxWATA' target='_blank' 
               style='display: inline-block; background-color: #FEE500; color: #1a1a1a;
                      padding: 10px 20px; border-radius: 6px; text-decoration: none;
                      font-weight: 600; font-size: 0.9rem;'>
                📱 KakaoPay로 후원하기
            </a>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 실시간 데이터 안내
st.info("📡 " + t('realtime_data_notice'))


# 사이드바 - 언어 선택
st.sidebar.header(t('language_header'))

available_languages = {
    'ko': '한국어 (Korean)',
    'en': 'English',
    'ja': '日本語 (Japanese)',
    'zh': '中文 (Chinese)',
    'es': 'Español (Spanish)'
}

selected_language = st.sidebar.selectbox(
    t('select_language'),
    options=list(available_languages.keys()),
    format_func=lambda x: available_languages[x],
    index=list(available_languages.keys()).index(st.session_state.language)
)

# 언어 변경 시 페이지 새로고침
if selected_language != st.session_state.language:
    st.session_state.language = selected_language
    st.rerun()

st.sidebar.markdown("---")

# 사이드바 - 리그 선택 (2025-26 시즌 진행 중인 리그)
leagues = {
    t('soccer'): ["EPL", "La Liga", "Bundesliga", "Serie A", "K리그1"],
    t('basketball'): ["NBA", "KBL"],
    t('baseball'): ["MLB", "KBO"],
    t('volleyball'): ["V-리그 남자", "V-리그 여자"]
}

st.sidebar.info(t('season_data_info'))

# 캐시 초기화 버튼
if st.sidebar.button(t('refresh_data')):
    st.session_state.collector_cache = {}
    # 실시간 API 캐시도 초기화
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
<div style='background: #2a2a2a; padding: 15px; border-radius: 8px; 
            text-align: center; margin: 10px 0; border: 1px solid #CCFF00;'>
    <h4 style='color: #CCFF00; margin: 0; font-size: 14px; font-weight: 600;'>📢 광고 공간</h4>
    <p style='color: #ffffff; margin: 8px 0; font-size: 11px;'>스폰서를 기다립니다</p>
    <p style='color: #CCFF00; font-size: 10px; margin: 5px 0;'>300 x 250 px</p>
</div>
""", unsafe_allow_html=True)

sport = st.sidebar.selectbox(t('sport'), list(leagues.keys()))
league = st.sidebar.selectbox(t('league'), leagues[sport])

# 사이드바 광고 공간 2
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='background: #2a2a2a; padding: 15px; border-radius: 8px; 
            text-align: center; margin: 10px 0; border: 1px solid #CCFF00;'>
    <h4 style='color: #CCFF00; margin: 0; font-size: 14px; font-weight: 600;'>📢 광고 공간</h4>
    <p style='color: #ffffff; margin: 8px 0; font-size: 11px;'>스폰서를 기다립니다</p>
    <p style='color: #CCFF00; font-size: 10px; margin: 5px 0;'>300 x 250 px</p>
</div>
""", unsafe_allow_html=True)

# NBA 선택 시 컨퍼런스 필터 추가
nba_conference = None
if league == "NBA":
    nba_conference = st.sidebar.radio(
        t('conference_filter'),
        [t('all'), "East", "West"],
        horizontal=True
    )

# 데이터 수집기 초기화 - 매번 새로 생성하여 캐시 문제 방지
# NBA의 경우 East와 West 데이터를 모두 수집
if league == "NBA":
    collector_key_east = f"{sport}_NBA East"
    collector_key_west = f"{sport}_NBA West"
    
    if collector_key_east not in st.session_state.collector_cache:
        st.session_state.collector_cache[collector_key_east] = DataCollector(sport, "NBA East")
        print(f"🆕 새 DataCollector 생성: {collector_key_east}")
    
    if collector_key_west not in st.session_state.collector_cache:
        st.session_state.collector_cache[collector_key_west] = DataCollector(sport, "NBA West")
        print(f"🆕 새 DataCollector 생성: {collector_key_west}")
    
    collector_east = st.session_state.collector_cache[collector_key_east]
    collector_west = st.session_state.collector_cache[collector_key_west]
    
    # 통합 collector 생성 (첫 번째 collector를 기본으로 사용)
    collector = collector_east
else:
    collector_key = f"{sport}_{league}"
    if collector_key not in st.session_state.collector_cache:
        st.session_state.collector_cache[collector_key] = DataCollector(sport, league)
        print(f"🆕 새 DataCollector 생성: {collector_key}")
    
    collector = st.session_state.collector_cache[collector_key]

analyzer = PerformanceAnalyzer()
predictor = SportRouter()
score_predictor = get_score_predictor()

# NBA 팀 목록 통합 함수
def get_all_teams():
    """리그의 모든 팀 반환 (NBA의 경우 East + West 통합)"""
    if league == "NBA":
        teams_east = collector_east.get_teams()
        teams_west = collector_west.get_teams()
        all_teams = teams_east + teams_west
        
        # 컨퍼런스 필터 적용
        if nba_conference == "East":
            return teams_east
        elif nba_conference == "West":
            return teams_west
        else:
            return all_teams
    else:
        return collector.get_teams()

# NBA 팀 데이터 가져오기 함수
def get_team_data_nba(team_name):
    """NBA 팀 데이터 가져오기 (East/West 자동 판별)"""
    if league == "NBA":
        # East 팀인지 확인
        if team_name in collector_east.get_teams():
            return collector_east.get_team_data(team_name)
        # West 팀인지 확인
        elif team_name in collector_west.get_teams():
            return collector_west.get_team_data(team_name)
    return collector.get_team_data(team_name)

# NBA 선수 목록 가져오기 함수
def get_players_nba(team_name):
    """NBA 선수 목록 가져오기 (East/West 자동 판별)"""
    if league == "NBA":
        if team_name in collector_east.get_teams():
            return collector_east.get_players(team_name)
        elif team_name in collector_west.get_teams():
            return collector_west.get_players(team_name)
    return collector.get_players(team_name)

# NBA 선수 데이터 가져오기 함수
def get_player_data_nba(player_name, team_name):
    """NBA 선수 데이터 가져오기 (East/West 자동 판별)"""
    if league == "NBA":
        if team_name in collector_east.get_teams():
            return collector_east.get_player_data(player_name, team_name)
        elif team_name in collector_west.get_teams():
            return collector_west.get_player_data(player_name, team_name)
    return collector.get_player_data(player_name, team_name)

# 메인 광고 공간 (모든 탭에서 동일하게 표시)
st.markdown("---")
with st.container():
    st.markdown("""
    <div style='background: #2a2a2a; padding: 15px; border-radius: 8px; 
                text-align: center; margin: 15px 0; border: 1px solid #CCFF00;'>
        <h4 style='color: #CCFF00; margin: 0; font-size: 15px; font-weight: 600;'>📢 광고 공간</h4>
        <p style='color: #ffffff; margin: 8px 0; font-size: 12px;'>스폰서를 기다립니다</p>
        <p style='color: #CCFF00; font-size: 11px;'>728 x 90 px</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

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

with tab1:
    st.header(t('match_prediction'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t('home_team'))
        home_team = st.selectbox(t('select_team'), get_all_teams(), key="home")
        home_data = get_team_data_nba(home_team)
        
        if home_data:
            # 실제 데이터 표시
            if home_data.get('real_data'):
                st.success(t('real_data'))
                if 'position' in home_data:
                    st.metric(t('league_rank'), f"{home_data['position']}{t('rank_suffix')}")
                if 'points' in home_data:
                    st.metric(t('points'), f"{home_data['points']}{t('points_suffix')}")
            else:
                st.warning(t('simulated_data'))
            
            st.metric(t('recent_5_winrate'), f"{home_data.get('recent_winrate', 0):.1%}")
            st.metric(t('home_winrate'), f"{home_data.get('home_winrate', 0):.1%}")
            st.metric(t('avg_score'), f"{home_data.get('avg_goals', 0):.2f}")
    
    with col2:
        st.subheader(t('away_team'))
        away_team = st.selectbox(t('select_team'), get_all_teams(), key="away")
        away_data = get_team_data_nba(away_team)
        
        if away_data:
            # 실제 데이터 표시
            if away_data.get('real_data'):
                st.success(t('real_data'))
                if 'position' in away_data:
                    st.metric(t('league_rank'), f"{away_data['position']}{t('rank_suffix')}")
                if 'points' in away_data:
                    st.metric(t('points'), f"{away_data['points']}{t('points_suffix')}")
            else:
                st.warning(t('simulated_data'))
            
            st.metric(t('recent_5_winrate'), f"{away_data.get('recent_winrate', 0):.1%}")
            st.metric(t('away_winrate'), f"{away_data.get('away_winrate', 0):.1%}")
            st.metric(t('avg_score'), f"{away_data.get('avg_goals', 0):.2f}")
    
    # 추가 요소 입력
    st.subheader(t('match_conditions'))
    col3, col4, col5 = st.columns(3)
    
    with col3:
        weather = st.selectbox(t('weather'), [
            t('weather_sunny'),
            t('weather_cloudy'),
            t('weather_rain'),
            t('weather_snow'),
            t('weather_windy')
        ])
        temperature = st.slider(t('temperature'), -10, 40, 20)
    
    with col4:
        field_condition = st.selectbox(t('field_condition'), [
            t('field_excellent'),
            t('field_good'),
            t('field_fair'),
            t('field_poor')
        ])
        match_importance = st.selectbox(t('match_importance'), [
            t('importance_normal'),
            t('importance_important'),
            t('importance_very_important')
        ])
    
    with col5:
        rest_days_home = st.number_input(t('rest_days_home'), 0, 30, 3)
        rest_days_away = st.number_input(t('rest_days_away'), 0, 30, 3)
    
    if st.button(t('run_prediction'), type="primary", use_container_width=True):
        with st.spinner(t('analyzing_data')):
            # 부상 정보 수집 (모든 지원 리그)
            injury_data = None
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
            
            if injury_league:
                try:
                    injury_fetcher = InjuryFetcher(league=injury_league)
                    home_injuries = injury_fetcher.get_team_injuries(home_team)
                    away_injuries = injury_fetcher.get_team_injuries(away_team)
                    
                    injury_data = {
                        'home': home_injuries,
                        'away': away_injuries
                    }
                    
                    # 부상 정보 표시
                    if home_injuries or away_injuries:
                        if injury_league in ["NBA", "MLB"]:
                            st.info(t('injury_info_applied'))
                        else:
                            st.info(t('injury_info_applied2'))
                        
                        col_inj1, col_inj2 = st.columns(2)
                        
                        with col_inj1:
                            if home_injuries:
                                st.warning(f"**{home_team}** " + t('injured_count_label') + f"{len(home_injuries)}" + t('people_unit'))
                                for inj in home_injuries[:3]:  # 최대 3명만 표시
                                    st.caption(f"• {inj['player']} ({inj['status']})")
                        
                        with col_inj2:
                            if away_injuries:
                                st.warning(f"**{away_team}** " + t('injured_count_label') + f"{len(away_injuries)}" + t('people_unit'))
                                for inj in away_injuries[:3]:  # 최대 3명만 표시
                                    st.caption(f"• {inj['player']} ({inj['status']})")
                except Exception as e:
                    st.caption(t('injury_info_collection_failed') + str(e))
            
            # 코칭스태프 정보 수집
            coaching_data = None
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
                    home_coaching = coaching_fetcher.fetch_team_coaching_staff(home_team)
                    away_coaching = coaching_fetcher.fetch_team_coaching_staff(away_team)
                    
                    coaching_data = {
                        'home': home_coaching,
                        'away': away_coaching
                    }
                except Exception as e:
                    pass  # 코칭스태프 정보 없어도 예측 진행
            
            # NBA의 경우 정확한 컨퍼런스 결정
            prediction_league = league
            if league == "NBA":
                # 홈팀의 컨퍼런스 확인
                if home_team in collector_east.get_teams():
                    prediction_league = "NBA East"
                elif home_team in collector_west.get_teams():
                    prediction_league = "NBA West"
                else:
                    # 기본값: East
                    prediction_league = "NBA East"
            
            # 예측 실행
            prediction = predictor.predict_match(
                league=prediction_league,
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
                injury_data=injury_data,
                coaching_data=coaching_data
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
            
            # 상세 분석
            st.subheader(t('detailed_analysis'))
            
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                st.write(t('key_factors'))
                for factor in prediction['key_factors']:
                    st.write(f"• {factor}")
            
            with analysis_col2:
                st.write(t('prediction_confidence'))
                confidence = prediction['confidence']
                st.progress(confidence)
                st.write(f"{t('confidence_label')}{confidence:.1%}")
            
            # 예상 스코어 (기존)
            st.subheader(t('expected_score_basic'))
            st.write(f"**{home_team} {prediction['expected_score_home']} - {prediction['expected_score_away']} {away_team}**")
            
            # 상위 3개 가능 스코어 표시
            if 'top_3_scores' in prediction:
                st.write("**가능성 높은 스코어 Top 3:**")
                for i, (score, prob) in enumerate(prediction['top_3_scores'], 1):
                    st.write(f"{i}. {score[0]}:{score[1]} ({prob*100:.1f}%)")
            
            # 기대 득점 λ 표시 (디버깅/분석용)
            if 'lambda_home' in prediction and 'lambda_away' in prediction:
                st.caption(f"기대 득점: 홈 λ={prediction['lambda_home']}, 원정 λ={prediction['lambda_away']}, 상관 λ_C={prediction.get('lambda_c', 0)}")
            
            # 상세 점수 예측 (새로운 기능)
            st.subheader(t('detailed_score_prediction_title'))
            
            try:
                score_prediction = score_predictor.predict_match_score(
                    league=prediction_league,  # NBA의 경우 정확한 컨퍼런스 사용
                    home_team=home_team,
                    away_team=away_team,
                    home_data=home_data,
                    away_data=away_data
                )
                
                # 예측 점수 카드
                score_col1, score_col2, score_col3 = st.columns([2, 1, 2])
                
                with score_col1:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background-color: #2a2a2a; border-radius: 10px; border: 1px solid #CCFF00;'>
                        <h2 style='color: #CCFF00; margin: 0;'>{home_team}</h2>
                        <h1 style='font-size: 48px; margin: 10px 0; color: #ffffff;'>{score_prediction['home_score']}</h1>
                        <p style='color: #CCFF00; margin: 0;'>승률 {score_prediction['home_win_probability']}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with score_col2:
                    st.markdown("""
                    <div style='text-align: center; padding: 40px 0;'>
                        <h1 style='font-size: 36px; color: #CCFF00;'>VS</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with score_col3:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background-color: #2a2a2a; border-radius: 10px; border: 1px solid #CCFF00;'>
                        <h2 style='color: #CCFF00; margin: 0;'>{away_team}</h2>
                        <h1 style='font-size: 48px; margin: 10px 0; color: #ffffff;'>{score_prediction['away_score']}</h1>
                        <p style='color: #CCFF00; margin: 0;'>승률 {score_prediction['away_win_probability']}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 무승부 확률 (축구만)
                if 'draw_probability' in score_prediction:
                    st.info(t('draw_probability_label') + f"{score_prediction['draw_probability']}%")
                
                # 신뢰도 표시
                confidence_color = {t('confidence_high'): "🟢", t('confidence_medium'): "🟡", t('confidence_low'): "🔴"}
                st.write(f"{t('prediction_confidence_label2')} {confidence_color.get(score_prediction['confidence'], '⚪')} {score_prediction['confidence']}")
                
                # 예측 설명
                with st.expander(t('view_prediction_basis'), expanded=False):
                    explanation = score_predictor.get_prediction_explanation(score_prediction)
                    st.markdown(explanation)
                    
                    # 추가 통계 (종목별)
                    if prediction_league in ["NBA East", "NBA West", "KBL"]:
                        # 농구
                        st.write(t('expected_total_points') + f" {score_prediction['total_points']}" + t('points_unit'))
                        st.write(t('score_difference_label') + f" {abs(score_prediction['spread'])}" + t('points_unit'))
                    elif 'total_goals' in score_prediction:
                        # 축구/야구/배구
                        st.write(t('expected_total_goals') + f" {score_prediction['total_goals']}" + t('goals_unit'))
                
            except Exception as e:
                st.warning(t('score_prediction_error') + str(e))

with tab2:
    st.header(t('team_analysis_title'))
    
    selected_team = st.selectbox(t('select_team_analysis'), get_all_teams(), key="team_analysis")
    
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
                    st.subheader(t('coaching_staff'))
                    
                    col_coach1, col_coach2 = st.columns(2)
                    
                    with col_coach1:
                        st.info(f"{t('head_coach_label')} {team_staff['head_coach']}")
                    
                    with col_coach2:
                        st.info(f"{t('coaches_label')} {len(team_staff['assistant_coaches'])}{t('people_count')}")
                    
                    with st.expander(t('coach_details')):
                        for i, coach in enumerate(team_staff['assistant_coaches'], 1):
                            st.write(f"{i}. {coach}")
            except Exception as e:
                st.caption(t('coaching_staff_load_failed') + str(e))
        
        # 최근 폼
        st.subheader(t('recent_form'))
        st.line_chart(team_analysis['form_chart'])
        
        # 강점/약점
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.subheader(t('strengths'))
            for strength in team_analysis['strengths']:
                st.success(strength)
        
        with col_t2:
            st.subheader(t('weaknesses'))
            for weakness in team_analysis['weaknesses']:
                st.warning(weakness)

with tab3:
    st.header(t('player_individual_analysis'))
    
    col_team, col_refresh = st.columns([4, 1])
    
    with col_team:
        team_for_players = st.selectbox(t('select_team'), get_all_teams(), key="player_team")
    
    with col_refresh:
        st.write("")  # 공간 확보
        if st.button(t('refresh_roster'), key="refresh_roster"):
            # 캐시 초기화
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
    
    if st.button(t('run_player_analysis')):
        player_analysis = analyzer.analyze_player(selected_player, collector)
        
        # 실제 데이터 확인
        player_data = get_player_data_nba(selected_player, team_for_players)
        
        if player_data.get('real_data'):
            st.success(t('real_data'))
            
            # 실제 통계 표시
            st.subheader(f"📊 {player_data['name']} - {player_data['position']}")
            
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            
            with col_p1:
                st.metric(t('age'), f"{player_data['age']}{t('age_suffix')}")
                st.metric(t('matches_played'), player_data['matches_played'])
            
            with col_p2:
                if 'ppg' in player_data:  # NBA
                    st.metric(t('avg_points'), f"{player_data['ppg']:.1f}")
                    st.metric(t('avg_rebounds'), f"{player_data.get('rpg', 0):.1f}")
                else:  # 축구
                    st.metric(t('goals'), player_data['goals'])
                    st.metric(t('assists'), player_data['assists'])
            
            with col_p3:
                st.metric(t('avg_rating'), f"{player_data['rating_avg']:.2f}/10")
                st.metric(t('condition'), f"{player_data['condition']:.1f}/100")
            
            with col_p4:
                st.metric(t('injury_status'), player_data['injury_status'])
                st.metric(t('fatigue_label'), f"{player_data['fatigue_level']:.1f}/100")
        else:
            st.warning(t('simulated_data'))
            
            col_p1, col_p2, col_p3 = st.columns(3)
            
            with col_p1:
                st.metric(t('condition_index_label'), f"{player_analysis['condition_index']:.1f}/10")
            
            with col_p2:
                st.metric(t('recent_5_rating'), f"{player_analysis['recent_rating']:.2f}")
            
            with col_p3:
                st.metric(t('injury_risk_label'), player_analysis['injury_risk'])
        
        st.subheader(t('performance_trend_label'))
        st.line_chart(player_analysis['performance_trend'])

with tab4:
    st.header(t('tab_schedule'))
    
    # 경기 일정 데이터 임포트 - 실시간 API 사용
    try:
        from modules.schedule_fetcher import (
            get_upcoming_matches, 
            get_team_next_matches, 
            get_all_upcoming_matches
        )
        
        st.info("📡 실시간 경기 일정 API 사용 중 (ESPN API)")
        
        # 일정 보기 모드 선택
        schedule_mode = st.radio(
            t('schedule_mode'),
            [t('all_schedule'), t('league_schedule'), t('team_schedule')],
            horizontal=True
        )
        
        if schedule_mode == t('all_schedule'):
            st.subheader(t('all_leagues_upcoming'))
            
            with st.spinner(t('loading_schedule')):
                all_matches = get_all_upcoming_matches()
            
            for league_name, matches in all_matches.items():
                if matches:
                    with st.expander(f"⚽ {league_name} ({len(matches)}경기)", expanded=True):
                        for match in matches[:10]:  # 최대 10경기 표시
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
            st.subheader(t('league_schedule_title'))
            
            # 리그 매핑
            league_map = {
                "EPL": "EPL",
                "La Liga": "La Liga",
                "Bundesliga": "Bundesliga",
                "Serie A": "Serie A",
                "NBA East": "NBA",
                "NBA West": "NBA"
            }
            
            schedule_league = league_map.get(league, league)
            
            with st.spinner(f"{schedule_league} 실시간 경기 일정 가져오는 중..."):
                matches = get_upcoming_matches(schedule_league, days=7)
            
            if matches:
                st.info(f"📊 {schedule_league} - 다가오는 {len(matches)}경기")
                
                # 날짜별로 그룹화
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
                st.warning(f"⚠️ {schedule_league} 리그의 실시간 일정을 가져올 수 없습니다.")
        
        elif schedule_mode == t('team_schedule'):
            st.subheader(t('team_next_matches'))
            
            schedule_team = st.selectbox(t('select_team'), get_all_teams(), key="schedule_team")
            
            # 리그 매핑
            league_map = {
                "EPL": "EPL",
                "La Liga": "La Liga",
                "Bundesliga": "Bundesliga",
                "Serie A": "Serie A",
                "NBA East": "NBA",
                "NBA West": "NBA"
            }
            
            schedule_league = league_map.get(league, league)
            
            with st.spinner(f"{schedule_team} 실시간 경기 일정 가져오는 중..."):
                team_matches = get_team_next_matches(schedule_league, schedule_team, limit=5)
            
            if team_matches:
                st.success(f"✅ {schedule_team}의 다음 {len(team_matches)}경기")
                
                for idx, match in enumerate(team_matches, 1):
                    with st.container():
                        st.subheader(t('match_number') + str(idx))
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**날짜:** {match['date']}")
                            st.write(f"**시간:** {match['time']}")
                            st.write(f"**장소:** {match['venue']}")
                            st.write(f"**중계:** {match['tv']}")
                            if 'status' in match:
                                st.caption(t('status_label') + match['status'])
                        
                        with col2:
                            # 홈/원정 표시
                            if schedule_team.lower() in match['home'].lower():
                                st.info(t('home_match'))
                                st.write(f"**상대팀:** {match['away']}")
                                opponent = match['away']
                            else:
                                st.warning(t('away_match'))
                                st.write(f"**상대팀:** {match['home']}")
                                opponent = match['home']
                        
                        # 점수 예측 추가
                        if st.button(t('predict_score'), key=f"predict_{idx}"):
                            try:
                                # 팀 데이터 가져오기
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
                                    
                                    st.success(t('expected_score_label') + f"{match['home']} {score_pred['home_score']} - {score_pred['away_score']} {match['away']}**")
                                    st.write(t('win_rate_label') + f"{match['home']} {score_pred['home_win_probability']}% vs {match['away']} {score_pred['away_win_probability']}%")
                                    if 'draw_probability' in score_pred:
                                        st.write(t('draw_label') + f"{score_pred['draw_probability']}%")
                                    st.caption(t('confidence_label') + score_pred['confidence'])
                                else:
                                    st.warning(t('team_data_not_found'))
                            except Exception as e:
                                st.error(t('prediction_error') + str(e))
                        
                        st.divider()
            else:
                st.warning(f"⚠️ {schedule_team}의 실시간 일정을 가져올 수 없습니다.")
    
    except ImportError as e:
        st.error(f"❌ 경기 일정 모듈을 불러올 수 없습니다: {e}")
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")

with tab5:
    st.header(t('tab_injury_report'))
    
    # 리그별 injury fetcher 초기화
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
        st.warning(t('injury_report_support') + ', '.join(injury_league_map.keys()) + t('leagues_only'))
    else:
        # 부상 정보 가져오기
        injury_fetcher = InjuryFetcher(league=injury_league)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if injury_league in ["NBA", "MLB"]:
                st.info(t('realtime_injury_data'))
            elif injury_league == "KBO":
                st.info(t('simulation_injury_data'))
            else:
                st.info(t('trying_realtime_injury'))
        
        with col2:
            if st.button(t('refresh_injury_info')):
                st.rerun()
        
        # 부상 요약 정보
        with st.spinner(t('loading_injury_info')):
            try:
                summary = injury_fetcher.get_injury_summary()
                
                st.subheader(t('league_injury_status'))
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    st.metric(t('total_injured_players'), f"{summary['total_injured_players']}명")
                
                with col_s2:
                    st.metric(t('out_status'), f"{summary['out']}명", delta=None, delta_color="inverse")
                
                with col_s3:
                    st.metric(t('day_to_day_status'), f"{summary['day_to_day']}명")
                
                with col_s4:
                    st.metric(t('questionable_status'), f"{summary['questionable']}명")
                
                st.caption(t('last_updated_label') + summary['last_updated'])
                
                # 팀별 부상 정보
                st.subheader(f"{'🏀' if injury_league == 'NBA' else '⚾' if injury_league in ['MLB', 'KBO'] else '⚽'} 팀별 부상 선수")
                
                # 팀 선택
                selected_team = st.selectbox(
                    t('select_team'),
                    [t('all_teams')] + get_all_teams(),
                    key="injury_team_select"
                )
                
                all_injuries = injury_fetcher.fetch_all_injuries()
                
                if selected_team == t('all_teams'):
                    # 모든 팀의 부상 정보 표시
                    for team_name, injuries in all_injuries.items():
                        if injuries:
                            with st.expander(f"**{team_name}** ({len(injuries)}명)", expanded=False):
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
                                    st.write(f"   상태: {injury['status']}")
                                    st.write(f"   부상: {injury['description']}")
                                    st.write(f"   예상 복귀: {injury['date']}")
                                    st.divider()
                else:
                    # 선택한 팀의 부상 정보만 표시
                    team_injuries = injury_fetcher.get_team_injuries(selected_team)
                    
                    if team_injuries:
                        st.write(f"**{selected_team}** 팀의 부상 선수: {len(team_injuries)}명")
                        
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
                                st.write(f"**상태:** {injury['status']}")
                                st.write(f"**부상:** {injury['description']}")
                                st.write(f"**예상 복귀:** {injury['date']}")
                            
                            st.divider()
                    else:
                        st.success(f"✅ {selected_team} 팀에는 현재 부상 선수가 없습니다!")
                
                # 선수별 검색
                st.subheader(t('player_injury_search'))
                
                player_search = st.text_input(t('enter_player_name'), placeholder=t('example_prefix') + ('LeBron James' if injury_league == 'NBA' else 'Shohei Ohtani' if injury_league == 'MLB' else '양현종' if injury_league == 'KBO' else 'Kevin De Bruyne'))
                
                if player_search:
                    player_injury = injury_fetcher.get_player_status(player_search)
                    
                    if player_injury:
                        st.warning(f"⚠️ {player_search}는 현재 부상 상태입니다.")
                        
                        col_p1, col_p2 = st.columns(2)
                        
                        with col_p1:
                            st.write(f"**포지션:** {player_injury['position']}")
                            st.write(f"**상태:** {player_injury['status']}")
                        
                        with col_p2:
                            st.write(f"**부상:** {player_injury['description']}")
                            st.write(f"**예상 복귀:** {player_injury['date']}")
                    else:
                        st.success(f"✅ {player_search}는 현재 건강한 상태입니다!")
                
            except Exception as e:
                st.error(f"❌ 부상 정보를 가져오는 중 오류가 발생했습니다: {e}")
                if injury_league in ["NBA", "MLB"]:
                    st.info(t('espn_access_error'))
                elif injury_league == "KBO":
                    st.info(t('kbo_simulation_data'))
                else:
                    st.info(t('realtime_data_failed'))

with tab6:
    st.header(t('tab_coaching_staff'))
    
    # 리그별 coaching staff fetcher 초기화
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
        st.warning(t('coaching_staff_support') + ', '.join(coaching_league_map.keys()) + t('leagues_only'))
    else:
        # 코칭스태프 정보 가져오기
        coaching_fetcher = CoachingStaffFetcher(league=coaching_league)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(t('coaching_staff_info_desc'))
        
        with col2:
            if st.button(t('refresh_coaching_staff')):
                st.rerun()
        
        # 코칭스태프 요약 정보
        with st.spinner(t('loading_coaching_staff')):
            try:
                summary = coaching_fetcher.get_coaching_summary()
                
                st.subheader(t('league_coaching_status'))
                
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    st.metric(t('total_teams_count'), f"{summary['total_teams']}팀")
                
                with col_s2:
                    st.metric(t('total_coaches_count'), f"{summary['total_coaches']}명")
                
                with col_s3:
                    st.metric(t('avg_coaches_per_team'), f"{summary['avg_coaches_per_team']:.1f}" + t('people_unit'))
                
                st.caption(t('last_updated_label') + summary['last_updated'])
                
                # 팀별 코칭스태프 정보
                st.subheader(f"{'🏀' if coaching_league == 'NBA' else '⚾' if coaching_league in ['MLB', 'KBO'] else '⚽'} 팀별 코칭스태프")
                
                # 팀 선택
                selected_team = st.selectbox(
                    t('select_team'),
                    [t('all_teams')] + get_all_teams(),
                    key="coaching_team_select"
                )
                
                all_coaching = coaching_fetcher.fetch_all_coaching_staff()
                
                if selected_team == t('all_teams'):
                    # 모든 팀의 코칭스태프 정보 표시
                    for team_name, staff in all_coaching.items():
                        with st.expander(f"**{team_name}**", expanded=False):
                            col_c1, col_c2 = st.columns([1, 2])
                            
                            with col_c1:
                                st.write(t('head_coach_title'))
                                st.write(f"**{staff['head_coach']}**")
                            
                            with col_c2:
                                st.write(t('coaches_title'))
                                for i, coach in enumerate(staff['assistant_coaches'], 1):
                                    st.write(f"{i}. {coach}")
                            
                            st.caption(t('updated_label') + staff['last_updated'])
                else:
                    # 선택한 팀의 코칭스태프 정보만 표시
                    team_staff = coaching_fetcher.fetch_team_coaching_staff(selected_team)
                    
                    if team_staff and team_staff.get('head_coach') != 'Unknown':
                        st.write(f"## {selected_team}")
                        
                        col_t1, col_t2 = st.columns(2)
                        
                        with col_t1:
                            st.subheader(t('head_coach_section'))
                            st.markdown(f"""
                            <div style='text-align: center; padding: 30px; background-color: #2a2a2a; border-radius: 10px; border: 1px solid #CCFF00;'>
                                <h2 style='color: #CCFF00; margin: 0;'>{team_staff['head_coach']}</h2>
                                <p style='color: #ffffff; margin-top: 10px;'>Head Coach</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_t2:
                            st.subheader(t('coaches_section'))
                            st.write(f"**총 {len(team_staff['assistant_coaches'])}명**")
                            
                            for i, coach in enumerate(team_staff['assistant_coaches'], 1):
                                st.write(f"{i}. {coach}")
                        
                        st.divider()
                        st.caption(t('last_updated_label') + team_staff['last_updated'])
                    else:
                        st.warning(f"⚠️ {selected_team}" + t('coaching_staff_not_found'))
                
                # 감독 검색
                st.subheader(t('coach_search_title'))
                
                coach_search = st.text_input(t('enter_coach_name'), placeholder=t('example_prefix') + ('Steve Kerr' if coaching_league == 'NBA' else 'Aaron Boone' if coaching_league == 'MLB' else '김종국' if coaching_league == 'KBO' else 'Pep Guardiola'))
                
                if coach_search:
                    found_teams = []
                    for team_name, staff in all_coaching.items():
                        if coach_search.lower() in staff['head_coach'].lower():
                            found_teams.append((team_name, staff))
                    
                    if found_teams:
                        st.success(f"✅ {len(found_teams)}" + t('found_in_teams') + coach_search + t('found_text'))
                        
                        for team_name, staff in found_teams:
                            with st.container():
                                col_f1, col_f2 = st.columns([1, 2])
                                
                                with col_f1:
                                    st.write(f"**팀:** {team_name}")
                                    st.write(f"**감독:** {staff['head_coach']}")
                                
                                with col_f2:
                                    st.write(f"**코치진:** {', '.join(staff['assistant_coaches'][:3])}")
                                
                                st.divider()
                    else:
                        st.warning(f"⚠️ '{coach_search}'" + t('not_found_text'))
                
            except Exception as e:
                st.error(f"❌ 코칭스태프 정보를 가져오는 중 오류가 발생했습니다: {e}")

with tab7:
    st.header(t('tab_settings'))
    
    st.subheader(t('data_source_settings_title'))
    
    enable_web_scraping = st.checkbox(t('enable_web_scraping'), value=True)
    enable_api = st.checkbox(t('enable_api_data'), value=False)
    
    if enable_api:
        api_key = st.text_input(t('api_key_label'), type="password")
    
    st.subheader(t('prediction_model_settings_title'))
    
    model_type = st.selectbox(t('select_model_label'), ["Random Forest", "XGBoost", "LightGBM", t('ensemble_model')])
    
    st.slider(t('historical_data_range'), 10, 100, 30)
    
    if st.button(t('save_settings_button')):
        st.success(t('settings_saved_message'))

# 푸터
st.divider()
st.caption(t('footer_title'))

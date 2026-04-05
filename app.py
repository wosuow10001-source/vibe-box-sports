import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# 페이지 설정 (SEO 최적화 타이틀)
st.set_page_config(
    page_title="VIBE BOX | AI 해외축구 NBA MLB KBL 분석 및 경기 예측 플랫폼",
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
from modules.community_database import get_community_database
import time
import streamlit.components.v1 as components

## SEO & Meta Tag Injection (Immediate Execution)
st.markdown(
    f"""
    <script>
        (function() {{
            function inject() {{
                var head = window.parent.document.head;
                if (!head) return;
                
                // Google Verification (Streamlit Cloud Domain)
                if (!head.querySelector('meta[name="google-site-verification"]')) {{
                    var m1 = window.parent.document.createElement('meta');
                    m1.name = "google-site-verification";
                    m1.content = "ovEC7t-O6fQOLmeHv7kO3hX1fI6YEqitU-J3-MivhIs";
                    head.prepend(m1);
                }}
                
                // Naver Verification
                if (!head.querySelector('meta[name="naver-site-verification"]')) {{
                    var m2 = window.parent.document.createElement('meta');
                    m2.name = "naver-site-verification";
                    m2.content = "cfecf320d62cc8ee0bf8d1e39581732ff46a0020";
                    head.prepend(m2);
                }}
                
                // Description
                if (!head.querySelector('meta[name="description"]')) {{
                    var m3 = window.parent.document.createElement('meta');
                    m3.name = "description";
                    m3.content = "VIBE BOX Sports MatchSignal - AI 기반 해외축구, NBA, MLB, KBL 분석 및 경기 예측 플랫폼. 실시간 데이터 기반 정밀 경기 분석을 제공합니다.";
                    head.prepend(m3);
                }}
                console.log("SEO Tags Injected Successfully");
            }}
        injectSEOTags();
        setTimeout(injectSEOTags, 2000);
        setTimeout(injectSEOTags, 5000);
    </script>
    """,
    unsafe_allow_html=True
)

# 검색 엔진봇을 위한 시맨틱 헤더 (화면에는 보이지 않음)
st.markdown("<h1 style='display:none;'>VIBE BOX Sports MatchSignal - AI 스포츠 분석 및 경기 예측</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='display:none;'>해외축구, NBA, MLB, KBL 실시간 데이터 기반 정교한 AI 예측 엔진</h2>", unsafe_allow_html=True)
st.markdown("<p style='display:none;'>스포츠 분석, 경기 예측, K리그, EPL, NBA, KBL, MLB, KBO 메트릭스 분석 플랫폼</p>", unsafe_allow_html=True)

# Streamlit 세션 상태 초기화
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.collector_cache = {}
    st.session_state.last_refresh_time = time.time()
    
    # 로스터 데이터 모듈 강제 리로드 (캐시 문제 방지)
    import importlib
    try:
        if 'data.kbo_rosters_complete_2026' in sys.modules:
            importlib.reload(sys.modules['data.kbo_rosters_complete_2026'])
        if 'data.kbl_rosters_complete_2025_26' in sys.modules:
            importlib.reload(sys.modules['data.kbl_rosters_complete_2025_26'])
        if 'data.kleague_rosters_complete_2026' in sys.modules:
            importlib.reload(sys.modules['data.kleague_rosters_complete_2026'])
        if 'data.vleague_rosters_complete_2025_26' in sys.modules:
            importlib.reload(sys.modules['data.vleague_rosters_complete_2025_26'])
        print("[OK] Roster data modules reloaded")
    except Exception as e:
        print(f"[WARNING] Module reload failed: {e}")
    
    print("[OK] App initialized")

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
    # 커피 후원 버튼 스타일 (st.popover 버튼에도 적용되도록 선택자 추가)
    st.markdown("""
    <style>
    /* 커피 후원 버튼 - 황금색 배경, 검정 텍스트 */
    div[data-testid="column"]:nth-child(2) .stButton > button,
    div[data-testid="column"]:nth-child(2) [data-testid="stPopover"] > button {
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
    div[data-testid="column"]:nth-child(2) .stButton > button:hover,
    div[data-testid="column"]:nth-child(2) [data-testid="stPopover"] > button:hover {
        background-color: #FFC700 !important;
        color: #000000 !important;
        border: 2px solid #FFC700 !important;
        box-shadow: 0 3px 8px rgba(255, 215, 0, 0.4) !important;
    }
    /* 커피 버튼 텍스트 강제 검정색 */
    div[data-testid="column"]:nth-child(2) .stButton > button p,
    div[data-testid="column"]:nth-child(2) [data-testid="stPopover"] > button p {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 팝오버를 사용해 클릭 시 즉시 렌더링 (리로드 방지)
    with st.popover("☕ 커피 한 잔 후원하기", use_container_width=True):
        st.markdown("""
        <div style='background-color: #2a2a2a; padding: 20px; border-radius: 12px; 
                    border: 1px solid #CCFF00; margin: 10px 0; text-align: center;'>
            <h4 style='color: #CCFF00; margin: 0 0 10px 0;'>☕ 커피 한 잔 후원하기 / Buy me a Coffee</h4>
            <p style='color: #ffffff; font-size: 0.875rem; margin-bottom: 15px;'>
                개발자를 응원해주세요! / Support the Developer!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 이미지 경로
        curr_dir = Path(__file__).parent
        kakao_qr_path = str(curr_dir / "assets" / "coffee_qr.jpg")
        paypal_qr_path = str(curr_dir / "assets" / "paypal_qr.png")
        
        col_q1, col_q2 = st.columns(2)
        
        # KakaoPay 섹션
        with col_q1:
            st.markdown("<p style='text-align: center; color: #CCFF00; font-weight: 600; margin-bottom: 10px;'>🇰🇷 KakaoPay (KRW)</p>", unsafe_allow_html=True)
            if os.path.exists(kakao_qr_path):
                st.image(kakao_qr_path, use_container_width=True)
            
            st.markdown("""
            <div style='text-align: center; margin-top: 10px;'>
                <a href='https://qr.kakaopay.com/FHucxWATA' target='_blank' 
                   style='display: inline-block; background-color: #FEE500; color: #1a1a1a;
                          padding: 8px 16px; border-radius: 6px; text-decoration: none;
                          font-weight: 700; font-size: 0.85rem; width: 80%;'>
                    📱 KakaoPay
                </a>
            </div>
            """, unsafe_allow_html=True)
            
        # PayPal 섹션
        with col_q2:
            st.markdown("<p style='text-align: center; color: #CCFF00; font-weight: 600; margin-bottom: 10px;'>🌎 PayPal (Global)</p>", unsafe_allow_html=True)
            if os.path.exists(paypal_qr_path):
                st.image(paypal_qr_path, use_container_width=True)
            else:
                st.warning("PayPal QR code not found.")
                
            st.markdown("""
            <div style='text-align: center; margin-top: 10px;'>
                <a href='https://www.paypal.com' target='_blank' 
                   style='display: inline-block; background-color: #0070ba; color: #ffffff;
                          padding: 8px 16px; border-radius: 6px; text-decoration: none;
                          font-weight: 700; font-size: 0.85rem; width: 80%;'>
                    💳 PayPal Support
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        # 코인 후원 섹션 추가
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #CCFF00; font-weight: 600;'>💎 Crypto Donation</p>", unsafe_allow_html=True)
        
        crypto_col1, crypto_col2 = st.columns(2)
        with crypto_col1:
            st.caption("ETH / ERC20")
            st.code("0xB7BBF47aa5c8aC9551C7DEC9dD175DbBC5F98E54", language=None)
            st.caption("BTC")
            st.code("bc1q86v59zwytg72mdtsv5l3nkhlda7wztmkv4gv9e", language=None)
            
        with crypto_col2:
            st.caption("SOL / Solana")
            st.code("4tSoak4dM1KYciQv5FQJK1fzSb8PpH1roQLv4TbQPuuP", language=None)
            st.caption("TRX / TRC20")
            st.code("TSByfvevhYhX6Wo6VEvrJhHwd1azaCYaox", language=None)

    # 후원 안내 메시지
    st.markdown("""
    <p style='color: #cccccc; font-size: 0.75rem; text-align: center; margin-top: 5px; line-height: 1.4;'>
        후원금은 서비스 개발 및<br>운영 비용으로 사용됩니다 🙏
    </p>
    """, unsafe_allow_html=True)

st.markdown("---")

# 실시간 데이터 안내
st.info("[FETCH] " + t('realtime_data_notice'))


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
    t('soccer'): ["EPL", "La Liga", "Bundesliga", "Serie A", "K리그1", "MLS"],
    t('basketball'): ["NBA", "KBL"],
    t('baseball'): ["MLB", "KBO"],
    t('volleyball'): ["V-리그 남자", "V-리그 여자"]
}

st.sidebar.info(t('season_data_info'))

# 캐시 초기화 버튼
if st.sidebar.button(t('refresh_data')):
    st.session_state.collector_cache = {}
    st.session_state.last_refresh_time = time.time()
    # 실시간 API 캐시도 초기화
    try:
        from modules.player_stats_fetcher import refresh_player_cache
        from modules.schedule_fetcher import get_schedule_fetcher
        from modules.live_data_fetcher import get_live_fetcher
        refresh_player_cache()
        fetcher = get_schedule_fetcher()
        fetcher.cache = {}
        # LiveDataFetcher 캐시도 강제 삭제
        live_fetcher = get_live_fetcher()
        live_fetcher.clear_cache()
        st.sidebar.success(t('cache_cleared'))
    except Exception as e:
        st.sidebar.warning(f"[WARNING] {e}")
    st.rerun()

# [ALERT] 긴급 캐시 초기화 버튼 (KBO 로스터 문제 해결용)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 문제 해결")

col_reset1, col_reset2 = st.sidebar.columns(2)

with col_reset1:
    if st.button("완전 초기화", key="emergency_reset", use_container_width=True):
        # 1. Session state 완전 초기화
        keys_to_delete = [k for k in st.session_state.keys() if k not in ['language']]
        for key in keys_to_delete:
            del st.session_state[key]
        
        # 2. 로스터 모듈 강제 리로드
        import importlib
        roster_modules = [
            'data.kbo_rosters_complete_2026',
            'data.kbl_rosters_complete_2025_26',
            'data.kleague_rosters_complete_2026',
            'data.vleague_rosters_complete_2025_26',
            'modules.data_collector',
            'modules.roster_fetcher'
        ]
        
        for module_name in roster_modules:
            if module_name in sys.modules:
                try:
                    importlib.reload(sys.modules[module_name])
                    print(f"[OK] {module_name} reloaded")
                except Exception as e:
                    print(f"[WARNING] {module_name} reload failed: {e}")
        
        st.sidebar.success("초기화 완료!")
        st.rerun()

with col_reset2:
    if st.button("브라우저 캐시", key="browser_cache_info", use_container_width=True):
        st.sidebar.info("""
        **브라우저 캐시 삭제 방법:**
        1. Ctrl+Shift+Delete
        2. 캐시/쿠키 삭제
        3. 브라우저 완전 종료
        4. 다시 열기
        """)

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
        print(f"[NEW] DataCollector created: {collector_key_east}")
    
    if collector_key_west not in st.session_state.collector_cache:
        st.session_state.collector_cache[collector_key_west] = DataCollector(sport, "NBA West")
        print(f"[NEW] DataCollector created: {collector_key_west}")
    
    collector_east = st.session_state.collector_cache[collector_key_east]
    collector_west = st.session_state.collector_cache[collector_key_west]
    
    # 통합 collector 생성 (첫 번째 collector를 기본으로 사용)
    collector = collector_east
else:
    collector_key = f"{sport}_{league}"
    if collector_key not in st.session_state.collector_cache:
        st.session_state.collector_cache[collector_key] = DataCollector(sport, league)
        print(f"[NEW] DataCollector created: {collector_key}")
    
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    t('tab_match_prediction'),
    t('tab_team_analysis'),
    t('tab_player_analysis'),
    t('tab_schedule'),
    t('tab_injury_report'),
    t('tab_coaching_staff'),
    "📢 공지사항",
    "💼 비즈니스 문의",
    "💬 게시판",
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
                
                # NBA 순위 표시 (컨퍼런스 순위로 명시)
                if 'rank' in home_data and home_data['rank'] > 0:
                    rank_label = "컨퍼런스 순위" if league == "NBA" else "시즌 순위"
                    st.metric(rank_label, f"{home_data['rank']}위")
                elif 'position' in home_data:
                    st.metric(t('league_rank'), f"{home_data['position']}{t('rank_suffix')}")
                
                # 시즌 전적 표시
                if 'wins' in home_data and 'losses' in home_data:
                    st.metric("시즌 전적", f"{home_data['wins']}승 {home_data['losses']}패")
                
                # 최근 10경기 성적 표시
                if 'last_10' in home_data and home_data['last_10']:
                    st.metric("최근 10경기", home_data['last_10'])
                elif 'last_10_wins' in home_data:
                    st.metric("최근 10경기", f"{home_data['last_10_wins']}승 {home_data['last_10_losses']}패")
                
                # 스트레이크(연승/연패) 표시
                if 'streak' in home_data and home_data['streak']:
                    st.metric("현재 흐름", home_data['streak'])
                
                # 평균 득점/실점 (NBA)
                if 'ppg' in home_data:
                    col_ppg1, col_ppg2 = st.columns(2)
                    with col_ppg1:
                        st.metric("평균 득점", f"{home_data['ppg']:.1f}")
                    with col_ppg2:
                        st.metric("평균 실점", f"{home_data['opp_ppg']:.1f}")
                
                if 'points' in home_data:
                    st.metric(t('points'), f"{home_data['points']}{t('points_suffix')}")
            else:
                st.warning(t('simulated_data'))
            
            if 'ppg' not in home_data:
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
                
                # NBA 순위 표시 (컨퍼런스 순위로 명시)
                if 'rank' in away_data and away_data['rank'] > 0:
                    rank_label = "컨퍼런스 순위" if league == "NBA" else "시즌 순위"
                    st.metric(rank_label, f"{away_data['rank']}위")
                elif 'position' in away_data:
                    st.metric(t('league_rank'), f"{away_data['position']}{t('rank_suffix')}")
                
                # 시즌 전적 표시
                if 'wins' in away_data and 'losses' in away_data:
                    st.metric("시즌 전적", f"{away_data['wins']}승 {away_data['losses']}패")
                
                # 최근 10경기 성적 표시
                if 'last_10' in away_data and away_data['last_10']:
                    st.metric("최근 10경기", away_data['last_10'])
                elif 'last_10_wins' in away_data:
                    st.metric("최근 10경기", f"{away_data['last_10_wins']}승 {away_data['last_10_losses']}패")
                
                # 스트레이크(연승/연패) 표시
                if 'streak' in away_data and away_data['streak']:
                    st.metric("현재 흐름", away_data['streak'])
                
                # 평균 득점/실점 (NBA)
                if 'ppg' in away_data:
                    col_ppg1, col_ppg2 = st.columns(2)
                    with col_ppg1:
                        st.metric("평균 득점", f"{away_data['ppg']:.1f}")
                    with col_ppg2:
                        st.metric("평균 실점", f"{away_data['opp_ppg']:.1f}")
                
                if 'points' in away_data:
                    st.metric(t('points'), f"{away_data['points']}{t('points_suffix')}")
            else:
                st.warning(t('simulated_data'))
            
            if 'ppg' not in away_data:
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
            
            pass_flag = prediction.get('pass_flag', False)
            
            if pass_flag:
                st.warning("⚠️ 신뢰도 분석 결과: 이 경기는 분석을 통과(PASS)합니다. (근거 부족 또는 박빙)")
            else:
                if prediction.get('sport_type') == 'basketball' or 'spread_probability' in prediction:
                    st.markdown("### 📊 마켓별 확률 분석 (10,000회 시뮬레이션)")
                    col_r1, col_r2, col_r3 = st.columns(3)
                    
                    with col_r1:
                        win_prob = prediction.get('win_probability', {})
                        h_prob = win_prob.get('home', prediction.get('home_win_prob', 0.5))
                        st.metric(
                            t('home_win_prob'),
                            f"{h_prob:.1%}",
                            help="승무패 마켓: 홈팀 승리 확률"
                        )
                    
                    with col_r2:
                        spread_prob = prediction.get('spread_probability', {})
                        h_spread = spread_prob.get('cover_home', 0.5)
                        st.metric(
                            "핸디캡 커버 (홈)",
                            f"{h_spread:.1%}",
                            help="핸디캡 마켓: 홈팀이 핸디캡을 극복하고 승리할 확률"
                        )
                    
                    with col_r3:
                        ou_prob = prediction.get('over_under_probability', {})
                        over_p = ou_prob.get('over', 0.5)
                        st.metric(
                            "오버 (O/U)",
                            f"{over_p:.1%}",
                            help="언오버 마켓: 양 팀 합산 점수가 기준점보다 높을 확률"
                        )
                else:
                    # 축구 승무패
                    col_r1, col_r2, col_r3 = st.columns(3)
                    
                    with col_r1:
                        h_prob = prediction.get('home_win_prob')
                        if h_prob is not None:
                            st.metric(
                                t('home_win_prob'),
                                f"{h_prob:.1%}",
                                delta=f"{h_prob - 0.33:.1%}" if h_prob is not None else None
                            )
                    
                    with col_r2:
                        d_prob = prediction.get('draw_prob', 0)
                        st.metric(
                            t('draw_prob'),
                            f"{d_prob:.1%}",
                            delta=f"{d_prob - 0.33:.1%}" if d_prob > 0 else None
                        )
                    
                    with col_r3:
                        a_prob = prediction.get('away_win_prob')
                        if a_prob is not None:
                            st.metric(
                                t('away_win_prob'),
                                f"{a_prob:.1%}",
                                delta=f"{a_prob - 0.33:.1%}"
                            )
                    
                    # ========== 축구 추가 베팅 마켓 (NEW) ==========
                    st.markdown("#### 🎫 마켓별 상세 확률 (50,000회 시뮬레이션)")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    
                    with m_col1:
                        o25 = prediction.get('over_2_5_prob', 0.5)
                        st.metric("Over 2.5", f"{o25:.1%}", help="양 팀 합산 3골 이상 확률")
                        
                        o35 = prediction.get('over_3_5_prob', 0.2)
                        st.metric("Over 3.5", f"{o35:.1%}", help="양 팀 합산 4골 이상 확률")
                        
                    with m_col2:
                        btts = prediction.get('btts_prob', 0.5)
                        st.metric("BTTS (Yes)", f"{btts:.1%}", help="양 팀 모두 득점할 확률")
                    
                    with m_col3:
                        dc = prediction.get('double_chance', {})
                        st.metric("Double Chance (1X)", f"{dc.get('1X', 0):.1%}", help="홈팀 승리 또는 무승부")
                        st.metric("Double Chance (X2)", f"{dc.get('X2', 0):.1%}", help="원정팀 승리 또는 무승부")
                    
                    # ========== V4 Advanced Analysis (NEW) ==========
                    st.markdown("#### 🔍 심층 경기 분석 (V4 Engine)")
                    a_col1, a_col2, a_col3 = st.columns(3)
                    
                    with a_col1:
                        state = prediction.get('game_state', 'BALANCED')
                        state_color = "🔴" if state == "OPEN" else "🔵" if state == "CLOSED" else "🟢"
                        st.markdown(f"**경기 템포**\n{state_color} {state}")
                        
                    with a_col2:
                        upset = prediction.get('upset_mode', False)
                        upset_label = "⚠️ HIGH" if upset else "✅ LOW"
                        st.markdown(f"**이변 가능성**\n{upset_label}")
                        
                    with a_col3:
                        conf = prediction.get('confidence', 'medium').upper()
                        st.markdown(f"**예측 신뢰도**\n{conf}")
                        
                    # 베팅 인사이트
                    if 'betting_insight' in prediction:
                        st.info(f"💡 **전문가 분석 제언:** {prediction['betting_insight']}")
            
            # 상세 분석
            st.subheader(t('detailed_analysis'))
            
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                st.write(t('key_factors'))
                if 'key_factors' in prediction:
                    for factor in prediction['key_factors']:
                        st.write(f"• {factor}")
            
            with analysis_col2:
                st.write(t('prediction_confidence'))
                conf_label = prediction.get('confidence', 'medium')
                conf_score = 0.8 if conf_label == 'high' else 0.6 if conf_label == 'medium' else 0.4
                st.progress(conf_score)
                st.write(f"{t('confidence_label')}{conf_label.upper()}")
                
                # V4 Summary Hints
                if 'summary_hints' in prediction:
                    for hint in prediction['summary_hints']:
                        st.caption(f"ℹ️ {hint}")
            
            # 예상 스코어 (기존)
            if not pass_flag and prediction.get('expected_score_home') is not None:
                st.subheader(t('expected_score_basic'))
                
                # 순위 표시 (팀 순위)
                h_rank_str = ""
                a_rank_str = ""
                if 'ranks' in prediction:
                    h_r = prediction['ranks'].get('home_rank', '-')
                    a_r = prediction['ranks'].get('away_rank', '-')
                    if h_r and str(h_r) != '0' and str(h_r) != '-': h_rank_str = f"({h_r}위) "
                    if a_r and str(a_r) != '0' and str(a_r) != '-': a_rank_str = f" ({a_r}위)"
                
                st.write(f"**{h_rank_str}{home_team} {prediction['expected_score_home']} - {prediction['expected_score_away']} {away_team}{a_rank_str}**")
            
            # 상위 5개 가능 스코어 표시
            if 'top_5_scores' in prediction:
                st.write("**가능성 높은 스코어 Top 5:**")
                for i, (score, prob) in enumerate(prediction['top_5_scores'], 1):
                    st.write(f"{i}. {score[0]}:{score[1]} ({prob*100:.1f}%)")
            elif 'top_3_scores' in prediction:
                st.write("**가능성 높은 스코어 Top 3:**")
                for i, (score, prob) in enumerate(prediction['top_3_scores'], 1):
                    st.write(f"{i}. {score[0]}:{score[1]} ({prob*100:.1f}%)")
            
            # ========== 고급 메트릭스 표시 (NEW) ==========
            st.markdown("---")
            
            # 데이터 소스 및 상태 안내 (개선된 UI)
            h_src = home_data.get('data_source', '기본 통계')
            a_src = away_data.get('data_source', '기본 통계')
            
            if home_data.get('is_estimated') or away_data.get('is_estimated'):
                st.warning(f"⚠️ **데이터 안내:** 일부 실시간 지표가 부족하여 **{h_src}** 및 **{a_src}**를 기반으로 분석되었습니다. (정확도 보정 적용)")
            else:
                st.success(f"✅ **데이터 확인:** 현재 분석은 **{h_src}** 및 **{a_src}** 최신 데이터를 엔진에 직접 연결하여 진행 중입니다.")
            
            st.subheader("📊 고급 메트릭스 분석")
            
            # 스포츠별 고급 메트릭스 표시
            if sport == "축구":
                st.markdown("### ⚽ 축구 고급 메트릭스 (xG, xA, PPDA)")
                
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.markdown(f"**{home_team} (홈)**")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    
                    with m_col1:
                        xg_home = home_data.get('team_xg', prediction.get('lambda_home', 0))
                        st.metric("xG (기대 득점)", f"{xg_home:.2f}", 
                                 help="Expected Goals - 슈팅 위치와 상황을 고려한 기대 득점")
                    
                    with m_col2:
                        xa_home = home_data.get('team_xa', 0)
                        st.metric("xA (기대 어시스트)", f"{xa_home:.2f}",
                                 help="Expected Assists - 패스 품질을 고려한 기대 어시스트")
                    
                    with m_col3:
                        ppda_home = home_data.get('ppda', 12.0)
                        st.metric("PPDA (압박 강도)", f"{ppda_home:.1f}",
                                 help="Passes Per Defensive Action - 낮을수록 강한 압박")
                    
                    # 추가 메트릭스
                    if 'team_defensive' in home_data:
                        st.caption(f"수비 기여도: {home_data['team_defensive']:.1f}")
                    if 'advanced_attack_rating' in home_data:
                        st.caption(f"공격력 평가: {home_data['advanced_attack_rating']:.1f}/100")
                    if 'advanced_defense_rating' in home_data:
                        st.caption(f"수비력 평가: {home_data['advanced_defense_rating']:.1f}/100")
                
                with metrics_col2:
                    st.markdown(f"**{away_team} (원정)**")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    
                    with m_col1:
                        xg_away = away_data.get('team_xg', prediction.get('lambda_away', 0))
                        st.metric("xG (기대 득점)", f"{xg_away:.2f}")
                    
                    with m_col2:
                        xa_away = away_data.get('team_xa', 0)
                        st.metric("xA (기대 어시스트)", f"{xa_away:.2f}")
                    
                    with m_col3:
                        ppda_away = away_data.get('ppda', 12.0)
                        st.metric("PPDA (압박 강도)", f"{ppda_away:.1f}")
                    
                    # 추가 메트릭스
                    if 'team_defensive' in away_data:
                        st.caption(f"수비 기여도: {away_data['team_defensive']:.1f}")
                    if 'advanced_attack_rating' in away_data:
                        st.caption(f"공격력 평가: {away_data['advanced_attack_rating']:.1f}/100")
                    if 'advanced_defense_rating' in away_data:
                        st.caption(f"수비력 평가: {away_data['advanced_defense_rating']:.1f}/100")
                
                # xG 비교 차트
                st.markdown("**xG 비교**")
                xg_comparison = pd.DataFrame({
                    '팀': [home_team, away_team],
                    'xG': [xg_home, xg_away]
                })
                st.bar_chart(xg_comparison.set_index('팀'))
            
            elif sport == "야구":
                st.markdown("### ⚾ 야구 고급 메트릭스 (OPS, wOBA, ERA+, FIP)")
                
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.markdown(f"**{home_team} (홈)**")
                    
                    # 타자 메트릭스
                    st.markdown("**타자 지표**")
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        ops_home = home_data.get('avg_ops', 0.750)
                        st.metric("OPS", f"{ops_home:.3f}",
                                 help="On-base Plus Slugging - 출루율 + 장타율")
                    with m_col2:
                        woba_home = home_data.get('avg_woba', 0.330)
                        st.metric("wOBA", f"{woba_home:.3f}",
                                 help="Weighted On-Base Average - 가중 출루율")
                    
                    # 투수 메트릭스
                    st.markdown("**투수 지표**")
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        era_plus_home = home_data.get('avg_era_plus', 100)
                        st.metric("ERA+", f"{era_plus_home:.0f}",
                                 help="Adjusted ERA - 100이 평균, 높을수록 우수")
                    with m_col2:
                        fip_home = home_data.get('avg_fip', 4.00)
                        st.metric("FIP", f"{fip_home:.2f}",
                                 help="Fielding Independent Pitching - 수비 무관 투구 평가")
                    
                    # WAR
                    if 'total_war' in home_data:
                        st.metric("팀 WAR", f"{home_data['total_war']:.1f}",
                                 help="Wins Above Replacement - 대체 선수 대비 승리 기여")
                
                with metrics_col2:
                    st.markdown(f"**{away_team} (원정)**")
                    
                    # 타자 메트릭스
                    st.markdown("**타자 지표**")
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        ops_away = away_data.get('avg_ops', 0.750)
                        st.metric("OPS", f"{ops_away:.3f}")
                    with m_col2:
                        woba_away = away_data.get('avg_woba', 0.330)
                        st.metric("wOBA", f"{woba_away:.3f}")
                    
                    # 투수 메트릭스
                    st.markdown("**투수 지표**")
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        era_plus_away = away_data.get('avg_era_plus', 100)
                        st.metric("ERA+", f"{era_plus_away:.0f}")
                    with m_col2:
                        fip_away = away_data.get('avg_fip', 4.00)
                        st.metric("FIP", f"{fip_away:.2f}")
                    
                    # WAR
                    if 'total_war' in away_data:
                        st.metric("팀 WAR", f"{away_data['total_war']:.1f}")
                
                # OPS 비교 차트
                st.markdown("**OPS 비교**")
                ops_comparison = pd.DataFrame({
                    '팀': [home_team, away_team],
                    'OPS': [ops_home, ops_away]
                })
                st.bar_chart(ops_comparison.set_index('팀'))
            
            elif sport == "배구":
                st.markdown("### 🏐 배구 고급 메트릭스 (스파이크율, 블록, 워크로드)")
                
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.markdown(f"**{home_team} (홈)**")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    
                    with m_col1:
                        spike_rate_home = home_data.get('team_spike_rate', 0.45)
                        st.metric("스파이크 성공률", f"{spike_rate_home:.1%}",
                                 help="(킬 - 에러) / 총 시도")
                    
                    with m_col2:
                        block_eff_home = home_data.get('team_block_eff', 2.5)
                        st.metric("블록 효율", f"{block_eff_home:.1f}",
                                 help="세트당 블록 포인트")
                    
                    with m_col3:
                        dig_eff_home = home_data.get('team_dig_eff', 12.0)
                        st.metric("디그 효율", f"{dig_eff_home:.1f}",
                                 help="세트당 디그 수")
                    
                    # 추가 메트릭스
                    if 'team_set_eff' in home_data:
                        st.caption(f"세트 효율: {home_data['team_set_eff']:.1%}")
                    if 'team_fatigue' in home_data:
                        fatigue_pct = (1 - home_data['team_fatigue']) * 100
                        st.caption(f"피로도: {fatigue_pct:.0f}%")
                    if 'advanced_attack_rating' in home_data:
                        st.caption(f"공격력: {home_data['advanced_attack_rating']:.1f}/100")
                
                with metrics_col2:
                    st.markdown(f"**{away_team} (원정)**")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    
                    with m_col1:
                        spike_rate_away = away_data.get('team_spike_rate', 0.45)
                        st.metric("스파이크 성공률", f"{spike_rate_away:.1%}")
                    
                    with m_col2:
                        block_eff_away = away_data.get('team_block_eff', 2.5)
                        st.metric("블록 효율", f"{block_eff_away:.1f}")
                    
                    with m_col3:
                        dig_eff_away = away_data.get('team_dig_eff', 12.0)
                        st.metric("디그 효율", f"{dig_eff_away:.1f}")
                    
                    # 추가 메트릭스
                    if 'team_set_eff' in away_data:
                        st.caption(f"세트 효율: {away_data['team_set_eff']:.1%}")
                    if 'team_fatigue' in away_data:
                        fatigue_pct = (1 - away_data['team_fatigue']) * 100
                        st.caption(f"피로도: {fatigue_pct:.0f}%")
                    if 'advanced_attack_rating' in away_data:
                        st.caption(f"공격력: {away_data['advanced_attack_rating']:.1f}/100")
                
                # 스파이크 성공률 비교 차트
                st.markdown("**스파이크 성공률 비교**")
                spike_comparison = pd.DataFrame({
                    '팀': [home_team, away_team],
                    '성공률': [spike_rate_home * 100, spike_rate_away * 100]
                })
                st.bar_chart(spike_comparison.set_index('팀'))
            
            elif sport == "농구":
                st.markdown("### 🏀 농구 고급 메트릭스 (PER, Win Shares, BPM)")
                
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.markdown(f"**{home_team} (홈)**")
                    
                    # 팀 평균 고급 메트릭스
                    if 'avg_per' in home_data:
                        m_col1, m_col2, m_col3 = st.columns(3)
                        with m_col1:
                            st.metric("평균 PER", f"{home_data['avg_per']:.1f}",
                                     help="Player Efficiency Rating - 15가 평균")
                        with m_col2:
                            st.metric("평균 WS", f"{home_data['avg_ws']:.1f}",
                                     help="Win Shares - 승리 기여도")
                        with m_col3:
                            st.metric("평균 BPM", f"{home_data['avg_bpm']:.1f}",
                                     help="Box Plus-Minus - 출전 시 득실차")
                    
                    # 기본 통계
                    st.caption(f"평균 득점: {home_data.get('ppg', 0):.1f}")
                    st.caption(f"평균 실점: {home_data.get('opp_ppg', 0):.1f}")
                
                with metrics_col2:
                    st.markdown(f"**{away_team} (원정)**")
                    
                    # 팀 평균 고급 메트릭스
                    if 'avg_per' in away_data:
                        m_col1, m_col2, m_col3 = st.columns(3)
                        with m_col1:
                            st.metric("평균 PER", f"{away_data['avg_per']:.1f}")
                        with m_col2:
                            st.metric("평균 WS", f"{away_data['avg_ws']:.1f}")
                        with m_col3:
                            st.metric("평균 BPM", f"{away_data['avg_bpm']:.1f}")
                    
                    # 기본 통계
                    st.caption(f"평균 득점: {away_data.get('ppg', 0):.1f}")
                    st.caption(f"평균 실점: {away_data.get('opp_ppg', 0):.1f}")
            
            # 메트릭스 설명
            with st.expander("📖 고급 메트릭스 설명", expanded=False):
                if sport == "축구":
                    st.markdown("""
                    **xG (Expected Goals)**: 슈팅 위치, 각도, 상황을 고려한 기대 득점. 실제 득점보다 팀의 공격 능력을 정확하게 반영합니다.
                    
                    **xA (Expected Assists)**: 패스 품질을 고려한 기대 어시스트. 패스가 득점으로 이어질 확률을 측정합니다.
                    
                    **PPDA (Passes Per Defensive Action)**: 상대의 패스 수 / 우리의 수비 액션. 낮을수록 강한 압박을 의미합니다.
                    """)
                elif sport == "야구":
                    st.markdown("""
                    **OPS (On-base Plus Slugging)**: 출루율 + 장타율. 타자의 종합 능력을 나타냅니다. (0.800+ 우수)
                    
                    **wOBA (Weighted On-Base Average)**: 각 결과에 가중치를 부여한 출루율. OPS보다 정확한 타격 평가 지표입니다.
                    
                    **ERA+ (Adjusted ERA)**: 리그 평균 대비 조정된 평균자책점. 100이 평균, 높을수록 우수합니다.
                    
                    **FIP (Fielding Independent Pitching)**: 수비와 무관한 투수 능력 평가. 홈런, 볼넷, 삼진만으로 계산합니다.
                    
                    **WAR (Wins Above Replacement)**: 대체 선수 대비 승리 기여도. 선수의 종합 가치를 나타냅니다.
                    """)
                elif sport == "배구":
                    st.markdown("""
                    **스파이크 성공률**: (킬 - 에러) / 총 시도. 공격 효율을 나타냅니다.
                    
                    **블록 효율**: 세트당 블록 포인트 (솔로 블록 = 1점, 어시스트 = 0.5점). 수비 능력을 측정합니다.
                    
                    **디그 효율**: 세트당 디그 수. 수비 범위와 반응 속도를 나타냅니다.
                    
                    **피로도**: 점프 워크로드와 이동 워크로드를 기반으로 계산. 높을수록 선수들이 피곤한 상태입니다.
                    """)
                elif sport == "농구":
                    st.markdown("""
                    **PER (Player Efficiency Rating)**: 1분당 생산성 측정. 15가 리그 평균입니다.
                    
                    **Win Shares (WS)**: 승리에 기여한 점수화. 공격/수비 기여도를 종합합니다.
                    
                    **BPM (Box Plus-Minus)**: 출전 시 득실차 조정. 선수의 영향력을 측정합니다.
                    """)
            
            st.markdown("---")
            # ========== 고급 메트릭스 표시 끝 ==========
            
            # 기대 득점 λ 표시 (디버깅/분석용)
            if 'lambda_home' in prediction and 'lambda_away' in prediction:
                st.caption(f"기대 득점: 홈 λ={prediction['lambda_home']}, 원정 λ={prediction['lambda_away']}, 상관 λ_C={prediction.get('lambda_c', 0)}")
            
            try:
                if pass_flag:
                    st.info("전문 분석 모델이 현재 경기를 PASS로 판정하여 상세 점수 예측을 제공하지 않습니다.")
                else:
                    st.subheader(t('detailed_score_prediction_title'))
                    
                    # NBA의 경우 NBAPredictor의 결과를 전용 소스로 사용 (데이터 정합성 강제)
                    if sport == "농구" and "NBA" in prediction_league:
                        score_prediction = {
                            'home_score': prediction.get('expected_score_home', 0),
                            'away_score': prediction.get('expected_score_away', 0),
                            'home_win_probability': int(round(prediction.get('win_probability', {}).get('home', 0.5) * 100)),
                            'away_win_probability': int(round(prediction.get('win_probability', {}).get('away', 0.5) * 100)),
                            'spread_probability': prediction.get('spread_probability'),
                            'over_under_probability': prediction.get('over_under_probability'),
                            'prediction': prediction.get('prediction'),
                            'confidence': prediction.get('confidence', '중간'),
                            'key_factors': prediction.get('key_factors', []),
                            'total_points': prediction.get('expected_score_home', 0) + prediction.get('expected_score_away', 0),
                            'spread': abs(prediction.get('expected_score_home', 0) - prediction.get('expected_score_away', 0)),
                            'model_type': prediction.get('model_type', 'NBA V2.6 MC Engine'),
                            'sport_type': 'basketball'
                        }
                    else:
                        score_prediction = score_predictor.predict_match_score(
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
                            st.write(t('expected_total_points') + f" {score_prediction.get('total_points', score_prediction['home_score'] + score_prediction['away_score'])}" + t('points_unit'))
                            st.write(t('score_difference_label') + f" {abs(score_prediction.get('spread', score_prediction['home_score'] - score_prediction['away_score']))}" + t('points_unit'))
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
            # 강력한 캐시 초기화 - session_state의 collector_cache 자체를 초기화
            if 'collector_cache' in st.session_state:
                # 모든 collector의 캐시 초기화
                for collector_instance in st.session_state.collector_cache.values():
                    collector_instance.clear_cache()
                # session_state의 collector_cache 자체를 초기화
                st.session_state.collector_cache = {}
                print("[OK] All DataCollector instances and caches cleared")
            st.success(t('roster_cache_cleared'))
            st.rerun()
    
    players = get_players_nba(team_for_players)
    
    def has_valid_players(players_list):
        return isinstance(players_list, list) and len(players_list) > 0

    def should_show_player_dropdown(current_league, players_list):
        if current_league == "MLS":
            return False
        return has_valid_players(players_list)

    def get_player_options(players_list):
        if not has_valid_players(players_list):
            return []
        return players_list

    # Debug Logging (REQUIRED)
    print("League:", league)
    print("Players count:", len(players) if players else 0)
    
    if not should_show_player_dropdown(league, players):
        st.info("No player data available")
    else:
        safe_options = get_player_options(players)
        selected_player = st.selectbox(t('select_player'), safe_options)
        
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
        
        st.info("[FETCH] 실시간 경기 일정 API 사용 중 (ESPN API)")
        
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
                st.warning(f"[WARNING] {schedule_league} 리그의 실시간 일정을 가져올 수 없습니다.")
        
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
                st.success(f"[OK] {schedule_team}의 다음 {len(team_matches)}경기")
                
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
                st.warning(f"[WARNING] {schedule_team}의 실시간 일정을 가져올 수 없습니다.")
    
    except ImportError as e:
        st.error(f"[ERROR] 경기 일정 모듈을 불러올 수 없습니다: {e}")
    except Exception as e:
        st.error(f"[ERROR] 오류 발생: {str(e)}")

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
                        st.success(f"[OK] {selected_team} 팀에는 현재 부상 선수가 없습니다!")
                
                # 선수별 검색
                st.subheader(t('player_injury_search'))
                
                player_search = st.text_input(t('enter_player_name'), placeholder=t('example_prefix') + ('LeBron James' if injury_league == 'NBA' else 'Shohei Ohtani' if injury_league == 'MLB' else '양현종' if injury_league == 'KBO' else 'Kevin De Bruyne'))
                
                if player_search:
                    player_injury = injury_fetcher.get_player_status(player_search)
                    
                    if player_injury:
                        st.warning(f"[WARNING] {player_search}는 현재 부상 상태입니다.")
                        
                        col_p1, col_p2 = st.columns(2)
                        
                        with col_p1:
                            st.write(f"**포지션:** {player_injury['position']}")
                            st.write(f"**상태:** {player_injury['status']}")
                        
                        with col_p2:
                            st.write(f"**부상:** {player_injury['description']}")
                            st.write(f"**예상 복귀:** {player_injury['date']}")
                    else:
                        st.success(f"[OK] {player_search}는 현재 건강한 상태입니다!")
                
            except Exception as e:
                st.error(f"[ERROR] 부상 정보를 가져오는 중 오류가 발생했습니다: {e}")
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
                        st.warning(f"[WARNING] {selected_team}" + t('coaching_staff_not_found'))
                
                # 감독 검색
                st.subheader(t('coach_search_title'))
                
                coach_search = st.text_input(t('enter_coach_name'), placeholder=t('example_prefix') + ('Steve Kerr' if coaching_league == 'NBA' else 'Aaron Boone' if coaching_league == 'MLB' else '김종국' if coaching_league == 'KBO' else 'Pep Guardiola'))
                
                if coach_search:
                    found_teams = []
                    for team_name, staff in all_coaching.items():
                        if coach_search.lower() in staff['head_coach'].lower():
                            found_teams.append((team_name, staff))
                    
                    if found_teams:
                        st.success(f"[OK] {len(found_teams)}" + t('found_in_teams') + coach_search + t('found_text'))
                        
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
                        st.warning(f"[WARNING] '{coach_search}'" + t('not_found_text'))
                
            except Exception as e:
                st.error(f"[ERROR] 코칭스태프 정보를 가져오는 중 오류가 발생했습니다: {e}")

with tab7:
    st.header("📢 공지사항")
    
    # 커뮤니티 DB 초기화
    community_db = get_community_database()
    
    # 관리자 모드 (간단한 비밀번호 체크)
    if 'admin_mode' not in st.session_state:
        st.session_state.admin_mode = False
    
    # 관리자 로그인 (URL 파라미터 ?admin=true 일 때만 노출)
    is_admin_url = st.query_params.get("admin", "") == "true"
    
    if is_admin_url or st.session_state.admin_mode:
        with st.sidebar:
            st.markdown("---")
            st.subheader("🔐 관리자 모드")
            
            if not st.session_state.admin_mode:
                admin_password = st.text_input("관리자 비밀번호", type="password", key="admin_pw")
                if st.button("로그인", key="admin_login"):
                    # Use st.secrets for production, fallback to default for local
                    secure_password = st.secrets.get("ADMIN_PASSWORD", "admin1234")
                    if admin_password == secure_password:
                        st.session_state.admin_mode = True
                        st.success("관리자 로그인 성공!")
                        st.rerun()
                    else:
                        st.error("비밀번호가 틀렸습니다.")
            
            if st.session_state.admin_mode:
                st.success("[OK] 관리자 모드 활성화됨")
                if st.button("로그아웃", key="admin_logout"):
                    st.session_state.admin_mode = False
                    if "admin" in st.query_params:
                        del st.query_params["admin"]
                    st.rerun()
    
    # 관리자 - 공지사항 작성
    if st.session_state.admin_mode:
        with st.expander("✍️ 새 공지사항 작성", expanded=False):
            new_title = st.text_input("제목", key="new_announcement_title")
            new_content = st.text_area("내용", height=200, key="new_announcement_content")
            
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                is_important = st.checkbox("중요 공지", key="new_announcement_important")
            with col_a2:
                is_pinned = st.checkbox("상단 고정", key="new_announcement_pinned")
            
            if st.button("공지사항 등록", type="primary", key="create_announcement"):
                if new_title and new_content:
                    announcement_id = community_db.create_announcement(
                        title=new_title,
                        content=new_content,
                        is_important=is_important,
                        is_pinned=is_pinned
                    )
                    st.success(f"[OK] 공지사항이 등록되었습니다! (ID: {announcement_id})")
                    st.rerun()
                else:
                    st.error("제목과 내용을 모두 입력해주세요.")
    
    # 공지사항 목록
    st.markdown("---")
    announcements = community_db.get_announcements(limit=20)
    
    if not announcements:
        st.info("📭 등록된 공지사항이 없습니다.")
    else:
        for announcement in announcements:
            # 공지사항 카드
            importance_badge = "🔴 중요" if announcement['is_important'] else ""
            pinned_badge = "📌 고정" if announcement['is_pinned'] else ""
            badges = f"{pinned_badge} {importance_badge}".strip()
            
            with st.expander(
                f"{badges} {announcement['title']} (조회: {announcement['views']})",
                expanded=announcement['is_pinned']
            ):
                st.markdown(f"**작성자**: {announcement['author']}")
                st.caption(f"작성일: {announcement['created_at']}")
                st.markdown("---")
                st.markdown(announcement['content'])
                
                # 관리자 - 수정/삭제
                if st.session_state.admin_mode:
                    st.markdown("---")
                    col_edit1, col_edit2 = st.columns(2)
                    
                    with col_edit1:
                        if st.button("수정", key=f"edit_announcement_{announcement['id']}"):
                            st.session_state[f'editing_announcement_{announcement["id"]}'] = True
                    
                    with col_edit2:
                        if st.button("삭제", key=f"delete_announcement_{announcement['id']}"):
                            community_db.delete_announcement(announcement['id'])
                            st.success("삭제되었습니다.")
                            st.rerun()
                    
                    # 수정 폼
                    if st.session_state.get(f'editing_announcement_{announcement["id"]}', False):
                        edit_title = st.text_input("제목", value=announcement['title'], key=f"edit_title_{announcement['id']}")
                        edit_content = st.text_area("내용", value=announcement['content'], height=200, key=f"edit_content_{announcement['id']}")
                        
                        if st.button("저장", key=f"save_announcement_{announcement['id']}"):
                            community_db.update_announcement(
                                announcement['id'],
                                title=edit_title,
                                content=edit_content
                            )
                            st.session_state[f'editing_announcement_{announcement["id"]}'] = False
                            st.success("수정되었습니다.")
                            st.rerun()

with tab8:
    st.header("💼 비즈니스 및 광고 문의")
    
    community_db = get_community_database()
    
    # 관리자 모드가 아닌 경우 - 문의 제출 및 조회
    if not st.session_state.get('admin_mode', False):
        # 탭으로 문의 제출과 조회 분리
        inquiry_tab1, inquiry_tab2 = st.tabs(["📝 문의 제출", "[SEARCH] 문의 조회"])
        
        with inquiry_tab1:
            st.markdown("""
            ### 광고 및 스폰서십 문의
            
            VIBE BOX Sports MatchSignal은 스포츠 예측 플랫폼으로 많은 스포츠 팬들이 방문합니다.
            
            **광고 상품**:
            - 🎯 배너 광고 (사이드바, 메인 페이지)
            - 📊 데이터 스폰서십
            - 🤝 파트너십 프로그램
            
            아래 양식을 작성해주시면 빠른 시일 내에 답변드리겠습니다.
            """)
            
            st.markdown("---")
            
            # 문의 유형 선택
            inquiry_type = st.selectbox(
                "문의 유형",
                ["광고 문의", "스폰서십 문의", "데이터 제휴", "기타 비즈니스 문의"]
            )
            
            # 문의 폼
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                company_name = st.text_input("회사명 (선택)")
                contact_name = st.text_input("담당자명 *")
                email = st.text_input("이메일 *")
            
            with col_b2:
                phone = st.text_input("연락처 (선택)")
                subject = st.text_input("제목 *")
            
            message = st.text_area("문의 내용 *", height=200, placeholder="문의하실 내용을 자세히 작성해주세요.")
            
            # 개인정보 동의
            privacy_agree = st.checkbox("개인정보 수집 및 이용에 동의합니다.")
            
            if st.button("문의 제출", type="primary", use_container_width=True):
                if not contact_name or not email or not subject or not message:
                    st.error("[ERROR] 필수 항목(*)을 모두 입력해주세요.")
                elif not privacy_agree:
                    st.error("[ERROR] 개인정보 수집 및 이용에 동의해주세요.")
                else:
                    inquiry_id = community_db.create_business_inquiry(
                        inquiry_type=inquiry_type,
                        company_name=company_name,
                        contact_name=contact_name,
                        email=email,
                        phone=phone,
                        subject=subject,
                        message=message
                    )
                    
                    st.success(f"""
                    [OK] 문의가 성공적으로 접수되었습니다!
                    
                    **접수번호**: {inquiry_id}
                    
                    접수번호와 이메일을 이용하여 '문의 조회' 탭에서 답변을 확인하실 수 있습니다.
                    빠른 시일 내에 {email}로 답변드리겠습니다.
                    """)
        
        with inquiry_tab2:
            st.markdown("""
            ### 문의 내역 조회
            
            접수번호와 이메일을 입력하여 문의 내역과 답변을 확인하실 수 있습니다.
            """)
            
            st.markdown("---")
            
            col_lookup1, col_lookup2 = st.columns(2)
            
            with col_lookup1:
                lookup_id = st.number_input("접수번호", min_value=1, step=1, key="lookup_inquiry_id")
            
            with col_lookup2:
                lookup_email = st.text_input("이메일", key="lookup_inquiry_email")
            
            if st.button("조회하기", type="primary", use_container_width=True):
                if not lookup_id or not lookup_email:
                    st.error("[ERROR] 접수번호와 이메일을 모두 입력해주세요.")
                else:
                    inquiry = community_db.get_business_inquiry_by_credentials(lookup_id, lookup_email)
                    
                    if not inquiry:
                        st.error("[ERROR] 해당 접수번호와 이메일로 등록된 문의를 찾을 수 없습니다.")
                    else:
                        status_badge = "🟡 대기중" if inquiry['status'] == 'pending' else "🟢 답변완료"
                        
                        st.success(f"[OK] 문의 내역을 찾았습니다. {status_badge}")
                        
                        st.markdown("---")
                        
                        col_i1, col_i2 = st.columns(2)
                        
                        with col_i1:
                            st.markdown(f"**문의 유형**: {inquiry['inquiry_type']}")
                            st.markdown(f"**회사**: {inquiry['company_name'] or 'N/A'}")
                            st.markdown(f"**담당자**: {inquiry['contact_name']}")
                            st.markdown(f"**이메일**: {inquiry['email']}")
                        
                        with col_i2:
                            st.markdown(f"**연락처**: {inquiry['phone'] or 'N/A'}")
                            st.markdown(f"**접수일**: {inquiry['created_at']}")
                            st.markdown(f"**상태**: {status_badge}")
                        
                        st.markdown("---")
                        st.markdown(f"**제목**: {inquiry['subject']}")
                        st.markdown("**문의 내용**:")
                        st.text(inquiry['message'])
                        
                        if inquiry['admin_reply']:
                            st.markdown("---")
                            st.success("**답변**:")
                            st.markdown(inquiry['admin_reply'])
                            st.caption(f"답변일: {inquiry['replied_at']}")
                        else:
                            st.info("답변 대기 중입니다. 빠른 시일 내에 답변드리겠습니다.")
    
    # 관리자 모드 - 문의 관리
    else:
        st.markdown("---")
        st.subheader("📋 문의 관리 (관리자)")
        
        status_filter = st.selectbox("상태 필터", ["전체", "대기중", "답변완료"], key="inquiry_status_filter")
        
        status_map = {"전체": None, "대기중": "pending", "답변완료": "replied"}
        inquiries = community_db.get_business_inquiries(status=status_map[status_filter], limit=50)
        
        if not inquiries:
            st.info("문의가 없습니다.")
        else:
            for inquiry in inquiries:
                status_badge = "🟡 대기중" if inquiry['status'] == 'pending' else "🟢 답변완료"
                
                with st.expander(f"{status_badge} [{inquiry['inquiry_type']}] {inquiry['subject']} (접수번호: {inquiry['id']})"):
                    col_i1, col_i2 = st.columns(2)
                    
                    with col_i1:
                        st.markdown(f"**회사**: {inquiry['company_name'] or 'N/A'}")
                        st.markdown(f"**담당자**: {inquiry['contact_name']}")
                        st.markdown(f"**이메일**: {inquiry['email']}")
                    
                    with col_i2:
                        st.markdown(f"**연락처**: {inquiry['phone'] or 'N/A'}")
                        st.markdown(f"**접수일**: {inquiry['created_at']}")
                        st.markdown(f"**접수번호**: {inquiry['id']}")
                    
                    st.markdown("---")
                    st.markdown("**문의 내용**:")
                    st.text(inquiry['message'])
                    
                    if inquiry['admin_reply']:
                        st.markdown("---")
                        st.success(f"**답변**: {inquiry['admin_reply']}")
                        st.caption(f"답변일: {inquiry['replied_at']}")
                    else:
                        st.markdown("---")
                        admin_reply = st.text_area("답변 작성", key=f"reply_{inquiry['id']}")
                        if st.button("답변 전송", key=f"send_reply_{inquiry['id']}"):
                            community_db.reply_business_inquiry(inquiry['id'], admin_reply)
                            st.success("답변이 전송되었습니다.")
                            st.rerun()

with tab9:
    st.header("💬 커뮤니티 게시판")
    
    community_db = get_community_database()
    
    # 카테고리 선택
    categories = ["전체", "자유게시판", "예측 토론", "팀 분석", "선수 분석", "질문/답변"]
    selected_category = st.selectbox("카테고리", categories, key="board_category")
    
    # 검색
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_keyword = st.text_input("[SEARCH] 검색", placeholder="제목 또는 내용 검색", key="board_search")
    with col_s2:
        st.write("")
        st.write("")
        if st.button("검색", key="board_search_btn"):
            if search_keyword:
                st.session_state.search_results = community_db.search_posts(
                    keyword=search_keyword,
                    category=None if selected_category == "전체" else selected_category
                )
    
    # 글쓰기 버튼
    if st.button("✍️ 글쓰기", key="write_post_btn"):
        st.session_state.writing_post = True
    
    # 글쓰기 폼
    if st.session_state.get('writing_post', False):
        with st.form("new_post_form"):
            st.subheader("새 게시글 작성")
            
            post_category = st.selectbox("카테고리", categories[1:], key="new_post_category")
            post_title = st.text_input("제목 *", key="new_post_title")
            post_content = st.text_area("내용 *", height=300, key="new_post_content")
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                post_author = st.text_input("작성자 *", key="new_post_author")
            with col_p2:
                post_password = st.text_input("비밀번호 * (수정/삭제용)", type="password", key="new_post_password")
            
            submitted = st.form_submit_button("게시글 등록", type="primary")
            
            if submitted:
                if not post_title or not post_content or not post_author or not post_password:
                    st.error("모든 필수 항목을 입력해주세요.")
                else:
                    post_id = community_db.create_post(
                        category=post_category,
                        title=post_title,
                        content=post_content,
                        author=post_author,
                        password=post_password
                    )
                    st.success(f"[OK] 게시글이 등록되었습니다! (ID: {post_id})")
                    st.session_state.writing_post = False
                    st.rerun()
    
    st.markdown("---")
    
    # 게시글 목록
    if st.session_state.get('search_results'):
        posts = st.session_state.search_results
        st.info(f"[SEARCH] 검색 결과: {len(posts)}개")
    else:
        posts = community_db.get_posts(
            category=None if selected_category == "전체" else selected_category,
            limit=20
        )
    
    if not posts:
        st.info("📭 게시글이 없습니다.")
    else:
        for post in posts:
            # 게시글 카드
            col_post1, col_post2, col_post3 = st.columns([6, 2, 2])
            
            with col_post1:
                notice_badge = "📌 " if post['is_notice'] else ""
                if st.button(
                    f"{notice_badge}[{post['category']}] {post['title']}",
                    key=f"post_{post['id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_post_id = post['id']
            
            with col_post2:
                st.caption(f"👤 {post['author']}")
            
            with col_post3:
                st.caption(f"👁️ {post['views']} 💬 {post['comment_count']} 👍 {post['likes']}")
    
    # 게시글 상세보기
    if st.session_state.get('selected_post_id'):
        st.markdown("---")
        post = community_db.get_post(st.session_state.selected_post_id)
        
        if post:
            st.subheader(f"[{post['category']}] {post['title']}")
            
            col_detail1, col_detail2 = st.columns([3, 1])
            with col_detail1:
                st.caption(f"작성자: {post['author']} | 작성일: {post['created_at']}")
            with col_detail2:
                st.caption(f"조회: {post['views']} | 좋아요: {post['likes']}")
            
            st.markdown("---")
            st.markdown(post['content'])
            st.markdown("---")
            
            # 좋아요 버튼
            col_like1, col_like2, col_like3 = st.columns([1, 1, 8])
            with col_like1:
                if st.button("👍 좋아요", key=f"like_post_{post['id']}"):
                    if community_db.add_like('post', post['id'], 'user_ip_placeholder'):
                        st.success("좋아요!")
                        st.rerun()
                    else:
                        st.warning("이미 좋아요를 눌렀습니다.")
            
            with col_like2:
                if st.button("🔙 목록", key="back_to_list"):
                    st.session_state.selected_post_id = None
                    st.rerun()
            
            # 댓글 섹션
            st.markdown("---")
            st.subheader(f"💬 댓글 ({len(community_db.get_comments(post['id']))})")
            
            # 댓글 작성
            with st.form(f"comment_form_{post['id']}"):
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    comment_author = st.text_input("작성자", key=f"comment_author_{post['id']}")
                with col_c2:
                    comment_password = st.text_input("비밀번호", type="password", key=f"comment_password_{post['id']}")
                
                comment_content = st.text_area("댓글 내용", key=f"comment_content_{post['id']}")
                
                if st.form_submit_button("댓글 작성"):
                    if comment_author and comment_password and comment_content:
                        comment_id = community_db.create_comment(
                            post_id=post['id'],
                            author=comment_author,
                            content=comment_content,
                            password=comment_password
                        )
                        st.success("댓글이 작성되었습니다!")
                        st.rerun()
                    else:
                        st.error("모든 항목을 입력해주세요.")
            
            # 댓글 목록
            comments = community_db.get_comments(post['id'])
            
            for comment in comments:
                indent = "　　" if comment['parent_comment_id'] else ""
                reply_icon = "↳ " if comment['parent_comment_id'] else ""
                
                with st.container():
                    col_cm1, col_cm2 = st.columns([5, 1])
                    
                    with col_cm1:
                        st.markdown(f"{indent}{reply_icon}**{comment['author']}** | {comment['created_at']}")
                        st.markdown(f"{indent}{comment['content']}")
                    
                    with col_cm2:
                        if st.button("👍", key=f"like_comment_{comment['id']}"):
                            community_db.add_like('comment', comment['id'], 'user_ip_placeholder')
                            st.rerun()
                        st.caption(f"{comment['likes']}")
                    
                    st.markdown("---")

with tab10:
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

# SEO 최적화 키워드 섹션 (검색 엔진 점수 향상용)
st.markdown("""
<div style='text-align: center; color: #4a4a4a; font-size: 0.75rem; margin-top: 50px; padding: 20px; border-top: 1px solid #2a2a2a;'>
    <p style='margin-bottom: 5px;'><b>VIBE BOX Sports MatchSignal - 프리미엄 AI 스포츠분석 및 경기 예측 서비스</b></p>
    <p style='margin-bottom: 5px;'>분석 종목: 해외축구(EPL, 라리가, 분데스리가), 농구(NBA, KBL), 야구(MLB), 배구(V-리그)</p>
    <p style='margin-bottom: 5px;'>핵심 기술: 실시간 ESPN API 연동, Bivariate Poisson 시뮬레이션, Gradient Boosting 확률 보정, AI 딥러닝 예측 엔진</p>
    <p>전문 키워드: 스포츠분석기, 승무패 예측, AI 스포츠 데이터, 실시간 경기 분석, 매치시그널 전문가용 분석 도구</p>
</div>
""", unsafe_allow_html=True)

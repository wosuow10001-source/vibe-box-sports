# ⚡ VIBE BOX Sports MatchSignal

AI 기반 스포츠 경기 예측 플랫폼 - 실시간 데이터와 고급 메트릭스로 정확한 예측을 제공합니다.

## 🎯 주요 기능

### 1. 🔮 경기 예측
- **다중 스포츠 지원**: 축구, 야구, 농구, 배구
- **실시간 데이터**: 선수 통계, 부상 리포트, 경기 일정 자동 업데이트
- **고급 메트릭스**: xG, OPS, PER, 스파이크율 등 스포츠별 전문 지표
- **AI 예측 모델**: Poisson, Negative Binomial, Markov Chain 기반
- **상세 분석**: 승률, 예상 스코어, 주요 영향 요인, 신뢰도

### 2. 📊 고급 메트릭스

#### ⚽ 축구
- **xG (Expected Goals)**: 슈팅 위치와 상황을 고려한 기대 득점
- **xA (Expected Assists)**: 패스 품질 기반 기대 어시스트
- **PPDA**: 압박 강도 측정 (낮을수록 강한 압박)
- **Poisson 모델**: 득점 상관을 반영한 확률 분포

#### ⚾ 야구
- **OPS**: 출루율 + 장타율 (타자 종합 능력)
- **wOBA**: 가중 출루율 (정확한 타격 평가)
- **ERA+**: 조정 평균자책점 (100이 평균)
- **FIP**: 수비 무관 투구 평가
- **WAR**: 대체 선수 대비 승리 기여도

#### 🏀 농구
- **PER**: 1분당 생산성 (15가 평균)
- **Win Shares**: 승리 기여도
- **BPM**: 출전 시 득실차 조정
- **선수 능력치**: 실제 선수 데이터 반영

#### 🏐 배구
- **스파이크 성공률**: (킬 - 에러) / 총 시도
- **블록 효율**: 세트당 블록 포인트
- **디그 효율**: 세트당 디그 수
- **워크로드**: 점프 및 이동 피로도

### 3. 💬 커뮤니티 시스템

#### 📢 공지사항
- 관리자 공지사항 게시
- 중요 공지 및 상단 고정 기능
- 조회수 자동 집계

#### 💼 비즈니스 문의
- 광고 및 스폰서십 문의
- 데이터 제휴 문의
- 문의 접수 및 답변 시스템
- 상태 관리 (대기중/답변완료)
- 🔒 프라이버시 보호: 접수번호 + 이메일 인증으로 본인만 조회 가능

#### 💬 게시판
- 카테고리별 게시판 (자유, 예측 토론, 팀/선수 분석, Q&A)
- 댓글 및 대댓글 시스템
- 좋아요 기능 (중복 방지)
- 검색 기능
- 비밀번호 보호 (수정/삭제)

### 4. 🔄 실시간 데이터 시스템

#### 자동 업데이트
- **선수 통계**: 매일 오전 6시
- **부상 리포트**: 매 시간
- **경기 일정**: 매일 오전 7시
- **경기 당일**: 30분마다 업데이트

#### 데이터 소스
- **NBA**: Basketball-Reference, NBA.com
- **KBL**: KBL 공식 홈페이지
- **K-League**: Statiz, K-League 데이터 포털
- **KBO**: Statiz, KBO 공식 홈페이지
- **V-League**: KOVO

## 🚀 설치 및 실행

### 1. 필수 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 커뮤니티 데이터베이스 초기화

```bash
python scripts/init_community.py
```

### 4. 실시간 데이터 업데이트 시작 (선택)

```bash
python scripts/start_data_updater.py
```

### 5. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 열립니다 (기본: http://localhost:8501)

## 📁 프로젝트 구조

```
.
├── app.py                              # 메인 애플리케이션
├── app_multilang.py                    # 다국어 버전
├── requirements.txt                    # 필수 패키지
├── COMMUNITY_GUIDE.md                  # 커뮤니티 가이드
│
├── modules/                            # 핵심 모듈
│   ├── data_collector.py              # 데이터 수집
│   ├── sport_router.py                # 스포츠별 라우팅
│   ├── analyzer.py                    # 분석 모듈
│   ├── score_predictor.py             # 점수 예측
│   │
│   ├── predictor_soccer.py            # 축구 예측 (Poisson)
│   ├── predictor_baseball.py          # 야구 예측 (Negative Binomial)
│   ├── predictor_basketball_*.py      # 농구 예측
│   ├── predictor_volleyball.py        # 배구 예측 (Markov Chain)
│   │
│   ├── advanced_soccer_metrics.py     # 축구 고급 메트릭스
│   ├── advanced_baseball_metrics.py   # 야구 고급 메트릭스
│   ├── advanced_volleyball_metrics.py # 배구 고급 메트릭스
│   ├── advanced_player_metrics.py     # 농구 고급 메트릭스
│   │
│   ├── realtime_data_fetcher.py       # 실시간 데이터 수집
│   ├── player_stats_database.py       # 선수 통계 DB
│   ├── data_update_scheduler.py       # 자동 업데이트
│   │
│   ├── community_database.py          # 커뮤니티 DB
│   ├── injury_fetcher.py              # 부상 정보
│   ├── coaching_staff_fetcher.py      # 코칭스태프 정보
│   └── translator.py                  # 다국어 지원
│
├── data/                               # 데이터 저장소
│   ├── players_2026.py                # 선수 데이터
│   ├── real_data_2026.py              # 실제 경기 데이터
│   ├── *_rosters_*.py                 # 로스터 데이터
│   ├── player_stats.db                # 선수 통계 DB
│   └── community.db                   # 커뮤니티 DB
│
├── scripts/                            # 유틸리티 스크립트
│   ├── init_community.py              # 커뮤니티 초기화
│   ├── start_data_updater.py          # 데이터 업데이트 시작
│   ├── manual_update.py               # 수동 업데이트
│   └── daily_update.py                # 일일 업데이트
│
└── examples/                           # 사용 예시
    └── advanced_metrics_usage.py      # 고급 메트릭스 사용법
```

## 🎮 사용 방법

### 1. 경기 예측

1. 사이드바에서 스포츠 및 리그 선택
2. 홈팀과 원정팀 선택
3. 경기 조건 입력 (날씨, 온도, 경기장 상태 등)
4. "예측 실행" 버튼 클릭
5. 결과 확인:
   - 승/무/패 확률
   - 예상 스코어
   - 고급 메트릭스 분석
   - 주요 영향 요인
   - 예측 신뢰도

### 2. 팀 분석

1. "팀 분석" 탭 선택
2. 분석할 팀 선택
3. "팀 분석 실행" 클릭
4. 결과 확인:
   - 최근 폼 차트
   - 강점/약점
   - 코칭스태프 정보

### 3. 선수 분석

1. "선수 분석" 탭 선택
2. 팀 선택 후 선수 선택
3. "선수 분석 실행" 클릭
4. 결과 확인:
   - 컨디션 지수
   - 최근 평점
   - 부상 위험도
   - 성적 추이

### 4. 커뮤니티 이용

#### 공지사항 확인
- "📢 공지사항" 탭에서 최신 공지 확인

#### 비즈니스 문의
1. "💼 비즈니스 문의" 탭 이동
2. "📝 문의 제출" 탭에서 문의 유형 선택
3. 정보 입력 및 제출
4. 접수번호 확인 및 저장
5. "🔍 문의 조회" 탭에서 접수번호 + 이메일로 답변 확인

#### 게시판 이용
1. "💬 게시판" 탭 이동
2. 카테고리 선택
3. "✍️ 글쓰기" 클릭
4. 게시글 작성 및 등록
5. 댓글 작성 및 좋아요

### 5. 관리자 모드

1. 사이드바에서 "관리자 모드" 찾기
2. 비밀번호 입력: `admin1234`
3. 로그인 후 관리 기능 사용:
   - 공지사항 작성/수정/삭제
   - 비즈니스 문의 조회 및 답변

## 🔧 설정

### 관리자 비밀번호 변경

보안을 위해 반드시 비밀번호를 변경하세요:

```python
# app.py에서 수정
if admin_password == "your_secure_password":
    st.session_state.admin_mode = True
```

또는 환경변수 사용:

```bash
export ADMIN_PASSWORD="your_secure_password"
```

```python
import os
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin1234')
```

### 데이터 업데이트 주기 변경

`modules/data_update_scheduler.py`에서 수정:

```python
# 선수 통계: 매일 오전 6시 → 오전 5시로 변경
schedule.every().day.at("05:00").do(self.update_all_player_stats)

# 부상 리포트: 매 시간 → 30분마다로 변경
schedule.every(30).minutes.do(self.update_injury_reports)
```

## 📊 지원 리그

### ⚽ 축구
- K리그1
- EPL (잉글랜드 프리미어리그)
- La Liga (스페인)
- Bundesliga (독일)
- Serie A (이탈리아)

### ⚾ 야구
- KBO (한국)
- MLB (미국)

### 🏀 농구
- KBL (한국)
- NBA (미국)

### 🏐 배구
- V-리그 남자
- V-리그 여자

## 🔐 보안 및 개인정보

### 데이터 보호
- 게시글/댓글 비밀번호: SHA-256 해시 저장
- SQL Injection 방지: Parameterized queries 사용
- XSS 방지: Streamlit 기본 보호 활용

### 개인정보 처리
- 비즈니스 문의: 이메일, 연락처 수집 (동의 필수)
- 게시판: IP 주소 수집 (좋아요 중복 방지)
- 관리자만 접근 가능

## 📈 성능 최적화

### 캐시 시스템
- 실시간 데이터: 5분 캐시
- 선수 통계: 24시간 캐시
- 경기 일정: 24시간 캐시

### 데이터베이스 최적화
- SQLite 인덱스 자동 생성
- 정기적인 VACUUM 실행 권장

```bash
sqlite3 data/player_stats.db "VACUUM;"
sqlite3 data/community.db "VACUUM;"
```

## 🐛 문제 해결

### 데이터베이스 오류
```bash
# 데이터베이스 재초기화
rm data/community.db
python scripts/init_community.py
```

### 실시간 데이터 수집 실패
```bash
# 수동 업데이트 실행
python scripts/manual_update.py --league NBA --team "Boston Celtics"
```

### 캐시 초기화
앱 사이드바에서 "데이터 새로고침" 버튼 클릭

## 📚 추가 문서

- [커뮤니티 시스템 가이드](COMMUNITY_GUIDE.md)
- [고급 메트릭스 통합 가이드](ADVANCED_METRICS_INTEGRATION.md)
- [영문 README](README_EN.md)

## ⚠️ 주의사항

이 시스템은 분석 도구이며:

- 예측은 참고용이며 100% 정확하지 않습니다
- 스포츠 경기는 예측 불가능한 변수가 많습니다
- 투자 결정은 사용자 책임입니다
- 상업적 사용 금지
- 무단 배포 금지

## 🎯 향후 개선 방향

1. ✅ 실시간 데이터 수집 (완료)
2. ✅ 고급 메트릭스 통합 (완료)
3. ✅ 커뮤니티 시스템 (완료)
4. 🔄 머신러닝 모델 학습 (진행 중)
5. 📱 모바일 앱 개발
6. 🌐 다국어 지원 확대
7. 📊 대시보드 고도화
8. 🤖 AI 챗봇 통합

## 📞 문의 및 지원

### 비즈니스 문의
앱 내 "💼 비즈니스 문의" 탭 이용

### 기술 지원
앱 내 "💬 게시판" > "질문/답변" 카테고리 이용

### 버그 리포트
GitHub Issues 또는 게시판 이용

## 📄 라이선스

개인 프로젝트 - 비상업적 용도로만 사용 가능

## 🙏 감사의 말

데이터 제공:
- Basketball-Reference
- Statiz
- KBO, KBL, K-League, KOVO 공식 홈페이지

---

**VIBE BOX Sports MatchSignal** - AI 기반 스포츠 예측의 새로운 기준

⚡ Powered by Advanced Metrics & Real-time Data

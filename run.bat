@echo off
echo ========================================
echo 스포츠 경기 예측 시스템 시작
echo ========================================
echo.

REM 가상환경 확인
if not exist "venv" (
    echo 가상환경이 없습니다. 생성 중...
    python -m venv venv
    echo 가상환경 생성 완료!
    echo.
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 패키지 설치 확인
echo 필요한 패키지 설치 중...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo 웹 브라우저에서 자동으로 열립니다
echo 종료하려면 Ctrl+C를 누르세요
echo ========================================
echo.

REM Streamlit 실행
streamlit run app.py

pause

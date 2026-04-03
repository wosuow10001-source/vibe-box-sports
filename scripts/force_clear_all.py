"""
모든 캐시와 임시 파일을 강제로 삭제하는 스크립트
Streamlit 앱의 모든 캐시를 완전히 초기화합니다.
"""

import sys
import shutil
from pathlib import Path

print("="*80)
print("🚨 강제 캐시 초기화 스크립트")
print("="*80)

# 프로젝트 루트
project_root = Path(__file__).parent.parent

# 1. Streamlit 캐시 디렉토리 삭제
streamlit_cache_dirs = [
    project_root / ".streamlit" / "cache",
    Path.home() / ".streamlit" / "cache",
]

for cache_dir in streamlit_cache_dirs:
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ 삭제 완료: {cache_dir}")
        except Exception as e:
            print(f"⚠️ 삭제 실패: {cache_dir} - {e}")
    else:
        print(f"ℹ️ 없음: {cache_dir}")

# 2. Python __pycache__ 디렉토리 삭제
pycache_dirs = list(project_root.rglob("__pycache__"))

print(f"\n__pycache__ 디렉토리 {len(pycache_dirs)}개 발견")

for pycache_dir in pycache_dirs:
    try:
        shutil.rmtree(pycache_dir)
        print(f"✅ 삭제: {pycache_dir.relative_to(project_root)}")
    except Exception as e:
        print(f"⚠️ 실패: {pycache_dir.relative_to(project_root)} - {e}")

# 3. .pyc 파일 삭제
pyc_files = list(project_root.rglob("*.pyc"))

print(f"\n.pyc 파일 {len(pyc_files)}개 발견")

for pyc_file in pyc_files:
    try:
        pyc_file.unlink()
        print(f"✅ 삭제: {pyc_file.relative_to(project_root)}")
    except Exception as e:
        print(f"⚠️ 실패: {pyc_file.relative_to(project_root)} - {e}")

print("\n" + "="*80)
print("✅ 캐시 초기화 완료!")
print("="*80)
print("\n다음 단계:")
print("1. 실행 중인 Streamlit 앱을 Ctrl+C로 완전 종료")
print("2. 브라우저를 완전히 닫기")
print("3. 다시 streamlit run app.py 실행")
print("4. 새 브라우저 창에서 앱 열기")
print("\n또는 시크릿/프라이빗 모드로 앱 열기")

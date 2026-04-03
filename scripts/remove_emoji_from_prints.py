"""
모든 Python 파일에서 print 문의 이모지를 제거하는 스크립트
Windows cp949 인코딩 오류 해결
"""

import re
from pathlib import Path

# 이모지 매핑
emoji_map = {
    '✅': '[OK]',
    '⚠️': '[WARNING]',
    '❌': '[ERROR]',
    '🔍': '[SEARCH]',
    '📡': '[FETCH]',
    '🔄': '[REFRESH]',
    '🆕': '[NEW]',
    '🚨': '[ALERT]',
}

def remove_emoji_from_file(file_path):
    """파일에서 print 문의 이모지 제거"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 각 이모지를 텍스트로 변환
        for emoji, text in emoji_map.items():
            content = content.replace(emoji, text)
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Fixed: {file_path}")
            return True
        else:
            print(f"[SKIP] No emoji: {file_path}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed: {file_path} - {e}")
        return False

# 수정할 파일 목록 - 모든 Python 파일
files_to_fix = [
    'modules/data_collector.py',
    'modules/player_data_loader.py',
    'modules/roster_fetcher.py',
    'modules/community_database.py',
    'modules/injury_fetcher.py',
    'modules/live_data_fetcher.py',
    'modules/realtime_data_fetcher.py',
    'modules/coaching_staff_fetcher.py',
    'modules/lineup_manager.py',
    'modules/analyzer.py',
    'modules/predictor_baseball.py',
    'modules/predictor_basketball_league_normalized.py',
    'modules/predictor_basketball_pro.py',
    'modules/predictor_soccer.py',
    'modules/predictor_volleyball.py',
    'modules/score_predictor.py',
    'modules/sport_router.py',
    'modules/tactical_matchup_system.py',
    'modules/player_rating_system.py',
    'modules/player_stats_database.py',
    'modules/data_update_scheduler.py',
    'modules/advanced_baseball_metrics.py',
    'modules/advanced_soccer_metrics.py',
    'modules/advanced_volleyball_metrics.py',
    'modules/advanced_player_metrics.py',
    'app.py',
]

print("="*80)
print("Removing emoji from print statements")
print("="*80)

project_root = Path(__file__).parent.parent
fixed_count = 0

for file_path in files_to_fix:
    full_path = project_root / file_path
    if full_path.exists():
        if remove_emoji_from_file(full_path):
            fixed_count += 1
    else:
        print(f"[SKIP] Not found: {file_path}")

print("\n" + "="*80)
print(f"Fixed {fixed_count} files")
print("="*80)

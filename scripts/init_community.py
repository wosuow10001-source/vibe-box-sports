"""
커뮤니티 데이터베이스 초기화 및 샘플 데이터 추가
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from modules.community_database import get_community_database


def init_community_data():
    """커뮤니티 초기 데이터 생성"""
    
    db = get_community_database()
    
    print("🚀 커뮤니티 데이터베이스 초기화 시작...")
    
    # 1. 샘플 공지사항 추가
    print("\n📢 공지사항 추가 중...")
    
    announcements = [
        {
            'title': '🎉 VIBE BOX Sports MatchSignal 오픈!',
            'content': '''
안녕하세요! VIBE BOX Sports MatchSignal에 오신 것을 환영합니다.

저희 플랫폼은 AI 기반 스포츠 경기 예측 서비스를 제공합니다.

**주요 기능**:
- 🏀 NBA, KBL 농구 예측
- ⚽ K-League, EPL, La Liga 축구 예측
- ⚾ KBO, MLB 야구 예측
- 🏐 V-League 배구 예측

**고급 메트릭스**:
- 축구: xG, xA, PPDA
- 야구: OPS, wOBA, ERA+, FIP
- 배구: 스파이크율, 블록 효율
- 농구: PER, Win Shares, BPM

실시간 데이터 업데이트로 정확한 예측을 제공합니다!

감사합니다.
            ''',
            'is_important': True,
            'is_pinned': True
        },
        {
            'title': '📊 실시간 데이터 업데이트 시스템 가동',
            'content': '''
실시간 데이터 업데이트 시스템이 정상 가동 중입니다.

**업데이트 주기**:
- 선수 통계: 매일 오전 6시
- 부상 리포트: 매 시간
- 경기 일정: 매일 오전 7시
- 경기 당일: 30분마다

데이터 소스: Basketball-Reference, Statiz, KBO, KOVO 등
            ''',
            'is_important': False,
            'is_pinned': False
        },
        {
            'title': '💼 광고 및 스폰서십 문의 안내',
            'content': '''
VIBE BOX Sports MatchSignal과 함께 성장하실 파트너를 찾습니다!

**광고 상품**:
- 배너 광고 (사이드바, 메인 페이지)
- 데이터 스폰서십
- 파트너십 프로그램

자세한 문의는 "비즈니스 문의" 탭을 이용해주세요.
            ''',
            'is_important': False,
            'is_pinned': False
        }
    ]
    
    for announcement in announcements:
        announcement_id = db.create_announcement(**announcement)
        print(f"  ✅ 공지사항 추가: {announcement['title']} (ID: {announcement_id})")
    
    # 2. 샘플 게시글 추가
    print("\n💬 샘플 게시글 추가 중...")
    
    posts = [
        {
            'category': '자유게시판',
            'title': '안녕하세요! 첫 게시글입니다',
            'content': '''
VIBE BOX Sports MatchSignal 오픈을 축하합니다!

AI 기반 예측이 정말 정확하네요. 앞으로 자주 이용하겠습니다!
            ''',
            'author': '스포츠팬',
            'password': 'test1234'
        },
        {
            'category': '예측 토론',
            'title': 'NBA 디트로이트 vs 레이커스 예측 어떻게 보시나요?',
            'content': '''
오늘 경기 예측 결과를 보니 디트로이트가 유리하다고 나오는데,
여러분 생각은 어떠신가요?

최근 폼을 보면 디트로이트가 9승 1패로 정말 좋은 상태인 것 같습니다.
            ''',
            'author': 'NBA매니아',
            'password': 'test1234'
        },
        {
            'category': '질문/답변',
            'title': 'xG가 정확히 무엇인가요?',
            'content': '''
축구 예측에서 xG (Expected Goals)라는 지표가 나오는데,
이게 정확히 무엇을 의미하는 건가요?

자세한 설명 부탁드립니다!
            ''',
            'author': '축구초보',
            'password': 'test1234'
        }
    ]
    
    for post in posts:
        post_id = db.create_post(**post)
        print(f"  ✅ 게시글 추가: {post['title']} (ID: {post_id})")
        
        # 첫 번째 게시글에 댓글 추가
        if post_id == 1:
            comment_id = db.create_comment(
                post_id=post_id,
                author='관리자',
                content='환영합니다! 많은 이용 부탁드립니다 😊',
                password='admin1234'
            )
            print(f"    ✅ 댓글 추가 (ID: {comment_id})")
    
    # 3. 통계 출력
    print("\n📊 커뮤니티 통계:")
    stats = db.get_statistics()
    print(f"  - 공지사항: {stats['total_announcements']}개")
    print(f"  - 게시글: {stats['total_posts']}개")
    print(f"  - 댓글: {stats['total_comments']}개")
    print(f"  - 비즈니스 문의: {stats['total_inquiries']}개")
    
    print("\n✅ 커뮤니티 데이터베이스 초기화 완료!")


if __name__ == "__main__":
    init_community_data()

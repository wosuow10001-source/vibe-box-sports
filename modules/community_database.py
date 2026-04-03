"""
커뮤니티 데이터베이스
- 공지사항
- 비즈니스/광고 문의
- 게시판 (댓글 시스템 포함)
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import hashlib


class CommunityDatabase:
    """커뮤니티 데이터베이스 관리"""
    
    def __init__(self, db_path: str = "data/community.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        self.create_tables()
        print(f"[OK] 커뮤니티 데이터베이스 초기화: {self.db_path}")
    
    def create_tables(self):
        """테이블 생성"""
        
        # 공지사항 테이블
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT DEFAULT '관리자',
                is_important BOOLEAN DEFAULT 0,
                is_pinned BOOLEAN DEFAULT 0,
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 비즈니스/광고 문의 테이블
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS business_inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inquiry_type TEXT NOT NULL,
                company_name TEXT,
                contact_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                admin_reply TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                replied_at TIMESTAMP
            )
        ''')
        
        # 게시판 테이블
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS board_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                author_ip TEXT,
                password_hash TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                is_notice BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 댓글 테이블
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS board_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                parent_comment_id INTEGER,
                author TEXT NOT NULL,
                author_ip TEXT,
                password_hash TEXT,
                content TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES board_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_comment_id) REFERENCES board_comments(id) ON DELETE CASCADE
            )
        ''')
        
        # 좋아요 기록 테이블 (중복 방지)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS likes_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_type TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                user_ip TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target_type, target_id, user_ip)
            )
        ''')
        
        self.conn.commit()
    
    # ==================== 공지사항 ====================
    
    def create_announcement(self, title: str, content: str, author: str = '관리자',
                          is_important: bool = False, is_pinned: bool = False) -> int:
        """공지사항 생성"""
        
        cursor = self.conn.execute('''
            INSERT INTO announcements (title, content, author, is_important, is_pinned)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, author, is_important, is_pinned))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_announcements(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """공지사항 목록 조회 (고정 공지 우선)"""
        
        cursor = self.conn.execute('''
            SELECT * FROM announcements
            ORDER BY is_pinned DESC, is_important DESC, created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_announcement(self, announcement_id: int) -> Optional[Dict]:
        """공지사항 상세 조회"""
        
        # 조회수 증가
        self.conn.execute(
            'UPDATE announcements SET views = views + 1 WHERE id = ?',
            (announcement_id,)
        )
        self.conn.commit()
        
        cursor = self.conn.execute(
            'SELECT * FROM announcements WHERE id = ?',
            (announcement_id,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_announcement(self, announcement_id: int, title: str = None,
                          content: str = None, is_important: bool = None,
                          is_pinned: bool = None) -> bool:
        """공지사항 수정"""
        
        updates = []
        params = []
        
        if title is not None:
            updates.append('title = ?')
            params.append(title)
        if content is not None:
            updates.append('content = ?')
            params.append(content)
        if is_important is not None:
            updates.append('is_important = ?')
            params.append(is_important)
        if is_pinned is not None:
            updates.append('is_pinned = ?')
            params.append(is_pinned)
        
        if not updates:
            return False
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(announcement_id)
        
        query = f"UPDATE announcements SET {', '.join(updates)} WHERE id = ?"
        self.conn.execute(query, params)
        self.conn.commit()
        
        return True
    
    def delete_announcement(self, announcement_id: int) -> bool:
        """공지사항 삭제"""
        
        self.conn.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
        self.conn.commit()
        return True
    
    # ==================== 비즈니스 문의 ====================
    
    def create_business_inquiry(self, inquiry_type: str, contact_name: str,
                               email: str, subject: str, message: str,
                               company_name: str = None, phone: str = None) -> int:
        """비즈니스 문의 생성"""
        
        cursor = self.conn.execute('''
            INSERT INTO business_inquiries 
            (inquiry_type, company_name, contact_name, email, phone, subject, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (inquiry_type, company_name, contact_name, email, phone, subject, message))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_business_inquiries(self, status: str = None, limit: int = 50) -> List[Dict]:
        """비즈니스 문의 목록 조회"""
        
        if status:
            cursor = self.conn.execute('''
                SELECT * FROM business_inquiries
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (status, limit))
        else:
            cursor = self.conn.execute('''
                SELECT * FROM business_inquiries
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_business_inquiry(self, inquiry_id: int) -> Optional[Dict]:
        """비즈니스 문의 상세 조회"""
        
        cursor = self.conn.execute(
            'SELECT * FROM business_inquiries WHERE id = ?',
            (inquiry_id,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_business_inquiry_by_credentials(self, inquiry_id: int, email: str) -> Optional[Dict]:
        """비즈니스 문의 조회 (접수번호 + 이메일 인증)"""
        
        cursor = self.conn.execute(
            'SELECT * FROM business_inquiries WHERE id = ? AND email = ?',
            (inquiry_id, email)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def reply_business_inquiry(self, inquiry_id: int, admin_reply: str) -> bool:
        """비즈니스 문의 답변"""
        
        self.conn.execute('''
            UPDATE business_inquiries
            SET status = 'replied', admin_reply = ?, replied_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (admin_reply, inquiry_id))
        
        self.conn.commit()
        return True
    
    def update_inquiry_status(self, inquiry_id: int, status: str) -> bool:
        """문의 상태 변경"""
        
        self.conn.execute(
            'UPDATE business_inquiries SET status = ? WHERE id = ?',
            (status, inquiry_id)
        )
        self.conn.commit()
        return True
    
    # ==================== 게시판 ====================
    
    def create_post(self, category: str, title: str, content: str,
                   author: str, password: str, author_ip: str = None) -> int:
        """게시글 작성"""
        
        password_hash = self._hash_password(password)
        
        cursor = self.conn.execute('''
            INSERT INTO board_posts 
            (category, title, content, author, author_ip, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (category, title, content, author, author_ip, password_hash))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_posts(self, category: str = None, limit: int = 20, offset: int = 0) -> List[Dict]:
        """게시글 목록 조회"""
        
        if category:
            cursor = self.conn.execute('''
                SELECT p.*, 
                       (SELECT COUNT(*) FROM board_comments WHERE post_id = p.id) as comment_count
                FROM board_posts p
                WHERE category = ?
                ORDER BY is_notice DESC, created_at DESC
                LIMIT ? OFFSET ?
            ''', (category, limit, offset))
        else:
            cursor = self.conn.execute('''
                SELECT p.*,
                       (SELECT COUNT(*) FROM board_comments WHERE post_id = p.id) as comment_count
                FROM board_posts p
                ORDER BY is_notice DESC, created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_post(self, post_id: int) -> Optional[Dict]:
        """게시글 상세 조회"""
        
        # 조회수 증가
        self.conn.execute(
            'UPDATE board_posts SET views = views + 1 WHERE id = ?',
            (post_id,)
        )
        self.conn.commit()
        
        cursor = self.conn.execute(
            'SELECT * FROM board_posts WHERE id = ?',
            (post_id,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_post(self, post_id: int, password: str, title: str = None,
                   content: str = None) -> bool:
        """게시글 수정"""
        
        # 비밀번호 확인
        post = self.get_post(post_id)
        if not post or not self._verify_password(password, post['password_hash']):
            return False
        
        updates = []
        params = []
        
        if title is not None:
            updates.append('title = ?')
            params.append(title)
        if content is not None:
            updates.append('content = ?')
            params.append(content)
        
        if not updates:
            return False
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(post_id)
        
        query = f"UPDATE board_posts SET {', '.join(updates)} WHERE id = ?"
        self.conn.execute(query, params)
        self.conn.commit()
        
        return True
    
    def delete_post(self, post_id: int, password: str) -> bool:
        """게시글 삭제"""
        
        # 비밀번호 확인
        post = self.get_post(post_id)
        if not post or not self._verify_password(password, post['password_hash']):
            return False
        
        self.conn.execute('DELETE FROM board_posts WHERE id = ?', (post_id,))
        self.conn.commit()
        return True
    
    def search_posts(self, keyword: str, category: str = None, limit: int = 20) -> List[Dict]:
        """게시글 검색"""
        
        keyword_pattern = f'%{keyword}%'
        
        if category:
            cursor = self.conn.execute('''
                SELECT p.*,
                       (SELECT COUNT(*) FROM board_comments WHERE post_id = p.id) as comment_count
                FROM board_posts p
                WHERE category = ? AND (title LIKE ? OR content LIKE ?)
                ORDER BY created_at DESC
                LIMIT ?
            ''', (category, keyword_pattern, keyword_pattern, limit))
        else:
            cursor = self.conn.execute('''
                SELECT p.*,
                       (SELECT COUNT(*) FROM board_comments WHERE post_id = p.id) as comment_count
                FROM board_posts p
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (keyword_pattern, keyword_pattern, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 댓글 ====================
    
    def create_comment(self, post_id: int, author: str, content: str,
                      password: str, author_ip: str = None,
                      parent_comment_id: int = None) -> int:
        """댓글 작성"""
        
        password_hash = self._hash_password(password)
        
        cursor = self.conn.execute('''
            INSERT INTO board_comments 
            (post_id, parent_comment_id, author, author_ip, password_hash, content)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (post_id, parent_comment_id, author, author_ip, password_hash, content))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_comments(self, post_id: int) -> List[Dict]:
        """댓글 목록 조회 (대댓글 포함)"""
        
        cursor = self.conn.execute('''
            SELECT * FROM board_comments
            WHERE post_id = ?
            ORDER BY parent_comment_id IS NULL DESC, created_at ASC
        ''', (post_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_comment(self, comment_id: int, password: str) -> bool:
        """댓글 삭제"""
        
        # 비밀번호 확인
        cursor = self.conn.execute(
            'SELECT password_hash FROM board_comments WHERE id = ?',
            (comment_id,)
        )
        row = cursor.fetchone()
        
        if not row or not self._verify_password(password, row['password_hash']):
            return False
        
        self.conn.execute('DELETE FROM board_comments WHERE id = ?', (comment_id,))
        self.conn.commit()
        return True
    
    # ==================== 좋아요 ====================
    
    def add_like(self, target_type: str, target_id: int, user_ip: str) -> bool:
        """좋아요 추가"""
        
        try:
            # 중복 체크 및 추가
            self.conn.execute('''
                INSERT INTO likes_log (target_type, target_id, user_ip)
                VALUES (?, ?, ?)
            ''', (target_type, target_id, user_ip))
            
            # 좋아요 수 증가
            if target_type == 'post':
                self.conn.execute(
                    'UPDATE board_posts SET likes = likes + 1 WHERE id = ?',
                    (target_id,)
                )
            elif target_type == 'comment':
                self.conn.execute(
                    'UPDATE board_comments SET likes = likes + 1 WHERE id = ?',
                    (target_id,)
                )
            
            self.conn.commit()
            return True
        
        except sqlite3.IntegrityError:
            # 이미 좋아요를 누른 경우
            return False
    
    def check_liked(self, target_type: str, target_id: int, user_ip: str) -> bool:
        """좋아요 여부 확인"""
        
        cursor = self.conn.execute('''
            SELECT COUNT(*) FROM likes_log
            WHERE target_type = ? AND target_id = ? AND user_ip = ?
        ''', (target_type, target_id, user_ip))
        
        count = cursor.fetchone()[0]
        return count > 0
    
    # ==================== 통계 ====================
    
    def get_statistics(self) -> Dict:
        """커뮤니티 통계"""
        
        cursor = self.conn.execute('SELECT COUNT(*) FROM announcements')
        total_announcements = cursor.fetchone()[0]
        
        cursor = self.conn.execute('SELECT COUNT(*) FROM business_inquiries')
        total_inquiries = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM business_inquiries WHERE status = 'pending'")
        pending_inquiries = cursor.fetchone()[0]
        
        cursor = self.conn.execute('SELECT COUNT(*) FROM board_posts')
        total_posts = cursor.fetchone()[0]
        
        cursor = self.conn.execute('SELECT COUNT(*) FROM board_comments')
        total_comments = cursor.fetchone()[0]
        
        return {
            'total_announcements': total_announcements,
            'total_inquiries': total_inquiries,
            'pending_inquiries': pending_inquiries,
            'total_posts': total_posts,
            'total_comments': total_comments
        }
    
    # ==================== 유틸리티 ====================
    
    def _hash_password(self, password: str) -> str:
        """비밀번호 해시"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """비밀번호 확인"""
        return self._hash_password(password) == password_hash
    
    def close(self):
        """데이터베이스 연결 종료"""
        self.conn.close()


# 싱글톤 인스턴스
_community_db = None

def get_community_database() -> CommunityDatabase:
    """CommunityDatabase 싱글톤 반환"""
    global _community_db
    if _community_db is None:
        _community_db = CommunityDatabase()
    return _community_db

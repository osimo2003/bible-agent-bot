import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_path='database/bible_agent.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferences TEXT
            )
        ''')
        
        # Reading progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reading_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                book TEXT NOT NULL,
                chapter INTEGER NOT NULL,
                completed BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Bookmarks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                book TEXT NOT NULL,
                chapter INTEGER NOT NULL,
                verse INTEGER,
                note TEXT,
                topic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Conversations table (for context)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                intent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Daily schedule table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                scheduled_time TEXT,
                timezone TEXT DEFAULT 'UTC',
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User methods
    def create_user(self, user_id, name=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (user_id, name, preferences)
                VALUES (?, ?, ?)
            ''', (user_id, name, json.dumps({})))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    # Reading progress methods
    def get_current_chapter(self, user_id):
        """Get the next chapter to read in NT sequence"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # NT books in order
        nt_books = [
            'Matthew', 'Mark', 'Luke', 'John', 'Acts',
            'Romans', '1 Corinthians', '2 Corinthians', 'Galatians',
            'Ephesians', 'Philippians', 'Colossians',
            '1 Thessalonians', '2 Thessalonians',
            '1 Timothy', '2 Timothy', 'Titus', 'Philemon',
            'Hebrews', 'James', '1 Peter', '2 Peter',
            '1 John', '2 John', '3 John', 'Jude', 'Revelation'
        ]
        
        # Get last completed chapter
        cursor.execute('''
            SELECT book, chapter FROM reading_progress
            WHERE user_id = ? AND completed = 1
            ORDER BY completed_at DESC LIMIT 1
        ''', (user_id,))
        
        last = cursor.fetchone()
        conn.close()
        
        if not last:
            return {'book': 'Matthew', 'chapter': 1}
        
        # Find next chapter
        book_idx = nt_books.index(last['book'])
        next_chapter = last['chapter'] + 1
        
        # Chapter counts
        chapter_counts = {
            'Matthew': 28, 'Mark': 16, 'Luke': 24, 'John': 21,
            'Acts': 28, 'Romans': 16, '1 Corinthians': 16,
            '2 Corinthians': 13, 'Galatians': 6, 'Ephesians': 6,
            'Philippians': 4, 'Colossians': 4, '1 Thessalonians': 5,
            '2 Thessalonians': 3, '1 Timothy': 6, '2 Timothy': 4,
            'Titus': 3, 'Philemon': 1, 'Hebrews': 13, 'James': 5,
            '1 Peter': 5, '2 Peter': 3, '1 John': 5, '2 John': 1,
            '3 John': 1, 'Jude': 1, 'Revelation': 22
        }
        
        current_book = last['book']
        if next_chapter > chapter_counts[current_book]:
            # Move to next book
            if book_idx + 1 < len(nt_books):
                return {'book': nt_books[book_idx + 1], 'chapter': 1}
            else:
                return {'book': 'Matthew', 'chapter': 1}
        
        return {'book': current_book, 'chapter': next_chapter}
    
    def mark_chapter_complete(self, user_id, book, chapter):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reading_progress (user_id, book, chapter, completed, completed_at)
            VALUES (?, ?, ?, 1, ?)
        ''', (user_id, book, chapter, datetime.now()))
        conn.commit()
        conn.close()
    
    # Bookmark methods
    def add_bookmark(self, user_id, book, chapter, verse=None, note=None, topic=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bookmarks (user_id, book, chapter, verse, note, topic)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, book, chapter, verse, note, topic))
        conn.commit()
        conn.close()
    
    def get_bookmarks(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bookmarks WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        bookmarks = cursor.fetchall()
        conn.close()
        return [dict(b) for b in bookmarks]
    
    # Conversation methods
    def save_conversation(self, user_id, message, response, intent=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_id, message, response, intent)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message, response, intent))
        conn.commit()
        conn.close()

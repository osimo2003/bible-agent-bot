import sqlite3
from pathlib import Path

class FullBibleDatabase:
    """
    Interface to complete Bible SQLite database
    Provides full-text search across Old and New Testament
    """
    
    def __init__(self, db_path='database/bible.db'):
        self.db_path = Path(__file__).parent / 'bible.db'
        self.conn = None
        self.book_cache = {}
        self.connect()
        self.load_books()
    
    def connect(self):
        """Connect to the Bible database"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            print(f"✅ Full Bible database connected")
        except Exception as e:
            print(f"❌ Error connecting to Bible database: {e}")
            self.conn = None
    
    def load_books(self):
        """Load book names into cache for fast lookup"""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT book_id, book_name, testament FROM books")
            books = cursor.fetchall()
            
            for book in books:
                self.book_cache[book['book_id']] = {
                    'name': book['book_name'],
                    'testament': book['testament']
                }
            
            print(f"✅ Loaded {len(self.book_cache)} books")
        except Exception as e:
            print(f"❌ Error loading books: {e}")
    
    def search_text(self, query, max_results=10):
        """
        Search for any word or phrase in the Bible
        Returns list of matching verses
        """
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            
            sql = """
                SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                FROM verses v
                WHERE v.text LIKE ? 
                ORDER BY v.id 
                LIMIT ?
            """
            
            cursor.execute(sql, (f'%{query}%', max_results))
            results = cursor.fetchall()
            
            verses = []
            for row in results:
                book_name = self.book_cache.get(row['book_id'], {}).get('name', 'Unknown')
                verses.append({
                    'book': book_name,
                    'chapter': row['chapter'],
                    'verse': row['verse'],
                    'text': row['text'],
                    'reference': f"{book_name} {row['chapter']}:{row['verse']}"
                })
            
            return verses
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_book(self, book_name, query=None, max_results=10):
        """Search within a specific book"""
        if not self.conn:
            return []
        
        try:
            # Find book_id by name
            book_id = None
            for bid, book_info in self.book_cache.items():
                if book_name.lower() in book_info['name'].lower():
                    book_id = bid
                    break
            
            if not book_id:
                return []
            
            cursor = self.conn.cursor()
            
            if query:
                sql = """
                    SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                    FROM verses v
                    WHERE v.book_id = ? AND v.text LIKE ?
                    ORDER BY v.chapter, v.verse
                    LIMIT ?
                """
                cursor.execute(sql, (book_id, f'%{query}%', max_results))
            else:
                sql = """
                    SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                    FROM verses v
                    WHERE v.book_id = ?
                    ORDER BY v.chapter, v.verse
                    LIMIT ?
                """
                cursor.execute(sql, (book_id, max_results))
            
            results = cursor.fetchall()
            
            verses = []
            for row in results:
                book_name_full = self.book_cache.get(row['book_id'], {}).get('name', book_name)
                verses.append({
                    'book': book_name_full,
                    'chapter': row['chapter'],
                    'verse': row['verse'],
                    'text': row['text'],
                    'reference': f"{book_name_full} {row['chapter']}:{row['verse']}"
                })
            
            return verses
            
        except Exception as e:
            print(f"Book search error: {e}")
            return []
    
    def get_verse(self, book, chapter, verse):
        """Get a specific verse"""
        if not self.conn:
            return None
        
        try:
            # Find book_id
            book_id = None
            for bid, book_info in self.book_cache.items():
                if book.lower() in book_info['name'].lower():
                    book_id = bid
                    break
            
            if not book_id:
                return None
            
            cursor = self.conn.cursor()
            sql = """
                SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                FROM verses v
                WHERE v.book_id = ? AND v.chapter = ? AND v.verse = ?
            """
            
            cursor.execute(sql, (book_id, chapter, verse))
            row = cursor.fetchone()
            
            if row:
                book_name = self.book_cache.get(row['book_id'], {}).get('name', book)
                return {
                    'book': book_name,
                    'chapter': row['chapter'],
                    'verse': row['verse'],
                    'text': row['text'],
                    'reference': f"{book_name} {row['chapter']}:{row['verse']}"
                }
            
            return None
            
        except Exception as e:
            print(f"Get verse error: {e}")
            return None
    
    def get_chapter(self, book, chapter):
        """Get all verses from a chapter"""
        if not self.conn:
            return []
        
        try:
            # Find book_id
            book_id = None
            for bid, book_info in self.book_cache.items():
                if book.lower() in book_info['name'].lower():
                    book_id = bid
                    break
            
            if not book_id:
                return []
            
            cursor = self.conn.cursor()
            sql = """
                SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                FROM verses v
                WHERE v.book_id = ? AND v.chapter = ?
                ORDER BY v.verse
            """
            
            cursor.execute(sql, (book_id, chapter))
            results = cursor.fetchall()
            
            verses = []
            book_name = self.book_cache.get(book_id, {}).get('name', book)
            for row in results:
                verses.append({
                    'book': book_name,
                    'chapter': row['chapter'],
                    'verse': row['verse'],
                    'text': row['text'],
                    'reference': f"{book_name} {row['chapter']}:{row['verse']}"
                })
            
            return verses
            
        except Exception as e:
            print(f"Get chapter error: {e}")
            return []
    
    def get_stats(self):
        """Get database statistics"""
        if not self.conn:
            return None
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total FROM verses")
            total = cursor.fetchone()['total']
            
            return {
                'total_verses': total,
                'total_books': len(self.book_cache),
                'status': 'connected'
            }
            
        except Exception as e:
            print(f"Stats error: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

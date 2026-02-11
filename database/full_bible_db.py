import sqlite3
import re
from pathlib import Path

class FullBibleDatabase:
    """Interface to complete Bible SQLite database"""
    
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
        """Load book names into cache"""
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
    
    def search_text(self, query, max_results=10, testament=None):
        """Search for any word or phrase in the Bible"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            query_lower = query.lower().strip()
            
            # Build testament filter
            testament_filter = ""
            if testament:
                book_ids = [bid for bid, info in self.book_cache.items() 
                           if info['testament'] == testament]
                if book_ids:
                    testament_filter = f" AND v.book_id IN ({','.join(map(str, book_ids))})"
            
            # Strategy 1: Flexible phrase search
            words = query_lower.split()
            if len(words) > 1:
                flexible_pattern = '%'.join(words)
                sql = f"""
                    SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                    FROM verses v
                    WHERE LOWER(v.text) LIKE ? {testament_filter}
                    ORDER BY v.id LIMIT ?
                """
                cursor.execute(sql, (f'%{flexible_pattern}%', max_results))
                results = cursor.fetchall()
                if results:
                    return self._format_results(results)
            
            # Strategy 2: Direct search
            sql = f"""
                SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                FROM verses v
                WHERE LOWER(v.text) LIKE ? {testament_filter}
                ORDER BY v.id LIMIT ?
            """
            cursor.execute(sql, (f'%{query_lower}%', max_results))
            results = cursor.fetchall()
            if results:
                return self._format_results(results)
            
            # Strategy 3: Multi-word AND search
            if len(words) > 1:
                conditions = ' AND '.join([f"LOWER(v.text) LIKE '%{word}%'" for word in words])
                sql = f"""
                    SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                    FROM verses v
                    WHERE {conditions} {testament_filter}
                    ORDER BY v.id LIMIT ?
                """
                cursor.execute(sql, (max_results,))
                results = cursor.fetchall()
                if results:
                    return self._format_results(results)
            
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _format_results(self, results):
        """Format database results"""
        verses = []
        for row in results:
            book_info = self.book_cache.get(row['book_id'], {})
            book_name = book_info.get('name', 'Unknown')
            testament = book_info.get('testament', 'Unknown')
            text = re.sub(r'\{([^}]*)\}', r'\1', row['text'])
            
            verses.append({
                'book': book_name,
                'chapter': row['chapter'],
                'verse': row['verse'],
                'text': text,
                'reference': f"{book_name} {row['chapter']}:{row['verse']}",
                'testament': testament
            })
        return verses
    
    def get_verse(self, book, chapter, verse):
        """Get a specific verse"""
        if not self.conn:
            return None
        try:
            book_id = None
            for bid, book_info in self.book_cache.items():
                if book.lower() in book_info['name'].lower():
                    book_id = bid
                    break
            if not book_id:
                return None
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                FROM verses v WHERE v.book_id = ? AND v.chapter = ? AND v.verse = ?
            """, (book_id, chapter, verse))
            row = cursor.fetchone()
            
            if row:
                book_info = self.book_cache.get(row['book_id'], {})
                text = re.sub(r'\{([^}]*)\}', r'\1', row['text'])
                return {
                    'book': book_info.get('name', book),
                    'chapter': row['chapter'],
                    'verse': row['verse'],
                    'text': text,
                    'reference': f"{book_info.get('name', book)} {row['chapter']}:{row['verse']}",
                    'testament': book_info.get('testament', 'Unknown')
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
            book_id = None
            for bid, book_info in self.book_cache.items():
                if book.lower() in book_info['name'].lower():
                    book_id = bid
                    break
            if not book_id:
                return []
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT v.id, v.book_id, v.chapter, v.verse, v.text
                FROM verses v WHERE v.book_id = ? AND v.chapter = ?
                ORDER BY v.verse
            """, (book_id, chapter))
            return self._format_results(cursor.fetchall())
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
            return {'total_verses': total, 'total_books': len(self.book_cache), 'status': 'connected'}
        except Exception as e:
            print(f"Stats error: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

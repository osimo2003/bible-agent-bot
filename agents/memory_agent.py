from datetime import datetime, timedelta

class MemoryAgent:
    """
    Manages user data, progress tracking, and preferences
    - Reading progress
    - Bookmarks
    - User preferences
    - Conversation history
    """
    
    def __init__(self, db):
        self.db = db
    
    def get_next_chapters(self, user_id, count=2):
        """
        Get the next chapters to read in NT sequence
        Returns list of {book, chapter} dicts
        """
        # Ensure user exists
        user = self.db.get_user(user_id)
        if not user:
            self.db.create_user(user_id)
        
        # Get current reading position
        current = self.db.get_current_chapter(user_id)
        
        chapters = []
        book = current['book']
        chapter = current['chapter']
        
        # Get chapter counts for NT books
        chapter_counts = self._get_nt_chapter_counts()
        
        for i in range(count):
            chapters.append({'book': book, 'chapter': chapter})
            
            # Increment to next chapter
            chapter += 1
            if chapter > chapter_counts.get(book, 1):
                # Move to next book
                next_book = self._get_next_book(book)
                if next_book:
                    book = next_book
                    chapter = 1
                else:
                    # Reached end of NT, start over
                    book = 'Matthew'
                    chapter = 1
        
        return chapters
    
    def mark_complete(self, user_id, book=None, chapter=None):
        """
        Mark reading as complete
        If book/chapter not specified, marks current chapters as complete
        """
        if not book or not chapter:
            # Get what they should have read
            chapters = self.get_next_chapters(user_id, 2)
            for ch in chapters:
                self.db.mark_chapter_complete(user_id, ch['book'], ch['chapter'])
        else:
            self.db.mark_chapter_complete(user_id, book, chapter)
        
        return True
    
    def save_bookmark(self, user_id, reference, note=None, topic=None):
        """Save a verse bookmark"""
        # Parse reference
        parts = reference.split()
        if len(parts) >= 2:
            book = ' '.join(parts[:-1])
            chapter_verse = parts[-1].split(':')
            chapter = int(chapter_verse[0])
            verse = int(chapter_verse[1]) if len(chapter_verse) > 1 else None
            
            self.db.add_bookmark(user_id, book, chapter, verse, note, topic)
            return True
        return False
    
    def get_bookmarks(self, user_id):
        """Get all bookmarks for user"""
        return self.db.get_bookmarks(user_id)
    
    def get_progress(self, user_id):
        """
        Get reading progress statistics
        Returns completion percentage, current book/chapter, etc.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get total completed chapters
        cursor.execute('''
            SELECT COUNT(*) as completed
            FROM reading_progress
            WHERE user_id = ? AND completed = 1
        ''', (user_id,))
        completed = cursor.fetchone()['completed']
        
        # Total NT chapters (260)
        total_nt_chapters = 260
        progress_percent = (completed / total_nt_chapters) * 100
        
        # Get current position
        current = self.db.get_current_chapter(user_id)
        
        # Get reading streak
        cursor.execute('''
            SELECT COUNT(DISTINCT DATE(completed_at)) as streak
            FROM reading_progress
            WHERE user_id = ? AND completed = 1
            AND completed_at >= date('now', '-7 days')
        ''', (user_id,))
        streak = cursor.fetchone()['streak']
        
        conn.close()
        
        return {
            'completed_chapters': completed,
            'total_chapters': total_nt_chapters,
            'progress_percent': round(progress_percent, 1),
            'current_book': current['book'],
            'current_chapter': current['chapter'],
            'streak_days': streak
        }
    
    def save_conversation(self, user_id, message, response, intent=None):
        """Save conversation for context and learning"""
        self.db.save_conversation(user_id, message, response, intent)
    
    def _get_nt_chapter_counts(self):
        """Get chapter counts for all NT books"""
        return {
            'Matthew': 28, 'Mark': 16, 'Luke': 24, 'John': 21,
            'Acts': 28, 'Romans': 16, '1 Corinthians': 16,
            '2 Corinthians': 13, 'Galatians': 6, 'Ephesians': 6,
            'Philippians': 4, 'Colossians': 4, '1 Thessalonians': 5,
            '2 Thessalonians': 3, '1 Timothy': 6, '2 Timothy': 4,
            'Titus': 3, 'Philemon': 1, 'Hebrews': 13, 'James': 5,
            '1 Peter': 5, '2 Peter': 3, '1 John': 5, '2 John': 1,
            '3 John': 1, 'Jude': 1, 'Revelation': 22
        }
    
    def _get_next_book(self, current_book):
        """Get the next book in NT sequence"""
        nt_order = [
            'Matthew', 'Mark', 'Luke', 'John', 'Acts',
            'Romans', '1 Corinthians', '2 Corinthians', 'Galatians',
            'Ephesians', 'Philippians', 'Colossians',
            '1 Thessalonians', '2 Thessalonians',
            '1 Timothy', '2 Timothy', 'Titus', 'Philemon',
            'Hebrews', 'James', '1 Peter', '2 Peter',
            '1 John', '2 John', '3 John', 'Jude', 'Revelation'
        ]
        
        try:
            current_idx = nt_order.index(current_book)
            if current_idx + 1 < len(nt_order):
                return nt_order[current_idx + 1]
        except ValueError:
            pass
        
        return None
    
    def get_user_preferences(self, user_id):
        """Get user preferences"""
        user = self.db.get_user(user_id)
        if user and user['preferences']:
            import json
            return json.loads(user['preferences'])
        return {}
    
    def update_user_preferences(self, user_id, preferences):
        """Update user preferences"""
        import json
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET preferences = ?
            WHERE user_id = ?
        ''', (json.dumps(preferences), user_id))
        
        conn.commit()
        conn.close()

import requests
import json
import sqlite3

class BibleAPI:
    """Free Bible API interface using API.Bible"""
    
    def __init__(self):
        # Using free Bible API - no key required for basic access
        self.base_url = "https://bible-api.com"
        self.backup_url = "https://labs.bible.org/api"
    
    def get_verse(self, reference):
        """
        Get a specific verse or passage
        reference: e.g., "John 3:16" or "Matthew 5:1-10"
        """
        try:
            # Primary API
            url = f"{self.base_url}/{reference}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'reference': data.get('reference', reference),
                    'text': data.get('text', ''),
                    'translation': data.get('translation_name', 'KJV'),
                    'verses': data.get('verses', [])
                }
            else:
                return self._get_verse_backup(reference)
        except Exception as e:
            print(f"Error fetching verse: {e}")
            return self._get_verse_backup(reference)
    
    def _get_verse_backup(self, reference):
        """Backup method using alternative API"""
        try:
            # Format: passage=John+3:16&type=json
            formatted_ref = reference.replace(' ', '+')
            url = f"{self.backup_url}/?passage={formatted_ref}&type=json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    text = ' '.join([v.get('text', '') for v in data])
                    return {
                        'reference': reference,
                        'text': text,
                        'translation': 'KJV',
                        'verses': data
                    }
            return None
        except Exception as e:
            print(f"Backup API error: {e}")
            return None
    
    def get_chapter(self, book, chapter):
        """Get entire chapter"""
        reference = f"{book} {chapter}"
        return self.get_verse(reference)
    
    def search_verses(self, keyword):
        """
        Search for verses containing keyword
        Note: This is limited on free tier, we'll implement local search
        """
        # For now, return common verses for keywords
        keyword_map = {
            'anxiety': ['Philippians 4:6-7', 'Matthew 6:34', 'Isaiah 41:10'],
            'fear': ['2 Timothy 1:7', 'Isaiah 41:10', 'Psalm 56:3'],
            'love': ['1 Corinthians 13:4-8', 'John 3:16', '1 John 4:8'],
            'peace': ['John 14:27', 'Philippians 4:7', 'Romans 5:1'],
            'strength': ['Philippians 4:13', 'Isaiah 40:31', 'Psalm 46:1'],
            'faith': ['Hebrews 11:1', 'Romans 10:17', 'James 2:17'],
            'hope': ['Romans 15:13', 'Jeremiah 29:11', 'Hebrews 6:19'],
            'forgiveness': ['1 John 1:9', 'Ephesians 4:32', 'Matthew 6:14-15'],
            'wisdom': ['James 1:5', 'Proverbs 3:5-6', 'Colossians 3:16'],
            'guidance': ['Proverbs 3:5-6', 'Psalm 32:8', 'Isaiah 30:21']
        }
        
        keyword_lower = keyword.lower()
        verses = []
        
        # Find matching keywords
        for key, refs in keyword_map.items():
            if key in keyword_lower or keyword_lower in key:
                for ref in refs:
                    verse_data = self.get_verse(ref)
                    if verse_data:
                        verses.append(verse_data)
        
        return verses if verses else []


class LocalBibleDB:
    """
    Local SQLite database for offline Bible access
    This is a fallback when API is unavailable
    """
    
    def __init__(self, db_path='database/bible_verses.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize local Bible database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book TEXT NOT NULL,
                chapter INTEGER NOT NULL,
                verse INTEGER NOT NULL,
                text TEXT NOT NULL,
                keywords TEXT,
                UNIQUE(book, chapter, verse)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_verse(self, book, chapter, verse, text, keywords=None):
        """Add a verse to local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO verses (book, chapter, verse, text, keywords)
                VALUES (?, ?, ?, ?, ?)
            ''', (book, chapter, verse, text, json.dumps(keywords) if keywords else None))
            conn.commit()
        except Exception as e:
            print(f"Error adding verse: {e}")
        finally:
            conn.close()
    
    def get_chapter(self, book, chapter):
        """Get all verses from a chapter"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM verses WHERE book = ? AND chapter = ?
            ORDER BY verse
        ''', (book, chapter))
        
        verses = cursor.fetchall()
        conn.close()
        return [dict(v) for v in verses]
    
    def search_keyword(self, keyword):
        """Search verses by keyword"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM verses 
            WHERE text LIKE ? OR keywords LIKE ?
            LIMIT 10
        ''', (f'%{keyword}%', f'%{keyword}%'))
        
        verses = cursor.fetchall()
        conn.close()
        return [dict(v) for v in verses]
    
    def populate_common_verses(self):
        """Populate database with commonly used verses"""
        common_verses = [
            ('Philippians', 4, 6, "Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God.", ['anxiety', 'prayer', 'peace']),
            ('Philippians', 4, 7, "And the peace of God, which transcends all understanding, will guard your hearts and your minds in Christ Jesus.", ['peace', 'anxiety']),
            ('John', 3, 16, "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.", ['love', 'salvation', 'faith']),
            ('Isaiah', 41, 10, "So do not fear, for I am with you; do not be dismayed, for I am your God. I will strengthen you and help you; I will uphold you with my righteous right hand.", ['fear', 'strength', 'courage']),
            ('Jeremiah', 29, 11, "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.", ['hope', 'future', 'plans']),
            ('Psalm', 23, 1, "The Lord is my shepherd, I lack nothing.", ['provision', 'trust', 'peace']),
            ('Matthew', 6, 34, "Therefore do not worry about tomorrow, for tomorrow will worry about itself. Each day has enough trouble of its own.", ['anxiety', 'worry', 'trust']),
            ('Proverbs', 3, 5, "Trust in the Lord with all your heart and lean not on your own understanding.", ['trust', 'wisdom', 'guidance']),
            ('Proverbs', 3, 6, "In all your ways submit to him, and he will make your paths straight.", ['guidance', 'trust', 'direction']),
            ('Romans', 8, 28, "And we know that in all things God works for the good of those who love him, who have been called according to his purpose.", ['hope', 'trust', 'purpose'])
        ]
        
        for verse in common_verses:
            self.add_verse(*verse)

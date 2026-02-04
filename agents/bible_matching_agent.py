from database.bible_data import BibleAPI, LocalBibleDB
from database.full_bible_db import FullBibleDatabase

class BibleMatchingAgent:
    """
    Handles all Bible content retrieval and matching
    - Fetches specific verses/chapters
    - Matches emotional states to relevant Scripture
    - Searches for topics
    """
    
    def __init__(self):
        self.api = BibleAPI()
        self.local_db = LocalBibleDB()
        self.full_bible = FullBibleDatabase()
        
        # Comprehensive keyword to Scripture mapping
        self.keyword_map = {
            # Emotions
            'anxiety': ['Philippians 4:6-7', 'Matthew 6:34', 'Isaiah 41:10', '1 Peter 5:7', 'Psalm 55:22'],
            'fear': ['2 Timothy 1:7', 'Isaiah 41:10', 'Psalm 56:3', 'Joshua 1:9', 'Deuteronomy 31:6'],
            'sad': ['Psalm 34:18', 'Matthew 5:4', '2 Corinthians 1:3-4', 'Psalm 147:3', 'John 14:1'],
            'sadness': ['Psalm 34:18', 'Matthew 5:4', '2 Corinthians 1:3-4'],
            'lonely': ['Deuteronomy 31:6', 'Psalm 68:6', 'Matthew 28:20', 'Hebrews 13:5'],
            'angry': ['Ephesians 4:26-27', 'Proverbs 15:1', 'James 1:19-20', 'Psalm 37:8'],
            'doubt': ['James 1:6-8', 'Hebrews 11:1', 'Mark 9:24', 'Jude 1:22'],
            'guilt': ['1 John 1:9', 'Romans 8:1', 'Psalm 103:12', 'Isaiah 43:25'],
            'hopeless': ['Jeremiah 29:11', 'Romans 15:13', 'Psalm 42:5', 'Lamentations 3:22-23'],
            'weak': ['Isaiah 40:31', 'Philippians 4:13', 'Psalm 46:1', '2 Corinthians 12:9'],
            
            # Spiritual concepts
            'love': ['1 Corinthians 13:4-8', 'John 3:16', '1 John 4:8', 'Romans 8:38-39', 'John 15:12'],
            'peace': ['John 14:27', 'Philippians 4:7', 'Romans 5:1', 'Isaiah 26:3', 'Colossians 3:15'],
            'joy': ['Nehemiah 8:10', 'Psalm 16:11', 'John 15:11', 'Romans 15:13', 'Philippians 4:4'],
            'faith': ['Hebrews 11:1', 'Romans 10:17', 'James 2:17', '2 Corinthians 5:7', 'Mark 11:22'],
            'hope': ['Romans 15:13', 'Jeremiah 29:11', 'Hebrews 6:19', 'Psalm 42:11', 'Romans 8:24-25'],
            'trust': ['Proverbs 3:5-6', 'Psalm 56:3', 'Isaiah 26:4', 'Nahum 1:7', 'Psalm 37:5'],
            'prayer': ['Matthew 6:6', 'Philippians 4:6', '1 Thessalonians 5:17', 'James 5:16', 'Luke 18:1'],
            'worship': ['Psalm 95:6', 'John 4:24', 'Psalm 100:2', 'Romans 12:1', 'Hebrews 13:15'],
            
            # Life situations
            'strength': ['Philippians 4:13', 'Isaiah 40:31', 'Psalm 46:1', '2 Corinthians 12:9'],
            'wisdom': ['James 1:5', 'Proverbs 3:5-6', 'Colossians 3:16', 'Proverbs 2:6'],
            'guidance': ['Proverbs 3:5-6', 'Psalm 32:8', 'Isaiah 30:21', 'James 1:5'],
            'patience': ['James 1:3-4', 'Romans 12:12', 'Galatians 5:22', 'Psalm 37:7'],
            'forgiveness': ['1 John 1:9', 'Ephesians 4:32', 'Matthew 6:14-15', 'Colossians 3:13'],
            'healing': ['Psalm 147:3', 'Jeremiah 17:14', 'Exodus 15:26', '1 Peter 2:24'],
            'comfort': ['2 Corinthians 1:3-4', 'Psalm 23:4', 'Matthew 5:4', 'John 14:1'],
            'provision': ['Philippians 4:19', 'Matthew 6:26', 'Psalm 23:1', 'Luke 12:24'],
            
            # Common Bible words
            'beginning': ['Genesis 1:1', 'John 1:1', 'Proverbs 9:10', 'Psalm 111:10'],
            'shepherd': ['Psalm 23:1', 'John 10:11', 'Hebrews 13:20', '1 Peter 5:4'],
            'light': ['John 8:12', 'Matthew 5:14', 'Psalm 119:105', '1 John 1:5'],
            'life': ['John 10:10', 'John 14:6', 'Romans 6:23', '1 John 5:12'],
            'salvation': ['Romans 10:9', 'Ephesians 2:8-9', 'Acts 4:12', 'John 3:16'],
            'grace': ['Ephesians 2:8-9', '2 Corinthians 12:9', 'Romans 3:24', 'Titus 2:11'],
            'eternal': ['John 3:16', 'John 17:3', '1 John 5:13', 'Romans 6:23'],
            'kingdom': ['Matthew 6:33', 'Luke 17:21', 'Mark 1:15', 'Matthew 5:3'],
            'glory': ['Romans 8:18', '2 Corinthians 4:17', 'Psalm 19:1', 'Isaiah 60:1'],
            'heaven': ['Matthew 6:20', 'Philippians 3:20', 'John 14:2', 'Revelation 21:4'],
        }
        
        # Legacy emotion_map for backward compatibility
        self.emotion_map = {
            'anxiety': {'keywords': ['anxious', 'worried', 'worry', 'stress', 'overwhelmed'], 'verses': self.keyword_map['anxiety']},
            'fear': {'keywords': ['afraid', 'scared', 'fear', 'fearful', 'terror'], 'verses': self.keyword_map['fear']},
            'sadness': {'keywords': ['sad', 'depressed', 'down', 'sorrow', 'grief'], 'verses': self.keyword_map['sad']},
            'loneliness': {'keywords': ['lonely', 'alone', 'isolated', 'abandoned'], 'verses': self.keyword_map['lonely']},
            'anger': {'keywords': ['angry', 'mad', 'furious', 'rage', 'frustrated'], 'verses': self.keyword_map['angry']},
            'doubt': {'keywords': ['doubt', 'uncertain', 'confused', 'questioning'], 'verses': self.keyword_map['doubt']},
            'guilt': {'keywords': ['guilty', 'shame', 'regret', 'condemned'], 'verses': self.keyword_map['guilt']},
            'hope': {'keywords': ['hopeless', 'despair', 'discouraged', 'giving up'], 'verses': self.keyword_map['hopeless']},
            'strength': {'keywords': ['weak', 'tired', 'exhausted', 'weary'], 'verses': self.keyword_map['weak']},
            'guidance': {'keywords': ['lost', 'direction', 'guidance', 'wisdom', 'decision'], 'verses': self.keyword_map['guidance']},
        }
    
    def fetch_chapters(self, book, start_chapter, count=2):
        """
        Fetch multiple chapters for daily reading
        Now uses full Bible database for faster retrieval
        """
        chapters = []
        
        for i in range(count):
            chapter_num = start_chapter + i
            
            # Try full Bible database first
            if self.full_bible and self.full_bible.conn:
                verses = self.full_bible.get_chapter(book, chapter_num)
                if verses:
                    # Combine all verse texts
                    text = ' '.join([v['text'] for v in verses])
                    chapters.append({
                        'book': book,
                        'chapter': chapter_num,
                        'text': text,
                        'reference': f"{book} {chapter_num}",
                        'verses': verses
                    })
                    continue
            
            # Fallback to API
            chapter_data = self.api.get_chapter(book, chapter_num)
            
            if chapter_data:
                chapters.append({
                    'book': book,
                    'chapter': chapter_num,
                    'text': chapter_data['text'],
                    'reference': chapter_data['reference'],
                    'verses': chapter_data.get('verses', [])
                })
            else:
                # Try local DB as last resort
                local_verses = self.local_db.get_chapter(book, chapter_num)
                if local_verses:
                    text = ' '.join([v['text'] for v in local_verses])
                    chapters.append({
                        'book': book,
                        'chapter': chapter_num,
                        'text': text,
                        'reference': f"{book} {chapter_num}",
                        'verses': local_verses
                    })
        
        return chapters
                   
    
    def find_relevant_verses(self, emotions, message=None):
        """
        Find Bible verses relevant to emotional state
        emotions: list of emotion keywords
        message: original user message for context
        """
        matched_verses = []
        seen_references = set()
        
        # Match emotions to verses
        for emotion in emotions:
            for emotion_key, emotion_data in self.emotion_map.items():
                if emotion in emotion_data['keywords'] or emotion == emotion_key:
                    # Get verses for this emotion
                    for verse_ref in emotion_data['verses'][:2]:
                        if verse_ref not in seen_references:
                            verse_data = self.api.get_verse(verse_ref)
                            if verse_data:
                                verse_data['emotion_matched'] = emotion_key
                                matched_verses.append(verse_data)
                                seen_references.add(verse_ref)
        
        # If no matches, provide general comfort verses
        if not matched_verses:
            general_verses = ['Psalm 46:1', 'Romans 8:28', 'Philippians 4:6']
            for ref in general_verses:
                verse_data = self.api.get_verse(ref)
                if verse_data:
                    verse_data['emotion_matched'] = 'general_comfort'
                    matched_verses.append(verse_data)
        
        return matched_verses[:3]
    
    def search_verses(self, topic):
        """
        Enhanced search with full Bible database
        Priority: Full Bible DB > Keyword Map > API > Local DB
        """
        topic_lower = topic.lower()
        verses = []
        
        # First, try full Bible database (TRUE full-text search!)
        if self.full_bible and self.full_bible.conn:
            results = self.full_bible.search_text(topic, max_results=5)
            if results:
                # Format to match expected structure
                for result in results:
                    verses.append({
                        'reference': result['reference'],
                        'text': result['text'],
                        'translation': 'KJV'
                    })
                return verses
        
        # Fallback to keyword map for common searches
        if topic_lower in self.keyword_map:
            verse_refs = self.keyword_map[topic_lower]
            for ref in verse_refs[:5]:
                verse_data = self.api.get_verse(ref)
                if verse_data:
                    verses.append(verse_data)
            if verses:
                return verses
        
        # Partial keyword match
        for keyword, verse_refs in self.keyword_map.items():
            if topic_lower in keyword or keyword in topic_lower:
                for ref in verse_refs[:3]:
                    verse_data = self.api.get_verse(ref)
                    if verse_data:
                        verses.append(verse_data)
                if verses:
                    return verses
        
        # Fallback to API
        if not verses:
            verses = self.api.search_verses(topic)
        
        # Last resort: local DB
        if not verses:
            verses = self.local_db.search_keyword(topic)
        
        return verses if verses else []
        

    
    def get_verse(self, reference):
        """Get a specific verse by reference"""
        verse_data = self.api.get_verse(reference)
        
        if not verse_data:
            # Try parsing and getting from local DB
            parts = reference.split()
            if len(parts) >= 2:
                book = ' '.join(parts[:-1])
                chapter_verse = parts[-1].split(':')
                if len(chapter_verse) == 2:
                    local_verses = self.local_db.get_chapter(book, int(chapter_verse[0]))
                    for v in local_verses:
                        if v['verse'] == int(chapter_verse[1]):
                            verse_data = {
                                'reference': reference,
                                'text': v['text'],
                                'translation': 'KJV'
                            }
                            break
        
        return verse_data
    
    def get_reflection_question(self, book, chapter, topic=None):
        """
        Generate a reflection question based on the passage
        """
        questions = {
            'Matthew': [
                "How does this passage challenge your understanding of discipleship?",
                "What does Jesus' teaching here reveal about God's kingdom?",
                "How can you apply this teaching in your daily life?"
            ],
            'Psalms': [
                "What does this psalm teach you about worship?",
                "How can you make this prayer your own today?",
                "What aspect of God's character is highlighted here?"
            ],
            'Proverbs': [
                "What wisdom can you apply to a current situation?",
                "How does this proverb align with or challenge your thinking?",
                "What practical step can you take based on this wisdom?"
            ],
            'Romans': [
                "How does this deepen your understanding of the Gospel?",
                "What does this passage teach about grace?",
                "How should this truth transform your daily walk?"
            ],
            'default': [
                "What is God teaching you through this passage?",
                "How can you apply this truth today?",
                "What stands out to you most in this reading?",
                "How does this passage point to Christ?",
                "What action will you take in response to this Scripture?"
            ]
        }

    def get_verse_of_the_day(self):
        """Get an inspiring verse for today"""
        import random
        from datetime import datetime
        
        # Seed random with today's date so same verse shows all day
        today = datetime.now().strftime('%Y-%m-%d')
        random.seed(today)
        
        daily_verses = [
            'Philippians 4:13', 'Jeremiah 29:11', 'Proverbs 3:5-6',
            'Isaiah 40:31', 'Romans 8:28', 'Psalm 23:1',
            'John 3:16', 'Matthew 6:33', 'Joshua 1:9',
            'Psalm 46:1', '2 Corinthians 12:9', 'Philippians 4:6-7',
            'Isaiah 41:10', 'Proverbs 16:3', 'Psalm 37:4',
            'Matthew 11:28', 'Romans 15:13', 'Psalm 118:24',
            'Colossians 3:23', 'James 1:5'
        ]
        
        verse_ref = random.choice(daily_verses)
        verse_data = self.get_verse(verse_ref)
        
        return verse_data

        # Get book-specific questions or default
        book_questions = questions.get(book, questions['default'])
        
        # Simple random selection
        import random
        return random.choice(book_questions)

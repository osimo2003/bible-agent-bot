import re
from database.bible_data import BibleAPI, LocalBibleDB
from database.full_bible_db import FullBibleDatabase
from agents.keyword_extractor import KeywordExtractor

class BibleMatchingAgent:
    """
    Handles Bible content retrieval and matching
    Returns 5 verses: 3 NT + 2 OT
    """
    
    def __init__(self):
        self.api = BibleAPI()
        self.local_db = LocalBibleDB()
        self.full_bible = FullBibleDatabase()
        self.keyword_extractor = KeywordExtractor()
        
        # Curated keyword to Scripture mapping
        self.keyword_map = {
            'anxiety': ['Philippians 4:6-7', 'Matthew 6:34', 'Isaiah 41:10', '1 Peter 5:7', 'Psalm 55:22'],
            'fear': ['2 Timothy 1:7', 'Isaiah 41:10', 'Psalm 56:3', 'Joshua 1:9', 'Deuteronomy 31:6'],
            'sadness': ['Psalm 34:18', 'Matthew 5:4', '2 Corinthians 1:3-4', 'Psalm 147:3', 'Revelation 21:4'],
            'sorrow': ['Psalm 34:18', 'John 16:22', 'Isaiah 53:3', 'Revelation 21:4', 'Psalm 30:5'],
            'loneliness': ['Deuteronomy 31:6', 'Psalm 68:6', 'Matthew 28:20', 'Hebrews 13:5', 'Isaiah 41:10'],
            'anger': ['Ephesians 4:26-27', 'Proverbs 15:1', 'James 1:19-20', 'Psalm 37:8', 'Colossians 3:8'],
            'doubt': ['James 1:6-8', 'Hebrews 11:1', 'Mark 9:24', 'Jude 1:22', 'Matthew 14:31'],
            'guilt': ['1 John 1:9', 'Romans 8:1', 'Psalm 103:12', 'Isaiah 43:25', 'Hebrews 10:22'],
            'despair': ['Jeremiah 29:11', 'Romans 15:13', 'Psalm 42:5', 'Lamentations 3:22-23', '2 Corinthians 4:8-9'],
            'weakness': ['Isaiah 40:31', 'Philippians 4:13', 'Psalm 46:1', '2 Corinthians 12:9', 'Nehemiah 8:10'],
            'temptation': ['1 Corinthians 10:13', 'James 1:12', 'Hebrews 4:15-16', 'Matthew 26:41', 'James 4:7'],
            'suffering': ['Romans 8:18', '2 Corinthians 4:17', 'James 1:2-4', '1 Peter 5:10', 'Psalm 34:19'],
            'comfort': ['2 Corinthians 1:3-4', 'Psalm 23:4', 'Matthew 5:4', 'John 14:1', 'Isaiah 66:13'],
            'love': ['1 Corinthians 13:4-7', 'John 3:16', '1 John 4:8', 'Romans 8:38-39', 'John 15:12'],
            'peace': ['John 14:27', 'Philippians 4:7', 'Romans 5:1', 'Isaiah 26:3', 'Colossians 3:15'],
            'joy': ['Nehemiah 8:10', 'Psalm 16:11', 'John 15:11', 'Romans 15:13', 'Philippians 4:4'],
            'faith': ['Hebrews 11:1', 'Romans 10:17', 'James 2:17', '2 Corinthians 5:7', 'Mark 11:22'],
            'hope': ['Romans 15:13', 'Jeremiah 29:11', 'Hebrews 6:19', 'Psalm 42:11', 'Romans 8:24-25'],
            'trust': ['Proverbs 3:5-6', 'Psalm 56:3', 'Isaiah 26:4', 'Nahum 1:7', 'Psalm 37:5'],
            'grace': ['Ephesians 2:8-9', '2 Corinthians 12:9', 'Romans 3:24', 'Titus 2:11', 'John 1:16'],
            'mercy': ['Lamentations 3:22-23', 'Ephesians 2:4-5', 'Psalm 103:8', 'Micah 7:18', 'Hebrews 4:16'],
            'prayer': ['Matthew 6:6', 'Philippians 4:6', '1 Thessalonians 5:17', 'James 5:16', 'Luke 18:1'],
            'worship': ['Psalm 95:6', 'John 4:24', 'Psalm 100:2', 'Romans 12:1', 'Hebrews 13:15'],
            'salvation': ['Romans 10:9', 'Ephesians 2:8-9', 'Acts 4:12', 'John 3:16', 'Titus 3:5'],
            'forgiveness': ['1 John 1:9', 'Ephesians 4:32', 'Matthew 6:14-15', 'Colossians 3:13', 'Psalm 103:12'],
            'repentance': ['Acts 3:19', '2 Chronicles 7:14', '1 John 1:9', 'Luke 15:7', 'Acts 2:38'],
            'guidance': ['Proverbs 3:5-6', 'Psalm 32:8', 'Isaiah 30:21', 'James 1:5', 'Proverbs 16:9'],
            'wisdom': ['James 1:5', 'Proverbs 3:5-6', 'Colossians 3:16', 'Proverbs 2:6', 'Proverbs 9:10'],
            'strength': ['Philippians 4:13', 'Isaiah 40:31', 'Psalm 46:1', '2 Corinthians 12:9', 'Nehemiah 8:10'],
            'patience': ['James 1:3-4', 'Romans 12:12', 'Galatians 5:22', 'Psalm 37:7', 'Ecclesiastes 7:8'],
            'healing': ['Psalm 147:3', 'Jeremiah 17:14', 'Exodus 15:26', '1 Peter 2:24', 'James 5:15'],
            'provision': ['Philippians 4:19', 'Matthew 6:26', 'Psalm 23:1', 'Luke 12:24', 'Malachi 3:10'],
            'protection': ['Psalm 91:1-2', 'Psalm 121:7-8', 'Isaiah 54:17', '2 Thessalonians 3:3', 'Proverbs 18:10'],
            'rest': ['Matthew 11:28-30', 'Psalm 23:2', 'Exodus 33:14', 'Hebrews 4:9-10', 'Isaiah 30:15'],
            'marriage': ['Ephesians 5:25', 'Genesis 2:24', '1 Corinthians 13:4-7', 'Colossians 3:19', 'Proverbs 18:22'],
            'family': ['Psalm 127:3', 'Proverbs 22:6', 'Ephesians 6:4', 'Joshua 24:15', 'Colossians 3:21'],
            'children': ['Psalm 127:3', 'Proverbs 22:6', 'Mark 10:14', 'Ephesians 6:1-3', 'Deuteronomy 6:6-7'],
            'enemies': ['Matthew 5:44', 'Romans 12:20', 'Proverbs 25:21', 'Luke 6:27-28', 'Exodus 23:4-5'],
            'friendship': ['Proverbs 17:17', 'Proverbs 18:24', 'John 15:13', 'Ecclesiastes 4:9-10', 'Proverbs 27:17'],
            'death': ['John 11:25-26', 'Psalm 23:4', '1 Corinthians 15:55', 'Philippians 1:21', 'Revelation 21:4'],
            'eternal': ['John 3:16', 'John 17:3', '1 John 5:13', 'Romans 6:23', 'John 10:28'],
            'heaven': ['John 14:2-3', 'Philippians 3:20', 'Revelation 21:4', 'Matthew 6:20', '2 Corinthians 5:1'],
            'purpose': ['Jeremiah 29:11', 'Romans 8:28', 'Ephesians 2:10', 'Proverbs 19:21', 'Psalm 138:8'],
            'help': ['Psalm 46:1', 'Isaiah 41:10', 'Hebrews 4:16', 'Psalm 121:1-2', 'Psalm 34:17'],
            'courage': ['Joshua 1:9', 'Deuteronomy 31:6', 'Isaiah 41:10', '2 Timothy 1:7', 'Psalm 27:1'],
            'contentment': ['Philippians 4:11-12', '1 Timothy 6:6', 'Hebrews 13:5', 'Proverbs 19:23', 'Ecclesiastes 5:10'],
            'identity': ['Ephesians 2:10', '1 Peter 2:9', '2 Corinthians 5:17', 'Galatians 2:20', 'Psalm 139:14'],
            'perseverance': ['James 1:12', 'Romans 5:3-4', 'Galatians 6:9', 'Hebrews 12:1', '2 Corinthians 4:16-17'],
            'victory': ['1 Corinthians 15:57', 'Romans 8:37', '1 John 5:4', '2 Corinthians 2:14', 'Revelation 12:11'],
            'freedom': ['John 8:36', 'Galatians 5:1', '2 Corinthians 3:17', 'Romans 6:18', 'Isaiah 61:1'],
            'purity': ['Psalm 51:10', 'Matthew 5:8', '1 John 1:9', 'Philippians 4:8', '2 Timothy 2:22'],
            'grief': ['Psalm 34:18', 'Matthew 5:4', '2 Corinthians 1:3-4', 'Revelation 21:4', 'John 14:1'],
        }
        
        self.emotion_map = {
            'anxiety': {'keywords': ['anxious', 'worried', 'stress', 'overwhelmed'], 'verses': self.keyword_map['anxiety']},
            'fear': {'keywords': ['afraid', 'scared', 'fearful'], 'verses': self.keyword_map['fear']},
            'sadness': {'keywords': ['sad', 'depressed', 'sorrow', 'grief'], 'verses': self.keyword_map['sadness']},
            'loneliness': {'keywords': ['lonely', 'alone', 'isolated'], 'verses': self.keyword_map['loneliness']},
            'anger': {'keywords': ['angry', 'mad', 'furious'], 'verses': self.keyword_map['anger']},
        }
    
    def fetch_chapters(self, book, start_chapter, count=2):
        """Fetch chapters for daily reading"""
        chapters = []
        for i in range(count):
            chapter_num = start_chapter + i
            if self.full_bible and self.full_bible.conn:
                verses = self.full_bible.get_chapter(book, chapter_num)
                if verses:
                    text = ' '.join([v['text'] for v in verses])
                    chapters.append({
                        'book': book, 'chapter': chapter_num, 'text': text,
                        'reference': f"{book} {chapter_num}", 'verses': verses
                    })
        return chapters
    
    def find_relevant_verses(self, emotions, message=None):
        """Find verses for emotional state"""
        matched_verses = []
        seen = set()
        for emotion in emotions:
            for key, data in self.emotion_map.items():
                if emotion in data['keywords'] or emotion == key:
                    for ref in data['verses'][:2]:
                        if ref not in seen:
                            verse = self.api.get_verse(ref)
                            if verse:
                                verse['emotion_matched'] = key
                                matched_verses.append(verse)
                                seen.add(ref)
        return matched_verses[:3]
    
    def search_verses(self, topic):
        """
        Smart search - returns 5 verses: 3 NT + 2 OT
        Handles words, phrases, sentences, questions
        """
        topic_lower = topic.lower().strip()
        keywords = self.keyword_extractor.extract(topic_lower)
        print(f"🔍 Extracted keywords: {keywords}")
        
        all_verses = []
        seen = set()
        
        # Search curated map first
        for keyword in keywords:
            if keyword in self.keyword_map:
                for ref in self.keyword_map[keyword]:
                    if ref not in seen:
                        verse = self._get_verse_from_reference(ref)
                        if verse:
                            all_verses.append(verse)
                            seen.add(ref)
        
        # Search database if needed
        if len(all_verses) < 10:
            for keyword in keywords[:5]:
                for testament in ['New', 'Old']:
                    results = self.full_bible.search_text(keyword, max_results=3, testament=testament)
                    for verse in results:
                        if verse['reference'] not in seen:
                            all_verses.append(verse)
                            seen.add(verse['reference'])
        
        # Direct phrase search
        if len(all_verses) < 5:
            results = self.full_bible.search_text(topic_lower, max_results=10)
            for verse in results:
                if verse['reference'] not in seen:
                    all_verses.append(verse)
                    seen.add(verse['reference'])
        
        return self._balance_testaments(all_verses, nt_count=3, ot_count=2)
    
    def _get_verse_from_reference(self, reference):
        """Get verse from reference string"""
        match = re.match(r'([1-3]?\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(\d+):(\d+)(?:-(\d+))?', reference)
        if match:
            book, chapter = match.group(1).strip(), int(match.group(2))
            verse_start = int(match.group(3))
            verse_end = int(match.group(4)) if match.group(4) else None
            
            verse_data = self.full_bible.get_verse(book, chapter, verse_start)
            if verse_data:
                if verse_end:
                    texts = []
                    for v in range(verse_start, verse_end + 1):
                        vd = self.full_bible.get_verse(book, chapter, v)
                        if vd:
                            texts.append(vd['text'])
                    verse_data['text'] = ' '.join(texts)
                    verse_data['reference'] = f"{book} {chapter}:{verse_start}-{verse_end}"
                return verse_data
        return None
    
    def _balance_testaments(self, verses, nt_count=3, ot_count=2):
        """Balance: 3 NT + 2 OT"""
        nt = [v for v in verses if v.get('testament') == 'New']
        ot = [v for v in verses if v.get('testament') == 'Old']
        unknown = [v for v in verses if v.get('testament') not in ['New', 'Old']]
        
        for v in unknown:
            v['testament'] = self._determine_testament(v.get('book', ''))
            (nt if v['testament'] == 'New' else ot).append(v)
        
        result = nt[:nt_count] + ot[:ot_count]
        
        if len(result) < nt_count + ot_count:
            for v in (nt[nt_count:] + ot[ot_count:]):
                if len(result) >= nt_count + ot_count:
                    break
                if v not in result:
                    result.append(v)
        
        return result[:nt_count + ot_count]
    
    def _determine_testament(self, book_name):
        """Determine testament"""
        nt_books = ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
                    '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
                    'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
                    '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews',
                    'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
                    'Jude', 'Revelation']
        return 'New' if any(b.lower() in book_name.lower() for b in nt_books) else 'Old'
    
    def get_verse(self, reference):
        return self._get_verse_from_reference(reference)
    
    def get_verse_by_reference(self, reference):
        """Get verse(s) by reference"""
        reference = reference.strip()
        match = re.match(r'^([1-3]?\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(\d+)(?::(\d+))?(?:-(\d+))?$', reference, re.IGNORECASE)
        if not match:
            return None
        
        book, chapter = match.group(1).strip(), int(match.group(2))
        verse_start = int(match.group(3)) if match.group(3) else None
        verse_end = int(match.group(4)) if match.group(4) else None
        
        if verse_start is None:
            verses = self.full_bible.get_chapter(book, chapter)
            if verses:
                return {'reference': f"{book} {chapter}", 'book': book, 'chapter': chapter,
                        'verses': verses[:20], 'text': '\n'.join([f"{v['verse']}. {v['text']}" for v in verses[:20]]),
                        'is_chapter': True}
            return None
        
        if verse_end is None:
            verse = self.full_bible.get_verse(book, chapter, verse_start)
            if verse:
                return {'reference': f"{book} {chapter}:{verse_start}", 'book': book,
                        'chapter': chapter, 'verse': verse_start, 'text': verse['text'], 'is_chapter': False}
            return None
        
        verses = [self.full_bible.get_verse(book, chapter, v) for v in range(verse_start, verse_end + 1)]
        verses = [v for v in verses if v]
        if verses:
            return {'reference': f"{book} {chapter}:{verse_start}-{verse_end}", 'book': book, 'chapter': chapter,
                    'verses': verses, 'text': '\n'.join([f"{v['verse']}. {v['text']}" for v in verses]), 'is_chapter': False}
        return None
    
    def get_reflection_question(self, book, chapter, topic=None):
        import random
        questions = {'default': ["What is God teaching you?", "How can you apply this today?", "What stands out to you?"]}
        return random.choice(questions.get(book, questions['default']))
    
    def get_verse_of_the_day(self):
        import random
        from datetime import datetime
        random.seed(datetime.now().strftime('%Y-%m-%d'))
        verses = ['Philippians 4:13', 'Jeremiah 29:11', 'Proverbs 3:5-6', 'Isaiah 40:31', 'Romans 8:28', 'John 3:16']
        return self.get_verse(random.choice(verses))

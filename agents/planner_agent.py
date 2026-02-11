import re
from datetime import datetime

class PlannerAgent:
    """
    Main orchestrator - decides what action to take based on user input
    Routes to appropriate specialized agents
    """
    
    def __init__(self, db):
        self.db = db
        self.intents = {
            'daily_reading': ['read today', 'daily reading', 'next chapter', 'continue reading', "today's reading"],
            'challenge': ['help me', 'i am struggling', 'feeling anxious', 'i am afraid', 'worried about', 'feeling sad', 'depressed', 'angry at', 'feeling lonely'],
            'bookmark': ['save', 'bookmark', 'remember', 'mark'],
            'bookmark_response': ['save ', 'bookmark '],
            'progress': ['my progress', 'how far', 'what chapter am i', 'where am i'],
            'search_triggers': ['find', 'search', 'verses about', 'verse about', 'show me', 'scripture about', 'what does the bible say about', 'bible says about', 'look for', 'look up'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good evening', 'good afternoon'],
            'complete': ['done', 'finished', 'completed'],
            'bookmark_no': ['no thanks', 'no', 'skip', 'not now']
        }
        
        # Common Bible topics - single words that should trigger search
        self.bible_topics = [
            'love', 'faith', 'hope', 'grace', 'peace', 'joy', 'wisdom', 'strength',
            'forgiveness', 'mercy', 'salvation', 'prayer', 'healing', 'trust',
            'patience', 'kindness', 'humility', 'courage', 'fear', 'anxiety',
            'death', 'life', 'heaven', 'hell', 'sin', 'repentance', 'baptism',
            'holy spirit', 'jesus', 'god', 'father', 'christ', 'lord', 'king',
            'blessing', 'worship', 'praise', 'thanksgiving', 'obedience',
            'righteousness', 'justice', 'truth', 'light', 'darkness', 'evil',
            'temptation', 'devil', 'satan', 'angel', 'miracle', 'resurrection',
            'eternal', 'glory', 'kingdom', 'gospel', 'commandment', 'covenant',
            'prophet', 'apostle', 'disciple', 'church', 'marriage', 'family',
            'children', 'money', 'wealth', 'poverty', 'work', 'rest', 'sabbath'
        ]
        
        # Bible book names for reference detection
        self.bible_books = [
            'genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy',
            'joshua', 'judges', 'ruth', '1 samuel', '2 samuel',
            '1 kings', '2 kings', '1 chronicles', '2 chronicles',
            'ezra', 'nehemiah', 'esther', 'job', 'psalms', 'psalm',
            'proverbs', 'ecclesiastes', 'song of solomon', 'isaiah',
            'jeremiah', 'lamentations', 'ezekiel', 'daniel', 'hosea',
            'joel', 'amos', 'obadiah', 'jonah', 'micah', 'nahum',
            'habakkuk', 'zephaniah', 'haggai', 'zechariah', 'malachi',
            'matthew', 'mark', 'luke', 'john', 'acts', 'romans',
            '1 corinthians', '2 corinthians', 'galatians', 'ephesians',
            'philippians', 'colossians', '1 thessalonians', '2 thessalonians',
            '1 timothy', '2 timothy', 'titus', 'philemon', 'hebrews',
            'james', '1 peter', '2 peter', '1 john', '2 john', '3 john',
            'jude', 'revelation'
        ]
    
    def analyze_intent(self, message):
        """
        Determine user intent from message
        Returns: intent type and extracted data
        """
        message_lower = message.lower().strip()
        
        # Check for "No thanks" button click (bookmark decline)
        if any(phrase in message_lower for phrase in self.intents['bookmark_no']):
            return {'type': 'bookmark_no', 'data': None}
        
        # Check for "Save all" command from button click
        if 'save all:' in message_lower:
            parts = message.split('save all:', 1)
            if len(parts) > 1:
                refs = [r.strip() for r in parts[1].split(',')]
                return {'type': 'bookmark_all', 'data': {'references': refs}}
        
        # Check for verse reference FIRST (e.g., "John 3:16", "Psalm 23:1")
        verse_ref = self._extract_verse_reference(message)
        if verse_ref:
            return {'type': 'get_verse', 'data': {'reference': verse_ref}}
        
        # Check for greetings (exact or start of message)
        for greeting in self.intents['greeting']:
            if message_lower == greeting or message_lower.startswith(greeting + ' '):
                return {'type': 'greeting', 'data': None}
        
        # Check for completion markers 
        if message_lower in ['done', 'finished', 'completed']:
            return {'type': 'complete', 'data': None}
        
        # Check for bookmark request (from button click or manual command)
        if any(word in message_lower for word in self.intents['bookmark_response']):
            verse_ref = self._extract_verse_reference(message)
            if verse_ref:
                return {'type': 'bookmark', 'data': {'reference': verse_ref}}
        
        # Check for progress inquiry
        if any(phrase in message_lower for phrase in self.intents['progress']):
            return {'type': 'progress', 'data': None}
        
        # Check for daily reading request
        if any(phrase in message_lower for phrase in self.intents['daily_reading']):
            return {'type': 'daily_reading', 'data': None}
        
        # Check for explicit search request
        if any(trigger in message_lower for trigger in self.intents['search_triggers']):
            topic = self._extract_topic(message_lower)
            return {'type': 'search', 'data': {'topic': topic}}
        
        # Check for emotional/challenge keywords (multi-word phrases)
        emotions = []
        challenge_words = ['struggle', 'struggling', 'anxious', 'anxiety', 'afraid', 'fear', 
                          'worried', 'worry', 'sad', 'depressed', 'depression', 'angry', 
                          'anger', 'lonely', 'loneliness', 'hopeless', 'desperate', 'hurt']
        
        for word in challenge_words:
            if word in message_lower:
                emotions.append(word)
        
        if emotions:
            return {'type': 'challenge', 'data': {'emotions': emotions, 'message': message}}
        
        # Check if single word or short phrase matches Bible topic
        if self._is_bible_topic(message_lower):
            return {'type': 'search', 'data': {'topic': message_lower}}
        
        # Check if it looks like a search query (short phrase, no question structure)
        if self._looks_like_search(message_lower):
            return {'type': 'search', 'data': {'topic': message_lower}}
        
        # Default to general conversation
        return {'type': 'general', 'data': {'message': message}}
    
    def _extract_verse_reference(self, message):
        """
        Extract Bible verse reference from message
        Handles: John 3:16, 1 Corinthians 13:4-7, Psalm 23, Romans 8:28
        """
        message_clean = message.strip()
        
        # Pattern for books with numbers (1 John, 2 Kings, etc.)
        pattern_numbered = r'^([1-3])\s*([A-Za-z]+)\s+(\d+)(?::(\d+))?(?:-(\d+))?$'
        
        # Pattern for regular books (John, Romans, etc.)
        pattern_regular = r'^([A-Za-z]+)\s+(\d+)(?::(\d+))?(?:-(\d+))?$'
        
        # Pattern for "Song of Solomon" style
        pattern_multi_word = r'^(song\s+of\s+solomon)\s+(\d+)(?::(\d+))?(?:-(\d+))?$'
        
        # Try numbered book pattern (1 John 3:16)
        match = re.match(pattern_numbered, message_clean, re.IGNORECASE)
        if match:
            book_num = match.group(1)
            book_name = match.group(2)
            chapter = match.group(3)
            verse_start = match.group(4)
            verse_end = match.group(5)
            
            full_book = f"{book_num} {book_name}"
            
            if self._is_valid_book(full_book):
                ref = f"{full_book} {chapter}"
                if verse_start:
                    ref += f":{verse_start}"
                    if verse_end:
                        ref += f"-{verse_end}"
                return ref
        
        # Try multi-word book pattern (Song of Solomon)
        match = re.match(pattern_multi_word, message_clean, re.IGNORECASE)
        if match:
            book_name = match.group(1)
            chapter = match.group(2)
            verse_start = match.group(3)
            verse_end = match.group(4)
            
            ref = f"{book_name} {chapter}"
            if verse_start:
                ref += f":{verse_start}"
                if verse_end:
                    ref += f"-{verse_end}"
            return ref
        
        # Try regular book pattern (John 3:16)
        match = re.match(pattern_regular, message_clean, re.IGNORECASE)
        if match:
            book_name = match.group(1)
            chapter = match.group(2)
            verse_start = match.group(3)
            verse_end = match.group(4)
            
            if self._is_valid_book(book_name):
                ref = f"{book_name} {chapter}"
                if verse_start:
                    ref += f":{verse_start}"
                    if verse_end:
                        ref += f"-{verse_end}"
                return ref
        
        return None
    
    def _is_valid_book(self, book_name):
        """Check if the book name is a valid Bible book"""
        book_lower = book_name.lower().strip()
        
        for book in self.bible_books:
            if book_lower == book or book_lower == book.replace(' ', ''):
                return True
            if book.startswith(book_lower) and len(book_lower) >= 3:
                return True
        
        return False
    
    def _is_bible_topic(self, message):
        """Check if message is a common Bible topic"""
        message_clean = message.strip().lower()
        
        if message_clean in self.bible_topics:
            return True
        
        for topic in self.bible_topics:
            if topic in message_clean and len(message_clean) < 50:
                return True
        
        return False
    
    def _looks_like_search(self, message):
        """Determine if a message looks like a search query"""
        words = message.split()
        
        if len(words) <= 5 and len(words) >= 1:
            if not any(g in message for g in self.intents['greeting']):
                if message not in ['done', 'finished', 'completed', 'yes', 'no', 'ok', 'okay']:
                    return True
        
        return False
    
    def _extract_topic(self, message):
        """Extract the topic/keyword from search messages"""
        message_lower = message.lower().strip()
        
        patterns = [
            r'what does the bible say about\s+(.+)',
            r'bible says about\s+(.+)',
            r'scripture about\s+(.+)',
            r'verses? about\s+(.+)',
            r'find verses? (?:about|on|for)\s+(.+)',
            r'find\s+(.+)',
            r'search for\s+(.+)',
            r'search\s+(.+)',
            r'show me verses? (?:about|on|for)\s+(.+)',
            r'show me\s+(.+)',
            r'look for\s+(.+)',
            r'look up\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                topic = match.group(1).strip()
                topic = re.sub(r'\s+(please|thanks|thank you|in the bible)$', '', topic)
                return topic
        
        triggers = ['find', 'search', 'show me', 'look for', 'look up', 'verses about', 
                   'verse about', 'what does the bible say about', 'scripture about']
        
        result = message_lower
        for trigger in sorted(triggers, key=len, reverse=True):
            result = result.replace(trigger, '')
        
        result = result.strip()
        result = re.sub(r'^(about|for|on)\s+', '', result)
        result = re.sub(r'\s+(about|for|on)$', '', result)
        
        return result if result else message_lower
    
    def plan_action(self, user_id, message):
        """
        Main planning method
        Returns: action plan with agent to call and data
        """
        intent = self.analyze_intent(message)
        
        plan = {
            'intent': intent['type'],
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'actions': []
        }
        
        if intent['type'] == 'greeting':
            plan['actions'] = [{
                'agent': 'response_composer',
                'action': 'greet',
                'data': {'user_id': user_id}
            }]
        
        elif intent['type'] == 'daily_reading':
            plan['actions'] = [
                {
                    'agent': 'memory',
                    'action': 'get_next_chapters',
                    'data': {'user_id': user_id, 'count': 2}
                },
                {
                    'agent': 'bible_matching',
                    'action': 'fetch_chapters',
                    'data': {}
                },
                {
                    'agent': 'response_composer',
                    'action': 'present_daily_reading',
                    'data': {}
                }
            ]
        
        elif intent['type'] == 'challenge':
            plan['actions'] = [
                {
                    'agent': 'bible_matching',
                    'action': 'find_relevant_verses',
                    'data': intent['data']
                },
                {
                    'agent': 'response_composer',
                    'action': 'comfort_response',
                    'data': intent['data']
                }
            ]
        
        elif intent['type'] == 'bookmark':
            plan['actions'] = [
                {
                    'agent': 'memory',
                    'action': 'save_bookmark',
                    'data': intent['data']
                },
                {
                    'agent': 'response_composer',
                    'action': 'confirm_bookmark',
                    'data': intent['data']
                }
            ]
        
        elif intent['type'] == 'bookmark_all':
            plan['actions'] = [
                {
                    'agent': 'memory',
                    'action': 'save_multiple_bookmarks',
                    'data': intent['data']
                },
                {
                    'agent': 'response_composer',
                    'action': 'confirm_multiple_bookmarks',
                    'data': intent['data']
                }
            ]
        
        elif intent['type'] == 'bookmark_no':
            plan['actions'] = [
                {
                    'agent': 'response_composer',
                    'action': 'acknowledge_no_bookmark',
                    'data': {}
                }
            ]
        
        elif intent['type'] == 'progress':
            plan['actions'] = [
                {
                    'agent': 'memory',
                    'action': 'get_progress',
                    'data': {'user_id': user_id}
                },
                {
                    'agent': 'response_composer',
                    'action': 'show_progress',
                    'data': {}
                }
            ]
        
        elif intent['type'] == 'complete':
            plan['actions'] = [
                {
                    'agent': 'memory',
                    'action': 'mark_complete',
                    'data': {'user_id': user_id}
                },
                {
                    'agent': 'response_composer',
                    'action': 'celebrate_completion',
                    'data': {}
                }
            ]
        
        elif intent['type'] == 'search':
            plan['actions'] = [
                {
                    'agent': 'bible_matching',
                    'action': 'search_verses',
                    'data': intent['data']
                },
                {
                    'agent': 'response_composer',
                    'action': 'present_search_results',
                    'data': intent['data']
                }
            ]
        
        elif intent['type'] == 'get_verse':
            plan['actions'] = [
                {
                    'agent': 'bible_matching',
                    'action': 'get_specific_verse',
                    'data': intent['data']
                },
                {
                    'agent': 'response_composer',
                    'action': 'present_verse',
                    'data': intent['data']
                }
            ]
        
        else:
            plan['actions'] = [
                {
                    'agent': 'response_composer',
                    'action': 'general_response',
                    'data': intent['data']
                }
            ]
        
        return plan

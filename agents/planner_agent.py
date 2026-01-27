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
            'daily_reading': ['read', 'today', 'daily', 'next chapter', 'continue'],
            'challenge': ['help', 'struggle', 'anxiety', 'fear', 'worried', 'sad', 'depressed', 'angry', 'lonely'],
            'bookmark': ['save', 'bookmark', 'remember', 'mark'],
            'progress': ['progress', 'how far', 'what chapter', 'where am i'],
            'search': ['find', 'search', 'verse about', 'show me', 'verses about', 'scripture about',
            'what does the bible say about'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good evening'],
            'complete': ['done', 'finished', 'read', 'completed']
        }
    
    def analyze_intent(self, message):
        """
        Determine user intent from message
        Returns: intent type and extracted data
        """
        message_lower = message.lower()
        
        # Check for greetings
        if any(word in message_lower for word in self.intents['greeting']):
            return {'type': 'greeting', 'data': None}
        
        # Check for completion markers 
        completion_words = ['done', 'finished', 'completed']
        if message_lower.strip() in completion_words:
            return {'type': 'complete', 'data': None}
        
        # Check for bookmark request
        if any(word in message_lower for word in self.intents['bookmark']):
            verse_ref = self._extract_verse_reference(message)
            return {'type': 'bookmark', 'data': {'reference': verse_ref}}
        
        # Check for progress inquiry
        if any(word in message_lower for word in self.intents['progress']):
            return {'type': 'progress', 'data': None}
        
        # Check for daily reading request
        if any(word in message_lower for word in self.intents['daily_reading']):
            return {'type': 'daily_reading', 'data': None}
        
        # Check for search request
        if any(word in message_lower for word in self.intents['search']):
            topic = self._extract_topic(message, self.intents['search'])
            return {'type': 'search', 'data': {'topic': topic}}
        
        # Check for emotional/challenge keywords
        emotions = []
        for word in self.intents['challenge']:
            if word in message_lower:
                emotions.append(word)
        
        if emotions:
            return {'type': 'challenge', 'data': {'emotions': emotions, 'message': message}}
        
        # Default to general conversation
        return {'type': 'general', 'data': {'message': message}}
    
    def _extract_verse_reference(self, message):
        """Extract Bible verse reference from message"""
        # Pattern: Book Chapter:Verse or Book Chapter
        pattern = r'([1-3]?\s?[A-Za-z]+)\s+(\d+):?(\d+)?'
        match = re.search(pattern, message)
        
        if match:
            book = match.group(1).strip()
            chapter = match.group(2)
            verse = match.group(3) if match.group(3) else None
            return f"{book} {chapter}" + (f":{verse}" if verse else "")
        
        return None
    
    def _extract_topic(self, message, keywords):
        """Extract the topic/keyword after search terms"""
        message_lower = message.lower()
        
        for keyword in keywords:
            if keyword in message_lower:
                # Get everything after the keyword
                parts = message_lower.split(keyword, 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                    # Remove common words
                    topic = topic.replace('about', '').replace('for', '').replace('on', '').strip()
                    return topic
        
        return message
    
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
        
        else:
            plan['actions'] = [
                {
                    'agent': 'response_composer',
                    'action': 'general_response',
                    'data': intent['data']
                }
            ]
        
        return plan

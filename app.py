from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid

# Import our agents and database
from database.schema import Database
from agents.planner_agent import PlannerAgent
from agents.bible_matching_agent import BibleMatchingAgent
from agents.memory_agent import MemoryAgent
from agents.response_composer import ResponseComposer

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")
CORS(app, resources={r"/api/*": {"origins": "https://bible-agent-bot.onrender.com"}})

# Initialize database and agents
db = Database()
planner = PlannerAgent(db)
bible_matcher = BibleMatchingAgent()
memory = MemoryAgent(db)
composer = ResponseComposer()

# Agent Orchestrator
class AgentOrchestrator:
    """
    Executes the action plan from Planner Agent
    Coordinates between all agents to produce final response
    """
    
    def __init__(self, planner, bible_matcher, memory, composer):
        self.planner = planner
        self.bible_matcher = bible_matcher
        self.memory = memory
        self.composer = composer
    
    def process_message(self, user_id, message):
        """
        Main processing pipeline
        1. Plan the action
        2. Execute agents in sequence
        3. Compose response
        """
        # Get action plan from Planner
        plan = self.planner.plan_action(user_id, message)
        
        # Execute actions
        results = {}
        
        for action in plan['actions']:
            agent_name = action['agent']
            action_type = action['action']
            data = action['data']
            
            if agent_name == 'memory':
                results[action_type] = self._execute_memory_action(action_type, user_id, data)
            
            elif agent_name == 'bible_matching':
                results[action_type] = self._execute_bible_action(action_type, data, results)
            
            elif agent_name == 'response_composer':
                final_response = self._execute_composer_action(action_type, data, results)
        
        # Save conversation
        self.memory.save_conversation(user_id, message, final_response, plan['intent'])
        
        return {
            'response': final_response,
            'intent': plan['intent'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_memory_action(self, action_type, user_id, data):
        """Execute Memory Agent actions"""
        if action_type == 'get_next_chapters':
            return self.memory.get_next_chapters(user_id, data.get('count', 2))
        
        elif action_type == 'mark_complete':
            return self.memory.mark_complete(user_id)
        
        elif action_type == 'save_bookmark':
            ref = data.get('reference')
            if ref:
                return self.memory.save_bookmark(user_id, ref)
            return False
        
        elif action_type == 'get_progress':
            return self.memory.get_progress(user_id)
        
        return None
    
    def _execute_bible_action(self, action_type, data, previous_results):
        """Execute Bible Matching Agent actions"""
        if action_type == 'fetch_chapters':
            # Get chapters from previous memory action
            chapters_info = previous_results.get('get_next_chapters', [])
            if chapters_info:
                first_chapter = chapters_info[0]
                chapters = self.bible_matcher.fetch_chapters(
                    first_chapter['book'],
                    first_chapter['chapter'],
                    count=len(chapters_info)
                )
                return chapters
            return []
        
        elif action_type == 'find_relevant_verses':
            emotions = data.get('emotions', [])
            message = data.get('message')
            return self.bible_matcher.find_relevant_verses(emotions, message)
        
        elif action_type == 'search_verses':
            topic = data.get('topic', '')
            return self.bible_matcher.search_verses(topic)

        elif action_type == 'get_specific_verse':
            reference = data.get('reference', '')
            return self.bible_matcher.get_verse_by_reference(reference)

        return None
    
    def _execute_composer_action(self, action_type, data, previous_results):
        """Execute Response Composer actions"""
        if action_type == 'greet':
            return self.composer.greet(data.get('user_id'))
        
        elif action_type == 'present_daily_reading':
            chapters = previous_results.get('fetch_chapters', [])
            if chapters:
                # Get reflection question
                reflection = self.bible_matcher.get_reflection_question(
                    chapters[0]['book'],
                    chapters[0]['chapter']
                )
                return self.composer.present_daily_reading(chapters, reflection)
            return "Couldn't load today's reading. Please try again."
        
        elif action_type == 'comfort_response':
            verses = previous_results.get('find_relevant_verses', [])
            emotions = data.get('emotions', [])
            return self.composer.comfort_response(verses, emotions)
        
        elif action_type == 'confirm_bookmark':
            ref = data.get('reference')
            return self.composer.confirm_bookmark(ref)
        
        elif action_type == 'show_progress':
            progress = previous_results.get('get_progress', {})
            return self.composer.show_progress(progress)
        
        elif action_type == 'celebrate_completion':
            return self.composer.celebrate_completion()
        

        elif action_type == 'present_verse':
            verse_data = previous_results.get('get_specific_verse')
            return self.composer.present_verse(verse_data)
        elif action_type == 'present_search_results':
            verses = previous_results.get('search_verses', [])
            topic = data.get('topic', '')
            return self.composer.present_search_results(verses, topic)
        
        elif action_type == 'general_response':
            return self.composer.general_response(data.get('message', ''))
        
        return "I'm not sure how to help with that. Try asking for today's reading or a specific verse."

# Initialize orchestrator
orchestrator = AgentOrchestrator(planner, bible_matcher, memory, composer)

# Routes
@app.route('/api/verse-of-day', methods=['GET'])
def verse_of_day():
    """Get verse of the day"""
    try:
        verse = bible_matcher.get_verse_of_the_day()
        if verse:
            return jsonify({
                'reference': verse['reference'],
                'text': verse['text'],
                'translation': verse.get('translation', 'KJV')
            })
        return jsonify({'error': 'Could not load verse'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Main chat interface"""
    # Generate or get user ID
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or create user ID
        user_id = session.get('user_id')
        if not user_id:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
        
        # Ensure user exists in database
        user = db.get_user(user_id)
        if not user:
            db.create_user(user_id)
        
        # Process message through orchestrator
        result = orchestrator.process_message(user_id, message)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get user's reading progress"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No user session'}), 401
        
        progress = memory.get_progress(user_id)
        return jsonify(progress)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    """Get user's bookmarks"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No user session'}), 401
        
        bookmarks = memory.get_bookmarks(user_id)
        formatted = composer.format_bookmarks(bookmarks)
        
        return jsonify({
            'bookmarks': bookmarks,
            'formatted': formatted
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/daily-reading', methods=['GET'])
def daily_reading():
    """Get today's daily reading"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
            db.create_user(user_id)
        
        # Get next chapters
        chapters_info = memory.get_next_chapters(user_id, 2)
        
        # Fetch Bible content
        if chapters_info:
            first_chapter = chapters_info[0]
            chapters = bible_matcher.fetch_chapters(
                first_chapter['book'],
                first_chapter['chapter'],
                count=len(chapters_info)
            )
            
            # Get reflection question
            reflection = bible_matcher.get_reflection_question(
                first_chapter['book'],
                first_chapter['chapter']
            )
            
            response = composer.present_daily_reading(chapters, reflection)
            
            return jsonify({
                'response': response,
                'chapters': chapters
            })
        
        return jsonify({'error': 'Could not load reading'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database with common verses
    bible_matcher.local_db.populate_common_verses()
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    is_dev = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=is_dev, host='0.0.0.0', port=port)

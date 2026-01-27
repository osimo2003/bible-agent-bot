import random
from datetime import datetime

class ResponseComposer:
    """
    Composes natural, pastoral responses
    - Formats Bible content
    - Adds reflection questions
    - Creates encouraging messages
    - Maintains conversational tone
    """
    
    def __init__(self):
        self.greetings = [
            "Hello! 🙏 I'm here to help you grow in God's Word.",
            "Hi there! Ready to dive into Scripture today?",
            "Good to see you! Let's spend time in the Bible together.",
            "Welcome! How can I help you with your Bible study today?"
        ]
        
        self.completion_messages = [
            "Wonderful! 🎉 You've completed today's reading. God bless you for your faithfulness!",
            "Great job! 📖 Keep up the discipline of daily Scripture reading.",
            "Praise God! ✨ Your commitment to His Word is inspiring.",
            "Well done! 🌟 May today's reading transform your heart and mind."
        ]
    
    def greet(self, user_id, user_name=None):
        """Create greeting message"""
        greeting = random.choice(self.greetings)
        
        message = f"{greeting}\n\n"
        message += "I can help you with:\n"
        message += "📖 Daily Bible reading (2 chapters from NT)\n"
        message += "💭 Finding verses for life challenges\n"
        message += "🔖 Saving favorite verses\n"
        message += "📊 Tracking your progress\n\n"
        message += "Try saying:\n"
        message += "• 'Today's reading'\n"
        message += "• 'I'm feeling anxious'\n"
        message += "• 'Save John 3:16'\n"
        message += "• 'Show my progress'"
        
        return message
    
    def present_daily_reading(self, chapters, reflection_question=None):
        """
        Format daily reading with chapters and reflection
        chapters: list of chapter data from Bible Matching Agent
        """
        if not chapters:
            return "I couldn't retrieve today's reading. Please try again."
        
        # Header
        message = f"📖 **Today's Reading** ({datetime.now().strftime('%B %d, %Y')})\n\n"
        
        # List chapters
        chapter_refs = [f"{ch['book']} {ch['chapter']}" for ch in chapters]
        message += f"**Chapters:** {', '.join(chapter_refs)}\n\n"
        
        # Provide summary/preview
        message += "---\n\n"
        
        for i, chapter in enumerate(chapters, 1):
            message += f"**{chapter['reference']}**\n\n"
            
            # Provide first few verses as preview
            text = chapter['text']
            preview = text[:300] + "..." if len(text) > 300 else text
            message += f"{preview}\n\n"
            
            if i < len(chapters):
                message += "---\n\n"
        
        # Add reflection question
        if reflection_question:
            message += f"\n💭 **Reflection:** {reflection_question}\n\n"
        else:
            message += "\n💭 **Reflection:** What is God speaking to you through this passage?\n\n"
        
        # Call to action
        message += "---\n\n"
        message += "📝 When you're done reading, reply with **'READ'** or **'DONE'** to mark it complete.\n\n"
        message += "💡 Want to bookmark a verse? Just say **'Save [verse reference]'**"
        
        return message
    
    def comfort_response(self, verses, emotions, message=None):
        """
        Create comforting response with relevant verses
        verses: list of verse data from Bible Matching Agent
        emotions: list of detected emotions
        """
        if not verses:
            return "I'm here for you. Let me find some encouraging Scripture."
        
        # Empathetic opening
        emotion_responses = {
            'anxiety': "I understand you're feeling anxious. God cares deeply about your worries.",
            'fear': "It's okay to feel afraid. God promises to be with you.",
            'sadness': "I'm sorry you're going through a difficult time. God is close to the brokenhearted.",
            'lonely': "Loneliness is hard. Remember, God never leaves you.",
            'anger': "Your feelings are valid. Let's find peace in God's Word.",
            'doubt': "Doubt is part of the journey. God can handle your questions.",
            'guilt': "God's grace is greater than any guilt. Let's remember His forgiveness.",
            'hopeless': "Even in darkness, there is hope in Christ.",
            'weak': "When we are weak, God is strong. His strength is made perfect in our weakness."
        }
        
        # Find appropriate opening
        opening = None
        for emotion in emotions:
            if emotion in emotion_responses:
                opening = emotion_responses[emotion]
                break
        
        if not opening:
            opening = "Thank you for sharing what's on your heart. Let's turn to Scripture together."
        
        message_text = f"{opening}\n\n"
        message_text += "**Here are some verses for you:**\n\n"
        
        # Add verses
        for i, verse in enumerate(verses, 1):
            message_text += f"**{verse['reference']}**\n"
            message_text += f"_{verse['text']}_\n\n"
            
            if i < len(verses):
                message_text += "---\n\n"
        
        # Closing encouragement
        closings = [
            "💙 You are loved and not alone.",
            "🙏 God is faithful, even when circumstances are hard.",
            "✨ Hold onto these truths today.",
            "💪 God's strength is with you.",
            "🌟 Trust in the Lord with all your heart."
        ]
        
        message_text += f"\n{random.choice(closings)}\n\n"
        message_text += "💬 Want to talk more? I'm here to listen.\n"
        message_text += "🔖 Save any of these verses by saying **'Save [verse reference]'**"
        
        return message_text
    
    def confirm_bookmark(self, reference, note=None):
        """Confirm bookmark was saved"""
        message = f"✅ **Bookmark Saved!**\n\n"
        message += f"📌 **Verse:** {reference}\n"
        
        if note:
            message += f"📝 **Note:** {note}\n"
        
        message += "\n💡 You can view all your bookmarks anytime by saying **'Show my bookmarks'**"
        
        return message
    
    def show_progress(self, progress_data):
        """Display reading progress"""
        message = f"📊 **Your Reading Progress**\n\n"
        message += f"📖 **Chapters Completed:** {progress_data['completed_chapters']} / {progress_data['total_chapters']}\n"
        message += f"📈 **Progress:** {progress_data['progress_percent']}%\n"
        message += f"📍 **Current Position:** {progress_data['current_book']} {progress_data['current_chapter']}\n"
        message += f"🔥 **7-Day Streak:** {progress_data['streak_days']} days\n\n"
        
        # Progress bar
        percent = progress_data['progress_percent']
        filled = int(percent / 10)
        bar = "█" * filled + "░" * (10 - filled)
        message += f"{bar} {percent}%\n\n"
        
        # Encouragement based on progress
        if percent < 10:
            message += "🌱 Great start! Keep building the habit of daily reading."
        elif percent < 50:
            message += "🌿 You're making excellent progress! Stay consistent."
        elif percent < 90:
            message += "🌳 Wonderful dedication! You're over halfway through the New Testament."
        else:
            message += "🎉 Almost there! You're nearly finished with the entire New Testament!"
        
        return message
    
    def celebrate_completion(self, chapters_read=None):
        """Celebrate reading completion"""
        message = random.choice(self.completion_messages)
        message += "\n\n📚 Ready for tomorrow's reading? I'll be here when you are!"
        
        return message
    
    def present_search_results(self, verses, topic):
        """Format search results"""
        if not verses:
            return f"I couldn't find verses about '{topic}'. Try rephrasing or ask for help with a specific challenge."
        
        message = f"🔍 **Verses about: {topic}**\n\n"
        
        for verse in verses[:5]:
            message += f"**{verse.get('reference', 'Unknown')}**\n"
            message += f"{verse.get('text', '')}\n\n"
            message += "---\n\n"
        
        message += "💡 Want to save any of these? Say **'Save [verse reference]'**"
        
        return message
    
    def general_response(self, user_message):
        """Handle general conversation"""
        responses = [
            "I'm here to help you with Bible study. Try asking for today's reading or tell me how you're feeling.",
            "I'd love to help! You can ask me for Scripture, bookmark verses, or check your progress.",
            "Not sure what you need? Try:\n• 'Today's reading'\n• 'I need encouragement'\n• 'Find verses about peace'",
        ]
        
        return random.choice(responses)
    
    def format_bookmarks(self, bookmarks):
        """Format bookmarks list"""
        if not bookmarks:
            return "📖 You haven't saved any bookmarks yet.\n\nSay **'Save [verse reference]'** to bookmark your favorite verses!"
        
        message = f"🔖 **Your Bookmarks** ({len(bookmarks)} saved)\n\n"
        
        for bm in bookmarks[:10]:
            ref = f"{bm['book']} {bm['chapter']}"
            if bm['verse']:
                ref += f":{bm['verse']}"
            
            message += f"📌 **{ref}**\n"
            if bm['note']:
                message += f"   💭 {bm['note']}\n"
            if bm['topic']:
                message += f"   🏷️ {bm['topic']}\n"
            message += "\n"
        
        if len(bookmarks) > 10:
            message += f"\n_...and {len(bookmarks) - 10} more_"
        
        return message

"""
Smart Keyword Extractor
Understands complex phrases and maps them to Bible concepts
"""

import re

class KeywordExtractor:
    """
    Extracts meaningful Bible-related keywords from user input
    Handles complex sentences, idioms, and emotional expressions
    """
    
    def __init__(self):
        # Extensive phrase patterns mapped to Bible concepts
        self.phrase_patterns = {
            # ========== EMOTIONS ==========
            r'heart is heavy|heavy heart|feeling down|feeling low|feeling blue': ['sadness', 'comfort', 'sorrow'],
            r'can\'?t sleep|trouble sleeping|sleepless|insomnia': ['peace', 'rest', 'anxiety'],
            r'feeling empty|feel empty|emptiness': ['purpose', 'fulfillment', 'joy'],
            r'burned out|burn out|exhausted|worn out': ['rest', 'strength', 'peace'],
            r'overwhelmed|too much|can\'?t cope|can\'?t handle': ['peace', 'strength', 'help'],
            r'stressed|stress|stressful': ['peace', 'rest', 'anxiety', 'trust'],
            r'panic|panicking|panic attack': ['peace', 'fear', 'comfort'],
            r'crying|can\'?t stop crying|tears': ['comfort', 'sadness', 'hope'],
            r'numb|feel nothing|emotionless': ['hope', 'comfort', 'healing'],
            r'angry at god|mad at god|why god': ['faith', 'trust', 'suffering'],
            r'feel like giving up|want to quit|give up': ['perseverance', 'hope', 'strength'],
            r'feel worthless|not good enough|inadequate': ['identity', 'love', 'worth', 'grace'],
            r'feel unloved|nobody loves me|unlovable': ['love', 'acceptance', 'grace'],
            r'feel rejected|rejection|rejected': ['acceptance', 'love', 'comfort'],
            r'feel abandoned|abandoned': ['presence', 'comfort', 'faithfulness'],
            
            # ========== RELATIONSHIPS ==========
            r'marriage problems|marriage trouble|spouse|husband|wife': ['marriage', 'love', 'patience', 'forgiveness'],
            r'divorce|getting divorced|separated': ['marriage', 'comfort', 'guidance', 'healing'],
            r'boyfriend|girlfriend|dating|relationship': ['love', 'wisdom', 'purity', 'patience'],
            r'broke up|breakup|break up|broken heart': ['comfort', 'healing', 'hope'],
            r'cheated|cheating|affair|unfaithful': ['forgiveness', 'healing', 'trust'],
            r'fight with|argument|arguing|disagreement': ['peace', 'patience', 'forgiveness'],
            r'don\'?t trust|can\'?t trust|trust issues': ['trust', 'healing', 'faith'],
            r'family problems|family issues|parents|siblings': ['family', 'love', 'patience', 'forgiveness'],
            r'lonely|loneliness|no friends|alone': ['loneliness', 'comfort', 'presence'],
            r'friend betrayed|betrayal|betrayed': ['forgiveness', 'trust', 'healing'],
            
            # ========== WORK & FINANCES ==========
            r'lost my job|fired|laid off|unemployed': ['provision', 'trust', 'faith', 'hope'],
            r'need a job|looking for work|job search': ['provision', 'guidance', 'patience'],
            r'hate my job|miserable at work|bad job': ['contentment', 'patience', 'guidance'],
            r'difficult boss|boss problems|coworker': ['patience', 'wisdom', 'peace'],
            r'money problems|financial|debt|bills|broke': ['provision', 'trust', 'contentment'],
            r'can\'?t pay|can\'?t afford': ['provision', 'trust', 'faith'],
            r'poor|poverty|struggling financially': ['provision', 'hope', 'contentment'],
            
            # ========== HEALTH ==========
            r'sick|illness|disease|unwell|health problems': ['healing', 'faith', 'comfort', 'hope'],
            r'cancer|terminal|dying': ['healing', 'hope', 'comfort', 'eternal'],
            r'chronic pain|pain|suffering physically': ['healing', 'comfort', 'strength'],
            r'mental health|depression|bipolar': ['healing', 'hope', 'peace', 'comfort'],
            r'addiction|addicted|alcoholic|drugs': ['freedom', 'deliverance', 'strength', 'healing'],
            r'suicidal|suicide|end my life|don\'?t want to live': ['hope', 'life', 'love', 'help', 'purpose'],
            r'pregnant|pregnancy|expecting': ['blessing', 'children', 'provision', 'trust'],
            r'miscarriage|lost the baby|stillborn': ['comfort', 'grief', 'hope', 'healing'],
            
            # ========== LOSS & GRIEF ==========
            r'someone died|death of|passed away|lost someone': ['death', 'comfort', 'hope', 'resurrection'],
            r'grieving|grief|mourning': ['comfort', 'grief', 'hope'],
            r'funeral|memorial': ['comfort', 'hope', 'resurrection', 'eternal'],
            r'miss them|missing someone|wish they were here': ['comfort', 'hope'],
            r'widow|widower|lost my spouse': ['comfort', 'provision', 'hope'],
            r'lost my parent|mom died|dad died|parent passed': ['comfort', 'grief', 'hope'],
            r'lost my child|child died': ['comfort', 'grief', 'hope', 'healing'],
            
            # ========== FAITH & SPIRITUALITY ==========
            r'don\'?t feel god|god is silent|where is god': ['faith', 'presence', 'trust', 'waiting'],
            r'losing faith|lost my faith|doubt god': ['faith', 'doubt', 'trust'],
            r'how to pray|teach me to pray|prayer life': ['prayer'],
            r'how to hear god|god\'?s voice': ['guidance', 'prayer'],
            r'backsliding|fell away|returned to sin': ['repentance', 'grace', 'forgiveness', 'restoration'],
            r'tempted|temptation|struggling with sin': ['temptation', 'strength', 'victory', 'purity'],
            r'how to be saved|become christian|accept jesus': ['salvation', 'faith', 'eternal'],
            r'church hurt|hurt by church|church problems': ['forgiveness', 'healing', 'fellowship'],
            
            # ========== LIFE DECISIONS ==========
            r'don\'?t know what to do|confused|uncertain': ['guidance', 'wisdom', 'direction'],
            r'big decision|major decision|life decision': ['guidance', 'wisdom', 'trust'],
            r'god\'?s will|what should i do|which path': ['guidance', 'wisdom', 'direction'],
            r'moving|relocating|new city': ['guidance', 'trust', 'provision'],
            r'new job offer|career change': ['guidance', 'wisdom', 'provision'],
            r'getting married|engaged|wedding': ['marriage', 'love', 'blessing', 'wisdom'],
            r'having a baby|starting family|first child': ['children', 'blessing', 'family', 'trust'],
            
            # ========== FEAR & WORRY ==========
            r'afraid of death|fear of dying|scared to die': ['death', 'eternal', 'hope', 'fear'],
            r'afraid of future|worried about tomorrow': ['future', 'trust', 'anxiety', 'provision'],
            r'fear of failure|afraid to fail': ['courage', 'fear', 'faith', 'strength'],
            r'worried about children|fear for my kids': ['protection', 'trust', 'prayer', 'family'],
            
            # ========== SUCCESS & FAILURE ==========
            r'failed|failure|messed up|made mistake': ['grace', 'forgiveness', 'hope', 'restoration'],
            r'jealous of|envy|others have more': ['contentment', 'jealousy', 'gratitude'],
            r'ashamed|shame|embarrassed': ['grace', 'forgiveness', 'acceptance'],
            
            # ========== COMMON NEEDS ==========
            r'need help|help me|i need': ['help', 'strength', 'provision'],
            r'need peace|want peace': ['peace'],
            r'need strength|give me strength': ['strength'],
            r'need hope|give me hope': ['hope'],
            r'need wisdom|need advice': ['wisdom', 'guidance'],
            r'need courage|need bravery': ['courage', 'fear', 'strength'],
            r'need patience|be patient': ['patience'],
            r'need love|feel loved': ['love'],
            r'need comfort|need comforting': ['comfort'],
            r'need healing|heal me': ['healing'],
            r'thank god|grateful|thankful|blessed': ['thanksgiving', 'gratitude', 'praise'],
        }
        
        # Single word synonyms
        self.word_synonyms = {
            'scared': ['fear', 'afraid', 'courage'],
            'afraid': ['fear', 'courage'],
            'worried': ['anxiety', 'worry', 'trust'],
            'anxious': ['anxiety', 'peace'],
            'happy': ['joy'],
            'sad': ['sadness', 'sorrow', 'comfort'],
            'depressed': ['sadness', 'despair', 'hope'],
            'angry': ['anger', 'patience'],
            'mad': ['anger'],
            'frustrated': ['patience', 'peace'],
            'peaceful': ['peace'],
            'loving': ['love'],
            'hopeful': ['hope'],
            'hopeless': ['hope', 'despair'],
            'forgiving': ['forgiveness'],
            'merciful': ['mercy'],
            'wise': ['wisdom'],
            'strong': ['strength'],
            'weak': ['strength', 'weakness'],
            'patient': ['patience'],
            'humble': ['humility'],
            'proud': ['pride', 'humility'],
            'jealous': ['jealousy', 'envy', 'contentment'],
            'grateful': ['thanksgiving', 'gratitude'],
            'thankful': ['thanksgiving', 'gratitude'],
            'lonely': ['loneliness', 'comfort'],
            'alone': ['loneliness', 'presence'],
            'lost': ['guidance', 'direction'],
            'confused': ['wisdom', 'guidance'],
            'hurt': ['healing', 'comfort'],
            'sick': ['healing'],
            'dying': ['death', 'life', 'hope'],
            'grieving': ['grief', 'comfort'],
            'mourning': ['comfort', 'grief'],
            'money': ['provision', 'wealth', 'contentment'],
            'poor': ['provision', 'poverty', 'contentment'],
            'job': ['work', 'provision'],
            'marriage': ['marriage', 'love'],
            'divorced': ['divorce', 'healing'],
            'children': ['children', 'family'],
            'family': ['family', 'love'],
            'friend': ['friendship'],
            'enemy': ['enemies', 'forgiveness'],
            'sin': ['forgiveness', 'repentance', 'grace'],
            'sinned': ['forgiveness', 'repentance'],
            'tempted': ['temptation', 'strength'],
            'pray': ['prayer'],
            'worship': ['worship', 'praise'],
            'believe': ['faith', 'belief'],
            'trust': ['trust', 'faith'],
            'doubting': ['doubt', 'faith'],
            'saved': ['salvation'],
            'heaven': ['heaven', 'eternal'],
            'jesus': ['jesus', 'christ', 'savior'],
            'forgive': ['forgiveness'],
            'heal': ['healing'],
            'restore': ['restoration', 'healing'],
            'guide': ['guidance'],
            'protect': ['protection'],
            'comfort': ['comfort'],
        }
        
        # Stop words to remove
        self.stop_words = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
            'from', 'as', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'under', 'again', 'further', 'then',
            'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
            'and', 'but', 'if', 'or', 'because', 'until', 'while', 'about',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
            'am', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
            'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'tell', 'say',
            'says', 'said', 'bible', 'verse', 'verses', 'scripture', 'scriptures',
            'find', 'show', 'give', 'get', 'want', 'know', 'think', 'please',
            'thanks', 'thank', 'something', 'anything', 'everything',
            'really', 'like', 'going', 'today', 'now', 'always', 'never'
        }
    
    def extract(self, text):
        """Extract meaningful keywords from user input"""
        text_lower = text.lower().strip()
        keywords = set()
        
        # Step 1: Check phrase patterns first
        for pattern, concepts in self.phrase_patterns.items():
            if re.search(pattern, text_lower):
                keywords.update(concepts)
        
        # Step 2: Extract words and expand synonyms
        words = re.findall(r'\b[a-z]+\b', text_lower)
        
        for word in words:
            if word in self.stop_words or len(word) < 3:
                continue
            keywords.add(word)
            if word in self.word_synonyms:
                keywords.update(self.word_synonyms[word])
        
        # Step 3: Fallback
        if not keywords:
            keywords = {w for w in words if w not in self.stop_words and len(w) > 2}
        
        if not keywords:
            keywords = {text_lower}
        
        return list(keywords)

# 📖 Bible Agent Bot

An intelligent multi-agent system for daily Bible study, built with Python and Flask.

## ✨ Features

### Core Features
- **📖 Daily Bible Reading**: Structured 2-chapter daily readings through the New Testament (Matthew → Revelation)
- **💭 Emotional Support**: Find relevant verses based on feelings (anxiety, fear, sadness, hope, etc.)
- **🔍 Enhanced Bible Search**: Search 50+ keywords (love, faith, shepherd, grace, salvation, etc.)
- **🔖 Bookmark System**: Save and organize your favorite verses
- **📊 Progress Tracking**: Monitor your reading journey with completion statistics and streaks

### Additional Features
- **🌟 Verse of the Day**: Inspiring verse shown daily
- **🌙 Dark Mode**: Toggle between light and dark themes
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **💾 Persistent Storage**: SQLite database saves all progress

## 🏗️ Architecture

Multi-agent system with specialized components:

1. **Planner Agent**: Analyzes user intent and coordinates other agents
2. **Bible Matching Agent**: Retrieves and matches Scripture to user needs
3. **Memory Agent**: Tracks progress, bookmarks, and user preferences
4. **Response Composer**: Creates natural, pastoral responses

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git
- Virtual environment

### Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/bible-agent-bot.git
cd bible-agent-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:5000` in your browser.

## 🎯 Usage

### Daily Reading
Type: **"Today's reading"** or **"Continue reading"**

The bot provides your next 2 chapters with reflection questions.

### Emotional Support
Share your feelings: **"I'm feeling anxious"** or **"I need hope"**

The bot finds relevant, comforting Scripture.

### Bible Search
Use the search box or type: **"Find verses about love"**

Searches 50+ keywords including: love, faith, hope, peace, strength, wisdom, shepherd, light, salvation, grace, and more.

### Bookmarks
Save verses: **"Save John 3:16"** or **"Bookmark Philippians 4:6"**

### Progress
Check progress: **"Show my progress"** or click the **📊 Progress** button

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Bible API**: bible-api.com (free tier)
- **Frontend**: Vanilla JavaScript, CSS3
- **Deployment**: Render.com compatible

## 📂 Project Structure
```
bible-agent-bot/
├── agents/             # Multi-agent system
│   ├── planner_agent.py
│   ├── bible_matching_agent.py
│   ├── memory_agent.py
│   └── response_composer.py
├── database/           # Database schema and Bible data
│   ├── schema.py
│   └── bible_data.py
├── static/             # CSS and JavaScript
│   ├── css/style.css
│   └── js/app.js
├── templates/          # HTML templates
│   └── index.html
├── app.py             # Main Flask application
├── requirements.txt   # Python dependencies
└── README.md
```

## 🎨 Features in Detail

### Search Keywords Supported
**Emotions**: anxiety, fear, sad, lonely, angry, doubt, guilt, hopeless, weak  
**Spiritual**: love, peace, joy, faith, hope, trust, prayer, worship  
**Life**: strength, wisdom, guidance, patience, forgiveness, healing, comfort, provision  
**Biblical**: beginning, shepherd, light, life, salvation, grace, eternal, kingdom, glory, heaven

### Dark Mode
Click the **🌙 Dark** button to toggle between themes. Your preference is saved automatically.

### Progress Tracking
- Chapters completed counter
- Progress percentage
- Current reading position
- 7-day reading streak

## 🚢 Deployment

Ready to deploy on Render.com (free tier):

1. Push code to GitHub
2. Create account on [render.com](https://render.com)
3. Create new Web Service
4. Connect GitHub repository
5. Deploy!

See deployment guide in `DEPLOYMENT.md` (coming soon)

## 🤝 Contributing

Contributions welcome! Feel free to submit a Pull Request.

## 📜 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Bible API: [bible-api.com](https://bible-api.com)
- Built to help people engage with Scripture daily

---

**Built with Love to help people grow in God's Word**

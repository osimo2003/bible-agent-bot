// Main App JavaScript
class BibleAgentChat {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.progressBtn = document.getElementById('progressBtn');
        this.bookmarksBtn = document.getElementById('bookmarksBtn');
        this.darkModeBtn = document.getElementById('darkModeBtn');
        this.searchInput = document.getElementById('searchInput');
        this.searchToggleBtn = document.getElementById('searchToggleBtn');
        this.searchExpanded = false;
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        this.progressBtn.addEventListener('click', () => this.showProgress());
        this.bookmarksBtn.addEventListener('click', () => this.showBookmarks());
        this.darkModeBtn.addEventListener('click', () => this.toggleDarkMode());
        
        this.searchToggleBtn.addEventListener('click', () => this.toggleSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.searchExpanded) this.performSearch();
        });
        this.searchInput.addEventListener('blur', () => {
            if (!this.searchInput.value.trim()) {
                setTimeout(() => this.collapseSearch(), 200);
            }
        });
        
        // Quick reply buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-reply')) {
                this.messageInput.value = e.target.textContent;
                this.sendMessage();
            }
        });
        
        // Modal close buttons
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                closeBtn.closest('.modal').style.display = 'none';
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
        
        // Load verse of the day
        this.loadVerseOfDay();
        this.loadDarkModePreference();
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) return;
        
        // Disable input
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
        
        // Add user message
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        
        // Show loading
        this.showLoading();
        
        try {
            // Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Remove loading
            this.removeLoading();
            
            // Add bot response
            this.addMessage(data.response, 'bot');
            
        } catch (error) {
            console.error('Error:', error);
            this.removeLoading();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        } finally {
            // Re-enable input
            this.messageInput.disabled = false;
            this.sendBtn.disabled = false;
            this.messageInput.focus();
        }
    }
    
    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Convert markdown-style formatting to HTML
        const formattedText = this.formatMessage(text);
        contentDiv.innerHTML = formattedText;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    formatMessage(text) {
        // Convert **bold** to <strong>
        text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Convert _italic_ to <em>
        text = text.replace(/_(.+?)_/g, '<em>$1</em>');
        
        // Convert newlines to <br>
        text = text.replace(/\n/g, '<br>');
        
        // Convert --- to <hr>
        text = text.replace(/---/g, '<hr style="border: none; border-top: 1px solid #E1E8ED; margin: 1rem 0;">');
        
        // Detect and format lists
        const lines = text.split('<br>');
        let inList = false;
        let formattedLines = [];
        
        lines.forEach(line => {
            if (line.trim().match(/^[•●▪-]\s/)) {
                if (!inList) {
                    formattedLines.push('<ul>');
                    inList = true;
                }
                const listItem = line.trim().replace(/^[•●▪-]\s/, '');
                formattedLines.push(`<li>${listItem}</li>`);
            } else {
                if (inList) {
                    formattedLines.push('</ul>');
                    inList = false;
                }
                formattedLines.push(line);
            }
        });
        
        if (inList) {
            formattedLines.push('</ul>');
        }
        
        return formattedLines.join('<br>');
    }
    
    showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message';
        loadingDiv.id = 'loading-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading';
        loadingIndicator.innerHTML = '<span></span><span></span><span></span>';
        
        contentDiv.appendChild(loadingIndicator);
        loadingDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(loadingDiv);
        
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    removeLoading() {
        const loadingMsg = document.getElementById('loading-message');
        if (loadingMsg) {
            loadingMsg.remove();
        }
    }
    
    async showProgress() {
        const modal = document.getElementById('progressModal');
        const content = document.getElementById('progressContent');
        
        content.innerHTML = '<div class="loading"><span></span><span></span><span></span></div>';
        modal.style.display = 'block';
        
        try {
            const response = await fetch('/api/progress');
            const data = await response.json();
            
            const percent = data.progress_percent || 0;
            const filled = Math.floor(percent / 10);
            const progressBar = '█'.repeat(filled) + '░'.repeat(10 - filled);
            
            content.innerHTML = `
                <div style="padding: 1rem;">
                    <div style="margin-bottom: 1.5rem;">
                        <h3 style="color: var(--primary-color); margin-bottom: 0.5rem;">Chapters Completed</h3>
                        <p style="font-size: 2rem; font-weight: bold;">${data.completed_chapters} / ${data.total_chapters}</p>
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <h3 style="color: var(--primary-color); margin-bottom: 0.5rem;">Progress</h3>
                        <div style="font-size: 1.5rem; font-family: monospace; letter-spacing: 2px;">
                            ${progressBar} ${percent}%
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <h3 style="color: var(--primary-color); margin-bottom: 0.5rem;">Current Position</h3>
                        <p style="font-size: 1.2rem;">${data.current_book} ${data.current_chapter}</p>
                    </div>
                    
                    <div>
                        <h3 style="color: var(--primary-color); margin-bottom: 0.5rem;">7-Day Streak</h3>
                        <p style="font-size: 1.2rem;">🔥 ${data.streak_days} days</p>
                    </div>
                </div>
            `;
        } catch (error) {
            content.innerHTML = '<p>Error loading progress. Please try again.</p>';
        }
    }
    
    async showBookmarks() {
        const modal = document.getElementById('bookmarksModal');
        const content = document.getElementById('bookmarksContent');
        
        content.innerHTML = '<div class="loading"><span></span><span></span><span></span></div>';
        modal.style.display = 'block';
        
        try {
            const response = await fetch('/api/bookmarks');
            const data = await response.json();
            
            if (data.bookmarks && data.bookmarks.length > 0) {
                let html = '<div style="padding: 1rem;">';
                
                data.bookmarks.forEach(bm => {
                    const ref = `${bm.book} ${bm.chapter}${bm.verse ? ':' + bm.verse : ''}`;
                    const date = new Date(bm.created_at).toLocaleDateString();
                    
                    html += `
                        <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--background); border-radius: 8px; border-left: 3px solid var(--secondary-color);">
                            <h4 style="color: var(--primary-color); margin-bottom: 0.5rem;">📌 ${ref}</h4>
                            ${bm.note ? `<p style="margin-bottom: 0.5rem;"><em>${bm.note}</em></p>` : ''}
                            ${bm.topic ? `<p style="color: var(--text-secondary); font-size: 0.9rem;">🏷️ ${bm.topic}</p>` : ''}
                            <p style="color: var(--text-secondary); font-size: 0.85rem; margin-top: 0.5rem;">${date}</p>
                        </div>
                    `;
                });
                
                html += '</div>';
                content.innerHTML = html;
            } else {
                content.innerHTML = `
                    <div style="padding: 2rem; text-align: center;">
                        <p>📖 You haven't saved any bookmarks yet.</p>
                        <p style="margin-top: 1rem; color: var(--text-secondary);">Say "Save [verse reference]" to bookmark your favorite verses!</p>
                    </div>
                `;
            }
        } catch (error) {
            content.innerHTML = '<p>Error loading bookmarks. Please try again.</p>';
        }
    }
    
    async loadVerseOfDay() {
        try {
            const response = await fetch('/api/verse-of-day');
            const verse = await response.json();
            
            if (verse.reference && verse.text) {
                const verseMessage = `🌟 **Verse of the Day**

**${verse.reference}**

_${verse.text}_`;
                this.addMessage(verseMessage, 'bot');
            }
        } catch (error) {
            console.log('Could not load verse of the day');
        }
    }
    
    toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
        
        this.darkModeBtn.innerHTML = isDark ? '☀️ Light' : '🌙 Dark';
    }
    
    loadDarkModePreference() {
        const isDark = localStorage.getItem('darkMode') === 'true';
        if (isDark) {
            document.body.classList.add('dark-mode');
            this.darkModeBtn.innerHTML = '☀️ Light';
        }
    }
    
    toggleSearch() {
        if (this.searchExpanded) {
            this.performSearch();
        } else {
            this.expandSearch();
        }
    }
    
    expandSearch() {
        this.searchExpanded = true;
        this.searchInput.className = 'search-input-expanded';
        this.searchInput.focus();
        this.searchToggleBtn.innerHTML = '➤';
    }
    
    collapseSearch() {
        this.searchExpanded = false;
        this.searchInput.className = 'search-input-collapsed';
        this.searchInput.value = '';
        this.searchToggleBtn.innerHTML = '🔍';
    }
    
    async performSearch() {
        const query = this.searchInput.value.trim();
        
        if (!query) return;
        
        this.searchInput.disabled = true;
        this.searchToggleBtn.disabled = true;
        
        this.addMessage(`Search for: "${query}"`, 'user');
        
        this.searchInput.value = '';
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: `find verses about ${query}` })
            });
            
            if (!response.ok) {
                throw new Error('Search failed');
            }
            
            const data = await response.json();
            
            this.removeLoading();
            
            this.addMessage(data.response, 'bot');
            
        } catch (error) {
            console.error('Search error:', error);
            this.removeLoading();
            this.addMessage('Sorry, search failed. Please try again.', 'bot');
        } finally {
            this.searchInput.disabled = false;
            this.searchToggleBtn.disabled = false;
            this.collapseSearch();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BibleAgentChat();
});

// chat-manager.js
import { CONFIG, emotionIconMap, polarityTextMap } from '../config/constants.js';
import { escapeHtml, getCurrentTime } from '../utils/common-utils.js';

export class ChatManager {
    constructor(personaManager) {
        this.chatBox = document.getElementById('chatBox');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.sessionIdSpan = document.getElementById('sessionId');
        this.msgCountSpan = document.getElementById('msgCount');
        this.emotionIndicator = document.getElementById('emotionIndicator');
        this.emotionIcon = document.getElementById('emotionIcon');
        this.emotionLabel = document.getElementById('emotionLabel');
        this.emotionBadge = document.getElementById('emotionBadge');
        this.emotionConfidence = document.getElementById('emotionConfidence');
        this.personaManager = personaManager;
        this.messageCount = 0;
        this.isLoading = false;
        this.lastEmotion = null;
        this.currentTypingMessage = null;
        this.sessionId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.sessionIdSpan.textContent = this.sessionId;
        this.setupEventListeners();
    }
    setupEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isLoading) {
                this.sendMessage();
            }
        });
    }
    clearEmptyState() {
        if (this.chatBox.querySelector('.empty-state')) {
            this.chatBox.innerHTML = '';
        }
    }
    addMessageToChat(content, isUser = false) {
        this.clearEmptyState();
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = `<span>${escapeHtml(content)}</span>`;
        messageDiv.appendChild(textDiv);
        if (isUser) {
            const statusDiv = document.createElement('div');
            statusDiv.className = 'message-status';
            statusDiv.innerHTML = `
                <span class="status-icon">✓</span>
                <span class="status-label">已发送</span>
                <span class="message-timestamp">${getCurrentTime()}</span>
            `;
            messageDiv.appendChild(statusDiv);
        }
        this.chatBox.appendChild(messageDiv);
        this.chatBox.scrollTop = this.chatBox.scrollHeight;
        return messageDiv;
    }
    async typeMessage(container, content, speed = 50) {
        const textSpan = container.querySelector('span');
        textSpan.textContent = '';
        container.classList.add('typing-text');
        for (let i = 0; i < content.length; i++) {
            textSpan.textContent += content[i];
            await new Promise(resolve => setTimeout(resolve, speed));
        }
        container.classList.remove('typing-text');
    }
    async sendMessage() {
        const content = this.messageInput.value.trim();
        if (!content || this.isLoading) return;
        this.isLoading = true;
        this.addMessageToChat(content, true);
        this.messageInput.value = '';
        this.msgCountSpan.textContent = ++this.messageCount;
        const aiDiv = this.addMessageToChat('...');
        try {
            const res = await fetch(CONFIG.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: content,
                    session_id: this.sessionId,
                    persona_id: this.personaManager.getCurrentPersonaId()
                })
            });
            const data = await res.json();
            if (data.status === 'success') {
                await this.typeMessage(aiDiv.querySelector('.message-text'), data.reply);
                this.updateEmotion(data.emotion);
            } else {
                aiDiv.querySelector('.message-text').textContent = 'AI未能回复，请稍后再试';
            }
        } catch (e) {
            aiDiv.querySelector('.message-text').textContent = '网络错误，请检查连接';
        }
        this.isLoading = false;
    }
    updateEmotion(emotion) {
        if (!emotion) {
            this.emotionIndicator.classList.remove('active');
            return;
        }
        this.emotionIndicator.classList.add('active');
        this.emotionIcon.textContent = emotionIconMap[emotion.emotion] || '😊';
        this.emotionLabel.textContent = emotion.emotion;
        this.emotionBadge.textContent = polarityTextMap[emotion.polarity] || '';
        this.emotionConfidence.textContent = `置信度 ${(emotion.confidence * 100).toFixed(0)}%`;
    }
    receiveCareMessage(msg) {
        this.addMessageToChat(msg, false);
    }
    setMsgCount(count) {
        this.messageCount = count;
        this.msgCountSpan.textContent = count;
    }
}

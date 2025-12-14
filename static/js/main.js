// main.js
import { ThemeManager } from './modules/theme-manager.js';
import { PersonaManager } from './modules/persona-manager.js';
import { ChatManager } from './modules/chat-manager.js';
import { WebSocketManager } from './modules/websocket-manager.js';

document.addEventListener('DOMContentLoaded', async () => {
    const themeManager = new ThemeManager();
    const personaManager = new PersonaManager();
    await personaManager.loadPersonas();
    const chatManager = new ChatManager(personaManager);
    // WebSocket连接状态指示
    const wsStatusDot = document.getElementById('wsStatusDot');
    const wsStatusText = document.getElementById('wsStatusText');
    function updateWSStatus(connected) {
        wsStatusDot.style.backgroundColor = connected ? '#4CAF50' : '#ccc';
        wsStatusText.textContent = connected ? '在线' : '离线';
    }
    const wsManager = new WebSocketManager(updateWSStatus, (msg) => chatManager.receiveCareMessage(msg));
    wsManager.connect(chatManager.sessionId);
});

// websocket-manager.js
import { CONFIG } from '../config/constants.js';

export class WebSocketManager {
    constructor(onStatusChange, onMessage) {
        this.socket = null;
        this.onStatusChange = onStatusChange;
        this.onMessage = onMessage;
        this.connected = false;
    }
    connect(sessionId) {
        this.socket = io(CONFIG.wsUrl, {
            query: { session_id: sessionId }
        });
        this.socket.on('connect', () => {
            this.connected = true;
            this.onStatusChange(true);
        });
        this.socket.on('disconnect', () => {
            this.connected = false;
            this.onStatusChange(false);
        });
        this.socket.on('reconnect', () => {
            this.connected = true;
            this.onStatusChange(true);
        });
        this.socket.on('care_message', (msg) => {
            if (this.onMessage) this.onMessage(msg);
        });
    }
    send(event, data) {
        if (this.socket && this.connected) {
            this.socket.emit(event, data);
        }
    }
    isConnected() {
        return this.connected;
    }
}

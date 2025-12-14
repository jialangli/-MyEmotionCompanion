// constants.js
export const CONFIG = {
    apiUrl: 'http://127.0.0.1:5000/api/chat',
    wsUrl: 'http://127.0.0.1:5000',
    maxRetries: 3,
    retryDelay: 1000
};

export const emotionIconMap = {
    '难过': '😢',
    '开心': '😊',
    '生气': '😠',
    '疲惫': '😴',
    '焦虑': '😰',
    '兴奋': '🤩',
    '害怕': '😨',
    '厌恶': '🤮',
    '恐惧': '😱',
    '惊讶': '😲',
    '中性': '😐'
};

export const polarityTextMap = ['失望', '平常', '开心'];

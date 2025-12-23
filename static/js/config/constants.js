// constants.js
export const CONFIG = {
    // 使用相对地址：前端打开在 5001 时自动请求 5001；打开在 5000 时自动请求 5000
    apiUrl: `${window.location.origin}/api/chat`,
    wsUrl: `${window.location.origin}`,
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

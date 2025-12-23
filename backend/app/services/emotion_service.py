"""
emotion_service.py - 情感分析服务层

第 3 步：服务层内聚实现
- 直接在 backend/services 内实现百度情感分析（不再依赖旧 config.py / 旧 services）。
"""

from __future__ import annotations

import time
from typing import Optional

import requests

from ..config.settings import Settings


class BaiduEmotionAnalyzer:
    """百度AI情感倾向分析工具类（移植自旧实现，保持返回结构一致）"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token: Optional[str] = None
        self.token_expire_time = 0.0

    def _get_access_token(self) -> str:
        token_url = (
            "https://aip.baidubce.com/oauth/2.0/token"
            f"?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        )
        resp = requests.get(token_url, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        if "access_token" not in result:
            raise RuntimeError(f"获取Token失败：{result}")
        self.access_token = result["access_token"]
        # expires_in 单位秒，提前 1 天过期
        self.token_expire_time = time.time() + (float(result.get("expires_in", 0)) - 86400.0)
        return self.access_token

    def analyze_emotion(self, text: str) -> dict:
        if not self.access_token or time.time() > self.token_expire_time:
            self._get_access_token()

        emotion_url = (
            "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify"
            f"?access_token={self.access_token}"
        )
        payload = {"text": text, "mode": "precise"}
        resp = requests.post(emotion_url, json=payload, timeout=10)
        resp.raise_for_status()
        result = resp.json()

        if "items" in result and result["items"]:
            item = result["items"][0]
            emotion_result = {
                "polarity": item.get("sentiment", 1),
                "confidence": item.get("confidence", 0.5),
                "emotion": item.get("emotion", "neutral"),
            }
            emotion_map = {
                "sad": "难过",
                "happy": "开心",
                "angry": "生气",
                "tired": "疲惫",
                "anxious": "焦虑",
                "excited": "兴奋",
                "scared": "害怕",
                "hate": "厌恶",
                "fear": "恐惧",
                "surprise": "惊讶",
                "neutral": "中性",
            }
            try:
                emotion_result["emotion"] = emotion_map.get(str(emotion_result["emotion"]).lower(), "中性")
            except Exception:
                emotion_result["emotion"] = "中性"
            return emotion_result

        return {"polarity": 1, "confidence": 0.9, "emotion": "中性"}


_analyzer: Optional[BaiduEmotionAnalyzer] = None


def analyze_emotion(text: str) -> Optional[dict]:
    """
    返回与旧后端一致的结构：
    { polarity: 0/1/2, confidence: 0-1, emotion: 中文标签 }
    未配置百度 Key 时返回 None（保持“可选”特性）。
    """
    global _analyzer
    settings = Settings.load()
    if not settings.BAIDU_API_KEY or not settings.BAIDU_SECRET_KEY:
        return None

    if _analyzer is None:
        _analyzer = BaiduEmotionAnalyzer(settings.BAIDU_API_KEY, settings.BAIDU_SECRET_KEY)

    try:
        return _analyzer.analyze_emotion(text)
    except Exception:
        # 保持稳定：异常时不让接口崩
        return {"polarity": 1, "confidence": 0.9, "emotion": "中性"}



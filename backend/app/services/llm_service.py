"""
llm_service.py - LLM 服务层

第 3 步：服务层内聚实现
- 直接在 backend/services 内实现 DeepSeek / 火山引擎 调用
- 在这里统一做 C3KG 常识注入 + 情感提示词注入（由 routes 传入 persona 的 system_prompt）
"""

from __future__ import annotations

from typing import List, Optional, Dict

import requests
from openai import OpenAI

from ..config.settings import Settings
from ..utils.common_sense_utils import get_c3kg_knowledge


def get_reply(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    emotion_data: Optional[dict] = None,
    system_prompt: Optional[str] = None,
) -> str:
    settings = Settings.load()
    provider = (settings.AI_PROVIDER or "deepseek").strip().lower()

    # 1) 组装系统提示词（人格 prompt + C3KG 常识 + 情感提示）
    base_system_prompt = system_prompt or "你是一个温暖、善解人意且知识渊博的伴侣。"

    # C3KG 注入
    try:
        c3kg = get_c3kg_knowledge(user_message, top_k=3)
        if c3kg:
            base_system_prompt += (
                f"\n\n{c3kg}\n\n请参考上述相关常识来理解和回复用户的问题，让回复更加符合常识和逻辑。"
            )
    except Exception:
        pass

    # 情感注入（如果有）
    if emotion_data and emotion_data.get("emotion"):
        emotion_label = emotion_data.get("emotion", "中性")
        polarity_text = ["失望", "平常", "开心"][emotion_data.get("polarity", 1)]
        base_system_prompt += f"""

【用户当前情感状态】
- 情绪标签：{emotion_label}
- 情感极性：{polarity_text}
- 可信度：{emotion_data.get('confidence', 0.5):.1%}

请根据用户的情绪状态，调整你的回复方式：
- 如果用户感到负面（如疲惫、委屈、生气），请更加温柔、理解、贴心，多用安慰和鼓励。
- 如果用户感到正面（如开心、兴奋），请分享他的快乐，用更活跃、热情的语气回应。
- 始终保持同理心，让用户感受到你真的在倾听和关心他的情绪。
"""

    history = conversation_history or []

    # 2) 调用模型
    if provider == "volcengine":
        return _call_volcengine(settings, base_system_prompt, history, user_message)
    return _call_deepseek(settings, base_system_prompt, history, user_message)

def _call_deepseek(
    settings: Settings,
    system_prompt: str,
    history: List[Dict[str, str]],
    user_message: str,
) -> str:
    if not settings.DEEPSEEK_API_KEY:
        return "抱歉，我现在还没有配置好（缺少 DEEPSEEK_API_KEY）。"

    api_url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}", "Content-Type": "application/json"}

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    # history: [{'role':'user'|'assistant', 'content': '...'}]
    for m in history:
        role = m.get("role")
        content = m.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    payload = {"model": "deepseek-chat", "messages": messages, "max_tokens": 500, "temperature": 0.7, "stream": False}

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return "抱歉，我现在有点连接不稳定，请稍后再和我聊天吧。"


def _call_volcengine(
    settings: Settings,
    system_prompt: str,
    history: List[Dict[str, str]],
    user_message: str,
) -> str:
    if not settings.VOLCENGINE_API_KEY:
        return "抱歉，我现在还没有配置好（缺少 VOLCENGINE_API_KEY）。"

    model = settings.VOLCENGINE_MODEL or "deepseek-v3-2-251201"
    client = OpenAI(base_url=settings.VOLCENGINE_BASE_URL or "https://ark.cn-beijing.volces.com/api/v3", api_key=settings.VOLCENGINE_API_KEY)

    # 这里沿用你旧 volcengine_service 的“responses.create + input 列表”形式，确保兼容
    input_messages: List[Dict[str, str]] = [
        {"role": "user", "content": system_prompt},
        {"role": "assistant", "content": "好的，我明白了。"},
    ]
    for m in history:
        role = m.get("role")
        content = m.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            input_messages.append({"role": role, "content": content})
    input_messages.append({"role": "user", "content": user_message})

    try:
        resp = client.responses.create(model=model, input=input_messages)
        if resp.status == "completed" and resp.output:
            for msg in resp.output:
                if hasattr(msg, "content"):
                    for c in msg.content:
                        if hasattr(c, "text"):
                            return c.text
        raise RuntimeError(f"volcengine status abnormal: {getattr(resp, 'status', None)}")
    except Exception:
        return "抱歉，我现在有点连接不稳定，请稍后再和我聊天吧。"



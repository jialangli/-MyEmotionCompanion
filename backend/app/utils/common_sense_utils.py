"""
common_sense_utils.py - 常识增强工具（C3KG）

第 4 步（去掉兼容层）：在 backend 内部直接加载 `c3kg_data.json` 并做检索，
不再 import 项目根的旧 `services/c3kg_retriever.py`。
"""

from __future__ import annotations

import json
import os
import re
from typing import List, Dict, Optional

from ..config.settings import Settings


_data_cache: Optional[List[Dict]] = None


def _load_data() -> List[Dict]:
    global _data_cache
    if _data_cache is not None:
        return _data_cache

    settings = Settings.load()
    path = settings.C3KG_DATA_PATH
    if not path or not os.path.exists(path):
        _data_cache = []
        return _data_cache

    with open(path, "r", encoding="utf-8") as f:
        _data_cache = json.load(f)
    return _data_cache


def _extract_keywords(text: str) -> List[str]:
    stopwords = {
        "的",
        "了",
        "和",
        "是",
        "就",
        "都",
        "而",
        "及",
        "与",
        "这",
        "那",
        "在",
        "有",
        "人",
        "某",
        "我",
        "你",
        "他",
        "她",
        "它",
        "我们",
        "你们",
        "什么",
        "怎么",
        "为什么",
        "如何",
        "吗",
        "呢",
        "啊",
        "吧",
        "哦",
    }
    words = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    return [w for w in words if w not in stopwords]


def _jaccard(a: List[str], b: List[str]) -> float:
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


def _score(user_message: str, item: Dict) -> float:
    uk = _extract_keywords(user_message)
    ik = item.get("keywords", []) or []
    keyword_score = _jaccard(uk, ik)
    event_score = _jaccard(uk, _extract_keywords(item.get("event", "")))

    knowledge_scores = []
    for k in (item.get("knowledge") or [])[:5]:
        content = k.get("content", "")
        if content:
            knowledge_scores.append(_jaccard(uk, _extract_keywords(content)))
    max_k = max(knowledge_scores) if knowledge_scores else 0.0

    return keyword_score * 0.4 + event_score * 0.4 + max_k * 0.2


def get_c3kg_knowledge(user_message: str, top_k: int = 3) -> str:
    data = _load_data()
    if not data:
        return ""

    scored = []
    for item in data:
        s = _score(user_message, item)
        if s > 0:
            scored.append((s, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    if not top:
        return ""

    lines = ["【相关常识】"]
    for i, (s, item) in enumerate(top, 1):
        event = item.get("event", "")
        lines.append(f"\n{i}. 事件：{event}")
        lines.append("   相关常识：")
        for k in (item.get("knowledge") or [])[:3]:
            rn = k.get("relation_name") or k.get("relation") or ""
            c = k.get("content", "")
            if c:
                lines.append(f"   - {rn}：{c}")
    return "\n".join(lines)



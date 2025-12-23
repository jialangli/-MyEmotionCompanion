"""
request_utils.py - 请求工具
"""

from __future__ import annotations

import json
import urllib.parse
from flask import Request


def get_json_required(req: Request) -> dict:
    # 0) 先缓存原始 body（避免 get_json() 消耗流后拿不到数据）
    raw_bytes = req.get_data(cache=True) or b""

    # 1) 常规解析（Content-Type: application/json）
    data = req.get_json(silent=True)
    if isinstance(data, dict):
        return data

    # 2) 兜底：优先尝试 request.form（常见于 application/x-www-form-urlencoded）
    # - 情况 A：正常表单键值对 => 直接转 dict
    # - 情况 B：整段 JSON 被当成一个 key（value 为空）=> 尝试把 key 当 JSON 解析
    if req.form:
        try:
            form_dict = req.form.to_dict(flat=True)
        except Exception:
            form_dict = dict(req.form)

        if len(form_dict) == 1:
            only_key = next(iter(form_dict.keys()))
            only_val = form_dict.get(only_key)
            if (only_val is None or only_val == "") and isinstance(only_key, str):
                s = only_key.strip()
                if s.startswith("{") and s.endswith("}"):
                    try:
                        parsed = json.loads(s)
                        if isinstance(parsed, dict):
                            return parsed
                    except Exception:
                        pass

        return form_dict

    # 3) 兜底：从 request.data 里按多种编码恢复 JSON
    if raw_bytes:
        for enc in ("utf-8-sig", "utf-8", "utf-16", "utf-16le", "utf-16be", "gbk"):
            try:
                raw = raw_bytes.decode(enc).strip()
                if not raw:
                    continue

                # 3.1) 直接 JSON
                if raw.startswith("{") and raw.endswith("}"):
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        return parsed

                # 3.2) URL 编码：a=1&b=2 或 payload=%7B...%7D
                qs = urllib.parse.parse_qs(raw, keep_blank_values=True)
                if qs:
                    # payload 优先
                    for k in ("payload", "data", "json", "body"):
                        if k in qs and qs[k]:
                            cand = qs[k][0].strip()
                            if cand.startswith("{") and cand.endswith("}"):
                                try:
                                    parsed = json.loads(cand)
                                    if isinstance(parsed, dict):
                                        return parsed
                                except Exception:
                                    pass
                    # 否则把 querystring 当 dict（取第一个值）
                    return {k: (v[0] if isinstance(v, list) and v else v) for k, v in qs.items()}
            except Exception:
                continue

    raise ValueError("请求体必须为 JSON object")



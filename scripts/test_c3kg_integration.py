# scripts/test_c3kg_integration.py - 项目内集成测试：C3KG 检索 -> Prompt 注入 ->（可选）LLM
"""
目标：
1) 直接在项目里跑：验证 “用户消息 -> C3KG 检索 -> 注入 Prompt” 的效果（可视化）。
2) 若已配置 LLM Key（DeepSeek 或火山引擎），可选执行一次真实调用。

建议运行方式（Windows）：
- 优先用项目自带虚拟环境：
  MyEmotionCompanion\\venv\\Scripts\\python.exe MyEmotionCompanion\\scripts\\test_c3kg_integration.py
"""

import os
import sys
from typing import List, Optional


def _project_root() -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def _print_sep(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def _try_import_ai_service():
    """
    尝试导入项目 AI 服务（会依赖 config -> python-dotenv）。
    导入失败时返回 None，不影响 C3KG 检索链路测试。
    """
    try:
        from services.ai_service import get_ai_reply  # type: ignore

        return get_ai_reply
    except Exception as e:
        print(f"[提示] AI 服务导入失败（不影响检索链路测试）：{e}")
        print("[提示] 若你希望进行真实 LLM 调用，请用项目 venv 运行，并确保已安装依赖/配置 API Key。")
        return None


def _build_prompt_preview(user_message: str, c3kg_knowledge: str) -> str:
    """
    复刻 ai_service.py 中的注入逻辑：把检索到的常识拼到 system prompt 末尾。
    这里只做“可视化预览”，不改变线上逻辑。
    """
    base = "【SYSTEM】你是一个温暖、善解人意且知识渊博的伴侣（略）。"
    if not c3kg_knowledge:
        return base + "\n\n【C3KG】(未检索到相关常识)"
    return (
        base
        + "\n\n"
        + c3kg_knowledge
        + "\n\n请参考上述相关常识来理解和回复用户的问题，让回复更加符合常识和逻辑。"
        + "\n\n【USER】"
        + user_message
    )


def run_retrieval_demo(test_messages: List[str]) -> None:
    _print_sep("步骤 1/2：C3KG 检索 + Prompt 注入预览（不调用 LLM）")

    # 延迟导入，确保脚本可在任意 cwd 运行
    sys.path.insert(0, _project_root())
    from services.c3kg_retriever import get_c3kg_retriever  # type: ignore

    retriever = get_c3kg_retriever()

    for msg in test_messages:
        print("\n---")
        print(f"[用户消息] {msg}")
        c3kg_knowledge = retriever.get_relevant_knowledge(msg, top_k=3)
        if c3kg_knowledge:
            print("[检索结果] 找到相关常识（已截断展示前 600 字符）：")
            print(c3kg_knowledge[:600] + ("..." if len(c3kg_knowledge) > 600 else ""))
        else:
            print("[检索结果] 未检索到相关常识")

        preview = _build_prompt_preview(msg, c3kg_knowledge)
        print("\n[Prompt 注入预览]（已截断展示前 900 字符）：")
        print(preview[:900] + ("..." if len(preview) > 900 else ""))


def run_optional_llm_call(user_message: str) -> None:
    _print_sep("步骤 2/2（可选）：走项目真实对话链路（会调用 LLM）")

    get_ai_reply = _try_import_ai_service()
    if get_ai_reply is None:
        print("[跳过] 未能导入 AI 服务，因此跳过真实 LLM 调用。")
        return

    # 尝试调用一次真实 LLM（如果未配置 key，项目本身可能会报错或返回兜底文案）
    try:
        reply = get_ai_reply(user_message=user_message, conversation_history=[], emotion_data=None, system_prompt=None)
        print(f"[用户消息] {user_message}")
        print(f"\n[AI 回复] {reply}")
    except Exception as e:
        print(f"[失败] 真实 LLM 调用失败：{e}")
        print("[提示] 请检查 .env 配置（DEEPSEEK_API_KEY / VOLCENGINE_API_KEY 等）以及网络可用性。")


def main():
    # 让输出尽量不受编码影响（Windows 控制台常见为 GBK）
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # py3.7+
    except Exception:
        pass

    test_messages = [
        "某人完全放弃某物",
        "我今天有点沮丧，想放弃这份工作",
        "有人帮助了我，我很感激",
        "我最近压力很大，睡不好",
    ]

    run_retrieval_demo(test_messages)

    # 可选：走一次真实调用（只用第一条，避免花费太多 token）
    run_optional_llm_call("我今天有点沮丧，想放弃这份工作")

    _print_sep("完成")
    print("[完成] 集成测试脚本执行结束。")


if __name__ == "__main__":
    main()



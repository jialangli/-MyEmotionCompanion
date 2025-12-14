#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试火山引擎API集成
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from services.ai_service import get_ai_reply

def test_volcengine_api():
    """测试火山引擎API"""
    print("=" * 60)
    print("测试火山引擎API集成")
    print("=" * 60)
    
    # 检查配置
    print(f"\n当前AI提供商: {config.AI_PROVIDER}")
    print(f"火山引擎API URL: {config.VOLCENGINE_API_URL}")
    print(f"火山引擎模型: {config.VOLCENGINE_MODEL}")
    print(f"火山引擎API Key: {config.VOLCENGINE_API_KEY[:20]}...")
    
    # 测试简单对话
    test_messages = [
        "你好",
        "今天天气怎么样？",
        "你能帮我讲个笑话吗？"
    ]
    
    print("\n开始测试对话...")
    history = []
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n--- 测试 {i}/{len(test_messages)} ---")
        print(f"[用户] {msg}")
        
        try:
            reply = get_ai_reply(msg, history)
            print(f"[AI] {reply}")
            
            # 更新历史
            history.append({"role": "user", "content": msg})
            history.append({"role": "assistant", "content": reply})
            
            # 限制历史长度
            if len(history) > 6:
                history = history[-6:]
                
        except Exception as e:
            print(f"[错误] {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_volcengine_api()

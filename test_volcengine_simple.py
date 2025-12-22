# -*- coding: utf-8 -*-
"""
使用OpenAI SDK测试火山引擎API - 不使用web_search工具
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取API KEY
api_key = os.getenv('VOLCENGINE_API_KEY')

print("=" * 60)
print("使用OpenAI SDK测试火山引擎API（不使用工具）")
print("=" * 60)
print(f"API Key: {api_key[:20]}...")
print(f"Base URL: https://ark.cn-beijing.volces.com/api/v3")

client = OpenAI(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=api_key
)

try:
    print("\n测试 1: 简单问候")
    response = client.responses.create(
        model="deepseek-v3-2-251201",
        input=[{"role": "user", "content": "你好"}],
    )
    
    print(f"状态: {response.status}")
    if response.output:
        for msg in response.output:
            if hasattr(msg, 'content'):
                for content in msg.content:
                    if hasattr(content, 'text'):
                        print(f"回复: {content.text}")
    
    print("\n" + "="*60)
    print("\n测试 2: 带系统提示词的对话")
    response2 = client.responses.create(
        model="deepseek-v3-2-251201",
        input=[
            {"role": "user", "content": "你是一个温暖友好的AI助手"},
            {"role": "assistant", "content": "好的，我会保持温暖友好的语气"},
            {"role": "user", "content": "给我讲个笑话吧"}
        ],
    )
    
    print(f"状态: {response2.status}")
    if response2.output:
        for msg in response2.output:
            if hasattr(msg, 'content'):
                for content in msg.content:
                    if hasattr(content, 'text'):
                        print(f"回复: {content.text}")
    
    print("\n" + "="*60)
    print("测试成功！")
    
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()

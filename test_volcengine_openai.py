#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用OpenAI SDK测试火山引擎API
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取API KEY
api_key = os.getenv('VOLCENGINE_API_KEY')

print("=" * 60)
print("使用OpenAI SDK测试火山引擎API")
print("=" * 60)
print(f"API Key: {api_key[:20]}...")
print(f"Base URL: https://ark.cn-beijing.volces.com/api/v3")

client = OpenAI(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=api_key
)

tools = [{
    "type": "web_search",
    "max_keyword": 2,
}]

try:
    print("\n发送请求: 北京的天气怎么样？")
    # 创建一个对话请求
    response = client.responses.create(
        model="deepseek-v3-2-251201",
        input=[{"role": "user", "content": "北京的天气怎么样？"}],
        tools=tools,
    )
    
    print("\n响应结果:")
    print(response)
    
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()

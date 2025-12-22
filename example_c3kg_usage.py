# example_c3kg_usage.py - C3KG 模块使用示例
"""
展示如何使用 C3KG 知识检索功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from services.c3kg_retriever import get_c3kg_retriever
from services.ai_service import get_ai_reply

def example_1_retrieve_knowledge():
    """示例 1：直接使用检索器检索常识"""
    print("=" * 60)
    print("示例 1: 直接检索常识")
    print("=" * 60)
    
    retriever = get_c3kg_retriever()
    
    user_message = "我今天感到很沮丧，想要放弃"
    
    # 检索相关常识
    retrieved = retriever.retrieve(user_message, top_k=2)
    
    print(f"用户消息: {user_message}\n")
    print("检索到的常识:")
    for idx, item in enumerate(retrieved, 1):
        print(f"\n{idx}. 事件: {item['event']}")
        print(f"   得分: {item['score']:.3f}")
        print(f"   相关常识:")
        for knowledge in item['knowledge'][:3]:
            print(f"      - {knowledge.get('relation_name', '')}: {knowledge.get('content', '')}")

def example_2_format_for_prompt():
    """示例 2：获取格式化的 Prompt 文本"""
    print("\n" + "=" * 60)
    print("示例 2: 获取格式化的 Prompt 文本")
    print("=" * 60)
    
    retriever = get_c3kg_retriever()
    
    user_message = "有人帮助了我，我很感激"
    
    # 获取格式化的常识 Prompt
    formatted_knowledge = retriever.get_relevant_knowledge(user_message, top_k=2)
    
    print(f"用户消息: {user_message}\n")
    print("格式化后的常识 Prompt:")
    print("-" * 60)
    print(formatted_knowledge)

def example_3_integrated_with_ai():
    """示例 3：与 AI 服务集成（自动检索和注入）"""
    print("\n" + "=" * 60)
    print("示例 3: 与 AI 服务集成（自动检索和注入）")
    print("=" * 60)
    
    # 注意：这需要配置了 API Key 才能运行
    print("使用 get_ai_reply() 时，C3KG 检索会自动执行：")
    print("\n```python")
    print("from services.ai_service import get_ai_reply")
    print("")
    print("reply = get_ai_reply(")
    print("    user_message='我今天感到很沮丧'")
    print(")")
    print("```")
    print("\n系统会自动：")
    print("1. 检索与用户消息相关的 C3KG 常识")
    print("2. 将常识注入到系统 Prompt 中")
    print("3. LLM 基于增强后的 Prompt 生成回复")

def main():
    """主函数"""
    print("\nC3KG 知识检索模块使用示例\n")
    
    # 检查数据文件是否存在
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    json_path = os.path.join(data_dir, 'c3kg_data.json')
    
    if not os.path.exists(json_path):
        print("[警告] c3kg_data.json 不存在！")
        print("请先运行: python utils/c3kg_converter.py")
        print("\n或者运行: python scripts/test_c3kg.py (会自动转换)")
        return
    
    try:
        example_1_retrieve_knowledge()
        example_2_format_for_prompt()
        example_3_integrated_with_ai()
        
        print("\n" + "=" * 60)
        print("[完成] 所有示例运行完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[错误] 运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()


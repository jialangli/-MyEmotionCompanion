# scripts/test_retriever_simple.py - 简单的检索功能测试（不依赖其他模块）
"""
简单的 C3KG 检索功能测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.c3kg_retriever import C3KGRetriever

def main():
    """主测试函数"""
    print("=" * 60)
    print("C3KG 检索功能简单测试")
    print("=" * 60)
    
    # 初始化检索器
    print("\n正在初始化检索器...")
    retriever = C3KGRetriever()
    
    if not retriever.knowledge_data:
        print("[错误] 未加载知识数据，请检查 c3kg_data.json 是否存在")
        return
    
    print(f"[成功] 已加载 {len(retriever.knowledge_data)} 条知识记录\n")
    
    # 测试不同的查询
    test_queries = [
        "有人帮助了我",
        "我感到沮丧",
        "我想要放弃",
        "有人鼓励我",
        "我感到开心",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print(f"{'='*60}")
        
        # 检索相关常识
        results = retriever.retrieve(query, top_k=2)
        
        if results:
            for idx, item in enumerate(results, 1):
                print(f"\n结果 {idx} (相关性得分: {item['score']:.3f}):")
                print(f"  事件: {item['event']}")
                print(f"  相关常识 (前3条):")
                for knowledge in item['knowledge'][:3]:
                    relation = knowledge.get('relation_name', knowledge.get('relation', ''))
                    content = knowledge.get('content', '')
                    print(f"    - {relation}: {content}")
        else:
            print("  未找到相关常识")
        
        # 显示格式化的 Prompt
        formatted = retriever.format_knowledge_for_prompt(results)
        if formatted:
            print(f"\n格式化后的 Prompt:")
            print("-" * 60)
            print(formatted[:200] + "..." if len(formatted) > 200 else formatted)
    
    print(f"\n{'='*60}")
    print("[完成] 测试完成！")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()



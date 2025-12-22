# scripts/test_retriever_with_data.py - 使用实际数据关键词测试检索功能
"""
使用实际数据中的关键词测试检索功能
"""
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.c3kg_retriever import C3KGRetriever

def main():
    """主测试函数"""
    print("=" * 60)
    print("C3KG 检索功能测试（使用实际数据关键词）")
    print("=" * 60)
    
    # 初始化检索器
    print("\n正在初始化检索器...")
    retriever = C3KGRetriever()
    
    if not retriever.knowledge_data:
        print("[错误] 未加载知识数据")
        return
    
    print(f"[成功] 已加载 {len(retriever.knowledge_data)} 条知识记录\n")
    
    # 从实际数据中提取一些测试查询（基于实际事件和关键词）
    test_queries = [
        "某人完全放弃某物",  # 直接使用事件
        "放弃工作",  # 包含关键词"放弃"
        "感到沮丧",  # 包含关键词"沮丧"
        "某人结婚了",  # 使用实际事件
        "有人帮助了我",  # 包含"帮助"
        "我想要找新工作",  # 包含"新工作"
        "我感到开心",  # 情感相关
    ]
    
    print(f"\n测试 {len(test_queries)} 个查询...\n")
    
    success_count = 0
    for idx, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"测试 {idx}/{len(test_queries)}: {query}")
        print(f"{'='*60}")
        
        # 检索相关常识
        results = retriever.retrieve(query, top_k=2)
        
        if results:
            success_count += 1
            print(f"[成功] 找到 {len(results)} 条相关常识")
            for i, item in enumerate(results, 1):
                print(f"\n  结果 {i} (得分: {item['score']:.3f}):")
                print(f"    事件: {item['event']}")
                print(f"    相关常识 (前2条):")
                for knowledge in item['knowledge'][:2]:
                    relation = knowledge.get('relation_name', knowledge.get('relation', ''))
                    content = knowledge.get('content', '')
                    print(f"      - {relation}: {content}")
        else:
            print("[未找到] 未检索到相关常识")
    
    print(f"\n{'='*60}")
    print(f"测试完成！成功匹配: {success_count}/{len(test_queries)}")
    print(f"{'='*60}")
    
    # 测试格式化功能
    print(f"\n{'='*60}")
    print("测试 Prompt 格式化功能")
    print(f"{'='*60}")
    
    test_query = "某人完全放弃某物"
    results = retriever.retrieve(test_query, top_k=2)
    formatted = retriever.format_knowledge_for_prompt(results)
    
    print(f"\n查询: {test_query}")
    print(f"\n格式化后的 Prompt:")
    print("-" * 60)
    print(formatted)
    print("-" * 60)

if __name__ == '__main__':
    main()


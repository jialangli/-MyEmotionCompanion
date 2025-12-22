# scripts/test_c3kg.py - C3KG 模块测试脚本
"""
测试 C3KG 数据转换和检索功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.c3kg_converter import main as convert_main
from services.c3kg_retriever import C3KGRetriever

def test_converter():
    """测试数据转换"""
    print("=" * 60)
    print("测试 1: 数据转换")
    print("=" * 60)
    try:
        convert_main()
        print("[通过] 数据转换测试通过")
        return True
    except Exception as e:
        print(f"[失败] 数据转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_retriever():
    """测试检索功能"""
    print("\n" + "=" * 60)
    print("测试 2: 知识检索")
    print("=" * 60)
    
    try:
        retriever = C3KGRetriever()
        
        if not retriever.knowledge_data:
            print("[警告] 未加载知识数据，请先运行数据转换")
            return False
        
        test_messages = [
            "我今天感到沮丧",
            "我想放弃这份工作",
            "有人帮助了我，我很感激",
            "我感到很开心",
        ]
        
        for msg in test_messages:
            print(f"\n用户消息: {msg}")
            print("-" * 60)
            
            retrieved = retriever.retrieve(msg, top_k=2)
            if retrieved:
                for idx, item in enumerate(retrieved, 1):
                    print(f"\n结果 {idx} (得分: {item['score']:.3f}):")
                    print(f"  事件: {item['event']}")
                    print(f"  相关常识:")
                    for knowledge in item['knowledge'][:3]:
                        print(f"    - {knowledge.get('relation_name', '')}: {knowledge.get('content', '')}")
            else:
                print("  未检索到相关常识")
        
        print("\n[通过] 检索功能测试通过")
        return True
        
    except Exception as e:
        print(f"[失败] 检索功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_formatting():
    """测试 Prompt 格式化"""
    print("\n" + "=" * 60)
    print("测试 3: Prompt 格式化")
    print("=" * 60)
    
    try:
        retriever = C3KGRetriever()
        
        if not retriever.knowledge_data:
            print("[警告] 未加载知识数据，请先运行数据转换")
            return False
        
        test_message = "我今天感到很沮丧，不知道该怎么办"
        
        formatted = retriever.get_relevant_knowledge(test_message, top_k=2)
        print(f"用户消息: {test_message}")
        print("\n格式化后的常识 Prompt:")
        print("-" * 60)
        print(formatted)
        
        print("\n[通过] Prompt 格式化测试通过")
        return True
        
    except Exception as e:
        print(f"[失败] Prompt 格式化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("C3KG 模块完整测试")
    print("=" * 60)
    
    results = []
    
    # 检查数据文件是否存在
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    atomic_path = os.path.join(data_dir, 'ATOMIC_Chinese.tsv')
    json_path = os.path.join(data_dir, 'c3kg_data.json')
    
    if not os.path.exists(json_path):
        print("\n检测到 c3kg_data.json 不存在，开始数据转换...")
        results.append(("数据转换", test_converter()))
    else:
        print(f"\n[跳过] 检测到 c3kg_data.json 已存在（{os.path.getsize(json_path) / 1024 / 1024:.2f} MB），跳过转换")
        results.append(("数据转换", True))
    
    # 测试检索功能
    results.append(("知识检索", test_retriever()))
    
    # 测试 Prompt 格式化
    results.append(("Prompt格式化", test_prompt_formatting()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, result in results:
        status = "[通过]" if result else "[失败]"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n[成功] 所有测试通过！")
    else:
        print("\n[警告] 部分测试失败，请检查错误信息")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


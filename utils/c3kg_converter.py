# utils/c3kg_converter.py - C3KG 数据转换工具
"""
将原始 C3KG 数据（ATOMIC_Chinese.tsv, head_phrase.csv, head_shortSentence.csv）
转换为可检索的结构化 JSON 格式：事件 + 常识 + 对话流 + 关键词
"""
import csv
import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Set

# 关系类型映射（用于组织常识）
RELATION_TYPES = {
    'xWant': '想要',
    'xEffect': '导致',
    'xReact': '反应',
    'xAttr': '属性',
    'xIntent': '意图',
    'xNeed': '需要',
    'oWant': '他人想要',
    'oEffect': '他人导致',
    'oReact': '他人反应',
}

def load_atomic_data(tsv_path: str) -> Dict[str, List[Dict]]:
    """
    加载 ATOMIC_Chinese.tsv 文件，按事件（head）分组
    
    返回: {事件: [{'relation': 关系类型, 'tail': 常识内容}, ...]}
    """
    atomic_data = defaultdict(list)
    
    print(f"正在加载 {tsv_path}...")
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        count = 0
        for row in reader:
            head = row.get('head', '').strip()
            relation = row.get('relation', '').strip()
            tail = row.get('tail', '').strip()
            
            if head and relation and tail:
                atomic_data[head].append({
                    'relation': relation,
                    'tail': tail
                })
                count += 1
                if count % 100000 == 0:
                    print(f"  已处理 {count} 条记录...")
    
    print(f"  总共加载 {count} 条常识记录，{len(atomic_data)} 个唯一事件")
    return dict(atomic_data)

def load_head_mapping(csv_path: str) -> Dict[str, str]:
    """
    加载 head_phrase.csv 或 head_shortSentence.csv，创建 head -> head_translated 映射
    
    返回: {原始head: 中文翻译}
    """
    head_mapping = {}
    
    print(f"正在加载 {csv_path}...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            head = row.get('head', '').strip()
            translated = row.get('head_translated', '').strip()
            
            if head and translated:
                head_mapping[head] = translated
                count += 1
    
    print(f"  加载了 {count} 条映射记录")
    return head_mapping

def extract_keywords(text: str) -> List[str]:
    """
    从文本中提取关键词（简单实现：分词和过滤）
    """
    # 移除常见停用词
    stopwords = {'的', '了', '和', '是', '就', '都', '而', '及', '與', '這', '那', '在', '有', '人', '某'}
    
    # 简单分词：按常见分隔符分割
    words = re.findall(r'[\u4e00-\u9fff]+', text)
    
    # 过滤停用词和单字
    keywords = [w for w in words if w not in stopwords and len(w) >= 2]
    
    return keywords

def generate_dialogue_flow(event: str, knowledge_items: List[Dict]) -> List[str]:
    """
    根据事件和常识生成对话流示例
    
    返回: [对话示例1, 对话示例2, ...]
    """
    dialogue_flows = []
    
    # 基于不同关系类型生成对话示例
    for item in knowledge_items[:3]:  # 每个事件最多取3个常识生成对话
        relation = item['relation']
        tail = item['tail']
        
        # 根据关系类型生成不同的对话流
        if relation == 'xWant':
            dialogue = f"用户：{event.replace('某人', '我')}，我应该怎么做？\n助手：你可以考虑{tail}。"
        elif relation == 'xEffect':
            dialogue = f"用户：如果{event.replace('某人', '我')}会怎样？\n助手：这可能会导致{tail}。"
        elif relation == 'xReact':
            dialogue = f"用户：{event.replace('某人', '我')}，我感觉{tail}。\n助手：我理解你的感受。"
        elif relation == 'oReact':
            dialogue = f"用户：有人{event.replace('某人', '')}，其他人会怎么想？\n助手：其他人可能会感到{tail}。"
        else:
            dialogue = f"用户：关于{event}，有什么相关常识？\n助手：通常来说，{tail}。"
        
        dialogue_flows.append(dialogue)
    
    return dialogue_flows

def convert_to_structured_json(
    atomic_data: Dict[str, List[Dict]],
    phrase_mapping: Dict[str, str],
    sentence_mapping: Dict[str, str]
) -> List[Dict]:
    """
    将原始数据转换为结构化 JSON 格式
    
    返回: [{
        'event': 事件（中文）,
        'event_original': 原始事件,
        'knowledge': [常识列表],
        'dialogue_flow': [对话流],
        'keywords': [关键词列表]
    }, ...]
    """
    structured_data = []
    
    print("正在转换为结构化格式...")
    processed = 0
    
    for event_original, knowledge_items in atomic_data.items():
        # 查找中文翻译
        event_chinese = sentence_mapping.get(event_original) or phrase_mapping.get(event_original) or event_original
        
        # 组织常识（按关系类型分组）
        knowledge_list = []
        for item in knowledge_items:
            relation = item['relation']
            tail = item['tail']
            relation_name = RELATION_TYPES.get(relation, relation)
            
            knowledge_list.append({
                'relation': relation,
                'relation_name': relation_name,
                'content': tail
            })
        
        # 生成对话流
        dialogue_flows = generate_dialogue_flow(event_chinese, knowledge_items)
        
        # 提取关键词（从事件和常识中）
        event_keywords = extract_keywords(event_chinese)
        knowledge_keywords = []
        for item in knowledge_items[:10]:  # 只从部分常识中提取关键词
            knowledge_keywords.extend(extract_keywords(item['tail']))
        
        all_keywords = list(set(event_keywords + knowledge_keywords))[:20]  # 最多20个关键词
        
        # 构建结构化数据
        structured_item = {
            'event': event_chinese,
            'event_original': event_original,
            'knowledge': knowledge_list,
            'dialogue_flow': dialogue_flows,
            'keywords': all_keywords
        }
        
        structured_data.append(structured_item)
        processed += 1
        
        if processed % 10000 == 0:
            print(f"  已处理 {processed} 个事件...")
    
    print(f"转换完成！共 {len(structured_data)} 条结构化数据")
    return structured_data

def main():
    """主函数：执行数据转换"""
    # 确定文件路径（使用绝对路径，确保在不同目录下运行都能找到文件）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')
    data_dir = os.path.normpath(data_dir)  # 规范化路径
    atomic_path = os.path.join(data_dir, 'ATOMIC_Chinese.tsv')
    phrase_path = os.path.join(data_dir, 'head_phrase.csv')
    sentence_path = os.path.join(data_dir, 'head_shortSentence.csv')
    output_path = os.path.join(data_dir, 'c3kg_data.json')
    
    # 检查文件是否存在
    for path in [atomic_path, phrase_path, sentence_path]:
        if not os.path.exists(path):
            print(f"错误：文件不存在 {path}")
            return
    
    # 1. 加载数据
    print("=" * 60)
    print("开始转换 C3KG 数据")
    print("=" * 60)
    
    atomic_data = load_atomic_data(atomic_path)
    phrase_mapping = load_head_mapping(phrase_path)
    sentence_mapping = load_head_mapping(sentence_path)
    
    # 2. 转换为结构化 JSON
    structured_data = convert_to_structured_json(
        atomic_data, phrase_mapping, sentence_mapping
    )
    
    # 3. 保存为 JSON 文件
    print(f"\n正在保存到 {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[完成] 转换完成！已保存 {len(structured_data)} 条数据到 {output_path}")
    print(f"  文件大小：{os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    main()


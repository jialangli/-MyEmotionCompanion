# services/c3kg_retriever.py - C3KG 知识检索模块
"""
C3KG 知识检索模块：根据用户消息匹配相关常识
"""
import json
import os
import re
from typing import List, Dict, Optional
from collections import Counter

class C3KGRetriever:
    """C3KG 知识检索器"""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        初始化检索器
        
        参数:
            data_path: c3kg_data.json 文件路径，如果为 None 则使用默认路径
        """
        if data_path is None:
            # 使用绝对路径，确保在不同目录下运行都能找到文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, '..', 'data')
            data_dir = os.path.normpath(data_dir)  # 规范化路径
            data_path = os.path.join(data_dir, 'c3kg_data.json')
        
        self.data_path = data_path
        self.knowledge_data = []
        self._load_data()
    
    def _load_data(self):
        """加载 C3KG 数据"""
        if not os.path.exists(self.data_path):
            print(f"警告：C3KG 数据文件不存在：{self.data_path}")
            print("请先运行 utils/c3kg_converter.py 生成数据文件")
            return
        
        print(f"正在加载 C3KG 数据：{self.data_path}")
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.knowledge_data = json.load(f)
        
        print(f"[成功] 已加载 {len(self.knowledge_data)} 条知识记录")
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 停用词
        stopwords = {
            '的', '了', '和', '是', '就', '都', '而', '及', '与', '这', '那', 
            '在', '有', '人', '某', '我', '你', '他', '她', '它', '我们', '你们',
            '什么', '怎么', '为什么', '如何', '吗', '呢', '啊', '吧', '哦'
        }
        
        # 提取中文词汇（2个字符及以上）
        words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        
        # 过滤停用词
        keywords = [w for w in words if w not in stopwords]
        
        return keywords
    
    def _calculate_keyword_similarity(self, user_keywords: List[str], item_keywords: List[str]) -> float:
        """计算关键词相似度（简单的 Jaccard 相似度）"""
        if not user_keywords or not item_keywords:
            return 0.0
        
        user_set = set(user_keywords)
        item_set = set(item_keywords)
        
        intersection = len(user_set & item_set)
        union = len(user_set | item_set)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _calculate_text_similarity(self, user_text: str, target_text: str) -> float:
        """计算文本相似度（基于关键词重叠）"""
        user_keywords = self._extract_keywords_from_text(user_text)
        target_keywords = self._extract_keywords_from_text(target_text)
        
        return self._calculate_keyword_similarity(user_keywords, target_keywords)
    
    def _score_item(self, user_message: str, item: Dict) -> float:
        """
        对知识项进行评分
        
        参数:
            user_message: 用户消息
            item: 知识项（包含 event, knowledge, keywords 等）
        
        返回:
            评分（0-1之间）
        """
        user_keywords = self._extract_keywords_from_text(user_message)
        item_keywords = item.get('keywords', [])
        
        # 1. 关键词匹配得分
        keyword_score = self._calculate_keyword_similarity(user_keywords, item_keywords)
        
        # 2. 事件匹配得分（用户消息与事件描述的相似度）
        event_score = self._calculate_text_similarity(user_message, item.get('event', ''))
        
        # 3. 常识内容匹配得分（检查用户消息是否提及常识内容）
        knowledge_scores = []
        for knowledge in item.get('knowledge', [])[:5]:  # 只检查前5个常识
            content = knowledge.get('content', '')
            if content:
                score = self._calculate_text_similarity(user_message, content)
                knowledge_scores.append(score)
        
        max_knowledge_score = max(knowledge_scores) if knowledge_scores else 0.0
        
        # 综合得分（加权平均）
        final_score = (
            keyword_score * 0.4 +      # 关键词匹配权重 40%
            event_score * 0.4 +        # 事件匹配权重 40%
            max_knowledge_score * 0.2  # 常识匹配权重 20%
        )
        
        return final_score
    
    def retrieve(self, user_message: str, top_k: int = 3) -> List[Dict]:
        """
        根据用户消息检索相关常识
        
        参数:
            user_message: 用户输入的消息
            top_k: 返回最相关的 top_k 条知识
        
        返回:
            [{'event': 事件, 'knowledge': [常识列表], 'score': 得分}, ...]
        """
        if not self.knowledge_data:
            return []
        
        # 对每条知识进行评分
        scored_items = []
        for item in self.knowledge_data:
            score = self._score_item(user_message, item)
            if score > 0:  # 只保留有匹配的知识
                scored_items.append({
                    'event': item.get('event', ''),
                    'event_original': item.get('event_original', ''),
                    'knowledge': item.get('knowledge', []),
                    'dialogue_flow': item.get('dialogue_flow', []),
                    'keywords': item.get('keywords', []),
                    'score': score
                })
        
        # 按得分排序，返回 top_k
        scored_items.sort(key=lambda x: x['score'], reverse=True)
        return scored_items[:top_k]
    
    def format_knowledge_for_prompt(self, retrieved_items: List[Dict]) -> str:
        """
        将检索到的知识格式化为 Prompt 文本
        
        参数:
            retrieved_items: retrieve() 方法返回的知识列表
        
        返回:
            格式化的 Prompt 文本
        """
        if not retrieved_items:
            return ""
        
        prompt_parts = ["【相关常识】"]
        
        for idx, item in enumerate(retrieved_items, 1):
            event = item.get('event', '')
            knowledge_list = item.get('knowledge', [])
            
            if not event or not knowledge_list:
                continue
            
            prompt_parts.append(f"\n{idx}. 事件：{event}")
            prompt_parts.append("   相关常识：")
            
            # 只取前3个常识，避免 Prompt 过长
            for knowledge in knowledge_list[:3]:
                relation_name = knowledge.get('relation_name', knowledge.get('relation', ''))
                content = knowledge.get('content', '')
                if content:
                    prompt_parts.append(f"   - {relation_name}：{content}")
        
        return "\n".join(prompt_parts)
    
    def get_relevant_knowledge(self, user_message: str, top_k: int = 3) -> str:
        """
        便捷方法：检索并格式化知识
        
        参数:
            user_message: 用户消息
            top_k: 返回 top_k 条知识
        
        返回:
            格式化的知识文本（可直接用于 Prompt）
        """
        retrieved = self.retrieve(user_message, top_k)
        return self.format_knowledge_for_prompt(retrieved)

# 全局检索器实例（单例模式）
_retriever_instance = None

def get_c3kg_retriever() -> C3KGRetriever:
    """获取全局 C3KG 检索器实例"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = C3KGRetriever()
    return _retriever_instance

# 测试函数
if __name__ == '__main__':
    print("测试 C3KG 检索模块...")
    
    retriever = C3KGRetriever()
    
    test_messages = [
        "我今天感到沮丧",
        "我想放弃这份工作",
        "我感到很开心",
        "有人帮助了我"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"用户消息：{msg}")
        print(f"{'='*60}")
        
        knowledge = retriever.get_relevant_knowledge(msg, top_k=2)
        print(knowledge)


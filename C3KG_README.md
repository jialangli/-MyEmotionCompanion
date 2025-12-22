# C3KG 知识检索模块使用说明

## 概述

本项目集成了 C3KG（中文常识知识图谱）知识检索功能，能够根据用户消息自动检索相关常识，并将其注入到 LLM 的 Prompt 中，让 AI 生成更有常识、更符合逻辑的回复。

## 功能特性

1. **数据转换**：将原始 C3KG 数据（ATOMIC_Chinese.tsv、head_phrase.csv、head_shortSentence.csv）转换为结构化的 JSON 格式
2. **知识检索**：基于关键词和语义匹配，从知识库中检索与用户消息相关的常识
3. **Prompt 增强**：将检索到的常识自动注入到 LLM Prompt 中，提升回复质量

## 文件结构

```
MyEmotionCompanion/
├── data/
│   ├── ATOMIC_Chinese.tsv          # 原始 C3KG 数据（事件-关系-常识三元组）
│   ├── head_phrase.csv              # 短语映射表
│   ├── head_shortSentence.csv       # 短句映射表
│   └── c3kg_data.json               # 转换后的结构化 JSON（自动生成）
├── utils/
│   └── c3kg_converter.py            # 数据转换脚本
├── services/
│   ├── c3kg_retriever.py            # 知识检索模块
│   ├── ai_service.py                # AI 服务（已集成检索功能）
│   └── volcengine_service.py        # 火山引擎服务（已集成检索功能）
└── scripts/
    └── test_c3kg.py                 # 测试脚本
```

## 快速开始

### 1. 数据转换（首次使用必须执行）

运行数据转换脚本，将原始数据转换为结构化 JSON：

```bash
cd MyEmotionCompanion
python utils/c3kg_converter.py
```

**注意**：
- 数据文件较大（ATOMIC_Chinese.tsv 包含 100 多万条记录），转换可能需要几分钟时间
- 转换完成后会在 `data/c3kg_data.json` 生成结构化数据文件
- 生成的 JSON 文件大小约为几百 MB

### 2. 测试功能

运行测试脚本验证功能是否正常：

```bash
python scripts/test_c3kg.py
```

测试脚本会：
- 检查数据文件是否存在，如不存在则自动运行转换
- 测试知识检索功能
- 测试 Prompt 格式化功能

### 3. 使用

检索功能已自动集成到 `ai_service.py` 和 `volcengine_service.py` 中。当用户发送消息时，系统会自动：

1. 从用户消息中提取关键词
2. 在 C3KG 知识库中检索相关常识
3. 将检索到的常识注入到系统 Prompt 中
4. LLM 基于增强后的 Prompt 生成回复

**无需额外代码**，直接使用 `get_ai_reply()` 函数即可：

```python
from services.ai_service import get_ai_reply

reply = get_ai_reply(
    user_message="我今天感到很沮丧",
    conversation_history=None,
    emotion_data=None
)
```

## 数据格式说明

转换后的 `c3kg_data.json` 格式如下：

```json
[
  {
    "event": "某人完全放弃某物",
    "event_original": "PersonX gives up completely",
    "knowledge": [
      {
        "relation": "xReact",
        "relation_name": "反应",
        "content": "沮丧的"
      },
      {
        "relation": "xWant",
        "relation_name": "想要",
        "content": "找一份新工作"
      }
    ],
    "dialogue_flow": [
      "用户：我完全放弃某物，我应该怎么做？\n助手：你可以考虑找一份新工作。"
    ],
    "keywords": ["放弃", "新工作", "沮丧"]
  }
]
```

## 检索原理

检索模块使用以下策略匹配用户消息和常识：

1. **关键词匹配**（权重 40%）：提取用户消息和知识项的关键词，计算 Jaccard 相似度
2. **事件匹配**（权重 40%）：计算用户消息与事件描述的相似度
3. **常识匹配**（权重 20%）：检查用户消息是否提及常识内容

综合得分排序后，返回 top_k 条最相关的知识。

## 配置选项

在 `services/c3kg_retriever.py` 中可以调整：

- `top_k`：检索返回的常识数量（默认 3 条）
- 检索权重：关键词、事件、常识的匹配权重
- 关键词提取：停用词列表、最小词长等

## 故障排除

### 问题：提示 "C3KG 数据文件不存在"

**解决方案**：
1. 检查 `data/` 目录下是否有 `ATOMIC_Chinese.tsv`、`head_phrase.csv`、`head_shortSentence.csv`
2. 运行 `python utils/c3kg_converter.py` 生成 `c3kg_data.json`

### 问题：数据转换很慢

**原因**：数据文件包含 100 多万条记录，转换需要时间

**解决方案**：
- 正常现象，请耐心等待
- 可以查看控制台输出，了解转换进度

### 问题：检索不到相关常识

**可能原因**：
1. 用户消息与知识库中的事件/常识没有匹配
2. 关键词提取不准确

**解决方案**：
- 尝试使用更完整、更具体的消息
- 调整检索权重或关键词提取逻辑

### 问题：内存占用过高

**原因**：加载整个知识库到内存

**解决方案**：
- 这是正常现象（知识库较大）
- 如果内存不足，可以考虑：
  - 使用数据库存储替代 JSON 文件
  - 实现增量加载
  - 使用向量数据库（如 FAISS）进行相似度检索

## 性能优化建议

1. **首次加载较慢**：检索器首次加载时会读取整个 JSON 文件，后续使用会很快
2. **使用单例模式**：`get_c3kg_retriever()` 使用单例模式，避免重复加载
3. **考虑缓存**：可以为频繁查询的消息添加缓存机制

## 未来改进方向

1. **向量检索**：使用词向量或句向量进行语义检索，提升匹配精度
2. **数据库存储**：使用 SQLite 或向量数据库替代 JSON 文件
3. **增量更新**：支持增量更新知识库，无需重新转换整个数据集
4. **相关性评分优化**：引入更复杂的相关性评分算法

## 相关资源

- C3KG 项目主页：https://github.com/thunlp/C3KG
- ATOMIC 数据集：https://allenai.org/data/atomic

## 许可证

本项目遵循原 C3KG 项目的许可证要求。


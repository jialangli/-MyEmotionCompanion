# MyEmotionCompanion 💕

一个具备**主动关怀**功能的智能情感陪伴应用，集成 AI 对话、情感分析、定时推送和实时通信。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**安全提醒：请务必将 API Key 等敏感信息保存在 `.env`，且不要把 `.env`、数据库文件或包含凭据的配置提交到 Git。**

---

## 🛠️ 前端工程化与模块化重构

为了解决原有前端代码耦合严重、全局变量过多、可读性差、维护困难等问题，项目已完成前端工程化与模块化重构：

- **ES6 模块化**：所有功能按主题切换、人格管理、聊天逻辑、WebSocket 通信、工具函数、配置常量等分为独立 JS 模块，互不干扰，便于维护和扩展。
- **关注点分离**：DOM 操作、消息处理、WebSocket 连接、人格加载、主题切换等逻辑彻底分离，避免全局作用域污染。
- **面向对象封装**：核心功能均以类（如 `ChatManager`、`PersonaManager`、`ThemeManager`、`WebSocketManager`）实现，提升可读性和复用性。
- **工程目录结构清晰**：
  - `static/js/config/`：配置常量
  - `static/js/utils/`：通用工具函数
  - `static/js/modules/`：各功能模块
  - `static/js/main.js`：入口初始化
- **现代化开发体验**：支持热更新、易于单元测试和持续集成。

> 通过上述优化，前端代码结构更清晰，易于维护和二次开发，极大提升了项目的可扩展性和工程质量。

## 🌋 火山引擎AI API 集成

项目现已支持火山引擎(豆包)AI服务，可与DeepSeek API无缝切换：

- **双AI提供商支持**：通过环境变量 `AI_PROVIDER` 切换 `deepseek` 或 `volcengine`
- **使用OpenAI SDK**：火山引擎API兼容OpenAI SDK接口，集成简便
- **完整功能支持**：支持自定义系统提示词、情感分析、对话历史上下文保留等全部功能
- **配置方式**：在 `.env` 文件中配置：
  ```env
  AI_PROVIDER=volcengine
  VOLCENGINE_API_KEY=your_api_key
  VOLCENGINE_MODEL=deepseek-v3-2-251201
  VOLCENGINE_API_URL=https://ark.cn-beijing.volces.com/api/v3
  ```
- **测试方式**：
  ```bash
  # 简单测试（无工具）
  python test_volcengine_simple.py
  
  # 完整功能测试
  python test_volcengine.py
  ```

> 火山引擎API提供了更稳定、更快的响应速度，尤其适合需要实时推送和高并发的场景。

## ✨ 核心功能

### 🤖 智能对话
- 基于 **DeepSeek API** 的自然语言对话
- 支持自定义人格（温暖伴侣/知识百科）
- 对话历史持久化，重启后保持上下文

### 🧠 C3KG 常识增强（新功能）
- **自动常识检索**：用户发送消息后，系统会从 C3KG（ATOMIC_Chinese）中匹配相关事件/常识
- **Prompt 注入**：将检索到的常识注入到 LLM 的系统提示词中，让回复更符合常识与逻辑
- **结构化知识库**：将原始三元组整理为可检索的 JSON（事件 + 常识 + 对话流 + 关键词）

### 🎭 AI 人格切换（新功能！）
- 💕 **暖心伴侣（女友）**：温柔黏人、高共情、细心体贴，偶尔撒娇
- 🧠 **理性顾问**：沉稳逻辑清晰、客观中立，提供专业建议
- 😜 **幽默朋友**：开朗风趣、爱开玩笑，用段子化解负面情绪
- 👂 **安静倾听者**：温柔耐心、少说教，主要以倾听为主
- ⚙️ **动态切换**：前端下拉框选择，实时生效无需重启

### 💖 主动关怀系统
- ⏰ **定时推送**：早安、晚安、下班关怀三种类型
- 🎯 **个性化消息**：AI 根据时间和情境生成温暖内容
- 📱 **实时推送**：WebSocket 双向通信，消息即时送达
- ⚙️ **灵活配置**：用户可自定义推送时间和启用/禁用

### 😊 情感分析
- 集成百度 AI 情感分析 API
- 实时识别用户情绪状态
- 根据情感调整回复风格

### 🎨 现代化界面
- 响应式设计，支持日间/夜间主题
- 📱 **移动端优化**：完全适配 320px-1920px 各种屏幕尺寸
- 打字机效果展示 AI 回复
- 特殊样式标识主动推送消息
- 实时连接状态显示（绿点在线/灰点离线）

---

## 📁 项目结构

```
MyEmotionCompanion/
├── app.py                      # Flask 主应用（集成所有模块）
├── config.py                   # 环境配置
├── models.py                   # 用户偏好数据库模型
├── scheduler.py                # APScheduler 定时任务调度
├── websocket_handler.py        # WebSocket 实时推送服务
├── requirements.txt            # Python 依赖
├── TEST_GUIDE.md              # 完整测试指南
├── config/
│   └── persona_config.json    # AI 人格配置文件（支持无代码自定义）
├── utils/
│   └── persona_utils.py       # 人格加载工具模块（动态加载配置）
│   └── c3kg_converter.py      # C3KG 数据转换：生成结构化 c3kg_data.json
├── services/
│   ├── ai_service.py          # DeepSeek AI 对话服务
│   └── emotion_analyzer.py    # 百度情感分析服务
│   └── c3kg_retriever.py      # C3KG 知识检索：匹配常识并格式化注入 Prompt
├── templates/
│   ├── index.html             # 主聊天界面（含 WebSocket 客户端）
│   └── test.html              # 主动关怀功能测试页面
├── scripts/
│   ├── start_app.sh           # Linux/Mac 启动脚本
│   ├── stop_app.sh            # Linux/Mac 停止脚本
│   ├── start_app.ps1          # Windows PowerShell 启动脚本
│   └── stop_app.ps1           # Windows PowerShell 停止脚本
│   └── test_c3kg.py           # C3KG 转换/检索测试脚本
│   └── test_c3kg_integration.py  # C3KG 集成测试：检索→注入→(可选)真实LLM调用
└── databases/
    ├── chat_history.db        # 对话历史数据库
    └── companion.db           # 用户偏好数据库
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/jialangli/-MyEmotionCompanion.git
cd MyEmotionCompanion

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate          # Linux/Mac
# 或
venv\Scripts\activate              # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# DeepSeek API Key（必需）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxx

# Flask Secret Key（必需）
SECRET_KEY=your-random-secret-key-here

# 百度情感分析 API（可选）
BAIDU_API_KEY=your-baidu-api-key
BAIDU_SECRET_KEY=your-baidu-secret-key
```

### 4. 启动应用

**方式一：直接运行**
```bash
python app.py
```

**方式二：使用启动脚本（推荐）**

Linux/Mac:
```bash
bash ./scripts/start_app.sh
```

Windows PowerShell:
```powershell
./scripts/start_app.ps1
```

### 5. 访问应用

- **主页面**: http://127.0.0.1:5000
  - 💻 PC 端：完整功能体验
  - 📱 移动端：自适应布局，流畅使用体验
- **健康检查**: http://127.0.0.1:5000/health
- **测试页面**: http://127.0.0.1:5000/test

---

## 🧠 C3KG 常识增强：数据转换与测试

### 1. 原始数据文件

请确保以下文件存在于 `data/` 目录：
- `data/ATOMIC_Chinese.tsv`
- `data/head_phrase.csv`
- `data/head_shortSentence.csv`

### 2. 生成结构化知识库（首次必须执行）

```bash
python utils/c3kg_converter.py
```

运行后会生成：`data/c3kg_data.json`（体积较大，转换可能需要几分钟）。

### 3. 检索模块单测

```bash
python scripts/test_c3kg.py
```

### 4. 直接用项目做集成验证（推荐）

该脚本会展示：**用户消息 → C3KG 检索结果 → Prompt 注入预览**，并可选执行一次真实 LLM 调用（需要配置 API Key）。

```bash
python scripts/test_c3kg_integration.py
```

### 5. 运行时行为（无需额外调用）

在 `services/ai_service.py`（DeepSeek）与 `services/volcengine_service.py`（火山引擎）中已自动集成：
- 每次用户消息进入时会触发 C3KG 检索
- 若检索到常识，会自动注入到系统 Prompt 中

---

## 📊 主动关怀系统使用

### 设置用户推送偏好

```bash
curl -X POST http://127.0.0.1:5000/api/user/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "enable_morning": 1,
    "morning_time": "08:30",
    "enable_evening": 1,
    "evening_time": "22:00",
    "enable_care": 1,
    "care_time": "18:00"
  }'
```

### 查询用户推送偏好

```bash
curl "http://127.0.0.1:5000/api/user/schedule?user_id=your_user_id"
```

### 查看系统状态

```bash
# WebSocket 连接状态
curl http://127.0.0.1:5000/api/websocket/status

# 调度器任务状态
curl http://127.0.0.1:5000/api/scheduler/status
```

---

## 🧪 测试

### 快速测试

1. 打开测试页面: http://127.0.0.1:5000/test
2. 点击"连接"按钮建立 WebSocket 连接
3. 设置关怀时间（建议设置为当前时间 + 2分钟）
4. 点击"保存设置"
5. 等待到达设定时间，观察主动推送的关怀消息

### 详细测试指南

参见 [TEST_GUIDE.md](TEST_GUIDE.md) 了解完整的测试流程和 API 文档。

---

## 🔧 技术栈

- **后端框架**: Flask 3.1.2
- **AI 服务**: DeepSeek API
- **情感分析**: 百度 AI
- **数据库**: SQLite
- **任务调度**: APScheduler 3.10.4
- **实时通信**: Flask-SocketIO 5.3.6
- **前端**: HTML5 + CSS3 + Vanilla JavaScript

---

## 📝 API 文档

### 聊天接口

**POST** `/api/chat`

请求体:
```json
{
  "message": "用户消息",
  "session_id": "会话ID",
  "persona_id": "人格标识（可选，默认 warm_partner）"
}
```

响应:
```json
{
  "status": "success",
  "reply": "AI回复内容",
  "emotion": {
    "emotion": "开心",
    "polarity": 2,
    "confidence": 0.95
  }
}
```

### 人格列表接口

**GET** `/api/personas`

响应:
```json
{
  "status": "success",
  "personas": [
    {
      "id": "warm_partner",
      "name": "暖心伴侣（女友）",
      "emoji": "💕"
    },
    {
      "id": "rational_advisor",
      "name": "理性顾问",
      "emoji": "🧠"
    }
  ]
}
```

### 人格配置

无需 API 调用，直接编辑 `config/persona_config.json` 即可自定义 AI 人格：

```json
{
  "personas": {
    "your_persona_id": {
      "name": "人格名称",
      "system_prompt": "AI 系统提示词，定义性格和行为...",
      "emoji": "😊"
    }
  }
}
```

修改后前端自动加载新人格，无需重启服务。

### 用户推送偏好

**GET/POST** `/api/user/schedule`

**POST** `/api/user/schedule/disable`

详见 [TEST_GUIDE.md](TEST_GUIDE.md)

---

## 🛠️ 开发

### 目录说明

- `app.py`: Flask 主应用，路由定义
- `models.py`: 数据库模型（用户偏好）
- `scheduler.py`: 定时任务调度逻辑
- `websocket_handler.py`: WebSocket 事件处理
- `config/persona_config.json`: AI 人格配置文件
- `utils/persona_utils.py`: 人格加载工具
- `services/`: 外部服务封装
  - `ai_service.py`: AI 对话服务（支持动态 system_prompt）
  - `emotion_analyzer.py`: 情感分析服务

### 自定义 AI 人格

**方式一：配置文件法（推荐，无需重启）**

编辑 `config/persona_config.json` 添加新的人格配置：

```json
{
  "personas": {
    "your_persona_id": {
      "name": "人格名称",
      "system_prompt": "系统提示词定义 AI 的性格和行为...",
      "emoji": "😊"
    }
  }
}
```

保存后前端自动加载，无需修改代码或重启服务。

**方式二：代码修改法**

编辑 `services/ai_service.py` 中的 `get_ai_reply()` 函数，自定义默认的 `system_prompt`。

### 添加新的推送类型

### 添加新的推送类型

1. 在 `models.py` 中添加新的字段
2. 在 `scheduler.py` 中添加新的任务类型
3. 在 `websocket_handler.py` 中处理新的消息类型
4. 更新前端以显示新类型的消息

---

## 🚫 停止应用

**直接停止**:
```bash
# 找到进程ID并终止
ps aux | grep "python app.py"
kill <PID>
```

**使用停止脚本**:

Linux/Mac:
```bash
bash ./scripts/stop_app.sh
```

Windows PowerShell:
```powershell
./scripts/stop_app.ps1
```

---

## 📌 注意事项

### 安全性
- ⚠️ 不要将 `.env` 文件提交到版本控制
- ⚠️ 定期更换 API Key 和 Secret Key
- ⚠️ 生产环境使用 HTTPS 和 WSS

### 移动端使用
- ✅ 完全支持手机、平板等各种尺寸设备
- ✅ 自动适配 320px 超小屏到 1920px 超大屏
- ✅ 触摸友好的输入框和按钮
- 📝 建议在手机上添加到主屏幕（Safari "添加到主屏幕" / Chrome "安装应用"）

### 性能优化
- 建议使用 Gunicorn + Nginx 部署生产环境
- 配置日志轮转避免日志文件过大
- 定期清理过期的对话历史
- 使用 CDN 加速静态资源（Socket.IO 库）

### 代理设置
- 如果访问外部 API 失败，检查网络代理配置
- 确保代理工具（如 Clash）正常运行

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的 AI 对话能力
- [百度 AI](https://ai.baidu.com/) - 提供情感分析服务
- [Flask](https://flask.palletsprojects.com/) - 优秀的 Python Web 框架
- [APScheduler](https://apscheduler.readthedocs.io/) - 强大的 Python 任务调度库

---

## 📮 联系方式

- **作者**: jialangli
- **仓库**: https://github.com/jialangli/-MyEmotionCompanion

---

## 🔮 未来规划

- [ ] 支持多用户系统
- [ ] 添加语音对话功能
- [ ] 集成更多 AI 模型选择
- [ ] 移动端 App 开发
- [ ] 添加记忆系统（长期记忆）
- [ ] 支持图片、表情包发送
- [ ] 添加用户画像分析
- [ ] 集成天气、新闻等外部数据

---

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！** 😊

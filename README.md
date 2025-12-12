# MyEmotionCompanion 💕

一个具备**主动关怀**功能的智能情感陪伴应用，集成 AI 对话、情感分析、定时推送和实时通信。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**安全提醒：请务必将 API Key 等敏感信息保存在 `.env`，且不要把 `.env`、数据库文件或包含凭据的配置提交到 Git。**

---

## ✨ 核心功能

### 🤖 智能对话
- 基于 **DeepSeek API** 的自然语言对话
- 支持自定义人格（温暖伴侣/知识百科）
- 对话历史持久化，重启后保持上下文

### 💖 主动关怀系统（新功能！）
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
- 打字机效果展示 AI 回复
- 特殊样式标识主动推送消息
- 实时连接状态显示

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
├── services/
│   ├── ai_service.py          # DeepSeek AI 对话服务
│   └── emotion_analyzer.py    # 百度情感分析服务
├── templates/
│   ├── index.html             # 主聊天界面（含 WebSocket 客户端）
│   └── test.html              # 主动关怀功能测试页面
├── scripts/
│   ├── start_app.sh           # Linux/Mac 启动脚本
│   ├── stop_app.sh            # Linux/Mac 停止脚本
│   ├── start_app.ps1          # Windows PowerShell 启动脚本
│   └── stop_app.ps1           # Windows PowerShell 停止脚本
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
- **健康检查**: http://127.0.0.1:5000/health
- **测试页面**: http://127.0.0.1:5000/test

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
  "session_id": "会话ID"
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
- `services/`: 外部服务封装
  - `ai_service.py`: AI 对话服务
  - `emotion_analyzer.py`: 情感分析服务

### 自定义 AI 人格

编辑 `services/ai_service.py` 中的 `system_prompt` 变量来调整 AI 的性格和回复风格。

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

### 性能优化
- 建议使用 Gunicorn + Nginx 部署生产环境
- 配置日志轮转避免日志文件过大
- 定期清理过期的对话历史

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

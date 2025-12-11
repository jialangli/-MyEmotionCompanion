# MyEmotionCompanion

一个本地运行的情感陪伴 Flask 应用，集成了 AI 服务（通过 DeepSeek API）。

**重要：不要将 `.env` 或包含密钥的配置文件提交到远程仓库。**

## 快速开始

先在项目根目录创建并激活虚拟环境，然后安装依赖：

```bash

# MyEmotionCompanion

MyEmotionCompanion 是一个本地运行的情感陪伴 Flask 应用，集成了第三方 LLM 服务（DeepSeek API）用于生成带有人格化风格的对话回复，并使用 SQLite 保存对话历史以实现重启持久化。适合作为个人情感陪伴、原型验证或二次开发的起点。

**安全提醒：请务必将 API Key 等敏感信息保存在 `.env`，且不要把 `.env`、数据库文件或包含凭据的配置提交到 Git。仓库已包含 `.gitignore`。**

## 功能特性

- 基于 Flask 提供 HTTP API 与网页前端（`templates/index.html`）。
- 将会话历史持久化到 SQLite 数据库（`chat_history.db`），重启后能恢复上下文。
- 可通过 `services/ai_service.py` 自定义 system prompt 来调节 AI 的人格（例如“暖心伴侣/女友”）。
- 前端使用简单的 JavaScript（Fetch API）与后端交互，包含重试与错误提示机制。
- 包含基础的单元测试模板及 GitHub Actions CI 工作流。

## 目录结构（重要文件）

- `app.py` — Flask 主程序，包含路由与数据库助手函数。
- `config.py` — 环境配置（从 `.env` 加载 API Key 等）。
- `services/ai_service.py` — 封装与 DeepSeek API 的交互与 system prompt。
- `templates/index.html` — 聊天前端界面。
- `chat_history.db` — SQLite 数据库（不应纳入版本控制）。
- `.github/workflows/ci.yml` — 简单的 CI 工作流（运行 pytest）。

## 安装与配置

先在项目根创建并激活虚拟环境，然后安装依赖：

```bash
cd /d/Desktop/AIFriend/MyEmotionCompanion
python -m venv venv
# Windows (Git Bash / MINGW)：
source venv/Scripts/activate
pip install -r requirements.txt
```

创建 `.env` 并写入你的 API Key（示例）：

```text
DEEPSEEK_API_KEY=sk-xxxxxx
SECRET_KEY=replace-with-random-secret
```

（注意：如果你使用不同的变量名或配置文件，请相应修改 `config.py`。）

## 本地运行

激活虚拟环境后运行：

```bash
source venv/Scripts/activate
python app.py
```

然后在浏览器打开 `http://127.0.0.1:5000`。

## API 接口说明

- `GET /health`
	- 描述：健康检查接口
	- 返回：`{ "status": "healthy", "ai_integrated": true }`

- `POST /api/chat`
	- 描述：发送用户消息并获取 AI 回复
	- 请求体（JSON）：
		```json
		{
			"session_id": "user_12345",
			"message": "你好"
		}
		```
	- 返回（JSON）：
		```json
		{
			"reply": "AI 的回复文本",
			"session_id": "user_12345"
		}
		```

- `POST /api/clear_history`
	- 描述：清除某个会话的对话历史
	- 请求体（JSON）： `{ "session_id": "user_12345" }`
	- 返回：成功/失败状态

（注：具体字段以 `app.py` 中的实现为准，必要时可扩展验证与错误码。）

## 部署指南（建议）

开发环境使用 Flask 自带服务器即可，但生产请使用 WSGI 服务器（Gunicorn/uvicorn）并在反向代理（Nginx）后面运行：

示例：使用 `gunicorn`（Linux）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

如果部署在 Windows Server 或 IIS，请使用合适的 WSGI 容器或考虑容器化（Docker）。

部署时注意：
- 使用环境变量或密钥管理服务保存 API Key（例如：GitHub Secrets、Azure Key Vault、AWS Secrets Manager）。
- 不要把 `.env` 上传到远程仓库；若误提交，请参考 `git filter-repo` 或 `bfg-repo-cleaner` 清理历史。

## CI / 测试

仓库包含一个基础 GitHub Actions workflow（`.github/workflows/ci.yml`），在 `main` 分支的 push 或 PR 时运行 `pytest`（如果检测到测试文件）。本地运行测试：

```bash
source venv/Scripts/activate
pytest -q
```

## 常见问题与排查

- 页面提示 `Failed to fetch`：确认 Flask 服务是否运行（`http://127.0.0.1:5000/health`），并检查浏览器是否使用了代理或 CORS 设置。
- `.env` 未加载：确认 `python-dotenv` 已安装并且 `.env` 文件位于项目根；`config.py` 使用 `load_dotenv(path)` 明确加载。
- 端口被占用或进程异常退出：检查端口（`netstat -ano | findstr :5000`）并查看 `app.py` 的启动日志。

## 贡献与许可

欢迎提出 Issue 或 PR 来改进功能、修复 bug 或补充文档。你可以在仓库中直接创建分支并发起 PR。

如果你希望我为仓库添加更多示例（例如 Dockerfile、更多测试或自动部署工作流），告诉我你的目标平台，我可以继续实现。

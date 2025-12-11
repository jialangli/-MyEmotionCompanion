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

## 安全与密钥管理（不要把 Key 写进代码）

强烈建议不要把 `API Key`、`Secret Key` 等敏感信息直接写入源码或提交到远程仓库。推荐做法：

- 在项目根使用 `.env` 文件保存敏感变量，并把 `.env` 写入 `.gitignore`（仓库已包含此项）。
- 在 `config.py` 中使用 `python-dotenv` 或直接读取环境变量，示例：

```python
from dotenv import load_dotenv
import os

# 在模块加载时显式加载项目根目录下的 .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
BAIDU_API_KEY = os.getenv('BAIDU_API_KEY')
BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY')
```

- 如果不慎将密钥提交到 Git 仓库，请尽快：
	1. 从远程历史中移除敏感文件（示例命令，会修改历史，谨慎操作）：

```bash
# 从最新提交中删除 .env 并提交（保留本地文件）
git rm --cached .env
git commit -m "remove .env from repo"
git push origin main

# 若密钥已出现在历史提交中，使用 recommended 工具 清理历史（示例）
# 推荐使用: https://github.com/newren/git-filter-repo 或 BFG
# 例如（使用 git-filter-repo）：
# git filter-repo --path .env --invert-paths
```

	2. 立即在相应服务/平台（DeepSeek、Baidu 等）上撤销并重新生成新的密钥（密钥轮换）。不要继续使用已泄露的密钥。

- 为方便协作，推荐提交一个 `.env.example`（不包含真实密钥），示例：

```text
DEEPSEEK_API_KEY=sk-REPLACE_WITH_YOURS
BAIDU_API_KEY=REPLACE_WITH_YOURS
BAIDU_SECRET_KEY=REPLACE_WITH_YOURS
SECRET_KEY=replace-with-random-secret
```

如果需要，我可以帮助你生成用于从 Git 历史中删除已提交密钥的命令示例（按照你的偏好使用 `git-filter-repo` 或 `bfg-repo-cleaner`），以及一份密钥轮换与通知的操作清单。

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

## 运行与调试（情感分析专用提示）

如果你发现前端或 API 返回中缺少 `emotion` 字段，按下面步骤排查：

- 确认服务实例：可能存在旧的多个 Flask 进程并行运行，导致请求由未加载最新代码的旧实例处理。查看并结束旧进程：

```bash
# 列出占用 5000 端口的进程（Windows）
netstat -ano | findstr :5000
# 使用任务管理器或 taskkill 结束指定 PID：
taskkill /PID <PID> /F
```

- 检查 `flask_output.log`（或你启动时指定的日志文件）以查看 `情感分析` 或 `Debug` 打印是否存在：

```bash
tail -n 200 flask_output.log
```

- 直接在 Python REPL 中测试情感分析器是否可用（在虚拟环境下运行）：

```bash
source venv/Scripts/activate
python - <<'PY'
from services.emotion_analyzer import BaiduEmotionAnalyzer
import config
an = BaiduEmotionAnalyzer(config.BAIDU_API_KEY, config.BAIDU_SECRET_KEY)
print(an.analyze_emotion('我今天很难过'))
PY
```

- 如果情感分析器返回 `None` 或回退到中性，这是网络/密钥或百度 API 可用性导致的正常回退行为；应用会仍然返回 AI 回复，但 `emotion` 可能为空或为回退值。

- 为避免未来出现多进程冲突，推荐使用进程管理器或 PID 文件（见“生产建议”小节）。

## 生产建议（进程管理与自动重启）

开发时直接运行 `python app.py` 足够，但在线上建议使用 WSGI 进程管理：

- 使用 `gunicorn`（Linux）：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

- Windows 平台可用 `waitress-serve` 或将应用容器化（Docker）。示例 `waitress`：

```bash
pip install waitress
waitress-serve --listen=0.0.0.0:5000 app:app
```

- 使用 `systemd` 或 `supervisord` 管理 Gunicorn，可确保单实例、自动重启以及日志收集。

（如需，我可以为你生成 `systemd` unit 文件或 `supervisord` 配置样例。）


### Git 网络问题与解决（常见命令）

下面列出一些在推送/拉取时常见的网络问题与调试/修复命令，复制到终端执行即可。请根据你所在网络环境（是否使用代理、防火墙等）选择适用的方案。

- 查看与远程连接的详细调试信息：

```bash
# 显示 Git 与 curl 的调试输出（有助于诊断 TLS/代理/认证问题）
GIT_TRACE=1 GIT_CURL_VERBOSE=1 git push origin main
```

- 使用代理时配置 Git：

```bash
# 设置 HTTP/HTTPS 代理（示例：本地代理 127.0.0.1:7890）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

- 临时通过环境变量设置代理（只在当前 shell 有效）：

```bash
export HTTP_PROXY="http://user:pass@127.0.0.1:7890"
export HTTPS_PROXY="http://user:pass@127.0.0.1:7890"
```

- 若系统或浏览器已设置代理并影响 Git（Windows 上常见），可尝试禁用这些代理或在 Git 中取消代理设置：

```bash
git config --system --unset http.proxy || true
git config --global --unset http.proxy || true
```

- 切换到 SSH 推送（避免 HTTPS/代理相关问题）：

```bash
# 1) 生成 SSH 密钥（若尚未有）
ssh-keygen -t ed25519 -C "your-email@example.com"
# 2) 启动 ssh-agent 并添加密钥
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
# 3) 将 ~/.ssh/id_ed25519.pub 内容添加到 GitHub -> Settings -> SSH and GPG keys
# 4) 切换远程为 SSH URL 并推送
git remote set-url origin git@github.com:你的用户名/仓库名.git
git push -u origin main
```

- 如果遇到凭证/认证提示（HTTP Basic / Personal Access Token）：

```bash
# 使用 GitHub 的 Personal Access Token (PAT) 作为密码，或使用 Git Credential Manager
GIT_ASKPASS=echo git push https://<username>:<token>@github.com/<username>/<repo>.git
```

- 测试 TLS/证书或与远程主机的连通性：

```bash
# 使用 curl 简单测试
curl -v https://github.com

# 使用 openssl 检查证书链
openssl s_client -connect github.com:443 -servername github.com
```

- （仅用于排查）临时跳过证书校验——强烈不推荐长期使用，仅用于排查内网证书问题：

```bash
# 非推荐：请谨慎使用
GIT_SSL_NO_VERIFY=true git push origin main
```

- 如果遇到 `.netrc` 或凭证缓存问题：

```bash
# 查看当前 Git 配置中的凭证管理器设置
git config --list | grep credential

# 清除已缓存的凭证（Windows 下可能使用 Credential Manager）
printf "protocol=https\nhost=github.com\n" | git credential-reject
```

如果你把代理、公司网络或 VPN 作为常见因素，请告知我你的网络环境（是否使用公司代理、代理地址、是否能够连接外网等），我可以给出更准确的步骤。若你希望我把 SSH 配置的具体步骤（含公钥上传辅助命令）也写进 README，我可以一并补充。

## 贡献与许可

欢迎提出 Issue 或 PR 来改进功能、修复 bug 或补充文档。你可以在仓库中直接创建分支并发起 PR。

如果你希望我为仓库添加更多示例（例如 Dockerfile、更多测试或自动部署工作流），告诉我你的目标平台，我可以继续实现。

# MyEmotionCompanion

一个本地运行的情感陪伴 Flask 应用，集成了 AI 服务（通过 DeepSeek API）。

**重要：不要将 `.env` 或包含密钥的配置文件提交到远程仓库。**

## 快速开始

先在项目根目录创建并激活虚拟环境，然后安装依赖：

```bash
cd /d/Desktop/AIFriend/MyEmotionCompanion
python -m venv venv
# Windows (Git Bash / MINGW)：
source venv/Scripts/activate
pip install -r requirements.txt
```

创建 `.env` 文件并写入你的 API Key：

```
DEEPSEEK_API_KEY=sk-xxxxxx
```

启动服务器：

```bash
source venv/Scripts/activate
python app.py
```

打开浏览器访问： `http://127.0.0.1:5000`

## 常见命令

- 查看健康检查接口：
```
curl http://127.0.0.1:5000/health
```
- 清除会话历史（示例 API）：
```
curl -X POST -H "Content-Type: application/json" -d '{"session_id": "your_session_id"}' http://127.0.0.1:5000/api/clear_history
```

## 开发与 CI
仓库包含一个简单的 GitHub Actions 工作流（`.github/workflows/ci.yml`），用于在推送或 PR 时运行测试（`pytest`）。

## 安全与注意事项
- 请不要将 `.env`、`config.py` 或其他凭据文件提交到 Git。仓库中已有 `.gitignore` 忽略这些文件。
- 生产环境请使用更安全的部署方式（例如 Gunicorn + Nginx、并使用容器化或云托管）。

如果你想让我帮你添加自动部署或更完整的 CI（例如：自动构建 Docker 镜像并推送到容器注册表），告诉我你希望部署到的目标平台（Heroku / AWS / Azure / 自托管服务器）。

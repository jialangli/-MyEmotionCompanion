#!/bin/bash
# 推送恢复脚本 - 网络连接恢复后运行此脚本

cd "$(dirname "$0")" || exit 1

echo "=========================================="
echo "MyEmotionCompanion Git Push Recovery"
echo "=========================================="

# 确保远程 URL 是 HTTPS
git remote set-url origin https://github.com/jialangli/-MyEmotionCompanion.git

echo "📍 当前分支: $(git rev-parse --abbrev-ref HEAD)"
echo "📦 未推送提交:"
git log --oneline origin/main..HEAD

echo ""
echo "🔄 开始推送... (最多尝试 5 次)"
echo ""

max_retries=5
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    retry_count=$((retry_count + 1))
    echo "尝试 $retry_count/$max_retries..."
    
    if git push origin main; then
        echo ""
        echo "✅ 推送成功！"
        echo ""
        git log --oneline -3
        echo ""
        echo "📊 最新状态:"
        git status
        exit 0
    else
        if [ $retry_count -lt $max_retries ]; then
            wait_time=$((retry_count * 5))
            echo "❌ 推送失败，等待 ${wait_time} 秒后重试..."
            sleep "$wait_time"
        fi
    fi
done

echo ""
echo "❌ 推送失败（$max_retries 次尝试后）"
echo "💡 建议："
echo "  1. 检查网络连接: ping github.com"
echo "  2. 检查 Git 配置: git config --list | grep remote"
echo "  3. 尝试 SSH: git remote set-url origin git@github.com:jialangli/-MyEmotionCompanion.git"
echo "  4. 查看日志: GIT_TRACE=1 git push origin main"
echo ""
exit 1

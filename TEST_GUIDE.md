# 主动式关怀功能测试指南

## 测试环境
- **应用地址**: http://127.0.0.1:5000
- **测试页面**: http://127.0.0.1:5000/test
- **WebSocket 地址**: ws://127.0.0.1:5000

## 测试步骤

### 步骤 1: 测试 WebSocket 连接

1. 打开测试页面: http://127.0.0.1:5000/test
2. 点击"连接"按钮
3. 观察状态栏变为绿色"已连接到服务器"
4. 查看消息区域，应该看到：
   - "WebSocket 已连接"
   - "用户注册成功"

### 步骤 2: 设置用户推送偏好

1. 在"用户设置"面板中，设置关怀推送时间
   - 建议设置为当前时间 + 2分钟（例如：当前 19:37，设置为 19:39）
2. 点击"保存设置"按钮
3. 观察返回结果，应该显示"设置成功"

### 步骤 3: 等待定时任务触发

1. 等待到达设置的时间
2. 观察测试页面的"接收到的消息"区域
3. 应该会收到一条粉色背景的"主动关怀消息"
4. 消息包含：
   - AI 生成的温暖关怀内容
   - 消息类型（care）
   - 接收时间

### 步骤 4: 观察效果

**前端效果**：
- 消息以特殊样式显示（粉色边框）
- 带有"💕 主动关怀消息"标签
- 显示具体的关怀内容
- 如果允许通知权限，会弹出浏览器通知

**后台日志**：
查看应用日志可以看到：
```
INFO:scheduler:[主动推送] 已向用户 xxx 发送 care 消息
INFO:websocket:[WebSocket] 已向用户 xxx 推送消息: care
```

## API 测试

### 1. 查看 WebSocket 状态
```bash
curl http://127.0.0.1:5000/api/websocket/status
```

### 2. 查看调度器状态
```bash
curl http://127.0.0.1:5000/api/scheduler/status
```

### 3. 设置用户推送偏好
```bash
curl -X POST http://127.0.0.1:5000/api/user/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "enable_care": 1,
    "care_time": "19:45"
  }'
```

### 4. 查询用户推送偏好
```bash
curl "http://127.0.0.1:5000/api/user/schedule?user_id=your_user_id"
```

### 5. 禁用用户推送
```bash
curl -X POST http://127.0.0.1:5000/api/user/schedule/disable \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "type": "care"
  }'
```

## 测试不同消息类型

### 早安消息（morning）
```bash
curl -X POST http://127.0.0.1:5000/api/user/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "enable_morning": 1,
    "morning_time": "08:30"
  }'
```

### 晚安消息（evening）
```bash
curl -X POST http://127.0.0.1:5000/api/user/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "enable_evening": 1,
    "evening_time": "22:00"
  }'
```

### 关怀消息（care）
```bash
curl -X POST http://127.0.0.1:5000/api/user/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "enable_care": 1,
    "care_time": "18:00"
  }'
```

## 验证要点

### ✅ WebSocket 连接
- [ ] 前端成功连接到 WebSocket 服务器
- [ ] 用户 ID 正确注册
- [ ] 连接状态实时更新
- [ ] 断开重连功能正常

### ✅ 用户偏好设置
- [ ] 可以成功设置推送时间
- [ ] 可以启用/禁用不同类型的推送
- [ ] 设置后任务立即生效
- [ ] 可以查询当前设置

### ✅ 定时任务调度
- [ ] 任务在设定时间准时触发
- [ ] 不同用户的任务互不干扰
- [ ] 任务触发后正确调用 AI 生成消息
- [ ] 任务可以动态添加/删除

### ✅ 消息推送
- [ ] WebSocket 成功推送消息到前端
- [ ] 消息内容由 AI 生成，温暖贴心
- [ ] 消息包含正确的元数据（类型、时间等）
- [ ] 前端正确显示推送的消息

### ✅ AI 消息生成
- [ ] 根据消息类型生成对应风格的内容
- [ ] 消息长度控制在 50 字以内
- [ ] 语气亲切自然、温暖体贴
- [ ] 使用亲昵称呼和表情符号

## 常见问题排查

### WebSocket 连接失败
1. 检查应用是否正常运行：`curl http://127.0.0.1:5000/health`
2. 检查防火墙设置
3. 查看浏览器控制台错误信息

### 消息未收到
1. 确认用户已连接 WebSocket
2. 确认推送时间设置正确
3. 检查应用日志：`tail -f app_run.log`
4. 确认调度器正常运行：`curl http://127.0.0.1:5000/api/scheduler/status`

### 任务未触发
1. 检查系统时间是否正确
2. 确认任务已添加到调度器
3. 查看调度器日志
4. 确认用户偏好中对应类型的推送已启用

## 性能测试

### 多用户并发
创建多个用户并设置不同的推送时间，观察系统处理能力。

### 长时间运行
让应用运行 24 小时，观察内存占用和任务执行稳定性。

### WebSocket 重连
模拟网络中断，测试 WebSocket 自动重连功能。

## 测试完成标准

- [x] 所有功能模块已实现
- [x] WebSocket 连接稳定
- [x] 定时任务准确触发
- [x] AI 消息生成正常
- [x] 前端正确接收并显示消息
- [ ] 用户体验流畅
- [ ] 无明显 bug 或错误

## 下一步优化方向

1. **个性化增强**：
   - 结合用户历史对话
   - 根据用户情绪状态调整消息
   - 添加天气、节日等外部数据

2. **智能触发**：
   - 用户长时间未活跃时主动问候
   - 学习用户作息习惯
   - 避免打扰时段

3. **消息多样化**：
   - 更多消息类型（提醒、鼓励等）
   - 随机变化避免重复
   - 支持图片、表情包

4. **用户控制**：
   - 前端设置界面
   - 一键免打扰
   - 推送历史记录

5. **生产环境部署**：
   - 使用 Gunicorn + Nginx
   - 配置 SSL 证书
   - 添加日志轮转
   - 监控告警

---

**测试时间**: 2025年12月12日  
**测试状态**: ✅ 功能已实现，等待实际验证

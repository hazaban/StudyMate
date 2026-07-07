---
name: ai-test
description: AI 功能端到端测试。当用户说「测试AI功能/检查AI/AI测试/验证AI接口」时触发。
---

# AI 功能端到端测试规范

## 测试环境
- 前端: https://studymate-5w0.pages.dev
- 后端: https://server-ten-eosin-90.vercel.app
- 测试账号: test@studymate.com / 123456
- 工具: Playwright MCP

## 测试流程

### 0. 登录
1. 导航到 `https://studymate-5w0.pages.dev/#/pages/auth/login`
2. 填写邮箱 `test@studymate.com`，密码 `123456`
3. 点击登录，等待跳转首页

### 1. 聊天意图 (chat)
- 导航到 `https://studymate-5w0.pages.dev/#/pages/plan/ai-plan`
- 输入「你好，你能做什么？」
- ✅ 预期: AI 友好回复介绍功能，无 data 字段，tool=chat

### 2. 任务解析 + 自动写入DB (task)
- 输入「明天上午9点复习数据结构二叉树2小时」
- ✅ 预期:
  - duration=120（不是2！）
  - 日期=明天
  - 显示「已自动添加到日程」
  - 无「确认添加任务」按钮
- 🔍 验证: 切到任务看板→周视图→找到明天的列→应有该任务卡片

### 3. 引导式规划流程 (plan)
- 输入「帮我做学习规划」
- ✅ 预期:
  - AI 不应直接出计划，而是开始阶段1提问
  - 进度条显示 4 步（基本信息/科目设置/章节确认/汇总生成）
  - 回答后 AI 应过渡到阶段2
  - 输入「跳过」→ AI 应跳过当前阶段进入下一阶段
  - 阶段4 应汇总信息并生成完整计划
- ⚠️ 已知问题: plan JSON 过大可能被 max_tokens=2048 截断

### 4. 章节分析 (syllabus)
- 输入「分析教材目录：数据结构要学链表、栈、队列、二叉树、图、排序、查找」
- ✅ 预期:
  - 识别章节列表，含 daily_duration 和 estimated_days
  - 显示「确认写入计划」按钮
- 🔍 验证: 点击确认→切到任务看板→应有按章节展开的任务

### 5. 每日复盘 (review)
- 输入「给我复盘一下今天学了什么」
- ✅ 预期: AI 识别 review 意图，询问具体学习内容

### 6. 对话持久化
- 已有对话的情况下，导航到首页再回到 AI 规划页
- ✅ 预期: 之前的对话消息完整保留

### 7. 历史会话侧边栏
- 点击 ☰ 打开侧边栏
- ✅ 预期: 显示历史会话列表（需先有保存的会话）

### 8. TaskFormModal AI 添加
- 任务看板→添加任务→🤖 AI添加
- 输入「今天晚上7点做操作系统作业1小时」
- 点击「开始解析」
- ✅ 预期: duration=60，科目=操作系统，时间=19:00

## 常见问题排查

| 现象 | 原因 | 修复 |
|------|------|------|
| duration 浮点数 422 | GLM 返回 `1.5` | 前端 `sanitizeTask()` Math.round |
| type 中文 422 | GLM 返回「复习」 | 前端 typeMap 映射 |
| plan JSON 截断 | max_tokens=2048 不够 | 增大 Worker plan 路由 token 上限 |
| 对话丢失 | onUnmounted 未保存 | `saveCurrentConversation()` + LAST_CONV_KEY |
| 页面白屏 | computed 未导入 | `import { computed } from 'vue'` |

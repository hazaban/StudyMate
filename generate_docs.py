#!/usr/bin/env python3
"""Generate StudyMate functional specification and architecture document as PDF."""

from weasyprint import HTML
import os

html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>StudyMate 学习星球 - 功能说明书与架构设计</title>
<style>
  @page {
    size: A4;
    margin: 2cm 2.5cm;
    @top-center {
      content: "StudyMate 学习星球 - 功能说明书与架构设计";
      font-size: 10pt;
      color: #666;
    }
    @bottom-right {
      content: counter(page) " / " counter(pages);
      font-size: 10pt;
      color: #666;
    }
  }
  body {
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
  }
  h1 {
    font-size: 22pt;
    color: #2f7d4f;
    border-bottom: 3px solid #2f7d4f;
    padding-bottom: 10px;
    margin-top: 0;
    page-break-before: always;
  }
  h1:first-of-type {
    page-break-before: avoid;
  }
  h2 {
    font-size: 16pt;
    color: #2f7d4f;
    border-left: 5px solid #2f7d4f;
    padding-left: 12px;
    margin-top: 30px;
  }
  h3 {
    font-size: 13pt;
    color: #1a1a2e;
    margin-top: 20px;
  }
  h4 {
    font-size: 11pt;
    color: #555;
    margin-top: 15px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 10pt;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 8px 10px;
    text-align: left;
  }
  th {
    background: #f5f7f5;
    color: #2f7d4f;
    font-weight: 600;
  }
  tr:nth-child(even) {
    background: #fafbf9;
  }
  .cover {
    text-align: center;
    padding: 80px 40px;
    page-break-after: always;
  }
  .cover h1 {
    font-size: 32pt;
    border: none;
    padding: 0;
    margin: 0 0 20px 0;
  }
  .cover .subtitle {
    font-size: 14pt;
    color: #666;
    margin-bottom: 60px;
  }
  .cover .meta {
    font-size: 11pt;
    color: #888;
    margin-top: 100px;
  }
  .cover .logo {
    font-size: 60pt;
    margin-bottom: 30px;
  }
  .toc {
    page-break-after: always;
  }
  .toc ul {
    list-style: none;
    padding-left: 0;
  }
  .toc li {
    padding: 6px 0;
    border-bottom: 1px dashed #ddd;
  }
  .toc a {
    color: #333;
    text-decoration: none;
  }
  .toc .level1 {
    font-weight: 600;
    font-size: 12pt;
    padding-left: 0;
  }
  .toc .level2 {
    padding-left: 20px;
    font-size: 11pt;
  }
  .toc .level3 {
    padding-left: 40px;
    font-size: 10pt;
    color: #666;
  }
  .highlight-box {
    background: #f0f7f2;
    border-left: 4px solid #2f7d4f;
    padding: 12px 16px;
    margin: 15px 0;
    border-radius: 0 8px 8px 0;
  }
  .info-box {
    background: #e8f4fd;
    border-left: 4px solid #2196f3;
    padding: 12px 16px;
    margin: 15px 0;
    border-radius: 0 8px 8px 0;
  }
  .warning-box {
    background: #fff8e1;
    border-left: 4px solid #ff9800;
    padding: 12px 16px;
    margin: 15px 0;
    border-radius: 0 8px 8px 0;
  }
  pre {
    background: #f5f5f5;
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.4;
  }
  code {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10pt;
    font-family: Consolas, Monaco, monospace;
  }
  ul, ol {
    padding-left: 22px;
  }
  li {
    margin: 4px 0;
  }
  .tech-badge {
    display: inline-block;
    background: #2f7d4f;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 9pt;
    margin-right: 6px;
  }
  .architecture-diagram {
    background: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin: 15px 0;
    font-family: Consolas, Monaco, monospace;
    font-size: 9pt;
    line-height: 1.5;
    white-space: pre;
  }
  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

<!-- 封面 -->
<div class="cover">
  <div class="logo">🌱</div>
  <h1>StudyMate 学习星球</h1>
  <div class="subtitle">AI 抗遗忘备考工具 — 功能说明书与架构设计</div>
  <div class="meta">
    <p>版本: 1.0.3</p>
    <p>日期: 2026年7月</p>
    <p>技术栈: Vue 3 + UniApp + FastAPI + PostgreSQL</p>
  </div>
</div>

<!-- 目录 -->
<div class="toc">
  <h1>目 录</h1>
  <ul>
    <li class="level1"><a href="#overview">一、产品概述</a></li>
    <li class="level2"><a href="#product-intro">1.1 产品简介</a></li>
    <li class="level2"><a href="#target-users">1.2 目标用户</a></li>
    <li class="level2"><a href="#core-values">1.3 核心价值</a></li>
    <li class="level2"><a href="#tech-stack">1.4 技术栈概览</a></li>

    <li class="level1"><a href="#functional-spec">二、功能说明书</a></li>
    <li class="level2"><a href="#home-page">2.1 首页</a></li>
    <li class="level2"><a href="#task-board">2.2 任务看板</a></li>
    <li class="level2"><a href="#pomodoro">2.3 番茄钟</a></li>
    <li class="level2"><a href="#flash-cards">2.4 知识卡片</a></li>
    <li class="level2"><a href="#mistake-book">2.5 错题本</a></li>
    <li class="level2"><a href="#review-mode">2.6 复习模式</a></li>
    <li class="level2"><a href="#farm">2.7 学习农场</a></li>
    <li class="level2"><a href="#statistics">2.8 学习统计</a></li>
    <li class="level2"><a href="#plan-management">2.9 计划管理</a></li>
    <li class="level2"><a href="#ai-planning">2.10 AI 智能规划</a></li>
    <li class="level2"><a href="#profile">2.11 个人中心</a></li>
    <li class="level2"><a href="#memory-algorithm">2.12 艾宾浩斯记忆算法</a></li>

    <li class="level1"><a href="#architecture">三、系统架构设计</a></li>
    <li class="level2"><a href="#arch-overview">3.1 整体架构</a></li>
    <li class="level2"><a href="#frontend-arch">3.2 前端架构</a></li>
    <li class="level2"><a href="#backend-arch">3.3 后端架构</a></li>
    <li class="level2"><a href="#database-design">3.4 数据库设计</a></li>
    <li class="level2"><a href="#api-design">3.5 API 接口设计</a></li>
    <li class="level2"><a href="#deployment">3.6 部署架构</a></li>

    <li class="level1"><a href="#appendix">四、附录</a></li>
    <li class="level2"><a href="#env-config">4.1 环境变量配置</a></li>
    <li class="level2"><a href="#quick-start">4.2 快速开始</a></li>
    <li class="level2"><a href="#test-account">4.3 测试账号</a></li>
  </ul>
</div>

<!-- 第一部分：产品概述 -->
<h1 id="overview">一、产品概述</h1>

<h2 id="product-intro">1.1 产品简介</h2>
<p><strong>StudyMate 学习星球</strong> 是一款面向考研/考公/考证备考人群的 <strong>AI 抗遗忘学习工具</strong>。结合智谱 GLM AI 规划、科学间隔记忆复习调度、番茄钟专注计时、游戏化学习农场四大核心能力，帮助备考人群高效学习，让知识真正进脑子。</p>

<div class="highlight-box">
  <strong>核心 slogan：</strong>让知识进脑子，而不是走过场。
</div>

<h3>四大核心能力</h3>
<ul>
  <li>📋 <strong>AI 智能规划</strong>：GLM-4.5-Air 生成学习计划、拆解每日任务、生成复习卡片</li>
  <li>🖼️ <strong>AI 图片识别</strong>：GLM-4.1V-Thinking-FlashX 识别教材目录，自动提取章节</li>
  <li>🍅 <strong>番茄钟计时</strong>：自定义专注/休息时长，自动记录实际学习时长到数据库</li>
  <li>🧠 <strong>知识卡片 + 错题本</strong>：按记忆曲线自动安排复习时间，文字+图片混合卡片</li>
  <li>🌱 <strong>游戏化学习农场</strong>：完成任务/番茄自动种植收割，赚金币升级</li>
  <li>📊 <strong>学习统计看板</strong>：总时长、番茄数、科目分布、趋势图表</li>
</ul>

<h2 id="target-users">1.2 目标用户</h2>
<table>
  <tr><th>用户群体</th><th>典型场景</th><th>核心需求</th></tr>
  <tr>
    <td>考研学生</td>
    <td>多科目长期备考，需要系统规划和持续复习</td>
    <td>计划制定、进度追踪、抗遗忘复习</td>
  </tr>
  <tr>
    <td>考公人群</td>
    <td>行测+申论多模块学习</td>
    <td>时间管理、错题整理、刷题效率</td>
  </tr>
  <tr>
    <td>考证人士</td>
    <td>职业资格证书短期冲刺</td>
    <td>高效记忆、重点突破、模拟测试</td>
  </tr>
  <tr>
    <td>学生群体</td>
    <td>日常课程学习、期中期末考试</td>
    <td>笔记整理、知识巩固、学习激励</td>
  </tr>
</table>

<h2 id="core-values">1.3 核心价值</h2>
<ol>
  <li><strong>科学记忆</strong>：基于艾宾浩斯遗忘曲线，智能安排复习时间，大幅提升记忆效率</li>
  <li><strong>AI 赋能</strong>：从计划生成到任务拆解，再到卡片制作，AI 全程辅助减少重复劳动</li>
  <li><strong>多端同步</strong>：H5 网页 + 小程序 + App 一套代码多端运行，随时随地学习</li>
  <li><strong>游戏激励</strong>：学习农场将枯燥的学习变成有趣的种植游戏，提升学习动力</li>
  <li><strong>数据驱动</strong>：详细的学习统计和分析，帮助用户了解自己的学习模式</li>
</ol>

<h2 id="tech-stack">1.4 技术栈概览</h2>
<p>
  <span class="tech-badge">Vue 3.4</span>
  <span class="tech-badge">UniApp 3.0</span>
  <span class="tech-badge">Pinia</span>
  <span class="tech-badge">FastAPI</span>
  <span class="tech-badge">PostgreSQL 16</span>
  <span class="tech-badge">SQLAlchemy 2.0</span>
  <span class="tech-badge">智谱 GLM</span>
  <span class="tech-badge">Vite 5</span>
</p>

<table>
  <tr><th>层级</th><th>技术选型</th><th>说明</th></tr>
  <tr><td>前端框架</td><td>Vue 3 + UniApp 3.0 + Composition API</td><td>跨端开发，支持 H5/微信小程序/原生 App</td></tr>
  <tr><td>状态管理</td><td>Pinia</td><td>Vue 官方推荐，轻量易上手</td></tr>
  <tr><td>样式方案</td><td>SCSS + CSS 变量</td><td>组件化样式开发</td></tr>
  <tr><td>后端框架</td><td>FastAPI + SQLAlchemy 2.0</td><td>Python Serverless 架构</td></tr>
  <tr><td>数据库</td><td>PostgreSQL 16（Supabase）</td><td>云端托管，免费 500MB</td></tr>
  <tr><td>AI 能力</td><td>智谱 GLM-4.5-Air / GLM-4.1V</td><td>文本规划 + 图片识别</td></tr>
  <tr><td>图片存储</td><td>腾讯云 COS（可选）</td><td>对象存储 + CDN</td></tr>
  <tr><td>部署方案</td><td>Cloudflare Pages + Vercel</td><td>全免费自动部署</td></tr>
</table>

<!-- 第二部分：功能说明书 -->
<h1 id="functional-spec" class="page-break">二、功能说明书</h1>

<h2 id="home-page">2.1 首页</h2>

<h3>布局概览</h3>
<ol>
  <li><strong>问候区</strong>：显示"早安/午安/晚安，{昵称}！"+ 当前日期</li>
  <li><strong>励志卡片</strong>：名言 + 🔥 连续学习天数</li>
  <li><strong>统计卡片</strong>：今日完成任务数、距离考试天数、农场等级</li>
  <li><strong>当前计划卡片</strong>：计划名称、考试日期</li>
  <li><strong>快捷入口</strong>：🍅 开始学习 / 📚 今日复习 / 🌱 照顾农场 / 📊 学习统计</li>
  <li><strong>今日任务预览</strong>：最多显示 3 条今日任务，可勾选完成、编辑、跳转番茄钟</li>
</ol>

<h3>功能清单</h3>
<table>
  <tr><th>功能</th><th>操作</th><th>说明</th></tr>
  <tr><td>查看连续学习天数</td><td>自动显示</td><td>从后端番茄记录计算，从今天往前数连续活跃天数</td></tr>
  <tr><td>查看今日完成数</td><td>自动显示</td><td>从任务看板同步</td></tr>
  <tr><td>查看剩余天数</td><td>自动显示</td><td>当前计划考试日期 - 今天</td></tr>
  <tr><td>查看农场等级</td><td>自动显示</td><td>经验值 / 100 + 1</td></tr>
  <tr><td>跳转番茄钟</td><td>点击「🍅 开始学习」</td><td>进入番茄计时页面</td></tr>
  <tr><td>跳转复习</td><td>点击「📚 今日复习」</td><td>进入知识卡片页面（复习tab）</td></tr>
  <tr><td>跳转农场</td><td>点击「🌱 照顾农场」</td><td>进入学习农场</td></tr>
  <tr><td>跳转统计</td><td>点击「📊 学习统计」</td><td>进入统计分析页面</td></tr>
  <tr><td>完成任务</td><td>点击任务左边的 ○</td><td>切换完成/未完成状态</td></tr>
  <tr><td>编辑任务</td><td>点击任务内容或 ✎ 按钮</td><td>弹出编辑弹窗</td></tr>
  <tr><td>任务跳转番茄钟</td><td>点击任务右侧 🍅</td><td>跳转番茄钟，自动关联该任务</td></tr>
</table>

<h3>编辑任务弹窗</h3>
<ul>
  <li><strong>科目</strong>：从科目网格中选择</li>
  <li><strong>章节</strong>：文本输入（如"第3章 二叉树"）</li>
  <li><strong>任务内容</strong>：多行文本输入</li>
  <li><strong>类型</strong>：新学 / 复习 / 错题（三选一）</li>
  <li><strong>预计时间</strong>：分钟数</li>
  <li><strong>开始时间</strong>：小时选择（6:00-23:00）</li>
  <li><strong>四象限分类</strong>：重要紧急/重要不紧急/紧急不重要/不紧急不重要</li>
  <li><strong>循环</strong>：不循环 / 每天 / 工作日 / 节假日</li>
  <li><strong>实际用时</strong>：系统自动记录（不可编辑）</li>
</ul>

<h2 id="task-board">2.2 任务看板</h2>

<h3>布局概览</h3>
<ol>
  <li><strong>顶部统计</strong>：已完成 / 待完成 / 总任务</li>
  <li><strong>视图切换</strong>：今日 / 周视图 / 月视图</li>
  <li><strong>日历</strong>：月视图日历，有任务的日期显示圆点标记</li>
  <li><strong>周视图</strong>：7列×18行时间网格（6:00-23:00），每格显示该时段任务</li>
  <li><strong>四象限开关</strong>：开启后任务卡片显示象限标签</li>
  <li><strong>筛选标签</strong>：全部 / 待完成 / 已完成</li>
  <li><strong>科目筛选</strong>：横向滚动，可选择全部或特定科目</li>
  <li><strong>任务列表</strong>：每条显示复选框、内容、科目、章节、估计/实际用时、🍅 按钮</li>
  <li><strong>番茄记录区</strong>：选中日期若有专注记录，显示总次数和分钟数</li>
</ol>

<h3>周视图特色功能</h3>
<div class="highlight-box">
  <strong>周视图科目颜色区分：</strong>每个科目任务块使用不同的颜色，基于科目名称哈希生成动态 HSL 颜色。新增科目自动获得独特颜色，无需手动配置。
  <ul>
    <li>背景色：浅色调（亮度 94%），清晰易读</li>
    <li>文字颜色：深色调（亮度 32%），与背景形成对比</li>
    <li>时间颜色：中深色调（亮度 38%），层次分明</li>
  </ul>
</div>

<h3>功能清单</h3>
<table>
  <tr><th>功能</th><th>操作</th><th>说明</th></tr>
  <tr><td>添加任务</td><td>点击「+ 添加任务」</td><td>弹出添加弹窗（支持AI解析 / 自定义添加）</td></tr>
  <tr><td>编辑任务</td><td>点击任务内容区域</td><td>弹出编辑弹窗</td></tr>
  <tr><td>完成任务</td><td>点击 ○</td><td>完成后自动给农场对应科目施肥</td></tr>
  <tr><td>取消完成</td><td>再次点击 ✓</td><td>恢复为待完成</td></tr>
  <tr><td>跳转番茄钟</td><td>点击 🍅</td><td>自动关联该任务到计时器</td></tr>
  <tr><td>切换视图</td><td>点击今日/周视图/月视图</td><td>不同时间粒度查看任务</td></tr>
  <tr><td>周视图添加任务</td><td>点击时间格</td><td>自动填入日期+开始小时，弹出添加弹窗</td></tr>
  <tr><td>周视图右键菜单</td><td>右键/长按时间格</td><td>新建任务 / 从已有任务复制</td></tr>
  <tr><td>月视图选择日期</td><td>点击日历格子</td><td>加载该日期的任务和番茄记录</td></tr>
  <tr><td>切换月份/周数</td><td>点击 ‹ › 箭头</td><td>浏览不同月份/周数</td></tr>
  <tr><td>筛选任务类型</td><td>点击标签</td><td>全部/待完成/已完成</td></tr>
  <tr><td>筛选科目</td><td>点击科目标签</td><td>只看该科目的任务</td></tr>
  <tr><td>下载周计划</td><td>点击下载按钮</td><td>导出周视图为图片</td></tr>
</table>

<h3>循环任务</h3>
<p>创建任务时可选择重复类型：</p>
<ul>
  <li><strong>不循环</strong>：仅在指定日期出现</li>
  <li><strong>每天</strong>：从创建日起每天都会出现</li>
  <li><strong>工作日</strong>：周一至周五出现</li>
  <li><strong>节假日</strong>：周六日出现</li>
</ul>

<h2 id="pomodoro">2.3 番茄钟</h2>

<h3>布局概览</h3>
<ol>
  <li><strong>关联任务</strong>：点击可选择今日任务，计时时显示任务名</li>
  <li><strong>计时圆环</strong>：渐变圆环显示进度（红色=专注，绿色=休息）</li>
  <li><strong>时间显示</strong>：MM:SS 大数字</li>
  <li><strong>状态标签</strong>：准备专注 / 专注中 🔥 / 休息中 ☕ / 已暂停</li>
  <li><strong>控制按钮</strong>：开始专注 / 暂停 / 重置</li>
  <li><strong>时间设置</strong>：专注时长（5-120分钟）、休息时长（1-30分钟）</li>
  <li><strong>统计</strong>：今日完成番茄数、今日总时长</li>
  <li><strong>今日记录</strong>：列表显示每次专注的任务名、时间、时长</li>
  <li><strong>手动添加</strong>：输入分钟数和任务描述，手动添加一条记录</li>
</ol>

<h3>完成通知机制</h3>
<p>番茄钟完成一轮后：</p>
<ul>
  <li><strong>Web Audio API</strong>：播放上行音阶（C5→E5→G5）</li>
  <li><strong>振动</strong>：H5 用 <code>navigator.vibrate()</code></li>
  <li><strong>浏览器通知</strong>：页面在后台时弹出系统通知</li>
  <li><strong>后端同步</strong>：自动创建 FocusRecord 到数据库</li>
  <li><strong>农场浇水</strong>：自动给对应科目的植物浇水</li>
</ul>

<h2 id="flash-cards">2.4 知识卡片</h2>

<h3>布局概览</h3>
<ol>
  <li><strong>顶部统计</strong>：待复习 / 总卡片 / 已掌握</li>
  <li><strong>筛选体系（三层）</strong>：科目 → 标签 → 掌握程度</li>
  <li><strong>标签支持多选</strong>：选中 ≥2 个标签时出现「或 / 且」切换按钮</li>
  <li><strong>卡片列表</strong>：科目标签、标签、掌握程度徽章、问题、图片缩略图、复习次数、下次复习日期</li>
</ol>

<h3>功能清单</h3>
<table>
  <tr><th>功能</th><th>操作</th><th>说明</th></tr>
  <tr><td>添加卡片</td><td>点击右下角 + 按钮</td><td>弹出添加弹窗</td></tr>
  <tr><td>编辑卡片</td><td>点击「编辑」按钮</td><td>弹出编辑弹窗</td></tr>
  <tr><td>删除卡片</td><td>点击「删除」</td><td>二次确认</td></tr>
  <tr><td>科目筛选</td><td>点击科目标签</td><td>单一科目筛选</td></tr>
  <tr><td>标签多选</td><td>点击标签</td><td>可多选，支持 AND/OR 逻辑</td></tr>
  <tr><td>掌握程度筛选</td><td>点击掌握程度标签</td><td>未掌握(红)/较熟悉(橙)/已掌握(绿)</td></tr>
  <tr><td>开始复习</td><td>点击「开始复习」</td><td>进入复习模式</td></tr>
  <tr><td>查看图片</td><td>点击图片缩略图</td><td>全屏预览</td></tr>
  <tr><td>AI 生成卡片</td><td>输入学习内容</td><td>GLM-4.5-Air 自动拆解成问答卡片</td></tr>
</table>

<h3>卡片创建弹窗</h3>
<ul>
  <li><strong>科目</strong>：网格选择，可「+ 自定义」</li>
  <li><strong>标签</strong>：已有标签选择器 + 自定义输入框</li>
  <li><strong>问题/答案</strong>：文本区域 + 图片（📷拍照/🖼️相册最多9张/📋粘贴）</li>
  <li>纯图片卡片（无文字）完全支持</li>
</ul>

<h2 id="mistake-book">2.5 错题本</h2>

<h3>布局概览</h3>
<ol>
  <li><strong>顶部统计</strong>：总错题 / 已掌握 / 待攻克</li>
  <li><strong>筛选体系（三层）</strong>：科目 → 标签 → 做错次数</li>
  <li><strong>错题列表</strong>：科目、标签、难度、已掌握标记、题目、正确答案、错误分析、创建日期、正确进度、做错次数</li>
</ol>

<h3>功能清单</h3>
<table>
  <tr><th>功能</th><th>操作</th><th>说明</th></tr>
  <tr><td>添加错题</td><td>点击右下角 + 按钮</td><td>弹出添加弹窗</td></tr>
  <tr><td>编辑错题</td><td>点击「编辑」</td><td>弹出编辑弹窗</td></tr>
  <tr><td>删除错题</td><td>点击「删除」</td><td>二次确认</td></tr>
  <tr><td>标记已掌握</td><td>点击「已掌握」</td><td>手动标记为已掌握</td></tr>
  <tr><td>重新攻克</td><td>点击「重新攻克」</td><td>取消已掌握标记</td></tr>
  <tr><td>科目筛选</td><td>点击科目标签</td><td>同卡片</td></tr>
  <tr><td>标签多选</td><td>点击标签</td><td>同卡片，支持 AND/OR</td></tr>
  <tr><td>做错次数筛选</td><td>点击次数标签</td><td>1次(橙)/2次(红)/3次+(深红)</td></tr>
  <tr><td>开始复习</td><td>点击「开始复习」</td><td>进入复习模式</td></tr>
</table>

<h3>错题创建弹窗</h3>
<ul>
  <li><strong>科目</strong>：同卡片；<strong>标签</strong>：同卡片（红色主题）</li>
  <li><strong>题目内容</strong>、<strong>正确答案</strong>、<strong>错误分析</strong>（选填）</li>
  <li><strong>难度</strong>：简单 / 中等 / 困难（三选一）</li>
  <li><strong>图片</strong>：📷 / 🖼️ / 📋</li>
</ul>

<h2 id="review-mode">2.6 复习模式</h2>

<h3>卡片复习流程</h3>
<ol>
  <li>点击「开始复习」进入 → 显示进度：<strong>3 / 10</strong></li>
  <li>每次显示一张卡片：科目标签 + Q（文字+图片）</li>
  <li>点击「点击查看答案」→ 显示 A（文字+图片）</li>
  <li>底部反馈：
    <ul>
      <li>😣 未掌握 → 明天复习</li>
      <li>🤔 较熟悉 → 3天后复习</li>
      <li>😎 已掌握 → 7天后复习</li>
    </ul>
  </li>
  <li>复习完显示 🏆 "复习完成！"</li>
</ol>

<h3>错题复习流程</h3>
<ol>
  <li>类似卡片，显示 Q（题目+图片）</li>
  <li>查看答案后额外显示错误分析</li>
  <li>反馈：
    <ul>
      <li>❌ 做错了 → 清零重来</li>
      <li>✅ 做对了 → 连续3次标记已掌握</li>
    </ul>
  </li>
  <li>复习完显示 🏆 "复习完成！" + 正确/总题数</li>
</ol>

<h2 id="farm">2.7 学习农场</h2>

<h3>游戏化激励机制</h3>
<p>学习农场将枯燥的学习变成有趣的种植游戏：</p>
<ul>
  <li>每个科目对应一株植物</li>
  <li>完成番茄钟 → 给植物浇水 💧</li>
  <li>完成任务 → 给植物施肥 🌱</li>
  <li>植物成长阶段：种子 → 发芽 → 成长 → 成熟 → 收获</li>
  <li>收获植物获得金币 💰 和经验值 ⭐</li>
  <li>经验值累积提升农场等级</li>
</ul>

<h3>功能清单</h3>
<table>
  <tr><th>功能</th><th>说明</th></tr>
  <tr><td>查看农场</td><td>展示所有科目的植物及其成长状态</td></tr>
  <tr><td>种植新植物</td><td>新增科目时自动创建对应植物</td></tr>
  <tr><td>浇水</td><td>番茄钟完成后自动浇水</td></tr>
  <tr><td>施肥</td><td>任务完成后自动施肥</td></tr>
  <tr><td>收获</td><td>植物成熟后可收获，获得金币和经验</td></tr>
  <tr><td>等级系统</td><td>经验值积累提升农场等级</td></tr>
  <tr><td>金币系统</td><td>可用于购买道具（未来扩展）</td></tr>
</table>

<h2 id="statistics">2.8 学习统计</h2>

<h3>统计维度</h3>
<ul>
  <li><strong>时间范围</strong>：今日 / 本周 / 本月 / 全部</li>
  <li><strong>概况卡片</strong>：总学习时长、番茄数、完成任务数</li>
  <li><strong>饼图</strong>：各科目学习时长占比</li>
  <li><strong>趋势图</strong>：每日学习时长趋势</li>
  <li><strong>科目分布</strong>：各科目详细统计数据</li>
</ul>

<div class="info-box">
  <strong>数据来源：</strong>所有统计数据来自后端数据库的 <code>focus_records</code> 表，确保数据准确可靠。
</div>

<h2 id="plan-management">2.9 计划管理</h2>

<h3>计划总览页</h3>
<ul>
  <li><strong>计划切换</strong>：点击切换面板切换计划</li>
  <li><strong>计划信息</strong>：考试名称、日期、每日学习时间、剩余天数</li>
  <li><strong>科目列表</strong>：每个科目显示名称、目标分数</li>
  <li><strong>甘特图</strong>：计划 vs 实际进度对比可视化</li>
  <li><strong>AI 识别教材目录</strong>：上传教材目录图片，GLM-4.1V 视觉模型自动识别章节</li>
</ul>

<h3>新建/编辑计划</h3>
<ul>
  <li>考试名称、考试日期（日期选择器）</li>
  <li>每日学习时间（分钟）</li>
  <li>动态科目列表（科目名 + 目标分数），可添加/删除</li>
  <li>可选备注</li>
</ul>

<h3>甘特图功能</h3>
<ul>
  <li><strong>三种视图模式</strong>：仅计划 / 仅实际 / 对比</li>
  <li><strong>科目章节展示</strong>：每个章节横向条显示时间跨度</li>
  <li><strong>点击编辑</strong>：点击章节条可编辑计划和实际日期</li>
  <li><strong>今日标记</strong>：红色竖线标记今天位置</li>
</ul>

<h2 id="ai-planning">2.10 AI 智能规划</h2>

<h3>AI 模型选型</h3>
<table>
  <tr><th>场景</th><th>模型</th><th>特点</th></tr>
  <tr><td>纯文本对话、工具调用、Agent</td><td>glm-4.5-air</td><td>激活参少、便宜、速度快</td></tr>
  <tr><td>传图 / 传视频 / GUI 理解</td><td>glm-4.1v-thinking-flashx</td><td>便宜、极速、多模态</td></tr>
</table>

<h3>AI 功能列表</h3>
<table>
  <tr><th>接口</th><th>功能</th><th>模型</th></tr>
  <tr><td>POST /api/plans/ai/generate</td><td>生成完整学习计划</td><td>GLM-4.5-Air</td></tr>
  <tr><td>POST /api/tasks/ai/generate</td><td>生成今日任务</td><td>GLM-4.5-Air</td></tr>
  <tr><td>POST /api/cards/ai/generate</td><td>从学习内容生成卡片</td><td>GLM-4.5-Air</td></tr>
  <tr><td>POST /api/ai/review</td><td>生成每日复盘总结</td><td>GLM-4.5-Air</td></tr>
  <tr><td>POST /api/ai/syllabus</td><td>识别教材目录图片</td><td>GLM-4.1V-Thinking-FlashX</td></tr>
</table>

<div class="highlight-box">
  <strong>降级机制：</strong>未配置 GLM_API_KEY 时，文本生成类接口使用内置 Mock 数据演示功能；图片识别接口返回 mock 的章节列表。
</div>

<h2 id="profile">2.11 个人中心</h2>

<h3>统计卡片</h3>
<ul>
  <li><strong>学习计划</strong>：当前用户拥有的计划总数</li>
  <li><strong>复习卡片</strong>：所有计划下的卡片总数（跨计划汇总）</li>
  <li><strong>学习天数</strong>：所有计划下有番茄记录的日期总数（去重）</li>
</ul>

<h3>菜单列表</h3>
<ul>
  <li><strong>计划管理</strong>：我的计划、新建计划、AI 生成计划</li>
  <li><strong>学习管理</strong>：学习统计</li>
  <li><strong>其他</strong>：设置</li>
</ul>

<h3>设置功能</h3>
<ul>
  <li>个人信息编辑（昵称、头像）</li>
  <li>修改密码</li>
  <li>偏好设置</li>
  <li>退出登录（二次确认）</li>
</ul>

<h2 id="memory-algorithm">2.12 艾宾浩斯记忆算法</h2>

<h3>知识卡片复习间隔</h3>
<table>
  <tr><th>掌握程度</th><th>第1次</th><th>第2次</th><th>第3次</th><th>第4次</th><th>第5次</th><th>第6次+</th><th>长期</th></tr>
  <tr><td>未掌握</td><td>1天</td><td>1天</td><td>2天</td><td>3天</td><td>5天</td><td>8天</td><td>30天</td></tr>
  <tr><td>较熟悉</td><td>3天</td><td>5天</td><td>8天</td><td>14天</td><td>21天</td><td>30天</td><td>-</td></tr>
  <tr><td>已掌握</td><td>7天</td><td>14天</td><td>30天</td><td>30天</td><td>30天</td><td>30天</td><td>-</td></tr>
</table>

<h4>规则说明</h4>
<ul>
  <li>复习时回答正确 → 掌握程度升一级（未掌握→较熟悉→已掌握）</li>
  <li>回答错误 → 降一级（已掌握→较熟悉→未掌握）</li>
  <li>下次复习日期 = 上次复习日期 + 对应天数</li>
  <li>系统保证<strong>下次复习日期永不低于创建日期</strong></li>
</ul>

<h3>错题本复习间隔</h3>
<table>
  <tr><th>连续正确次数</th><th>下次复习间隔</th></tr>
  <tr><td>0次（刚做错）</td><td>明天</td></tr>
  <tr><td>第1次正确</td><td>1天后</td></tr>
  <tr><td>第2次正确</td><td>3天后</td></tr>
  <tr><td>第3次正确</td><td>7天后</td></tr>
  <tr><td>第4次正确</td><td>14天后</td></tr>
  <tr><td>第5次正确</td><td>30天后</td></tr>
</table>

<h4>规则说明</h4>
<ul>
  <li>做错时正确次数清零，错误次数+1</li>
  <li>连续正确 ≥3 次 → 自动标记为"已掌握"</li>
</ul>

<!-- 第三部分：系统架构设计 -->
<h1 id="architecture" class="page-break">三、系统架构设计</h1>

<h2 id="arch-overview">3.1 整体架构</h2>

<h3>架构图</h3>
<div class="architecture-diagram">
用户手机/电脑浏览器（国内网络）
        │
        ▼
Cloudflare Pages 前端（静态 H5 + _worker.js API代理）
        │
        ├── 静态资源 ──► Cloudflare CDN（国内节点）
        │
        └── /api/* 请求 ──► _worker.js 代理 ──► Vercel 后端（FastAPI）
                                                        │
                                            ┌───────────┴───────────┐
                                            ▼                       ▼
                                    Supabase PostgreSQL      腾讯云 COS（图片）
</div>

<h3>架构设计原则</h3>
<ol>
  <li><strong>前后端分离</strong>：前端 UniApp 多端输出，后端 FastAPI 纯 API 服务</li>
  <li><strong>Serverless 优先</strong>：前后端均部署在 Serverless 平台，按需付费，免费额度充足</li>
  <li><strong>CDN 加速</strong>：前端静态资源通过 Cloudflare CDN 全球加速</li>
  <li><strong>国内访问优化</strong>：使用 Cloudflare Worker 代理 API 请求，绕过 Vercel 国内 DNS 污染</li>
  <li><strong>可扩展性</strong>：模块化设计，易于添加新功能和新模块</li>
</ol>

<h2 id="frontend-arch">3.2 前端架构</h2>

<h3>目录结构</h3>
<pre>
frontend/
├── src/
│   ├── pages/                  # 页面组件
│   │   ├── index/              #   首页
│   │   ├── auth/               #   登录/注册
│   │   ├── plan/               #   计划管理 + AI规划
│   │   ├── daily/              #   任务看板 + 番茄钟 + 四象限
│   │   ├── review/             #   复习（卡片+错题）
│   │   ├── farm/               #   学习农场
│   │   ├── statistics/         #   学习统计
│   │   └── profile/            #   个人中心 + 设置
│   ├── components/             # 公共组件
│   │   ├── TaskFormModal.vue   #   任务表单弹窗
│   │   └── TaskReflectionModal.vue
│   ├── stores/                 # Pinia 状态管理
│   │   ├── user.js             #   用户状态
│   │   ├── plan.js             #   学习计划状态
│   │   ├── task.js             #   任务状态
│   │   ├── card.js             #   卡片状态
│   │   ├── farm.js             #   农场状态
│   │   └── subjects.js         #   科目状态
│   ├── api/                    # API 请求封装
│   │   ├── client.js           #   API 客户端
│   │   ├── ai.js               #   AI 相关 API
│   │   └── supabase.js         #   Supabase 封装
│   ├── utils/                  # 工具函数
│   │   ├── date.js             #   日期处理
│   │   ├── export.js           #   导出功能
│   │   ├── storage.js          #   本地存储
│   │   └── upload.js           #   图片上传
│   ├── styles/                 # 全局样式
│   │   ├── global.scss
│   │   ├── mixins.scss
│   │   └── variables.scss
│   ├── static/                 # 静态资源
│   ├── App.vue                 # 根组件
│   ├── main.js                 # 入口文件
│   └── pages.json              # 页面路由配置
├── _worker.js                  # Cloudflare Worker（API代理）
├── vite.config.js
└── package.json
</pre>

<h3>状态管理（Pinia）</h3>
<table>
  <tr><th>Store</th><th>核心状态</th><th>主要方法</th></tr>
  <tr>
    <td><strong>userStore</strong></td>
    <td>user, isLoggedIn, token</td>
    <td>login, register, logout, getUserInfo</td>
  </tr>
  <tr>
    <td><strong>planStore</strong></td>
    <td>currentPlan, plans</td>
    <td>getPlansByUserId, createPlan, updatePlan, deletePlan, switchPlan</td>
  </tr>
  <tr>
    <td><strong>taskStore</strong></td>
    <td>tasks, weekTasks</td>
    <td>getTasks, createTask, updateTask, completeTask, uncompleteTask</td>
  </tr>
  <tr>
    <td><strong>cardStore</strong></td>
    <td>cards</td>
    <td>getCards, createCard, updateCard, deleteCard, reviewCard</td>
  </tr>
  <tr>
    <td><strong>farmStore</strong></td>
    <td>plants, farmState</td>
    <td>getPlants, ensureCrop, waterPlant, fertilizePlant, harvestPlant</td>
  </tr>
  <tr>
    <td><strong>subjectsStore</strong></td>
    <td>subjects, userSubjects, planSubjects</td>
    <td>load, add, remove</td>
  </tr>
</table>

<h3>页面路由</h3>
<table>
  <tr><th>路径</th><th>页面名称</th><th>TabBar</th></tr>
  <tr><td>/pages/index/index</td><td>首页</td><td>✅</td></tr>
  <tr><td>/pages/daily/task-board</td><td>任务看板</td><td>✅</td></tr>
  <tr><td>/pages/farm/farm</td><td>学习农场</td><td>✅</td></tr>
  <tr><td>/pages/review/index</td><td>复习</td><td>✅</td></tr>
  <tr><td>/pages/profile/profile</td><td>个人中心</td><td>✅</td></tr>
  <tr><td>/pages/auth/login</td><td>登录</td><td>❌</td></tr>
  <tr><td>/pages/auth/register</td><td>注册</td><td>❌</td></tr>
  <tr><td>/pages/plan/plan-overview</td><td>计划总览</td><td>❌</td></tr>
  <tr><td>/pages/plan/target-setup</td><td>目标设置</td><td>❌</td></tr>
  <tr><td>/pages/plan/ai-plan</td><td>AI 生成计划</td><td>❌</td></tr>
  <tr><td>/pages/daily/pomodoro</td><td>番茄钟</td><td>❌</td></tr>
  <tr><td>/pages/daily/quadrant</td><td>四象限</td><td>❌</td></tr>
  <tr><td>/pages/statistics/stats</td><td>学习统计</td><td>❌</td></tr>
  <tr><td>/pages/profile/settings</td><td>设置</td><td>❌</td></tr>
</table>

<h2 id="backend-arch">3.3 后端架构</h2>

<h3>目录结构</h3>
<pre>
backend/
├── main.py                  # 应用入口，FastAPI 实例
├── config.py                # 环境配置
├── database.py              # 数据模型（SQLAlchemy）
├── seed.py                  # 种子数据脚本
├── routes/                  # API 路由
│   ├── __init__.py
│   ├── auth.py              #   认证相关
│   ├── plans.py             #   学习计划
│   ├── tasks.py             #   每日任务
│   ├── cards.py             #   知识卡片
│   ├── mistakes.py          #   错题本
│   ├── farm.py              #   学习农场
│   ├── focus.py             #   番茄钟记录
│   ├── ai.py                #   AI 功能
│   ├── upload.py            #   图片上传
│   ├── subjects.py          #   自定义科目
│   └── reflections.py       #   任务反思
├── services/                # 业务服务
│   ├── ai_service.py        #   AI 服务（智谱 GLM）
│   ├── cos_service.py       #   腾讯云 COS 服务
│   └── memory.py            #   记忆曲线算法
├── schemas/                 # Pydantic 数据校验
│   ├── user.py
│   ├── plan.py
│   ├── task.py
│   ├── card.py
│   ├── mistake.py
│   ├── farm.py
│   └── focus.py
├── api/index.py             # Vercel Serverless 入口
├── pyproject.toml
└── requirements.txt
</pre>

<h3>核心模块说明</h3>

<h4>1. 认证模块（auth.py）</h4>
<ul>
  <li>用户注册（邮箱+密码）</li>
  <li>用户登录（JWT Token）</li>
  <li>密码使用 bcrypt 哈希存储</li>
  <li>Token 有效期可配置（默认 1440 分钟）</li>
</ul>

<h4>2. 计划模块（plans.py）</h4>
<ul>
  <li>CRUD 学习计划</li>
  <li>计划切换</li>
  <li>科目章节管理</li>
  <li>AI 生成计划接口</li>
</ul>

<h4>3. 任务模块（tasks.py）</h4>
<ul>
  <li>CRUD 每日任务</li>
  <li>任务完成/取消完成</li>
  <li>循环任务支持</li>
  <li>按日期/科目筛选</li>
</ul>

<h4>4. 卡片模块（cards.py）</h4>
<ul>
  <li>CRUD 知识卡片</li>
  <li>按艾宾浩斯曲线计算下次复习日期</li>
  <li>掌握程度管理（未掌握/较熟悉/已掌握）</li>
  <li>标签筛选（支持 AND/OR）</li>
  <li>AI 生成卡片</li>
</ul>

<h4>5. 错题模块（mistakes.py）</h4>
<ul>
  <li>CRUD 错题</li>
  <li>错误次数统计</li>
  <li>连续正确计数</li>
  <li>自动标记已掌握</li>
</ul>

<h4>6. 农场模块（farm.py）</h4>
<ul>
  <li>植物 CRUD</li>
  <li>浇水/施肥</li>
  <li>收获</li>
  <li>金币/经验/等级系统</li>
</ul>

<h4>7. 番茄钟模块（focus.py）</h4>
<ul>
  <li>专注记录 CRUD</li>
  <li>统计数据计算</li>
  <li>按时间范围查询</li>
</ul>

<h2 id="database-design">3.4 数据库设计</h2>

<h3>数据表清单</h3>
<table>
  <tr><th>表名</th><th>说明</th><th>核心字段</th></tr>
  <tr>
    <td><strong>users</strong></td>
    <td>用户表</td>
    <td>id, email, nickname, avatar_url, hashed_password</td>
  </tr>
  <tr>
    <td><strong>study_plans</strong></td>
    <td>学习计划表</td>
    <td>id, user_id, exam_name, exam_date, target_scores, daily_study_time, subjects</td>
  </tr>
  <tr>
    <td><strong>daily_tasks</strong></td>
    <td>每日任务表</td>
    <td>id, plan_id, date, type, subject, content, duration, status, repeat_type, importance</td>
  </tr>
  <tr>
    <td><strong>task_reflections</strong></td>
    <td>任务反思表</td>
    <td>id, task_id, plan_id, task_date, actual_duration, completion_issues</td>
  </tr>
  <tr>
    <td><strong>flash_cards</strong></td>
    <td>知识卡片表</td>
    <td>id, plan_id, question, answer, subject, mastery_level, next_review_date, tags</td>
  </tr>
  <tr>
    <td><strong>mistakes</strong></td>
    <td>错题本表</td>
    <td>id, plan_id, question, answer, analysis, subject, difficulty, error_count, next_review_date</td>
  </tr>
  <tr>
    <td><strong>plants</strong></td>
    <td>农场植物表</td>
    <td>id, plan_id, type, subject, progress, water_count, fertilize_count</td>
  </tr>
  <tr>
    <td><strong>farm_states</strong></td>
    <td>农场状态表</td>
    <td>id, plan_id, coins, experience, level</td>
  </tr>
  <tr>
    <td><strong>focus_records</strong></td>
    <td>番茄记录表</td>
    <td>id, plan_id, user_id, date, type, subject, task_id, duration</td>
  </tr>
  <tr>
    <td><strong>user_subjects</strong></td>
    <td>用户自定义科目</td>
    <td>id, user_id, name</td>
  </tr>
</table>

<h3>实体关系图（ER 图概览）</h3>
<div class="architecture-diagram">
users (1) ──< study_plans (N)
                      │
                      ├──< daily_tasks (N)
                      │        │
                      │        └──< task_reflections (N)
                      │
                      ├──< flash_cards (N)
                      │
                      ├──< mistakes (N)
                      │
                      ├──< plants (N)
                      │
                      ├──< farm_states (1)
                      │
                      └──< focus_records (N)

users (1) ──< user_subjects (N)
users (1) ──< focus_records (N)
</div>

<h3>索引设计</h3>
<ul>
  <li><code>users.email</code>：唯一索引</li>
  <li><code>study_plans.user_id</code>：普通索引</li>
  <li><code>daily_tasks.plan_id</code>：普通索引</li>
  <li><code>daily_tasks.date</code>：普通索引</li>
  <li><code>flash_cards.plan_id</code>：普通索引</li>
  <li><code>flash_cards.next_review_date</code>：普通索引</li>
  <li><code>mistakes.plan_id</code>：普通索引</li>
  <li><code>mistakes.next_review_date</code>：普通索引</li>
  <li><code>focus_records.plan_id</code>：普通索引</li>
  <li><code>focus_records.user_id</code>：普通索引</li>
  <li><code>focus_records.date</code>：普通索引</li>
</ul>

<h2 id="api-design">3.5 API 接口设计</h2>

<h3>认证接口</h3>
<table>
  <tr><th>方法</th><th>路径</th><th>说明</th><th>请求体</th><th>响应</th></tr>
  <tr><td>POST</td><td>/api/auth/register</td><td>用户注册</td><td>{email, password, nickname}</td><td>{access_token, user}</td></tr>
  <tr><td>POST</td><td>/api/auth/login</td><td>用户登录</td><td>{email, password}</td><td>{access_token, user}</td></tr>
  <tr><td>GET</td><td>/api/auth/me</td><td>获取当前用户</td><td>-</td><td>{user}</td></tr>
</table>

<h3>计划接口</h3>
<table>
  <tr><th>方法</th><th>路径</th><th>说明</th></tr>
  <tr><td>GET</td><td>/api/plans</td><td>获取计划列表</td></tr>
  <tr><td>POST</td><td>/api/plans</td><td>创建计划</td></tr>
  <tr><td>GET</td><td>/api/plans/{id}</td><td>获取计划详情</td></tr>
  <tr><td>PUT</td><td>/api/plans/{id}</td><td>更新计划</td></tr>
  <tr><td>DELETE</td><td>/api/plans/{id}</td><td>删除计划</td></tr>
  <tr><td>POST</td><td>/api/plans/ai/generate</td><td>AI 生成计划</td></tr>
</table>

<h3>任务接口</h3>
<table>
  <tr><th>方法</th><th>路径</th><th>说明</th></tr>
  <tr><td>GET</td><td>/api/tasks</td><td>获取任务列表（支持 date 筛选）</td></tr>
  <tr><td>POST</td><td>/api/tasks</td><td>创建任务</td></tr>
  <tr><td>PUT</td><td>/api/tasks/{id}</td><td>更新任务</td></tr>
  <tr><td>DELETE</td><td>/api/tasks/{id}</td><td>删除任务</td></tr>
  <tr><td>POST</td><td>/api/tasks/{id}/complete</td><td>完成任务</td></tr>
  <tr><td>POST</td><td>/api/tasks/{id}/uncomplete</td><td>取消完成</td></tr>
  <tr><td>POST</td><td>/api/tasks/ai/generate</td><td>AI 生成任务</td></tr>
</table>

<h3>卡片接口</h3>
<table>
  <tr><th>方法</th><th>路径</th><th>说明</th></tr>
  <tr><td>GET</td><td>/api/cards</td><td>获取卡片列表</td></tr>
  <tr><td>POST</td><td>/api/cards</td><td>创建卡片</td></tr>
  <tr><td>PUT</td><td>/api/cards/{id}</td><td>更新卡片</td></tr>
  <tr><td>DELETE</td><td>/api/cards/{id}</td><td>删除卡片</td></tr>
  <tr><td>POST</td><td>/api/cards/{id}/review</td><td>提交复习结果</td></tr>
  <tr><td>POST</td><td>/api/cards/ai/generate</td><td>AI 生成卡片</td></tr>
</table>

<h3>错题接口</h3>
<table>
  <tr><th>方法</th><th>路径</th><th>说明</th></tr>
  <tr><td>GET</td><td>/api/mistakes</td><td>获取错题列表</td></tr>
  <tr><td>POST</td><td>/api/mistakes</td><td>创建错题</td></tr>
  <tr><td>PUT</td><td>/api/mistakes/{id}</td><td>更新错题</td></tr>
  <tr><td>DELETE</td><td>/api/mistakes/{id}</td><td>删除错题</td></tr>
  <tr><td>POST</td><td>/api/mistakes/{id}/review</td><td>提交复习结果</td></tr>
</table>

<h3>农场接口</h3>
<table>
  <tr><th>方法</th><th>路径</th><th>说明</th></tr>
  <tr><td>GET</td><td>/api/farm/plants</td><td>获取植物列表</td></tr>
  <tr><td>POST</td><td>/api/farm/ensure</td><td>确保作物存在</td></tr>
  <tr><td>POST</td><td>/api/farm/water</td><td>浇水</td></tr>
  <tr><td>POST</td><td>/api/farm/fertilize</td><td>施肥</td></tr>
  <tr><td>POST</td><td>/api/farm/harvest</td><td>收获</td></tr>
  <tr><td>GET</td><td>/api/farm/state</td><td>获取农场状态</td></tr>
</table>

<h3>番茄钟接口</h3>
<table>
  <tr><th>方法</th><th>路径</th><th>说明</th></tr>
  <tr><td>GET</td><td>/api/focus</td><td>获取专注记录</td></tr>
  <tr><td>POST</td><td>/api/focus</td><td>创建专注记录</td></tr>
  <tr><td>GET</td><td>/api/focus/stats</td><td>获取统计数据</td></tr>
</table>

<h2 id="deployment">3.6 部署架构</h2>

<h3>当前生产部署方案</h3>
<table>
  <tr><th>组件</th><th>平台</th><th>费用</th><th>说明</th></tr>
  <tr><td>前端 H5</td><td>Cloudflare Pages</td><td>免费</td><td>仓库路径 frontend/，自动从 GitHub 构建</td></tr>
  <tr><td>后端 API</td><td>Vercel</td><td>免费</td><td>Serverless Functions，仓库路径 backend/</td></tr>
  <tr><td>数据库</td><td>Supabase</td><td>免费 500MB</td><td>PostgreSQL 托管</td></tr>
  <tr><td>图片存储</td><td>腾讯云 COS</td><td>免费额度</td><td>可选配置</td></tr>
  <tr><td>API 代理</td><td>Cloudflare Worker</td><td>免费</td><td>_worker.js 绕过 Vercel 国内 DNS 污染</td></tr>
</table>

<div class="info-box">
  <strong>为什么用 Cloudflare 前端 + Vercel 后端？</strong><br>
  Vercel 在国内有 DNS 污染问题。前端放 Cloudflare Pages 走国内 CDN，API 请求通过 <code>_worker.js</code> 代理转发到 Vercel 后端，绕过污染。
</div>

<h3>CI/CD 流程</h3>
<ol>
  <li>代码推送到 GitHub main 分支</li>
  <li>Cloudflare Pages 自动构建前端并部署</li>
  <li>Vercel 自动构建后端 Serverless Functions 并部署</li>
  <li>数据库表结构通过 <code>Base.metadata.create_all()</code> 自动创建</li>
</ol>

<!-- 第四部分：附录 -->
<h1 id="appendix" class="page-break">四、附录</h1>

<h2 id="env-config">4.1 环境变量配置</h2>

<h3>后端环境变量（backend/.env）</h3>
<table>
  <tr><th>变量名</th><th>必填</th><th>说明</th><th>示例</th></tr>
  <tr><td>DATABASE_URL</td><td>✅</td><td>数据库连接字符串</td><td>postgresql://user:pass@host:5432/db</td></tr>
  <tr><td>DB_SSLMODE</td><td>-</td><td>SSL 模式</td><td>require / disable</td></tr>
  <tr><td>SECRET_KEY</td><td>✅</td><td>JWT 密钥</td><td>openssl rand -hex 32 生成</td></tr>
  <tr><td>ACCESS_TOKEN_EXPIRE_MINUTES</td><td>-</td><td>Token 有效期（分钟）</td><td>1440</td></tr>
  <tr><td>GLM_API_KEY</td><td>-</td><td>智谱 AI API Key</td><td>-</td></tr>
  <tr><td>GLM_TEXT_MODEL</td><td>-</td><td>文本模型</td><td>glm-4.5-air</td></tr>
  <tr><td>GLM_VISION_MODEL</td><td>-</td><td>视觉模型</td><td>glm-4.1v-thinking-flashx</td></tr>
  <tr><td>COS_SECRET_ID</td><td>-</td><td>腾讯云 COS SecretId</td><td>-</td></tr>
  <tr><td>COS_SECRET_KEY</td><td>-</td><td>腾讯云 COS SecretKey</td><td>-</td></tr>
  <tr><td>COS_BUCKET</td><td>-</td><td>COS 存储桶</td><td>-</td></tr>
  <tr><td>COS_REGION</td><td>-</td><td>COS 地域</td><td>ap-guangzhou</td></tr>
  <tr><td>CORS_ORIGINS</td><td>-</td><td>CORS 源</td><td>*</td></tr>
</table>

<h2 id="quick-start">4.2 快速开始</h2>

<h3>环境要求</h3>
<ul>
  <li><strong>Node.js</strong> >= 18 + npm >= 9</li>
  <li><strong>Python</strong> >= 3.10</li>
  <li><strong>Docker</strong> + Docker Compose（可选，用于本地 PostgreSQL）</li>
</ul>

<h3>启动步骤</h3>
<ol>
  <li>
    <p><strong>克隆项目</strong></p>
    <pre>git clone https://github.com/hazaban/StudyMate.git
cd StudyMate</pre>
  </li>
  <li>
    <p><strong>启动数据库（Docker 方式）</strong></p>
    <pre>docker compose up -d
# 数据库在 localhost:5433，用户 studymate / 密码 studymate123</pre>
  </li>
  <li>
    <p><strong>启动后端</strong></p>
    <pre>cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn main:app --host 0.0.0.0 --port 8002 --reload</pre>
  </li>
  <li>
    <p><strong>启动前端</strong></p>
    <pre>cd frontend
npm install
npm run dev:h5</pre>
  </li>
</ol>

<p>打开 http://localhost:5173 即可使用。</p>

<h2 id="test-account">4.3 测试账号</h2>
<table>
  <tr><th>项目</th><th>值</th></tr>
  <tr><td>邮箱</td><td>test@studymate.com</td></tr>
  <tr><td>密码</td><td>123456</td></tr>
  <tr><td>预置计划</td><td>考研408计算机 + 软考中级</td></tr>
  <tr><td>预置数据</td><td>30天历史番茄记录、12张卡片、9道错题、8株植物、3个自定义科目</td></tr>
</table>

<div class="highlight-box">
  执行 <code>cd backend && python seed.py</code> 可重置为上述测试数据。
</div>

</body>
</html>
"""

output_path = "/workspace/StudyMate_功能说明书与架构设计.pdf"
HTML(string=html_content).write_pdf(output_path)
print(f"PDF generated successfully: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")

# StudyMate 学习星球 - 项目框架规划

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **前端框架** | UniApp + Vue3 + Composition API | 跨端开发，支持 Web/微信小程序/原生 App |
| **状态管理** | Pinia | Vue 官方推荐，轻量易上手 |
| **UI组件库** | uView Plus | UniApp 生态组件库，中文文档完善 |
| **后端/BaaS** | Supabase | 用户认证、PostgreSQL 数据库、实时同步 |
| **图片存储** | 腾讯云 COS | 对象存储，STS 临时凭证签名直传 |
| **AI能力** | DeepSeek V4-Flash / DeepSeek V4-Pro | 性价比极高，支持 1M 上下文，缓存命中价格极低 |
| **构建工具** | Vite | 快速开发，热更新 |

---

## 目录结构

```
studymate-uniapp/
├── src/
│   ├── pages/                    # 页面目录
│   │   ├── auth/                 # 认证页面
│   │   │   ├── login.vue         # 登录页
│   │   │   └── register.vue      # 注册页
│   │   ├── plan/                 # 学习计划页面
│   │   │   ├── target-setup.vue  # 目标设置页
│   │   │   └── plan-overview.vue # 计划总览页
│   │   ├── daily/                # 每日任务页面
│   │   │   ├── task-board.vue    # 任务看板页
│   │   │   └── pomodoro.vue      # 番茄钟页
│   │   ├── review/               # 复习页面
│   │   │   ├── flash-cards.vue   # 复习卡片页
│   │   │   └── mistake-book.vue  # 错题本页
│   │   ├── farm/                 # 农场页面
│   │   │   └── farm.vue          # 学习农场页
│   │   ├── statistics/           # 统计页面
│   │   │   └── stats.vue         # 学习统计页
│   │   ├── profile/              # 个人中心
│   │   │   └── profile.vue       # 个人信息页
│   │   └── index.vue             # 首页
│   ├── components/               # 组件目录
│   │   ├── common/               # 公共组件
│   │   │   ├── NavBar.vue        # 导航栏
│   │   │   ├── TabBar.vue        # 底部标签栏
│   │   │   ├── Loading.vue       # 加载动画
│   │   │   └── EmptyState.vue    # 空状态
│   │   ├── task/                 # 任务相关组件
│   │   │   ├── TaskCard.vue      # 任务卡片
│   │   │   └── TaskProgress.vue  # 任务进度条
│   │   ├── farm/                 # 农场相关组件
│   │   │   ├── PlantCard.vue     # 植物卡片
│   │   │   └── FarmAnimation.vue # 农场动画
│   │   └── card/                 # 卡片相关组件
│   │       ├── FlashCard.vue     # 复习卡片
│   │       └── CardFlip.vue      # 卡片翻转效果
│   ├── stores/                   # Pinia 状态管理
│   │   ├── user.js               # 用户状态
│   │   ├── plan.js               # 学习计划状态
│   │   ├── task.js               # 每日任务状态
│   │   ├── card.js               # 复习卡片状态
│   │   └── farm.js               # 农场状态
│   ├── api/                      # API 接口封装
│   │   ├── supabase.js           # Supabase 封装
│   │   ├── cos.js                # 腾讯云 COS 封装
│   │   └── ai.js                 # AI API 封装
│   ├── utils/                    # 工具函数
│   │   ├── upload.js             # 图片上传工具
│   │   ├── pomodoro.js           # 番茄钟工具
│   │   ├── date.js               # 日期格式化工具
│   │   ├── memory.js             # 记忆曲线算法
│   │   └── storage.js            # 本地存储工具
│   ├── styles/                   # 全局样式
│   │   ├── variables.scss        # 样式变量
│   │   ├── mixins.scss           # 样式混入
│   │   └── global.scss           # 全局样式
│   ├── static/                   # 静态资源
│   │   ├── images/               # 图片资源
│   │   ├── icons/                # 图标资源
│   │   └── data/                 # 模拟数据
│   ├── App.vue                   # 根组件
│   ├── main.js                   # 入口文件
│   └── pages.json                # 页面路由配置
├── public/                       # 静态资源（Web端）
├── index.html                    # HTML 模板
├── package.json                  # 依赖配置
├── vite.config.js                # Vite 配置
└── manifest.json                 # UniApp 配置
```

---

## 页面路由规划

### 页面清单

| 页面路径 | 页面名称 | 功能描述 | 是否 TabBar |
|---------|---------|---------|-------------|
| `/pages/index` | 首页 | 学习概览、快速入口、今日推荐 | ✅ |
| `/pages/daily/task-board` | 任务看板 | 今日任务列表、新学/复习/错题分类 | ✅ |
| `/pages/farm/farm` | 学习农场 | 植物成长可视化、浇水施肥互动 | ✅ |
| `/pages/review/flash-cards` | 复习卡片 | 问答复习、掌握程度标记 | ✅ |
| `/pages/auth/login` | 登录页 | 邮箱/手机号登录 | ❌ |
| `/pages/auth/register` | 注册页 | 用户注册 | ❌ |
| `/pages/plan/target-setup` | 目标设置 | 考试日期、科目配置、目标分数 | ❌ |
| `/pages/plan/plan-overview` | 计划总览 | 阶段计划、进度统计 | ❌ |
| `/pages/daily/pomodoro` | 番茄钟 | 计时、暂停、完成、统计 | ❌ |
| `/pages/review/mistake-book` | 错题本 | 错题收集、分类、重做 | ❌ |
| `/pages/statistics/stats` | 学习统计 | 时长统计、掌握进度图表 | ❌ |
| `/pages/profile/profile` | 个人中心 | 用户信息、设置、帮助 | ❌ |

### TabBar 配置

```json
{
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#2f7d4f",
    "borderStyle": "black",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index",
        "text": "首页",
        "iconPath": "static/icons/home.png",
        "selectedIconPath": "static/icons/home-active.png"
      },
      {
        "pagePath": "pages/daily/task-board",
        "text": "任务",
        "iconPath": "static/icons/task.png",
        "selectedIconPath": "static/icons/task-active.png"
      },
      {
        "pagePath": "pages/farm/farm",
        "text": "农场",
        "iconPath": "static/icons/farm.png",
        "selectedIconPath": "static/icons/farm-active.png"
      },
      {
        "pagePath": "pages/review/flash-cards",
        "text": "复习",
        "iconPath": "static/icons/card.png",
        "selectedIconPath": "static/icons/card-active.png"
      }
    ]
  }
}
```

---

## 组件清单

### 公共组件

| 组件名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `NavBar` | 自定义导航栏 | 全局页面 |
| `TabBar` | 底部标签栏 | TabBar 页面 |
| `Loading` | 加载动画 | 数据请求时 |
| `EmptyState` | 空状态展示 | 列表为空时 |

### 任务相关组件

| 组件名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `TaskCard` | 任务卡片展示 | 任务看板 |
| `TaskProgress` | 任务进度条 | 任务详情、计划总览 |

### 农场相关组件

| 组件名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `PlantCard` | 植物卡片 | 农场页面 |
| `FarmAnimation` | 农场动画效果 | 种植、浇水、收获 |

### 卡片相关组件

| 组件名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `FlashCard` | 复习卡片 | 复习页面 |
| `CardFlip` | 卡片翻转效果 | 复习卡片 |

---

## 数据模型

### Supabase 数据库表

#### 1. users（用户表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键，用户ID |
| email | TEXT | 邮箱（唯一） |
| nickname | TEXT | 昵称 |
| avatar_url | TEXT | 头像URL |
| created_at | TIMESTAMP | 创建时间 |

#### 2. study_plans（学习计划表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 用户ID（外键） |
| exam_name | TEXT | 考试名称 |
| exam_date | DATE | 考试日期 |
| target_scores | JSONB | 各科目标分数 |
| daily_study_time | INT | 每日学习时长（分钟） |
| weak_points | TEXT[] | 薄弱点 |
| created_at | TIMESTAMP | 创建时间 |

#### 3. daily_tasks（每日任务表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| plan_id | UUID | 计划表ID（外键） |
| date | DATE | 任务日期 |
| type | TEXT | 任务类型：new_study/review/mistake |
| subject | TEXT | 科目 |
| content | TEXT | 任务内容 |
| duration | INT | 预计时长（分钟） |
| status | TEXT | 状态：pending/doing/completed |
| completed_at | TIMESTAMP | 完成时间 |
| proof_image_url | TEXT | 完成凭证图片URL |
| created_at | TIMESTAMP | 创建时间 |

#### 4. flash_cards（复习卡片表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| plan_id | UUID | 计划表ID（外键） |
| question | TEXT | 问题 |
| answer | TEXT | 答案 |
| subject | TEXT | 科目 |
| mastery_level | TEXT | 掌握程度：unmastered/familiar/mastered |
| next_review_date | DATE | 下次复习日期 |
| review_count | INT | 复习次数 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### 5. plants（农场植物表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| plan_id | UUID | 计划表ID（外键） |
| type | TEXT | 植物类型：seed/sprout/growing/mature/harvested |
| subject | TEXT | 对应科目 |
| progress | INT | 成长进度 0-100 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### Pinia Store 模块

#### 1. userStore

```js
{
  user: null,
  isLoggedIn: false,
  token: null
}

login(email, password)
register(email, password, nickname)
logout()
getUserInfo()
```

#### 2. planStore

```js
{
  currentPlan: null,
  plans: [],
  targetScores: {},
  dailyStudyTime: 0,
  weakPoints: []
}

createPlan(data)
updatePlan(id, data)
deletePlan(id)
getPlanById(id)
getPlansByUserId()
generatePlanByAI()
```

#### 3. taskStore

```js
{
  todayTasks: [],
  currentTask: null,
  completedCount: 0,
  totalCount: 0
}

getTasksByDate(date)
createTask(data)
updateTask(id, data)
completeTask(id)
generateDailyTasks()
```

#### 4. cardStore

```js
{
  cards: [],
  currentCardIndex: 0,
  reviewMode: false,
  masteryLevel: 'unmastered'
}

getCardsByPlanId(planId)
createCard(data)
updateCard(id, data)
deleteCard(id)
markMastery(id, level)
generateCardsByAI()
```

#### 5. farmStore

```js
{
  plants: [],
  coins: 0,
  experience: 0,
  level: 1
}

getPlantsByPlanId(planId)
plantSeed(subject)
waterPlant(id)
harvestPlant(id)
updatePlantProgress(id, progress)
```

---

## API 层设计

### 1. supabase.js

```js
signInWithEmail(email, password)
signUpWithEmail(email, password)
signOut()
getUser()
createStudyPlan(data)
updateStudyPlan(id, data)
deleteStudyPlan(id)
getStudyPlanById(id)
getStudyPlansByUserId(userId)
createDailyTask(data)
updateDailyTask(id, data)
deleteDailyTask(id)
getDailyTasksByDate(planId, date)
createFlashCard(data)
updateFlashCard(id, data)
deleteFlashCard(id)
getFlashCardsByPlanId(planId)
createPlant(data)
updatePlant(id, data)
deletePlant(id)
getPlantsByPlanId(planId)
```

### 2. cos.js

```js
getSTSCredential()
uploadImage(filePath, options)
deleteImage(imageUrl)
getPreviewUrl(imageUrl)
```

### 3. ai.js

```js
generateStudyPlan(params)
generateDailyTasks(params)
generateFlashCards(content)
generateDailyReview(params)
askQuestion(question)
```

---

## 工具函数清单

### 1. upload.js

```js
compressImage(filePath, options)
getUploadSignature()
uploadToCOS(filePath, signature)
getImageUrl(fileName)
```

### 2. pomodoro.js

```js
startTimer(duration, callback)
pauseTimer()
resumeTimer()
stopTimer()
getRemainingTime()
formatTime(seconds)
```

### 3. date.js

```js
formatDate(date, format)
formatTime(date, format)
getToday()
getYesterday()
getTomorrow()
getDaysBetween(startDate, endDate)
isToday(date)
```

### 4. memory.js

```js
calculateNextReviewDate(lastReviewDate, masteryLevel)
getReviewInterval(masteryLevel)
updateMasteryLevel(currentLevel, isCorrect)
```

### 5. storage.js

```js
set(key, value)
get(key)
remove(key)
clear()
setObject(key, obj)
getObject(key)
```

---

## 成本估算

### Supabase

| 资源类型 | 免费额度 | 超出后价格 |
|---------|---------|-----------|
| 数据库存储 | 500 MB | $0.125/GB/月 |
| 文件存储 | 1 GB | $0.021/GB/月 |
| 月活跃用户 | 50,000 | $0.00325/用户 |
| 数据外传流量 | 5 GB | $0.09/GB |

### AI API 推荐方案（DeepSeek V4）

| 模型 | 输入（缓存命中） | 输入（缓存未命中） | 输出 | 并发限制 | 推荐场景 |
|------|-----------------|-------------------|------|---------|---------|
| **DeepSeek V4-Flash** | 0.02元/百万Token | 1元/百万Token | 2元/百万Token | 2500 | **MVP主力模型** |
| **DeepSeek V4-Pro** | 0.025元/百万Token | 3元/百万Token | 6元/百万Token | 500 | 复杂推理任务 |
| 通义千问 Qwen-VL-Max | - | 3元/百万Token | 9元/百万Token | - | 后期图片识别 |

**注意**：高峰时段（9:00-12:00, 14:00-18:00）价格翻倍

### MVP 月成本估算（使用 V4-Flash）

| 项目 | 日均调用量 | 月均Token | 费用 |
|------|-----------|-----------|------|
| AI计划生成 | 1次/周 | ~5万 | ¥0.1 |
| AI任务生成 | 1次/天 | ~30万 | ¥0.6 |
| AI卡片生成 | 5次/天 | ~150万 | ¥3 |
| AI复盘总结 | 1次/天 | ~20万 | ¥0.4 |
| **AI API合计** | - | - | **~¥4.1/月** |
| **Supabase** | - | - | **¥0** |
| **腾讯云 COS** | - | - | **¥0** |
| **合计** | - | - | **~¥4.1/月** |

---

## AI 多模态需求分析

| 场景 | 类型 | 是否需要多模态 |
|------|------|--------------|
| AI生成学习计划 | 纯文本 | ❌ |
| AI生成每日任务 | 纯文本 | ❌ |
| AI生成复习卡片 | 纯文本 | ❌ |
| AI每日复盘总结 | 纯文本 | ❌ |
| 拍照凭证AI识别 | 多模态 | ⚠️ 后期扩展 |

**结论：MVP阶段使用纯文本模型即可，无需多模态。**

---

## 开发里程碑

### 阶段一：项目初始化（第1-2周）

- [ ] 初始化 UniApp + Vue3 项目
- [ ] 配置 Supabase 连接
- [ ] 配置腾讯云 COS
- [ ] 创建数据库表结构
- [ ] 实现用户注册/登录

### 阶段二：核心功能开发（第3-4周）

- [ ] 实现目标设置页面
- [ ] 接入 AI API 生成计划
- [ ] 实现每日任务看板
- [ ] 数据持久化存储

### 阶段三：核心功能开发（第5-6周）

- [ ] 实现番茄钟计时功能
- [ ] 实现拍照上传凭证
- [ ] 实现农场动画效果
- [ ] 实现抗遗忘卡片

### 阶段四：完善与测试（第7-8周）

- [ ] 实现每日复盘功能
- [ ] 多端适配测试（Web/小程序）
- [ ] Bug 修复与性能优化
- [ ] 部署上线
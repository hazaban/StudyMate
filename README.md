# StudyMate 学习星球

<p align="center">
  <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=A%20beautiful%20logo%20for%20a%20study%20app%20named%20StudyMate%20with%20a%20planet%20and%20stars%20theme%2C%20green%20and%20%5B...%5D" />
</p>

<p align="center">
  <strong>AI 抗遗忘备考工具 —— 让知识进脑子，而不是走过场</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vuedotjs" alt="Vue" />
  <img src="https://img.shields.io/badge/UniApp-3.0-2B9939?logo=uni-app" alt="UniApp" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License" />
</p>

---

## 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [项目架构](#项目架构)
- [目录结构](#目录结构)
- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [1. 克隆项目](#1-克隆项目)
  - [2. 后端部署](#2-后端部署)
  - [3. 前端启动](#3-前端启动)
  - [4. 种子数据](#4-种子数据)
- [API 文档](#api-文档)
- [落地方案](#落地方案)
- [开发指南](#开发指南)
- [License](#license)

---

## 项目简介

StudyMate 学习星球是一款面向考研/考公/考证备考人群的 **AI 抗遗忘学习工具**。它结合了**艾宾浩斯遗忘曲线**科学的复习调度、**番茄钟专注计时**、[...]

## 核心功能

<table>
  <tr>
    <td width="50%">
      <h4>📋 智能任务管理</h4>
      <p>创建学习计划，按天拆解任务。支持新学、复习、错题三种任务类型，查看每日进度。</p>
    </td>
    <td width="50%">
      <h4>🧠 知识卡片 + 艾宾浩斯复习</h4>
      <p>创建知识卡片，支持文字和图片混合输入。根据艾宾浩斯遗忘曲线自动推算每日复习任务，答案可手动展开。</p>
    </td>
  </tr>
  <tr>
    <td>
      <h4>❌ 错题本 + 掌握度追踪</h4>
      <p>记录错题（文字+图片），连续做对 2 次即标记"已掌握"。按艾宾浩斯曲线安排复习时间，支持自定义标签筛选。</p>
    </td>
    <td>
      <h4>🍅 番茄钟专注计时</h4>
      <p>自定义专注/休息时长，支持手动输入或按钮调整。沉浸式专注体验，完成番茄数计入统计。</p>
    </td>
  </tr>
  <tr>
    <td>
      <h4>🌱 游戏化学习农场</h4>
      <p>每完成学习任务即可浇水种植，植物从种子→发芽→生长→成熟→收获，学习进度可视化，收获金币和等级。</p></td>
    <td>
      <h4>📊 学习统计看板</h4>
      <p>总学习时长、番茄数、任务完成率、科目分布、学习趋势图表、成就徽章系统。</p>
    </td>
  </tr>
  <tr>
    <td>
      <h4>🤖 AI 智能规划（DeepSeek）</h4>
      <p>接入 DeepSeek V4 大模型，根据用户目标自动生成个性化学习计划，AI 辅助知识卡片生成。</p>
    </td>
    <td>
      <h4>📷 图片上传支持</h4>
      <p>题目和答案均支持腾讯云 COS 直传图片，问题图片和答案图片独立管理，不限数量。</p>
    </td>
  </tr>
</table>

## 技术栈

### 前端

| 技术 | 说明 |
|------|------|
| **Vue 3** (Composition API) | 渐进式 JavaScript 框架 |
| **UniApp 3.0** | 跨端开发框架，一套代码多端运行 |
| **Pinia** | Vue 3 官方状态管理 |
| **SCSS** | CSS 预处理器 |
| **Vite** | 下一代前端构建工具 |

### 后端

| 技术 | 说明 |
|------|------|
| **FastAPI** | 高性能 Python Web 框架 |
| **SQLAlchemy 2.0** | Python ORM |
| **PostgreSQL** | 关系型数据库 |
| **JWT (python-jose)** | 无状态身份认证 |
| **bcrypt** | 密码哈希 |
| **DeepSeek API** | AI 大模型接口 |
| **腾讯云 COS** | 对象存储（图片） |

## 项目架构

```
┌──────────────────────────────────────────────────────┐
│                    客户端 (UniApp)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  首页   │  │ 任务看板 │  │ 复习卡片 │  │ 个人中心 │ │
│  │  index  │  │  task   │  │  review  │  │ profile  │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘ │
│       │            │            │            │        │
│  ┌────┴────────────┴────────────┴────────────┴────┐  │
│  │              Pinia Stores (状态管理)             │  │
│  │  user · plan · task · card · farm              │  │
│  └──────────────────────┬─────────────────────────┘  │
│                         │                            │
│  ┌──────────────────────┴─────────────────────────┐  │
│  │              API Client (client.js)             │  │
│  │              /api → Vite Proxy → FastAPI        │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────┘
                       │  HTTP / REST
┌──────────────────────┴───────────────────────────────┐
│                  服务端 (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Routes  │  │ Services │  │ Schemas  │           │
│  │  auth    │  │  memory  │  │  user    │           │
│  │  plans   │  │ ai_svc   │  │  plan    │           │
│  │  tasks   │  │ cos_svc  │  │  task    │           │
│  │  cards   │  │          │  │  card    │           │
│  │ mistakes │  │          │  │ mistake  │           │
│  │  farm    │  │          │  │  farm    │           │
│  │  ai      │  │          │  │          │           │
│  │  upload  │  │          │  │          │           │
│  └────┬─────┘  └──────────┘  └──────────┘           │
│       │                                              │
│  ┌────┴──────────────────────────────────────┐       │
│  │        SQLAlchemy ORM + PostgreSQL          │       │
│  │  users · study_plans · daily_tasks          │       │
│  │  flash_cards · mistakes · plants            │       │
│  │  farm_states                                 │       │
│  └─────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────┘
```

### 数据流

```
用户操作 → Vue 组件 → Pinia Store → API Client (HTTP)
    → FastAPI Router → Service Layer → SQLAlchemy → PostgreSQL
    → 响应返回 → Store 更新 → 组件响应式渲染
```

### 艾宾浩斯复习算法

```
复习间隔: [1天, 3天, 7天, 14天, 30天]
         ↓
第1次做对 → 1天后复习
第2次做对 → 3天后复习
第3次做对 → 7天后复习
第4次做对 → 14天后复习
第5次做对 → 30天后复习
第6次做对 → 标记"已掌握"
做错 → correct_count 清零，重新从第1天开始
```

## 目录结构

```
studymate-uniapp/
├── server/                         # 后端服务
│   ├── routes/                     # API 路由
│   │   ├── auth.py                 #   用户认证（注册/登录）
│   │   ├── plans.py                #   学习计划 CRUD
│   │   ├── tasks.py                #   每日任务管理
│   │   ├── cards.py                #   知识卡片 + 艾宾浩斯复习
│   │   │   ├── mistakes.py             #   错题本 + 掌握度追踪
│   │   │   ├── farm.py                 #   学习农场（种植/浇水/收获）
│   │   │   ├── ai.py                   #   DeepSeek AI 接口
│   │   │   └── upload.py               #   腾讯云 COS 图片上传
│   │   ├── schemas/                    # Pydantic 数据校验
│   │   │   ├── user.py
│   │   │   ├── plan.py
│   │   │   ├── task.py
│   │   │   ├── card.py
│   │   │   ├── mistake.py
│   │   │   └── farm.py
│   │   ├── services/                   # 业务逻辑层
│   │   │   ├── memory.py               #   艾宾浩斯遗忘曲线算法
│   │   │   ├── ai_service.py           #   DeepSeek API 封装
│   │   │   └── cos_service.py          #   腾讯云 COS STS 凭证
│   │   ├── config.py                   # 环境配置
│   │   ├── database.py                 # 数据库模型 & 连接
│   │   ├── main.py                     # FastAPI 应用入口
│   │   ├── seed.py                     # 测试种子数据脚本
│   │   │   └── requirements.txt            # Python 依赖
│
├── src/                            # 前端源码
│   ├── pages/                      # 页面组件
│   │   ├── index/                  #   首页
│   │   ├── daily/                  #   每日任务
│   │   │   ├── task-board.vue      #     任务看板
│   │   │   └── pomodoro.vue        #     番茄钟
│   │   ├── review/                 #   复习
│   │   │   ├── flash-cards.vue     #     知识卡片
│   │   │   └── mistake-book.vue    #     错题本
│   │   ├── farm/                   #   学习农场
│   │   │   ├── plan/                   #   学习计划
│   │   │   │   ├── target-setup.vue    #     目标设置
│   │   │   │   └── plan-overview.vue   #     计划总览
│   │   │   ├── statistics/             #   学习统计
│   │   │   ├── profile/                #   个人中心
│   │   │   └── auth/                   #   登录/注册
│   │   ├── stores/                     # Pinia 状态管理
│   │   │   ├── user.js                 #   用户状态
│   │   │   ├── plan.js                 #   计划状态
│   │   │   ├── task.js                 #   任务状态
│   │   │   ├── card.js                 #   卡片状态
│   │   │   └── farm.js                 #   农场状态
│   │   ├── api/                        # API 请求封装
│   │   │   ├── client.js               #   Axios 实例 + 拦截器
│   │   │   └── ai.js                   #   AI 接口
│   │   ├── utils/                      # 工具函数
│   │   │   ├── date.js                 #   日期格式化
│   │   │   ├── storage.js              #   本地存储
│   │   │   └── upload.js               #   图片上传
│   │   ├── styles/                     # 全局样式
│   │   │   ├── variables.scss          #   SCSS 变量
│   │   │   ├── mixins.scss             #   SCSS 混入
│   │   │   └── global.scss             #   全局样式
│   │   ├── static/icons/               # 图标资源
│   │   ├── App.vue                     # 根组件
│   │   ├── main.js                     # 入口文件
│   │   ├── pages.json                  # 页面路由配置
│   │   │   └── manifest.json               # 应用配置
│   │
│   │
│   ├── vite.config.js                  # Vite 构建配置
│   ├── package.json                    # Node 依赖
│   └── README.md
```

## 快速开始

### 环境要求

- **Node.js** >= 18
- **Python** >= 3.12
- **PostgreSQL** >= 16
- **npm** >= 9

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd studymate-uniapp
```

### 2. 后端部署

#### 2.1 创建 PostgreSQL 数据库

```bash
# 登录 PostgreSQL
psql -U postgres

# 创建数据库和用户
CREATE USER studymate WITH PASSWORD 'studymate123';
CREATE DATABASE studymate OWNER studymate;
\q
```

#### 2.2 配置环境变量

```bash
cd server
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接和 API 密钥：

```env
# 数据库（默认开发配置）
DATABASE_URL=postgresql://studymate:studymate123@localhost:5432/studymate

# JWT 密钥（生产环境务必修改）
SECRET_KEY=your-secret-key-change-in-production

# DeepSeek AI（可选，不配置则 AI 功能不可用）
DEEPSEEK_API_KEY=sk-your-api-key

# 腾讯云 COS（可选，不配置则图片上传不可用）
COS_SECRET_ID=your-secret-id
COS_SECRET_KEY=your-secret-key
COS_BUCKET=studymate-1250000000
COS_REGION=ap-guangzhou
```

#### 2.3 安装依赖 & 启动

```bash
cd server

# 安装 Python 依赖
pip install -r requirements.txt

# 运行种子数据（创建测试用户）
python seed.py

# 启动后端服务
python main.py
# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 3. 前端启动

```bash
# 在项目根目录
npm install

# 启动 H5 开发服务器
npm run dev:h5
```

前端启动后访问 http://localhost:5173 即可看到应用。

**测试账号：**
- 邮箱：`test@studymate.com`
- 密码：`123456`

### 4. 种子数据

种子数据包含完整的测试内容：

| 板块 | 数据量 | 说明 |
|------|--------|------|
| 用户 | 1 个 | test@studymate.com |
| 学习计划 | 1 个 | 考研408计算机专业基础综合 |
| 每日任务 | 6 个 | 3 种类型（新学/复习/错题），4 个科目 |
| 知识卡片 | 9 个 | 5 张今日到期，4 张未来到期 |
| 错题 | 5 个 | 3 道今日待复习，1 道已掌握 |
| 农场植物 | 2 株 | 生长中（70%）和发芽中（30%） |
| 农场状态 | Lv.2 | 120 金币，70 经验值 |

```bash
cd server
python seed.py
```

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看完整的 Swagger UI 交互式 API 文档。

### 主要 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| POST | `/api/plans` | 创建学习计划 |
| GET | `/api/plans` | 获取用户所有计划 |
| GET | `/api/tasks` | 获取指定日期任务 |
| POST | `/api/tasks` | 创建任务 |
| PATCH | `/api/tasks/{id}/status` | 更新任务状态 |
| POST | `/api/cards` | 创建知识卡片 |
| GET | `/api/cards` | 获取卡片列表（支持标签/科目筛选） |
| GET | `/api/cards/pending` | 获取今日待复习卡片 |
| POST | `/api/cards/{id}/review` | 提交复习结果 |
| POST | `/api/mistakes` | 创建错题 |
| GET | `/api/mistakes` | 获取错题列表 |
| GET | `/api/mistakes/pending` | 获取今日待复习错题 |
| POST | `/api/mistakes/{id}/review` | 提交错题复习结果 |
| GET | `/api/farm` | 获取农场状态 |
| POST | `/api/farm/water/{plant_id}` | 浇水 |
| POST | `/api/farm/harvest/{plant_id}` | 收获 |
| POST | `/api/ai/generate-plan` | AI 生成学习计划 |
| POST | `/api/upload/cos-credential` | 获取 COS 上传凭证 |

## 落地方案

### 当前项目可以直接落地使用，以下为三种方案：

---

### 方案一：H5 移动端 Web 应用（推荐，最快落地）

**适用场景：** 手机浏览器访问，无需安装

**部署方式：**

```bash
# 1. 构建 H5 产物
npm run build:h5

# 2. 产物在 dist/build/h5 目录，部署到任意静态服务器
# 可选：Nginx、Vercel、Netlify、阿里云 OSS + CDN
```

**优势：**
- 零安装成本，扫码即用
- 一次部署，iOS/Android 通用
- 更新无需审核，即时生效
- 适合 MVP 快速验证

**推荐部署平台：** Vercel（免费）或阿里云 OSS + CDN

---

### 方案二：微信小程序（用户量最大）

**适用场景：** 微信生态内使用，方便分享

**操作步骤：**

```bash
# 1. 构建微信小程序
npm run dev:mp-weixin

# 2. 用微信开发者工具打开 dist/dev/mp-weixin
# 3. 在微信公众平台注册小程序 → 上传代码 → 提交审核
```

**优势：**
- 微信 12 亿用户生态
- 下拉入口、分享卡片、模板消息
- UniApp 直接编译，无需额外开发

**注意事项：**
- 需要微信小程序备案（个人/企业主体均可）
- 后端 API 域名需 HTTPS 并配置到小程序白名单
- 部分 Web API（如 WebSocket）在小程序中有限制

---

### 方案三：Android/iOS App（最完整体验）

**适用场景：** 需要原生能力（推送、后台计时、离线存储）

**操作步骤：**

```bash
# 构建 App 资源
npm run build:app

# 用 HBuilderX 打开项目 → 发行 → 原生 App-云打包
```

**优势：**
- 完整的原生体验
- 可以上架应用商店
- 支持离线使用

**注意事项：**
- 需要 Apple Developer 账号（$99/年）上架 App Store
- Android 需要各应用商店的开发者账号
- 审核周期较长

---

### 推荐落地方案：H5 + 微信小程序 双端

| 端 | 平台 | 部署方式 | 成本 |
|----|------|----------|------|
| 手机端 | H5 Web | Vercel / 阿里云 OSS | 免费~几十元/月 |
| 手机端 | 微信小程序 | 微信公众平台 | 免费 |
| 电脑端 | H5 Web | 同手机端 | 已包含 |
| 后端 | FastAPI | 阿里云/腾讯云 ECS 2C4G | ~100元/月 |
| 数据库 | PostgreSQL | 云数据库 RDS | ~50元/月 |

**电脑端使用：** H5 版本天然支持 PC 浏览器访问，无需额外开发。UniApp 的 H5 模式在 PC 上会自动适配为宽屏布局。

**手机端使用：** 通过 H5 链接或微信小程序扫码即可使用，无需安装 App。

---

## 开发指南

### 添加新页面

1. 在 `src/pages/` 下创建 `.vue` 文件
2. 在 `src/pages.json` 的 `pages` 数组中注册路由
3. 如需 TabBar 页面，在 `tabBar.list` 中配置

### 添加新 API

1. 在 `server/routes/` 下创建路由文件
2. 在 `server/main.py` 中 `include_router`
3. 在 `src/api/` 下封装前端请求方法
4. 在 `src/stores/` 中创建对应的 Pinia Store

### 数据库迁移

修改 `server/database.py` 中的模型后：

```bash
cd server
python -c "from database import init_db; init_db()"
# 或手动 ALTER TABLE
```

### 代码规范

- 前端：Vue 3 Composition API + `<script setup>` 语法
- 后端：FastAPI 路由 + Pydantic Schema 校验
- 命名：文件 kebab-case，组件 PascalCase，函数 camelCase

## License

MIT License

---

<p align="center">
  Made with ❤️ for learners everywhere
</p>

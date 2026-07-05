# StudyMate 学习星球

<p align="center">
  <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=A%20beautiful%20logo%20for%20a%20study%20app%20named%20StudyMate%20with%20a%20planet%20and%20stars%20theme%2C%20green%20and%20purple%20color%20scheme%2C%20flat%20vector%20style%2C%20modern%20design&image_size=square" alt="StudyMate Logo" width="120" />
</p>

<p align="center">
  <strong>抗遗忘备考工具 —— 让知识进脑子，而不是走过场</strong>
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
- [部署方案](#部署方案)
- [落地方案](#落地方案)
- [开发指南](#开发指南)
- [License](#license)

---

## 项目简介

StudyMate 学习星球是一款面向考研/考公/考证备考人群的 **抗遗忘学习工具**。它结合了**科学的间隔记忆复习调度**、**番茄钟专注计时**、**游戏化学习农场**三大核心机制，帮助用户高效记忆、持续专注、快乐学习。

## 核心功能

<table>
  <tr>
    <td width="50%">
      <h4>📋 智能任务管理</h4>
      <p>创建学习计划，按天拆解任务。支持新学、复习、错题三种任务类型，查看每日进度。</p>
    </td>
    <td width="50%">
      <h4>🧠 知识卡片 + 间隔记忆复习</h4>
      <p>创建知识卡片，支持文字和图片混合输入。根据三级掌握度（未掌握/较熟悉/已掌握）自动推算每日复习任务，答案可手动展开。</p>
    </td>
  </tr>
  <tr>
    <td>
      <h4>❌ 错题本 + 掌握度追踪</h4>
      <p>记录错题（文字+图片），连续做对 3 次即标记"已掌握"。按间隔记忆安排复习时间，支持自定义标签筛选。</p>
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
      <h4>🤖 AI 智能规划（后续开通）</h4>
      <p>预留 AI 大模型接口，后续可根据用户目标自动生成个性化学习计划，AI 辅助知识卡片生成。</p>
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
| **腾讯云 COS** | 对象存储（图片） |

## 项目架构

```
┌─────────────────────────────────────────────────────────────┐
│                Cloudflare Pages（前端 H5）                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  首页   │  │ 任务看板 │  │ 复习卡片 │  │ 个人中心 │       │
│  │  index  │  │  task   │  │  review  │  │ profile  │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
│       │            │            │            │               │
│  ┌────┴────────────┴────────────┴────────────┴────┐        │
│  │              Pinia Stores (状态管理)             │        │
│  │  user · plan · task · card · farm              │        │
│  └──────────────────────┬─────────────────────────┘        │
│                         │                                   │
│  ┌──────────────────────┴─────────────────────────┐        │
│  │         _worker.js (Cloudflare Worker)          │        │
│  │       /api/* 代理 ──► Vercel 后端               │        │
│  └────────────────────────────────────────────────┘        │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTPS
┌──────────────────────────┴──────────────────────────────────┐
│                  Vercel（后端 FastAPI）                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Routes  │  │ Services │  │ Schemas  │                  │
│  │  auth    │  │  memory  │  │  user    │                  │
│  │  plans   │  │ cos_svc  │  │  plan    │                  │
│  │  tasks   │  │          │  │  task    │                  │
│  │  cards   │  │          │  │  card    │                  │
│  │ mistakes │  │          │  │ mistake  │                  │
│  │  farm    │  │          │  │  farm    │                  │
│  │  upload  │  │          │  │          │                  │
│  └────┬─────┘  └──────────┘  └──────────┘                  │
│       │                                                     │
│  ┌────┴──────────────┐         ┌───────────────────┐        │
│  │ PostgreSQL (Supabase) │      │ 腾讯云 COS (图片)  │        │
│  └─────────────────────┘       └───────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户操作 → Vue 组件 → Pinia Store → API Client (HTTP)
    → FastAPI Router → Service Layer → SQLAlchemy → PostgreSQL
    → 响应返回 → Store 更新 → 组件响应式渲染
```

### 间隔记忆复习算法

知识卡片采用三级掌握度体系，每级对应不同的复习间隔：

| 掌握程度 | 第1次 | 第2次 | 第3次 | 第4次 | 第5次 | 第6次+ | 长期 |
|---------|------|------|------|------|------|--------|------|
| 未掌握 | 1天 | 1天 | 2天 | 3天 | 5天 | 8天 | 30天 |
| 较熟悉 | 3天 | 5天 | 8天 | 14天 | 21天 | 30天 | - |
| 已掌握 | 7天 | 14天 | 30天 | 30天 | 30天 | 30天 | - |

**规则**：
- 复习时回答正确 → 掌握程度升一级（未掌握→较熟悉→已掌握）
- 回答错误 → 降一级（已掌握→较熟悉→未掌握）
- 下次复习日期 = 上次复习日期 + 对应天数

错题本采用连续正确次数体系：

| 连续正确次数 | 下次复习间隔 |
|------------|------------|
| 0次（刚做错） | 明天 |
| 第1次正确 | 1天后 |
| 第2次正确 | 3天后 |
| 第3次正确 | 7天后 |
| 第4次正确 | 14天后 |
| 第5次正确 | 30天后 |

**规则**：
- 做错时正确次数清零，错误次数+1
- 连续正确 ≥2 次 → 自动标记为"已掌握"

## 目录结构

```
studymate-uniapp/
├── server/                         # 后端服务（部署到 Vercel）
│   ├── api/                        # Vercel Serverless 入口
│   │   └── index.py
│   ├── routes/                     # API 路由
│   │   ├── auth.py                 #   用户认证（注册/登录）
│   │   ├── plans.py                #   学习计划 CRUD
│   │   ├── tasks.py                #   每日任务管理
│   │   ├── cards.py                #   知识卡片 + 艾宾浩斯复习
│   │   ├── mistakes.py             #   错题本 + 掌握度追踪
│   │   ├── farm.py                 #   学习农场（种植/浇水/收获）
│   │   ├── ai.py                   #   DeepSeek AI 接口
│   │   └── upload.py               #   腾讯云 COS 图片上传
│   ├── schemas/                    # Pydantic 数据校验
│   │   ├── user.py
│   │   ├── plan.py
│   │   ├── task.py
│   │   ├── card.py
│   │   ├── mistake.py
│   │   └── farm.py
│   ├── services/                   # 业务逻辑层
│   │   ├── memory.py               #   艾宾浩斯遗忘曲线算法
│   │   ├── ai_service.py           #   DeepSeek API 封装
│   │   └── cos_service.py          #   腾讯云 COS 预签名 URL
│   ├── config.py                   # 环境配置
│   ├── database.py                 # 数据库模型 & 连接
│   ├── main.py                     # FastAPI 应用入口
│   ├── seed.py                     # 测试种子数据脚本
│   ├── vercel.json                 # Vercel 部署配置
│   └── requirements.txt            # Python 依赖
│
├── src/                            # 前端源码（部署到 Cloudflare Pages）
│   ├── pages/                      # 页面组件
│   │   ├── index/                  #   首页
│   │   ├── daily/                  #   每日任务
│   │   │   ├── task-board.vue      #     任务看板
│   │   │   └── pomodoro.vue        #     番茄钟
│   │   ├── review/                 #   复习（卡片+错题）
│   │   │   └── index.vue           #     知识卡片 & 错题本
│   │   ├── farm/                   #   学习农场
│   │   ├── plan/                   #   学习计划
│   │   │   ├── target-setup.vue    #     目标设置
│   │   │   └── plan-overview.vue   #     计划总览
│   │   ├── statistics/             #   学习统计
│   │   ├── profile/                #   个人中心
│   │   └── auth/                   #   登录/注册
│   ├── stores/                     # Pinia 状态管理
│   │   ├── user.js
│   │   ├── plan.js
│   │   ├── task.js
│   │   ├── card.js
│   │   └── farm.js
│   ├── api/                        # API 请求封装
│   │   ├── client.js               #   请求客户端（含 BASE_URL 配置）
│   │   └── supabase.js             #   Supabase 封装
│   ├── utils/                      # 工具函数
│   │   ├── date.js
│   │   ├── storage.js
│   │   ├── upload.js               #   图片上传到 COS
│   │   └── export.js               #   导出功能
│   ├── styles/                     # 全局样式
│   │   ├── variables.scss
│   │   ├── mixins.scss
│   │   └── global.scss
│   ├── static/icons/               # 图标资源
│   ├── App.vue
│   ├── main.js
│   ├── pages.json
│   └── manifest.json
│
├── public/                         # 静态资源（原样复制到构建产物）
│   └── _redirects                  # SPA 路由重定向规则
├── _worker.js                      # Cloudflare Worker（API 代理到 Vercel）
├── vite.config.js                  # Vite 构建配置
├── package.json
├── vercel.json                     # 根目录 Vercel 配置（前端）
└── README.md
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

## 部署方案

### 🏆 当前生产部署方案：Cloudflare Pages + Vercel + Supabase + 腾讯云 COS

当前线上生产环境采用以下架构，**国内访问稳定、无需代理**：

| 组件 | 平台 | 费用 | 说明 |
|------|------|------|------|
| 前端 H5 | **Cloudflare Pages** | 免费 | 全球 CDN，国内访问快，自动部署 |
| 后端 API | **Vercel** | 免费 | FastAPI Serverless，自动扩缩容 |
| 数据库 | **Supabase** | 免费 | PostgreSQL，500MB 空间，稳定可靠 |
| 图片存储 | **腾讯云 COS** | 免费额度 | 6个月50GB，之后几元/月 |
| API 代理 | **Cloudflare Worker** | 免费 | 内置在 Pages 中，绕过 Vercel 国内 DNS 污染 |

**架构图：**

```
用户手机/电脑（国内网络）
    │
    ▼
Cloudflare Pages 前端（静态 H5 + _worker.js）
    │
    ├── 静态资源 ──► Cloudflare CDN（国内节点）
    │
    └── /api/* 请求 ──► _worker.js 代理
                            │
                            ▼
                       Vercel 后端（FastAPI）
                            │
                            ├──► 腾讯云 COS（图片）
                            │
                            └──► Supabase PostgreSQL（数据库）
```

**为什么用 Cloudflare Pages 前端 + Vercel 后端？**

| 问题 | 解决方案 |
|------|----------|
| Vercel 国内访问不稳定 | 前端放 Cloudflare Pages，国内 CDN 节点速度快 |
| Vercel 国内 DNS 污染 | API 请求通过 Cloudflare Worker 代理转发，绕过污染 |
| 全放在 Cloudflare | Cloudflare Pages 不能直接跑 Python/FastAPI |
| 全放在 Vercel | 国内访问慢甚至打不开 |

> 💡 **关键技术**：前端通过 `_worker.js`（Cloudflare Worker）将所有 `/api/*` 请求代理到 Vercel 后端，前端代码无需改动，国内用户访问 Cloudflare 域名即可正常使用。

### 详细部署步骤

📖 完整部署文档请查看：[**docs/cloudflare-vercel-deploy.md**](docs/cloudflare-vercel-deploy.md)

包含从零开始的每一步操作：Supabase 数据库创建、腾讯云 COS 配置、Vercel 后端部署、Cloudflare Pages 前端部署、_worker.js 代理配置、常见问题排查。

---

### 其他部署方案参考

#### 方案对比

| 方案 | 优点 | 缺点 | 适合 |
|------|------|------|------|
| **Cloudflare + Vercel** ⭐ | 国内访问快，全免费，自动部署 | 两个平台管理 | 国内用户，个人使用 |
| **全 Vercel** | 一个平台管理 | 国内访问不稳定，需要代理 | 海外用户 |
| **全 Render** | 一个平台管理，无函数超时 | 国内访问慢，免费版休眠 | 追求简单，海外用户 |
| **全腾讯云** | 国内速度最快 | 要花钱（约50元/月） | 预算充足，企业级 |

#### 端侧落地方式

| 端 | 平台 | 部署方式 | 成本 |
|----|------|----------|------|
| 手机端 | H5 Web | Cloudflare Pages / 腾讯云 COS | 免费~几十元/月 |
| 手机端 | 微信小程序 | 微信公众平台 | 免费 |
| 电脑端 | H5 Web | 同手机端 | 已包含 |

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
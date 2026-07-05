# StudyMate 学习星球

<p align="center">
  <strong style="font-size:1.15em">抗遗忘备考工具 —— 让知识进脑子,而不是走过场</strong>
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

## 项目简介

StudyMate 学习星球是一款面向考研/考公/考证备考人群的 **抗遗忘学习工具**。结合**科学间隔记忆**复习调度、**番茄钟专注计时**、**游戏化学习农场**三大核心能力,帮助你:

- 📋 制定多科备考计划,按科目 + 章节拆分到每天
- 🍅 番茄钟计时,自动记录实际学习时长
- 🧠 知识卡片 + 错题本按记忆曲线自动安排复习
- 🌱 完成学习即可种植作物,游戏化激励持续学习
- 📊 学习时长、番茄数、科目分布多维度统计

**电脑端 + 手机端通用**:H5 网页(Cloudflare Pages)+ 微信小程序(后续),一套 UniApp 代码多端运行,同一账号数据互通。

---

## 核心功能

| 模块 | 说明 |
|------|------|
| 📋 智能任务管理 | 创建学习计划,按天拆解任务,支持新学/复习/错题三类 + 循环任务 |
| 🧠 知识卡片 + 间隔记忆复习 | 文字 + 图片混合卡片,按三级掌握度自动推算复习日期 |
| ❌ 错题本 + 掌握度追踪 | 记录错题(文字+图片),连续做对 3 次标记"已掌握" |
| 🍅 番茄钟专注计时 | 自定义专注/休息时长,完成后自动写入数据库,支持手动补录 |
| 🌱 游戏化学习农场 | 完成任务/番茄自动浇水施肥,植物从种子到收获,赚金币升级 |
| 📊 学习统计看板 | 总时长、番茄数、任务完成率、科目分布、趋势图表、成就徽章 |
| 📷 图片上传 | 腾讯云 COS 直传,支持拍照/相册/粘贴,自动压缩 |
| 📤 数据导出 | 卡片/错题支持 CSV / Excel / PDF 三种格式导出 |
| 🤖 AI 智能规划(预留) | 预留 AI 接口,后续可接入大模型生成计划/任务/卡片 |

> 📖 完整功能说明请参见 [FEATURES.md](FEATURES.md)

---

## 技术栈

### 前端

| 技术 | 说明 |
|------|------|
| **Vue 3** (Composition API) | 渐进式 JavaScript 框架 |
| **UniApp 3.0** | 跨端开发框架,一套代码 H5 / 小程序 / App 多端运行 |
| **Pinia** | Vue 3 官方状态管理 |
| **SCSS** | CSS 预处理器 |
| **Vite 5** | 下一代前端构建工具 |

### 后端

| 技术 | 说明 |
|------|------|
| **FastAPI** | 高性能异步 Python Web 框架 |
| **SQLAlchemy 2.0** | Python ORM |
| **PostgreSQL** | 关系型数据库(本地 Docker / 云端 Supabase) |
| **JWT (python-jose)** | 无状态身份认证 |
| **bcrypt** | 密码哈希 |
| **腾讯云 COS** | 对象存储(图片) |
| **Mangum** | FastAPI → AWS Lambda / CloudBase Serverless 适配器 |

---

## 项目架构

```
┌──────────────────────────────────────────────────────────────┐
│              客户端(UniApp 多端)                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │  首页    │  │ 任务看板  │  │ 复习卡片  │  │ 个人中心  │   │
│   │  index   │  │  task    │  │  review  │  │ profile  │   │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│        └────────────┬┴──────────────┴────────────┘          │
│                Pinia Stores(user/plan/task/card/farm)        │
│                        │  uni.request                         │
│                API Client(client.js)                         │
└────────────────────────┬─────────────────────────────────────┘
                         │  HTTPS / REST
┌────────────────────────┴─────────────────────────────────────┐
│             服务端(FastAPI,多入口)                            │
│   ┌─────────────────────────────────────────────────────┐    │
│   │  本地开发:uvicorn main:app --port 8002              │    │
│   │  Vercel:    server/api/index.py  (Mangum)            │    │
│   │  CloudBase: server/index.py      (Mangum)            │    │
│   └─────────────────────────────────────────────────────┘    │
│   Routes: auth plans tasks cards mistakes farm focus upload subjects       │
│   Services: cos_service  memory(间隔记忆算法)                              │
│   Schemas: user plan task card mistake farm focus                          │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ↓                                 ↓
┌──────────────────┐         ┌─────────────────────┐
│  PostgreSQL      │         │  腾讯云 COS          │
│  本地 Docker     │         │  (图片对象存储)      │
│  云端 Supabase   │         │                     │
└──────────────────┘         └─────────────────────┘
```

### 数据流

```
用户操作 → Vue 组件 → Pinia Store → API Client
       → FastAPI Router → Service Layer → SQLAlchemy → PostgreSQL
       → 响应返回 → Store 更新 → 组件响应式渲染
```

### 间隔记忆复习算法

知识卡片采用三级掌握度体系(未掌握/较熟悉/已掌握),每级对应不同的复习间隔:

| 掌握程度 | 第1次 | 第2次 | 第3次 | 第4次 | 第5次 | 第6次+ | 长期 |
|---------|------|------|------|------|------|--------|------|
| 未掌握 | 1天 | 1天 | 2天 | 3天 | 5天 | 8天 | 30天 |
| 较熟悉 | 3天 | 5天 | 8天 | 14天 | 21天 | 30天 | - |
| 已掌握 | 7天 | 14天 | 30天 | 30天 | 30天 | 30天 | - |

**规则**:
- 复习时回答正确 → 掌握程度升一级
- 回答错误 → 降一级
- 下次复习日期 = 上次复习日期 + 对应天数

错题本采用连续正确次数体系:

| 连续正确次数 | 下次复习间隔 |
|------------|------------|
| 0次(刚做错) | 明天 |
| 第1次正确 | 1天后 |
| 第2次正确 | 3天后 |
| 第3次正确 | 7天后 |
| 第4次正确 | 14天后 |
| 第5次正确 | 30天后 |

**规则**:
- 做错时正确次数清零,错误次数+1
- 连续正确 ≥3 次 → 自动标记为"已掌握"

---

## 目录结构

```
StudyMate/
├── README.md                          # 本文档
├── FEATURES.md                        # 功能说明书
├── PROJECT_PLAN.md                    # 项目规划
├── docker-compose.yml                 # 本地 PostgreSQL
├── .gitignore
│
└── studymate/                         # 应用主目录
    ├── package.json                   # 前端依赖与脚本
    ├── vite.config.js                 # Vite 配置
    ├── vercel.json                    # Vercel 前端部署配置
    ├── manifest.json                  # UniApp 应用配置
    ├── index.html                     # H5 入口 HTML
    ├── _worker.js                     # Cloudflare Worker(API 代理到 Vercel 后端)
    ├── .env.example                   # 前端环境变量模板
    │
    ├── public/                         # 静态资源
    │   └── _redirects                 # SPA 路由重定向
    │
    ├── src/                           # 前端源码
    │   ├── App.vue                    # 根组件
    │   ├── main.js                    # 入口文件
    │   ├── pages.json                 # 页面路由 + TabBar
    │   ├── manifest.json              # UniApp 各端配置
    │   ├── env.d.ts
    │   │
    │   ├── pages/                     # 页面
    │   │   ├── index/index.vue        #   首页
    │   │   ├── auth/login.vue         #   登录
    │   │   ├── auth/register.vue      #   注册
    │   │   ├── plan/                  #   计划(target-setup/plan-overview/ai-plan)
    │   │   ├── daily/                 #   每日(task-board/pomodoro)
    │   │   ├── review/index.vue       #   复习(卡片+错题)
    │   │   ├── farm/farm.vue          #   学习农场
    │   │   ├── statistics/stats.vue   #   学习统计
    │   │   └── profile/               #   个人中心(profile/settings)
    │   │
    │   ├── stores/                    # Pinia 状态管理
    │   │   ├── user.js  plan.js  task.js  card.js  farm.js
    │   │
    │   ├── api/                       # API 请求封装
    │   │   ├── client.js              #   主请求实例(全部后端接口)
    │   │   ├── ai.js                  #   AI 接口(预留)
    │   │   └── supabase.js            #   Supabase 直连(可选)
    │   │
    │   ├── utils/                     # 工具
    │   │   ├── date.js                #   日期处理
    │   │   ├── storage.js             #   本地存储
    │   │   ├── upload.js              #   图片上传(COS + 压缩)
    │   │   └── export.js              #   CSV/Excel/PDF 导出
    │   │
    │   ├── styles/                    # 全局样式
    │   │   ├── variables.scss  mixins.scss  global.scss
    │   │
    │   └── static/icons/              # 图标资源
    │
    ├── server/                        # 后端服务(FastAPI,部署到 Vercel)
    │   ├── main.py                    # FastAPI 应用入口
    │   ├── config.py                  # 环境配置
    │   ├── database.py                # 数据库模型 + 连接
    │   ├── seed.py                    # 种子数据脚本
    │   ├── requirements.txt           # Python 依赖
    │   ├── vercel.json                # Vercel 后端部署配置
    │   ├── package.json
    │   ├── .env.example               # 后端环境变量模板
    │   │
    │   ├── api/                       # Serverless 入口
    │   │   └── index.py               #   Vercel Python Functions 入口
    │   │
    │   ├── routes/                    # API 路由
    │   │   ├── auth.py                #   认证(注册/登录/我)
    │   │   ├── plans.py               #   学习计划 CRUD
    │   │   ├── tasks.py               #   每日任务 + 完成/循环
    │   │   ├── cards.py               #   知识卡片 + 间隔记忆复习
    │   │   ├── mistakes.py            #   错题本 + 掌握度追踪
    │   │   ├── farm.py                #   学习农场(种植/浇水/施肥/收获)
    │   │   ├── focus.py               #   番茄钟记录 + 多维度统计
    │   │   ├── subjects.py            #   用户自定义科目
    │   │   └── upload.py              #   腾讯云 COS 预签名 URL
    │   │
    │   ├── schemas/                   # Pydantic 数据校验
    │   │   ├── user.py  plan.py  task.py
    │   │   ├── card.py  mistake.py  farm.py  focus.py
    │   │
    │   ├── services/                  # 业务逻辑层
    │   │   ├── ai_service.py          #   AI 多 provider(预留,默认 mock)
    │   │   ├── cos_service.py         #   腾讯云 COS
    │   │   └── memory.py              #   间隔记忆算法
    │   │
    │   └── docs/                      # 部署文档
    │       ├── deploy.md                    # 通用部署指引
    │       ├── deploy-dual-endpoint.md      # H5+小程序双端部署教学
    │       ├── cloudbase-deploy.md          # CloudBase 云函数部署教程
    │       ├── cloud-deploy-readiness.md    # 云部署准备清单
    │       ├── cloudflare-vercel-deploy.md   # Cloudflare + Vercel 部署指南
    │       └── features.md                  # 功能说明
    │
    └── docs/                          # (旧文档)
```

---

## 快速开始

### 环境要求

- **Node.js** >= 18 + npm >= 9
- **Python** >= 3.10
- **Docker** + Docker Compose(可选,用于本地 PostgreSQL)

### 1. 克隆项目

```bash
git clone https://github.com/hazaban/StudyMate.git
cd StudyMate
```

### 2. 启动数据库(二选一)

**方式 A:Docker PostgreSQL(推荐)**

```bash
docker compose up -d
# 数据库在 localhost:5433,用户 studymate / 密码 studymate123 / 库 studymate
```

**方式 B:用云端 Supabase**

跳过本步,在下一步 `.env` 里把 `DATABASE_URL` 改成 Supabase 连接串即可。

### 3. 启动后端

```bash
cd studymate/server
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # 按需修改里面的值
python seed.py                                         # 初始化表结构 + 种子数据(可选)
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

后端启动后访问:
- API 根:http://localhost:8002
- Swagger 文档:http://localhost:8002/docs
- 健康检查:http://localhost:8002/health

### 4. 启动前端

```bash
cd studymate
npm install
npm run dev:h5
```

打开 http://localhost:5173 即可使用。Vite 已配置 `/api` 代理到 `localhost:8002`,前后端自动联通。

**测试账号**(执行过 `seed.py` 后可用):
- 邮箱:`test@studymate.com`
- 密码:`123456`

### 5. 服务总览

| 服务 | 地址 |
|------|------|
| Docker PostgreSQL | `localhost:5433` |
| FastAPI 后端 | `http://localhost:8002` |
| Swagger API 文档 | `http://localhost:8002/docs` |
| UniApp H5 前端 | `http://localhost:5173` |

---

## 环境变量配置

### 前端(`studymate/.env`)

```ini
# 后端 API 地址(本地开发留空走 Vite 代理;生产填完整域名)
VITE_API_BASE_URL=https://你的后端域名/api
```

### 后端(`studymate/server/.env`)

```ini
# ===== 数据库(必填)=====
DATABASE_URL=postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres
DB_SSLMODE=require

# ===== JWT(必填,生产环境务必改)=====
SECRET_KEY=openssl rand -hex 32 生成
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ===== CORS(生产建议填具体域名)=====
CORS_ORIGINS=*

# ===== AI(预留,暂未启用,不配则走 mock)=====
# HUNYUAN_API_KEY=
# HUNYUAN_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
# HUNYUAN_MODEL=hunyuan-pro
# DEEPSEEK_API_KEY=
# DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# ===== 腾讯云 COS(可选,不配则图片存 base64)=====
COS_SECRET_ID=
COS_SECRET_KEY=
COS_BUCKET=
COS_REGION=ap-guangzhou
```

---

## API 文档

启动后端后访问 http://localhost:8002/docs 查看完整 Swagger 文档。

### 主要 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| GET/POST | `/api/plans` | 学习计划列表 / 创建 |
| GET/POST | `/api/tasks` | 任务列表 / 创建 |
| POST | `/api/tasks/{id}/complete` | 完成任务 |
| GET/POST | `/api/cards` | 卡片列表 / 创建 |
| GET | `/api/cards/pending` | 今日待复习卡片 |
| POST | `/api/cards/{id}/review` | 提交卡片复习结果 |
| GET/POST | `/api/mistakes` | 错题列表 / 创建 |
| POST | `/api/mistakes/{id}/review` | 提交错题复习结果 |
| GET | `/api/farm` | 农场状态 |
| POST | `/api/farm/plants/{id}/water` | 浇水 |
| POST | `/api/farm/plants/{id}/harvest` | 收获 |
| GET/POST | `/api/focus` | 番茄记录列表 / 创建 |
| GET | `/api/focus/stats` | 番茄统计(总览) |
| GET | `/api/focus/stats/subject` | 按科目统计 |
| GET | `/api/focus/stats/daily` | 按日统计 |
| GET/POST | `/api/subjects` | 自定义科目列表 / 添加 |
| POST | `/api/upload/sts` | 获取 COS 上传凭证 |

---

## 部署方案

### 🏆 当前生产部署方案:Cloudflare Pages + Vercel + Supabase + 腾讯云 COS

当前线上生产环境采用以下架构,**国内访问稳定、无需代理**:

| 组件 | 平台 | 费用 | 说明 |
|------|------|------|------|
| 前端 H5 | **Cloudflare Pages** | 免费 | 全球 CDN,国内访问快,自动部署 |
| 后端 API | **Vercel** | 免费 | FastAPI Serverless,自动扩缩容 |
| 数据库 | **Supabase** | 免费 | PostgreSQL,500MB 空间 |
| 图片存储 | **腾讯云 COS** | 免费额度 | 6个月50GB,之后几元/月 |
| API 代理 | **Cloudflare Worker** | 免费 | 内置在 Pages 中,绕过 Vercel 国内 DNS 污染 |

**架构图:**

```
用户手机/电脑(国内网络)
    │
    ▼
Cloudflare Pages 前端(静态 H5 + _worker.js)
    │
    ├── 静态资源 ──► Cloudflare CDN(国内节点)
    │
    └── /api/* 请求 ──► _worker.js 代理
                            │
                            ▼
                       Vercel 后端(FastAPI)
                            │
                            ├──► 腾讯云 COS(图片)
                            │
                            └──► Supabase PostgreSQL(数据库)
```

**为什么用 Cloudflare Pages 前端 + Vercel 后端?**

| 问题 | 解决方案 |
|------|----------|
| Vercel 国内访问不稳定 | 前端放 Cloudflare Pages,国内 CDN 节点速度快 |
| Vercel 国内 DNS 污染 | API 请求通过 Cloudflare Worker 代理转发,绕过污染 |
| 全放在 Cloudflare | Cloudflare Pages 不能直接跑 Python/FastAPI |
| 全放在 Vercel | 国内访问慢甚至打不开 |

> 💡 **关键技术**:前端通过 `_worker.js`(Cloudflare Worker)将所有 `/api/*` 请求代理到 Vercel 后端,前端代码无需改动,国内用户访问 Cloudflare 域名即可正常使用。

**为什么前端从 Vercel 迁移到 Cloudflare?**

最初前端和后端都部署在 Vercel,但 Vercel 在国内存在 DNS 污染问题,导致手机端和部分网络环境下无法访问。迁移到 Cloudflare Pages 后,前端静态资源走 Cloudflare 国内 CDN 节点,API 请求通过 Worker 代理,国内访问体验大幅提升。

### 详细部署步骤

📖 完整部署文档请查看:[**studymate/docs/cloudflare-vercel-deploy.md**](studymate/docs/cloudflare-vercel-deploy.md)

包含从零开始的每一步操作:Supabase 数据库创建、腾讯云 COS 配置、Vercel 后端部署、Cloudflare Pages 前端部署、_worker.js 代理配置、常见问题排查。

---

### 其他部署方案参考

#### 方案对比

| 方案 | 优点 | 缺点 | 适合 |
|------|------|------|------|
| **Cloudflare + Vercel** ⭐ | 国内访问快,全免费,自动部署 | 两个平台管理 | 国内用户,个人使用 |
| **全 Vercel** | 一个平台管理 | 国内访问不稳定,需要代理 | 海外用户 |
| **全 Render** | 一个平台管理,无函数超时 | 国内访问慢,免费版休眠 | 追求简单,海外用户 |
| **全腾讯云** | 国内速度最快 | 要花钱(约50元/月) | 预算充足,企业级 |

#### 端侧落地方式

| 端 | 平台 | 部署方式 | 成本 |
|----|------|----------|------|
| 手机端 | H5 Web | Cloudflare Pages / 腾讯云 COS | 免费~几十元/月 |
| 手机端 | 微信小程序 | 微信公众平台 | 免费 |
| 电脑端 | H5 Web | 同手机端 | 已包含 |

**电脑端使用:** H5 版本天然支持 PC 浏览器访问,无需额外开发。UniApp 的 H5 模式在 PC 上会自动适配为宽屏布局。

**手机端使用:** 通过 H5 链接或微信小程序扫码即可使用,无需安装 App。

---

## 开发指南

### 添加新页面

1. 在 `src/pages/` 下创建 `.vue` 文件
2. 在 `src/pages.json` 的 `pages` 数组中注册
3. TabBar 页面需在 `tabBar.list` 中配置

### 添加新 API

1. 在 `server/routes/` 下创建路由文件
2. 在 `server/main.py` 中 `include_router`
3. 在 `src/api/client.js` 中封装前端请求方法
4. 在 `src/stores/` 中创建对应 Pinia Store

### 数据库迁移

修改 `server/database.py` 模型后:

```bash
cd studymate/server
python -c "from database import init_db; init_db()"
# 或手动 ALTER TABLE
```

### 代码规范

- 前端:Vue 3 Composition API + `<script setup>` 语法
- 后端:FastAPI 路由 + Pydantic Schema 校验
- 命名:文件 kebab-case,组件 PascalCase,函数 camelCase

---

## 常见问题

### 端口占用

```bash
# macOS / Linux
lsof -ti :8002 | xargs kill -9
lsof -ti :5173 | xargs kill -9

# Windows PowerShell
netstat -ano | findstr :8002
taskkill //F //PID <PID>
```

### 重置数据

```bash
cd studymate/server
python seed.py        # 清空旧数据 + 重新创建种子数据
```

### AI 接口返回 mock 数据

后端没配置 AI API Key,默认走 mock 模式。如需启用真实 AI,在 `.env` 里填入 `HUNYUAN_API_KEY` 或 `DEEPSEEK_API_KEY` 即可。

### 图片上传失败

检查腾讯云 COS 配置(`COS_SECRET_ID` / `COS_SECRET_KEY` / `COS_BUCKET` / `COS_REGION`)是否完整,以及 COS 存储桶的 CORS 跨域规则。

---

## License

MIT License

---

<p align="center">
  Made with ❤️ for learners everywhere
</p>

# StudyMate 学习星球

<p align="center">
  <strong style="font-size:1.15em">AI 抗遗忘备考工具 —— 让知识进脑子,而不是走过场</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vuedotjs" alt="Vue" />
  <img src="https://img.shields.io/badge/UniApp-3.0-2B9939?logo=uni-app" alt="UniApp" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Hunyuan-AI-3F87FF?logo=tencentqq" alt="Hunyuan" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License" />
</p>

---

## 项目简介

StudyMate 学习星球是一款面向考研/考公/考证备考人群的 **AI 抗遗忘学习工具**。结合**艾宾浩斯遗忘曲线**科学复习调度、**番茄钟专注计时**、**游戏化学习农场**和 **AI 智能规划**四大核心能力,帮助你:

- 📋 制定多科备考计划,按科目 + 章节拆分到每天
- 🍅 番茄钟计时,自动记录实际学习时长
- 🧠 知识卡片 + 错题本按记忆曲线自动安排复习
- 🤖 AI 生成学习计划 / 每日任务 / 复习卡片 / 教材目录识别
- 🌱 完成学习即可种植作物,游戏化激励持续学习
- 📊 学习时长、番茄数、科目分布多维度统计

**电脑端 + 手机端通用**:H5 网页(Vercel)+ 微信小程序(后续),一套 UniApp 代码多端运行,同一账号数据互通。

---

## 核心功能

| 模块 | 说明 |
|------|------|
| 📋 智能任务管理 | 创建学习计划,按天拆解任务,支持新学/复习/错题三类 + 循环任务 |
| 🧠 知识卡片 + 艾宾浩斯复习 | 文字 + 图片混合卡片,自动按遗忘曲线推算复习日期 |
| ❌ 错题本 + 掌握度追踪 | 记录错题(文字+图片),连续做对 2 次标记"已掌握" |
| 🍅 番茄钟专注计时 | 自定义专注/休息时长,完成后自动写入数据库,支持手动补录 |
| 🌱 游戏化学习农场 | 完成任务/番茄自动浇水施肥,植物从种子到收获,赚金币升级 |
| 📊 学习统计看板 | 总时长、番茄数、任务完成率、科目分布、趋势图表、成就徽章 |
| 🤖 AI 智能规划 | 腾讯混元大模型生成计划/任务/卡片,通义千问识别教材目录图片 |
| 📷 图片上传 | 腾讯云 COS 直传 + base64 数据库存储双模式,支持拍照/相册/粘贴 |
| 📤 数据导出 | 卡片/错题支持 CSV / Excel / PDF 三种格式导出 |

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
| **腾讯混元 API** | 主 AI 大模型(兼容 OpenAI 协议) |
| **通义千问 Vision** | 图片识别(教材目录) |
| **DeepSeek API** | 备用 AI(可选) |
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
│   Routes: auth plans tasks cards mistakes farm ai upload      │
│          focus subjects                                       │
│   Services: ai_service(混元/DeepSeek/mock)  cos_service       │
│             memory(艾宾浩斯算法)                              │
│   Schemas: user plan task card mistake farm focus             │
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

### 艾宾浩斯复习算法

```
复习间隔: [1天, 3天, 7天, 14天, 30天]
第1次做对 → 1天后复习
第2次做对 → 3天后复习
...
第6次做对 → 标记"已掌握"
做错 → correct_count 清零,重新从第1天开始
```

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
└── studymate-uniapp/                  # 应用主目录
    ├── package.json                   # 前端依赖与脚本
    ├── vite.config.js                 # Vite 配置(/api 代理到 8002)
    ├── vercel.json                    # Vercel 前端部署配置
    ├── manifest.json                  # UniApp 应用配置
    ├── index.html                     # H5 入口 HTML
    ├── .env.example                   # 前端环境变量模板
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
    │   │   ├── ai.js                  #   AI 接口
    │   │   └── supabase.js            #   Supabase 直连(可选)
    │   │
    │   ├── utils/                     # 工具
    │   │   ├── date.js                #   日期处理
    │   │   ├── storage.js             #   本地存储
    │   │   ├── upload.js              #   图片上传(COS/base64)
    │   │   └── export.js              #   CSV/Excel/PDF 导出
    │   │
    │   ├── styles/                    # 全局样式
    │   │   ├── variables.scss  mixins.scss  global.scss
    │   │
    │   └── static/icons/              # 图标资源
    │
    └── server/                        # 后端服务
        ├── main.py                    # FastAPI 应用入口
        ├── index.py                   # CloudBase 云函数入口(Mangum)
        ├── config.py                  # 环境配置(多 provider AI)
        ├── database.py                # 数据库模型 + 连接
        ├── seed.py                    # 种子数据脚本
        ├── requirements.txt           # Python 依赖
        ├── runtime.txt                # Python 版本(Vercel)
        ├── vercel.json                # Vercel 后端部署配置
        ├── package.json
        ├── .env.example               # 后端环境变量模板
        │
        ├── api/                       # Serverless 入口
        │   └── index.py               #   Vercel Python Functions 入口
        │
        ├── routes/                    # API 路由(10 个模块)
        │   ├── auth.py                #   认证(注册/登录/我)
        │   ├── plans.py               #   学习计划 CRUD + AI 生成
        │   ├── tasks.py               #   每日任务 + AI 生成 + 完成/循环
        │   ├── cards.py               #   知识卡片 + 艾宾浩斯复习
        │   ├── mistakes.py            #   错题本 + 掌握度追踪
        │   ├── farm.py                #   学习农场(种植/浇水/施肥/收获)
        │   ├── focus.py               #   番茄钟记录 + 多维度统计
        │   ├── ai.py                  #   AI 接口(计划/任务/卡片/复习/目录)
        │   ├── subjects.py            #   用户自定义科目
        │   └── upload.py              #   腾讯云 COS STS 凭证
        │
        ├── schemas/                   # Pydantic 数据校验
        │   ├── user.py  plan.py  task.py
        │   ├── card.py  mistake.py  farm.py  focus.py
        │
        ├── services/                  # 业务逻辑层
        │   ├── ai_service.py          #   AI 多 provider(混元/DeepSeek/mock)
        │   ├── cos_service.py         #   腾讯云 COS STS
        │   └── memory.py              #   艾宾浩斯遗忘曲线算法
        │
        └── docs/                      # 部署文档
            ├── deploy.md                    # 通用部署指引
            ├── deploy-dual-endpoint.md      # H5+小程序双端部署教学
            ├── cloudbase-deploy.md          # CloudBase 云函数部署教程
            ├── cloud-deploy-readiness.md    # 云部署准备清单
            └── features.md                  # (旧版功能说明,已被根目录 FEATURES.md 替代)
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
cd studymate-uniapp/server
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
cd studymate-uniapp
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

### 前端(`studymate-uniapp/.env`)

```ini
# 后端 API 地址(本地开发留空走 Vite 代理;生产填完整域名)
VITE_API_BASE_URL=https://你的后端域名/api
```

### 后端(`studymate-uniapp/server/.env`)

```ini
# ===== 数据库(必填)=====
DATABASE_URL=postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres
DB_SSLMODE=require

# ===== JWT(必填,生产环境务必改)=====
SECRET_KEY=openssl rand -hex 32 生成
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ===== CORS(生产建议填具体域名)=====
CORS_ORIGINS=*

# ===== AI(三选一,不配则走 mock)=====
# 推荐:腾讯混元(可配合 CloudBase 1亿 Token 福利)
HUNYUAN_API_KEY=
HUNYUAN_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
HUNYUAN_MODEL=hunyuan-pro

# 备选:DeepSeek
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 图片识别(可选)
QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_VISION_MODEL=qwen-vl-max

# ===== 腾讯云 COS(可选,不配则图片存 base64)=====
COS_SECRET_ID=
COS_SECRET_KEY=
COS_BUCKET=
COS_REGION=ap-guangzhou
```

> AI Provider 自动选择优先级:`HUNYUAN_API_KEY` > `DEEPSEEK_API_KEY` > mock。也可通过环境变量 `AI_PROVIDER=hunyuan|deepseek|mock` 强制指定。

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
| POST | `/api/plans/ai/generate` | AI 生成学习计划 |
| GET/POST | `/api/tasks` | 任务列表 / 创建 |
| POST | `/api/tasks/{id}/complete` | 完成任务 |
| POST | `/api/tasks/ai/generate` | AI 生成今日任务 |
| GET/POST | `/api/cards` | 卡片列表 / 创建 |
| GET | `/api/cards/pending` | 今日待复习卡片 |
| POST | `/api/cards/{id}/review` | 提交卡片复习结果 |
| POST | `/api/cards/ai/generate` | AI 生成卡片 |
| GET/POST | `/api/mistakes` | 错题列表 / 创建 |
| POST | `/api/mistakes/{id}/review` | 提交错题复习结果 |
| GET | `/api/farm` | 农场状态 |
| POST | `/api/farm/plants/{id}/water` | 浇水 |
| POST | `/api/farm/plants/{id}/harvest` | 收获 |
| GET/POST | `/api/focus` | 番茄记录列表 / 创建 |
| GET | `/api/focus/stats` | 番茄统计(总览) |
| GET | `/api/focus/stats/subject` | 按科目统计 |
| GET | `/api/focus/stats/daily` | 按日统计 |
| POST | `/api/ai/review` | AI 生成每日复盘 |
| POST | `/api/ai/syllabus` | AI 识别教材目录图片 |
| POST | `/api/upload/sts` | 获取 COS 上传凭证 |

---

## 部署方案

### 当前已部署:Vercel(前端 + 后端)

前端和后端都部署在 Vercel:
- **前端**:H5 静态站点,从 `studymate-uniapp/` 构建,产物 `dist/build/h5`
- **后端**:Vercel Python Serverless Functions,入口 [server/api/index.py](studymate-uniapp/server/api/index.py),用 Mangum 适配
- **数据库**:Supabase PostgreSQL
- **图片**:腾讯云 COS(可选)

> ⚠️ Vercel Python Serverless 有 10 秒超时硬限制,AI 接口可能超时。如需长超时,建议迁移后端到 CloudBase 或云服务器。

### 后续规划:CloudBase 云函数 + 小程序

利用微信「AI 小程序成长计划」福利:
- 6 个月免费 CloudBase 环境(部署后端)
- 1 亿混元 Token(AI 接口)
- 1 万张混元文生图

详细教程:
- [docs/deploy-dual-endpoint.md](studymate-uniapp/docs/deploy-dual-endpoint.md) — H5 + 小程序双端部署完整教学
- [docs/cloudbase-deploy.md](studymate-uniapp/docs/cloudbase-deploy.md) — CloudBase 云函数部署教程

### 后续规划:云服务器

迁移到腾讯云轻量服务器(60-100 元/年),Docker Compose 一键拉起 Nginx + FastAPI + PostgreSQL,最稳定最便宜。

### 多端访问

| 端 | 平台 | 状态 |
|----|------|------|
| 电脑网页 | H5(Vercel) | ✅ 已部署 |
| 手机网页 | H5(Vercel,加主屏幕) | ✅ 已部署 |
| 微信小程序 | mp-weixin | ⏳ 规划中 |
| Android/iOS App | app-plus | ⏳ 可选 |

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
cd studymate-uniapp/server
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
cd studymate-uniapp/server
python seed.py        # 清空旧数据 + 重新创建种子数据
```

### AI 接口返回 mock 数据

后端没配 `HUNYUAN_API_KEY` 或 `DEEPSEEK_API_KEY`,自动走 mock 模式。在 `.env` 里填入任一 API Key 即可启用真实 AI。

### 图片上传失败

检查腾讯云 COS 配置(`COS_SECRET_ID` / `COS_SECRET_KEY` / `COS_BUCKET` / `COS_REGION`)是否完整,以及 COS 存储桶的 CORS 跨域规则。

---

## License

MIT License

---

<p align="center">
  Made with ❤️ for learners everywhere
</p>

# StudyMate 学习星球

<p align="center">
  <strong style="font-size:1.15em">AI 抗遗忘备考工具 —— 让知识进脑子，而不是走过场</strong>
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

StudyMate 学习星球是一款面向考研/考公/考证备考人群的 **AI 抗遗忘学习工具**。结合**智谱 GLM AI 规划**、**科学间隔记忆复习调度**、**番茄钟专注计时**、**游戏化学习农场**四大核心能力。

- 📋 AI 智能规划：GLM-4.5-Air 生成学习计划、拆解每日任务、生成复习卡片
- 🖼️ AI 图片识别：GLM-4.1V-Thinking-FlashX 识别教材目录，自动提取章节
- 🍅 番茄钟计时：自定义专注/休息时长，自动记录实际学习时长到数据库
- 🧠 知识卡片 + 错题本：按记忆曲线自动安排复习时间，文字+图片混合卡片
- 🌱 游戏化学习农场：完成任务/番茄自动种植收割，赚金币升级
- 📊 学习统计看板：总时长、番茄数、科目分布、趋势图表

**电脑端 + 手机端通用**：H5 网页（Cloudflare Pages），一套 UniApp 代码多端运行，同一账号数据互通。

---

## 项目架构

```
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
```

### 目录结构

```
StudyMate/
├── README.md                    # 本文档
├── FEATURES.md                  # 详细功能说明书
├── PROJECT_PLAN.md              # 项目规划
├── docker-compose.yml           # 本地 PostgreSQL
├── docs/                        # 部署文档
│   ├── deploy.md
│   ├── cloudflare-vercel-deploy.md
│   └── cloudbase-deploy.md
├── frontend/                    # UniApp H5 前端（Cloudflare Pages）
│   ├── src/pages/               # 页面组件
│   │   ├── index/               #   首页
│   │   ├── auth/                #   登录/注册
│   │   ├── plan/                #   计划管理 + AI规划
│   │   ├── daily/               #   任务看板 + 番茄钟 + 四象限
│   │   ├── review/              #   复习（卡片+错题）
│   │   ├── farm/                #   学习农场
│   │   ├── statistics/          #   学习统计
│   │   └── profile/             #   个人中心
│   ├── src/stores/              # Pinia 状态管理
│   ├── src/api/                 # API 请求封装
│   ├── _worker.js               # Cloudflare Worker（API代理）
│   ├── vite.config.js
│   └── package.json
└── backend/                     # FastAPI 后端（Vercel）
    ├── main.py                  # 应用入口
    ├── config.py                # 环境配置（GLM/COS/JWT/DB）
    ├── database.py              # 数据模型（SQLAlchemy）
    ├── seed.py                  # 种子数据脚本
    ├── routes/                  # API 路由
    ├── services/                # AI + COS + Memory 服务
    ├── schemas/                 # Pydantic 校验
    └── pyproject.toml
```

---

## 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| **前端** | Vue 3 + UniApp 3.0 + Pinia + SCSS + Vite 5 | H5 响应式，一套代码多端 |
| **后端** | FastAPI + SQLAlchemy 2.0 + JWT + bcrypt | Python Serverless |
| **数据库** | PostgreSQL（Supabase 免费 500MB） | 云端托管 |
| **AI** | 智谱 GLM-4.5-Air / GLM-4.1V-Thinking-FlashX | 文本规划 + 图片识别 |
| **图片** | 腾讯云 COS（可选） | 对象存储 + CDN |
| **部署** | Cloudflare Pages + Vercel | 全免费自动部署 |

---

## AI 模型选型

| 场景 | 模型 | 特点 |
|------|------|------|
| 纯文本对话、工具调用、Agent | `glm-4.5-air` | 激活参少、便宜、速度快 |
| 传图 / 传视频 / GUI 理解 | `glm-4.1v-thinking-flashx` | 便宜、极速、多模态 |

申请地址：https://open.bigmodel.cn/

---

## 快速开始

### 环境要求

- **Node.js** >= 18 + npm >= 9
- **Python** >= 3.10
- **Docker** + Docker Compose（可选，用于本地 PostgreSQL）

### 1. 克隆项目

```bash
git clone https://github.com/hazaban/StudyMate.git
cd StudyMate
```

### 2. 启动数据库（二选一）

**方式 A：Docker PostgreSQL（推荐）**

```bash
docker compose up -d
# 数据库在 localhost:5433，用户 studymate / 密码 studymate123
```

**方式 B：云端 Supabase**

跳过本步，在 `.env` 里把 `DATABASE_URL` 改成 Supabase 连接串。

### 3. 启动后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # 按需修改
python seed.py                                       # 初始化表 + 种子数据
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

后端启动后访问：
- API 根：http://localhost:8002
- Swagger 文档：http://localhost:8002/docs
- 健康检查：http://localhost:8002/health

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev:h5
```

打开 http://localhost:5173 即可使用。Vite 已配置 `/api` 代理到 `localhost:8002`。

**测试账号**（执行过 `seed.py` 后可用）：
- 邮箱：`test@studymate.com` / 密码：`123456`

---

## 环境变量配置

### 后端（`backend/.env`）

```ini
# 数据库（必填）
DATABASE_URL=postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres
DB_SSLMODE=require

# JWT（必填，生产务必改成随机字符串）
SECRET_KEY=openssl rand -hex 32 生成
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 智谱 GLM AI（https://open.bigmodel.cn/ 申请）
GLM_API_KEY=
GLM_TEXT_MODEL=glm-4.5-air
GLM_VISION_MODEL=glm-4.1v-thinking-flashx

# 腾讯云 COS（可选，不配则图片存base64）
COS_SECRET_ID=  COS_SECRET_KEY=  COS_BUCKET=  COS_REGION=ap-guangzhou
```

---

## 部署方案

### 当前生产部署：Cloudflare Pages + Vercel + Supabase

| 组件 | 平台 | 费用 |
|------|------|------|
| 前端 H5 | **Cloudflare Pages**（`frontend/`） | 免费 |
| 后端 API | **Vercel**（`backend/`） | 免费 |
| 数据库 | **Supabase** | 免费 500MB |
| 图片存储 | **腾讯云 COS** | 免费额度 |
| API 代理 | **Cloudflare Worker**（`_worker.js`） | 免费 |

**为什么用 Cloudflare 前端 + Vercel 后端？**

Vercel 在国内有 DNS 污染问题。前端放 Cloudflare Pages 走国内 CDN，API 请求通过 `_worker.js` 代理转发到 Vercel 后端，绕过污染。

---

## API 文档

启动后端后访问 http://localhost:8002/docs 查看 Swagger。

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET/POST | `/api/plans` | 计划列表 / 创建 |
| GET/POST | `/api/tasks` | 任务列表 / 创建 |
| POST | `/api/tasks/{id}/complete` | 完成任务 |
| GET/POST | `/api/cards` | 卡片列表 / 创建 |
| POST | `/api/cards/{id}/review` | 提交复习结果 |
| GET/POST | `/api/mistakes` | 错题列表 / 创建 |
| GET/POST | `/api/focus` | 番茄记录列表 / 创建 |
| GET | `/api/focus/stats` | 番茄统计 |
| POST | `/api/plans/ai/generate` | AI 生成计划 |
| POST | `/api/tasks/ai/generate` | AI 生成任务 |
| POST | `/api/cards/ai/generate` | AI 生成卡片 |
| POST | `/api/ai/review` | AI 每日复盘 |
| POST | `/api/ai/syllabus` | AI 识别教材目录 |

---

## License

MIT

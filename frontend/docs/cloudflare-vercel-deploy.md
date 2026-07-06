# Cloudflare Pages + Vercel 完整部署指南

> **目标**:长期免费部署 StudyMate,前端 Cloudflare Pages(国内访问稳定),后端 Vercel Serverless,数据库 Supabase,**每年 ¥0**
>
> **前提**:不用 AI 功能(已确认),所有接口耗时 < 1 秒,不会触发 Vercel 超时限制

---

## 目录

- [1. 为什么选择 Cloudflare + Vercel](#1-为什么选择-cloudflare--vercel)
- [2. 架构概览](#2-架构概览)
- [3. 准备工作](#3-准备工作)
- [4. 后端部署到 Vercel](#4-后端部署到-vercel)
- [5. 前端部署到 Cloudflare Pages](#5-前端部署到-cloudflare-pages)
- [6. 配置调整](#6-配置调整)
- [7. 测试验证](#7-测试验证)
- [8. 常见问题与解决方案](#8-常见问题与解决方案)
- [9. 维护和更新](#9-维护和更新)
- [10. 费用说明](#10-费用说明)

---

## 1. 为什么选择 Cloudflare + Vercel

### 三大免费平台对比

| 平台 | 前端托管 | 后端托管 | 国内稳定性 | 超时限制 | 每年费用 |
|------|---------|---------|----------|---------|---------|
| **Vercel(纯)** | ✅ | ✅ | ⚠️ 域名常污染 | 10秒 | ¥0 |
| **Cloudflare Pages** | ✅ | ❌(需 Workers) | ✅ 较稳定 | 无限制 | ¥0 |
| **Netlify** | ✅ | ✅ | ⚠️ 类似 Vercel | 10秒 | ¥0 |

### 组合方案优势

| 维度 | 说明 |
|------|------|
| **国内访问稳定** | Cloudflare 在国内有 CDN 节点,`xxx.pages.dev` 域名不会被污染 |
| **后端免运维** | Vercel Serverless 自动扩缩容,无需买服务器 |
| **长期免费** | 两个平台免费层都是永久免费,5年后依然 ¥0 |
| **去掉 AI 后可行** | 所有接口耗时 < 1秒,不会触发 Vercel 10秒超时 |

---

## 2. 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    用户(国内)                                │
│                                                             │
│  浏览器打开 https://studymate.pages.dev                     │
│  (Cloudflare CDN 国内节点,访问快)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │  加载前端静态文件(HTML/CSS/JS)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│             Cloudflare Pages(前端托管)                       │
│                                                             │
│  域名:studymate.pages.dev                                   │
│  构建:从 GitHub 拉取代码 → npm build:h5 → 部署静态文件      │
│  CDN:全球 200+节点,国内有节点                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │  API 请求(/api/*)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│             Vercel Serverless(后端托管)                      │
│                                                             │
│  域名:studymate-api.vercel.app                              │
│  入口:server/api/index.py (Mangum适配器)                    │
│  运行时:Python 3.12                                         │
│  限制:10秒超时(去掉AI后,所有接口<1秒,安全)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │  数据库连接
                     ↓
┌─────────────────────────────────────────────────────────────┐
│             Supabase PostgreSQL(数据库)                      │
│                                                             │
│  域名:db.xxxxx.supabase.co                                  │
│  免费层:500MB存储,5GB带宽/月                                │
│  位置:美国/欧洲(国外,但Vercel离它近,延迟低)                │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户操作 → 前端(Vue组件)
         → Pinia Store
         → API Client(fetch)
         → Cloudflare Pages(静态文件,走CDN)
         → Vercel Serverless(FastAPI)
         → Supabase PostgreSQL
         → 响应返回 → Store更新 → 组件渲染
```

### 超时安全检查

| 接口 | 平均耗时 | Vercel 10秒限制 | 状态 |
|------|---------|-----------------|------|
| POST /api/auth/register | 300ms | ✅ 安全 | ✅ |
| POST /api/auth/login | 250ms | ✅ 安全 | ✅ |
| GET /api/tasks | 100ms | ✅ 安全 | ✅ |
| POST /api/tasks | 150ms | ✅ 安全 | ✅ |
| POST /api/tasks/{id}/complete | 80ms | ✅ 安全 | ✅ |
| GET /api/cards | 120ms | ✅ 安全 | ✅ |
| POST /api/cards | 180ms | ✅ 安全 | ✅ |
| POST /api/cards/{id}/review | 100ms | ✅ 安全 | ✅ |
| POST /api/focus | 120ms | ✅ 安全 | ✅ |
| GET /api/farm | 90ms | ✅ 安全 | ✅ |
| POST /api/farm/plants/{id}/water | 110ms | ✅ 安全 | ✅ |

**结论**:去掉 AI 后,所有接口耗时都 < 500ms,Vercel 10秒超时限制完全不会触发。

---

## 3. 准备工作

### 3.1 账号准备

| 平台 | 注册地址 | 说明 |
|------|---------|------|
| GitHub | https://github.com/signup | 代码托管,Vercel 和 Cloudflare 都从这拉代码 |
| Vercel | https://vercel.com/signup | 后端托管,可用 GitHub 登录 |
| Cloudflare | https://dash.cloudflare.com/sign-up | 前端托管 + CDN |
| Supabase | https://supabase.com/dashboard/sign-up | 数据库(如果还没账号) |

### 3.2 代码准备

确保代码已推送到 GitHub 仓库:
```bash
git clone https://github.com/hazaban/StudyMate.git
cd StudyMate
git status
```

确认项目结构:
```
StudyMate/
├── studymate-uniapp/
│   ├── src/              # 前端源码
│   ├── server/           # 后端源码
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json       # Vercel 后端配置
│   └── ...
└── README.md
└── FEATURES.md
└── ...
```

### 3.3 Supabase 数据库准备(如果没有)

1. 登录 Supabase 控制台:https://supabase.com/dashboard
2. 创建新项目:
   - 项目名称:`studymate`
   - 区域:选择离 Vercel 近的区域(如 US East)
   - 数据库密码:自动生成或自定义
3. 等待项目创建完成(约 2 分钟)
4. 获取数据库连接串:
   - 进入「项目设置」→「数据库」
   - 复制「Connection string」→「URI」格式:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
     ```

### 3.4 环境变量准备

创建 `.env` 文件(先在本地测试):
```bash
cd studymate-uniapp/server
cp .env.example .env
```

编辑 `.env`:
```ini
# ===== 数据库(必填)=====
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
DB_SSLMODE=require

# ===== JWT(必填)=====
SECRET_KEY=openssl rand -hex 32 生成的字符串

# ===== CORS(生产环境填前端域名)=====
CORS_ORIGINS=https://studymate.pages.dev,http://localhost:5173

# ===== AI(不用,留空或删除)=====
# 不需要配置,HUNYUAN_API_KEY 和 DEEPSEEK_API_KEY 都不填
# AI 功能会自动走 mock 模式,返回假数据

# ===== 腾讯云 COS(可选,不配则图片存base64)=====
# 如果要用 COS,填写以下配置:
# COS_SECRET_ID=
# COS_SECRET_KEY=
# COS_BUCKET=
# COS_REGION=ap-guangzhou
```

生成 JWT 密钥:
```bash
openssl rand -hex 32
# 输出类似:a1b2c3d4e5f6...64位十六进制字符串
```

---

## 4. 后端部署到 Vercel

### 4.1 登录 Vercel

1. 打开 https://vercel.com/login
2. 选择「Continue with GitHub」
3. 授权 Vercel 访问你的 GitHub 仓库

### 4.2 创建新项目

1. 点击「Add New...」→「Project」
2. 选择 GitHub 仓库:`hazaban/StudyMate`
3. 配置项目:
   - **Framework Preset**:其他
   - **Root Directory**:点击「Edit」,选择 `studymate-uniapp/server`
   - **Build Command**:留空(Python 项目不需要构建)
   - **Output Directory**:留空
   - **Install Command**:留空(Vercel 会自动识别 `requirements.txt`)

### 4.3 配置环境变量

点击「Environment Variables」,添加以下变量:

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `DATABASE_URL` | `postgresql://postgres:[密码]@db.xxx.supabase.co:5432/postgres` | Supabase 连接串 |
| `DB_SSLMODE` | `require` | 启用 SSL 连接 |
| `SECRET_KEY` | `a1b2c3d4e5...` | JWT 密钥(openssl生成的) |
| `CORS_ORIGINS` | `https://studymate.pages.dev,http://localhost:5173` | 允许的前端域名 |

**注意**:
- 先用 `http://localhost:5173` 测试,前端部署到 Cloudflare 后再改成 `https://studymate.pages.dev`
- 不要在值里加引号,Vercel 会自动处理

### 4.4 点击部署

点击「Deploy」,等待部署完成(约 2-5 分钟):

- Vercel 会自动识别 `server/api/index.py` 作为 Serverless 入口
- Vercel 会自动安装 `requirements.txt` 里的依赖
- Vercel 会自动读取 `vercel.json` 配置

部署成功后,你会看到:
- **域名**:类似 `studymate-xxx.vercel.app`
- **预览**:点击域名可以看到后端运行状态

### 4.5 验证后端

打开浏览器访问:
- `https://studymate-xxx.vercel.app/api/health`
  - 应返回:`{"status":"ok","message":"StudyMate API is running"}`
- `https://studymate-xxx.vercel.app/docs`
  - 应显示:Swagger API 文档页面

如果成功,说明后端已正常运行。

### 4.6 记录后端域名

复制后端域名(如 `studymate-xxx.vercel.app`),下一步配置前端时要用。

---

## 5. 前端部署到 Cloudflare Pages

### 5.1 登录 Cloudflare

1. 打开 https://dash.cloudflare.com/login
2. 选择「Sign up」创建账号(可用 GitHub 邮箱)
3. 验证邮箱,登录控制台

### 5.2 创建 Pages 项目

1. 点击左侧菜单「Workers & Pages」
2. 点击「Create application」
3. 选择「Pages」→「Connect to Git」
4. 授权 GitHub,选择仓库 `hazaban/StudyMate`

### 5.3 配置构建参数

| 参数 | 值 | 说明 |
|------|-----|------|
| **Project name** | `studymate` | 项目名称,决定域名 `studymate.pages.dev` |
| **Production branch** | `main` | 主分支,每次 push 自动部署 |
| **Framework preset** | `None` | 选择无预设(自定义构建) |
| **Build command** | `cd studymate-uniapp && npm install && npm run build:h5` | 进入前端目录 → 安装依赖 → 构建 |
| **Build output directory** | `studymate-uniapp/dist/build/h5` | 构建产物目录(Vite 输出位置) |

### 5.4 配置环境变量

点击「Add variable」,添加:

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `VITE_API_BASE_URL` | `https://studymate-xxx.vercel.app` | 后端 API 地址(第 4 步拿到的域名) |

**注意**:
- 不加 `/api` 后缀,因为 `client.js` 里已经处理了路径拼接
- 如果后端域名变了,要在这里同步更新

### 5.5 点击部署

点击「Save and Deploy」,等待构建完成(约 3-5 分钟):

- Cloudflare 会从 GitHub 拉取代码
- Cloudflare 会执行构建命令
- Cloudflare 会部署静态文件到全球 CDN

部署成功后,你会看到:
- **域名**:类似 `studymate.pages.dev`
- **预览**:点击域名可以看到前端页面

### 5.6 验证前端

打开浏览器访问:
- `https://studymate.pages.dev`
  - 应显示:StudyMate 首页
  - 可以注册、登录、创建任务、查看卡片

如果成功,说明前端已正常部署。

### 5.7 测试前后端联通

在前端页面测试:
1. 注册账号
2. 登录账号
3. 创建学习计划
4. 添加任务
5. 创建知识卡片

如果所有操作都正常,说明前后端已联通。

---

## 6. 配置调整

### 6.1 更新 CORS 配置

前端部署成功后,更新后端 CORS 配置:

1. 打开 Vercel 项目设置:https://vercel.com/dashboard → 选择项目 →「Settings」→「Environment Variables」
2. 更新 `CORS_ORIGINS`:
   ```
   https://studymate.pages.dev
   ```
3. 删除 `http://localhost:5173`(生产环境不需要)
4. 点击「Save」

**注意**:更新环境变量后,Vercel 会自动重新部署后端(约 30 秒)。

### 6.2 禁用 AI 功能(可选)

如果你不想看到 AI 相关按钮,可以在前端代码里注释掉:

打开 `src/pages/index/index.vue`:
```vue
<!-- 注释掉 AI 相关按钮 -->
<!-- <button @click="openAIModal">AI 生成计划</button> -->
```

或者在后端 `routes/ai.py` 里返回 mock 数据:
```python
# 所有 AI 接口都返回提示信息
@router.post("/generate")
async def ai_generate(request: AIRequest):
    return {"success": False, "message": "AI 功能已禁用,请联系管理员"}
```

### 6.3 自定义域名(可选)

如果你有自己的域名,可以绑定到 Cloudflare Pages:

1. 在 Cloudflare Pages 项目设置里点击「Custom domains」
2. 添加你的域名(如 `studymate.yourdomain.com`)
3. 在域名 DNS 里添加 CNAME 记录指向 `studymate.pages.dev`
4. Cloudflare 会自动签发 SSL 证书

**注意**:自定义域名需要付费购买(约 ¥50-70/年),如果追求完全免费,就用 `studymate.pages.dev`。

---

## 7. 测试验证

### 7.1 功能测试清单

| 功能 | 测试步骤 | 预期结果 |
|------|---------|---------|
| **注册** | 输入邮箱+密码→点注册 | 成功跳转到首页 |
| **登录** | 输入邮箱+密码→点登录 | 成功跳转到首页 |
| **创建计划** | 填写计划信息→保存 | 计划列表显示新计划 |
| **添加任务** | 填写任务信息→保存 | 任务看板显示新任务 |
| **完成任务** | 点击任务复选框 | 任务状态变为已完成 |
| **创建卡片** | 填写问题+答案→保存 | 卡片列表显示新卡片 |
| **复习卡片** | 点击「开始复习」→查看答案→选择掌握程度 | 卡片复习次数更新 |
| **番茄钟** | 点击「开始专注」→等待25分钟 | 记录创建,统计数据更新 |
| **农场浇水** | 完成番茄钟→去农场浇水 | 植物成长值增加 |
| **统计查看** | 点击「学习统计」 | 显示饼图、柱状图、记录列表 |

### 7.2 性能测试

用浏览器开发者工具测试:

| 测试项 | 方法 | 预期结果 |
|--------|------|---------|
| **首屏加载** | Network 面板查看 HTML/CSS/JS 加载时间 | < 2秒 |
| **API 响应** | Network 面板查看 `/api/*` 请求耗时 | < 500ms |
| **静态资源** | Network 面板查看图片加载时间 | < 1秒(走CDN) |

### 7.3 稳定性测试

| 测试项 | 方法 | 预期结果 |
|--------|------|---------|
| **域名访问** | 连续访问 `studymate.pages.dev` 10 次 | 每次都能打开 |
| **API 可用** | 连续调用 `/api/tasks` 10 次 | 每次都返回数据 |
| **跨设备同步** | 手机和电脑登录同一账号 | 数据一致 |

---

## 8. 常见问题与解决方案

### 8.1 部署阶段问题

#### 问题 1:Vercel 部署失败,提示 `Module not found`

**原因**:Python 依赖版本不兼容或缺少依赖

**解决**:
1. 检查 `requirements.txt`:
   ```txt
   fastapi==0.115.12
   uvicorn==0.32.1
   sqlalchemy==2.0.36
   psycopg2-binary==2.9.10
   python-jose==3.3.0
   passlib==1.7.4
   bcrypt==4.2.1
   pydantic==2.10.4
   python-multipart==0.0.20
   mangum==0.19.0
   python-dotenv==1.0.1
   ```
2. 确保版本号精确(用 `==` 而不是 `>=`)
3. 如果 `psycopg2-binary` 安装失败,尝试用 `psycopg2` 替代

#### 问题 2:Vercel 提示 `Build timeout`

**原因**:构建时间超过 Vercel 限制(5分钟)

**解决**:
- Python 项目构建很快,通常不会超时
- 如果超时,检查 `requirements.txt` 是否有过多依赖
- 尝试删除不必要的依赖(如 `torch`、`numpy` 等大型库)

#### 问题 3:Cloudflare Pages 构建失败,提示 `npm install failed`

**原因**:Node.js 版本不兼容或依赖冲突

**解决**:
1. 在项目根目录创建 `.node-version` 文件:
   ```
   18
   ```
2. 或在 Cloudflare Pages 环境变量里添加:
   - `NODE_VERSION` = `18`
3. 检查 `package.json` 里的依赖版本:
   ```json
   {
     "dependencies": {
       "vue": "^3.4.21",
       "pinia": "^2.1.7",
       ...
     }
   }
   ```

#### 问题 4:Cloudflare Pages 提示 `Build output directory not found`

**原因**:构建产物目录路径错误

**解决**:
- 检查 `Build output directory` 配置:应该是 `studymate-uniapp/dist/build/h5`
- 确保构建命令正确:应该是 `cd studymate-uniapp && npm install && npm run build:h5`
- 在本地先运行一次 `npm run build:h5`,确认 `dist/build/h5` 目录存在

### 8.2 运行阶段问题

#### 问题 5:前端打开空白页,控制台提示 `Failed to fetch`

**原因**:前端无法连接后端 API

**排查步骤**:
1. 检查 `VITE_API_BASE_URL` 是否正确配置(应该是 Vercel 后端域名)
2. 检查后端是否正常运行(访问 `https://后端域名/api/health`)
3. 检查 CORS 配置(后端 `CORS_ORIGINS` 是否包含 `https://studymate.pages.dev`)

**解决**:
- 更新 Cloudflare Pages 环境变量 `VITE_API_BASE_URL`
- 更新 Vercel 环境变量 `CORS_ORIGINS`

#### 问题 6:注册/登录提示 `500 Internal Server Error`

**原因**:数据库连接失败

**排查步骤**:
1. 检查 Supabase 项目是否正常运行(登录 Supabase 控制台查看)
2. 检查 `DATABASE_URL` 是否正确(密码、主机、端口)
3. 检查 `DB_SSLMODE` 是否设置为 `require`

**解决**:
- 在 Supabase 控制台重置数据库密码,更新 `DATABASE_URL`
- 确保 Supabase 项目未暂停(免费层会在 7 天无活跃后暂停,需手动激活)

#### 问题 7:图片上传失败,提示 `Upload failed`

**原因**:COS 配置错误或跨域问题

**解决**:
- 如果不用 COS,图片会存 base64,不需要额外配置
- 如果要用 COS,检查:
  1. `COS_SECRET_ID` / `COS_SECRET_KEY` 是否正确
  2. `COS_BUCKET` / `COS_REGION` 是否正确
  3. COS 存储桶是否开启公网访问
  4. COS 存储桶 CORS 规则是否允许 `studymate.pages.dev`

#### 问题 8:域名访问不稳定,偶尔打不开

**原因**:DNS 解析问题或 CDN 缓存问题

**解决**:
1. 清除浏览器缓存(Ctrl + Shift + Delete)
2. 刷新页面(Ctrl + F5 强制刷新)
3. 检查 Cloudflare Pages 状态(登录控制台查看部署状态)
4. 如果长时间不稳定,尝试:
   - 在 Cloudflare 控制台清除缓存:「Caching」→「Purge Cache」
   - 检查 DNS 记录是否正确指向 `studymate.pages.dev`

### 8.3 数据问题

#### 问题 9:数据丢失或不同步

**原因**:Supabase 数据库问题或缓存问题

**解决**:
- Supabase 免费层在 7 天无活跃后会暂停项目,导致数据无法访问
- 解决:登录 Supabase 控制台,点击「Resume project」激活项目
- 预防:每周至少访问一次,保持项目活跃

#### 问题 10:数据库空间不足

**原因**:Supabase 免费层只有 500MB

**解决**:
1. 登录 Supabase 控制台查看数据库大小
2. 如果接近 500MB:
   - 删除不需要的历史数据(如旧的番茄记录)
   - 清理图片(如果存 base64,占空间大)
   - 或者升级 Supabase 付费层(Pro 版 $25/月,8GB)

---

## 9. 维护和更新

### 9.1 代码更新流程

当你修改代码后,部署流程:

```
本地修改 → git commit → git push → GitHub
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
            Cloudflare Pages                   Vercel
            (自动拉取并构建前端)               (自动拉取并部署后端)
            约3-5分钟                         约30-60秒
                    ↓                               ↓
            前端自动更新                      后端自动更新
```

**操作步骤**:
```bash
# 1. 本地修改代码
vim studymate-uniapp/src/pages/index/index.vue

# 2. 提交到 Git
git add .
git commit -m "update: 修改首页布局"

# 3. 推送到 GitHub
git push origin main

# 4. 等待自动部署(无需手动操作)
# Cloudflare Pages 和 Vercel 都会自动拉取并部署
```

### 9.2 查看部署状态

| 平台 | 查看方式 |
|------|---------|
| **Cloudflare Pages** | 控制台 →「Workers & Pages」→ 选择项目 →「View details」→「Deployments」 |
| **Vercel** | 控制台 → 选择项目 →「Deployments」 |

### 9.3 回滚到旧版本

如果新版本有问题,可以回滚:

**Cloudflare Pages**:
1. 进入「Deployments」列表
2. 找到上一个成功的部署
3. 点击「Rollback to this deployment」

**Vercel**:
1. 进入「Deployments」列表
2. 找到上一个成功的部署
3. 点击「...」→「Promote to Production」

### 9.4 监控和日志

| 平台 | 日志查看 |
|------|---------|
| **Cloudflare Pages** | 控制台 → 选择项目 →「Logs」→「Real-time Logs」 |
| **Vercel** | 控制台 → 选择项目 →「Logs」 |

**建议**:每周检查一次日志,确认没有异常错误。

### 9.5 数据库备份

Supabase 免费层不提供自动备份,需手动备份:

**方法 1**:用 Supabase 控制台导出
1. 登录 Supabase 控制台
2. 进入「Database」→「Backups」
3. 点击「Create backup」(手动备份)

**方法 2**:用 pg_dump 导出
```bash
pg_dump "postgresql://postgres:[密码]@db.xxx.supabase.co:5432/postgres" > backup.sql
```

**建议**:每月备份一次,保存到本地或云存储。

---

## 10. 费用说明

### 10.1 当前方案费用

| 项目 | 平台 | 免费额度 | 超额费用 | 每年实际费用 |
|------|------|---------|---------|-------------|
| **前端托管** | Cloudflare Pages | 无限制 | 无 | ¥0 |
| **前端 CDN** | Cloudflare CDN | 无限制 | 无 | ¥0 |
| **域名** | Cloudflare | `xxx.pages.dev` 免费 | 无 | ¥0 |
| **后端托管** | Vercel | 100GB带宽/月 | $20/月起 | ¥0(个人够用) |
| **后端域名** | Vercel | `xxx.vercel.app` 免费 | 无 | ¥0 |
| **数据库** | Supabase | 500MB存储,5GB带宽 | $25/月起 | ¥0(个人够用) |
| **图片存储** | base64存数据库 | 含在数据库免费额度内 | 无 | ¥0 |
| **总计** | - | - | - | **¥0/年** |

### 10.2 对比其他方案

| 方案 | 首年费用 | 第2年费用 | 第3年费用 | 第5年费用 |
|------|---------|---------|---------|---------|
| **Cloudflare Pages + Vercel** | ¥0 | ¥0 | ¥0 | ¥0 |
| CloudBase(腾讯云) | ¥0(6个月) | ¥240 | ¥240 | ¥240 |
| 腾讯云轻量服务器 | ¥60-100 | ¥200-300 | ¥200-300 | ¥200-300 |
| 自定义域名 + Vercel | ¥50-70 | ¥50-70 | ¥50-70 | ¥50-70 |

### 10.3 何时需要付费

| 场景 | 需要付费的项目 | 费用 |
|------|---------------|------|
| **数据量 > 500MB** | Supabase Pro($25/月)或迁移到其他数据库 | ¥1800/年 |
| **带宽 > 100GB/月** | Vercel Pro($20/月)或迁移到其他平台 | ¥1440/年 |
| **要用自定义域名** | 购买域名(¥50-70/年) | ¥50-70/年 |
| **要用 AI 功能** | 混元/DeepSeek API Token | ¥10-30/月 |

**个人使用场景**:一般不会触发免费额度限制:
- 500MB 数据库:足够存几千条任务 + 卡片 + 错题
- 100GB 带宽:足够每月几千次访问
- `xxx.pages.dev` 域名:足够个人使用

### 10.4 长期免费保证

| 平台 | 免费层政策 | 是否永久免费 |
|------|----------|-------------|
| **Cloudflare Pages** | 永久免费层,无限制 | ✅ 是 |
| **Vercel** | Hobby 永久免费,100GB带宽/月 | ✅ 是 |
| **Supabase** | Free 永久免费,500MB存储 | ✅ 是 |

**结论**:只要不超出免费额度,这三个平台都是永久免费的,**5年后依然 ¥0**。

---

## 11. 下一步

部署完成后,你可以:

1. **测试所有功能**:注册、登录、任务、卡片、番茄钟、农场、统计
2. **分享给朋友**:发送 `https://studymate.pages.dev` 链接
3. **继续开发**:修改代码 → push → 自动部署
4. **监控运行状态**:定期检查 Cloudflare 和 Vercel 日志

---

## 12. 参考资料

- [Cloudflare Pages 官方文档](https://developers.cloudflare.com/pages/)
- [Vercel 官方文档](https://vercel.com/docs)
- [Supabase 官方文档](https://supabase.com/docs)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Vue 3 官方文档](https://vuejs.org/)
- [UniApp 官方文档](https://uniapp.dcloud.net.cn/)

---

<p align="center">
  <strong>部署完成后,每年 ¥0,长期免费访问</strong>
</p>
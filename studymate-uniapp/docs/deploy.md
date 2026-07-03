# StudyMate 部署指南

> 本文档提供详细的生产环境部署步骤，推荐方案：**Vercel 前端 + Render 后端 + Supabase 数据库 + 腾讯云 COS 图片存储**

---

## 目录

- [架构概览](#架构概览)
- [方案对比](#方案对比)
- [第 0 步：准备工作](#第-0-步准备工作)
- [第 1 步：创建 Supabase 数据库](#第-1-步创建-supabase-数据库)
- [第 2 步：配置腾讯云 COS](#第-2-步配置腾讯云-cos)
- [第 3 步：部署后端到 Render](#第-3-步部署后端到-render)
- [第 4 步：部署前端到 Vercel](#第-4-步部署前端到-vercel)
- [第 5 步：手机和电脑同步使用](#第-5-步手机和电脑同步使用)
- [部署检查清单](#部署检查清单)
- [常见问题](#常见问题)
- [其他部署方案](#其他部署方案)

---

## 架构概览

```
用户手机/电脑
    │
    ▼
Vercel 前端（静态 H5，免费）
    │
    ▼
Render 后端（FastAPI，免费）
    │
    ├──► 腾讯云 COS（图片存储，免费额度）
    │
    └──► Supabase PostgreSQL（数据库，免费）
```

---

## 方案对比

| 方案 | 前端 | 后端 | 数据库 | 图片 | 费用 | 推荐度 |
|------|------|------|--------|------|------|--------|
| **方案 A（推荐）** | Vercel | Render | Supabase | 腾讯云 COS | 全免费 | ⭐⭐⭐⭐⭐ |
| 方案 B | Vercel | Vercel Serverless | Supabase | 腾讯云 COS | 全免费 | ⭐⭐⭐ |
| 方案 C | Render | Render | Render PG | 腾讯云 COS | 全免费 | ⭐⭐⭐⭐ |
| 方案 D（全腾讯云）| 腾讯云 OSS | 腾讯云轻量 | 腾讯云 TencentDB | 腾讯云 COS | ~50元/月 | ⭐⭐⭐ |

### 为什么推荐方案 A？

- ✅ **全免费**：所有平台的免费额度个人使用完全够用
- ✅ **无超时限制**：Render 后端没有 Vercel Serverless 的 10 秒超时，AI 功能正常
- ✅ **数据库稳定**：Supabase 比 Render 免费版数据库更稳定，不会休眠删库
- ✅ **速度快**：Vercel 前端全球 CDN，访问速度快
- ✅ **自动部署**：Push 到 GitHub 自动更新

---

## 第 0 步：准备工作

### 需要注册的账号

| 平台 | 用途 | 链接 |
|------|------|------|
| GitHub | 代码托管，必须 | https://github.com |
| Vercel | 前端部署 | https://vercel.com |
| Render | 后端部署 | https://render.com |
| Supabase | 数据库 | https://supabase.com |
| 腾讯云 | COS 图片存储 | https://cloud.tencent.com/product/cos |

### 代码推送

确保你的代码已经推送到 GitHub 仓库（Render 和 Vercel 都从 GitHub 拉代码自动部署）。

---

## 第 1 步：创建 Supabase 数据库

### 1.1 注册 Supabase
- 打开 https://supabase.com
- 用 GitHub 登录

### 1.2 新建项目
1. 点击 **New Project**
2. 填写：
   - **Name**：`studymate`
   - **Database Password**：设置一个强密码（请记下来！）
   - **Region**：选 `Southeast Asia (Singapore)`（离中国近，延迟低）
   - **Pricing Plan**：选 **Free**
3. 点击 **Create new project**
4. 等待数据库创建（约 2 分钟）

### 1.3 获取连接字符串
1. 进入项目 → 左侧菜单 **Settings**（齿轮图标）→ **Database**
2. 找到 **Connection string** → 选择 **URI** 选项卡
3. 把 `[YOUR-PASSWORD]` 替换成你刚才设置的密码
4. 复制完整连接串，格式如下：
   ```
   postgresql://postgres:你的密码@db.xxxxxx.supabase.co:5432/postgres
   ```

> ⚠️ **保存好这个连接串**，后面 Render 部署要用。

---

## 第 2 步：配置腾讯云 COS

### 2.1 开通 COS
1. 打开 https://cloud.tencent.com/product/cos
2. 注册/登录，开通对象存储 COS
   - 新用户有 6 个月 50GB 免费额度
   - 付费也很便宜，10GB 存储 + 流量每月约几元钱

### 2.2 创建存储桶
1. 进入 COS 控制台 → **存储桶列表** → **创建存储桶**
2. 填写：
   - **名称**：`studymate-你的QQ号`（全局唯一，比如 `studymate-12345678`）
   - **所属地域**：选离你最近的（广州/上海/北京/成都等）
   - **访问权限**：**公有读私有写**（图片要前端直接显示，必须公有读）
3. 点击 **确定**

### 2.3 获取 API 密钥
1. 访问 https://console.cloud.tencent.com/cam/capi
2. 点击 **新建密钥**
3. 复制 `SecretId` 和 `SecretKey`
   - ⚠️ **SecretKey 只显示一次，务必保存好**
   - ⚠️ 不要把密钥提交到公开仓库

### 2.4 配置 CORS 跨域（重要！）

前端直传图片到 COS 必须配置跨域，否则浏览器会拦截。

1. 进入你的存储桶 → **安全管理** → **跨域访问CORS设置**
2. 点击 **添加规则**
3. 填写：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 来源Origin | `*` | 允许所有域名，生产环境可改成你的前端域名 |
| Methods | 勾选 GET、POST、PUT、HEAD | 上传和读取需要这些方法 |
| Allow-Headers | `*` | 允许所有请求头 |
| Expose-Headers | `ETag`、`Content-Length` | 前端需要读取这些响应头 |
| Max-Age（秒） | `3600` | 预检请求缓存时间 |

4. 点击 **保存**

### 2.5 记下 COS 信息

部署后端时需要以下信息：
- `COS_SECRET_ID`：上面拿到的 SecretId
- `COS_SECRET_KEY`：上面拿到的 SecretKey
- `COS_BUCKET`：存储桶名称，如 `studymate-12345678`
- `COS_REGION`：地域，如 `ap-guangzhou`（广州）、`ap-shanghai`（上海）、`ap-beijing`（北京）

---

## 第 3 步：部署后端到 Render

### 3.1 注册 Render
- 打开 https://render.com
- 用 GitHub 登录，授权访问你的仓库

### 3.2 新建 Web Service
1. 右上角 **New** → **Web Service**
2. 选择你的 GitHub 仓库
3. 如果找不到，点击 **Configure account** 授权 Render 访问你的仓库

### 3.3 填写配置

仔细填写，不要错（错了会部署失败）：

| 配置项 | 填什么 | 说明 |
|--------|--------|------|
| **Name** | `studymate-api` | 随便起，会变成你的二级域名 |
| **Region** | `Singapore` | 和 Supabase 同区域，延迟低 |
| **Branch** | `main` | 你的主分支名 |
| **Root Directory** | `server` | ⚠️ 重要！指向后端目录 |
| **Runtime** | `Python 3` | 选最新的 Python 3 版本 |
| **Build Command** | `pip install -r requirements.txt` | 安装依赖 |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` | 启动服务，必须用 `$PORT` |
| **Instance Type** | **Free** | 免费版 |

### 3.4 配置环境变量

往下滑找到 **Environment Variables**。

可以点击 **Add from .env**，然后把下面的内容粘进去（注意替换成你自己的值）：

```env
# ---------- 数据库（必填）----------
DATABASE_URL=postgresql://postgres:你的密码@db.xxx.supabase.co:5432/postgres

# ---------- JWT（必填）----------
SECRET_KEY=请改成一串随机字符串
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ---------- CORS（必填）----------
CORS_ORIGINS=*

# ---------- 腾讯云 COS（推荐配置）----------
COS_SECRET_ID=你的COS_SecretId
COS_SECRET_KEY=你的COS_SecretKey
COS_BUCKET=你的存储桶名称
COS_REGION=ap-guangzhou

# ---------- DeepSeek AI（可选）----------
DEEPSEEK_API_KEY=

# ---------- 通义千问（可选）----------
QWEN_API_KEY=
```

#### 各环境变量说明：

| 变量 | 必填 | 说明 |
|------|------|------|
| `DATABASE_URL` | ✅ | Supabase 的连接字符串 |
| `SECRET_KEY` | ✅ | JWT 密钥，生产环境务必改随机字符串 |
| `ALGORITHM` | ✅ | 默认 `HS256` 就行 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Token 有效期，默认 1440 分钟（1天） |
| `CORS_ORIGINS` | ✅ | 允许跨域的域名，`*` 表示全部允许 |
| `COS_SECRET_ID` | ⭕ | 不配置的话图片上传功能不可用 |
| `COS_SECRET_KEY` | ⭕ | 同上 |
| `COS_BUCKET` | ⭕ | 同上 |
| `COS_REGION` | ⭕ | 同上 |
| `DEEPSEEK_API_KEY` | ❌ | AI 生成功能，没有就空着 |
| `QWEN_API_KEY` | ❌ | 图片识别功能，没有就空着 |

> 💡 生成强随机密钥的方法（本地终端执行）：
> ```bash
> openssl rand -hex 32
> ```

### 3.5 点击 Create Web Service

- 等待部署（第一次约 2-5 分钟）
- 可以看实时日志，有问题根据报错排查
- 日志里出现 `Uvicorn running on http://0.0.0.0:10000` 就成功了

### 3.6 测试后端

部署成功后，顶部会显示你的域名，比如 `https://studymate-api.onrender.com`。

在浏览器里访问以下地址测试：

| 地址 | 预期结果 |
|------|---------|
| `https://你的域名/health` | 返回 `{"status":"ok"}` |
| `https://你的域名/docs` | 显示 FastAPI Swagger 文档页面 |

> ⚠️ **第一次访问可能慢**：Render 免费版 15 分钟不用会休眠，冷启动需要 10-30 秒，正常现象。

---

## 第 4 步：部署前端到 Vercel

### 4.1 注册 Vercel
- 打开 https://vercel.com
- 用 GitHub 登录

### 4.2 新建项目
1. 点击 **Add New** → **Project**
2. 选择你的 GitHub 仓库
3. 点击 **Import**

### 4.3 配置项目

| 配置项 | 填什么 | 说明 |
|--------|--------|------|
| **Framework Preset** | `Other` | UniApp 不是 Vercel 默认支持的框架 |
| **Root Directory** | 留空 / 项目目录 | 代码在仓库根目录就留空 |
| **Build Command** | `npm run build:h5` | 构建 H5 版本 |
| **Output Directory** | `dist/build/h5` | 构建产物目录 |
| **Install Command** | `npm install` | 安装依赖 |

### 4.4 添加环境变量

往下找 **Environment Variables**，添加：

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://你的后端域名.onrender.com/api` |

> 把 `你的后端域名` 替换成第 3 步 Render 给你的域名，注意末尾要加 `/api`。

### 4.5 点击 Deploy

- 等待构建（约 1-2 分钟）
- 成功后 Vercel 会给你一个域名，比如 `https://studymate-xxx.vercel.app`

### 4.6 测试前端

打开 Vercel 给你的域名，测试以下功能：

- [ ] 注册页面能正常显示
- [ ] 能正常注册新账号
- [ ] 能正常登录
- [ ] 首页数据能加载
- [ ] 能添加知识卡片/错题本
- [ ] 图片能正常上传和显示（说明 COS 配置成功）

---

## 第 5 步：手机和电脑同步使用

部署完成后，数据天然同步，因为前后端都是同一套。

### 电脑端
- 直接用浏览器打开 Vercel 域名
- 建议「添加到收藏夹」或「安装为应用」（Chrome 支持 PWA）

### 手机端
- 手机浏览器打开同一个 Vercel 域名
- 建议「添加到主屏幕」，用起来像原生 App
  - iOS：Safari → 分享按钮 → 添加到主屏幕
  - Android：Chrome → 菜单 → 添加到主屏幕

### 数据同步
- 同一个账号登录，数据自动同步
- 所有数据存在 Supabase 数据库和腾讯云 COS 里

---

## 部署检查清单

部署完按这个列表逐项检查：

### 基础配置
- [ ] Supabase 数据库创建成功，连接串已复制
- [ ] 腾讯云 COS 存储桶创建好，权限设为公有读私有写
- [ ] COS 的 CORS 跨域已配置
- [ ] API 密钥（SecretId / SecretKey）已获取

### 后端部署
- [ ] Render 的 Root Directory 设为 `server`
- [ ] 所有环境变量都配置了（DATABASE_URL、SECRET_KEY、COS_xxx 等）
- [ ] 启动命令是 `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] 后端部署成功，`/health` 返回 ok
- [ ] `/docs` 能看到 API 文档

### 前端部署
- [ ] Vercel 的 Build Command 是 `npm run build:h5`
- [ ] Output Directory 是 `dist/build/h5`
- [ ] `VITE_API_BASE_URL` 环境变量配置正确，末尾带 `/api`
- [ ] 前端页面能正常打开
- [ ] 能正常注册和登录

### 功能测试
- [ ] 创建学习计划功能正常
- [ ] 添加每日任务功能正常
- [ ] 添加知识卡片功能正常
- [ ] 图片上传后能正常显示（COS 验证）
- [ ] 添加错题功能正常
- [ ] 学习农场功能正常
- [ ] 番茄钟能正常计时
- [ ] 统计页面数据正确

---

## 常见问题

### Q: Render 部署失败怎么办？

**A:** 看实时日志，常见原因：

1. **Root Directory 错了**：没填 `server`，Render 找不到 Python 代码
2. **DATABASE_URL 错了**：密码没替换，或者连接串不完整
3. **依赖安装失败**：检查 `requirements.txt` 是否在 `server` 目录里
4. **启动命令错了**：必须用 `$PORT` 变量，不能写死端口

### Q: 前端连不上后端？

**A:** 按顺序检查：

1. 后端自己能访问吗？打开 `https://后端域名/health` 测试
2. Vercel 的 `VITE_API_BASE_URL` 对不对？末尾有没有 `/api`？
3. 后端 `CORS_ORIGINS` 是不是 `*`？
4. 浏览器 F12 看 Console 和 Network，具体报什么错

### Q: 图片上传失败？

**A:** 检查：

1. COS 的 SecretId / SecretKey 对不对
2. 存储桶权限是不是「公有读私有写」
3. COS 的 CORS 跨域配置好了吗
4. COS_BUCKET 和 COS_REGION 对不对

### Q: 第一次打开好慢？

**A:** 正常现象。Render 免费版 15 分钟无人访问会休眠，第一次访问需要冷启动（10-30秒）。之后就快了。

解决方法：用 https://cron-job.org 免费服务，每 10 分钟访问一次你的后端，让它一直醒着。

### Q: Render 免费版会删库吗？

**A:** 用 **Supabase** 数据库就不会。Render 自己的免费版 PostgreSQL 确实可能在 90 天无活动后暂停，但 Supabase 免费版没有这个问题，更稳定。

### Q: 怎么更新代码？

**A:** 直接 push 到 GitHub 的 main 分支，Vercel 和 Render 都会自动检测并重新部署。

### Q: 怎么自定义域名？

**A:** 两个平台都支持：

- **Vercel**：项目设置 → Domains → 添加域名 → 按提示改 DNS
- **Render**：项目设置 → Custom Domains → 添加域名

---

## 其他部署方案

### 方案 B：全 Vercel（前端 + 后端 Serverless）

适合：AI 功能用得少，能接受 10 秒超时

- 前端：Vercel 静态站
- 后端：Vercel Serverless Functions（用 Mangum 包装 FastAPI）
- 数据库：Supabase
- 图片：腾讯云 COS

配置文件见 `server/api/index.py` 和 `server/vercel.json`。

### 方案 C：全 Render（前端 + 后端 + 数据库）

适合：想只用一个平台管理，对前端速度要求不高

- 前端：Render Static Site
- 后端：Render Web Service
- 数据库：Render PostgreSQL
- 图片：腾讯云 COS

### 方案 D：国内部署（全腾讯云）

适合：追求国内访问速度，愿意付费

- 前端：腾讯云 OSS + CDN
- 后端：腾讯云轻量应用服务器（~50元/月）
- 数据库：腾讯云 TencentDB（可选）
- 图片：腾讯云 COS

---

## 费用估算（个人使用）

| 服务 | 免费额度 | 超出后费用 | 个人实际费用 |
|------|---------|-----------|------------|
| Vercel 前端 | 100GB 带宽/月 | 超出后 $40/100GB | 0 元 |
| Render 后端 | 750 小时/月 | $7/月起 | 0 元 |
| Supabase 数据库 | 500MB + 1GB 带宽 | $25/月起 | 0 元 |
| 腾讯云 COS | 6个月50GB | 存储 ~0.1元/GB/月 | 0元 → 几元/月 |
| **合计** | - | - | **0元 → 几元/月** |

---

<p align="center">
  部署过程中有问题，随时参考本文档排查 🚀
</p>

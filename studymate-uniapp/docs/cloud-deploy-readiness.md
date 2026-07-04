# StudyMate 云部署优化清单

> 目标架构：Vercel(前端) + Render(后端) + Supabase(数据库) + 腾讯云COS(图片)
> 本文只列问题和修复方案，不修改代码文件。

---

## 🔴 CRITICAL（必须修，否则部署失败或安全事故）

### 1. `config.py` — JWT 密钥默认值存在安全漏洞
**位置**：`studymate-uniapp/server/config.py` 第 15 行  
**现状**：`SECRET_KEY = os.getenv("SECRET_KEY", "studymate-secret-key-change-in-production")`  
**问题**：代码公开在 GitHub。若部署时忘记设环境变量，任何人可通过源码中的默认密钥伪造 JWT，冒充任意用户。  
**修法**：移除默认值，启动时若未检测到则抛 `ValueError("SECRET_KEY must be set")` 阻止启动。

### 2. `config.py` — 数据库 URL 默认指向 localhost
**位置**：`studymate-uniapp/server/config.py` 第 9-12 行  
**现状**：`DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://studymate:studymate123@localhost:5432/studymate")`  
**问题**：若 Render 环境变量未配，后端会尝试连接本地 5432，超时后才报错，难以排查。  
**修法**：去掉默认值，未设置时启动抛异常。

### 3. `database.py` — SSL 模式不兼容 Supabase
**位置**：`studymate-uniapp/server/database.py` 第 22 行  
**现状**：`"sslmode": "prefer"`  
**问题**：Supabase PostgreSQL 强制 SSL。`prefer` 可能降级为明文被拒绝。  
**修法**：改为 `"sslmode": "require"`。

### 4. `main.py` — 启动端口硬编码
**位置**：`studymate-uniapp/server/main.py` 第 62 行  
**现状**：`uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)`  
**问题**：Render 通过 `$PORT` 动态分配端口，硬编码 8000 会导致绑定失败。  
**修法**：`port=int(os.getenv("PORT", "8000"))`。

### 5. 缺少 `vercel.json`
**问题**：Vercel 部署需要 `vercel.json` 指定构建命令、输出目录、SPA 路由重写（非根路由刷新 404）。没有此文件则前端无法访问。  
**修法**：在 `studymate-uniapp/` 根目录创建：
```json
{
  "buildCommand": "npm run build:h5",
  "outputDirectory": "dist/build/h5",
  "rewrites": [{"source": "/(.*)", "destination": "/index.html"}]
}
```

### 6. `.env` — VITE_API_BASE_URL 为空
**位置**：`studymate-uniapp/.env` 第 10 行  
**现状**：`VITE_API_BASE_URL=`（空）  
**问题**：Vite 构建时，`client.js` 回退到 `/api` 相对路径，Vercel 上所有 API 请求 404。  
**修法**：Vercel 环境变量中必须设置 `VITE_API_BASE_URL=https://你的域名.onrender.com/api`；本地 `.env` 保持空（开发用代理）。

### 7. `pomodoro.vue` — 番茄记录仅存 localStorage
**位置**：`studymate-uniapp/src/pages/daily/pomodoro.vue` 第 454-458+567-570 行  
**现状**：`completeSession()` 写入 `studymate_pomodoro_records`（localStorage）；手动编辑/删除只改 localStorage，不调后端。
**问题**：多设备使用同一账号时，A 设备的番茄历史在 B 设备完全看不到。  
**修法**：`onMounted` 时从后端 `getFocusRecords` 拉取同步到 localStorage；手动编辑/删除增加 `updateFocusRecord` / `deleteFocusRecord` API 调用。

---

## 🟠 HIGH（可能导致功能异常）

### 8. `cos_service.py` — COS 未配置时仍生成演示凭证
**位置**：`studymate-uniapp/server/services/cos_service.py` 第 50-63 行  
**问题**：COS 密钥为空时返回假凭证，前端以为上传成功，实际图片从未到达 COS。  
**修法**：启动时检查 COS 配置，未配置则不注册 `/api/upload` 路由或返回明确错误。

### 9. `cos_service.py` — STS 权限前缀过窄
**位置**：`studymate-uniapp/server/services/cos_service.py` 第 29 行  
**现状**：`"allow_prefix": [f"proofs/{user_id}/*"]`  
**问题**：仅允许 `proofs/` 路径上传，但前端还上传到 `cards/question/` `cards/answer/` `mistakes/question/` `mistakes/answer/` `avatars/`。  
**修法**：改为允许所有用户相关前缀，或改为动态前缀参数。

### 10. `config.py` — COS_BUCKET 默认值指向原开发者
**位置**：`studymate-uniapp/server/config.py` 第 33 行  
**现状**：`COS_BUCKET = os.getenv("COS_BUCKET", "studymate-1250000000")`  
**问题**：部署后若忘配环境变量，所有图片 URL 指向不存在的 bucket。  
**修法**：去掉默认值。

---

## 🟡 MEDIUM（建议优化）

### 11. 缺少数据库迁移工具
**问题**：`init_db()` 只 `create_all`（建新表不建新列）。任何模型变更都需要手动 `ALTER TABLE`。  
**建议**：加入 Alembic 或使用 Supabase Migration（SQL 文件方式）。

### 12. `seed.py` 无环境保护
**位置**：`studymate-uniapp/server/seed.py` 第 24 行  
**问题**：`Base.metadata.create_all(bind=engine)` 之后直接写数据，若误在生产运行会清真实用户数据。  
**建议**：加 `if os.getenv("ENV") != "production"` 保护。

### 13. 数据库连接池过大
**位置**：`studymate-uniapp/server/database.py` 第 16 行  
**现状**：`pool_size=5, max_overflow=10` = 最多 15 连接  
**问题**：Supabase 免费版上限 15，若 Render 冷启动多实例叠加可能超限。  
**建议**：`pool_size=2, max_overflow=5` 或通过环境变量控制。

### 14. 多页面 CORS/JWT 重复代码
**问题**：`_get_user_id()` 在 `routes/auth.py` `upload.py` `plans.py` `ai.py` `subjects.py` 等 8 处重复定义。  
**建议**：抽取到 `utils/auth.py`，统一依赖注入。

### 15. `pomodoro.vue` — 时间设置仅存 localStorage
**问题**：专注时长/休息时长设置不跨设备同步。  
**建议**：存入后端 User 表的 `settings` JSON 字段，前端优先读后端。

### 16. 缺少 `runtime.txt`
**问题**：Render 需要知道 Python 版本，当前无此文件。  
**建议**：创建 `studymate-uniapp/server/runtime.txt`，内容 `python-3.11`。

---

## 🔵 LOW（非必需但值得做）

### 17. `server/db.js` — 无用的旧文件
**问题**：残留的 SQLite 原型代码，内容乱码。  
**建议**：删除。

### 18. `picsum.photos` 占位图片
**问题**：种子数据中 16 处使用 `https://picsum.photos/seed/...` 占位图。  
**建议**：部署后替换为 COS 真实图片 URL，或保留作为 demo 演示。

### 19. DeepSeek/Qwen API Key 为空时的 Mock 降级
**问题**：AI 功能无 Key 时返回 mock 数据，前端无感知。  
**现状**：已正确处理，用户不会看到报错。无需改动。

---

## 总结

| 优先级 | 数量 | 涉及文件 |
|--------|------|---------|
| 🔴 CRITICAL | 7 | config.py, database.py, main.py, .env, pomodoro.vue, vercel.json(缺) |
| 🟠 HIGH | 3 | cos_service.py, config.py |
| 🟡 MEDIUM | 6 | seed.py, database.py, routes/*.py, runtime.txt(缺) |
| 🔵 LOW | 3 | db.js, seed.py(图片URL) |

**关键风险**：安全问题(#1)、数据库连接(#2#3)、前端 API 断连(#5#6)、多设备数据丢失(#7)。

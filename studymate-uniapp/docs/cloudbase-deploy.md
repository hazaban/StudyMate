# CloudBase 云函数部署后端 + 混元 AI 福利使用教程

> 本文档教你把 StudyMate 后端部署到腾讯云 CloudBase(6 个月免费),并用上「AI 小程序成长计划」送的 1 亿混元 Token。
>
> 后端代码已改好,你直接照步骤操作即可。

---

## 目录

1. [代码已做了哪些改动](#1-代码已做了哪些改动)
2. [第一步:确认你的福利到账了](#2-第一步确认你的福利到账了)
3. [第二步:申请混元 API Key](#3-第二步申请混元-api-key)
4. [第三步:准备后端代码包](#4-第三步准备后端代码包)
5. [第四步:在 CloudBase 控制台创建云函数](#5-第四步在-cloudbase-控制台创建云函数)
6. [第五步:配置环境变量](#6-第五步配置环境变量)
7. [第六步:测试后端接口](#7-第六步测试后端接口)
8. [第七步:怎么确认 1 亿 Token 福利在消耗](#8-第七步怎么确认-1-亿-token-福利在消耗)
9. [常见问题](#9-常见问题)

---

## 1. 代码已做了哪些改动

### 改了 3 个文件

| 文件 | 改了什么 |
|------|----------|
| [server/config.py](../server/config.py) | 加了混元 AI 配置(`HUNYUAN_API_KEY` / `HUNYUAN_BASE_URL` / `HUNYUAN_MODEL`);加了 CloudBase/SCF 生产环境自动检测;加了 `AI_PROVIDER` 自动选择(混元 > DeepSeek > mock) |
| [server/services/ai_service.py](../server/services/ai_service.py) | `_call_deepseek` 函数内部改成了多 provider 模式,根据 `AI_PROVIDER` 自动选混元/DeepSeek/mock,**函数名没变**,其他调用点不用改 |
| [server/index.py](../server/index.py) | 新增 — CloudBase HTTP 云函数入口文件,用 Mangum 包 FastAPI |

### 不用改的

- 所有路由、数据库模型、COS 服务、JWT 认证 — 全不动
- `requirements.txt` — 依赖都兼容
- 前端 — 不用动

---

## 2. 第一步:确认你的福利到账了

1. 打开 CloudBase 控制台:https://console.cloud.tencent.com/tcb
2. 选择你的环境(名字应该是 `studymate` 之类)
3. 左侧菜单点「AI」
4. 看「生文模型」→ 应该显示 **1 亿 Token** 额度
5. 看「生图模型」→ 应该显示 **1 万张** 额度
6. 左侧「套餐用量」→ 确认是「个人版」,资源有效期 6 个月

如果没到账:
- 去微信小程序后台 → 行业能力 → AI 小程序成长计划 → 重新点「去使用」
- 确认你登录的腾讯云账号和小程序后台绑定的是同一个

---

## 3. 第二步:申请混元 API Key

> ⚠️ 重要:「AI 成长计划」送的 1 亿 Token 是在 CloudBase 的 AI 模块里,不是直接给你一个 API Key。
> 有两种用法,选一种:

### 方案 A:用 CloudBase AI 代理(推荐,直接消耗福利 Token)

CloudBase AI 模块提供了一个代理 URL,调它就直接扣福利额度。

**获取代理 URL 和 Token**:
1. CloudBase 控制台 → 你的环境 → 左侧「AI」→ 「生文模型」
2. 找「API 调用」或「接入指南」按钮
3. 复制「请求地址」(形如 `https://tcb-api.tencentcloudapi.com/api/v2/ai/chat/completions`)
4. 复制「API Key」或「访问凭证」

**填到环境变量里**:
```
HUNYUAN_BASE_URL=https://tcb-api.tencentcloudapi.com/api/v2/ai
HUNYUAN_API_KEY=你复制的API Key
HUNYUAN_MODEL=hunyuan-pro
```

### 方案 B:用混元官方 OpenAI 兼容 API(退路)

如果方案 A 找不到代理 URL,就直接用混元官方 API(兼容 OpenAI 协议)。
但注意:**这个要自购 Token,不消耗福利**。

1. 打开 https://console.cloud.tencent.com/hunyuan
2. 「API Key 管理」→ 新建密钥
3. 复制 SecretId 当 API Key(混元兼容模式用 SecretId 作为 Bearer Token)

```
HUNYUAN_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
HUNYUAN_API_KEY=你的SecretId
HUNYUAN_MODEL=hunyuan-pro
```

### 方案 C:先用 mock 模式(啥都不配也能跑)

不配任何 AI Key,后端自动返回 mock 数据,先把后端跑通再说。
AI 功能显示的是假数据,但其他功能(计划、任务、卡片、错题、农场、番茄)全正常。

---

## 4. 第三步:准备后端代码包

CloudBase 云函数需要上传整个 `server/` 目录。你有两种方式准备:

### 方式一:直接上传 server 文件夹(推荐,最简单)

1. 找到你本地的 `studymate-uniapp/server/` 目录
2. 确认里面有 `index.py`(我刚加的,就在根目录)
3. 选中整个 `server/` 文件夹,**压缩成 zip**
   - Windows:右键 → 发送到 → 压缩(zipped)文件夹
   - Mac:右键 → 压缩「server」
4. 文件名随便,比如 `studymate-server.zip`

### 方式二:用 CloudBase CLI 部署(适合后续频繁更新)

需要 Node.js 环境,命令行执行:

```bash
npm install -g @cloudbase/cli
tcb login
```

然后在项目根目录建 `cloudbaserc.json`,执行 `tcb fn deploy`。
(这个后续再折腾,先手动上传跑通)

---

## 5. 第四步:在 CloudBase 控制台创建云函数

1. 打开 CloudBase 控制台:https://console.cloud.tencent.com/tcb
2. 选你的环境
3. 左侧菜单 → **「云函数 / 托管 / 主机」**
4. 点 **「新建云函数」**
5. 填表单:

| 字段 | 填什么 |
|------|--------|
| 函数名称 | `studymate-api` |
| 函数类型 | **HTTP 云函数**(不是事件函数!) |
| 运行环境 | **Python 3.10** |
| 函数代码 | 选择「本地上传 zip 包」→ 上传刚才的 `studymate-server.zip` |
| 执行超时 | **300 秒**(默认 3 秒太短,AI 接口会超时) |
| 内存 | 512 MB(默认 256 可能不够) |
| 初始化超时 | 60 秒 |

6. 点「完成」或「确定」
7. 等 1-2 分钟部署完成

---

## 6. 第五步:配置环境变量

部署完成后,在函数详情页 → 「函数配置」→ 「环境变量」→ 点编辑。

把下面这些变量一个个加进去(**所有值都换成你自己的**):

```
# ===== 必须填的 =====
IS_PRODUCTION=true
DATABASE_URL=postgresql://postgres:你的密码@db.xxxx.supabase.co:5432/postgres
DB_SSLMODE=require
SECRET_KEY=用 openssl rand -hex 32 生成的64位字符串
CORS_ORIGINS=*

# ===== AI(混元,可选,不配就走 mock)=====
HUNYUAN_API_KEY=你的混元API Key
HUNYUAN_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
HUNYUAN_MODEL=hunyuan-pro

# ===== 腾讯云 COS(可选,不配就存 base64)=====
COS_SECRET_ID=AKIDxxxxxxxxxxxx
COS_SECRET_KEY=xxxxxxxxxxxxxx
COS_BUCKET=studymate-1250000000
COS_REGION=ap-guangzhou

# ===== 通义千问(可选,图片识别用)=====
QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_VISION_MODEL=qwen-vl-max
```

### 怎么生成 SECRET_KEY

本地命令行跑:
```bash
openssl rand -hex 32
```
会输出一长串随机字符,复制粘贴进去。

---

## 7. 第六步:测试后端接口

### 7.1 获取 HTTP 访问地址

云函数详情页 → 「触发器」→ 找到 HTTP 触发器的访问路径。
应该长这样:
```
https://你的环境ID.service.tcloudbase.com/studymate-api
```
或者:
```
https://你的环境ID.tcloudbaseapp.com/api
```

复制这个地址,后面叫它 `BACKEND_URL`。

### 7.2 浏览器测试

打开 `BACKEND_URL/docs`,应该能看到 FastAPI 的 Swagger 文档页面。
能看到就说明后端跑起来了。

### 7.3 注册测试账号

用 curl 或者 Postman:

```bash
curl -X POST BACKEND_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@studymate.com","password":"123456","nickname":"测试用户"}'
```

返回 `access_token` 就成功了。

### 7.4 测试 AI 接口

```bash
# 先登录拿 token
TOKEN=$(curl -s -X POST BACKEND_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@studymate.com","password":"123456"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 调 AI 生成计划
curl -X POST BACKEND_URL/api/ai/plan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exam_name":"考研","exam_date":"2026-12-20","target_scores":{"math":120},"daily_study_time":480,"weak_points":["数学","英语"],"study_phase":"基础阶段"}'
```

返回 `plan` 字段就是 AI 生成的结果。
- 如果有 `phases` 数组且内容合理 → 混元 API 工作正常
- 如果内容是固定的「基础阶段/强化阶段/冲刺阶段」→ 走的是 mock,检查 API Key 配没配

---

## 8. 第七步:怎么确认 1 亿 Token 福利在消耗

如果你用的是 **方案 A(CloudBase AI 代理)**:

1. CloudBase 控制台 → 你的环境 → 左侧「AI」
2. 「生文模型」→ 看「已用 / 剩余」额度
3. 调一次 AI 接口后刷新,剩余额度应该减少

如果你用的是 **方案 B(混元官方 API)**:**不消耗福利**,走的是自购 Token。
要消耗福利必须走 CloudBase AI 模块的代理接口。

### 怎么判断自己走的是不是福利

最简单的方法:把 `HUNYUAN_API_KEY` 故意填错。
- 调 AI 接口报错 401 → 说明走的是官方 API(不是福利)
- 调 AI 接口还能用 → 说明走的是 CloudBase 内部代理(用的福利)

---

## 9. 常见问题

### Q1:云函数部署失败 / 启动报错

**A**:大概率是依赖问题。CloudBase 会自动根据 `requirements.txt` 装依赖,但有时候网络慢。
- 看「日志监控」→ 「函数日志」找报错
- 常见错误:`ModuleNotFoundError: No module named 'xxx'` → 检查 requirements.txt
- 或者在云函数控制台的「函数代码」里在线编辑,手动补包

### Q2:数据库连不上

**A**:
- 检查 `DATABASE_URL` 里的密码对不对
- Supabase 控制台 → Project Settings → Database → Connection Pooler → 试试用连接池地址
- `DB_SSLMODE` 必须是 `require`(Supabase 强制 SSL)
- Supabase 有没有开 Network restrictions?关了试试

### Q3:AI 接口超时

**A**:云函数超时设太短了。
- 控制台 → 函数配置 → 「执行超时」改到 **300 秒**
- 另外混元接口本身有时候慢,正常

### Q4:上传图片失败

**A**:
- COS 的四个环境变量都填了吗?
- COS 存储桶权限是不是「公有读私有写」?
- COS CORS 跨域规则配了吗?(H5 端需要,小程序端不需要)

### Q5:CORS 跨域报错(H5 端调不了)

**A**:环境变量 `CORS_ORIGINS` 加你的 H5 域名:
```
CORS_ORIGINS=https://studymate.vercel.app,https://你的域名.com
```
多个域名用逗号分隔。

### Q6:6 个月后 CloudBase 到期了怎么办

**A**:三个选择:
1. 续费 CloudBase 个人版(约 19.9 元/月)
2. 迁移到腾讯云 SCF(100 万次/月免费,但 AI 福利没了)
3. 迁移到腾讯云轻量服务器(60-100 元/年,最划算,所有服务自部署)

到时候再说,先用 6 个月免费的。

---

## 下一步

后端跑通了之后,下一步是部署前端(H5 到 Vercel,小程序到微信)。
需要的话告诉我,我继续写教程。

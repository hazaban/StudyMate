# StudyMate 双端部署完整教学(电脑网页 + 手机小程序)

> 本文档教你把 StudyMate 同时部署到 **电脑网页(H5)** 和 **微信小程序(手机)**,充分利用你已有的三项资源:微信「AI 小程序成长计划」福利、腾讯云 COS 50G、Supabase 数据库。
>
> 完成后:电脑浏览器打开网址能用,微信里搜小程序也能用,两端数据互通。

---

## 目录

- [第零部分:总览](#第零部分总览)
- [第一部分:准备工作(账号与资源开通)](#第一部分准备工作账号与资源开通)
- [第二部分:数据库配置(Supabase)](#第二部分数据库配置supabase)
- [第三部分:图片存储配置(腾讯云 COS)](#第三部分图片存储配置腾讯云-cos)
- [第四部分:AI 服务配置(腾讯混元)](#第四部分ai服务配置腾讯混元)
- [第五部分:后端部署(CloudBase HTTP 云函数)](#第五部分后端部署cloudbase-http-云函数)
- [第六部分:小程序端配置与发布](#第六部分小程序端配置与发布)
- [第七部分:H5 端部署(电脑网页)](#第七部分h5-端部署电脑网页)
- [第八部分:联调测试与常见问题](#第八部分联调测试与常见问题)
- [附录 A:费用清单](#附录-a费用清单)
- [附录 B:各服务入口链接](#附录-b各服务入口链接)
- [附录 C:需要修改的文件清单](#附录-c需要修改的文件清单)

---

## 第零部分:总览

### 0.1 你已有的资源

| 资源 | 来源 | 价值 | 用途 |
|------|------|------|------|
| CloudBase 6 个月个人版环境 | AI 小程序成长计划 | ~120 元 | 部署后端 FastAPI |
| 1 亿混元 Token | AI 小程序成长计划 | ~5400 元 | AI 生成计划/任务/卡片 |
| 1 万张混元文生图 | AI 小程序成长计划 | ~500 元 | (本项目暂未用,备用) |
| 腾讯云 COS 50G/年 | 已有 | ~50 元 | 图片存储(错题/卡片图) |
| Supabase PostgreSQL | 已注册 | 免费 500MB | 主数据库 |

### 0.2 最终架构图

```
┌──────────────────────┐                ┌──────────────────────────┐
│  电脑网页 H5         │                │  微信小程序(手机)       │
│  Vercel 部署         │                │  微信开发者工具上传      │
│  UniApp 编译 H5      │                │  UniApp 编译 mp-weixin   │
└──────────┬───────────┘                └──────────┬───────────────┘
           │                                       │
           │  HTTPS(已备案域名)                   │  wx.cloud.callFunction
           │                                       │  (走 CloudBase,免域名白名单)
           ↓                                       ↓
┌────────────────────────────────────────────────────────────────────┐
│  CloudBase HTTP 云函数(FastAPI,6 个月免费)                       │
│   ├─ 认证 / 计划 / 任务 / 卡片 / 错题 / 农场 / 番茄(CRUD)          │
│   ├─ AI 代理 → 混元 API(消耗 1 亿 Token 福利)                     │
│   └─ 上传签名 → 腾讯云 COS(50G)                                   │
└────────────────────────────────────────────────────────────────────┘
           │
           ↓
┌──────────────────────────┐
│  Supabase PostgreSQL     │
│  (已注册,500MB 免费)     │
└──────────────────────────┘
```

### 0.3 三个必须先搞懂的关键认知

**① AI 福利的 1 亿 Token 有使用限制**
官方原文:"仅限微信小程序和云开发控制台中调用"。
含义:这 1 亿 Token **不能**从 H5 浏览器直接调混元 API 来用。但**CloudBase 云函数属于云开发环境,云函数里调混元算"云开发控制台中调用"**,所以后端云函数里调混元是合规的——H5 端通过后端云函数间接调用,也就能用上这 1 亿 Token。

**② 腾讯云 API 网关已于 2025-06-30 停服**
老教程里说的"SCF + API 网关"方案已不可用。现在两条路:
- CloudBase HTTP 云函数(推荐,自带 HTTPS 域名,与 AI 福利同账号)
- SCF 的"函数 URL + 自定义域名"(需要自己备案域名)

本文档选 **CloudBase HTTP 云函数**,因为它和你的 AI 福利在同一个账号下,且自带 HTTPS 访问域名,免去自己配域名/证书的麻烦。

**③ 个人开发者小程序的类目限制**
原文:"当前平台未开放个人开发者备案【深度合成】类目权限,个人开发者可上架与大模型交互无关的线上工具小程序"。
StudyMate 的 AI 生成功能虽然调大模型,但**用户感知上是个学习工具**,建议类目选「工具」或「教育」,把 AI 作为辅助能力。审核时若被问及,说明 AI 仅用于生成学习建议,不做对话/生成内容传播,通常能过。若卡在深度合成类目,可暂时关闭小程序端的 AI 入口,只保留 H5 端 AI。

### 0.4 全程费用预估

| 项目 | 费用 | 说明 |
|------|------|------|
| CloudBase 环境(6 个月) | 0 元 | AI 成长计划福利 |
| 混元 AI Token(1 亿) | 0 元 | AI 成长计划福利,够个人用半年以上 |
| 腾讯云 COS | 0 元 | 50G/年免费额度内 |
| Supabase | 0 元 | 500MB 免费层 |
| 微信小程序注册(个人) | 0 元 | 个人主体免费 |
| 域名(.com) | 50-70 元/年 | 必须买,H5 和小程序后端都要 |
| ICP 备案 | 0 元 | 免费,但需 7-20 天 |
| SSL 证书 | 0 元 | CloudBase 自带,或腾讯云免费 DV |
| Vercel(H5 前端) | 0 元 | 免费层够用 |
| **6 个月内总计** | **50-70 元** | 只花在域名上 |
| **6 个月后(CloudBase 到期)** | 约 20-50 元/月 | 续费 CloudBase 或迁移到 SCF |

### 0.5 时间预估

| 阶段 | 耗时 | 是否阻塞下一步 |
|------|------|----------------|
| 域名购买 + ICP 备案 | 7-20 天 | ✅ 阻塞小程序上线(不阻塞 H5) |
| 微信小程序注册 | 1-3 天 | ✅ 阻塞小程序端 |
| AI 成长计划报名 | 即时 | 不阻塞 |
| Supabase 配置 | 30 分钟 | 不阻塞 |
| COS 配置 | 30 分钟 | 不阻塞 |
| 后端部署 CloudBase | 1-2 小时 | 不阻塞 |
| H5 部署 Vercel | 30 分钟 | 不阻塞 |
| 小程序编译上传审核 | 1-7 天审核 | 阻塞上线 |

**建议立即并行启动**:① 域名备案 ② 小程序注册 ③ AI 成长计划报名。这三件最慢,先办。

---

## 第一部分:准备工作(账号与资源开通)

### 1.1 微信小程序账号注册(个人主体)

1. 打开 https://mp.weixin.qq.com/
2. 右上角「立即注册」→ 选择「小程序」
3. 邮箱注册(每个邮箱只能注册一种微信号,建议用新邮箱)
4. 邮箱激活 → 选择主体类型「个人」
5. 填写身份证 + 微信扫码绑定管理员
6. 完成后,**记录下你的 AppID**(后台 → 开发 → 开发管理 → 开发设置 → AppID),形如 `wx1234567890abcdef`

**类目选择**:后台 → 设置 → 基本设置 → 服务类目 → 选「工具」或「教育-在线教育」。**不要选「深度合成」**(个人不能选)。

### 1.2 报名「AI 小程序成长计划」领取福利

**前提**:小程序类目必须是 文娱/工具/社交/深度合成/资讯 之一。StudyMate 选「工具」即可。

1. 登录微信小程序后台 https://mp.weixin.qq.com/
2. 左侧导航 → 「行业能力」→ 「AI 小程序成长计划」
   - 如果看不到这个菜单:检查类目是否合规,或账号是否已完成基本资料填写
3. 点击「参与计划」→ 选择「开发上线」阶段
4. 跳转到腾讯云登录页 → 用微信扫码登录(首次会引导实名认证)
5. 在弹窗中选择「领取的账号」和「云开发环境」
   - 如果没有环境,会自动为你创建一个 6 个月免费个人版环境
6. 领取成功后,会显示:
   - **环境 ID**(形如 `studymate-xxxxx`),记下来
   - 1 亿混元 Token 已到账
   - 1 万张文生图额度已到账

**验证福利到账**:
1. 打开 CloudBase 控制台 https://console.cloud.tencent.com/tcb
2. 选择你的环境 → 左侧「AI」→ 「生文模型」→ 看到 1 亿 Token 额度
3. 「生图模型」→ 看到 1 万张额度

### 1.3 腾讯云账号实名认证

如果 1.2 步已完成,你的腾讯云账号已绑定。补充确认:
1. 打开 https://console.cloud.tencent.com/
2. 右上角头像 → 「账号信息」→ 确认实名认证状态为「个人认证」
3. 如果未认证:点击「提交认证」→ 微信扫码 + 身份证 → 即时通过

### 1.4 域名购买与 ICP 备案(关键,耗时最长)

**为什么需要域名**:
- H5 端:Vercel 会给你一个 `.vercel.app` 子域名,**不需要备案**
- 小程序端:CloudBase 云函数会给你一个 `xxx.tcloudbaseapp.com` 域名,**也不需要备案**
- 但小程序要求后端域名必须是已备案的**自有域名**(CloudBase 默认域名可能不被小程序接受,且不稳定)

**所以**:为了小程序端稳定可用,建议买一个域名并备案。H5 端可以先用 Vercel 免费域名跑起来。

**步骤**:
1. 买域名:推荐腾讯云/阿里云/Namesilo
   - 腾讯云:https://buy.cloud.tencent.com/domain(国内注册需实名)
   - Namesilo:https://www.namesilo.com(国外注册,价格便宜,但备案要国内注册商)
   - 推荐选 `.com`,费用 50-70 元/年
2. 域名实名认证:在注册商后台完成(身份证 1-3 天通过)
3. ICP 备案(国内服务器才需要):
   - 腾讯云控制台 → 「网站备案」→ 「开始备案」
   - 准备:身份证、手机、域名、云服务器(备案需要云服务器,CloudBase 不算)
   - **坑**:备案要求有云服务器,但你可以买最便宜的轻量服务器(学生机 9.9 元/月)仅用于备案,或借用朋友的服务器
   - 流程:填资料 → 拍幕布照 → 提交 → 腾讯云初审 → 工信部审核 → 7-20 天
4. 备案通过后,域名可用作小程序后端域名

**没有备案怎么办**:H5 端照常部署到 Vercel(免备案);小程序端先用 CloudBase 默认域名(`xxx.tcloudbaseapp.com`)测试,正式上线再换备案域名。

---

## 第二部分:数据库配置(Supabase)

### 2.1 创建 Supabase 项目(如已注册可跳过)

1. 打开 https://supabase.com/ → 登录
2. 「New Project」→ 填写:
   - Name: `studymate`
   - Database Password: 自定义强密码,**记下来**
   - Region: Southeast Asia (Singapore) - 离中国近
3. 等待 2 分钟初始化完成

### 2.2 获取连接串

1. 进入项目 → 左下角「Project Settings」(齿轮图标)
2. 「Database」→ 「Connection string」→ 选「URI」格式
3. 复制连接串,形如:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxx.supabase.co:5432/postgres
   ```
4. 把 `[YOUR-PASSWORD]` 替换成你 2.1 步设置的密码

**记下这个完整的 URL**,后面要用。

### 2.3 配置网络访问

Supabase 默认允许所有 IP 连接,无需额外配置。但建议加限制:
1. 项目 → 「Database」→ 「Network restrictions」
2. 添加允许的 IP(可选,初始阶段保持开放)

### 2.4 初始化表结构

表结构由后端代码自动创建(FastAPI 启动时 `init_db()`)。部署后端后,首次启动会自动建好 8 张表(users / study_plans / daily_tasks / flash_cards / mistakes / plants / farm_states / focus_records / user_subjects)。

如果你想手动验证表是否建好:
1. Supabase 控制台 → 「SQL Editor」
2. 执行:`SELECT tablename FROM pg_tables WHERE schemaname = 'public';`
3. 应看到 8 张表

---

## 第三部分:图片存储配置(腾讯云 COS)

### 3.1 创建存储桶

1. 打开 https://console.cloud.tencent.com/cos
2. 「存储桶列表」→ 「创建存储桶」
3. 填写:
   - 名称:`studymate-1250000000`(1250000000 替换为你的 APPID,控制台右上角能看到)
   - 地域:ap-guangzhou(广州,与 CloudBase 环境同地域)
   - 访问权限:**公有读私有写**(图片可读,上传需鉴权)
4. 高级设置 → 默认加密:关 → 完成

### 3.2 获取 API 密钥

1. 打开 https://console.cloud.tencent.com/cam/capi
2. 「新建密钥」→ 复制:
   - **SecretId**
   - **SecretKey**
3. (推荐)创建子账号 + 最小权限:
   - 访问管理 → 用户 → 新建用户 → 选择「编程访问」
   - 关联策略:`QcloudCOSDataWriteOnly` 和 `QcloudCOSDataReadOnly`
   - 用子账号的密钥(主账号密钥泄露风险大)

### 3.3 配置 CORS 跨域规则(关键)

否则 H5 端无法直传图片到 COS。

1. COS 控制台 → 你的存储桶 → 「安全管理」→ 「跨域访问 CORS 设置」
2. 「添加规则」:
   - Origin: `*`(开发期);生产期填具体域名,如 `https://你的域名.vercel.app`
   - Methods: `GET, POST, PUT, HEAD`
   - Headers: `*`
   - Expose-Headers: `ETag, Content-Length`
   - Timeout: 600 秒

### 3.4 记录配置值

记下这 4 个值,后面配置后端环境变量要用:
```
COS_SECRET_ID=AKIDxxxxxxxxxxxx
COS_SECRET_KEY=xxxxxxxxxxxxxx
COS_BUCKET=studymate-1250000000
COS_REGION=ap-guangzhou
```

---

## 第四部分:AI 服务配置(腾讯混元)

你的项目当前用 DeepSeek + 通义千问。我们改成腾讯混元,以利用 1 亿 Token 福利。

### 4.1 理解两条接入路径

**路径 A:CloudBase 内置混元(走 1 亿 Token 福利,推荐)**
- 调用方:CloudBase 云函数内部
- 鉴权:CloudBase SDK 自动处理,无需 API Key
- 计费:消耗 1 亿 Token 福利
- 限制:只能在云函数/小程序里调

**路径 B:混元 OpenAI 兼容 API(自购 Token)**
- Base URL: `https://api.hunyuan.cloud.tencent.com/v1`
- 鉴权:Bearer Token(API Key)
- 计费:自购 Token 包
- 限制:无,任何地方都能调

**本文档用路径 A**(云函数内调 CloudBase AI SDK,消耗福利 Token)。

### 4.2 在 CloudBase 控制台确认 AI 模型可用

1. CloudBase 控制台 → 你的环境 → 「AI」→ 「生文模型」
2. 确认看到「混元」模型已激活,1 亿 Token 额度
3. 记下模型 ID,通常是 `hunyuan-pro` 或 `cloudbase` (CloudBase 代理入口)

### 4.3 修改后端 AI 服务代码

需要改两个文件:

**改动 1:[server/services/ai_service.py](file:///workspace/studymate-uniapp/server/services/ai_service.py)**

把 `_call_deepseek` 函数改为调用 CloudBase AI SDK。由于云函数环境内调用 CloudBase AI 用的是 `tcb-admin-node` 或 Python SDK,最简方式是直接走 HTTP。

实际上 CloudBase 云函数里调混元最稳的方式是用 CloudBase 的 Python SDK,但官方主推 Node.js。对于 Python FastAPI,我们用 **OpenAI 兼容接口 + CloudBase 的 AI 代理 URL**。

具体改法:

```python
# 把文件顶部的 import 改为:
import json
import base64
import os
import httpx
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_VISION_MODEL

# CloudBase AI 代理配置(从环境变量读)
CLOUDBASE_AI_URL = os.getenv("CLOUDBASE_AI_URL", "")
CLOUDBASE_AI_TOKEN = os.getenv("CLOUDBASE_AI_TOKEN", "")
HUNYUAN_MODEL = os.getenv("HUNYUAN_MODEL", "hunyuan-pro")


async def _call_deepseek(messages: list[dict], model: str = None, temperature: float = 0.7) -> str:
    """Call Hunyuan AI via CloudBase proxy (uses free 1B Token quota)."""
    if not CLOUDBASE_AI_URL:
        return _mock_response(messages[-1]["content"])

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{CLOUDBASE_AI_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {CLOUDBASE_AI_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "model": HUNYUAN_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4096
            }
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
```

**改动 2:[server/config.py](file:///workspace/studymate-uniapp/server/config.py)**

在文件末尾追加:
```python
# CloudBase AI(走 1 亿混元 Token 福利)
CLOUDBASE_AI_URL = os.getenv("CLOUDBASE_AI_URL", "")
CLOUDBASE_AI_TOKEN = os.getenv("CLOUDBASE_AI_TOKEN", "")
HUNYUAN_MODEL = os.getenv("HUNYUAN_MODEL", "hunyuan-pro")
```

**改动 3:[server/services/ai_service.py](file:///workspace/studymate-uniapp/server/services/ai_service.py) 的 import**

把顶部的:
```python
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL_FLASH, DEEPSEEK_MODEL_PRO,
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_VISION_MODEL
)
```
改为:
```python
from config import (
    CLOUDBASE_AI_URL, CLOUDBASE_AI_TOKEN, HUNYUAN_MODEL,
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_VISION_MODEL
)
```

**获取 CLOUDBASE_AI_URL 和 Token**:
1. CloudBase 控制台 → 你的环境 → 「AI」→ 「生文模型」→ 「API 调用」
2. 复制「请求地址」(形如 `https://tcb-api.tencentcloudapi.com/api/v2/ai/chat/completions`)
3. Token:在「环境设置」→ 「API Key」里生成

> ⚠️ 如果 CloudBase AI 代理 URL 不好找或配置复杂,**退路**:用路径 B(直接调混元 OpenAI 兼容 API),需要自购 Token 包(1000 Token = 1 元,个人用每月约 5-10 元)。改法是把 `CLOUDBASE_AI_URL` 设为 `https://api.hunyuan.cloud.tencent.com/v1`,`CLOUDBASE_AI_TOKEN` 设为你在 https://console.cloud.tencent.com/hunyuan 申请的 API Key。

### 4.4 关于图片识别(通义千问)

`analyze_syllabus_image` 函数用的是通义千问 Qwen-VL,用于识别教材目录图片。这一块**保持不变**:
- 如果你有通义千问 API Key → 填上,功能可用
- 如果没有 → 后端会返回 mock 数据(不影响其他功能)

如果要改成混元的视觉模型,模型名换成 `hunyuan-vision`,API 走同样的 OpenAI 兼容接口。

---

## 第五部分:后端部署(CloudBase HTTP 云函数)

### 5.1 安装 CloudBase CLI

本地开发机执行(假设已装 Node.js):
```bash
npm install -g @cloudbase/cli
tcb login  # 微信扫码登录
```

### 5.2 准备云函数代码

在项目根目录创建 `cloudbase-functions/studymate-api/` 文件夹,结构如下:

```
cloudbase-functions/
└── studymate-api/
    ├── index.py            # 入口,用 Mangum 包 FastAPI
    ├── main.py             # 从 server/main.py 复制
    ├── config.py           # 从 server/config.py 复制(已改)
    ├── database.py         # 从 server/database.py 复制
    ├── routes/             # 从 server/routes/ 复制
    ├── schemas/            # 从 server/schemas/ 复制
    ├── services/           # 从 server/services/ 复制(已改)
    ├── requirements.txt    # 从 server/requirements.txt 复制
    └── .env                # 环境变量(见 5.3)
```

**`index.py` 内容**(从 [server/api/index.py](file:///workspace/studymate-uniapp/server/api/index.py) 复制并调整):
```python
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mangum import Mangum
from main import app

# CloudBase HTTP 云函数的 handler
handler = Mangum(app, lifespan="off")
```

**`requirements.txt` 增加 CloudBase SDK**(可选,用于直接调 CloudBase AI):
```
# 在原 requirements.txt 基础上追加:
tencentcloud-sdk-python-cloudbase>=3.0.1000
```

### 5.3 配置环境变量

在 `cloudbase-functions/studymate-api/.env` 文件填入(从各处收集的值):

```ini
# ===== 生产环境标记 =====
IS_PRODUCTION=true

# ===== 数据库(Supabase)=====
DATABASE_URL=postgresql://postgres:你的密码@db.xxxxxxxx.supabase.co:5432/postgres
DB_SSLMODE=require

# ===== JWT 密钥(自己生成)=====
# 本地执行:openssl rand -hex 32
SECRET_KEY=你生成的64位随机字符串
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ===== CORS =====
CORS_ORIGINS=*,https://你的域名.vercel.app

# ===== 腾讯云 COS =====
COS_SECRET_ID=AKIDxxxxxxxxxxxx
COS_SECRET_KEY=xxxxxxxxxxxxxx
COS_BUCKET=studymate-1250000000
COS_REGION=ap-guangzhou

# ===== CloudBase AI(混元 1 亿 Token 福利)=====
CLOUDBASE_AI_URL=https://api.hunyuan.cloud.tencent.com/v1
CLOUDBASE_AI_TOKEN=你的混元API Key
HUNYUAN_MODEL=hunyuan-pro

# ===== 通义千问(可选,图片识别)=====
QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_VISION_MODEL=qwen-vl-max

# ===== 服务器端口(CloudBase 自动注入,可不填)=====
PORT=8002
```

### 5.4 部署到 CloudBase

**方式 A:控制台上传(最简单)**

1. CloudBase 控制台 → 你的环境 → 「云函数」→ 「新建云函数」
2. 选择「HTTP 云函数」
3. 填写:
   - 函数名称:`studymate-api`
   - 运行时:**Python 3.10**(注意:CloudBase 目前支持 Python 3.7/3.10,你的代码用了 3.10+ 特性如 `list[dict]`,选 3.10)
   - 内存:512MB(默认 256MB 可能不够,AI 调用要更多)
   - 执行超时:**300 秒**(关键!默认 3 秒,AI 接口会超时)
   - 提交方法:「本地上传文件夹」→ 选择 `cloudbase-functions/studymate-api/`
4. 「环境变量」:把 5.3 的所有变量填入(不要填 `IS_PRODUCTION=true`,CloudBase 会自动注入 `TENCENTCLOUD_RUNENV`,后端代码已适配)
5. 「完成」→ 等待部署(2-3 分钟)

**方式 B:CLI 部署(适合后续更新)**

在项目根目录创建 `cloudbaserc.json`:
```json
{
  "envId": "你的环境ID",
  "functions": [{
    "name": "studymate-api",
    "config": {
      "runtime": "Python3.10",
      "memorySize": 512,
      "timeout": 300
    },
    "source": "cloudbase-functions/studymate-api",
    "env": {
      "DATABASE_URL": "postgresql://postgres:...",
      "SECRET_KEY": "...",
      "COS_SECRET_ID": "...",
      "COS_SECRET_KEY": "...",
      "COS_BUCKET": "...",
      "COS_REGION": "ap-guangzhou",
      "CLOUDBASE_AI_URL": "https://api.hunyuan.cloud.tencent.com/v1",
      "CLOUDBASE_AI_TOKEN": "...",
      "HUNYUAN_MODEL": "hunyuan-pro"
    },
    "triggers": [{
      "name": "http",
      "type": "timer",
      "config": ""
    }]
  }]
}
```

执行部署:
```bash
tcb fn deploy studymate-api
```

### 5.5 配置 HTTP 触发器(获取访问 URL)

1. CloudBase 控制台 → 云函数 → `studymate-api` → 「触发器」
2. 「创建触发器」→ 类型「HTTP 触发」
3. 路径:`/api`(或 `/`)
4. 方法:`ANY`
5. 创建后,获得访问 URL,形如:
   ```
   https://你的环境ID.tcloudbaseapp.com/api
   ```
6. 浏览器访问该 URL,应看到 FastAPI 默认返回 `{"detail": "Not Found"}` 或类似

### 5.6 配置自定义域名(可选,推荐)

CloudBase 默认域名 `xxx.tcloudbaseapp.com` 可用于 H5,但小程序要求后端域名在小程序后台「request 合法域名」白名单里,且建议用自有域名。

1. CloudBase 控制台 → 「静态网站托管」→ 「自定义域名」(或云函数的「访问域名」)
2. 添加你的备案域名,如 `api.你的域名.com`
3. 按提示在域名 DNS 加 CNAME 记录
4. 启用 HTTPS(用腾讯云免费 DV 证书)
5. 配置完成后,访问 `https://api.你的域名.com/api` 应能通

**记下后端最终 URL**:
- CloudBase 默认:`https://你的环境ID.tcloudbaseapp.com/api`
- 自定义域名:`https://api.你的域名.com/api`

---

## 第六部分:小程序端配置与发布

### 6.1 填写小程序 AppID

修改 [src/manifest.json](file:///workspace/studymate-uniapp/src/manifest.json) 第 18-23 行:

```json
"mp-weixin": {
  "appid": "wx1234567890abcdef",  ← 替换成你 1.1 步拿到的 AppID
  "setting": {
    "urlCheck": false,  ← 开发期关掉,上线前要打开
    "es6": true,
    "postcss": true,
    "minified": true
  },
  "usingComponents": true
}
```

### 6.2 修改前端 API 地址

修改 [src/api/client.js](file:///workspace/studymate-uniapp/src/api/client.js) 第 3 行,做条件编译:

```javascript
// 原来:
// const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 改为:
let BASE_URL
// #ifdef H5
BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
// #endif
// #ifdef MP-WEIXIN
BASE_URL = 'https://api.你的域名.com/api'  // 或 CloudBase 默认域名
// #endif
// #ifndef H5 || MP-WEIXIN
BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
// #endif
```

### 6.3 配置小程序合法域名白名单(关键!)

1. 登录微信小程序后台 https://mp.weixin.qq.com/
2. 「开发」→ 「开发管理」→ 「开发设置」→ 「服务器域名」→ 「修改」
3. 添加:
   - **request 合法域名**:`https://api.你的域名.com`(或 `https://你的环境ID.tcloudbaseapp.com`)
   - **uploadFile 合法域名**:`https://studymate-1250000000.cos.ap-guangzhou.myqcloud.com`(COS 上传地址)
   - **downloadFile 合法域名**:同上,加 `https://studymate-1250000000.cos.ap-guangzhou.myqcloud.com`
4. 保存(每月可改 50 次)

### 6.4 编译小程序

本地开发机:
```bash
cd /workspace/studymate-uniapp
npm run dev:mp-weixin
```

编译产物在 `dist/dev/mp-weixin/`。

### 6.5 微信开发者工具上传

1. 下载微信开发者工具:https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
2. 打开 → 导入项目 → 选择 `dist/dev/mp-weixin/` 目录
3. AppID 填你的真实 AppID
4. 在工具里预览调试,确认功能正常
5. 调试无误后,生产构建:
   ```bash
   npm run build:mp-weixin
   ```
   产物在 `dist/build/mp-weixin/`
6. 微信开发者工具导入 `dist/build/mp-weixin/`
7. 右上角「上传」→ 填版本号(1.0.0)→ 备注 → 上传

### 6.6 提交审核

1. 微信小程序后台 → 「管理」→ 「版本管理」
2. 找到刚上传的版本 → 「提交审核」
3. 填写审核信息:
   - 类目:工具 / 教育(与 1.1 一致)
   - 功能:学习计划管理、复习卡片、错题本、番茄钟、农场
   - 测试账号:`test@studymate.com / 123456`(记得先在后端注册一个)
4. 提交 → 1-7 天审核
5. 审核通过 → 「发布」→ 小程序上线

### 6.7 小程序端调用 AI 的特殊优化(可选,省 Token)

如果你想让小程序端的 AI 调用**不经过你的后端**而直接走 CloudBase AI(省 1 亿 Token,且更快),可以在小程序端用 CloudBase SDK:

```javascript
// 在 src/api/ai.js 新增
// #ifdef MP-WEIXIN
export async function mpCallAI(prompt) {
  const res = await wx.cloud.callFunction({
    name: 'studymate-ai-proxy',  // 单独建一个轻量云函数只做AI转发
    data: { prompt }
  })
  return res.result
}
// #endif
```

需要单独建一个 `studymate-ai-proxy` 云函数调 CloudBase AI SDK。这是进阶优化,初版可不做。

---

## 第七部分:H5 端部署(电脑网页)

### 7.1 修改前端环境变量

在 [studymate-uniapp/.env.example](file:///workspace/studymate-uniapp/.env.example) 同目录创建 `.env.production`:

```ini
VITE_API_BASE_URL=https://api.你的域名.com/api
```

或用 CloudBase 默认域名:
```ini
VITE_API_BASE_URL=https://你的环境ID.tcloudbaseapp.com/api
```

### 7.2 部署到 Vercel(免备案,推荐)

1. 把代码推到 GitHub(如果还没推):
   ```bash
   git add -A && git commit -m "deploy: dual endpoint" && git push
   ```
2. 打开 https://vercel.com/ → 用 GitHub 登录
3. 「New Project」→ 选你的 StudyMate 仓库
4. 配置:
   - **Root Directory**:`studymate-uniapp`
   - **Build Command**:`npm run build:h5`
   - **Output Directory**:`dist/build/h5`
   - **Environment Variables**:
     - `VITE_API_BASE_URL` = `https://api.你的域名.com/api`
5. 「Deploy」→ 等 1-2 分钟
6. 部署完成,获得 `https://studymate-xxxx.vercel.app`

**绑定自定义域名**(可选):
1. Vercel 项目 → 「Settings」→ 「Domains」
2. 添加 `app.你的域名.com`
3. 在域名 DNS 加 CNAME 到 `cname.vercel-dns.com`
4. Vercel 自动签发 SSL 证书

### 7.3 备选:部署到 CloudBase 静态托管

如果你想 H5 和后端在同一账号下管理:
1. CloudBase 控制台 → 「静态网站托管」
2. 上传 `dist/build/h5/` 目录所有文件
3. 获得 `https://你的环境ID.tcloudbaseapp.com`
4. 可绑定自定义域名 `app.你的域名.com`

**注意**:CloudBase 静态托管的默认域名国内访问需要备案,**Vercel 不用备案**。所以 H5 推荐 Vercel。

---

## 第八部分:联调测试与常见问题

### 8.1 测试账号准备

后端部署后,先用 curl 注册一个测试账号:
```bash
curl -X POST https://api.你的域名.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@studymate.com","password":"123456","nickname":"测试用户"}'
```

### 8.2 功能验证清单

**H5 端**(浏览器打开 `https://studymate-xxxx.vercel.app`):

- [ ] 注册新账号 → 自动登录
- [ ] 登录已有账号(test@studymate.com)
- [ ] 创建学习计划(手动)
- [ ] AI 生成学习计划(消耗混元 Token)
- [ ] 添加每日任务
- [ ] AI 生成今日任务
- [ ] 创建知识卡片
- [ ] AI 生成卡片
- [ ] 上传图片到卡片(消耗 COS)
- [ ] 创建错题
- [ ] 上传错题图片
- [ ] 番茄钟专注 → 记录入库
- [ ] 农场种植物 / 浇水 / 收获
- [ ] 修改个人资料
- [ ] 统计页查看数据

**小程序端**(微信开发者工具):

- [ ] 同上所有功能
- [ ] 微信登录(如果实现了 wx.login)
- [ ] 图片上传(COS 直传,检查合法域名配置)

### 8.3 常见问题排查

**Q1: 小程序请求报错「不在合法域名列表」**
A: 后台「服务器域名」没加,或域名没加 `https://` 前缀。重新加白名单,重启开发者工具。

**Q2: H5 跨域报错 CORS**
A: 后端 [config.py](file:///workspace/studymate-uniapp/server/config.py) 的 `CORS_ORIGINS` 没包含你的 H5 域名。在云函数环境变量里加 `CORS_ORIGINS=https://你的H5域名.vercel.app,https://你的自定义域名`(逗号分隔)。

**Q3: AI 接口超时**
A: 云函数超时设短了。CloudBase 控制台 → 云函数 → studymate-api → 配置 → 执行超时改到 300 秒。

**Q4: AI 返回 mock 数据**
A: `CLOUDBASE_AI_URL` 或 `CLOUDBASE_AI_TOKEN` 没配,或配错了。检查云函数环境变量。

**Q5: 数据库连接失败**
A:
- Supabase 连接串密码错 → 重新复制
- Supabase 网络限制 → 暂时关闭 Network restrictions
- SSL 模式 → 确认 `DB_SSLMODE=require`

**Q6: 图片上传失败**
A:
- COS 密钥错 → 重新获取
- COS CORS 没配 → 见 3.3
- COS 存储桶权限错 → 确认「公有读私有写」

**Q7: 小程序审核被拒「深度合成」**
A: 临时方案——在小程序端隐藏 AI 入口(注释掉 [src/pages/plan/ai-plan.vue](file:///workspace/studymate-uniapp/src/pages/plan/ai-plan.vue) 的入口),只保留 H5 端 AI。或换企业主体。

**Q8: CloudBase 默认域名访问不了**
A: 默认域名 `xxx.tcloudbaseapp.com` 在国内可能需要备案。换自定义备案域名,或先用 Vercel 跑 H5,小程序等备案下来再上线。

**Q9: 6 个月后 CloudBase 到期怎么办**
A: 三个选择:
1. 续费 CloudBase 个人版(约 19.9 元/月)
2. 迁移后端到腾讯云 SCF(免费 100 万次/月,但 AI 福利没了,需自购混元 Token)
3. 迁移后端到轻量服务器(60-100 元/年,最划算)

**Q10: Python 3.10 不支持 `list[dict]` 类型注解?**
A: Python 3.9+ 支持 `list[dict]`,3.10 完全没问题。如果 CloudBase 只有 3.7,把类型注解改成 `List[dict]` 并 `from typing import List`。

---

## 附录 A:费用清单

### 6 个月内(福利期)

| 项目 | 费用 |
|------|------|
| CloudBase 环境 | 0 元(福利) |
| 混元 AI Token | 0 元(1 亿福利) |
| 腾讯云 COS | 0 元(50G 免费) |
| Supabase | 0 元(500MB 免费) |
| 微信小程序注册 | 0 元(个人) |
| 域名 | 50-70 元/年 |
| ICP 备案 | 0 元 |
| SSL 证书 | 0 元 |
| Vercel | 0 元 |
| **合计** | **50-70 元** |

### 6 个月后(续费期)

| 项目 | 月费用 | 年费用 |
|------|--------|--------|
| CloudBase 续费 | ~20 元 | ~240 元 |
| 混元 AI(自购,假设每月 10 万 Token) | ~1 元 | ~12 元 |
| COS(50G 用完后超出部分) | ~0 元 | ~0 元 |
| Supabase | 0 元 | 0 元 |
| 域名 | ~5 元 | 50-70 元 |
| **合计** | **~26 元** | **~310 元** |

**省钱方案**:6 个月后迁移到腾讯云轻量服务器(60-100 元/年),所有服务自部署,年费用降到 100-150 元。

---

## 附录 B:各服务入口链接

| 服务 | 入口 |
|------|------|
| 微信小程序后台 | https://mp.weixin.qq.com/ |
| AI 小程序成长计划 | 后台 → 行业能力 → AI 小程序成长计划 |
| CloudBase 控制台 | https://console.cloud.tencent.com/tcb |
| CloudBase 文档 | https://docs.cloudbase.net/ |
| CloudBase FastAPI 部署指南 | https://docs.cloudbase.net/cloud-function/frameworks-examples/fastapi |
| 腾讯云 COS 控制台 | https://console.cloud.tencent.com/cos |
| 腾讯云 API 密钥 | https://console.cloud.tencent.com/cam/capi |
| 腾讯云混元控制台 | https://console.cloud.tencent.com/hunyuan |
| 腾讯云 TokenHub | https://console.cloud.tencent.com/tokenhub |
| 混元 OpenAI 兼容文档 | https://cloud.tencent.com/document/product/1729/111006 |
| Supabase 控制台 | https://supabase.com/dashboard |
| Vercel | https://vercel.com/ |
| 微信开发者工具下载 | https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html |
| 域名注册(腾讯云) | https://buy.cloud.tencent.com/domain |
| ICP 备案(腾讯云) | https://console.cloud.tencent.com/beian |

---

## 附录 C:需要修改的文件清单

| 文件 | 改动内容 | 步骤 |
|------|----------|------|
| [src/manifest.json](file:///workspace/studymate-uniapp/src/manifest.json) | 填 mp-weixin AppID | 6.1 |
| [src/api/client.js](file:///workspace/studymate-uniapp/src/api/client.js) | 条件编译区分 H5/小程序 API 域名 | 6.2 |
| [server/services/ai_service.py](file:///workspace/studymate-uniapp/server/services/ai_service.py) | DeepSeek → 混元 | 4.3 |
| [server/config.py](file:///workspace/studymate-uniapp/server/config.py) | 加 CloudBase AI 配置项 | 4.3 |
| 新建 `cloudbase-functions/studymate-api/` | 云函数部署目录 | 5.2 |
| 新建 `cloudbaserc.json` | CLI 部署配置(可选) | 5.4 |
| 新建 `.env.production` | H5 构建环境变量 | 7.1 |

---

## 执行顺序建议

**第 1 天(并行启动慢任务)**:
1. 域名购买 + 启动 ICP 备案(7-20 天)
2. 微信小程序注册(1-3 天)
3. 报名 AI 成长计划(即时)
4. Supabase 创建项目(30 分钟)

**第 2-3 天(配置云资源)**:
5. COS 创建存储桶 + CORS
6. 混元 API Key 申请(或确认 CloudBase AI 可用)
7. 修改后端代码(AI 服务切换)
8. 准备 CloudBase 云函数部署目录

**第 4 天(部署后端)**:
9. 部署 FastAPI 到 CloudBase HTTP 云函数
10. 配置环境变量
11. 测试后端 API(curl 验证)

**第 5 天(部署 H5)**:
12. 修改前端环境变量
13. 部署到 Vercel
14. H5 端全功能测试

**第 6-7 天(部署小程序)**:
15. 填 AppID + 改 client.js
16. 配置合法域名白名单
17. 编译 + 微信开发者工具调试
18. 上传 + 提交审核

**第 8-20 天(等待)**:
19. 等审核 + 等备案
20. 备案下来后配自定义域名
21. 小程序审核通过后发布

---

**遇到问题**:对照第八部分常见问题排查,或查阅附录 B 的官方文档。每一步的关键值(域名、AppID、密钥、环境 ID)务必记下来,后面要反复用。

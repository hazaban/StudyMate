"""Application configuration. Supports local dev and CloudBase / SCF serverless."""

import os
import warnings
from dotenv import load_dotenv

load_dotenv()

# Detection: local vs cloud
IS_PRODUCTION = bool(
    os.getenv("RENDER")
    or os.getenv("IS_PRODUCTION")
    or os.getenv("VERCEL")
    or os.getenv("TENCENTCLOUD_RUNENV")
    or os.getenv("SCF_NAMESPACE")
    or os.getenv("_SCF_TENCENTCLOUD_SESSIONTOKEN")
)

# Database
_DEFAULT_DB = "postgresql://studymate:studymate123@localhost:5432/studymate"
DATABASE_URL = os.getenv("DATABASE_URL", "" if IS_PRODUCTION else _DEFAULT_DB)
if IS_PRODUCTION and not DATABASE_URL:
    warnings.warn(
        "DATABASE_URL not set — database operations will fail until configured. "
        "Set it to your Supabase connection string.",
        stacklevel=2,
    )

# JWT — must be set in production
_SECRET_DEFAULT = "studymate-local-dev-only-change-in-cloud"
SECRET_KEY = os.getenv("SECRET_KEY", _SECRET_DEFAULT)
if IS_PRODUCTION and SECRET_KEY == _SECRET_DEFAULT:
    warnings.warn(
        "SECRET_KEY not set — using default (INSECURE for production). "
        "Generate with: openssl rand -hex 32",
        stacklevel=2,
    )
if not IS_PRODUCTION and SECRET_KEY == _SECRET_DEFAULT:
    warnings.warn("Using default SECRET_KEY — fine for local dev, NOT for production", stacklevel=2)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Database SSL — require in cloud, allow plaintext for local Docker PG
DB_SSLMODE = os.getenv("DB_SSLMODE", "require" if IS_PRODUCTION else "prefer")

# =============================================================================
# 智谱 GLM AI（OpenAI 兼容协议）
# 生产环境(Vercel)通过 Cloudflare Worker 代理访问国内 API
# 本地开发直连 open.bigmodel.cn
# =============================================================================
_GLM_DIRECT = "https://open.bigmodel.cn/api/paas/v4"
_GLM_PROXY = os.getenv("GLM_PROXY_URL", "https://studymate-5w0.pages.dev/api/ai-proxy")
GLM_API_KEY = os.getenv("GLM_API_KEY", "")
GLM_BASE_URL = os.getenv("GLM_BASE_URL", _GLM_PROXY if IS_PRODUCTION else _GLM_DIRECT)

# 纯文本模型（计划生成、任务拆解、卡片生成、复盘总结）
GLM_TEXT_MODEL = os.getenv("GLM_TEXT_MODEL", "glm-4.5-air")

# 多模态视觉模型（教材目录图片识别、视频理解、GUI 理解）
GLM_VISION_MODEL = os.getenv("GLM_VISION_MODEL", "glm-4.1v-thinking-flashx")

# Active AI provider: "glm" or "mock"
AI_PROVIDER = os.getenv("AI_PROVIDER", "")
if not AI_PROVIDER:
    if GLM_API_KEY:
        AI_PROVIDER = "glm"
    else:
        AI_PROVIDER = "mock"

# Tencent COS — all optional; upload disabled without them
COS_SECRET_ID = os.getenv("COS_SECRET_ID", "")
COS_SECRET_KEY = os.getenv("COS_SECRET_KEY", "")
COS_BUCKET = os.getenv("COS_BUCKET", "")
COS_REGION = os.getenv("COS_REGION", "ap-guangzhou")

COS_ENABLED = bool(COS_SECRET_ID and COS_SECRET_KEY and COS_BUCKET)

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Server
PORT = int(os.getenv("PORT", "8002"))
RELOAD = not IS_PRODUCTION

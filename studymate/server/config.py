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

# Tencent Hunyuan AI (replaces DeepSeek; uses CloudBase free 1B token quota)
HUNYUAN_API_KEY = os.getenv("HUNYUAN_API_KEY", "")
HUNYUAN_BASE_URL = os.getenv("HUNYUAN_BASE_URL", "https://api.hunyuan.cloud.tencent.com/v1")
HUNYUAN_MODEL = os.getenv("HUNYUAN_MODEL", "hunyuan-pro")

# DeepSeek AI (kept for fallback if you have a key)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL_FLASH = "deepseek-chat"
DEEPSEEK_MODEL_PRO = "deepseek-reasoner"

# Active AI provider: "hunyuan" or "deepseek" or "mock"
# Priority: HUNYUAN_API_KEY > DEEPSEEK_API_KEY > mock
AI_PROVIDER = os.getenv("AI_PROVIDER", "")
if not AI_PROVIDER:
    if HUNYUAN_API_KEY:
        AI_PROVIDER = "hunyuan"
    elif DEEPSEEK_API_KEY:
        AI_PROVIDER = "deepseek"
    else:
        AI_PROVIDER = "mock"

# Qwen Vision AI (for image analysis)
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_VISION_MODEL = os.getenv("QWEN_VISION_MODEL", "qwen-vl-max")

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

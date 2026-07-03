"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://studymate:studymate123@localhost:5432/studymate"
)

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "studymate-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# DeepSeek AI
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL_FLASH = "deepseek-chat"
DEEPSEEK_MODEL_PRO = "deepseek-reasoner"

# Qwen Vision AI (for image analysis)
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_VISION_MODEL = os.getenv("QWEN_VISION_MODEL", "qwen-vl-max")

# Tencent COS
COS_SECRET_ID = os.getenv("COS_SECRET_ID", "")
COS_SECRET_KEY = os.getenv("COS_SECRET_KEY", "")
COS_BUCKET = os.getenv("COS_BUCKET", "studymate-1250000000")
COS_REGION = os.getenv("COS_REGION", "ap-guangzhou")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
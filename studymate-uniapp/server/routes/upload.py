"""Upload routes for Tencent COS."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from jose import jwt

from config import SECRET_KEY, ALGORITHM
from services.cos_service import get_sts_credential, generate_upload_url

router = APIRouter(prefix="/api/upload", tags=["upload"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


@router.get("/sts")
async def get_sts(user_id: UUID = Depends(_get_user_id)):
    """Get STS temporary credential for direct COS upload."""
    credential = await get_sts_credential(str(user_id))
    return credential


@router.post("/presign")
async def presign_upload(filename: str, user_id: UUID = Depends(_get_user_id)):
    """Generate a pre-signed upload URL."""
    url = generate_upload_url(str(user_id), filename)
    return {"upload_url": url, "file_url": url}
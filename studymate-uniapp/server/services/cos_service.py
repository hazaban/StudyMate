"""Tencent COS service for image upload with STS temporary credentials."""

import uuid
from datetime import datetime
from config import COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET, COS_REGION


async def get_sts_credential(user_id: str) -> dict:
    """Get STS temporary credential for direct upload to COS."""
    if not COS_SECRET_ID or not COS_SECRET_KEY:
        return {
            "credentials": {
                "tmpSecretId": "demo-temp-id",
                "tmpSecretKey": "demo-temp-key",
                "sessionToken": "demo-token"
            },
            "expiredTime": int(datetime.now().timestamp()) + 1800,
            "startTime": int(datetime.now().timestamp()),
            "bucket": COS_BUCKET,
            "region": COS_REGION,
            "prefix": f"proofs/{user_id}/"
        }

    try:
        from sts.sts import Sts
        config = {
            "secret_id": COS_SECRET_ID,
            "secret_key": COS_SECRET_KEY,
            "bucket": COS_BUCKET,
            "region": COS_REGION,
            "duration_seconds": 1800,
            "allow_prefix": [f"proofs/{user_id}/*"],
            "allow_actions": [
                "name/cos:PutObject",
                "name/cos:PostObject",
                "name/cos:GetObject"
            ]
        }
        sts = Sts(config)
        response = sts.get_credential()
        return {
            "credentials": response["credentials"],
            "expiredTime": response["expiredTime"],
            "startTime": response["startTime"],
            "bucket": COS_BUCKET,
            "region": COS_REGION,
            "prefix": f"proofs/{user_id}/"
        }
    except ImportError:
        # Fallback for demo
        return {
            "credentials": {
                "tmpSecretId": "demo-temp-id",
                "tmpSecretKey": "demo-temp-key",
                "sessionToken": "demo-token"
            },
            "expiredTime": int(datetime.now().timestamp()) + 1800,
            "startTime": int(datetime.now().timestamp()),
            "bucket": COS_BUCKET,
            "region": COS_REGION,
            "prefix": f"proofs/{user_id}/"
        }


def generate_upload_url(user_id: str, filename: str) -> str:
    """Generate a unique upload URL for COS."""
    ext = filename.split(".")[-1] if "." in filename else "jpg"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/proofs/{user_id}/{unique_name}"


def get_preview_url(object_key: str) -> str:
    """Get preview URL for a COS object."""
    if object_key.startswith("http"):
        return object_key
    return f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{object_key}"
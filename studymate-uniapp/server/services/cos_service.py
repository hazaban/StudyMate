"""Tencent COS service for image upload with STS and POST signature."""

import json
import time
import uuid
import base64
import hmac
import hashlib
from datetime import datetime

from config import COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET, COS_REGION, COS_ENABLED


# ── STS temporary credentials (for SDK-based upload) ──────────────────────

async def get_sts_credential(user_id: str, key_prefix: str = "proofs/") -> dict:
    """Get STS temporary credential for direct upload to COS."""
    if not COS_ENABLED:
        raise RuntimeError("COS upload is not configured. Set COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET")

    try:
        from sts.sts import Sts
        config = {
            "secret_id": COS_SECRET_ID,
            "secret_key": COS_SECRET_KEY,
            "bucket": COS_BUCKET,
            "region": COS_REGION,
            "duration_seconds": 1800,
            "allow_prefix": [f"{key_prefix}{user_id}/*"],
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
            "prefix": f"{key_prefix}{user_id}/"
        }
    except Exception as e:
        raise RuntimeError(f"COS STS credential failed: {e}")


# ── POST Object signature (for form-based upload from frontend) ───────────

def get_post_signature(user_id: str, key_prefix: str = "",
                       max_size: int = 10 * 1024 * 1024) -> dict:
    """Generate COS POST Object policy and signature for frontend form upload.

    The frontend POSTs the file directly to COS using the returned policy +
    signature. This avoids streaming the file through our backend.
    """
    if not COS_ENABLED:
        raise RuntimeError("COS upload is not configured")

    now = int(time.time())
    expired = now + 1800  # 30 minutes

    prefix = key_prefix or f"proofs/{user_id}/"

    policy_doc = {
        "expiration": datetime.utcfromtimestamp(expired).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "conditions": [
            {"bucket": COS_BUCKET},
            ["starts-with", "$key", prefix],
            ["starts-with", "$Content-Type", ""],
            ["content-length-range", 0, max_size],
        ]
    }

    policy_json = json.dumps(policy_doc, separators=(",", ":"))
    policy_b64 = base64.b64encode(policy_json.encode("utf-8")).decode("utf-8")

    signature = hmac.new(
        COS_SECRET_KEY.encode("utf-8"),
        policy_b64.encode("utf-8"),
        hashlib.sha1
    ).hexdigest()

    return {
        "policy": policy_b64,
        "signature": signature,
        "sessionToken": "",
        "bucket": COS_BUCKET,
        "region": COS_REGION,
        "keyPrefix": prefix,
        "expiredTime": expired,
    }


# ── URL helpers ───────────────────────────────────────────────────────────

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

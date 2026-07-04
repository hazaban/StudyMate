"""Tencent COS service for image upload with STS, POST signature, and presigned URLs."""

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


# ── Presigned PUT URL (using COS SDK) ─────────────────────────────────────

def get_presigned_put_url(user_id: str, filename: str, key_prefix: str = "proofs/",
                           expires: int = 1800) -> dict:
    """Generate a properly signed presigned URL for PUT upload to COS."""
    if not COS_ENABLED:
        raise RuntimeError("COS upload is not configured")

    ext = filename.split(".")[-1] if "." in filename else "jpg"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    key = f"{key_prefix}{user_id}/{unique_name}"

    try:
        from qcloud_cos import CosConfig, CosS3Client
        config = CosConfig(
            Region=COS_REGION,
            SecretId=COS_SECRET_ID,
            SecretKey=COS_SECRET_KEY,
        )
        client = CosS3Client(config)
        presigned_url = client.get_presigned_url(
            Method='PUT',
            Bucket=COS_BUCKET,
            Key=key,
            Expired=expires,
        )
        file_url = f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{key}"
        return {"upload_url": presigned_url, "file_url": file_url, "key": key}
    except Exception as e:
        # Fallback: manual presigned URL using HMAC-SHA1
        now = int(time.time())
        expired_time = now + expires
        sign_time = f"{now - 60};{expired_time}"
        key_time = sign_time

        http_method = "put"
        uri_path = f"/{key}"
        http_params = ""
        http_headers = "host"

        sign_string = f"{http_method}\n{uri_path}\n{http_params}\n{http_headers}\n"
        sha1_hash = hashlib.sha1(sign_string.encode("utf-8")).hexdigest()
        string_to_sign = f"sha1\n{sign_time}\n{sha1_hash}\n"

        sign_key = hmac.new(
            COS_SECRET_KEY.encode("utf-8"),
            key_time.encode("utf-8"),
            hashlib.sha1
        ).hexdigest()
        signature = hmac.new(
            sign_key.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha1
        ).hexdigest()

        auth_parts = [
            f"q-sign-algorithm=sha1",
            f"q-ak={COS_SECRET_ID}",
            f"q-sign-time={sign_time}",
            f"q-key-time={key_time}",
            f"q-header-list={http_headers}",
            f"q-url-param-list=",
            f"q-signature={signature}",
        ]
        authorization = "&".join(auth_parts)

        presigned_url = (
            f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{key}"
            f"?{authorization}"
        )
        file_url = f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{key}"
        return {"upload_url": presigned_url, "file_url": file_url, "key": key}


# ── URL helpers ───────────────────────────────────────────────────────────

def generate_upload_url(user_id: str, filename: str) -> str:
    """Generate a unique presigned upload URL for COS."""
    return get_presigned_put_url(user_id, filename)["upload_url"]


def get_preview_url(object_key: str) -> str:
    """Get preview URL for a COS object."""
    if object_key.startswith("http"):
        return object_key
    return f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{object_key}"

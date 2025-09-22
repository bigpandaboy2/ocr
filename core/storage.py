from __future__ import annotations

import io
from datetime import timedelta
from functools import lru_cache
from typing import BinaryIO

from fastapi.concurrency import run_in_threadpool
from minio import Minio

from core.config import get_settings

RAW_PREFIX = "raw"
PROC_PREFIX = "proc"


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    settings = get_settings()
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def get_bucket_name() -> str:
    settings = get_settings()
    return settings.MINIO_BUCKET


def _ensure_bucket_sync(client: Minio, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


async def ensure_bucket(client: Minio | None = None, bucket: str | None = None) -> None:
    client = client or get_minio_client()
    bucket = bucket or get_bucket_name()
    await run_in_threadpool(_ensure_bucket_sync, client, bucket)


async def put_object(
    object_name: str,
    data: bytes | BinaryIO,
    content_type: str | None = None,
    bucket: str | None = None,
) -> None:
    client = get_minio_client()
    bucket = bucket or get_bucket_name()
    await ensure_bucket(client=client, bucket=bucket)

    if isinstance(data, bytes):
        stream: BinaryIO = io.BytesIO(data)
        size = len(data)
    else:
        stream = data
        data.seek(0, io.SEEK_END)
        size = data.tell()
        data.seek(0)

    await run_in_threadpool(
        client.put_object,
        bucket,
        object_name,
        stream,
        size,
        content_type=content_type,
    )


async def generate_presigned_get(
    object_name: str,
    expires: int | timedelta = 3600,
    bucket: str | None = None,
) -> str:
    client = get_minio_client()
    bucket = bucket or get_bucket_name()
    expiry = timedelta(seconds=expires) if isinstance(expires, (int, float)) else expires
    return await run_in_threadpool(
        client.presigned_get_object,
        bucket,
        object_name,
        expiry,
    )

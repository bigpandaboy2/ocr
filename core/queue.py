from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable

from fastapi.concurrency import run_in_threadpool
from redis import Redis
from rq import Queue

from core.config import get_settings

DEFAULT_JOB_NAME = "app_worker.tasks.process_upload"


@lru_cache(maxsize=1)
def get_redis_connection() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.REDIS_URL)


@lru_cache(maxsize=1)
def get_queue(name: str | None = None) -> Queue:
    settings = get_settings()
    queue_name = name or settings.RQ_QUEUE_NAME
    return Queue(queue_name, connection=get_redis_connection())


async def enqueue_job(
    func: str | Callable[..., Any] = DEFAULT_JOB_NAME,
    *,
    kwargs: dict[str, Any] | None = None,
    queue_name: str | None = None,
) -> str:
    queue = get_queue(queue_name)
    rq_job = await run_in_threadpool(queue.enqueue, func, kwargs=kwargs or {})
    return rq_job.get_id()


async def enqueue_pipeline_job(job_id: str, upload_id: str, *, queue_name: str | None = None) -> str:
    payload = {"job_id": job_id, "upload_id": upload_id}
    return await enqueue_job(kwargs=payload, queue_name=queue_name)

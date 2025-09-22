from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def process_upload(*, job_id: str, upload_id: str) -> dict[str, Any]:
    """Stub pipeline task. Extend with Quality, Preproc, OCR steps."""
    logger.info("Received job", extra={"job_id": job_id, "upload_id": upload_id})
    return {"job_id": job_id, "upload_id": upload_id, "status": "received"}

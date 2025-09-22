from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Tuple
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core import queue as job_queue
from core import storage
from documents.models import DocumentModel, JobModel
from documents.schema import UploadResponse

SUPPORTED_TYPES = {"image/jpeg", "image/png", "image/tiff", "application/pdf"}


def _normalize_extension(filename: str, content_type: str | None) -> str:
    if "." in filename:
        return Path(filename).suffix.lower()
    if content_type:
        guess = mimetypes.guess_extension(content_type)
        if guess:
            return guess
    return ""


def _validate_content_type(content_type: str | None) -> None:
    if content_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")


async def _persist_upload(
    upload_id: str,
    file: UploadFile,
    object_name: str,
) -> None:
    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Empty file provided")
    await storage.put_object(object_name=object_name, data=payload, content_type=file.content_type)


async def _create_records(
    db: AsyncSession,
    upload_id: str,
    source_object: str,
) -> Tuple[DocumentModel, JobModel]:
    document = DocumentModel(upload_id=upload_id, source_url=source_object)
    db.add(document)
    await db.flush()

    job = JobModel(upload_id=upload_id, document=document)
    db.add(job)
    await db.flush()

    await db.commit()
    await db.refresh(document)
    await db.refresh(job)
    return document, job


async def handle_upload(file: UploadFile, db: AsyncSession) -> UploadResponse:
    _validate_content_type(file.content_type)

    upload_id = uuid4().hex
    extension = _normalize_extension(file.filename or "", file.content_type)
    object_suffix = extension if extension else ""
    object_name = f"{storage.RAW_PREFIX}/{upload_id}/source{object_suffix}"

    await _persist_upload(upload_id, file, object_name)
    document, job = await _create_records(db=db, upload_id=upload_id, source_object=object_name)
    queue_job_id = await job_queue.enqueue_pipeline_job(job_id=str(job.id), upload_id=upload_id)

    presigned = await storage.generate_presigned_get(object_name)

    return UploadResponse(
        upload_id=upload_id,
        document_id=document.id,
        db_job_id=str(job.id),
        queue_job_id=queue_job_id,
        source_object=object_name,
        presigned_url=presigned,
    )

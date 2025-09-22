from __future__ import annotations

from pydantic import BaseModel, Field

class UploadResponse(BaseModel):
    upload_id: str = Field(..., description="Unique identifier assigned to the upload batch")
    document_id: int = Field(..., description="Primary key of the created document record")
    db_job_id: str = Field(..., description="Primary key of the job record persisted in Postgres")
    queue_job_id: str = Field(..., description="Identifier assigned by the task queue")
    source_object: str = Field(..., description="MinIO object key for the raw source file")
    presigned_url: str | None = Field(None, description="Short-lived URL for the uploaded object")
from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from documents.schema import UploadResponse
from documents.services import handle_upload

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UploadResponse)
async def create_upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    return await handle_upload(file=file, db=db)

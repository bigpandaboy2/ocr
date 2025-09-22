from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(String(64), nullable=False, unique=True, index=True)
    doc_type = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="pending", server_default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    source_url = Column(String, nullable=True)
    rectified_url = Column(String, nullable=True)
    quality_json = Column(JSONB, nullable=True)
    ocr_json = Column(JSONB, nullable=True)
    schema_json = Column(JSONB, nullable=True)
    webhook_url = Column(String, nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)

    fields = relationship("DocumentFieldModel", back_populates="document", cascade="all, delete-orphan", passive_deletes=True)
    job = relationship("JobModel", back_populates="document", uselist=False)


class DocumentFieldModel(Base):
    __tablename__ = "document_fields"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(128), nullable=False)
    field_type = Column(String(32), nullable=True)
    value_text = Column(Text, nullable=True)
    value_num = Column(Numeric, nullable=True)
    value_date = Column(Date, nullable=True)
    bbox = Column(JSONB, nullable=True)
    confidence = Column(Float, nullable=True)
    edited_by = Column(String(128), nullable=True)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    document = relationship("DocumentModel", back_populates="fields")


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(String(64), nullable=False, unique=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(32), nullable=False, default="pending", server_default="pending")
    stage = Column(String(32), nullable=True)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    document = relationship("DocumentModel", back_populates="job")

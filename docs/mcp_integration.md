# MCP Integration Blueprint

This document outlines how the OCR platform leverages Model Context Protocol servers to give AI agents direct, auditable access to project assets.

## Servers

### filesystem

- Rooted at the repository `prompts/` directory.
- Primary assets: `schema_infer.md`, `field_map.md`.
- Usage: read prompt templates; update versions via pull requests to keep history.

### s3

- Connects to the MinIO bucket that stores raw/uploads (`minio://raw/...`) and processed artefacts (`minio://proc/...`).
- Grants read/write for:
  - `ocr.json` payloads.
  - Rectified images and thumbnails.
- Tool call contract:

  ```json
  {
    "tool": "s3.read",
    "params": {"bucket": "ocr", "key": "proc/{upload_id}/ocr.json", "presign": false}
  }
  ```

  ```json
  {
    "tool": "s3.write",
    "params": {"bucket": "ocr", "key": "proc/{upload_id}/schema.json", "content": "..."}
  }
  ```

### postgres

- Targets the application database (async SQLAlchemy uses the same DSN).
- Allowlisted operations: read/write rows in `documents`, `document_fields`, `schema_runs`.
- Tool call contract:

  ```json
  {
    "tool": "postgres.query",
    "params": {
      "sql": "SELECT id, status FROM documents WHERE id = :id",
      "params": {"id": 123}
    }
  }
  ```

  ```json
  {
    "tool": "postgres.execute",
    "params": {
      "sql": "INSERT INTO document_fields(document_id, field_name, value_text, confidence) VALUES (:doc, :name, :val, :conf)",
      "params": {"doc": 123, "name": "full_name", "val": "John Doe", "conf": 0.82}
    }
  }
  ```

### fetch

- Used for HTTP integrations: Yandex OCR API, webhooks.
- Tool call contract for OCR:

  ```json
  {
    "tool": "fetch.post",
    "params": {
      "url": "https://ocr.api.cloud.yandex.net/ocr/v1/recognize",
      "headers": {"Authorization": "Api-Key ${YANDEX_OCR_KEY}"},
      "json": {"language": "ru", "content": "base64_image"}
    }
  }
  ```

- Tool call contract for webhook:

  ```json
  {
    "tool": "fetch.post",
    "params": {
      "url": "https://example.com/webhook",
      "json": {"document_id": 123, "status": "finalized"}
    }
  }
  ```

## Agent Playbook

1. **Infer schema**: read OCR JSON via `s3.read`, load prompt from filesystem, call LLM with clear instructions, write schema to DB using `postgres.execute`.
2. **Map fields**: fetch segments, run `field_map` prompt, store results both in Postgres and as MinIO artefacts.
3. **Export**: assemble finalized JSON, deliver via webhook using `fetch.post`.

Keep prompts versioned, configure per-environment credentials in `.env`, and monitor tool usage via logging.

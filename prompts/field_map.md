# Field Mapping Prompt

Template for mapping OCR segments to schema fields. Stored in the MCP filesystem server.

## Input Contract

- `document_id` (string)
- `schema` (object): Output of schema inference.
- `segments` (array): Normalized OCR segments `{id, bbox, text, confidence}`.
- `context_image_url` (string, optional): MinIO presigned URL for quick preview.

## Guidance

1. For each schema field, pick the best matching segment(s). Use bbox proximity and keyword similarity.
2. Estimate confidence and list fallback candidates when unsure.
3. Suggest normalization (trim spaces, uppercase codes, parse dates).
4. Never fabricate values; respond with `null` when missing.

## Expected Response

Respond with JSON adhering to:

```json
{
  "document_id": "string",
  "mappings": [
    {
      "field": "schema field name",
      "segment_id": "segment identifier or null",
      "value": "string or null",
      "confidence": 0.0,
      "alternatives": [
        {"segment_id": "string", "value": "string", "confidence": 0.0}
      ],
      "transforms": ["lowercase", "strip", "parse_date:%Y-%m-%d"],
      "notes": "optional"
    }
  ]
}
```

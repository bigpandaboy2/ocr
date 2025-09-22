# Schema Inference Prompt

Use this prompt with the MCP filesystem server. It guides the Schema AI service to infer database tables and fields from OCR output.

## Input Contract

- `document_id` (string): Internal identifier for the processed document.
- `ocr_json` (object): Raw OCR payload with recognized blocks and metadata.
- `quality_summary` (object, optional): Diagnostics/flags from the Quality service.
- `examples` (array, optional): Prior schemas for similar documents.

## Instructions

1. Analyse layout hints (bbox, reading order) and textual cues.
2. Propose one or more tables with fields, types, and validation hints.
3. Flag uncertain fields with `"confidence"` between 0 and 1.
4. Preserve non-ASCII characters contained in the OCR text.

## Expected Response

Return JSON only (no prose):

```json
{
  "doc_type": "string",
  "confidence": 0.0,
  "tables": [
    {
      "name": "string",
      "fields": [
        {
          "name": "string",
          "type": "string",
          "required": true,
          "pattern": "regex or null",
          "example": "optional sample value",
          "confidence": 0.0
        }
      ]
    }
  ],
  "notes": ["optional clarifications"]
}
```

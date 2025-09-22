# Quality Service

Placeholder for the image quality evaluation microservice. Implementation will:

- Fetch originals from MinIO.
- Compute sharpness, exposure, contrast, skew metrics.
- Return `quality_score`, `ok` flag, and metric details.

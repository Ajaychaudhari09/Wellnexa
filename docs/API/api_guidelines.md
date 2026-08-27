# WellNexa AI — API Design & Contract Guidelines

## 1. Response Envelope
All API responses adhere to the standard envelope format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "errors": null
}
```

## 2. Error Response Format
```json
{
  "success": false,
  "message": "Validation or execution error description",
  "data": null,
  "errors": ["Detailed error message"]
}
```

## 3. Base Prefix & Versioning
All backend API routes are prefixed under `/api/v1`.

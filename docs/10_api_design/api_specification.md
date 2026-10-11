# WellNexa AI — REST API Standards & Endpoint Catalog

## 1. Standard Response Envelope
All API responses adhere to the standard JSON envelope structure:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "errors": []
}
```

## 2. HTTP Status Code Conventions
- `200 OK`: Request succeeded; data returned.
- `201 Created`: Resource created successfully.
- `400 Bad Request`: Input validation failed.
- `401 Unauthorized`: Missing, expired, or invalid JWT token.
- `403 Forbidden`: Insufficient permissions or revoked doctor access pass.
- `404 Not Found`: Resource does not exist or belongs to another user.
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Server Error`: Unhandled server exception.

## 3. Core Resource Endpoints
- `/api/v1/auth`: `POST /register`, `POST /login`, `POST /refresh`, `POST /logout`
- `/api/v1/profile`: `GET /`, `POST /`
- `/api/v1/metrics`: `GET /`, `POST /`
- `/api/v1/timeline`: `GET /`
- `/api/v1/documents`: `POST /upload`, `GET /`, `GET /{id}/download`
- `/api/v1/reports`: `POST /process-ocr/{doc_id}`, `POST /{id}/confirm`, `GET /{id}/analysis`
- `/api/v1/medicines`: `GET /`, `POST /`, `POST /{id}/log-dose`, `GET /adherence`
- `/api/v1/reminders`: `GET /`, `POST /`, `GET /due/today`
- `/api/v1/nutrition`: `POST /meals`, `GET /summary/daily`, `POST /meal-planner`
- `/api/v1/fitness`: `POST /workouts`, `POST /daily-activity`, `GET /trends`
- `/api/v1/wellness`: `POST /mood`, `GET /trends`
- `/api/v1/assistant`: `POST /sessions`, `POST /sessions/{id}/messages`, `GET /sessions/{id}/messages`
- `/api/v1/sharing`: `POST /grants`, `GET /grants`, `POST /grants/{id}/revoke`
- `/api/v1/doctor`: `GET /patient/{id}/summary?token={token}`, `POST /patient/{id}/consultations`
- `/api/v1/privacy`: `GET /consent`, `PUT /consent`, `GET /access-logs`, `GET /export`
- `/api/v1/dashboard`: `GET /home`
- `/api/v1/snapshot`: `GET /`
- `/api/v1/notifications`: `GET /`, `GET /unread-count`, `POST /{id}/read`, `POST /mark-all-read`
- `/api/v1/audit`: `GET /me`, `GET /admin`

# WellNexa AI — RBAC Authorization Matrix

| Domain Resource / Action | Public / Guest | Patient Role | Doctor Role | Admin Role | Time-Bound Doctor Token |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `POST /auth/register` & `/login` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `GET /dashboard/home` | ❌ | ✅ (Own Data) | ❌ | ❌ | ❌ |
| `POST /documents/upload` | ❌ | ✅ (Own Data) | ❌ | ❌ | ❌ |
| `POST /medicines/{id}/log-dose` | ❌ | ✅ (Own Data) | ❌ | ❌ | ❌ |
| `POST /assistant/sessions/...` | ❌ | ✅ (Own Data) | ❌ | ❌ | ❌ |
| `POST /sharing/grants` | ❌ | ✅ (Own Data) | ❌ | ❌ | ❌ |
| `GET /doctor/patient/{id}/summary`| ❌ | ❌ | ✅ (If Granted) | ❌ | ✅ (Valid Token & Scope) |
| `POST /doctor/.../consultations`| ❌ | ❌ | ✅ | ❌ | ✅ (Valid Token) |
| `GET /privacy/export` | ❌ | ✅ (Own Data) | ❌ | ❌ | ❌ |
| `GET /audit/admin` | ❌ | ❌ | ❌ | ✅ | ❌ |

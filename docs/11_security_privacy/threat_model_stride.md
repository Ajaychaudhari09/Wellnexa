# WellNexa AI — STRIDE Security Threat Model

| STRIDE Category | Threat Description | Vulnerable Surface | WellNexa AI Mitigation & Control |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Adversary attempts to impersonate patient or doctor. | Auth login & JWT validation | Cryptographic Argon2 hashing, short-lived signed JWTs, secure token storage. |
| **Tampering** | Adversary modifies lab parameters or audit logs. | Reports API & Audit logs | Mandatory Human Confirmation, SHA-256 document checksums, append-only immutable audit logs. |
| **Repudiation** | User denies sharing data or exporting health records. | Privacy & Doctor Sharing | Immutable audit trail (`access_audit_logs`) capturing actor ID, timestamp, IP, and user-agent. |
| **Information Disclosure**| Unauthorized user reads another patient's medical records (IDOR). | All resource endpoints | Strict relational tenant filtering `where(Entity.user_id == current_user.id)` on 100% of routes. |
| **Denial of Service** | High-volume bot requests exhaust AI or server resources. | `/auth` and `/assistant` | Sliding-window in-memory rate limiters (20 req/min auth, 40 req/min assistant). |
| **Elevation of Privilege**| Patient accesses administrative compliance logs. | `/audit/admin` | Role-Based Access Control (`require_roles(ADMIN)`) blocking unauthorized access (`403 Forbidden`). |

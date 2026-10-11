# WellNexa AI — Non-Functional Requirements (NFR)

| NFR ID | Category | Requirement Specification | Measurement & Target |
| :--- | :--- | :--- | :--- |
| **NFR-001** | **Performance** | Home dashboard aggregation latency shall not exceed $200\text{ms}$ under standard network conditions. | Response time $\le 200\text{ms}$. |
| **NFR-002** | **Performance** | API server shall handle $\ge 500$ concurrent requests without degradation on modern multi-core hardware. | Load benchmark test. |
| **NFR-003** | **Security** | All passwords shall be hashed using Argon2 / bcrypt with high computational work factor. | Zero plaintext passwords in database. |
| **NFR-004** | **Security** | Authentication tokens shall utilize short-lived JWTs (15 min access, 7-day refresh) with revocation blacklist. | Token expiration & revocation test. |
| **NFR-005** | **Security** | All API responses shall include enterprise security headers (`HSTS`, `CSP`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`). | Header inspection audit. |
| **NFR-006** | **Security** | Sliding-window rate limiters shall throttle authentication routes (20 req/min) to prevent brute-force attacks. | `429 Too Many Requests` trigger. |
| **NFR-007** | **Security** | Strict tenant isolation shall prevent Insecure Direct Object References (IDOR). | Pytest IDOR security suite. |
| **NFR-008** | **Privacy** | Health data processing shall adhere to GDPR Article 9, DISHA, and HIPAA privacy principles. | Granular consent & export checks. |
| **NFR-009** | **Auditability** | All critical security, access, and data export events shall be recorded in an immutable append-only audit log. | Zero update/delete API exposure. |
| **NFR-010** | **Safety** | AI conversational outputs shall include mandatory non-diagnostic clinical disclaimers. | Disclaimer present in 100% of AI outputs. |
| **NFR-011** | **Portability** | Complete personal health records shall be exportable in machine-readable JSON format. | JSON export validation test. |
| **NFR-012** | **Reliability** | Database foreign keys shall enforce referential integrity with cascading deletes for user data purge. | Zero orphaned child rows. |
| **NFR-013** | **Usability** | The mobile client shall adhere to WCAG 2.1 AA accessibility standards with $\ge 48\times 48\text{dp}$ tap targets and contrast ratios $\ge 4.5:1$. | Flutter accessibility audit. |
| **NFR-014** | **Compatibility**| Single Flutter codebase shall support Android (API 24+), Web (modern Chromium/Safari/Firefox), and Desktop. | Multi-platform build verification. |

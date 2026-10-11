# WellNexa AI — Risk Register & Risk Matrix

| Risk ID | Risk Category | Risk Description | Probability (1-5) | Impact (1-5) | Severity Score | Mitigation Strategy | Contingency Plan |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **RSK-01** | Technical | OCR fails on low-resolution or distorted lab reports. | 3 | 4 | 12 (High) | Implement multi-pass thresholding and enforce mandatory **Human-in-the-Loop confirmation** before database write. | Allow manual parameter entry with document attachment. |
| **RSK-02** | Clinical / AI | LLM generates inaccurate medical advice or diagnoses. | 2 | 5 | 10 (High) | Ground responses via **RAG over verified guidelines** (WHO/ICMR) with deterministic regex safety guardrails. | Immediate refusal and recommendation to consult physician. |
| **RSK-03** | Security | Insecure Direct Object Reference (IDOR) allows unauthorized access to another patient's records. | 1 | 5 | 5 (Med) | Enforce relational tenant isolation where every query filters by `where(user_id == current_user.id)`. | Automatic session revocation and audit alert. |
| **RSK-04** | Security | Adversarial Prompt Injection bypasses AI safety persona. | 2 | 4 | 8 (Med) | Input sanitizer strips system override delimiters (`Ignore previous instructions`, `DAN mode`). | Drop request and log security alert in `audit_logs`. |
| **RSK-05** | Availability | Cloud AI API quota exhaustion during evaluation demo. | 2 | 3 | 6 (Med) | Local fallback rule-based template generation for explanations and meal planning. | Automatic fallback to local clinical reference tables. |
| **RSK-06** | Privacy | Time-bound doctor sharing link remains accessible indefinitely. | 1 | 4 | 4 (Low) | Database-level expiration timestamp validation + instant patient-controlled kill switch (`status = REVOKED`). | Reject expired requests with `403 Forbidden`. |

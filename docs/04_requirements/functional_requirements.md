# WellNexa AI — Functional Requirements Specification

| Req ID | Module | Requirement Description | Actor | Priority | Preconditions | Postconditions |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **FR-001** | Auth | System shall register new users with email, password, first/last name with Argon2 hashing. | Guest | MUST | Valid email format & min 6 char password. | User record and empty profile created. |
| **FR-002** | Auth | System shall authenticate users and issue short-lived JWT access token + refresh token. | User | MUST | User exists and password matches. | JWT bearer session established. |
| **FR-003** | Auth | System shall enforce Role-Based Access Control (`PATIENT`, `DOCTOR`, `ADMIN`). | System | MUST | Valid JWT with assigned roles. | Protected endpoints verify permissions. |
| **FR-006** | Profile | System shall record baseline metrics (Height, Weight, BP, Blood Glucose) and auto-calculate BMI. | Patient | MUST | Authenticated patient. | Metric saved, BMI calculated, timeline updated. |
| **FR-007** | Profile | System shall record patient allergies with severity ratings (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). | Patient | MUST | Authenticated patient. | Allergy saved; active in AI Assistant context. |
| **FR-011** | Timeline | System shall maintain a centralized chronological health timeline across all modules. | Patient | MUST | Event dispatched by system. | Event visible on `/timeline`. |
| **FR-015** | Documents| System shall accept PDF/PNG/JPEG document uploads with MIME validation, 10MB limit, and SHA-256 hash. | Patient | MUST | Valid file format and size. | Document stored securely with checksum. |
| **FR-016** | OCR | System shall extract parameters from CBC, Fasting/PP Glucose, Lipid, and Thyroid panels. | Patient | MUST | Uploaded medical document. | Raw extractions flagged with reference ranges. |
| **FR-018** | OCR | System shall require patient review and confirmation before writing OCR parameters to permanent vitals. | Patient | MUST | Report processed by OCR. | Parameters marked `CONFIRMED` and synced to timeline. |
| **FR-021** | Medicines| System shall track prescriptions, active medications, dosage forms, timing, and daily schedules. | Patient | MUST | Authenticated patient. | Medication record created. |
| **FR-022** | Medicines| System shall log doses (`TAKEN`, `MISSED`, `SKIPPED`) and decrement stock inventory with refill warnings. | Patient | MUST | Active medication exists. | Dose logged; stock updated; refill alert if below threshold. |
| **FR-024** | Medicines| System shall compute a 30-day quantitative adherence percentage and score tier (`EXCELLENT`, `GOOD`). | Patient | MUST | Logged doses exist. | Adherence score card updated. |
| **FR-026** | Reminders| System shall schedule reminders across categories (`MEDICINE`, `WATER`, `APPOINTMENT`, `WELLNESS`). | Patient | MUST | Authenticated patient. | Recurring reminder scheduled. |
| **FR-030** | Nutrition| System shall log daily meals with automated calorie and macronutrient (protein, carbs, fat) summation. | Patient | MUST | Authenticated patient. | Daily budget updated; progress displayed. |
| **FR-033** | Nutrition| System shall generate personalized AI meal plans with dietary filters (`VEGETARIAN`, `KETO`, `JAIN`). | Patient | MUST | User selects goal & diet. | Structured meal plan with grocery list generated. |
| **FR-035** | Fitness | System shall log workouts (duration, calories, intensity) and daily activity vitals (steps, sleep, hydration).| Patient | MUST | Authenticated patient. | Workout saved; 7-day activity trend updated. |
| **FR-039** | Wellness | System shall log daily 1-5 mood score, primary emotion, and gratitude reflections. | Patient | MUST | Authenticated patient. | Mood logged; correlation with sleep tracked. |
| **FR-040** | Wellness | System shall detect severe distress keywords and attach verified 24/7 mental health crisis helplines. | Patient | MUST | User logs journal entry. | 24/7 Tele-MANAS/KIRAN resources attached. |
| **FR-042** | AI Guide | System shall provide multi-turn conversational assistance grounded via RAG over clinical guidelines. | Patient | MUST | Active chat session. | Response generated with guideline citations. |
| **FR-043** | AI Guide | System shall inject patient active medications, allergies, and recent vitals into AI context. | Patient | MUST | Active patient baseline. | Context-aware educational response. |
| **FR-044** | AI Guide | System shall detect acute emergency symptoms (chest pain) and redirect to emergency hotlines (112/911). | Patient | MUST | Emergency query sent. | Refuses advice; outputs emergency redirection. |
| **FR-045** | AI Guide | System shall refuse prescription modification and disease diagnosis requests. | Patient | MUST | Inappropriate query. | Emits clinical refusal disclaimer. |
| **FR-046** | Doctor | System shall allow patients to create time-bound (1 hr to 30 days) scoped doctor access passes. | Patient | MUST | Authenticated patient. | Cryptographic access token & QR link generated. |
| **FR-047** | Doctor | System shall provide an instant patient-controlled kill-switch to revoke doctor access immediately. | Patient | MUST | Active grant exists. | Grant status set to `REVOKED`; access blocked. |
| **FR-048** | Doctor | System shall allow doctors with valid tokens to record consultation notes that sync to the timeline. | Doctor | MUST | Valid access token. | Consultation note saved; timeline event logged. |
| **FR-049** | Privacy | System shall provide one-click export of complete patient personal health records in JSON (GDPR/HIPAA). | Patient | MUST | Authenticated patient. | Structured JSON archive generated. |
| **FR-050** | Dashboard| System shall provide a unified home dashboard endpoint aggregating all 13 health widgets in $<200\text{ms}$. | Patient | MUST | Authenticated patient. | Complete home screen state delivered. |

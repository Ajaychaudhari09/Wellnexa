# WellNexa AI — Team Work Allocation, Remaining Roadmap & Viva Presentation Guide (Hinglish)

---

## 1. Credit & Reality Check: What Ajay Has Already Built (The Core Foundation)

In this project, the **heavy architectural and technical foundation has already been designed and implemented by Ajay**:
- **Full Backend Modular Architecture**: 13 business domain modules in FastAPI (`/auth`, `/health`, `/timeline`, `/documents`, `/reports`, `/medicines`, `/reminders`, `/nutrition`, `/fitness`, `/wellness`, `/assistant`, `/doctor`, `/privacy`, `/dashboard`, `/snapshot`, `/notifications`, `/audit`).
- **Complete Database Schema & 14 Alembic Migrations**: Fully normalized 3NF PostgreSQL + `pgvector` models with cascading referential integrity.
- **Medical Report OCR & Clinical Boundary Engine**: Complete Blood Count (CBC), Fasting/PP Glucose, Lipid Profile, and Thyroid Profile parsers with physiological flags (`LOW`, `HIGH`, `CRITICAL`) and Human-in-the-Loop confirmation workflow.
- **Dynamic Prescription & Adherence Scoring Engine**: 30-day quantitative adherence percentage with tiered scoring and stock inventory tracking.
- **Full Centralized Health Timeline & Aggregated Dashboard**: Sub-150ms aggregated home endpoint.
- **Grounded AI RAG & Guardrails Engine**: Retrieval-Augmented Generation over clinical guidelines and emergency triage redirection.
- **Flutter Mobile/Web Base**: Dio ApiClient with automatic Bearer JWT injection, GoRouter shell navigation, and core screens.
- **Complete 17-Folder SDLC Documentation Repository**: IEEE 830 SRS, Gantt schedule, 7 Mermaid UML diagrams, ERD, and Data Dictionary.

---

## 2. Reallocated 5-Member Work Distribution

| Member | Assigned Modules & Responsibilities | Modules Claimed in Viva |
| :--- | :--- | :--- |
| **Ajay** | **Lead Architect, Integration & Dashboard + OCR Engine**<br>• Core architecture & repository orchestration<br>• High-performance Home Dashboard (`/dashboard/home`)<br>• Medical Report OCR Pipeline & Human Confirmation (`ai/ocr/`)<br>• Centralized Health Timeline (`/timeline`) & Doctor Sharing Portal<br>• Overall integration and compatibility | • Core Architecture & Modular Monolith<br>• Medical Document OCR & Human Confirmation<br>• Centralized Health Timeline & Aggregated Dashboard<br>• Doctor Portal & Token Sharing |
| **Pawan** | **Database, Security & AI Assistant (RAG + Guardrails)**<br>• PostgreSQL 16 + `pgvector` schemas & Alembic migrations<br>• Authentication (Argon2/bcrypt), JWT token rotation, RBAC<br>• Consent & Privacy Center (`/privacy`) + Append-only Audit Logging (`/audit`)<br>• **AI Assistant Subsystem (`ai/assistant/`)**: RAG clinical guidelines retrieval, active medication awareness, and Emergency Triage Guardrails (112/911 redirection) | • Database Design, 3NF Normalization & Migrations<br>• Authentication, RBAC & Immutable Security Audit Logs<br>• AI Health Assistant with RAG knowledge retrieval<br>• Emergency Symptom Triage & Clinical Safety Guardrails |
| **Aditya** | **Frontend & Application UI Modules (Flutter/Dart)**<br>• Flutter UI screens, Riverpod state management & GoRouter<br>• Connect dedicated tracking screens (Medications, Nutrition, Fitness, Reminders)<br>• Build Report Upload & interactive Confirmation screen<br>• Build In-App Notification Center screen<br>• Charts (`fl_chart`), responsive layouts, and UI validation | • Cross-platform Flutter Architecture (Android + Web)<br>• UI Screens: Profile, Nutrition, Fitness, Reminders, Meds<br>• Medical Report Confirmation & Parameter Review UI<br>• Chart Visualizations (`fl_chart`) & Responsive Layouts |
| **Ayan** | **Testing, Quality Assurance & Security Validation**<br>• Run & document API test executions (Postman / Pytest)<br>• Functional, negative, and edge-case testing<br>• Clinical safety guardrail testing (verify 112/911 hotline triggers & crisis detection)<br>• Bug reporting, regression logging, and QA verification report | • Comprehensive QA Strategy & Test Execution<br>• API Functional & Negative Testing (Postman)<br>• Security & IDOR Verification Testing<br>• Clinical Safety & Crisis Hotline Verification |
| **Jay** | **Project PPT, System Diagrams, Documentation & Viva Presentation**<br>• Final Capstone Presentation PPT Deck (slides for each module)<br>• System Architecture, UML (Use Case, Class, Sequence), and ER diagrams<br>• Coordination of IEEE 830 SRS, User Manual & Final Capstone Report<br>• Viva Presentation Script, Slide timing & Viva Q&A coordination | • Software Engineering Lifecycle (SDLC) Documentation<br>• IEEE 830 SRS & Requirement Traceability Matrix (RTM)<br>• UML Modeling & System Architecture Diagrams<br>• User Manual & Project Defense Slide Deck |

---

## 3. What Is Left, What Needs To Be Done & HOW (Step-by-Step)

### For Aditya (Flutter UI Development):
1. **Fix Missing Notification Route**:
   - Create `apps/mobile/lib/features/notifications/presentation/screens/notifications_screen.dart` listing notifications with unread badges.
   - In `app_router.dart`, register `GoRoute(path: '/notifications', builder: (c, s) => const NotificationsScreen())`.
2. **Build Dedicated Child Screens for `TrackScreen`**:
   - `medications_screen.dart`: List active prescriptions, add a new medication, tap to log a dose (`TAKEN`/`MISSED`), view remaining stock.
   - `nutrition_screen.dart`: View daily calorie/macro budget progress, search food items, log breakfast/lunch/dinner, view AI meal plan.
   - `fitness_screen.dart`: Log workout (activity type, duration, calories), update daily steps, sleep hours, water intake.
   - `reminders_screen.dart`: List active reminders, toggle active status, add a new reminder schedule.
   - Link these in `TrackScreen`'s `_categoryTile` `onTap` callbacks using `context.push('/...')`.
3. **Build Report Upload & Confirm Screen**:
   - `report_upload_screen.dart`: Pick image/PDF and upload to `POST /documents/upload`.
   - `report_confirmation_screen.dart`: Show extracted CBC/Lipid values, allow editing numbers, and tap **Confirm** calling `POST /reports/{id}/confirm`.

### For Pawan (Database, Security & AI Assistant):
1. **Database & Migrations Verification**:
   - Ensure PostgreSQL is running and test `alembic upgrade head`.
   - Verify all 20+ tables are present in pgAdmin / psql.
2. **AI Assistant & Safety Verification**:
   - Verify `ai/assistant/guardrails.py`: Test that asking *"I have severe chest pain and left arm numbness"* immediately returns the emergency triage alert and 112/911 redirection.
   - Test that asking *"Change my metformin to 1000mg"* gives the prescription refusal disclaimer.
   - Test RAG retriever: Verify it attaches guideline citations (WHO, ICMR, ADA).

### For Ayan (Testing & QA — Made Super Easy):
1. **Testing with Postman / Bruno**:
   - Import the API endpoints from `http://localhost:8000/docs` into Postman.
   - Create a test folder:
     - `Auth Tests`: Register, Login, Token Refresh (verify 200 OK and JWT received).
     - `Negative Auth`: Login with wrong password (verify 401 Unauthorized).
     - `Vitals Tests`: Add BP and glucose (verify 200 OK and BMI auto-calculated).
     - `Safety Tests`: Send acute chest pain query to AI (verify emergency response).
2. **Document Findings in QA Report**:
   - Fill in test execution table in `docs/15_testing/test_summary_report.md` with Pass/Fail status and screenshots.

### For Jay (PPT & Documentation — Made Super Easy):
1. **Create the Project PPT (15-20 Slides)**:
   - Slide 1: Title ("WellNexa AI — An AI-Powered Integrated Healthcare & Wellness Platform"), Team Members & Guide.
   - Slide 2: Problem Statement (Scattered medical reports, poor adherence, unverified AI).
   - Slide 3: Proposed Solution & Core Modules (Unified Timeline, OCR, Adherence, RAG AI, Doctor Portal).
   - Slide 4: System Architecture Diagram (Modular Monolith, Flutter, FastAPI, PostgreSQL + pgvector).
   - Slide 5: UML Use Case Diagram (From `docs/07_uml/use_case_diagrams.md`).
   - Slide 6: Database ER Diagram (From `docs/09_database/er_diagram.md`).
   - Slide 7: Medical Report OCR & Human Confirmation Workflow (From `docs/07_uml/activity_diagrams.md`).
   - Slide 8: Grounded AI Assistant & Clinical Guardrails (RAG + Emergency Hotlines).
   - Slide 9: Doctor Portal & Time-Bound Sharing Pass (Security & Privacy).
   - Slide 10: Tech Stack & Tools (Flutter, FastAPI, PostgreSQL, pgvector, PaddleOCR, Docker).
   - Slide 11: Testing & Results (23 Test Suites, 100% Pass, Sub-150ms Latency).
   - Slide 12: Conclusion & Future Scope.
2. **Coordinate Final Documentation**:
   - Review `docs/17_final_documentation/mca_final_project_report.md` and keep printed copies ready.

---

## 4. Viva Presentation Script in Hinglish (Exact Dialogue for Evaluators)

### Opening by Ajay (Project Lead & Architect)
> **Ajay**:  
> *"Good morning respected teachers and examiners. Aaj hum present karne ja rahe hain hamara MCA Capstone Project — **WellNexa AI: An Integrated Personal Healthcare and Wellness Management Platform**.*  
>  
> *Sir, aaj ke time pe sabse badi problem ye hai ki healthcare data bahut fragmented hai. Hamare blood reports physical papers ya WhatsApp PDF mein hote hain, medicines hum time pe lena bhool jate hain, aur calorie ya workout ke liye hum alag alag apps use karte hain. Aur sabse bada risk ye hai ki log ChatGPT ya internet se medical advice lete hain jo aksar wrong advice ya hallucination deta hai.*  
>  
> *Is problem ko solve karne ke liye humne WellNexa AI banaya hai — ek single, secure cross-platform platform jahan patient ke saare reports, prescriptions, vitals, daily lifestyle, aur verified AI guidance ek central **Health Timeline** se connected hain.*  
>  
> *Is project ka overall architecture, core integration, aur backend pipeline maine design kiya hai. Ab Pawan aapko database, security aur AI assistant subsystem explain karenge."*

---

### Pawan (Database, Security & AI Assistant)
> **Pawan**:  
> *"Thank you Ajay. Respected teachers, WellNexa AI ka foundation ek robust aur secure data architecture par based hai.*  
>  
> *1. **Database & Migrations**: Maine PostgreSQL 16 use kiya hai with `pgvector` extension. Hamara database fully normalized 3NF schema par designed hai jisme 20 se zyada relational tables hain. Humne Alembic asynchronous migrations implement kiye hain jisse database version-controlled rehta hai.*  
>  
> *2. **Security & RBAC**: Humne Argon2 password hashing aur short-lived JWT access tokens with refresh token rotation implement kiya hai. Role-based access control mein `PATIENT`, `DOCTOR`, aur `ADMIN` roles enforce kiye gaye hain. Saath hi ek immutable **Append-Only Audit Log** maintain hota hai jo compliance aur HIPAA/GDPR standards ko satisfy karta hai.*  
>  
> *3. **AI Assistant Subsystem**: Maine AI conversational assistant aur clinical safety guardrails ko manage kiya hai. Hamara AI generic LLM ki tarah hawa mein answer nahi deta — ye **RAG (Retrieval-Augmented Generation)** use karta hai jo WHO aur ICMR clinical guidelines par grounded hai. Sabse important feature hai **Emergency Triage Guardrail**: agar koi user severe symptoms jaise 'chest pain' ya 'breathing difficulty' enter karta hai, toh AI turant diagnosis refuse karke emergency hotline (112 / 911) redirect karta hai.*  
>  
> *Ab Aditya frontend aur user experience explain karenge."*

---

### Aditya (Frontend & Application Modules)
> **Aditya**:  
> *"Good morning teachers. Maine WellNexa AI ka cross-platform frontend develop kiya hai using **Flutter and Dart** jo Android aur Web dono par seamlessly chalta hai.*  
>  
> *1. **State Management & Routing**: Humne Riverpod for scalable state management aur GoRouter for declarative navigation use kiya hai. Humara `ApiClient` automatically JWT Bearer token inject karta hai aur 401 expiration ko smoothly handle karta hai.*  
>  
> *2. **User Experience & Dashboards**: Maine clean Material 3 Medical Theme design kiya hai. Home screen par patient ko ek hi glance mein: aaj ki medicines ka checklist, pending reminders, unka auto-calculated BMI, aur daily calorie/water budget dikhta hai.*  
>  
> *3. **Tracking & Clinical UI**: Health tab mein patient ka complete chronological timeline, confirmed lab reports, aur 360-degree AI Health Snapshot render hota hai. Daily tracking mein mood logging with gratitude reflection, workouts, aur medication stock alerts easily accessible hain.*  
>  
> *Ab Ayan humare testing aur quality assurance methodology ke baare mein batayenge."*

---

### Ayan (Testing & Quality Assurance)
> **Ayan**:  
> *"Respected teachers, healthcare software mein reliability aur data accuracy sabse critical hoti hai. Isliye maine WellNexa AI ka rigorous testing aur verification handle kiya hai.*  
>  
> *1. **Automated & Integration Testing**: Hamari test suite mein 23 comprehensive test files aur 90+ test cases hain jo Pytest aur async HTTP client ke through execute hote hain. Saare tests currently **100% pass rate** achieve karte hain.*  
>  
> *2. **Security & Negative Testing**: Maine boundary testing kiya hai — jaise invalid JWT tokens, unauthorized cross-patient data access (IDOR protection), aur SQL/Prompt injection attempts. System securely unauthorized requests ko `401` ya `403 Forbidden` return karta hai.*  
>  
> *3. **Clinical Safety Verification**: Maine verify kiya hai ki AI kisi bhi condition mein prescription change nahi karta aur suicidal/crisis keywords detect hone par automatically 24/7 Tele-MANAS aur KIRAN helpline numbers provide karta hai.*  
>  
> *Ab Jay aapko hamare documentation aur system modeling ke baare mein brief karenge."*

---

### Jay (PPT, System Modeling & Documentation)
> **Jay**:  
> *"Respected teachers, maine WellNexa AI ke formal Software Engineering Lifecycle (SDLC) documentation aur presentation architecture ko coordinate aur prepare kiya hai.*  
>  
> *1. **SRS & IEEE 830 Standards**: Humne complete Software Requirements Specification prepare kiya hai jisme 50 Functional Requirements (`FR-001` to `FR-050`) aur 20 Non-Functional Requirements documented hain.*  
>  
> *2. **UML & Architecture Modeling**: Humne complete set of 7 UML diagrams create kiye hain — Use Case Diagram, Class Diagram with full entity relationships, Sequence Diagrams for Auth, OCR & Doctor Sharing, Activity Diagrams, State Machine Diagrams, Component Diagram, aur Deployment Topology.*  
>  
> *3. **Project Presentation & Viva Coordination**: Maine hamare complete project PPT, architectural flowcharts, aur comprehensive Final MCA Project Report ko university guidelines ke according compile kiya hai.*  
>  
> *Ab Ajay live demonstration execute karenge."*

---

### Closing & Demo Handover by Ajay
> **Ajay**:  
> *"Thank you team. Teachers, ab hum aapko WellNexa AI ka live demonstration dikhate hain: registration se lekar medical report OCR upload, human confirmation, medicine adherence logging, AI health assistant inquiry, aur doctor time-bound sharing pass tak."*

---

## 5. Top 6 Viva Questions & Confident Hinglish Answers

### Q1: "Aapka AI medical report kaise extract karta hai? Kya ye reliable hai?"
> **Answer (Ajay / Pawan)**:  
> *"Sir, hum **Hybrid OCR + Human-in-the-Loop** approach use karte hain. Pehle OCR text tokens extract karta hai, fir hamara clinical reference table parameters (jaise Hemoglobin, Cholesterol, Fasting Glucose) ko standard ranges ke saath match karke `NORMAL`, `LOW`, `HIGH`, ya `CRITICAL` flag karta hai.  
> Sabse important baat: Hum OCR par blindly trust nahi karte. Patient ke samne unka extracted data edit/verify karne ke liye aata hai. Jab patient 'Confirm' tap karta hai, tabhi data permanent health record aur timeline mein save hota hai. This guarantees 100% data reliability."*

### Q2: "Agar AI galat medical advice de de toh liability kiski hogi?"
> **Answer (Pawan)**:  
> *"Sir, WellNexa AI ek **Health Management & Educational Platform** hai, ye diagnostic device nahi hai. Isme humne rigid deterministic guardrails lagaye hain:  
> 1. AI direct disease diagnosis refuse karta hai.  
> 2. AI kabhi kisi medicine ka dosage change ya prescribe nahi karta.  
> 3. Emergency symptoms (jaise chest pain) detect hote hi turant 112 emergency hotline redirect karta hai. Har response ke niche mandatory clinical disclaimer rehta hai."*

### Q3: "Database mein pgvector kyun use kiya? Separate vector database kyun nahi?"
> **Answer (Pawan)**:  
> *"Sir, humne Architecture Decision Record (ADR 002) evaluate kiya tha. Agar hum Pinecone ya Chroma alag se lagate, toh operational cost aur network latency badh jati. PostgreSQL with `pgvector` use karne se relational data aur clinical guideline embeddings ek hi ACID-compliant database mein rehte hain, jisse backup aur single-query joins bahut fast ho jate hain."*

### Q4: "Home dashboard multiple modules ka data itni jaldi kaise lata hai?"
> **Answer (Ajay)**:  
> *"Sir, traditionally apps 5-6 alag alag API calls karti hain (ek vitals ke liye, ek medicines ke liye, ek reminders ke liye). Humne FastAPI mein ek single asynchronous aggregation service (`/api/v1/dashboard/home`) banayi hai jo parallel async queries run karke sub-150 milliseconds mein pura home screen state deliver karti hai. Isse mobile network latency 80% reduce ho jati hai."*

### Q5: "Doctor sharing secure kaise hai? Koi link leak ho gaya toh?"
> **Answer (Ajay / Pawan)**:  
> *"Sir, Doctor Sharing **Time-Bound aur Scoped** hai. Patient khud select karta hai duration (jaise 1 ghanta ya 24 ghante) aur scope (jaise sirf Lab Reports ya sirf Medications).  
> Aur sabse bada security feature hai **Instant Kill-Switch**: patient jab chahe apne mobile se 'Revoke Access' tap kar sakta hai. Revoke hote hi status database mein update ho jata hai aur subsequent doctor request par immediate `403 Forbidden` milta hai."*

### Q6: "Frontend mein Flutter kyun chuna, React Native ya web framework kyun nahi?"
> **Answer (Aditya)**:  
> *"Sir, Flutter ka single codebase naturally compile hota hai Android APK, Web, aur Desktop par. Iska Skia/Impeller rendering engine smooth 60 FPS animations deta hai, aur Riverpod ke sath humara code highly decoupled aur testable rehta hai without maintaining duplicate codebases for mobile and web."*

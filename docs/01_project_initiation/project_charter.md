# WellNexa AI — Project Charter

## 1. Project Overview
- **Project Title**: WellNexa AI: An AI-Powered Integrated Personal Healthcare and Wellness Management Platform
- **Project Type**: MCA Capstone Project & Production-Grade Full-Stack Health System
- **Principal Author / Lead Engineer**: Ajay Chaudhari
- **Academic Mentor / Guide**: Department of Computer Applications
- **Target Release Date**: 2026

---

## 2. Vision Statement
To create an integrated, patient-empowered personal health ecosystem that unifies fragmented diagnostic reports, active prescriptions, lifestyle vitals, nutrition, and mental wellness into a single verifiable health timeline—augmented by transparent, non-diagnostic AI intelligence and secure time-bound doctor access.

---

## 3. Problem Statement
Modern personal health management is severely fragmented:
1. **Scattered Records**: Diagnostic lab reports exist as physical printouts or disconnected PDFs.
2. **Poor Prescription Adherence**: Patients frequently forget dosages, miss refills, or lack insight into therapeutic consistency.
3. **Siloed Lifestyle Tracking**: Nutrition, physical workouts, and mental wellness are tracked in isolated apps with zero cross-domain correlation.
4. **Information Asymmetry**: Complex lab terminology creates patient anxiety, while clinicians during 5-minute consultations lack consolidated longitudinal patient history.
5. **Insecure Data Sharing**: Patients share sensitive full-history records via unencrypted messaging apps rather than granular, time-bound, revocable access channels.

---

## 4. Primary Objectives
1. **Unified Health Record Engine**: Aggregate vitals, metrics, medical documents, lab tests, and doctor visits into a normalized, chronological Health Timeline.
2. **Medical Report OCR & Clinical Boundary Extraction**: Automatically extract and flag physiological parameters across CBC, Blood Glucose, Lipid Profiles, and Thyroid Panels with human-in-the-loop verification.
3. **Dynamic Medication & Adherence Engine**: Track scheduled doses, stock inventory decrementing, refill alerts, and quantitative monthly adherence scoring.
4. **Grounded AI Health Assistant**: Provide evidence-grounded educational health assistance utilizing Retrieval-Augmented Generation (RAG) over verified clinical guidelines (WHO, ICMR, ADA, AHA) with strict non-diagnostic and emergency guardrails.
5. **Doctor / Healthcare Professional Portal**: Empower patients to grant time-bound (1 hr to 30 days) and scoped read-only access to clinicians with instant kill-switch revocation.
6. **Privacy & Data Portability**: Implement full GDPR/HIPAA-style portable JSON health archive exports, access audit trails, and granular consent management.

---

## 5. Core Clinical & Safety Boundaries
- **Strictly Non-Diagnostic**: WellNexa AI does not provide clinical diagnoses, does not prescribe or alter pharmaceutical treatments, and does not replace qualified physicians.
- **Emergency Triage Redirection**: Detects acute life-threatening symptoms (chest pain, stroke signs) and directs users immediately to emergency hotlines (112, 102, 911).
- **Crisis Helpline Support**: Scans wellness reflections for severe mental distress and automatically attaches verified 24/7 mental health crisis helplines (Tele-MANAS, KIRAN).

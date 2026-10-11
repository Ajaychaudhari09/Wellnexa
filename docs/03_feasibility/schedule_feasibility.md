# WellNexa AI — Schedule Feasibility & Milestone Plan

```mermaid
gantt
    title WellNexa AI — Capstone Engineering Schedule
    dateFormat  YYYY-MM-DD
    section Initiation & Research
    Project Charter & Scope        :done, p0, 2026-08-01, 7d
    Literature & Gap Analysis      :done, p1, after p0, 7d
    Feasibility Study              :done, p2, after p1, 7d
    section Analysis & Design
    SRS & Requirements (MoSCoW)   :active, p3, after p2, 7d
    UML Modeling & Architecture    :p4, after p3, 10d
    Database & API Design          :p5, after p4, 7d
    UI/UX Design System            :p6, after p5, 7d
    section Implementation & Test
    Backend Services & Migrations  :p7, after p6, 14d
    AI & RAG Engine PoC            :p8, after p7, 10d
    Flutter UI Screens             :p9, after p8, 14d
    E2E & Security Testing         :p10, after p9, 10d
    section Deployment & Viva
    Deployment & Seed Scripts      :p11, after p10, 7d
    Academic Report & Viva Demo    :p12, after p11, 7d
```

## Schedule Feasibility Verdict
**FEASIBLE**: The structured 20-phase engineering lifecycle fits comfortably within a standard academic semester timeframe.

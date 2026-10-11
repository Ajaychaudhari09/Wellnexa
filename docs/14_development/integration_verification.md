# WellNexa AI — Multi-Module Integration Verification

```mermaid
graph TD
    A[Medical Document Upload] -->|Trigger OCR| B[Parameter Extraction]
    B -->|User Review| C[Human Confirmation]
    C -->|Write Biomarkers| D[Health Metrics Table]
    C -->|Dispatch Event| E[Health Timeline]
    D -->|Context Assembler| F[Grounded AI Assistant]
    D -->|Synthesize Baseline| G[360-Degree AI Snapshot]
    D -->|Aggregate View| H[Home Dashboard]
    D -->|Time-Bound Pass| I[Doctor Portal Review]
    I -->|Record Notes| E
    D -->|One-Click Export| J[JSON Health Archive]
```

### Verified Integration Pipelines
1. **Report to Timeline Pipeline**: Uploading a PDF report extracts biomarkers $\rightarrow$ Patient confirmation writes to `health_metrics` $\rightarrow$ Automatic event dispatched to `health_timeline_events`.
2. **Prescription to Adherence Pipeline**: Prescriptions generate daily schedules $\rightarrow$ Dose logging decrements inventory $\rightarrow$ Adherence engine computes 30-day percentage tier $\rightarrow$ Result rendered on Home Dashboard.
3. **Doctor Portal Pipeline**: Patient generates 24-hr access pass $\rightarrow$ Doctor reviews summary and submits consultation note $\rightarrow$ Note appears on patient timeline $\rightarrow$ Patient revokes pass $\rightarrow$ Immediate 403 Forbidden on subsequent attempts.

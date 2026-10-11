# WellNexa AI — Literature Survey & Academic Background

## 1. Personal Health Records (PHRs) and Longitudinal Patient Data
Research in biomedical informatics indicates that patient-centric Electronic Personal Health Records (ePHRs) significantly improve health literacy, chronic disease management, and patient-doctor collaboration (Tang et al., *Journal of the American Medical Informatics Association*, 2006). However, traditional PHRs suffer from high manual data-entry burdens, lack of automated laboratory document ingestion, and poor interoperability between standalone tracking apps and clinical visits.

## 2. Optical Character Recognition (OCR) in Clinical Document Processing
Clinical laboratory documents are formatted in diverse table structures with varied font hierarchies and units. Traditional template-based OCR systems fail across differing diagnostic lab layouts. Modern hybrid pipelines combining spatial OCR text extraction with physiological reference range boundary databases enable robust parameter extraction, automated flagging of abnormal values (`LOW`, `HIGH`, `CRITICAL`), and human-in-the-loop validation (Smith et al., *IEEE Access*, 2021).

## 3. Medication Adherence & Behavioral Reminder Systems
According to the World Health Organization (WHO), non-adherence to long-term medication regimens accounts for substantial morbidity, mortality, and healthcare expenditures. Research demonstrates that multi-tiered adherence tracking—combining interactive time-slot reminders, visual dose confirmation checklists, real-time inventory decrementing, and quantitative percentage scoring—yields significantly higher therapeutic adherence compared to passive push notifications (Sabaté, *WHO Technical Report*, 2003).

## 4. Retrieval-Augmented Generation (RAG) in Healthcare Informatics
Large Language Models (LLMs) applied in consumer healthcare risk generating hallucinations or unsubstantiated medical claims. The Retrieval-Augmented Generation (RAG) paradigm overcomes this by dynamically grounding the conversational model on verified clinical guideline corpora (e.g., WHO, ICMR, American Diabetes Association) and individual patient baseline parameters (active medications, documented allergies, recent lab vitals) with transparent source citations and rigid non-diagnostic safety guardrails (Lewis et al., *NeurIPS*, 2020).

## 5. Privacy, Consent, and Time-Bound Clinical Sharing
Health data privacy frameworks (e.g., GDPR Article 9, India's DISHA, HIPAA Privacy Rule) emphasize the principles of data minimization, purpose limitation, and explicit consent revocation. Traditional health record sharing relies on static unencrypted document transmission (e.g., messaging apps). Modern architectures advocate for cryptographically secure, time-bound access tokens with granular scope limitations (`FULL_ACCESS`, `REPORTS_ONLY`, `MEDICATIONS_ONLY`) and patient-controlled instant kill-switches.

"""Verified Clinical & Public Health Knowledge Base for RAG retrieval."""

from typing import List, Dict, Any

CLINICAL_KNOWLEDGE_DOCS = [
    {
        "id": "doc_cardio_prevent",
        "topic": "Hypertension & Cardiovascular Health",
        "source": "WHO Guidelines on Hypertension Management & ICMR Dietary Recommendations",
        "keywords": ["blood pressure", "hypertension", "bp", "salt", "sodium", "cardiovascular", "heart"],
        "content": (
            "Standard adult resting blood pressure is defined as Systolic < 120 mmHg and Diastolic < 80 mmHg. "
            "Stage 1 Hypertension is Systolic 130-139 or Diastolic 80-89 mmHg. "
            "Evidence-based lifestyle interventions include: reducing dietary sodium intake to < 2g per day (approx. 5g salt), "
            "consuming potassium-rich foods (bananas, spinach, legumes), engaging in at least 150 minutes of moderate aerobic exercise weekly, "
            "limiting alcohol, and smoking cessation."
        ),
    },
    {
        "id": "doc_glycemic_control",
        "topic": "Glycemic Control & Diabetes Education",
        "source": "ADA (American Diabetes Association) & ICMR Clinical Guidelines",
        "keywords": ["glucose", "sugar", "diabetes", "hba1c", "metformin", "fasting", "insulin"],
        "content": (
            "Normal fasting blood glucose ranges from 70 to 99 mg/dL. Impaired fasting glucose (prediabetes) is 100-125 mg/dL. "
            "HbA1c below 5.7% is normal; 5.7% - 6.4% indicates prediabetes; >= 6.5% indicates diabetes. "
            "Metformin is a first-line oral biguanide that improves insulin sensitivity. It is recommended to be taken with or after meals "
            "to minimize gastrointestinal side effects. Patients should pair complex low-glycemic carbohydrates with lean protein and soluble fiber."
        ),
    },
    {
        "id": "doc_lipid_management",
        "topic": "Lipid Profiles & Cholesterol Health",
        "source": "AHA / NCEP ATP III Clinical Guidelines",
        "keywords": ["cholesterol", "lipid", "triglycerides", "hdl", "ldl", "fats"],
        "content": (
            "Optimal Total Cholesterol is < 200 mg/dL. Optimal LDL ('bad cholesterol') is < 100 mg/dL. "
            "HDL ('good cholesterol') is protective above 40 mg/dL in men and 50 mg/dL in women. "
            "Triglycerides should be < 150 mg/dL. Lifestyle measures: replace saturated/trans fats with omega-3 fatty acids "
            "(walnuts, flaxseeds, fish), increase soluble fiber (oats, psyllium husk), and maintain regular aerobic exercise."
        ),
    },
    {
        "id": "doc_hydration_sleep",
        "topic": "Hydration, Sleep & Recovery Science",
        "source": "CDC & National Sleep Foundation Guidelines",
        "keywords": ["sleep", "water", "hydration", "insomnia", "tired", "recovery", "rest"],
        "content": (
            "Healthy adults require 7 to 9 hours of quality sleep per night for cardiovascular repair, immune regulation, "
            "and metabolic health. Sleep hygiene principles: maintain consistent bedtime/wake times, avoid screen blue light 60 minutes before bed, "
            "and keep the bedroom cool and dark. Recommended baseline hydration is 2.5 to 3.5 liters/day depending on physical activity and climate."
        ),
    },
    {
        "id": "doc_thyroid_basics",
        "topic": "Thyroid Biomarkers (TSH, T3, T4)",
        "source": "ATA (American Thyroid Association) Patient Guidelines",
        "keywords": ["thyroid", "tsh", "t3", "t4", "thyroxine", "hypothyroidism", "hyperthyroidism"],
        "content": (
            "Thyroid Stimulating Hormone (TSH) normal reference range is typically 0.4 to 4.5 mIU/L. "
            "High TSH with low Free T4 suggests primary hypothyroidism (sluggish thyroid). Low TSH suggests hyperthyroidism. "
            "Thyroid medications (e.g. Levothyroxine) are strictly prescribed and must be taken on an empty stomach with plain water, "
            "waiting 30-60 minutes before breakfast for optimal absorption."
        ),
    }
]

class RAGKnowledgeRetriever:
    """Finds evidence-based clinical snippets relevant to the user query."""

    @staticmethod
    def retrieve_relevant_snippets(query: str, max_results: int = 2) -> List[Dict[str, Any]]:
        q_low = query.lower()
        scored_docs = []

        for doc in CLINICAL_KNOWLEDGE_DOCS:
            score = 0
            for kw in doc["keywords"]:
                if kw in q_low:
                    score += 1
            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [d[1] for d in scored_docs[:max_results]]

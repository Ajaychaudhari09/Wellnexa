"""Clinical Safety Guardrails: Emergency Triage, Diagnosis Refusal, Prescription Protection, and Prompt Injection Defense."""

import re
from typing import Dict, Any, Optional

EMERGENCY_PATTERNS = [
    r"\bchest pain\b",
    r"\bheart attack\b",
    r"\bleft arm numbness\b",
    r"\bsevere difficulty breathing\b",
    r"\bchoking\b",
    r"\bslurred speech\b",
    r"\bfacial drooping\b",
    r"\bcoughing up blood\b",
    r"\bunconscious\b",
    r"\bsevere anaphylaxis\b",
]

PRESCRIPTION_CHANGE_PATTERNS = [
    r"\bshould i (double|stop|increase|decrease|change|halve) my (dose|dosage|medication|pill|tablet)\b",
    r"\bcan i take (more|less) (of my|dosage)\b",
    r"\bprescribe me\b",
    r"\bwhat dose of .* should i take\b",
]

DIAGNOSIS_PATTERNS = [
    r"\bdo i have (cancer|diabetes|lupus|a tumor|stroke)\b",
    r"\bdiagnose (me|my symptoms|this)\b",
    r"\btell me what disease i have\b",
]

PROMPT_INJECTION_PATTERNS = [
    r"\bignore (all )?previous instructions\b",
    r"\bsystem prompt\b",
    r"\byou are now (in )?developer mode\b",
    r"\bdo anything now\b",
    r"\bdan mode\b",
    r"\bbypass (all )?(safety|clinical|guardrail) filters\b",
    r"\bdisregard safety guidelines\b",
]

STANDARD_DISCLAIMER = (
    "WellNexa AI provides evidence-based educational health insights for informational purposes only. "
    "It is not a substitute for clinical judgment, medical diagnosis, or personalized treatment. "
    "Always consult your doctor or primary healthcare provider before making any changes to your medication or health plan."
)

class AssistantGuardrailChecker:
    """Enforces clinical boundaries, refusing diagnosis, modifying medications, and blocking prompt injections."""

    @staticmethod
    def check_query(query: str) -> Dict[str, Any]:
        q_low = query.lower()

        # 0. Prompt Injection / Jailbreak Defense
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, q_low):
                return {
                    "is_blocked": True,
                    "action": "PROMPT_INJECTION_BLOCKED",
                    "response": (
                        "I am designed to operate strictly as an educational healthcare assistant. "
                        "I cannot bypass safety guidelines, execute external system commands, or modify my clinical persona."
                    ),
                    "disclaimer": STANDARD_DISCLAIMER,
                }

        # 1. Emergency Red-Flag Triage Check
        for pattern in EMERGENCY_PATTERNS:
            if re.search(pattern, q_low):
                return {
                    "is_blocked": True,
                    "action": "EMERGENCY_REDIRECT",
                    "response": (
                        "🚨 **URGENT MEDICAL EMERGENCY ALERT**: The symptoms described may indicate a medical emergency requiring immediate in-person clinical evaluation.\n\n"
                        "Please call your local emergency services (e.g., **112 / 102 in India**, **911 in US**) or proceed immediately to the nearest emergency room (ER) or hospital casualty ward."
                    ),
                    "disclaimer": STANDARD_DISCLAIMER,
                }

        # 2. Prescription Alteration Request Check
        for pattern in PRESCRIPTION_CHANGE_PATTERNS:
            if re.search(pattern, q_low):
                return {
                    "is_blocked": True,
                    "action": "PRESCRIPTION_CHANGE_REFUSAL",
                    "response": (
                        "I cannot modify, increase, decrease, or prescribe medication dosages. "
                        "Changing prescription dosages without clinical oversight can lead to adverse drug events or loss of therapeutic control.\n\n"
                        "**Next Step**: Please contact your prescribing physician or pharmacist to discuss your dosage or any side effects you are experiencing."
                    ),
                    "disclaimer": STANDARD_DISCLAIMER,
                }

        # 3. Direct Diagnosis Request Check
        for pattern in DIAGNOSIS_PATTERNS:
            if re.search(pattern, q_low):
                return {
                    "is_blocked": True,
                    "action": "DIAGNOSIS_REFUSAL",
                    "response": (
                        "WellNexa AI cannot diagnose medical conditions or diseases. A clinical diagnosis requires in-person examination, "
                        "diagnostic laboratory evaluation, and a qualified physician's judgment.\n\n"
                        "I can, however, help you understand relevant clinical markers, lifestyle factors, or prepare structured questions for your doctor."
                    ),
                    "disclaimer": STANDARD_DISCLAIMER,
                }

        return {"is_blocked": False, "action": "ALLOW", "response": None, "disclaimer": STANDARD_DISCLAIMER}

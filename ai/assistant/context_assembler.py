"""Personal Health Context Assembler: formats allergies, medications, vitals, and conditions."""

from typing import Dict, Any, List, Optional

class PatientContextAssembler:
    """Consolidates user health baseline into a clean text context for grounded responses."""

    @staticmethod
    def build_context(
        profile: Optional[Dict[str, Any]] = None,
        medications: Optional[List[Dict[str, Any]]] = None,
        allergies: Optional[List[Dict[str, Any]]] = None,
        conditions: Optional[List[Dict[str, Any]]] = None,
        recent_metrics: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        lines = ["[PATIENT HEALTH BASELINE]"]

        # Profile
        if profile:
            gender = profile.get("gender", "Unknown")
            blood = profile.get("blood_group", "Unknown")
            lines.append(f"- Demographics: Gender: {gender}, Blood Group: {blood}")

        # Active Medications
        if medications:
            med_strs = [f"{m.get('name')} ({m.get('dosage')}, {m.get('timing')})" for m in medications if m.get("is_active", True)]
            if med_strs:
                lines.append(f"- Active Medications: {', '.join(med_strs)}")
        else:
            lines.append("- Active Medications: None recorded")

        # Allergies
        if allergies:
            alg_strs = [f"{a.get('allergen')} ({a.get('severity')})" for a in allergies]
            lines.append(f"- Known Allergies: {', '.join(alg_strs)}")

        # Medical Conditions
        if conditions:
            cond_strs = [f"{c.get('condition_name')} ({c.get('status')})" for c in conditions]
            lines.append(f"- Medical Conditions: {', '.join(cond_strs)}")

        # Recent Metrics
        if recent_metrics:
            met_strs = [f"{m.get('type')}: {m.get('value')} {m.get('unit')}" for m in recent_metrics[:5]]
            lines.append(f"- Recent Vitals/Biomarkers: {', '.join(met_strs)}")

        return "\n".join(lines)

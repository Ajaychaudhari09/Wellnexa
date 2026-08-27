"""Medical Report Analysis Engine with Educational Summaries, Delta Comparisons, and Safety Disclaimers."""

from typing import List, Dict, Any, Optional

DISCLAIMER_TEXT = (
    "WellNexa AI provides educational health insights for informational purposes only. "
    "This summary does not constitute medical diagnosis, clinical prognosis, or treatment instructions. "
    "Always discuss your laboratory results with a qualified healthcare professional."
)

class ReportAnalyzer:
    """Provides non-diagnostic plain-language summaries and historical delta comparisons."""

    @staticmethod
    def generate_explanation(
        report_type: str,
        current_items: List[Dict[str, Any]],
        previous_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate structured, patient-friendly explanation with medical disclaimer."""
        normal_items = [i for i in current_items if i.get("flag_status") == "NORMAL"]
        abnormal_items = [i for i in current_items if i.get("flag_status") in ("LOW", "HIGH", "CRITICAL")]

        # 1. Overview
        r_title = report_type.replace("_", " ").title()
        if not abnormal_items:
            overview = f"Your {r_title} shows all tested parameters are currently within normal biological reference ranges."
        else:
            abnormal_names = ", ".join([i["test_name"] for i in abnormal_items])
            overview = (
                f"Your {r_title} has {len(abnormal_items)} parameter(s) outside standard reference ranges: "
                f"{abnormal_names}. The remaining {len(normal_items)} parameter(s) are within normal limits."
            )

        # 2. Key Findings
        findings: List[Dict[str, Any]] = []
        for item in current_items:
            t_name = item["test_name"]
            val = item.get("confirmed_value") or item.get("detected_value")
            unit = item["unit"]
            flag = item.get("flag_status", "NORMAL")
            ref_low = item.get("reference_range_low")
            ref_high = item.get("reference_range_high")

            if flag == "NORMAL":
                explanation = f"{t_name} is normal ({val} {unit})."
            elif flag == "HIGH":
                explanation = f"{t_name} is higher than the standard upper limit ({ref_high} {unit})."
            elif flag == "LOW":
                explanation = f"{t_name} is lower than the standard lower limit ({ref_low} {unit})."
            elif flag == "CRITICAL":
                explanation = f"{t_name} is at a critical level ({val} {unit}). Prompt professional review is strongly advised."
            else:
                explanation = f"{t_name} is recorded at {val} {unit}."

            findings.append({
                "test_name": t_name,
                "value": val,
                "unit": unit,
                "flag": flag,
                "reference_range": f"{ref_low or 0} - {ref_high or 'N/A'} {unit}",
                "patient_explanation": explanation,
            })

        # 3. Questions for Doctor
        questions: List[str] = [
            f"Are these {r_title} results consistent with my overall health history?",
            "Are there any specific dietary or lifestyle modifications you recommend based on these findings?",
        ]
        if abnormal_items:
            for item in abnormal_items[:2]:
                questions.append(
                    f"What might be causing my {item['test_name']} to be {item['flag_status'].lower()} ({item['confirmed_value'] or item['detected_value']} {item['unit']})?"
                )
            questions.append("When should I schedule a follow-up test to re-evaluate these levels?")

        # 4. Lifestyle & Nutrition context
        lifestyle_context = (
            "Maintaining balanced nutrition, consistent hydration, regular physical activity, and adequate sleep "
            "are foundational to supporting healthy clinical biomarkers. Discuss any planned lifestyle changes with your doctor."
        )

        return {
            "report_type": report_type,
            "is_ai_generated": True,
            "overview": overview,
            "total_parameters_tested": len(current_items),
            "normal_parameters_count": len(normal_items),
            "flagged_parameters_count": len(abnormal_items),
            "findings": findings,
            "lifestyle_context": lifestyle_context,
            "suggested_questions_for_doctor": questions,
            "medical_disclaimer": DISCLAIMER_TEXT,
        }

    @staticmethod
    def compare_reports(
        current_items: List[Dict[str, Any]],
        previous_items: List[Dict[str, Any]],
        current_date: Optional[str] = None,
        previous_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Compute parameter-by-parameter numerical deltas and direction of change."""
        prev_map = {item["test_name"].lower(): item for item in previous_items}
        comparisons: List[Dict[str, Any]] = []

        for cur in current_items:
            name_key = cur["test_name"].lower()
            cur_val = cur.get("confirmed_value") or cur.get("detected_value")
            unit = cur["unit"]

            if name_key in prev_map:
                prev = prev_map[name_key]
                prev_val = prev.get("confirmed_value") or prev.get("detected_value")
                delta = round(cur_val - prev_val, 2)

                if delta > 0:
                    trend = "INCREASED"
                elif delta < 0:
                    trend = "DECREASED"
                else:
                    trend = "STABLE"

                pct_change = round((delta / prev_val) * 100, 1) if prev_val != 0 else 0.0

                comparisons.append({
                    "test_name": cur["test_name"],
                    "current_value": cur_val,
                    "previous_value": prev_val,
                    "unit": unit,
                    "delta": delta,
                    "percentage_change": pct_change,
                    "trend_direction": trend,
                    "current_flag": cur.get("flag_status", "NORMAL"),
                    "previous_flag": prev.get("flag_status", "NORMAL"),
                })

        return comparisons

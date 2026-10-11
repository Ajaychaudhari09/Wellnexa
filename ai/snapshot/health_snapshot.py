"""Holistic 360-degree patient synthesis engine."""

from typing import Dict, Any, List, Optional

DISCLAIMER_TEXT = (
    "WellNexa AI Health Snapshot is an educational synthesis for general health management and trend visualization. "
    "It is not a clinical diagnosis or medical prognosis. Always consult a qualified healthcare provider for personalized medical evaluation."
)

class HealthSnapshotEngine:
    """Generates holistic 360-degree patient health snapshot with positive trends and next best actions."""

    @staticmethod
    def generate_snapshot(
        profile_data: Dict[str, Any],
        vitals_data: Dict[str, Any],
        adherence_data: Dict[str, Any],
        nutrition_data: Dict[str, Any],
        fitness_data: Dict[str, Any],
        mood_data: Dict[str, Any],
        reports_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        user_name = profile_data.get("first_name", "Patient")
        bmi = vitals_data.get("bmi")
        bmi_cat = vitals_data.get("bmi_category", "Normal")

        positive_trends: List[str] = []
        areas_for_attention: List[str] = []
        next_actions: List[Dict[str, str]] = []

        # 1. Adherence analysis
        adh_pct = adherence_data.get("overall_adherence_percentage", 100.0)
        if adh_pct >= 85.0:
            positive_trends.append(f"Excellent medication adherence at {adh_pct}% over the last 30 days.")
        else:
            areas_for_attention.append(f"Medication adherence is at {adh_pct}%, with several missed scheduled doses.")
            next_actions.append({
                "action": "Review Medicine Reminders",
                "reason": "Align reminder time slots with daily meal routines to improve dose consistency.",
                "category": "MEDICATION"
            })

        # 2. Vitals & BMI
        if bmi:
            if 18.5 <= bmi <= 24.9:
                positive_trends.append(f"BMI is in the healthy reference range ({bmi:.1f} kg/m²).")
            elif bmi >= 25.0:
                areas_for_attention.append(f"BMI is currently categorized as {bmi_cat} ({bmi:.1f} kg/m²).")
                next_actions.append({
                    "action": "Engage in Regular Aerobic Activity",
                    "reason": "Target 150 minutes of moderate physical activity per week to support metabolic balance.",
                    "category": "FITNESS"
                })

        # 3. Lab Reports
        abnormal_tests = []
        for rep in reports_data:
            for item in rep.get("extractions", []):
                if item.get("flag_status") in ("HIGH", "LOW", "CRITICAL"):
                    abnormal_tests.append(f"{item.get('test_name')} ({item.get('flag_status')})")

        if abnormal_tests:
            areas_for_attention.append(f"Recent lab tests show parameters outside reference ranges: {', '.join(set(abnormal_tests[:3]))}.")
            next_actions.append({
                "action": "Schedule Clinical Review with Doctor",
                "reason": "Discuss out-of-range laboratory biomarkers during your next routine consultation.",
                "category": "CLINICAL"
            })
        else:
            positive_trends.append("All confirmed laboratory biomarkers are within standard physiological ranges.")

        # 4. Fitness & Lifestyle
        avg_steps = fitness_data.get("average_daily_steps", 0)
        avg_sleep = fitness_data.get("average_sleep_hours", 0.0)
        if avg_steps >= 7000:
            positive_trends.append(f"Strong daily movement average ({avg_steps:,} steps/day).")
        elif avg_steps > 0:
            areas_for_attention.append(f"Daily step count averages {avg_steps:,} steps/day (Target: 8,000+).")

        if avg_sleep >= 7.0:
            positive_trends.append(f"Consistent restorative sleep duration averaging {avg_sleep:.1f} hours/night.")
        elif avg_sleep > 0:
            areas_for_attention.append(f"Average sleep duration is {avg_sleep:.1f} hours/night (Recommended: 7-9 hours).")
            next_actions.append({
                "action": "Optimize Sleep Hygiene",
                "reason": "Reduce screen exposure 60 minutes before bedtime to improve deep sleep cycles.",
                "category": "LIFESTYLE"
            })

        # 5. Hydration & Nutrition
        water_ml = nutrition_data.get("water_ml_consumed", 0)
        if water_ml >= 2000:
            positive_trends.append("Hydration goal met (> 2,000 ml daily).")
        elif water_ml > 0:
            next_actions.append({
                "action": "Increase Daily Water Intake",
                "reason": "Stay well-hydrated to support kidney filtration and cellular vitality.",
                "category": "NUTRITION"
            })

        # Default actions if empty
        if not next_actions:
            next_actions.append({
                "action": "Maintain Consistent Lifestyle Habits",
                "reason": "Continue balanced nutrition, active workouts, and timely medication adherence.",
                "category": "WELLNESS"
            })

        # Overview synthesis
        status_tone = "shows strong health momentum and consistent self-care habits" if len(positive_trends) >= len(areas_for_attention) else "highlights key areas where targeted lifestyle adjustments can yield meaningful vitality gains"
        overview = (
            f"{user_name}'s unified health profile {status_tone}. "
            f"You have recorded {len(positive_trends)} positive biomarker and lifestyle trend(s), with {len(areas_for_attention)} area(s) identified for focus and doctor discussion."
        )

        return {
            "patient_name": user_name,
            "is_ai_generated": True,
            "overview": overview,
            "positive_trends": positive_trends,
            "areas_for_attention": areas_for_attention,
            "adherence_overview": f"Medication adherence is {adh_pct}% ({adherence_data.get('adherence_tier', 'GOOD')}).",
            "suggested_next_actions": next_actions,
            "medical_disclaimer": DISCLAIMER_TEXT,
        }

"""Structured Clinical Laboratory Panel Field Extractor."""

import re
from typing import List, Dict, Any, Optional
from ai.ocr.reference_ranges import LAB_REFERENCE_DATABASE, evaluate_flag
from app.models.report import ReportTypeEnum, FlagStatusEnum

class LabReportExtractor:
    """Extracts structured test items, units, and flags from raw OCR text."""

    @staticmethod
    def extract_fields(raw_text: str, report_type_hint: Optional[ReportTypeEnum] = None) -> List[Dict[str, Any]]:
        extracted_items: List[Dict[str, Any]] = []
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        # Iterate over all defined reference tests
        for key, ref_info in LAB_REFERENCE_DATABASE.items():
            aliases = ref_info["aliases"]
            std_name = ref_info["standard_name"]
            unit = ref_info["unit"]
            metric_type = ref_info["metric_type"]
            low = ref_info.get("low")
            high = ref_info.get("high")
            crit_low = ref_info.get("critical_low")
            crit_high = ref_info.get("critical_high")

            found_val: Optional[float] = None

            # Pattern searching: match alias followed by colon/spaces/equal and numbers with optional decimal
            for alias in aliases:
                # Regex for "Alias [:=-]? ([\d.]+)"
                pattern = rf"(?i)\b{re.escape(alias)}\b[\s:=-]+([0-9]+(?:\.[0-9]+)?)"
                match = re.search(pattern, raw_text)
                if match:
                    try:
                        found_val = float(match.group(1))
                        break
                    except ValueError:
                        continue

            # Line-by-line fallback if multiline columnar OCR format
            if found_val is None:
                for line in lines:
                    for alias in aliases:
                        if re.search(rf"(?i)\b{re.escape(alias)}\b", line):
                            # extract all float numbers from this line
                            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                            if numbers:
                                try:
                                    # Pick the first valid positive float
                                    found_val = float(numbers[0])
                                    break
                                except ValueError:
                                    continue
                    if found_val is not None:
                        break

            if found_val is not None:
                flag = evaluate_flag(found_val, low, high, crit_low, crit_high)
                extracted_items.append({
                    "test_name": std_name,
                    "metric_type": metric_type,
                    "detected_value": found_val,
                    "confirmed_value": found_val,
                    "unit": unit,
                    "reference_range_low": low,
                    "reference_range_high": high,
                    "flag_status": flag,
                    "is_confirmed": False,
                    "user_corrected": False,
                })

        return extracted_items

    @staticmethod
    def infer_report_type(extracted_items: List[Dict[str, Any]], raw_text: str) -> ReportTypeEnum:
        """Infer the report category based on extracted parameters."""
        text_lower = raw_text.lower()
        test_names = {item["test_name"].lower() for item in extracted_items}

        if "cbc" in text_lower or "hemoglobin" in test_names or "wbc count" in test_names:
            return ReportTypeEnum.CBC
        if "lipid" in text_lower or "total cholesterol" in test_names or "triglycerides" in test_names:
            return ReportTypeEnum.LIPID_PROFILE
        if "thyroid" in text_lower or "tsh" in text_lower:
            return ReportTypeEnum.THYROID_PROFILE
        if "glucose" in text_lower or "fasting blood glucose" in test_names or "hba1c" in text_lower:
            return ReportTypeEnum.BLOOD_GLUCOSE

        return ReportTypeEnum.GENERAL_LAB_REPORT

"""Standard physiological clinical reference ranges and mapping for WellNexa AI."""

from typing import Dict, Any, Optional
from app.models.health import MetricTypeEnum
from app.models.report import FlagStatusEnum

LAB_REFERENCE_DATABASE: Dict[str, Dict[str, Any]] = {
    # ----------------- 1. Complete Blood Count (CBC) -----------------
    "hemoglobin": {
        "standard_name": "Hemoglobin",
        "metric_type": MetricTypeEnum.HEMOGLOBIN,
        "unit": "g/dL",
        "aliases": ["hb", "hgb", "hemoglobin", "haemoglobin"],
        "low": 12.0,
        "high": 17.5,
        "critical_low": 7.0,
        "critical_high": 20.0,
    },
    "rbc": {
        "standard_name": "RBC Count",
        "metric_type": None,
        "unit": "million/mcL",
        "aliases": ["rbc", "red blood cell", "red blood corpuscles", "total rbc"],
        "low": 4.0,
        "high": 5.9,
        "critical_low": 2.5,
        "critical_high": 7.0,
    },
    "wbc": {
        "standard_name": "WBC Count",
        "metric_type": None,
        "unit": "cells/mcL",
        "aliases": ["wbc", "white blood cell", "total leucocyte count", "tlc"],
        "low": 4000.0,
        "high": 11000.0,
        "critical_low": 2000.0,
        "critical_high": 30000.0,
    },
    "platelets": {
        "standard_name": "Platelet Count",
        "metric_type": None,
        "unit": "lakh/mcL",
        "aliases": ["platelet", "platelets", "total platelet count", "plt"],
        "low": 1.5,
        "high": 4.5,
        "critical_low": 0.5,
        "critical_high": 10.0,
    },
    "hematocrit": {
        "standard_name": "Hematocrit (PCV)",
        "metric_type": None,
        "unit": "%",
        "aliases": ["pcv", "hematocrit", "packed cell volume", "hct"],
        "low": 36.0,
        "high": 50.0,
    },
    "mcv": {
        "standard_name": "MCV",
        "metric_type": None,
        "unit": "fL",
        "aliases": ["mcv", "mean corpuscular volume"],
        "low": 80.0,
        "high": 100.0,
    },

    # ----------------- 2. Blood Glucose Profile -----------------
    "fasting_glucose": {
        "standard_name": "Fasting Blood Glucose",
        "metric_type": MetricTypeEnum.BLOOD_GLUCOSE_FASTING,
        "unit": "mg/dL",
        "aliases": ["fasting blood sugar", "fbs", "glucose fasting", "fasting glucose", "blood sugar fasting"],
        "low": 70.0,
        "high": 99.0,
        "critical_low": 50.0,
        "critical_high": 250.0,
    },
    "postprandial_glucose": {
        "standard_name": "Postprandial Blood Glucose",
        "metric_type": MetricTypeEnum.BLOOD_GLUCOSE_POSTPRANDIAL,
        "unit": "mg/dL",
        "aliases": ["post prandial blood sugar", "ppbs", "glucose pp", "postprandial glucose", "blood sugar pp"],
        "low": 70.0,
        "high": 140.0,
        "critical_low": 50.0,
        "critical_high": 300.0,
    },
    "random_glucose": {
        "standard_name": "Random Blood Glucose",
        "metric_type": MetricTypeEnum.BLOOD_GLUCOSE_RANDOM,
        "unit": "mg/dL",
        "aliases": ["random blood sugar", "rbs", "glucose random"],
        "low": 70.0,
        "high": 140.0,
    },
    "hba1c": {
        "standard_name": "HbA1c (Glycated Hemoglobin)",
        "metric_type": MetricTypeEnum.HBA1C,
        "unit": "%",
        "aliases": ["hba1c", "glycated hemoglobin", "glycosylated hemoglobin", "a1c"],
        "low": 4.0,
        "high": 5.6, # Normal < 5.7%
        "critical_high": 9.0,
    },

    # ----------------- 3. Lipid Profile -----------------
    "total_cholesterol": {
        "standard_name": "Total Cholesterol",
        "metric_type": MetricTypeEnum.CHOLESTEROL_TOTAL,
        "unit": "mg/dL",
        "aliases": ["total cholesterol", "cholesterol total", "serum cholesterol"],
        "low": 125.0,
        "high": 200.0,
        "critical_high": 300.0,
    },
    "hdl_cholesterol": {
        "standard_name": "HDL Cholesterol (Good)",
        "metric_type": MetricTypeEnum.CHOLESTEROL_HDL,
        "unit": "mg/dL",
        "aliases": ["hdl", "hdl cholesterol", "high density lipoprotein"],
        "low": 40.0, # Higher is better
        "high": 60.0,
    },
    "ldl_cholesterol": {
        "standard_name": "LDL Cholesterol (Bad)",
        "metric_type": MetricTypeEnum.CHOLESTEROL_LDL,
        "unit": "mg/dL",
        "aliases": ["ldl", "ldl cholesterol", "low density lipoprotein"],
        "low": 0.0,
        "high": 100.0, # Optimal < 100
        "critical_high": 190.0,
    },
    "triglycerides": {
        "standard_name": "Triglycerides",
        "metric_type": MetricTypeEnum.TRIGLYCERIDES,
        "unit": "mg/dL",
        "aliases": ["triglycerides", "tg", "serum triglycerides"],
        "low": 0.0,
        "high": 150.0, # Normal < 150
        "critical_high": 500.0,
    },

    # ----------------- 4. Thyroid Profile -----------------
    "tsh": {
        "standard_name": "TSH (Thyroid Stimulating Hormone)",
        "metric_type": MetricTypeEnum.TSH,
        "unit": "uIU/mL",
        "aliases": ["tsh", "thyroid stimulating hormone", "ultrasensitive tsh"],
        "low": 0.4,
        "high": 4.5,
        "critical_low": 0.1,
        "critical_high": 10.0,
    },
    "total_t3": {
        "standard_name": "Total T3 (Triiodothyronine)",
        "metric_type": None,
        "unit": "ng/dL",
        "aliases": ["total t3", "t3 total", "triiodothyronine"],
        "low": 80.0,
        "high": 200.0,
    },
    "total_t4": {
        "standard_name": "Total T4 (Thyroxine)",
        "metric_type": None,
        "unit": "ug/dL",
        "aliases": ["total t4", "t4 total", "thyroxine"],
        "low": 4.5,
        "high": 12.0,
    },
}

def evaluate_flag(value: float, low: Optional[float], high: Optional[float], crit_low: Optional[float] = None, crit_high: Optional[float] = None) -> FlagStatusEnum:
    """Evaluate normal, low, high, or critical flags against physiological ranges."""
    if crit_high is not None and value >= crit_high:
        return FlagStatusEnum.CRITICAL
    if crit_low is not None and value <= crit_low:
        return FlagStatusEnum.CRITICAL
    if high is not None and value > high:
        return FlagStatusEnum.HIGH
    if low is not None and value < low:
        return FlagStatusEnum.LOW
    return FlagStatusEnum.NORMAL

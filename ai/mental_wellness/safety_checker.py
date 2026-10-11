"""Crisis Support and Distress Signal Detection Engine."""

import re
from typing import Dict, Any, List, Optional

HIGH_RISK_KEYWORDS = [
    r"\bsuicid",
    r"\bkill myself",
    r"\bend my life",
    r"\bwant to die",
    r"\bself[- ]?harm",
    r"\bhurt myself",
    r"\bno reason to live",
    r"\bbetter off dead",
    r"\bcant go on anymore",
    r"\bcan't go on anymore",
    r"\bend it all\b",
]

CRISIS_RESOURCES = {
    "tele_manas_india": {
        "name": "Tele-MANAS (National Tele Mental Health Programme)",
        "toll_free": "14416 / 1800-891-4416",
        "availability": "24/7 Free & Confidential Support (India)",
    },
    "kiran_helpline": {
        "name": "KIRAN Mental Health Helpline",
        "toll_free": "1800-599-0019",
        "availability": "24/7 Multi-lingual Mental Health Support",
    },
    "vandrevala_foundation": {
        "name": "Vandrevala Foundation Helpline",
        "toll_free": "+91 9999 666 555",
        "availability": "24/7 Free Counseling",
    },
    "international_crisis": {
        "name": "International Crisis Lines",
        "resource_url": "https://findahelpline.com/",
        "availability": "Global Crisis Services & Lifelines",
    }
}

class CrisisSafetyChecker:
    """Detects high-risk distress signals and attaches supportive crisis care interventions."""

    @staticmethod
    def evaluate_text(text: Optional[str]) -> Dict[str, Any]:
        """Check journal or user text for severe distress or self-harm indications."""
        if not text or not text.strip():
            return {"is_crisis_detected": False, "resources": None}

        text_lower = text.lower()
        for pattern in HIGH_RISK_KEYWORDS:
            if re.search(pattern, text_lower):
                return {
                    "is_crisis_detected": True,
                    "support_message": (
                        "We noticed that you might be going through an intensely difficult moment. "
                        "Please know that you are not alone and there is compassionate, professional help available right now."
                    ),
                    "helpline_resources": CRISIS_RESOURCES,
                }

        return {"is_crisis_detected": False, "resources": None}

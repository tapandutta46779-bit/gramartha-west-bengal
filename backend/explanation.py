from __future__ import annotations

from backend.models.decision import DecisionExplanation, EvidenceGate

TEMPLATES = {
    "en": {
        "refusal": (
            "A venture recommendation was not produced because required evidence is missing."
        ),
        "conditional": "The result is conditional on the supplied evidence and assumptions.",
        "evidence": (
            "Computed values come from the frozen VentureDecision; missing inputs are not invented."
        ),
    },
    "bn": {
        "refusal": "প্রয়োজনীয় প্রমাণ অনুপস্থিত হওয়ায় কোনো উদ্যোগের সুপারিশ তৈরি করা হয়নি।",
        "conditional": "ফলাফলটি প্রদত্ত প্রমাণ ও অনুমানের উপর শর্তসাপেক্ষ।",
        "evidence": "হিসাব করা মানগুলি স্থির VentureDecision থেকে এসেছে; অনুপস্থিত তথ্য তৈরি করা হয়নি।",
    },
    "hi": {
        "refusal": "आवश्यक प्रमाण उपलब्ध न होने के कारण उद्यम की सिफारिश तैयार नहीं की गई।",
        "conditional": "परिणाम दिए गए प्रमाण और मान्यताओं पर सशर्त है।",
        "evidence": "गणना किए गए मान स्थिर VentureDecision से आते हैं; अनुपलब्ध जानकारी गढ़ी नहीं गई।",
    },
}


def deterministic_explanation(
    language: str, *, gates: list[EvidenceGate], has_selection: bool
) -> DecisionExplanation:
    selected_language = language if language in TEMPLATES else "en"
    template = TEMPLATES[selected_language]
    return DecisionExplanation(
        language=selected_language,
        summary=template["conditional"] if has_selection else template["refusal"],
        evidence_statement=template["evidence"],
        caveats=[f"{gate.code}: {gate.message}" for gate in gates],
    )

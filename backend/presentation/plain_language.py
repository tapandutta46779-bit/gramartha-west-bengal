from __future__ import annotations

# ruff: noqa: E501 - long multilingual strings are kept intact for translator review.
from backend.models.decision import DecisionStatus, VentureDecision
from backend.models.presentation import (
    CompetitionSummary,
    ConclusionStatus,
    PlainLanguagePresentation,
    PlainLanguageSummary,
    SummaryRange,
)

_SECTOR_NAMES = {
    "en": {
        "dairy": "Small dairy and milk service",
        "kirana": "Neighbourhood grocery shop",
        "poultry": "Poultry and egg aggregation",
        "fishery": "Fish collection and distribution",
        "food processing": "Small food processing unit",
        "flour mill": "Flour mill",
        "spice processing": "Spice processing unit",
        "mustard oil": "Mustard oil extraction unit",
        "household goods": "Household-goods distribution",
        "electronics": "Electronics and mobile retail",
        "transport": "Rural distribution and aggregation",
    },
    "bn": {
        "dairy": "ছোট দুগ্ধ ও দুধ পরিষেবা",
        "kirana": "পাড়ার মুদিখানা",
        "poultry": "পোল্ট্রি ও ডিম সংগ্রহ",
        "fishery": "মাছ সংগ্রহ ও বিতরণ",
        "food processing": "ক্ষুদ্র খাদ্য প্রক্রিয়াকরণ ইউনিট",
        "flour mill": "আটা কল",
        "spice processing": "মশলা প্রক্রিয়াকরণ ইউনিট",
        "mustard oil": "সরিষার তেল নিষ্কাশন ইউনিট",
        "household goods": "গৃহস্থালি পণ্য বিতরণ",
        "electronics": "ইলেকট্রনিক্স ও মোবাইল খুচরা বিক্রয়",
        "transport": "গ্রামীণ বিতরণ ও সংগ্রহ",
    },
    "hi": {
        "dairy": "छोटी डेयरी और दूध सेवा",
        "kirana": "पड़ोस की किराना दुकान",
        "poultry": "पोल्ट्री और अंडा एकत्रीकरण",
        "fishery": "मछली संग्रह और वितरण",
        "food processing": "लघु खाद्य प्रसंस्करण इकाई",
        "flour mill": "आटा चक्की",
        "spice processing": "मसाला प्रसंस्करण इकाई",
        "mustard oil": "सरसों तेल निष्कर्षण इकाई",
        "household goods": "घरेलू सामान वितरण",
        "electronics": "इलेक्ट्रॉनिक्स और मोबाइल खुदरा",
        "transport": "ग्रामीण वितरण और एकत्रीकरण",
    },
}

_TEXT = {
    "en": {
        "category": "Minimum viable local business",
        "why": "It is the lowest-investment tested configuration that satisfies the active profile constraints and improves useful local flow.",
        "why_here": "The evidence indicates a modelled service gap inside the selected catchment. This is a planning estimate, not measured locality turnover.",
        "suits": "An owner-operator who can supervise daily buying, selling, quality and cash control.",
        "avoid": "Avoid it if you cannot verify local customers, suppliers, prices and licences before committing capital.",
        "adv1": "Uses the minimum-capital configuration selected by the MVV test.",
        "adv2": "Keeps the recommendation tied to the selected locality and catchment.",
        "adv3": "Shows cash resilience, break-even and failure conditions before investment.",
        "dis1": "Local demand and supply are modelled from available evidence, not audited shop sales.",
        "dis2": "OSM candidate counts do not measure competitor capacity, sales or market share.",
        "risk1": "Actual selling price or input cost may differ from the planning range.",
        "risk2": "Working-capital pressure can delay break-even or create a cash shortfall.",
        "risk3": "Customer and supplier availability must be checked on the ground.",
        "action1": "Validate at least 20 likely customers and three suppliers before paying for equipment.",
        "action2": "Confirm current prices, licences, utilities and delivery costs in writing.",
        "action3": "Start with the minimum viable setup, track weekly cash, and expand only after repeat demand.",
        "confidence": "Confidence is {confidence}. Historical, estimated and current evidence remain separately labelled in the technical report.",
        "conclusion": {
            "PROMISING_VERIFY_START_SMALL": "Promising, but verify local prices and demand and start small.",
            "WORTH_TESTING_NOT_PROVEN": "Worth testing through a small pilot; the evidence does not prove business success.",
            "CAUTION_WEAK_OR_UNCERTAIN": "Proceed with caution because resilience or evidence quality is weak.",
            "NOT_ATTRACTIVE_UNDER_CURRENT_CONDITIONS": "Not attractive under the current capital, income or debt conditions.",
            "MORE_INFORMATION_IS_NEEDED_FIRST": "More information is needed before a responsible recommendation can be made.",
        },
        "labels": {
            "simple_summary": "Simple summary",
            "conclusion": "Bottom line",
            "why": "Why this venture",
            "who": "Who this suits",
            "avoid": "Who should avoid it",
            "money": "Money needed",
            "capital": "Total project cost",
            "own": "Own money used",
            "reserve": "Money kept as reserve",
            "finance": "External finance needed",
            "revenue": "Monthly revenue range",
            "cash": "Monthly operating-cash range",
            "break_even": "Operating break-even",
            "payback": "Investment payback",
            "market": "Local market",
            "demand": "Demand opportunity",
            "price": "Price guidance",
            "competition": "Competition",
            "advantages": "Top advantages",
            "disadvantages": "Main disadvantages",
            "risks": "Top risks",
            "actions": "First actions",
            "confidence": "Evidence confidence",
            "download": "Download PDF",
            "technical": "Detailed technical analysis",
            "month": "Month {month}",
            "beyond": "Beyond 36 months / not reached",
        },
    },
    "bn": {
        "category": "ন্যূনতম কার্যকর স্থানীয় ব্যবসা",
        "why": "এটি পরীক্ষিত বিকল্পগুলির মধ্যে সবচেয়ে কম বিনিয়োগের বিন্যাস, যা সক্রিয় প্রোফাইলের শর্ত পূরণ করে এবং উপযোগী স্থানীয় প্রবাহ বাড়ায়।",
        "why_here": "নির্বাচিত পরিসরে প্রমাণ একটি মডেলভিত্তিক পরিষেবা ঘাটতি নির্দেশ করে। এটি পরিকল্পনার অনুমান, স্থানীয় বিক্রয়ের প্রত্যক্ষ মাপ নয়।",
        "suits": "যিনি প্রতিদিনের ক্রয়, বিক্রয়, মান ও নগদ নিয়ন্ত্রণ নিজে তদারক করতে পারবেন।",
        "avoid": "মূলধন দেওয়ার আগে স্থানীয় ক্রেতা, সরবরাহকারী, দাম ও লাইসেন্স যাচাই করতে না পারলে এই উদ্যোগ এড়িয়ে চলুন।",
        "adv1": "MVV পরীক্ষায় নির্বাচিত সর্বনিম্ন মূলধনের বিন্যাস ব্যবহার করে।",
        "adv2": "সুপারিশটি নির্বাচিত এলাকা ও ক্যাচমেন্টের সঙ্গে যুক্ত থাকে।",
        "adv3": "বিনিয়োগের আগে নগদ স্থিতি, ব্রেক-ইভেন ও ব্যর্থতার সীমা দেখায়।",
        "dis1": "স্থানীয় চাহিদা ও সরবরাহ প্রাপ্ত প্রমাণ থেকে মডেল করা, নিরীক্ষিত দোকান বিক্রয় নয়।",
        "dis2": "OSM প্রার্থীর সংখ্যা প্রতিযোগীর ক্ষমতা, বিক্রয় বা বাজার অংশ মাপে না।",
        "risk1": "প্রকৃত বিক্রয়দর বা উপকরণ খরচ পরিকল্পিত সীমা থেকে আলাদা হতে পারে।",
        "risk2": "কার্যকরী মূলধনের চাপ ব্রেক-ইভেন বিলম্বিত করতে বা নগদ ঘাটতি তৈরি করতে পারে।",
        "risk3": "ক্রেতা ও সরবরাহকারীর প্রাপ্যতা মাঠে যাচাই করতে হবে।",
        "action1": "যন্ত্রপাতির টাকা দেওয়ার আগে অন্তত ২০ জন সম্ভাব্য ক্রেতা ও তিনজন সরবরাহকারী যাচাই করুন।",
        "action2": "বর্তমান দাম, লাইসেন্স, বিদ্যুৎ-পানি ও পরিবহন খরচ লিখিতভাবে নিশ্চিত করুন।",
        "action3": "ন্যূনতম কার্যকর বিন্যাসে শুরু করুন, সাপ্তাহিক নগদ হিসাব রাখুন এবং পুনরাবৃত্ত চাহিদার পরেই বাড়ান।",
        "confidence": "প্রমাণের আস্থা {confidence}। ঐতিহাসিক, অনুমিত ও বর্তমান প্রমাণ প্রযুক্তিগত প্রতিবেদনে আলাদাভাবে চিহ্নিত।",
        "conclusion": {
            "PROMISING_VERIFY_START_SMALL": "সম্ভাবনাময়, তবে স্থানীয় দাম ও চাহিদা যাচাই করে ছোটভাবে শুরু করুন।",
            "WORTH_TESTING_NOT_PROVEN": "ছোট পরীক্ষামূলক উদ্যোগ হিসেবে যাচাইযোগ্য; প্রমাণ ব্যবসায়িক সাফল্য নিশ্চিত করে না।",
            "CAUTION_WEAK_OR_UNCERTAIN": "স্থিতিশীলতা বা প্রমাণের মান দুর্বল হওয়ায় সতর্কভাবে এগোন।",
            "NOT_ATTRACTIVE_UNDER_CURRENT_CONDITIONS": "বর্তমান মূলধন, আয় বা ঋণের শর্তে আকর্ষণীয় নয়।",
            "MORE_INFORMATION_IS_NEEDED_FIRST": "দায়িত্বশীল সুপারিশের আগে আরও তথ্য প্রয়োজন।",
        },
        "labels": {
            "simple_summary": "সহজ সারাংশ",
            "conclusion": "মূল সিদ্ধান্ত",
            "why": "কেন এই উদ্যোগ",
            "who": "কার জন্য উপযুক্ত",
            "avoid": "কার এড়ানো উচিত",
            "money": "প্রয়োজনীয় অর্থ",
            "capital": "মোট প্রকল্প ব্যয়",
            "own": "নিজস্ব অর্থের ব্যবহার",
            "reserve": "সংরক্ষিত অর্থ",
            "finance": "বাহ্যিক অর্থায়নের প্রয়োজন",
            "revenue": "মাসিক আয়ের সীমা",
            "cash": "মাসিক পরিচালন নগদের সীমা",
            "break_even": "পরিচালন ব্রেক-ইভেন",
            "payback": "বিনিয়োগ ফেরত",
            "market": "স্থানীয় বাজার",
            "demand": "চাহিদার সুযোগ",
            "price": "দামের নির্দেশনা",
            "competition": "প্রতিযোগিতা",
            "advantages": "প্রধান সুবিধা",
            "disadvantages": "প্রধান অসুবিধা",
            "risks": "প্রধান ঝুঁকি",
            "actions": "প্রথম পদক্ষেপ",
            "confidence": "প্রমাণের আস্থা",
            "download": "PDF ডাউনলোড",
            "technical": "বিস্তারিত প্রযুক্তিগত বিশ্লেষণ",
            "month": "মাস {month}",
            "beyond": "৩৬ মাসের পরে / অর্জিত নয়",
        },
    },
    "hi": {
        "category": "न्यूनतम व्यवहार्य स्थानीय व्यवसाय",
        "why": "यह सबसे कम निवेश वाला परीक्षण किया गया विन्यास है जो सक्रिय प्रोफ़ाइल शर्तें पूरी करता है और उपयोगी स्थानीय प्रवाह बढ़ाता है।",
        "why_here": "चुने गए क्षेत्र में प्रमाण एक मॉडल-आधारित सेवा अंतर दिखाते हैं। यह योजना अनुमान है, स्थानीय बिक्री का प्रत्यक्ष माप नहीं।",
        "suits": "ऐसा मालिक-संचालक जो रोज़ की खरीद, बिक्री, गुणवत्ता और नकदी नियंत्रण देख सके।",
        "avoid": "पूंजी लगाने से पहले स्थानीय ग्राहक, आपूर्तिकर्ता, मूल्य और लाइसेंस सत्यापित न कर सकें तो इसे न चुनें।",
        "adv1": "MVV परीक्षण से चुना गया न्यूनतम-पूंजी विन्यास उपयोग करता है।",
        "adv2": "सिफारिश चुने गए स्थान और कैचमेंट से जुड़ी रहती है।",
        "adv3": "निवेश से पहले नकदी मजबूती, ब्रेक-ईवन और विफलता सीमाएं दिखाता है।",
        "dis1": "स्थानीय मांग और आपूर्ति उपलब्ध प्रमाण से मॉडल की गई है, ऑडिट की हुई दुकान बिक्री नहीं।",
        "dis2": "OSM उम्मीदवारों की संख्या प्रतिस्पर्धी क्षमता, बिक्री या बाजार हिस्सेदारी नहीं मापती।",
        "risk1": "वास्तविक बिक्री मूल्य या इनपुट लागत योजना सीमा से अलग हो सकती है।",
        "risk2": "कार्यशील पूंजी का दबाव ब्रेक-ईवन टाल सकता है या नकदी कमी बना सकता है।",
        "risk3": "ग्राहक और आपूर्तिकर्ता उपलब्धता जमीन पर जांचनी होगी।",
        "action1": "उपकरण का भुगतान करने से पहले कम से कम 20 संभावित ग्राहक और तीन आपूर्तिकर्ता जांचें।",
        "action2": "वर्तमान मूल्य, लाइसेंस, उपयोगिताएं और डिलीवरी लागत लिखित में पुष्टि करें।",
        "action3": "न्यूनतम व्यवहार्य सेटअप से शुरू करें, साप्ताहिक नकदी देखें और दोहराव वाली मांग के बाद ही विस्तार करें।",
        "confidence": "प्रमाण का भरोसा {confidence} है। ऐतिहासिक, अनुमानित और वर्तमान प्रमाण तकनीकी रिपोर्ट में अलग चिह्नित हैं।",
        "conclusion": {
            "PROMISING_VERIFY_START_SMALL": "संभावनाशील, लेकिन स्थानीय मूल्य और मांग जांचकर छोटे स्तर से शुरू करें।",
            "WORTH_TESTING_NOT_PROVEN": "छोटे पायलट में परीक्षण योग्य; प्रमाण व्यवसाय की सफलता सिद्ध नहीं करता।",
            "CAUTION_WEAK_OR_UNCERTAIN": "मजबूती या प्रमाण गुणवत्ता कमजोर होने के कारण सावधानी से आगे बढ़ें।",
            "NOT_ATTRACTIVE_UNDER_CURRENT_CONDITIONS": "वर्तमान पूंजी, आय या ऋण शर्तों में आकर्षक नहीं।",
            "MORE_INFORMATION_IS_NEEDED_FIRST": "जिम्मेदार सिफारिश से पहले अधिक जानकारी चाहिए।",
        },
        "labels": {
            "simple_summary": "सरल सारांश",
            "conclusion": "मुख्य निष्कर्ष",
            "why": "यह उद्यम क्यों",
            "who": "किसके लिए उपयुक्त",
            "avoid": "किसे इससे बचना चाहिए",
            "money": "कितना पैसा चाहिए",
            "capital": "कुल परियोजना लागत",
            "own": "अपना लगाया पैसा",
            "reserve": "बचाकर रखी राशि",
            "finance": "बाहरी वित्त की जरूरत",
            "revenue": "मासिक आय सीमा",
            "cash": "मासिक परिचालन नकदी सीमा",
            "break_even": "परिचालन ब्रेक-ईवन",
            "payback": "निवेश वापसी",
            "market": "स्थानीय बाजार",
            "demand": "मांग अवसर",
            "price": "मूल्य मार्गदर्शन",
            "competition": "प्रतिस्पर्धा",
            "advantages": "मुख्य लाभ",
            "disadvantages": "मुख्य नुकसान",
            "risks": "मुख्य जोखिम",
            "actions": "पहले कदम",
            "confidence": "प्रमाण भरोसा",
            "download": "PDF डाउनलोड",
            "technical": "विस्तृत तकनीकी विश्लेषण",
            "month": "माह {month}",
            "beyond": "36 माह से बाद / प्राप्त नहीं",
        },
    },
}


def _range(value, unit: str, status: str, spread: float = 0) -> SummaryRange:
    if value is None:
        return SummaryRange(unit=unit, status="UNAVAILABLE")
    central = float(value)
    return SummaryRange(
        lower=max(0.0, central * (1 - spread)),
        central=central,
        upper=central * (1 + spread),
        unit=unit,
        status=status,
    )


def _interval(interval, fallback_unit: str) -> SummaryRange:
    if interval is None:
        return SummaryRange(unit=fallback_unit, status="UNAVAILABLE")
    return SummaryRange(
        lower=interval.lower,
        central=interval.central,
        upper=interval.upper,
        unit=interval.unit,
        status=interval.status,
    )


def _conclusion(decision: VentureDecision) -> ConclusionStatus:
    if decision.status == DecisionStatus.INSUFFICIENT_EVIDENCE:
        return ConclusionStatus.MORE_INFORMATION_IS_NEEDED_FIRST
    if decision.status == DecisionStatus.NOT_FEASIBLE or decision.selected_venture is None:
        return ConclusionStatus.NOT_ATTRACTIVE_UNDER_CURRENT_CONDITIONS
    scenario = next(
        (
            item
            for item in decision.robust_comparison.get("candidate_summaries", [])
            if item.get("candidate_id") == decision.selected_venture.candidate_id
        ),
        {},
    )
    survival = scenario.get("scenario_survival_rate")
    if survival is not None and survival < 0.6:
        return ConclusionStatus.CAUTION_WEAK_OR_UNCERTAIN
    if decision.confidence.value in {"LOW", "INSUFFICIENT"}:
        return ConclusionStatus.CAUTION_WEAK_OR_UNCERTAIN
    if survival is not None and survival >= 0.8:
        return ConclusionStatus.PROMISING_VERIFY_START_SMALL
    return ConclusionStatus.WORTH_TESTING_NOT_PROVEN


def build_plain_language_summary(decision: VentureDecision) -> PlainLanguageSummary:
    venture = decision.selected_venture
    sector = decision.sector or ""
    twin = decision.digital_twin
    month_12 = twin.months[min(11, len(twin.months) - 1)] if twin and twin.months else None
    conclusion = _conclusion(decision)
    category = _TEXT["en"]["category"]
    name = _SECTOR_NAMES["en"].get(sector, sector.title() or "No venture selected")
    competition = decision.competition or {}
    direct = competition.get("likely_direct_competitors") or []
    indirect = competition.get("likely_indirect_competitors") or []
    coordinate = competition.get("coordinate") or decision.catchment.get("coordinate") or {}
    competition_summary = CompetitionSummary(
        direct_count=competition.get("direct_count"),
        indirect_count=competition.get("indirect_count"),
        intensity=competition.get("competition_intensity", "UNKNOWN"),
        radius_km=decision.catchment.get("radius_km"),
        coordinate_quality=(
            competition.get("coordinate_quality")
            or coordinate.get("coordinate_quality")
            or coordinate.get("quality")
        ),
        nearest_direct_name=(direct[0].get("name") if direct else None),
        nearest_indirect_name=(indirect[0].get("name") if indirect else None),
        caveat=competition.get("caveat")
        or "Mapped feature counts do not measure capacity, sales or market share.",
    )
    financing = decision.prudent_financing or {}
    localized = {}
    for language in ("en", "bn", "hi"):
        text = _TEXT[language]
        localized[language] = PlainLanguagePresentation(
            language=language,
            recommended_venture_name=_SECTOR_NAMES[language].get(
                sector, name if language == "en" else sector.title() or "-"
            ),
            recommended_venture_category=text["category"],
            why_recommended=text["why"],
            why_here=text["why_here"],
            who_suits=text["suits"],
            who_should_avoid=text["avoid"],
            top_advantages=[text["adv1"], text["adv2"], text["adv3"]],
            top_disadvantages=[text["dis1"], text["dis2"]],
            top_risks=[text["risk1"], text["risk2"], text["risk3"]],
            top_actions=[text["action1"], text["action2"], text["action3"]],
            data_confidence=text["confidence"].format(confidence=decision.confidence.value),
            conclusion_text=text["conclusion"][conclusion.value],
            labels=text["labels"],
        )
    english = localized["en"]
    return PlainLanguageSummary(
        analysis_id=decision.analysis_id,
        conclusion_status=conclusion,
        recommended_venture_name=name,
        recommended_venture_category=category,
        why_recommended=english.why_recommended,
        why_here=english.why_here,
        who_suits=english.who_suits,
        who_should_avoid=english.who_should_avoid,
        capital_required=_range(
            venture.investment if venture else None, "INR", "PLANNING_RANGE", 0.08
        ),
        own_money_used=_range(financing.get("own_capital_deployed"), "INR", "MODELLED"),
        money_kept_as_reserve=_range(
            financing.get("capital_preserved_as_reserve"), "INR", "MODELLED"
        ),
        finance_needed=_range(
            financing.get("illustrative_financing_requirement"), "INR", "ILLUSTRATIVE"
        ),
        monthly_revenue=_range(
            month_12.revenue if month_12 else None, "INR/month", "PROJECTED_MONTH_12", 0.1
        ),
        monthly_operating_cash=_range(
            month_12.operating_cash_flow if month_12 else None,
            "INR/month",
            "PROJECTED_MONTH_12",
            0.2,
        ),
        break_even_month=decision.operating_break_even,
        payback_month=decision.investment_payback,
        demand_opportunity=_interval(decision.demand, "units/month"),
        price_guidance=_interval(decision.price, "INR/unit"),
        competition_summary=competition_summary,
        top_advantages=english.top_advantages,
        top_disadvantages=english.top_disadvantages,
        top_risks=english.top_risks,
        top_actions=english.top_actions,
        data_confidence=english.data_confidence,
        conclusion_text=english.conclusion_text,
        presentations=localized,
    )

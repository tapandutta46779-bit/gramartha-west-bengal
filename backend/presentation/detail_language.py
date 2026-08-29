from __future__ import annotations

import re

# ruff: noqa: E501 - aligned multilingual vocabulary stays on parallel review lines.

# Human-reviewed deterministic presentation vocabulary.  Numbers, identifiers,
# locality names, source titles and URLs are deliberately never translated.

DETAIL_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "recommended_case": "Recommended planning case", "confidence": "confidence",
        "summary": "Summary", "market": "Local market", "opportunities": "Opportunities",
        "risk": "Risk & SWOT", "plan": "Business plan", "finance": "Finance",
        "action": "Action plan", "why_fits": "Why it fits here",
        "why_fits_body": "The flow model found a modelled service gap and the MVV oracle selected the lowest-investment tested configuration that repairs useful flow within your capital constraint.",
        "project_cost": "Project cost", "planning_interval": "planning interval",
        "own_capital": "Own capital deployed", "reserve_note": "remaining capital is reserve",
        "finance_required": "Finance required", "debt_note": "within your debt ceiling",
        "monthly_revenue": "Monthly revenue", "month12_model": "month 12 model",
        "owner_income": "Owner-income range", "cash_band": "central cash surplus ±20% planning band",
        "payback": "Investment payback", "beyond36": "Beyond 36 months",
        "not_operating_be": "not operating break-even", "scenario_survival": "Scenario survival",
        "quick_plan": "Quick plan", "planning_scenarios": "planning scenarios",
        "central_only": "central estimate only", "market_gap": "Market gap",
        "modelled_not_turnover": "modelled, not observed turnover", "entry_difficulty": "Entry difficulty",
        "unknown": "Unknown", "preserve_capital": "Preserve capital",
        "why_good": "Why it is good", "main_disadvantage": "Main disadvantage",
        "who_suits": "Who it suits", "who_avoid": "Who should avoid it",
        "geographic_evidence": "Geographic evidence", "canonical_locality": "Canonical locality",
        "current_hierarchy": "Current hierarchy", "locality_type": "Locality type",
        "coordinates_quality": "Coordinates / quality", "catchment_radius": "Catchment radius",
        "geography_sources": "Geography sources", "crosswalk": "Crosswalk",
        "geography_status": "Geography status", "demand_supply": "Demand and reachable supply",
        "demand": "Demand", "supply": "Supply", "demand_opportunity": "Demand / opportunity",
        "reachable_supply": "Reachable incumbent supply", "price": "Price / unit value",
        "gap": "Gap", "competition_catchment": "Competition and catchment",
        "direct_inside": "Direct OSM candidates inside radius", "indirect_inside": "Indirect OSM candidates inside radius",
        "nearest_direct": "Nearest named direct", "nearest_indirect": "Nearest named indirect",
        "competition_intensity": "Competition intensity", "planning_radius": "Planning radius",
        "discovery_radius": "Nearby-name discovery radius", "nearest_market": "Nearest market",
        "nearest_institution": "Nearest institution", "incumbent_capacity": "Incumbent capacity",
        "customer_segments": "Customer segments", "supplier_plan": "Supplier plan", "channels": "Channels",
        "all_direct": "All named direct alternatives", "all_indirect": "All named indirect alternatives",
        "repair_path": "Economic repair path", "suppliers": "Suppliers", "bottleneck": "Current service bottleneck",
        "customers": "Customers", "new_flow": "Newly served flow", "cannibalized": "Cannibalized existing flow",
        "options_tested": "Options tested", "option": "Option", "investment": "Investment",
        "capacity": "Capacity", "role": "Role", "other_sectors": "Other sectors compared",
        "computed_swot": "Computed SWOT", "scenario_resilience": "Scenario resilience",
        "scenarios": "Scenarios", "remain_solvent": "Remain solvent", "payback36": "Payback within 36 months",
        "p10_cash": "10th percentile minimum cash", "cvar": "Worst 5% cumulative cash (CVaR)",
        "not_run": "Not run", "sensitivity": "Sensitivity tornado", "premortem": "Pre-mortem: why this could fail",
        "failure_boundaries": "Adaptive failure boundaries", "run_deep": "Run Deep analysis to calculate boundaries.",
        "scenario_caveat": "Scenario rates are modelled planning survival, not probability of success. The triangular factors are not empirically calibrated.",
        "minimum_setup": "Minimum viable setup", "equipment_setup": "Equipment and setup",
        "working_capital": "Working capital", "monthly_opex": "Monthly fixed OPEX", "people": "People",
        "space": "Space", "service_radius": "Service radius", "capex_allocation": "CAPEX allocation",
        "working_cycle": "Working-capital cycle", "minimum_modelled": "Minimum modelled",
        "buffer15": "Recommended +15% buffer", "inventory_days": "Inventory days",
        "receivable_days": "Receivable days", "payable_days": "Payable days",
        "cash_cycle": "Cash conversion cycle", "licences": "Licences to verify", "equipment": "Equipment",
        "quality_controls": "Quality controls", "operational_factors": "Operational factors",
        "weather": "Weather and seasonality", "insurance": "Insurance / protection", "customer_plan": "Customer plan",
        "total_cost": "Total project cost", "your_capital": "Your own capital", "entered_by_you": "entered by you",
        "external_finance": "External financing", "illustrative": "illustrative, not approved",
        "operating_be": "Operating break-even", "cash_be": "Cash break-even", "closing_cash": "closing cash",
        "owner_recovered": "owner capital recovered", "unit_economics": "Unit economics and investment metrics",
        "gross_margin": "Gross margin", "month12": "month 12", "break_even_volume": "Break-even volume",
        "planning_units": "planning revenue units/month", "npv": "36-month NPV", "discount": "12% annual discount rate",
        "irr": "Annualized IRR", "benchmark_assumptions": "benchmark-adjusted assumptions",
        "cash36": "36-month closing cash", "finance_fit": "Possible finance fit",
        "before_starting": "Before starting", "week1": "Week 1", "month1": "Month 1",
        "months23": "Months 2–3", "months46": "Months 4–6", "stop_reconsider": "Stop / reconsider",
        "decision_chain": "Decision chain", "estimate_class": "Estimate class", "scope": "Scope",
        "evidence_limits": "Evidence limitations", "source_links": "Source links",
        "operational_weather": "Operational and weather factors", "operational": "Operational",
        "business_guidance": "Business-specific decision guidance", "advantages": "Advantages",
        "disadvantages_risks": "Disadvantages and top risks", "osm_context": "OSM competition and nearby context",
        "inside_radius": "inside planning radius", "outside_radius": "outside planning radius",
        "unnamed": "Unnamed mapped candidate", "mapped_place": "Mapped place", "no_candidate": "No mapped candidate found in the bounded search. This does not prove none exists.",
        "no_named": "No named candidate in bounded search", "page": "Page", "technical_report": "Detailed technical report",
        "recommendation": "Recommendation", "local_market_evidence": "Local market and evidence",
        "competition": "Competition and catchment", "business_setup": "Business setup",
        "costs": "CAPEX, OPEX and working capital", "finance_cash": "Finance and 36-month cash flow",
        "risk_scenarios": "Scenario analysis, SWOT and failure boundaries", "actions": "Action plan",
        "evidence": "Evidence, confidence and limitations", "variable": "Variable", "dataset": "Dataset",
        "observation": "Observation", "freshness": "Freshness", "status": "Status", "source": "Source",
        "limitations": "Limitations", "sources": "Sources", "name": "Name", "category": "Category",
        "distance": "Straight-line distance", "month": "Month", "revenue": "Revenue", "operating_cash": "Operating cash",
        "scheme": "Scheme", "eligibility": "Eligibility", "threshold": "Threshold", "interpretation": "Interpretation",
    },
    "bn": {}, "hi": {},
}

DETAIL_LABELS["bn"] = {
    "recommended_case":"সুপারিশকৃত পরিকল্পনার ক্ষেত্র","confidence":"আস্থা","summary":"সারাংশ","market":"স্থানীয় বাজার","opportunities":"সুযোগ","risk":"ঝুঁকি ও SWOT","plan":"ব্যবসায়িক পরিকল্পনা","finance":"অর্থায়ন","action":"কর্মপরিকল্পনা","why_fits":"এখানে কেন উপযুক্ত","why_fits_body":"প্রবাহ মডেল একটি মডেলভিত্তিক পরিষেবা ঘাটতি পেয়েছে এবং MVV পদ্ধতি আপনার মূলধনসীমার মধ্যে উপযোগী প্রবাহ মেরামতকারী সর্বনিম্ন বিনিয়োগের পরীক্ষিত বিন্যাস বেছে নিয়েছে।","project_cost":"প্রকল্প ব্যয়","planning_interval":"পরিকল্পনার সীমা","own_capital":"ব্যবহৃত নিজস্ব মূলধন","reserve_note":"অবশিষ্ট মূলধন সংরক্ষিত","finance_required":"প্রয়োজনীয় অর্থায়ন","debt_note":"আপনার ঋণসীমার মধ্যে","monthly_revenue":"মাসিক আয়","month12_model":"১২তম মাসের মডেল","owner_income":"মালিকের আয়ের সীমা","cash_band":"কেন্দ্রীয় নগদ উদ্বৃত্তের ±২০% পরিকল্পনা সীমা","payback":"বিনিয়োগ ফেরত","beyond36":"৩৬ মাসের পরে","not_operating_be":"পরিচালন ব্রেক-ইভেন নয়","scenario_survival":"দৃশ্যপট টিকে থাকা","quick_plan":"দ্রুত পরিকল্পনা","planning_scenarios":"পরিকল্পনা দৃশ্যপট","central_only":"শুধু কেন্দ্রীয় অনুমান","market_gap":"বাজারের ঘাটতি","modelled_not_turnover":"মডেলভিত্তিক, প্রত্যক্ষ বিক্রয় নয়","entry_difficulty":"প্রবেশের কঠিনতা","unknown":"অজানা","preserve_capital":"মূলধন সংরক্ষণ","why_good":"কেন ভালো","main_disadvantage":"প্রধান অসুবিধা","who_suits":"কার জন্য উপযুক্ত","who_avoid":"কার এড়ানো উচিত","geographic_evidence":"ভৌগোলিক প্রমাণ","canonical_locality":"মান্য স্থানীয় এলাকা","current_hierarchy":"বর্তমান প্রশাসনিক স্তর","locality_type":"এলাকার ধরন","coordinates_quality":"স্থানাঙ্ক / মান","catchment_radius":"ক্যাচমেন্ট ব্যাসার্ধ","geography_sources":"ভৌগোলিক উৎস","crosswalk":"ঐতিহাসিক-বর্তমান ক্রসওয়াক","geography_status":"ভৌগোলিক অবস্থা","demand_supply":"চাহিদা ও পৌঁছানো যায় এমন সরবরাহ","demand":"চাহিদা","supply":"সরবরাহ","demand_opportunity":"চাহিদা / সুযোগ","reachable_supply":"পৌঁছানো যায় এমন বর্তমান সরবরাহ","price":"দাম / একক মূল্য","gap":"ঘাটতি","competition_catchment":"প্রতিযোগিতা ও ক্যাচমেন্ট","direct_inside":"ব্যাসার্ধের মধ্যে সরাসরি OSM প্রার্থী","indirect_inside":"ব্যাসার্ধের মধ্যে পরোক্ষ OSM প্রার্থী","nearest_direct":"নিকটতম নামযুক্ত সরাসরি প্রার্থী","nearest_indirect":"নিকটতম নামযুক্ত পরোক্ষ প্রার্থী","competition_intensity":"প্রতিযোগিতার ঘনত্ব","planning_radius":"পরিকল্পনা ব্যাসার্ধ","discovery_radius":"নিকটবর্তী নাম অনুসন্ধান ব্যাসার্ধ","nearest_market":"নিকটতম বাজার","nearest_institution":"নিকটতম প্রতিষ্ঠান","incumbent_capacity":"বর্তমান ক্ষমতা","customer_segments":"ক্রেতা গোষ্ঠী","supplier_plan":"সরবরাহকারী পরিকল্পনা","channels":"বিক্রয় চ্যানেল","all_direct":"সব নামযুক্ত সরাসরি বিকল্প","all_indirect":"সব নামযুক্ত পরোক্ষ বিকল্প","repair_path":"অর্থনৈতিক মেরামত পথ","suppliers":"সরবরাহকারী","bottleneck":"বর্তমান পরিষেবা প্রতিবন্ধকতা","customers":"ক্রেতা","new_flow":"নতুনভাবে পরিবেশিত প্রবাহ","cannibalized":"বর্তমান প্রবাহ থেকে স্থানান্তর","options_tested":"পরীক্ষিত বিকল্প","option":"বিকল্প","investment":"বিনিয়োগ","capacity":"ক্ষমতা","role":"ভূমিকা","other_sectors":"তুলনাকৃত অন্য খাত","computed_swot":"হিসাব করা SWOT","scenario_resilience":"দৃশ্যপট স্থিতি","scenarios":"দৃশ্যপট","remain_solvent":"ঋণশোধ সক্ষম থাকে","payback36":"৩৬ মাসের মধ্যে বিনিয়োগ ফেরত","p10_cash":"১০ম পার্সেন্টাইল ন্যূনতম নগদ","cvar":"সবচেয়ে খারাপ ৫% সঞ্চিত নগদ (CVaR)","not_run":"চালানো হয়নি","sensitivity":"সংবেদনশীলতা টর্নেডো","premortem":"প্রি-মর্টেম: কেন ব্যর্থ হতে পারে","failure_boundaries":"অভিযোজিত ব্যর্থতার সীমা","run_deep":"সীমা হিসাব করতে গভীর বিশ্লেষণ চালান।","scenario_caveat":"দৃশ্যপটের হার মডেলভিত্তিক পরিকল্পনার টিকে থাকা; সাফল্যের সম্ভাবনা নয়। ত্রিভুজীয় উপাদানগুলি তথ্য দিয়ে ক্যালিব্রেট করা নয়।","minimum_setup":"ন্যূনতম কার্যকর বিন্যাস","equipment_setup":"যন্ত্রপাতি ও স্থাপন","working_capital":"কার্যকরী মূলধন","monthly_opex":"মাসিক স্থির পরিচালন ব্যয়","people":"কর্মী","space":"জায়গা","service_radius":"পরিষেবা ব্যাসার্ধ","capex_allocation":"মূলধনী ব্যয়ের বণ্টন","working_cycle":"কার্যকরী মূলধন চক্র","minimum_modelled":"মডেলভিত্তিক ন্যূনতম","buffer15":"সুপারিশকৃত +১৫% সুরক্ষা","inventory_days":"মজুতের দিন","receivable_days":"পাওনা আদায়ের দিন","payable_days":"দেনা পরিশোধের দিন","cash_cycle":"নগদ রূপান্তর চক্র","licences":"যে লাইসেন্স যাচাই করতে হবে","equipment":"যন্ত্রপাতি","quality_controls":"মান নিয়ন্ত্রণ","operational_factors":"পরিচালন উপাদান","weather":"আবহাওয়া ও মৌসুম","insurance":"বীমা / সুরক্ষা","customer_plan":"ক্রেতা পরিকল্পনা","total_cost":"মোট প্রকল্প ব্যয়","your_capital":"আপনার নিজস্ব মূলধন","entered_by_you":"আপনার দেওয়া","external_finance":"বাহ্যিক অর্থায়ন","illustrative":"উদাহরণমূলক, অনুমোদিত নয়","operating_be":"পরিচালন ব্রেক-ইভেন","cash_be":"নগদ ব্রেক-ইভেন","closing_cash":"সমাপনী নগদ","owner_recovered":"মালিকের মূলধন ফেরত","unit_economics":"একক অর্থনীতি ও বিনিয়োগ সূচক","gross_margin":"মোট মার্জিন","month12":"১২তম মাস","break_even_volume":"ব্রেক-ইভেন পরিমাণ","planning_units":"পরিকল্পিত আয় একক/মাস","npv":"৩৬ মাসের NPV","discount":"বার্ষিক ১২% ছাড়ের হার","irr":"বার্ষিক IRR","benchmark_assumptions":"বেঞ্চমার্ক-সমন্বিত অনুমান","cash36":"৩৬ মাসের সমাপনী নগদ","finance_fit":"সম্ভাব্য অর্থায়ন সামঞ্জস্য","before_starting":"শুরু করার আগে","week1":"প্রথম সপ্তাহ","month1":"প্রথম মাস","months23":"মাস ২–৩","months46":"মাস ৪–৬","stop_reconsider":"থামুন / পুনর্বিবেচনা","decision_chain":"সিদ্ধান্ত শৃঙ্খল","estimate_class":"অনুমানের শ্রেণি","scope":"পরিসর","evidence_limits":"প্রমাণের সীমাবদ্ধতা","source_links":"উৎসের লিংক","operational_weather":"পরিচালন ও আবহাওয়ার উপাদান","operational":"পরিচালন","business_guidance":"ব্যবসা-নির্দিষ্ট সিদ্ধান্ত নির্দেশনা","advantages":"সুবিধা","disadvantages_risks":"অসুবিধা ও প্রধান ঝুঁকি","osm_context":"OSM প্রতিযোগিতা ও নিকটবর্তী প্রেক্ষিত","inside_radius":"পরিকল্পনা ব্যাসার্ধের মধ্যে","outside_radius":"পরিকল্পনা ব্যাসার্ধের বাইরে","unnamed":"নামহীন মানচিত্র প্রার্থী","mapped_place":"মানচিত্রভুক্ত স্থান","no_candidate":"সীমিত অনুসন্ধানে কোনো মানচিত্রভুক্ত প্রার্থী মেলেনি। এতে প্রার্থী নেই প্রমাণ হয় না।","no_named":"সীমিত অনুসন্ধানে নামযুক্ত প্রার্থী নেই","page":"পৃষ্ঠা","technical_report":"বিস্তারিত প্রযুক্তিগত প্রতিবেদন","recommendation":"সুপারিশ","local_market_evidence":"স্থানীয় বাজার ও প্রমাণ","competition":"প্রতিযোগিতা ও ক্যাচমেন্ট","business_setup":"ব্যবসা স্থাপন","costs":"মূলধনী ব্যয়, পরিচালন ব্যয় ও কার্যকরী মূলধন","finance_cash":"অর্থায়ন ও ৩৬ মাসের নগদ প্রবাহ","risk_scenarios":"দৃশ্যপট বিশ্লেষণ, SWOT ও ব্যর্থতার সীমা","actions":"কর্মপরিকল্পনা","evidence":"প্রমাণ, আস্থা ও সীমাবদ্ধতা","variable":"চলক","dataset":"ডেটাসেট","observation":"পর্যবেক্ষণ","freshness":"সাম্প্রতিকতার অবস্থা","status":"অবস্থা","source":"উৎস","limitations":"সীমাবদ্ধতা","sources":"উৎসসমূহ","name":"নাম","category":"শ্রেণি","distance":"সরলরেখার দূরত্ব","month":"মাস","revenue":"আয়","operating_cash":"পরিচালন নগদ","scheme":"প্রকল্প","eligibility":"যোগ্যতা","threshold":"সীমামান","interpretation":"ব্যাখ্যা"
}

DETAIL_LABELS["hi"] = {
    "recommended_case":"अनुशंसित योजना मामला","confidence":"भरोसा","summary":"सारांश","market":"स्थानीय बाजार","opportunities":"अवसर","risk":"जोखिम और SWOT","plan":"व्यवसाय योजना","finance":"वित्त","action":"कार्य योजना","why_fits":"यहाँ क्यों उपयुक्त है","why_fits_body":"प्रवाह मॉडल ने एक मॉडल-आधारित सेवा अंतर पाया और MVV पद्धति ने आपकी पूंजी सीमा में उपयोगी प्रवाह सुधारने वाला सबसे कम निवेश का परीक्षण किया गया विन्यास चुना।","project_cost":"परियोजना लागत","planning_interval":"योजना सीमा","own_capital":"लगाई गई अपनी पूंजी","reserve_note":"बाकी पूंजी आरक्षित","finance_required":"आवश्यक वित्त","debt_note":"आपकी ऋण सीमा के भीतर","monthly_revenue":"मासिक आय","month12_model":"माह 12 मॉडल","owner_income":"मालिक आय सीमा","cash_band":"केंद्रीय नकदी अधिशेष की ±20% योजना सीमा","payback":"निवेश वापसी","beyond36":"36 माह के बाद","not_operating_be":"परिचालन ब्रेक-ईवन नहीं","scenario_survival":"परिदृश्य टिकाऊपन","quick_plan":"त्वरित योजना","planning_scenarios":"योजना परिदृश्य","central_only":"केवल केंद्रीय अनुमान","market_gap":"बाजार अंतर","modelled_not_turnover":"मॉडल-आधारित, प्रत्यक्ष बिक्री नहीं","entry_difficulty":"प्रवेश कठिनाई","unknown":"अज्ञात","preserve_capital":"पूंजी बचाएँ","why_good":"क्यों अच्छा है","main_disadvantage":"मुख्य नुकसान","who_suits":"किसके लिए उपयुक्त","who_avoid":"किसे इससे बचना चाहिए","geographic_evidence":"भौगोलिक प्रमाण","canonical_locality":"मान्य स्थानीय क्षेत्र","current_hierarchy":"वर्तमान प्रशासनिक क्रम","locality_type":"क्षेत्र का प्रकार","coordinates_quality":"निर्देशांक / गुणवत्ता","catchment_radius":"कैचमेंट त्रिज्या","geography_sources":"भौगोलिक स्रोत","crosswalk":"ऐतिहासिक-वर्तमान क्रॉसवॉक","geography_status":"भौगोलिक स्थिति","demand_supply":"मांग और पहुँच योग्य आपूर्ति","demand":"मांग","supply":"आपूर्ति","demand_opportunity":"मांग / अवसर","reachable_supply":"पहुँच योग्य मौजूदा आपूर्ति","price":"मूल्य / इकाई मूल्य","gap":"अंतर","competition_catchment":"प्रतिस्पर्धा और कैचमेंट","direct_inside":"त्रिज्या के भीतर प्रत्यक्ष OSM उम्मीदवार","indirect_inside":"त्रिज्या के भीतर अप्रत्यक्ष OSM उम्मीदवार","nearest_direct":"निकटतम नामित प्रत्यक्ष उम्मीदवार","nearest_indirect":"निकटतम नामित अप्रत्यक्ष उम्मीदवार","competition_intensity":"प्रतिस्पर्धा घनत्व","planning_radius":"योजना त्रिज्या","discovery_radius":"निकटवर्ती नाम खोज त्रिज्या","nearest_market":"निकटतम बाजार","nearest_institution":"निकटतम संस्था","incumbent_capacity":"मौजूदा क्षमता","customer_segments":"ग्राहक समूह","supplier_plan":"आपूर्तिकर्ता योजना","channels":"बिक्री चैनल","all_direct":"सभी नामित प्रत्यक्ष विकल्प","all_indirect":"सभी नामित अप्रत्यक्ष विकल्प","repair_path":"आर्थिक सुधार मार्ग","suppliers":"आपूर्तिकर्ता","bottleneck":"मौजूदा सेवा बाधा","customers":"ग्राहक","new_flow":"नई सेवा प्राप्त प्रवाह","cannibalized":"मौजूदा प्रवाह से स्थानांतरण","options_tested":"परीक्षित विकल्प","option":"विकल्प","investment":"निवेश","capacity":"क्षमता","role":"भूमिका","other_sectors":"तुलना किए गए अन्य क्षेत्र","computed_swot":"गणना किया गया SWOT","scenario_resilience":"परिदृश्य मजबूती","scenarios":"परिदृश्य","remain_solvent":"भुगतान-सक्षम रहता है","payback36":"36 माह में निवेश वापसी","p10_cash":"10वाँ परसेंटाइल न्यूनतम नकदी","cvar":"सबसे खराब 5% संचयी नकदी (CVaR)","not_run":"नहीं चलाया गया","sensitivity":"संवेदनशीलता टॉर्नेडो","premortem":"प्री-मॉर्टम: क्यों विफल हो सकता है","failure_boundaries":"अनुकूली विफलता सीमाएँ","run_deep":"सीमाएँ निकालने के लिए गहरा विश्लेषण चलाएँ।","scenario_caveat":"परिदृश्य दरें मॉडल-आधारित योजना टिकाऊपन हैं, सफलता की संभावना नहीं। त्रिकोणीय कारक अनुभवजन्य रूप से कैलिब्रेट नहीं हैं।","minimum_setup":"न्यूनतम व्यवहार्य विन्यास","equipment_setup":"उपकरण और स्थापना","working_capital":"कार्यशील पूंजी","monthly_opex":"मासिक स्थिर परिचालन खर्च","people":"लोग","space":"स्थान","service_radius":"सेवा त्रिज्या","capex_allocation":"पूंजीगत खर्च आवंटन","working_cycle":"कार्यशील पूंजी चक्र","minimum_modelled":"मॉडल-आधारित न्यूनतम","buffer15":"अनुशंसित +15% सुरक्षा","inventory_days":"भंडार दिन","receivable_days":"प्राप्य दिन","payable_days":"देय दिन","cash_cycle":"नकदी रूपांतरण चक्र","licences":"सत्यापित किए जाने वाले लाइसेंस","equipment":"उपकरण","quality_controls":"गुणवत्ता नियंत्रण","operational_factors":"परिचालन कारक","weather":"मौसम और मौसमी प्रभाव","insurance":"बीमा / सुरक्षा","customer_plan":"ग्राहक योजना","total_cost":"कुल परियोजना लागत","your_capital":"आपकी अपनी पूंजी","entered_by_you":"आपके द्वारा दर्ज","external_finance":"बाहरी वित्त","illustrative":"उदाहरणात्मक, स्वीकृत नहीं","operating_be":"परिचालन ब्रेक-ईवन","cash_be":"नकदी ब्रेक-ईवन","closing_cash":"समापन नकदी","owner_recovered":"मालिक पूंजी वापस","unit_economics":"इकाई अर्थशास्त्र और निवेश सूचक","gross_margin":"सकल मार्जिन","month12":"माह 12","break_even_volume":"ब्रेक-ईवन मात्रा","planning_units":"योजना आय इकाई/माह","npv":"36 माह का NPV","discount":"12% वार्षिक छूट दर","irr":"वार्षिक IRR","benchmark_assumptions":"बेंचमार्क-समायोजित मान्यताएँ","cash36":"36 माह की समापन नकदी","finance_fit":"संभावित वित्त अनुकूलता","before_starting":"शुरू करने से पहले","week1":"सप्ताह 1","month1":"माह 1","months23":"माह 2–3","months46":"माह 4–6","stop_reconsider":"रोकें / पुनर्विचार करें","decision_chain":"निर्णय श्रृंखला","estimate_class":"अनुमान वर्ग","scope":"दायरा","evidence_limits":"प्रमाण सीमाएँ","source_links":"स्रोत लिंक","operational_weather":"परिचालन और मौसम कारक","operational":"परिचालन","business_guidance":"व्यवसाय-विशिष्ट निर्णय मार्गदर्शन","advantages":"लाभ","disadvantages_risks":"नुकसान और मुख्य जोखिम","osm_context":"OSM प्रतिस्पर्धा और निकटवर्ती संदर्भ","inside_radius":"योजना त्रिज्या के भीतर","outside_radius":"योजना त्रिज्या के बाहर","unnamed":"बेनाम मानचित्र उम्मीदवार","mapped_place":"मानचित्रित स्थान","no_candidate":"सीमित खोज में कोई मानचित्रित उम्मीदवार नहीं मिला। इससे यह सिद्ध नहीं होता कि कोई नहीं है।","no_named":"सीमित खोज में नामित उम्मीदवार नहीं","page":"पृष्ठ","technical_report":"विस्तृत तकनीकी रिपोर्ट","recommendation":"सिफारिश","local_market_evidence":"स्थानीय बाजार और प्रमाण","competition":"प्रतिस्पर्धा और कैचमेंट","business_setup":"व्यवसाय स्थापना","costs":"पूंजीगत खर्च, परिचालन खर्च और कार्यशील पूंजी","finance_cash":"वित्त और 36 माह का नकदी प्रवाह","risk_scenarios":"परिदृश्य विश्लेषण, SWOT और विफलता सीमाएँ","actions":"कार्य योजना","evidence":"प्रमाण, भरोसा और सीमाएँ","variable":"चर","dataset":"डेटासेट","observation":"अवलोकन","freshness":"ताज़गी स्थिति","status":"स्थिति","source":"स्रोत","limitations":"सीमाएँ","sources":"स्रोत","name":"नाम","category":"श्रेणी","distance":"सीधी दूरी","month":"माह","revenue":"आय","operating_cash":"परिचालन नकदी","scheme":"योजना","eligibility":"पात्रता","threshold":"सीमा मान","interpretation":"व्याख्या"
}


_EXACT = {
    "bn": {
        "households":"পরিবার","small retailers":"ক্ষুদ্র খুচরা বিক্রেতা","retailers":"খুচরা বিক্রেতা","restaurants":"রেস্তোরাঁ","institutions":"প্রতিষ্ঠান","suppliers":"সরবরাহকারী","nearby households":"নিকটবর্তী পরিবার","high-frequency buyers":"ঘন ঘন ক্রেতা","price-sensitive households":"দাম-সংবেদনশীল পরিবার","milk producers":"দুধ উৎপাদক","collection centres":"সংগ্রহ কেন্দ্র","cooperatives/processors":"সমবায়/প্রক্রিয়াকারী","door delivery":"বাড়িতে সরবরাহ","retailer/tea-shop supply":"খুচরা বিক্রেতা/চা-দোকানে সরবরাহ","institutional supply":"প্রাতিষ্ঠানিক সরবরাহ","food-grade cans":"খাদ্যমানের ক্যান","weighing/testing kit":"ওজন/পরীক্ষার কিট","insulated transport":"তাপ-নিরোধক পরিবহন","heat stress":"তাপজনিত চাপ","flood/route disruption":"বন্যা/রুট ব্যাঘাত","fuel":"জ্বালানি","inventory":"মজুত","receivables":"পাওনা","route utilization":"রুট ব্যবহার","local trade registration":"স্থানীয় বাণিজ্য নিবন্ধন","food handling compliance":"খাদ্য পরিচালনা নিয়ম","FSSAI registration":"FSSAI নিবন্ধন","GST registration when applicable":"প্রযোজ্য হলে GST নিবন্ধন","TRUE":"হ্যাঁ","FALSE":"না","HIGH":"উচ্চ","MEDIUM":"মাঝারি","LOW":"কম","CURRENT":"বর্তমান","RECENT":"সাম্প্রতিক","HISTORICAL_BASELINE":"ঐতিহাসিক ভিত্তি","PROJECTED":"প্রক্ষেপিত","STALE_FOR_DECISION":"সিদ্ধান্তের জন্য পুরোনো","UNKNOWN":"অজানা","MODERATE_PROXY_DENSITY":"মাঝারি প্রক্সি ঘনত্ব","LOW_PROXY_DENSITY":"কম প্রক্সি ঘনত্ব","HIGH_PROXY_DENSITY":"উচ্চ প্রক্সি ঘনত্ব",
    },
    "hi": {
        "households":"परिवार","small retailers":"छोटे खुदरा विक्रेता","retailers":"खुदरा विक्रेता","restaurants":"रेस्तरां","institutions":"संस्थान","suppliers":"आपूर्तिकर्ता","nearby households":"आसपास के परिवार","high-frequency buyers":"बार-बार खरीदने वाले ग्राहक","price-sensitive households":"मूल्य-संवेदनशील परिवार","milk producers":"दूध उत्पादक","collection centres":"संग्रह केंद्र","cooperatives/processors":"सहकारी/प्रसंस्करणकर्ता","door delivery":"घर तक आपूर्ति","retailer/tea-shop supply":"खुदरा/चाय-दुकान आपूर्ति","institutional supply":"संस्थागत आपूर्ति","food-grade cans":"खाद्य-ग्रेड डिब्बे","weighing/testing kit":"तौल/परीक्षण किट","insulated transport":"तापरोधी परिवहन","heat stress":"गर्मी का दबाव","flood/route disruption":"बाढ़/मार्ग बाधा","fuel":"ईंधन","inventory":"भंडार","receivables":"प्राप्य राशि","route utilization":"मार्ग उपयोग","local trade registration":"स्थानीय व्यापार पंजीकरण","food handling compliance":"खाद्य संचालन अनुपालन","FSSAI registration":"FSSAI पंजीकरण","GST registration when applicable":"लागू होने पर GST पंजीकरण","TRUE":"हाँ","FALSE":"नहीं","HIGH":"उच्च","MEDIUM":"मध्यम","LOW":"कम","CURRENT":"वर्तमान","RECENT":"हालिया","HISTORICAL_BASELINE":"ऐतिहासिक आधार","PROJECTED":"अनुमानित","STALE_FOR_DECISION":"निर्णय के लिए पुराना","UNKNOWN":"अज्ञात","MODERATE_PROXY_DENSITY":"मध्यम प्रॉक्सी घनत्व","LOW_PROXY_DENSITY":"कम प्रॉक्सी घनत्व","HIGH_PROXY_DENSITY":"उच्च प्रॉक्सी घनत्व",
    },
}

_EXACT["bn"].update({
    "small retailers":"ক্ষুদ্র খুচরা বিক্রেতা","producers":"উৎপাদক","institutions and small businesses":"প্রতিষ্ঠান ও ক্ষুদ্র ব্যবসা","regional wholesalers":"আঞ্চলিক পাইকার","producer groups":"উৎপাদক গোষ্ঠী","transport contractors":"পরিবহন ঠিকাদার","fixed retailer route":"নির্দিষ্ট খুচরা বিক্রেতা রুট","aggregator service":"সংগ্রাহক পরিষেবা","institutional delivery":"প্রাতিষ্ঠানিক সরবরাহ","PRIMARY":"প্রধান","SECONDARY":"সহায়ক","LOW_ASSUMPTION_BASED":"কম আস্থা; অনুমানভিত্তিক","road access":"সড়ক যোগাযোগ","vehicle efficiency":"যানের দক্ষতা","load factor":"বোঝাইয়ের হার","empty return":"খালি ফেরত","downtime":"অচল সময়","heavy rain/flood route disruption":"ভারী বৃষ্টি/বন্যায় রুট ব্যাঘাত","commercial vehicle and goods-in-transit protection":"বাণিজ্যিক যান ও পরিবহনাধীন পণ্যের সুরক্ষা","rented/shared vehicle access":"ভাড়া/ভাগ করা যান ব্যবহারের সুযোগ","handling crates":"পণ্য ওঠানামার ক্রেট","route/phone tools":"রুট/ফোন সরঞ্জাম","trip sheet":"যাত্রা নথি","load-factor log":"বোঝাই হারের নথি","fuel and maintenance log":"জ্বালানি ও রক্ষণাবেক্ষণ নথি","commercial vehicle and trade compliance as applicable":"প্রযোজ্য বাণিজ্যিক যান ও ব্যবসায়িক নিয়ম মানা","STRENGTHS":"শক্তি","WEAKNESSES":"দুর্বলতা","OPPORTUNITIES":"সুযোগ","THREATS":"হুমকি","CONDITIONAL":"শর্তসাপেক্ষ","VILLAGE":"গ্রাম","TOWN":"শহর/পৌরসভা","WARD":"ওয়ার্ড",
    "Validate current customer prices and negotiate supplier terms first.":"বর্তমান ক্রেতামূল্য যাচাই করুন এবং আগে সরবরাহকারীর শর্ত নিয়ে আলোচনা করুন।","Obtain two supplier quotes and cap procurement cost per unit.":"দুই সরবরাহকারীর দর নিন এবং প্রতি এককের ক্রয়খরচের সীমা ঠিক করুন।","Avoid a long lease until three months of demand are demonstrated.":"তিন মাসের চাহিদা প্রমাণিত না হওয়া পর্যন্ত দীর্ঘমেয়াদি ভাড়া এড়ান।","Customer acquisition was slower because nearby alternatives existed.":"নিকটবর্তী বিকল্প থাকায় ক্রেতা সংগ্রহ ধীর হয়েছে।","Interview customers and differentiate channel/service before launch.":"শুরুর আগে ক্রেতাদের সাক্ষাৎকার নিন এবং চ্যানেল/পরিষেবায় পার্থক্য আনুন।","The regional benchmark did not translate into real locality sales.":"আঞ্চলিক বেঞ্চমার্ক বাস্তব স্থানীয় বিক্রয়ে রূপ নেয়নি।","Demand is modelled from a regional survey prior, not transaction data.":"চাহিদা আঞ্চলিক সমীক্ষার পূর্বধারণা থেকে মডেল করা, লেনদেনের তথ্য নয়।","Run a small paid pilot and replace the benchmark with observed sales.":"ছোট অর্থপ্রদত্ত পাইলট চালান এবং বেঞ্চমার্কের বদলে পর্যবেক্ষিত বিক্রয় ব্যবহার করুন।","Validate at least two current supplier quotations and one customer selling price.":"অন্তত দুইটি বর্তমান সরবরাহকারীর দর ও একটি ক্রেতা বিক্রয়দর যাচাই করুন।","Confirm premises, power/water/internet needs and every listed licence with authority.":"জায়গা, বিদ্যুৎ/জল/ইন্টারনেটের প্রয়োজন এবং প্রতিটি তালিকাভুক্ত লাইসেন্স কর্তৃপক্ষের সঙ্গে নিশ্চিত করুন।","Interview at least ten target customers and record purchase frequency and price.":"অন্তত দশজন লক্ষ্য ক্রেতার সাক্ষাৎকার নিন এবং ক্রয়ের ঘনত্ব ও দাম লিখুন।","Run a paid micro-pilot before buying the full equipment configuration.":"সম্পূর্ণ যন্ত্রপাতি কেনার আগে অর্থপ্রদত্ত ক্ষুদ্র পাইলট চালান।","Track daily sales, contribution margin, inventory days, cash and rejected/wasted stock.":"দৈনিক বিক্রয়, অবদান মার্জিন, মজুতের দিন, নগদ এবং বাতিল/নষ্ট মজুত নথিবদ্ধ করুন।","Reconcile supplier invoices and customer receipts weekly.":"সরবরাহকারীর চালান ও ক্রেতার রসিদ প্রতি সপ্তাহে মিলিয়ে নিন।","Continue only if contribution margin and closing cash remain non-negative.":"অবদান মার্জিন ও সমাপনী নগদ ঋণাত্মক না থাকলেই চালিয়ে যান।","Add the secondary channel only after the primary channel repeats reliably.":"প্রধান চ্যানেল নির্ভরযোগ্যভাবে পুনরাবৃত্ত হলে তবেই সহায়ক চ্যানেল যোগ করুন।","Compare realized sales with the model interval and recalibrate before expansion.":"বাস্তব বিক্রয় মডেলের সীমার সঙ্গে তুলনা করুন এবং সম্প্রসারণের আগে পুনঃক্যালিব্রেট করুন।","Build at least two active suppliers and avoid single-buyer dependence.":"অন্তত দুইজন সক্রিয় সরবরাহকারী গড়ুন এবং একক ক্রেতা নির্ভরতা এড়ান।","Use the tested demand-deterioration statement as the sales stop rule.":"পরীক্ষিত চাহিদা-অবনতি বিবৃতিকে বিক্রয় বন্ধের নিয়ম হিসেবে ব্যবহার করুন।","Scheme category screening is current; actual rate, sanction and lender underwriting still require a lender quote.":"প্রকল্প-শ্রেণি যাচাই বর্তমান; প্রকৃত হার, অনুমোদন ও ঋণদাতার মূল্যায়নের জন্য এখনও ঋণদাতার লিখিত দর প্রয়োজন।","OSM POIs are volunteered proxy evidence and may be incomplete.":"OSM-এর স্থানবিন্দু স্বেচ্ছায় দেওয়া প্রক্সি প্রমাণ এবং অসম্পূর্ণ হতে পারে।",
})

_EXACT["hi"].update({
    "small retailers":"छोटे खुदरा विक्रेता","producers":"उत्पादक","institutions and small businesses":"संस्थान और छोटे व्यवसाय","regional wholesalers":"क्षेत्रीय थोक विक्रेता","producer groups":"उत्पादक समूह","transport contractors":"परिवहन ठेकेदार","fixed retailer route":"निश्चित खुदरा मार्ग","aggregator service":"एकत्रीकरण सेवा","institutional delivery":"संस्थागत आपूर्ति","PRIMARY":"प्रमुख","SECONDARY":"सहायक","LOW_ASSUMPTION_BASED":"कम भरोसा; मान्यता-आधारित","road access":"सड़क पहुँच","vehicle efficiency":"वाहन दक्षता","load factor":"भार उपयोग","empty return":"खाली वापसी","downtime":"बंद समय","heavy rain/flood route disruption":"तेज बारिश/बाढ़ से मार्ग बाधा","commercial vehicle and goods-in-transit protection":"वाणिज्यिक वाहन और परिवहनाधीन सामान सुरक्षा","rented/shared vehicle access":"किराए/साझा वाहन की पहुँच","handling crates":"सामान संभालने के क्रेट","route/phone tools":"मार्ग/फोन उपकरण","trip sheet":"यात्रा पत्रक","load-factor log":"भार उपयोग रजिस्टर","fuel and maintenance log":"ईंधन और रखरखाव रजिस्टर","commercial vehicle and trade compliance as applicable":"लागू वाणिज्यिक वाहन और व्यापार अनुपालन","STRENGTHS":"ताकत","WEAKNESSES":"कमजोरियाँ","OPPORTUNITIES":"अवसर","THREATS":"खतरे","CONDITIONAL":"सशर्त","VILLAGE":"गाँव","TOWN":"शहर/नगरपालिका","WARD":"वार्ड",
    "Validate current customer prices and negotiate supplier terms first.":"वर्तमान ग्राहक मूल्य जाँचें और पहले आपूर्तिकर्ता शर्तों पर बातचीत करें।","Obtain two supplier quotes and cap procurement cost per unit.":"दो आपूर्तिकर्ता कोटेशन लें और प्रति इकाई खरीद लागत की सीमा तय करें।","Avoid a long lease until three months of demand are demonstrated.":"तीन माह की मांग सिद्ध होने तक लंबी लीज से बचें।","Customer acquisition was slower because nearby alternatives existed.":"आसपास विकल्प होने से ग्राहक प्राप्ति धीमी रही।","Interview customers and differentiate channel/service before launch.":"शुरू करने से पहले ग्राहकों से बात करें और चैनल/सेवा में अंतर बनाएँ।","The regional benchmark did not translate into real locality sales.":"क्षेत्रीय बेंचमार्क वास्तविक स्थानीय बिक्री में नहीं बदला।","Demand is modelled from a regional survey prior, not transaction data.":"मांग क्षेत्रीय सर्वेक्षण पूर्वमान से मॉडल की गई है, लेनदेन डेटा से नहीं।","Run a small paid pilot and replace the benchmark with observed sales.":"छोटा भुगतान वाला पायलट चलाएँ और बेंचमार्क को देखी गई बिक्री से बदलें।","Validate at least two current supplier quotations and one customer selling price.":"कम से कम दो वर्तमान आपूर्तिकर्ता कोटेशन और एक ग्राहक बिक्री मूल्य जाँचें।","Confirm premises, power/water/internet needs and every listed licence with authority.":"स्थान, बिजली/पानी/इंटरनेट जरूरत और हर सूचीबद्ध लाइसेंस को प्राधिकरण से पुष्टि करें।","Interview at least ten target customers and record purchase frequency and price.":"कम से कम दस लक्षित ग्राहकों से बात करें और खरीद आवृत्ति व मूल्य लिखें।","Run a paid micro-pilot before buying the full equipment configuration.":"पूरा उपकरण विन्यास खरीदने से पहले भुगतान वाला छोटा पायलट चलाएँ।","Track daily sales, contribution margin, inventory days, cash and rejected/wasted stock.":"दैनिक बिक्री, योगदान मार्जिन, भंडार दिन, नकदी और अस्वीकृत/बर्बाद स्टॉक दर्ज करें।","Reconcile supplier invoices and customer receipts weekly.":"आपूर्तिकर्ता चालान और ग्राहक रसीदें हर सप्ताह मिलाएँ।","Continue only if contribution margin and closing cash remain non-negative.":"योगदान मार्जिन और समापन नकदी गैर-ऋणात्मक रहें तभी जारी रखें।","Add the secondary channel only after the primary channel repeats reliably.":"प्रमुख चैनल विश्वसनीय रूप से दोहरने के बाद ही सहायक चैनल जोड़ें।","Compare realized sales with the model interval and recalibrate before expansion.":"वास्तविक बिक्री की मॉडल सीमा से तुलना करें और विस्तार से पहले पुनः कैलिब्रेट करें।","Build at least two active suppliers and avoid single-buyer dependence.":"कम से कम दो सक्रिय आपूर्तिकर्ता बनाएँ और एक खरीदार पर निर्भरता से बचें।","Use the tested demand-deterioration statement as the sales stop rule.":"परीक्षित मांग-गिरावट कथन को बिक्री रोक नियम बनाएँ।","Scheme category screening is current; actual rate, sanction and lender underwriting still require a lender quote.":"योजना-श्रेणी जाँच वर्तमान है; वास्तविक दर, स्वीकृति और ऋणदाता मूल्यांकन के लिए अभी भी ऋणदाता का लिखित कोटेशन चाहिए।","OSM POIs are volunteered proxy evidence and may be incomplete.":"OSM स्थान-बिंदु स्वैच्छिक प्रॉक्सी प्रमाण हैं और अधूरे हो सकते हैं।",
})

_EXACT["bn"].update({
    "illustrative eligibility screening; not lender approval": "উদাহরণমূলক যোগ্যতা যাচাই; ঋণদাতার অনুমোদন নয়",
    "current rule-window eligibility screening through 2026-09-30; not lender approval or confirmation that the application window is accepting submissions": "২০২৬-০৯-৩০ পর্যন্ত বর্তমান নিয়ম-সময়ের যোগ্যতা যাচাই; ঋণদাতার অনুমোদন বা আবেদন গ্রহণ চলছে—এমন নিশ্চয়তা নয়",
})

_EXACT["hi"].update({
    "illustrative eligibility screening; not lender approval": "उदाहरणात्मक पात्रता जाँच; ऋणदाता स्वीकृति नहीं",
    "current rule-window eligibility screening through 2026-09-30; not lender approval or confirmation that the application window is accepting submissions": "2026-09-30 तक वर्तमान नियम-अवधि पात्रता जाँच; ऋणदाता स्वीकृति या आवेदन स्वीकार किए जाने की पुष्टि नहीं",
})

_EXACT["bn"].update({
    "Selling Price": "বিক্রয়দর",
    "selling price": "বিক্রয়দর",
    "selling_price": "বিক্রয়দর",
    "selling_price_factor": "বিক্রয়দরের গুণক",
    "variable cost": "পরিবর্তনশীল খরচ",
    "variable_cost": "পরিবর্তনশীল খরচ",
    "variable_cost_factor": "পরিবর্তনশীল খরচের গুণক",
    "fixed opex": "স্থির পরিচালন ব্যয়",
    "fixed_opex": "স্থির পরিচালন ব্যয়",
    "fixed_opex_factor": "স্থির পরিচালন ব্যয়ের গুণক",
    "monthly_demand": "মাসিক চাহিদা",
    "minimum_cash_buffer": "ন্যূনতম নগদ সুরক্ষা",
    "planning revenue units/month": "পরিকল্পিত আয় একক/মাস",
    "share of central planning price": "কেন্দ্রীয় পরিকল্পিত দামের অংশ",
    "multiple of central variable cost": "কেন্দ্রীয় পরিবর্তনশীল খরচের গুণিতক",
    "multiple of central fixed OPEX": "কেন্দ্রীয় স্থির পরিচালন ব্যয়ের গুণিতক",
    "INR opening cash after startup investment": "প্রারম্ভিক বিনিয়োগের পর উদ্বোধনী নগদ (INR)",
    "No cash failure up to 100% demand deterioration.": "চাহিদা ১০০% কমার পরীক্ষিত সীমা পর্যন্ত নগদ ব্যর্থতা মেলেনি।",
    "No cash failure up to 100% selling price deterioration.": "বিক্রয়দর ১০০% কমার পরীক্ষিত সীমা পর্যন্ত নগদ ব্যর্থতা মেলেনি।",
    "No cash failure up to 900% fixed OPEX increase.": "স্থির পরিচালন ব্যয় ৯০০% বাড়ার পরীক্ষিত সীমা পর্যন্ত নগদ ব্যর্থতা মেলেনি।",
    "Approximately INR 0 opening cash is required to remain non-negative in the central 36-month model.": "কেন্দ্রীয় ৩৬ মাসের মডেলে নগদ ঋণাত্মক না রাখতে আনুমানিক INR 0 উদ্বোধনী নগদ প্রয়োজন।",
    "OSM candidates are deduplicated direct/indirect proxies; capacity, sales and market shares remain unknown, so HHI is not calculated.": "OSM প্রার্থীগুলি পুনরাবৃত্তি-মুক্ত সরাসরি/পরোক্ষ প্রক্সি; ক্ষমতা, বিক্রয় ও বাজার অংশ অজানা, তাই HHI হিসাব করা হয়নি।",
    "Segments are defensible sector groups, not measured local percentage shares.": "গোষ্ঠীগুলি যুক্তিসঙ্গত খাতভিত্তিক শ্রেণি; মাপা স্থানীয় শতাংশ অংশ নয়।",
    "Potentially eligible / illustrative structure; not lender approval.": "সম্ভাব্য যোগ্য / উদাহরণমূলক কাঠামো; ঋণদাতার অনুমোদন নয়।",
    "Project cost and requested finance are not yet established.": "প্রকল্প ব্যয় ও অনুরোধকৃত অর্থায়ন এখনও নিশ্চিত নয়।",
    "The result is conditional on the supplied evidence and assumptions.": "ফলাফল সরবরাহকৃত প্রমাণ ও অনুমানের শর্তসাপেক্ষ।",
    "NPV/IRR are planning outputs from benchmark-adjusted assumptions, not investment guarantees.": "NPV/IRR বেঞ্চমার্ক-সমন্বিত অনুমান থেকে পরিকল্পনার ফল; বিনিয়োগের নিশ্চয়তা নয়।",
    "Travel time is an estimate from OSM road class/default speeds; it is not observed traffic time.": "যাত্রার সময় OSM সড়কশ্রেণি/ডিফল্ট গতির অনুমান; পর্যবেক্ষিত যানচলাচলের সময় নয়।",
    "Adverse selling price moved cash below plan.": "প্রতিকূল বিক্রয়দর নগদকে পরিকল্পনার নিচে নামিয়েছে।",
    "Adverse variable cost moved cash below plan.": "প্রতিকূল পরিবর্তনশীল খরচ নগদকে পরিকল্পনার নিচে নামিয়েছে।",
    "Adverse fixed opex moved cash below plan.": "প্রতিকূল স্থির পরিচালন ব্যয় নগদকে পরিকল্পনার নিচে নামিয়েছে।",
})

_EXACT["hi"].update({
    "Selling Price": "बिक्री मूल्य",
    "selling price": "बिक्री मूल्य",
    "selling_price": "बिक्री मूल्य",
    "selling_price_factor": "बिक्री मूल्य गुणक",
    "variable cost": "परिवर्ती लागत",
    "variable_cost": "परिवर्ती लागत",
    "variable_cost_factor": "परिवर्ती लागत गुणक",
    "fixed opex": "स्थिर परिचालन व्यय",
    "fixed_opex": "स्थिर परिचालन व्यय",
    "fixed_opex_factor": "स्थिर परिचालन व्यय गुणक",
    "monthly_demand": "मासिक मांग",
    "minimum_cash_buffer": "न्यूनतम नकदी सुरक्षा",
    "planning revenue units/month": "योजना आय इकाई/माह",
    "share of central planning price": "केंद्रीय योजना मूल्य का हिस्सा",
    "multiple of central variable cost": "केंद्रीय परिवर्ती लागत का गुणक",
    "multiple of central fixed OPEX": "केंद्रीय स्थिर परिचालन व्यय का गुणक",
    "INR opening cash after startup investment": "प्रारंभिक निवेश के बाद आरंभिक नकदी (INR)",
    "No cash failure up to 100% demand deterioration.": "मांग में 100% गिरावट की परीक्षण सीमा तक नकदी विफलता नहीं मिली।",
    "No cash failure up to 100% selling price deterioration.": "बिक्री मूल्य में 100% गिरावट की परीक्षण सीमा तक नकदी विफलता नहीं मिली।",
    "No cash failure up to 900% fixed OPEX increase.": "स्थिर परिचालन व्यय में 900% वृद्धि की परीक्षण सीमा तक नकदी विफलता नहीं मिली।",
    "Approximately INR 0 opening cash is required to remain non-negative in the central 36-month model.": "केंद्रीय 36 माह के मॉडल में नकदी गैर-ऋणात्मक रखने के लिए लगभग INR 0 आरंभिक नकदी चाहिए।",
    "OSM candidates are deduplicated direct/indirect proxies; capacity, sales and market shares remain unknown, so HHI is not calculated.": "OSM उम्मीदवार दोहराव-मुक्त प्रत्यक्ष/अप्रत्यक्ष प्रॉक्सी हैं; क्षमता, बिक्री और बाजार हिस्सेदारी अज्ञात हैं, इसलिए HHI की गणना नहीं हुई।",
    "Segments are defensible sector groups, not measured local percentage shares.": "खंड उचित क्षेत्र-आधारित समूह हैं; मापे गए स्थानीय प्रतिशत हिस्से नहीं।",
    "Potentially eligible / illustrative structure; not lender approval.": "संभावित रूप से पात्र / उदाहरणात्मक संरचना; ऋणदाता स्वीकृति नहीं।",
    "Project cost and requested finance are not yet established.": "परियोजना लागत और मांगा गया वित्त अभी स्थापित नहीं है।",
    "The result is conditional on the supplied evidence and assumptions.": "परिणाम दिए गए प्रमाण और मान्यताओं पर सशर्त है।",
    "NPV/IRR are planning outputs from benchmark-adjusted assumptions, not investment guarantees.": "NPV/IRR बेंचमार्क-समायोजित मान्यताओं से योजना परिणाम हैं; निवेश की गारंटी नहीं।",
    "Travel time is an estimate from OSM road class/default speeds; it is not observed traffic time.": "यात्रा समय OSM सड़क-वर्ग/डिफॉल्ट गति से अनुमानित है; यह देखा गया यातायात समय नहीं।",
    "Adverse selling price moved cash below plan.": "प्रतिकूल बिक्री मूल्य ने नकदी को योजना से नीचे किया।",
    "Adverse variable cost moved cash below plan.": "प्रतिकूल परिवर्ती लागत ने नकदी को योजना से नीचे किया।",
    "Adverse fixed opex moved cash below plan.": "प्रतिकूल स्थिर परिचालन व्यय ने नकदी को योजना से नीचे किया।",
})


_DYNAMIC = {
    "bn": [
        (r"Selling Price is the strongest tested cash driver \(elasticity ([^\)]+)\)\.", r"বিক্রয়দর সবচেয়ে শক্তিশালী পরীক্ষিত নগদ চালক (স্থিতিস্থাপকতা \1)।"),
        (r"The modelled cash-conversion cycle is short at ([0-9.]+) days\.", r"মডেলভিত্তিক নগদ-রূপান্তর চক্রটি সংক্ষিপ্ত: \1 দিন।"),
        (r"Month-12 operating cash flow is positive in the central model\.", "কেন্দ্রীয় মডেলে ১২তম মাসের পরিচালন নগদ প্রবাহ ধনাত্মক।"),
        (r"Local demand is a regional benchmark, not observed locality sales\.", "স্থানীয় চাহিদা একটি আঞ্চলিক বেঞ্চমার্ক; পর্যবেক্ষিত স্থানীয় বিক্রয় নয়।"),
        (r"The planning graph contains ([0-9.]+) units of unserved flow\.", r"পরিকল্পনা গ্রাফে \1 একক অপরিসেবিত প্রবাহ রয়েছে।"),
        (r"A secondary aggregator service channel can diversify the primary route\.", "সহায়ক সংগ্রাহক পরিষেবা চ্যানেল প্রধান রুটকে বৈচিত্র্যময় করতে পারে।"),
        (r"A secondary (.+) channel can diversify the primary route\.", r"সহায়ক \1 চ্যানেল প্রধান রুটকে বৈচিত্র্যময় করতে পারে।"),
        (r"([0-9]+) marginal capacity repair options were evaluated\.", r"\1টি প্রান্তিক ক্ষমতা-মেরামত বিকল্প মূল্যায়ন করা হয়েছে।"),
        (r"(.+) is the strongest tested cash driver \(elasticity ([^\)]+)\)\.", r"\1 সবচেয়ে শক্তিশালী পরীক্ষিত নগদ চালক (স্থিতিস্থাপকতা \2)।"),
        (r"Competitor capacity and market shares remain unknown\.", "প্রতিযোগীর ক্ষমতা ও বাজার অংশ অজানা।"),
        (r"Adverse (.+) moved cash below plan\.", r"প্রতিকূল \1 নগদকে পরিকল্পনার নিচে নামিয়েছে।"),
        (r"Controlled \+/-([0-9]+)% perturbation; elasticity ([^\.]+)\.", r"নিয়ন্ত্রিত ±\1% পরিবর্তন; স্থিতিস্থাপকতা \2।"),
        (r"([0-9]+) direct OSM proxy candidates in the catchment; capacity remains unknown\.", r"ক্যাচমেন্টে \1টি সরাসরি OSM প্রক্সি প্রার্থী; ক্ষমতা অজানা।"),
        (r"Ring-fence at least INR ([0-9,]+) as working capital\.", r"কার্যকরী মূলধন হিসেবে অন্তত INR \1 আলাদা রাখুন।"),
        (r"Stage 0: validate prices, suppliers and paid demand using shared/rented assets\.", "ধাপ ০: ভাগ করা/ভাড়া সম্পদ দিয়ে দাম, সরবরাহকারী ও অর্থপ্রদত্ত চাহিদা যাচাই করুন।"),
        (r"Stage 1: deploy the selected configuration and preserve INR ([0-9,]+) reserve\.", r"ধাপ ১: নির্বাচিত বিন্যাস চালু করুন এবং INR \1 সংরক্ষণ রাখুন।"),
        (r"Stage 2: the central model first supports a 70% utilization plus reserve trigger in month ([0-9]+)\.", r"ধাপ ২: কেন্দ্রীয় মডেল প্রথম \1তম মাসে ৭০% ব্যবহার ও সংরক্ষণ ট্রিগার সমর্থন করে।"),
        (r"Stop-rule context: No cash failure up to 100% demand deterioration\.", "বন্ধের নিয়মের প্রেক্ষিত: চাহিদা ১০০% কমার পরীক্ষিত সীমা পর্যন্ত নগদ ব্যর্থতা মেলেনি।"),
        (r"Plan becomes cash-negative above approximately ([0-9.]+)x central variable cost\.", r"কেন্দ্রীয় পরিবর্তনশীল খরচ আনুমানিক \1 গুণের বেশি হলে পরিকল্পনার নগদ ঋণাত্মক হয়।"),
        (r"Approximately INR ([0-9,]+) opening cash is required to remain non-negative in the central 36-month model\.", r"কেন্দ্রীয় ৩৬ মাসের মডেলে নগদ ঋণাত্মক না রাখতে আনুমানিক INR \1 উদ্বোধনী নগদ প্রয়োজন।"),
    ],
    "hi": [
        (r"Selling Price is the strongest tested cash driver \(elasticity ([^\)]+)\)\.", r"बिक्री मूल्य सबसे मजबूत परीक्षण किया गया नकदी चालक है (लोच \1)।"),
        (r"The modelled cash-conversion cycle is short at ([0-9.]+) days\.", r"मॉडल-आधारित नकदी-रूपांतरण चक्र छोटा है: \1 दिन।"),
        (r"Month-12 operating cash flow is positive in the central model\.", "केंद्रीय मॉडल में माह 12 का परिचालन नकदी प्रवाह सकारात्मक है।"),
        (r"Local demand is a regional benchmark, not observed locality sales\.", "स्थानीय मांग क्षेत्रीय बेंचमार्क है; देखी गई स्थानीय बिक्री नहीं।"),
        (r"The planning graph contains ([0-9.]+) units of unserved flow\.", r"योजना ग्राफ में \1 इकाई असेवित प्रवाह है।"),
        (r"A secondary aggregator service channel can diversify the primary route\.", "सहायक एकत्रीकरण सेवा चैनल प्रमुख मार्ग में विविधता ला सकता है।"),
        (r"A secondary (.+) channel can diversify the primary route\.", r"सहायक \1 चैनल प्रमुख मार्ग में विविधता ला सकता है।"),
        (r"([0-9]+) marginal capacity repair options were evaluated\.", r"\1 सीमांत क्षमता-सुधार विकल्प का मूल्यांकन हुआ।"),
        (r"(.+) is the strongest tested cash driver \(elasticity ([^\)]+)\)\.", r"\1 सबसे मजबूत परीक्षण किया गया नकदी चालक है (लोच \2)।"),
        (r"Competitor capacity and market shares remain unknown\.", "प्रतिस्पर्धी क्षमता और बाजार हिस्सेदारी अज्ञात हैं।"),
        (r"Adverse (.+) moved cash below plan\.", r"प्रतिकूल \1 ने नकदी को योजना से नीचे किया।"),
        (r"Controlled \+/-([0-9]+)% perturbation; elasticity ([^\.]+)\.", r"नियंत्रित ±\1% परिवर्तन; लोच \2।"),
        (r"([0-9]+) direct OSM proxy candidates in the catchment; capacity remains unknown\.", r"कैचमेंट में \1 प्रत्यक्ष OSM प्रॉक्सी उम्मीदवार; क्षमता अज्ञात।"),
        (r"Ring-fence at least INR ([0-9,]+) as working capital\.", r"कार्यशील पूंजी के रूप में कम से कम INR \1 अलग रखें।"),
        (r"Stage 0: validate prices, suppliers and paid demand using shared/rented assets\.", "चरण 0: साझा/किराए के साधनों से मूल्य, आपूर्तिकर्ता और भुगतान वाली मांग जाँचें।"),
        (r"Stage 1: deploy the selected configuration and preserve INR ([0-9,]+) reserve\.", r"चरण 1: चुना विन्यास लागू करें और INR \1 आरक्षित रखें।"),
        (r"Stage 2: the central model first supports a 70% utilization plus reserve trigger in month ([0-9]+)\.", r"चरण 2: केंद्रीय मॉडल पहली बार माह \1 में 70% उपयोग और आरक्षित ट्रिगर का समर्थन करता है।"),
        (r"Stop-rule context: No cash failure up to 100% demand deterioration\.", "रोक नियम संदर्भ: मांग में 100% गिरावट की परीक्षण सीमा तक नकदी विफलता नहीं मिली।"),
        (r"Plan becomes cash-negative above approximately ([0-9.]+)x central variable cost\.", r"केंद्रीय परिवर्ती लागत लगभग \1 गुना से अधिक होने पर योजना की नकदी ऋणात्मक हो जाती है।"),
        (r"Approximately INR ([0-9,]+) opening cash is required to remain non-negative in the central 36-month model\.", r"केंद्रीय 36 माह के मॉडल में नकदी गैर-ऋणात्मक रखने के लिए लगभग INR \1 आरंभिक नकदी चाहिए।"),
    ],
}


def translate_detail_text(value: str, language: str) -> str:
    if language == "en" or not value:
        return value
    text = str(value)
    if text.startswith(("http://", "https://")):
        return text
    exact = _EXACT[language]
    if text in exact:
        return exact[text]
    upper = text.upper()
    if upper in exact:
        return exact[upper]
    for pattern, replacement in _DYNAMIC[language]:
        if re.fullmatch(pattern, text):
            return re.sub(pattern, replacement, text)
    # Preserve proper names and machine identifiers, but localize the recurring
    # scientific-honesty vocabulary used by generated explanations.
    replacements = {
        "bn": {
            "modelled":"মডেলভিত্তিক","planning":"পরিকল্পনা","current":"বর্তমান","historical":"ঐতিহাসিক",
            "estimated":"অনুমিত","projected":"প্রক্ষেপিত","evidence":"প্রমাণ","demand":"চাহিদা","supply":"সরবরাহ",
            "price":"দাম","cost":"খরচ","cash":"নগদ","revenue":"আয়","capacity":"ক্ষমতা","market":"বাজার",
            "competitor":"প্রতিযোগী","customer":"ক্রেতা","supplier":"সরবরাহকারী","risk":"ঝুঁকি","unknown":"অজানা",
            "not calculated":"হিসাব করা হয়নি","not available":"তথ্য নেই","not observed":"প্রত্যক্ষ পর্যবেক্ষণ নয়",
            "not measured":"মাপা নয়","not lender approval":"ঋণদাতার অনুমোদন নয়","must be verified":"যাচাই করতে হবে",
            "within the catchment":"ক্যাচমেন্টের মধ্যে","before launch":"শুরু করার আগে","before spending":"অর্থ ব্যয়ের আগে",
        },
        "hi": {
            "modelled":"मॉडल-आधारित","planning":"योजना","current":"वर्तमान","historical":"ऐतिहासिक",
            "estimated":"अनुमानित","projected":"प्रक्षेपित","evidence":"प्रमाण","demand":"मांग","supply":"आपूर्ति",
            "price":"मूल्य","cost":"लागत","cash":"नकदी","revenue":"आय","capacity":"क्षमता","market":"बाजार",
            "competitor":"प्रतिस्पर्धी","customer":"ग्राहक","supplier":"आपूर्तिकर्ता","risk":"जोखिम","unknown":"अज्ञात",
            "not calculated":"गणना नहीं की गई","not available":"जानकारी उपलब्ध नहीं","not observed":"प्रत्यक्ष अवलोकन नहीं",
            "not measured":"मापा नहीं गया","not lender approval":"ऋणदाता स्वीकृति नहीं","must be verified":"सत्यापित करना होगा",
            "within the catchment":"कैचमेंट के भीतर","before launch":"शुरू करने से पहले","before spending":"खर्च से पहले",
        },
    }[language]
    rendered = text
    for source, target in sorted(replacements.items(), key=lambda item: -len(item[0])):
        rendered = rendered.replace(source, target).replace(source.capitalize(), target)
    return rendered


def build_translation_map(values: list[str], language: str) -> dict[str, str]:
    return {value: translate_detail_text(value, language) for value in values if value}

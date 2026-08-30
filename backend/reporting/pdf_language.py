"""Human-reviewed PDF-only language corrections.

The website presentation dictionaries remain untouched.  This module prevents
the PDF renderer from producing hybrid Bengali/English fragments when an exact
domain phrase is available and preserves canonical identifiers and place names.
"""

from __future__ import annotations

# ruff: noqa: E501 - exact source phrases remain intact for deterministic lookup.
import re

from backend.presentation.detail_language import translate_detail_text

BENGALI_PDF_EXACT = {
    # Evidence status and technical metrics.
    "MEDIUM": "মাঝারি",
    "HISTORICAL_BASELINE": "ঐতিহাসিক ভিত্তি",
    "STALE_FOR_DECISION": "সিদ্ধান্তে ব্যবহারের জন্য পুরোনো",
    "Operating margin": "পরিচালন মুনাফার হার",
    "Contribution margin per unit": "প্রতি এককে অবদান মার্জিন",
    "Equipment And Fixtures": "যন্ত্রপাতি ও স্থায়ী সরঞ্জাম",
    "Installation And Setup": "স্থাপন ও প্রস্তুতি",
    "Premises Deposit And Basic Fitout": "জায়গার জামানত ও প্রাথমিক সাজসজ্জা",
    "Licensing And Contingency": "লাইসেন্স ও আপৎকালীন সংস্থান",
    "DELIVERY": "সরবরাহ",
    "DISTRIBUTION": "বিতরণ",
    "AGGREGATION": "সংগ্রহ ও সমন্বয়",
    "PROCESSING": "প্রক্রিয়াকরণ",
    "STORAGE": "সংরক্ষণ",
    "RETAIL": "খুচরা বিক্রয়",
    "TRANSPORT": "পরিবহন",
    "REPAIR": "মেরামত",
    "NO_OSM_DIRECT_CANDIDATE_FOUND": "সরাসরি OSM প্রার্থী পাওয়া যায়নি",
    "BLOCK_SIBLING_MEDIAN_PROXY": "একই ব্লকের অন্যান্য এলাকার মধ্যম মানভিত্তিক প্রক্সি",
    "OSM_PLACE_PROXY": "OSM স্থানভিত্তিক প্রক্সি",
    "OSM_DISTRICT_REPRESENTATIVE_POINT_PROXY": "OSM জেলা-প্রতিনিধি বিন্দুভিত্তিক প্রক্সি",
    "OFFICIAL_BSK_LOCALITY_SERVICE_CENTRE_PROXY": "সরকারি BSK স্থানীয় পরিষেবাকেন্দ্রভিত্তিক প্রক্সি",
    "OSM candidates are deduplicated direct/indirect proxies; capacity, sales and market shares remain unknown, so HHI is not calculated.": (
        "OSM প্রার্থীর পুনরাবৃত্তি বাদ দিয়ে সরাসরি ও পরোক্ষ প্রক্সি হিসেবে গণনা করা হয়েছে। "
        "তাদের সক্ষমতা, বিক্রয় ও বাজারের অংশ অজানা; তাই HHI গণনা করা হয়নি।"
    ),
    "প্রমাণের আস্থা MEDIUM। ঐতিহাসিক, অনুমিত ও বর্তমান প্রমাণ প্রযুক্তিগত প্রতিবেদনে আলাদাভাবে চিহ্নিত।": (
        "প্রমাণের আস্থা মাঝারি। ঐতিহাসিক, অনুমিত ও বর্তমান প্রমাণ প্রযুক্তিগত প্রতিবেদনে আলাদাভাবে চিহ্নিত।"
    ),
    # The four evidence limitations called out in the acceptance screenshot.
    "Current farmgate, procurement, wholesale and retail prices are not linked at this locality. The cash model uses an ASUSE enterprise-margin benchmark; validate current prices before spending.": (
        "এই এলাকার বর্তমান খামারদর, সংগ্রহমূল্য, পাইকারি ও খুচরা বাজারদর সংযুক্ত নেই। "
        "নগদ প্রবাহের মডেলে ASUSE-ভিত্তিক উদ্যোগের মার্জিন বেঞ্চমার্ক ব্যবহার করা হয়েছে; "
        "অর্থ ব্যয়ের আগে বর্তমান বাজারদর যাচাই করুন।"
    ),
    "Current route cost, travel time and chilling availability are unknown; validate the selected route and spoilage controls in a paid pilot.": (
        "বর্তমান পরিবহন ব্যয়, যাত্রাসময় ও শীতলীকরণ-সুবিধার তথ্য অজানা; নির্বাচিত পথে "
        "অর্থপ্রদত্ত পরীক্ষামূলক কার্যক্রম চালিয়ে যাত্রাপথ ও পণ্য নষ্ট হওয়া রোধের ব্যবস্থা যাচাই করুন।"
    ),
    "Current PMMY category screening is available, but lender-specific verified interest/tenure and underwriting are absent for a real financing decision.": (
        "বর্তমান PMMY শ্রেণিভিত্তিক যোগ্যতা যাচাই করা হয়েছে; তবে প্রকৃত অর্থায়নের সিদ্ধান্তের "
        "জন্য ঋণদাতা-নির্দিষ্ট যাচাইকৃত সুদের হার, ঋণের মেয়াদ ও ঋণঝুঁকি মূল্যায়নের তথ্য নেই।"
    ),
    "OSM POIs are volunteered proxy evidence and may be incomplete.": (
        "OSM-এর স্থানভিত্তিক তথ্য স্বেচ্ছায় সংযোজিত প্রক্সি প্রমাণ; তাই এটি অসম্পূর্ণ হতে পারে।"
    ),
    # Customer groups and suppliers across every supported sector.
    "tea/sweet shops": "চা ও মিষ্টির দোকান",
    "schools/institutions": "বিদ্যালয় ও প্রতিষ্ঠান",
    "restaurants and tea shops": "রেস্তোরাঁ ও চায়ের দোকান",
    "restaurants and institutions": "রেস্তোরাঁ ও প্রতিষ্ঠান",
    "small businesses": "ক্ষুদ্র ব্যবসা",
    "students/youth": "শিক্ষার্থী ও যুবসমাজ",
    "food businesses": "খাদ্য ব্যবসা",
    "food retailers": "খাদ্যপণ্যের খুচরা বিক্রেতা",
    "fish retailers": "মাছের খুচরা বিক্রেতা",
    "FMCG distributors": "FMCG পরিবেশক",
    "authorized distributors": "অনুমোদিত পরিবেশক",
    "regional manufacturers": "আঞ্চলিক উৎপাদক",
    "regional wholesalers": "আঞ্চলিক পাইকার",
    "wholesale markets": "পাইকারি বাজার",
    "wholesale traders": "পাইকারি ব্যবসায়ী",
    "local produce suppliers": "স্থানীয় উৎপাদিত পণ্যের সরবরাহকারী",
    "farm/wholesale raw-material suppliers": "খামার ও পাইকারি কাঁচামাল সরবরাহকারী",
    "packaging suppliers": "মোড়কসামগ্রী সরবরাহকারী",
    "farmer groups": "কৃষক গোষ্ঠী",
    "grain wholesalers": "শস্যের পাইকার",
    "spice wholesalers/farmers": "মসলা ব্যবসায়ী ও চাষি",
    "oilseed farmers/wholesalers": "তৈলবীজ চাষি ও পাইকার",
    "egg/poultry producers": "ডিম ও হাঁস-মুরগি উৎপাদক",
    "feed/input dealers": "খাদ্য ও উপকরণ বিক্রেতা",
    "fishers/pond operators": "মৎস্যজীবী ও পুকুরচাষি",
    "landing/wholesale markets": "মাছ অবতরণকেন্দ্র ও পাইকারি বাজার",
    "ice suppliers": "বরফ সরবরাহকারী",
    "repair/accessory suppliers": "মেরামত ও আনুষঙ্গিক সামগ্রী সরবরাহকারী",
    # Sales and distribution channels.
    "walk-in retail": "দোকানে সরাসরি খুচরা বিক্রয়",
    "walk-in milling": "দোকানে এসে পেষাই পরিষেবা",
    "local delivery": "স্থানীয় সরবরাহ",
    "phone/digital ordering": "ফোন ও ডিজিটাল অর্ডার",
    "assisted digital ordering": "সহায়তাপ্রাপ্ত ডিজিটাল অর্ডার",
    "direct retail": "সরাসরি খুচরা বিক্রয়",
    "direct bulk order": "সরাসরি বড় অর্ডার",
    "retailer supply": "খুচরা বিক্রেতাকে সরবরাহ",
    "retailer distribution": "খুচরা বিক্রেতার মাধ্যমে বিতরণ",
    "retailer route": "খুচরা বিক্রেতাভিত্তিক সরবরাহপথ",
    "market retail": "বাজারে খুচরা বিক্রয়",
    "market aggregation": "বাজারভিত্তিক সংগ্রহ",
    "packaged retail": "মোড়কজাত খুচরা বিক্রয়",
    "restaurant supply": "রেস্তোরাঁয় সরবরাহ",
    "restaurant/institution supply": "রেস্তোরাঁ ও প্রতিষ্ঠানে সরবরাহ",
    "institutional/restaurant supply": "প্রতিষ্ঠান ও রেস্তোরাঁয় সরবরাহ",
    "institution/small-business supply": "প্রতিষ্ঠান ও ক্ষুদ্র ব্যবসায় সরবরাহ",
    "bulk food-business supply": "খাদ্য ব্যবসায়ে পাইকারি সরবরাহ",
    # Equipment.
    "shelving": "তাক",
    "counter and weighing equipment": "কাউন্টার ও ওজন মাপার সরঞ্জাম",
    "basic billing device": "মৌলিক বিলিং যন্ত্র",
    "stackable crates": "স্তূপ করে রাখা যায় এমন বাক্স",
    "weighing scale": "ওজন মাপার যন্ত্র",
    "clean handling table": "পরিষ্কার পণ্য-পরিচালনা টেবিল",
    "insulated boxes": "তাপ-নিরোধক বাক্স",
    "washable handling table": "ধোয়া যায় এমন পণ্য-পরিচালনা টেবিল",
    "processing machine": "প্রক্রিয়াকরণ যন্ত্র",
    "weighing equipment": "ওজন মাপার সরঞ্জাম",
    "sealing/packaging equipment": "সিল ও মোড়কজাত করার সরঞ্জাম",
    "flour mill": "আটা কল",
    "sieves and dust control": "চালুনি ও ধুলো নিয়ন্ত্রণ ব্যবস্থা",
    "grinder": "গুঁড়ো করার যন্ত্র",
    "sieving unit": "চালুনি ইউনিট",
    "sealer": "সিল করার যন্ত্র",
    "oil expeller": "তেল নিষ্কাশন যন্ত্র",
    "filter unit": "ছাঁকনি ইউনিট",
    "storage drums": "সংরক্ষণ ড্রাম",
    "filling/sealing equipment": "ভর্তি ও সিল করার সরঞ্জাম",
    "secure display": "নিরাপদ প্রদর্শনী ব্যবস্থা",
    "billing device": "বিলিং যন্ত্র",
    "basic testing tools": "প্রাথমিক পরীক্ষার সরঞ্জাম",
    "storage racks": "সংরক্ষণ তাক",
    "weighing/packing tools": "ওজন ও মোড়কজাত করার সরঞ্জাম",
    "delivery handling equipment": "সরবরাহের পণ্য-পরিচালনা সরঞ্জাম",
    # Quality-control records.
    "expiry rotation": "মেয়াদ অনুযায়ী পণ্য ঘোরানো",
    "daily stockout log": "দৈনিক মজুত-ঘাটতির নথি",
    "supplier invoice reconciliation": "সরবরাহকারীর চালান মিলিয়ে দেখা",
    "breakage log": "ভাঙনের নথি",
    "batch/source trace": "ব্যাচ ও উৎস শনাক্তকরণ",
    "cleaning and biosecurity checklist": "পরিচ্ছন্নতা ও জৈবনিরাপত্তার যাচাইতালিকা",
    "temperature/time log": "তাপমাত্রা ও সময়ের নথি",
    "ice-use log": "বরফ ব্যবহারের নথি",
    "spoilage and rejection log": "পণ্য নষ্ট ও বাতিলের নথি",
    "batch records": "ব্যাচের নথি",
    "cleaning schedule": "পরিচ্ছন্নতার সময়সূচি",
    "weight/yield check": "ওজন ও উৎপাদনহারের যাচাই",
    "label compliance": "লেবেলবিধি মেনে চলা",
    "moisture check": "আর্দ্রতা যাচাই",
    "cleaning log": "পরিচ্ছন্নতার নথি",
    "yield/weight reconciliation": "উৎপাদনহার ও ওজন মিলিয়ে দেখা",
    "batch trace": "ব্যাচ শনাক্তকরণ",
    "adulteration control": "ভেজাল নিয়ন্ত্রণ",
    "pack weight check": "মোড়কের ওজন যাচাই",
    "seed moisture check": "বীজের আর্দ্রতা যাচাই",
    "batch yield log": "ব্যাচভিত্তিক উৎপাদন নথি",
    "filtration check": "ছাঁকন প্রক্রিয়া যাচাই",
    "serial/warranty record": "ক্রমিক নম্বর ও ওয়ারেন্টির নথি",
    "return log": "ফেরত পণ্যের নথি",
    "stock ageing report": "মজুতের বয়সভিত্তিক প্রতিবেদন",
    "dispatch reconciliation": "প্রেরিত পণ্য মিলিয়ে দেখা",
    "damage log": "ক্ষয়ক্ষতির নথি",
    "receivable ageing": "পাওনার বয়সভিত্তিক হিসাব",
    "collection time log": "সংগ্রহের সময়ের নথি",
    "temperature/acidity check": "তাপমাত্রা ও অম্লতা যাচাই",
    "rejection/spoilage log": "বাতিল ও নষ্ট পণ্যের নথি",
    # Operational and weather factors.
    "footfall": "ক্রেতা চলাচল",
    "rent": "ভাড়া",
    "supplier credit": "সরবরাহকারীর বাকিসুবিধা",
    "inventory turnover": "মজুত আবর্তন",
    "stockouts": "মজুত ঘাটতি",
    "feed cost": "পশুখাদ্যের ব্যয়",
    "mortality": "মৃত্যুহার",
    "biosecurity": "জৈবনিরাপত্তা",
    "temperature": "তাপমাত্রা",
    "selling price": "বিক্রয়দর",
    "water/landing supply": "জল ও অবতরণকেন্দ্রের সরবরাহ",
    "feed": "খাদ্য",
    "disease": "রোগ",
    "cold chain": "শীতল সরবরাহশৃঙ্খল",
    "transport": "পরিবহন",
    "raw materials": "কাঁচামাল",
    "electricity": "বিদ্যুৎ",
    "machine utilization": "যন্ত্রের ব্যবহারহার",
    "conversion yield": "রূপান্তর উৎপাদনহার",
    "packaging": "মোড়কসামগ্রী",
    "grain input cost": "শস্যের উপকরণ ব্যয়",
    "utilization": "ব্যবহারহার",
    "raw spice cost": "কাঁচা মসলার ব্যয়",
    "power": "বিদ্যুৎ",
    "seasonal demand": "মৌসুমি চাহিদা",
    "seed cost": "বীজের ব্যয়",
    "oil price": "তেলের দাম",
    "by-product realization": "উপজাত পণ্যের বিক্রয়মূল্য",
    "inventory capital": "মজুতে আবদ্ধ মূলধন",
    "obsolescence": "পণ্য অচল হয়ে যাওয়া",
    "margin": "মার্জিন",
    "returns/warranty": "ফেরত ও ওয়ারেন্টি",
    "brand competition": "ব্র্যান্ড প্রতিযোগিতা",
    "route time": "যাত্রাপথের সময়",
    "feed/fodder": "পশুখাদ্য ও ঘাস",
    "animal health": "পশুস্বাস্থ্য",
    "spoilage": "পণ্য নষ্ট হওয়া",
    "chilling": "শীতলীকরণ",
    "heavy rainfall": "ভারী বৃষ্টি",
    "humidity/storage risk": "আর্দ্রতা ও সংরক্ষণ ঝুঁকি",
    # Insurance and protection.
    "inventory/fire protection where economical": "সাশ্রয়ী হলে মজুত ও অগ্নি-সুরক্ষা",
    "stock/transit cover where available": "প্রাপ্য হলে মজুত ও পরিবহন বীমা",
    "transit/stock protection where available": "প্রাপ্য হলে পরিবহন ও মজুত সুরক্ষা",
    "machine and stock protection": "যন্ত্র ও মজুত সুরক্ষা",
    "machine and fire protection": "যন্ত্র ও অগ্নি-সুরক্ষা",
    "machine, fire and stock protection": "যন্ত্র, অগ্নি ও মজুত সুরক্ষা",
    "inventory/theft protection": "মজুত ও চুরি-সংক্রান্ত সুরক্ষা",
    "vehicle, stock and transit protection": "যানবাহন, মজুত ও পরিবহন সুরক্ষা",
    "livestock, vehicle and stock/transit protection where applicable": (
        "প্রযোজ্য ক্ষেত্রে পশু, যানবাহন, মজুত ও পরিবহন সুরক্ষা"
    ),
    # Current dairy case and shared analytical statements.
    "yield": "উৎপাদনহার",
    "Central planning payback is 4 months.": "কেন্দ্রীয় পরিকল্পনায় বিনিয়োগ ফেরতের সময় ৪ মাস।",
    "A secondary retailer/tea-shop supply channel can diversify the primary route.": (
        "সহায়ক খুচরা বিক্রেতা ও চায়ের দোকানে সরবরাহের চ্যানেল প্রধান পথের ঝুঁকি কমাতে পারে।"
    ),
    "Plan becomes cash-negative below approximately 0.177x central selling price.": (
        "বিক্রয়দর কেন্দ্রীয় পরিকল্পিত দামের আনুমানিক ০.১৭৭ গুণের নিচে নামলে নগদ ঋণাত্মক হয়।"
    ),
    "Stage 2: the central model first supports a 70% utilization plus reserve trigger in month 5.": (
        "ধাপ ২: কেন্দ্রীয় মডেলে ৫ম মাসে প্রথমবার ৭০% ব্যবহারহার ও সংরক্ষিত অর্থের শর্ত পূরণ হয়।"
    ),
}


_BENGALI_PDF_PATTERNS = (
    (
        re.compile(r"Central planning payback is ([0-9.]+) months\."),
        r"কেন্দ্রীয় পরিকল্পনায় বিনিয়োগ ফেরতের সময় \1 মাস।",
    ),
    (
        re.compile(r"The modelled cash-conversion cycle is short at ([0-9.]+) days\."),
        r"মডেলভিত্তিক নগদ-রূপান্তর চক্রটি সংক্ষিপ্ত: \1 দিন।",
    ),
    (
        re.compile(r"The planning graph contains ([0-9.]+) units of unserved flow\."),
        r"পরিকল্পনা গ্রাফে \1 একক অপূর্ণ চাহিদাপ্রবাহ রয়েছে।",
    ),
    (
        re.compile(r"([0-9]+) marginal capacity repair options were evaluated\."),
        r"প্রান্তিক সক্ষমতা মেরামতের \1টি বিকল্প মূল্যায়ন করা হয়েছে।",
    ),
    (
        re.compile(
            r"Plan becomes cash-negative below approximately ([0-9.]+)x central selling price\."
        ),
        r"বিক্রয়দর কেন্দ্রীয় পরিকল্পিত দামের আনুমানিক \1 গুণের নিচে নামলে নগদ ঋণাত্মক হয়।",
    ),
)


def translate_pdf_text(value, language: str) -> str:
    """Translate report prose while keeping website language behavior unchanged."""
    if value is None:
        return "-"
    text = str(value)
    if language != "bn":
        return translate_detail_text(text, language)
    if text in BENGALI_PDF_EXACT:
        return BENGALI_PDF_EXACT[text]
    for pattern, replacement in _BENGALI_PDF_PATTERNS:
        if pattern.fullmatch(text):
            return pattern.sub(replacement, text)
    return translate_detail_text(text, language)

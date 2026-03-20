"""
image_classifier.py — Phân loại địa điểm du lịch từ ảnh.
Version 5.2 — Fix: destination field trả về canonical city (không phải tỉnh thô)
  ✅ "Lâm Đồng" → "Da Lat"
  ✅ "Lào Cai" → "Sa Pa"
  ✅ "Quảng Ninh" → "Ha Long"
  ✅ Tất cả province → canonical city mapping
"""

import os, base64, warnings, io, json, re

warnings.filterwarnings("ignore")

from PIL import Image

try:
    from config import GROQ_API_KEY
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_VISION_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "llama-3.2-90b-vision-preview",
    "llama-3.2-11b-vision-preview",
]

# ══════════════════════════════════════════════════════════════════
# PROVINCE → CANONICAL CITY MAP
# Classifier đôi khi trả tỉnh thay vì thành phố
# ══════════════════════════════════════════════════════════════════
_PROVINCE_TO_CANONICAL = {
    # Vietnam provinces → canonical destination name
    "Lâm Đồng": "Da Lat",
    "Lam Dong": "Da Lat",
    "Quảng Ninh": "Ha Long",
    "Quang Ninh": "Ha Long",
    "Khánh Hòa": "Nha Trang",
    "Khanh Hoa": "Nha Trang",
    "Kiên Giang": "Phu Quoc",
    "Kien Giang": "Phu Quoc",
    "Lào Cai": "Sa Pa",
    "Lao Cai": "Sa Pa",
    "Thừa Thiên Huế": "Hue",
    "Thua Thien Hue": "Hue",
    "Thừa Thiên": "Hue",
    "Đà Nẵng": "Da Nang",
    "Da Nang": "Da Nang",
    "Hà Nội": "Hanoi",
    "Ha Noi": "Hanoi",
    "Hanoi": "Hanoi",
    "TP. Hồ Chí Minh": "Ho Chi Minh City",
    "Ho Chi Minh": "Ho Chi Minh City",
    "Hồ Chí Minh": "Ho Chi Minh City",
    "Bà Rịa - Vũng Tàu": "Vung Tau",
    "Ba Ria Vung Tau": "Vung Tau",
    "Bà Rịa": "Vung Tau",
    "Bình Thuận": "Mui Ne",
    "Binh Thuan": "Mui Ne",
    "Quảng Nam": "Hoi An",
    "Quang Nam": "Hoi An",
    "Ninh Bình": "Ninh Binh",
    "Ninh Binh": "Ninh Binh",
    "Hà Giang": "Ha Giang",
    "Ha Giang": "Ha Giang",
    "Tây Ninh": "Tay Ninh",
    "Tay Ninh": "Tay Ninh",
    "Hải Phòng": "Hai Phong",
    "Hai Phong": "Hai Phong",
    "Bình Định": "Quy Nhon",
    "Binh Dinh": "Quy Nhon",
    "Phú Yên": "Tuy Hoa",
    "Phu Yen": "Tuy Hoa",
    "Đắk Lắk": "Buon Ma Thuot",
    "Dak Lak": "Buon Ma Thuot",
    "Gia Lai": "Pleiku",
    "Kon Tum": "Kon Tum",
    "Thanh Hóa": "Thanh Hoa",
    "Thanh Hoa": "Thanh Hoa",
    "Nghệ An": "Vinh",
    "Nghe An": "Vinh",
    "Quảng Bình": "Phong Nha",
    "Quang Binh": "Phong Nha",
    "Cần Thơ": "Can Tho",
    "Can Tho": "Can Tho",
    "Đồng Tháp": "Can Tho",
    "An Giang": "Chau Doc",
    # Special landmark → city mapping
    "Núi Bà Đen": "Tay Ninh",
    "Nui Ba Den": "Tay Ninh",
    "Chùa Bái Đính": "Ninh Binh",
    "Bai Dinh": "Ninh Binh",
    "Fansipan": "Sa Pa",
    "Tràng An": "Ninh Binh",
    "Trang An": "Ninh Binh",
    "Phong Nha": "Phong Nha",
    "Son Doong": "Phong Nha",
    "Ba Na Hills": "Da Nang",
    "Bà Nà Hills": "Da Nang",
    "Golden Bridge": "Da Nang",
    "Cầu Vàng": "Da Nang",
    "Lady Buddha": "Da Nang",
    "Linh Ứng": "Da Nang",
}


def _normalize_destination(raw_dest: str, raw_label: str = "") -> str:
    """
    Normalize destination từ classifier output.
    Map tỉnh → canonical city.
    """
    if not raw_dest or raw_dest in ("Unknown", "nan", ""):
        return raw_dest or "Unknown"

    # Check direct mapping
    canonical = _PROVINCE_TO_CANONICAL.get(raw_dest)
    if canonical:
        return canonical

    # Check label field for landmark hints
    if raw_label:
        canonical = _PROVINCE_TO_CANONICAL.get(raw_label)
        if canonical:
            return canonical

    # Partial match on province name
    for province, city in _PROVINCE_TO_CANONICAL.items():
        if province.lower() in raw_dest.lower() or raw_dest.lower() in province.lower():
            return city

    return raw_dest


# ══════════════════════════════════════════════════════════════════
# PROMPT — BƯỚC 1: Nhận diện ban đầu
# ══════════════════════════════════════════════════════════════════

PROMPT_STEP1 = """You are a travel destination expert. Analyze this image carefully.

FIRST — Scan for any visible TEXT in the image:
Look for signs, watermarks, captions, logos, website names, location tags, tour company names.
ANY visible text is your strongest clue — report it exactly.

THEN — Analyze these visual features:

=== VIETNAM LOCATIONS — READ CAREFULLY ===

NÚI BÀ ĐEN (Tây Ninh):
KEY FEATURES that MUST be present:
- Mountain rises from COMPLETELY FLAT lowland plains (Mekong delta farmland)
- Sun World cable car (orange/white cabins) visible on steep mountain slopes
- Large white Buddha OR temple complex near the summit
- Dense tropical jungle covering all slopes
- Looking from the top: flat farmland/rice fields spreading to horizon in all directions
- The mountain stands ALONE — no other mountains or hills around it
- NO sea, NO ocean, NO beach, NO coastal city visible anywhere

LADY BUDDHA / CHÙA LINH ỨNG (Sơn Trà, Đà Nẵng):
KEY FEATURES that MUST be present:
- Tall white STANDING Buddha (67m) on a hillside/peninsula
- BLUE SEA or OCEAN clearly visible in the background
- Da Nang city coastline, high-rise buildings, beach visible behind
- The statue faces toward the ocean
- Peninsula setting — sea visible on multiple sides

CẦU VÀNG / GOLDEN BRIDGE (Bà Nà Hills, Đà Nẵng):
- Pedestrian bridge supported by TWO GIANT GREY STONE HANDS
- Bridge floats above a sea of clouds/mist
- French village architecture nearby

FANSIPAN (Sa Pa, Lào Cai):
- Highest mountain in Indochina (3,143m)
- At or above the clouds — looking DOWN at cloud layer
- Snow or frost visible (in cooler months)
- Metal platform/viewing deck at summit
- Surrounded by other high mountain peaks of the Hoang Lien Son range

CHÙA BÁI ĐÍNH (Ninh Bình):
- MULTIPLE large bronze/golden Buddha statues lined up IN A ROW along wide corridors
- Very large temple complex on hillside (NOT isolated mountain)
- Bell towers, many courtyards
- Limestone hills of Ninh Bình visible nearby

VŨNG TÀU Christ statue:
- White CHRIST statue with arms outstretched horizontally (like Rio de Janeiro)
- Sea/ocean visible on both sides (peninsula)

ĐÀ LẠT (Lâm Đồng):
- Hill town with pine forests + French colonial buildings + flower gardens
- Cool misty/foggy atmosphere
- Xuan Huong lake in valley
- Valley/bowl-shaped terrain with hills on all sides
- Colorful flower fields (hydrangea, sunflower)
- NO beach, NO ocean, NOT tropical flat land

SA PA (Lào Cai):
- Stepped rice terraces on mountain slopes
- H'Mông minority villages with traditional houses
- Morning mist in mountain valleys
- Fansipan mountain visible in distance
- Terraced hillsides, NOT flat land

=== OTHER VIETNAM ===
HẠ LONG BAY: Limestone karst pillars FROM WATER, boats, misty bay
HỘI AN: Yellow/ochre walls + red lanterns + covered bridge + narrow old streets
CẦN THƠ: Floating market boats with fruit/vegetables on wide Mekong river at sunrise
PHÚ QUỐC: Turquoise/emerald crystal clear sea + white sand + Vinpearl cable car OVER sea
HUẾ CITADEL: Thick ancient brick walls + yellow Ngọ Môn gate + Perfume River
MÚI NÉ: Orange/red sand dunes + basket boats
NHA TRANG: Curved bay + Cham towers on hill + Vinpearl cable car
HÀ NỘI: Hoan Kiếm lake + red Huc Bridge + Turtle Tower on small island
HỒ CHÍ MINH CITY: Bitexco tower + Notre-Dame Cathedral red brick facade + Ben Thanh market

=== INTERNATIONAL ===
BALI: Tanah Lot sea temple / Tegalalang rice terraces / stone split gates
BANGKOK: Wat Arun spires on river / Grand Palace gold roofs
ANGKOR WAT: Stone temple complex with 5 towers, moat, jungle
SINGAPORE: Marina Bay Sands 3-tower hotel + Gardens supertrees
PARIS: Eiffel Tower iron lattice + Seine
TOKYO: Mount Fuji snow cap / red torii gates / Shibuya crossing
SANTORINI: White buildings + blue domed churches + caldera cliff

IMPORTANT: Return the specific CITY/ATTRACTION name, NOT the province name.
- If you see Da Lat → destination = "Da Lat" (NOT "Lam Dong" or "Lâm Đồng")
- If you see Sa Pa → destination = "Sa Pa" (NOT "Lao Cai")
- If you see Ha Long → destination = "Ha Long" (NOT "Quang Ninh")

Return ONLY a JSON object (no markdown, no explanation outside JSON):
{
  "is_travel": true,
  "confidence": 85,
  "label": "Da Lat Hill Town",
  "label_vi": "Thành phố Đà Lạt",
  "destination": "Da Lat",
  "destination_vi": "Đà Lạt",
  "country": "Vietnam",
  "category": "Hill Town",
  "description": "3 sentences: what you see in the image, which specific features you identified, and how they confirm this location.",
  "visual_evidence": ["pine forests on hillside", "French colonial architecture", "foggy valley atmosphere"],
  "text_in_image": "exact text visible or none",
  "similar_places_ruled_out": "Sa Pa ruled out: no rice terraces. Ha Long ruled out: no sea/karst pillars.",
  "uncertainty": "none"
}"""


# ══════════════════════════════════════════════════════════════════
# PROMPT — BƯỚC 2: Xác nhận
# ══════════════════════════════════════════════════════════════════


def _build_step2_prompt(step1: dict) -> str:
    label = step1.get("label", "Unknown")
    dest = step1.get("destination", "Unknown")
    conf = step1.get("confidence", 50)
    evid = step1.get("visual_evidence", [])
    txt = step1.get("text_in_image", "none")
    ruled = step1.get("similar_places_ruled_out", "")
    uncert = step1.get("uncertainty", "none")
    ev_str = ", ".join(str(e) for e in evid) if evid else "none"

    return f"""You identified this image as "{label}" in "{dest}" with {conf}% confidence.
Evidence: {ev_str}
Text in image: {txt}
Ruled out: {ruled}
Uncertainty: {uncert}

Now VERIFY by answering these specific questions about what you see in the image:

QUESTION 1 — Is there sea/ocean/beach visible anywhere in the image?
→ YES = likely Lady Buddha (Da Nang) or Vung Tau or coastal location
→ NO = rules out Lady Buddha Da Nang, rules out Vung Tau

QUESTION 2 — Is the mountain/hill rising from completely flat land (no sea)?
→ YES = supports Nui Ba Den (Tay Ninh)
→ NO = rules out Nui Ba Den

QUESTION 3 — Is there a cable car visible on the mountain slopes?
→ YES with steep mountain from flat land = Nui Ba Den (Tay Ninh)
→ YES with sea in background = Phu Quoc Vinpearl or Nha Trang Vinpearl

QUESTION 4 — Are you looking DOWN through/above clouds from a very high altitude?
→ YES = likely Fansipan summit (Sa Pa)

QUESTION 5 — Is it a valley/bowl-shaped hill town with pine forests and European-style buildings?
→ YES + cool misty + NO sea = Da Lat (Lam Dong)

QUESTION 6 — Are there stepped rice terraces on mountain slopes with minority villages?
→ YES + misty mountains = Sa Pa (Lao Cai)

QUESTION 7 — What does the visible text say? (if any text was found)
→ Trust text completely over visual guesses

Based on your answers, provide your FINAL identification.
IMPORTANT: Use the specific CITY name, NOT the province name:
- Da Lat (not Lam Dong), Sa Pa (not Lao Cai), Ha Long (not Quang Ninh)
- Nha Trang (not Khanh Hoa), Phu Quoc (not Kien Giang)

Return ONLY valid JSON:
{{
  "confirmed": true or false,
  "final_label": "specific place name",
  "final_label_vi": "Vietnamese name",
  "final_destination": "city name (NOT province)",
  "final_destination_vi": "Vietnamese city name",
  "final_country": "country",
  "final_confidence": 0-100,
  "final_description": "4 sentences: what you see, key features that confirm this identification, what you ruled out and why.",
  "final_evidence": ["evidence 1", "evidence 2", "evidence 3"],
  "q1_sea_visible": "yes/no - explain",
  "q2_flat_land": "yes/no - explain",
  "q3_cable_car": "yes/no - explain",
  "q5_hill_town": "yes/no - explain",
  "q6_rice_terraces": "yes/no - explain",
  "correction_reason": "why you changed or kept the answer"
}}"""


# ══════════════════════════════════════════════════════════════════
# NOT-TRAVEL MESSAGES
# ══════════════════════════════════════════════════════════════════

_NOT_TRAVEL = {
    "vi": {
        "face": "Đây là ảnh chân dung/người. Vui lòng gửi ảnh phong cảnh hoặc địa danh.",
        "doc": "Đây là ảnh tài liệu/văn bản. Vui lòng gửi ảnh địa điểm du lịch.",
        "screen": "Ảnh chụp màn hình không rõ địa điểm. Vui lòng gửi ảnh phong cảnh.",
        "food": "Đây là ảnh món ăn. Bạn muốn tư vấn ẩm thực tại điểm đến nào?",
        "indoor": "Ảnh không gian trong nhà. Hãy gửi ảnh địa điểm du lịch ngoài trời.",
        "default": "Ảnh này không phải địa điểm du lịch. Hãy gửi ảnh phong cảnh, di tích hoặc địa danh.",
    },
    "en": {
        "face": "Portrait photo detected. Please send a travel destination photo.",
        "doc": "Document image. Please send a travel destination photo.",
        "screen": "Non-travel screenshot. Please send a landscape or landmark photo.",
        "food": "Food photo. Would you like cuisine recommendations for a destination?",
        "indoor": "Indoor space. Please send an outdoor travel destination photo.",
        "default": "This doesn't appear to be a travel destination. Please send landscape or landmark photos.",
    },
}


def _not_travel_msg(reason: str, lang: str = "vi") -> str:
    m = _NOT_TRAVEL.get(lang, _NOT_TRAVEL["vi"])
    r = (reason or "").lower()
    if any(w in r for w in ["face", "portrait", "person", "people", "selfie"]):
        return m["face"]
    if any(w in r for w in ["screen", "screenshot"]):
        return m["screen"]
    if any(w in r for w in ["document", "text", "paper"]):
        return m["doc"]
    if any(w in r for w in ["food", "meal", "dish", "plate"]):
        return m["food"]
    if any(w in r for w in ["indoor", "room", "office", "interior"]):
        return m["indoor"]
    return m["default"]


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════


def _encode(img: Image.Image, max_size: int = 1024) -> str:
    img = img.convert("RGB")
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=93)
    return base64.b64encode(buf.getvalue()).decode()


def _parse(raw: str) -> dict | None:
    if not raw:
        return None
    raw = re.sub(r"```(?:json)?\s*", "", raw.strip()).rstrip("`").strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None
    text = m.group()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fixed = re.sub(r",(\s*[}\]])", r"\1", text)
        try:
            return json.loads(fixed)
        except Exception:
            return None


def _clean(v, fallback: str = "Unknown") -> str:
    s = str(v or "").strip()
    return fallback if s in ("", "nan", "None", "none", "null", "undefined") else s


def _call(client, b64: str, prompt: str, max_tokens: int = 900) -> dict | None:
    for model in GROQ_VISION_MODELS:
        try:
            print(f"[IMG] → {model[:55]}")
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.05,
            )
            raw = resp.choices[0].message.content.strip()
            print(f"[IMG] Raw: {raw[:200]}")
            parsed = _parse(raw)
            if parsed:
                print(f"[IMG] ✅ Parsed OK")
                return parsed
            print(f"[IMG] ⚠️ JSON parse failed, trying next model")
        except Exception as e:
            err = str(e).lower()
            print(f"[IMG] ⚠️ {model[:30]}: {e}")
            if not any(
                k in err
                for k in [
                    "not support",
                    "invalid model",
                    "model_not_found",
                    "vision",
                    "image",
                    "unsupported",
                    "does not support",
                ]
            ):
                break
    return None


# ══════════════════════════════════════════════════════════════════
# RESULT BUILDER — FIXED: normalize destination to canonical city
# ══════════════════════════════════════════════════════════════════


def _build(raw: dict, lang: str) -> list[dict]:
    # Not travel
    if not bool(raw.get("is_travel", True)):
        reason = raw.get("not_travel_reason", "")
        return [
            {
                "label": "NOT_TRAVEL",
                "destination": "Unknown",
                "category": "Unknown",
                "confidence": 0.0,
                "display_name": "Không phải ảnh du lịch"
                if lang == "vi"
                else "Not a travel photo",
                "is_specific": False,
                "is_travel": False,
                "description": _clean(raw.get("description", ""), ""),
                "error": _not_travel_msg(reason, lang),
                "not_travel_reason": reason,
                "enrichment_context": "",
                "visual_evidence": [],
                "text_in_image": "",
            }
        ]

    # Raw values from classifier
    label_vi_raw = _clean(
        raw.get("label_vi")
        or raw.get("final_label_vi")
        or raw.get("label")
        or raw.get("final_label")
    )
    label_en_raw = _clean(raw.get("label") or raw.get("final_label"), label_vi_raw)
    dest_raw = _clean(
        raw.get("destination")
        or raw.get("final_destination")
        or raw.get("destination_vi")
        or raw.get("final_destination_vi")
    )
    dest_vi_raw = _clean(
        raw.get("destination_vi")
        or raw.get("final_destination_vi")
        or raw.get("destination")
        or raw.get("final_destination")
    )

    # ── NORMALIZE destination to canonical city ──────────────
    # This is the critical fix: map province → city
    dest_canonical = _normalize_destination(dest_raw, label_en_raw)
    dest_vi_canonical = _normalize_destination(dest_vi_raw, label_vi_raw)

    # If canonical is an English city name, try to get the VI version
    _CANONICAL_VI = {
        "Da Lat": "Đà Lạt",
        "Ha Long": "Hạ Long",
        "Nha Trang": "Nha Trang",
        "Phu Quoc": "Phú Quốc",
        "Sa Pa": "Sa Pa",
        "Hue": "Huế",
        "Da Nang": "Đà Nẵng",
        "Hanoi": "Hà Nội",
        "Ho Chi Minh City": "TP. Hồ Chí Minh",
        "Vung Tau": "Vũng Tàu",
        "Mui Ne": "Mũi Né",
        "Hoi An": "Hội An",
        "Ninh Binh": "Ninh Bình",
        "Ha Giang": "Hà Giang",
        "Tay Ninh": "Tây Ninh",
        "Quy Nhon": "Quy Nhơn",
        "Can Tho": "Cần Thơ",
        "Phong Nha": "Phong Nha - Kẻ Bàng",
        "Buon Ma Thuot": "Buôn Ma Thuột",
        "Pleiku": "Pleiku",
    }

    if lang == "vi":
        dest_display = _CANONICAL_VI.get(
            dest_canonical, dest_vi_canonical or dest_canonical
        )
    else:
        dest_display = dest_canonical

    country = _clean(raw.get("country") or raw.get("final_country"))
    cat = _clean(raw.get("category"), "General")
    conf = float(raw.get("confidence") or raw.get("final_confidence") or 50)
    desc = _clean(raw.get("description") or raw.get("final_description"), "")
    evid = raw.get("visual_evidence") or raw.get("final_evidence") or []
    txt = _clean(raw.get("text_in_image", "none"), "")
    ruled = _clean(
        raw.get("similar_places_ruled_out") or raw.get("correction_reason"), ""
    )

    if isinstance(evid, str):
        evid = [evid]

    # Display label
    if lang == "vi":
        display_label = label_vi_raw
    else:
        display_label = label_en_raw

    GENERIC = {
        "Beach",
        "Mountain",
        "Temple",
        "City",
        "Waterfall",
        "Cave",
        "Rice Terrace",
        "Market",
        "Forest",
        "Island",
        "Harbor",
        "Bay",
        "Ruins",
        "National Park",
        "Ancient Town",
        "Pagoda",
        "Lake",
        "River",
        "Desert",
        "Village",
        "Travel Destination",
        "Statue",
        "General",
        "Unknown",
        "Landmark",
        "Attraction",
        "Temple/Mountain",
        "Mountain/Temple",
        "Hill Town",
    }
    is_spec = (
        conf >= 60
        and dest_canonical not in ("Unknown", "")
        and label_en_raw not in GENERIC
        and len(label_en_raw) > 3
    )

    # Build enrichment context
    parts = []
    if display_label not in ("Unknown", ""):
        parts.append(f"Địa điểm nhận diện từ ảnh: {display_label}")
    if dest_canonical not in ("Unknown", ""):
        parts.append(f"Điểm đến: {dest_display}")
    if country not in ("Unknown", ""):
        parts.append(f"Quốc gia: {country}")
    if conf >= 50:
        parts.append(f"Độ tin cậy: {conf:.0f}%")
    if evid:
        parts.append(f"Đặc điểm nhận ra: {', '.join(str(e) for e in evid[:3])}")
    if txt and txt != "none":
        parts.append(f"Văn bản trong ảnh: {txt}")
    if ruled:
        parts.append(f"Đã loại trừ: {ruled}")

    print(
        f"[IMG] Normalized destination: '{dest_raw}' → '{dest_canonical}' (display: '{dest_display}')"
    )

    return [
        {
            "label": display_label,
            "label_en": label_en_raw,
            "destination": dest_canonical,  # ← canonical city for routing
            "destination_display": dest_display,  # ← localized display name
            "country": country,
            "category": cat,
            "confidence": round(conf, 1),
            "display_name": display_label,
            "is_specific": is_spec,
            "is_travel": True,
            "description": desc,
            "visual_evidence": [str(e) for e in evid] if isinstance(evid, list) else [],
            "text_in_image": txt if txt != "none" else "",
            "enrichment_context": " | ".join(parts),
            "similar_places_ruled_out": ruled,
        }
    ]


# ══════════════════════════════════════════════════════════════════
# IMAGE CLASSIFIER
# ══════════════════════════════════════════════════════════════════


class ImageClassifier:
    """
    Travel destination classifier v5.2
    Fix: destination luôn là canonical city (không phải tỉnh)
    """

    def __init__(self):
        self._client = None
        self._lang = "vi"
        self._model = "none"

        if not GROQ_API_KEY:
            print("[IMG] ⚠️ GROQ_API_KEY chưa đặt.")
            return
        try:
            from groq import Groq

            self._client = Groq(api_key=GROQ_API_KEY)
            self._model = GROQ_VISION_MODELS[0]
            print(f"[IMG] ✅ ImageClassifier v5.2 ready (Groq Vision)")
        except Exception as e:
            print(f"[IMG] ❌ Groq init: {e}")

    def set_labels_from_df(self, df):
        pass

    def get_destinations(self) -> list:
        return []

    def get_active_model(self) -> str:
        return self._model

    def classify(
        self,
        image_path_or_pil,
        top_k: int = 3,
        lang: str = "vi",
    ) -> list[dict]:
        self._lang = lang

        # Load image
        try:
            if isinstance(image_path_or_pil, str):
                img = Image.open(image_path_or_pil).convert("RGB")
            else:
                img = image_path_or_pil.convert("RGB")
        except Exception as e:
            return self._err(f"Không thể đọc ảnh: {e}")

        if not self._client:
            return self._err("GROQ_API_KEY chưa cấu hình.")

        b64 = _encode(img, max_size=1024)

        # ── STEP 1 ──────────────────────────────────────────
        print("[IMG] ═══ STEP 1: Identification ═══")
        s1 = _call(self._client, b64, PROMPT_STEP1, max_tokens=900)

        if s1 is None:
            return self._err("Không thể phân tích ảnh. Kiểm tra GROQ_API_KEY.")

        if not bool(s1.get("is_travel", True)):
            return _build(s1, lang)

        s1_conf = float(s1.get("confidence", 50))
        s1_label = str(s1.get("label", "Unknown"))
        s1_dest = str(s1.get("destination", "Unknown"))
        print(f"[IMG] Step1: '{s1_label}' @ '{s1_dest}' conf={s1_conf:.0f}%")

        # ── STEP 2: Verify ───────────────────────────────────
        is_ambiguous_scene = any(
            kw in (s1_label + s1.get("category", "") + s1_dest).lower()
            for kw in [
                "buddha",
                "statue",
                "tượng",
                "lady",
                "linh",
                "temple",
                "pagoda",
                "mountain",
                "núi",
                "fansipan",
                "bái đính",
                "bà đen",
                "vũng tàu",
                "vung tau",
                "da lat",
                "đà lạt",
                "lam dong",
                "lâm đồng",
                "sa pa",
                "sapa",
                "lao cai",
                "lào cai",
            ]
        )

        should_verify = (
            s1_conf < 85 or s1_dest in ("Unknown", "nan", "") or is_ambiguous_scene
        )

        if should_verify:
            print(
                f"[IMG] ═══ STEP 2: Verification (ambiguous={is_ambiguous_scene}, conf={s1_conf:.0f}) ═══"
            )
            s2 = _call(self._client, b64, _build_step2_prompt(s1), max_tokens=700)

            if s2:
                s2_conf = float(s2.get("final_confidence", s1_conf))
                s2_label = _clean(
                    s2.get("final_label_vi") or s2.get("final_label"), s1_label
                )
                s2_dest = _clean(
                    s2.get("final_destination") or s2.get("final_destination_vi"),
                    s1_dest,
                )
                print(f"[IMG] Step2: '{s2_label}' @ '{s2_dest}' conf={s2_conf:.0f}%")

                merged = dict(s1)
                merged["label"] = s2.get("final_label") or s1.get("label")
                merged["label_vi"] = s2.get("final_label_vi") or s1.get("label_vi")
                merged["destination"] = s2.get("final_destination") or s1.get(
                    "destination"
                )
                merged["destination_vi"] = s2.get("final_destination_vi") or s1.get(
                    "destination_vi"
                )
                merged["country"] = s2.get("final_country") or s1.get("country")
                merged["confidence"] = s2_conf
                merged["description"] = s2.get("final_description") or s1.get(
                    "description"
                )
                merged["visual_evidence"] = s2.get("final_evidence") or s1.get(
                    "visual_evidence"
                )
                merged["similar_places_ruled_out"] = s2.get(
                    "correction_reason"
                ) or s1.get("similar_places_ruled_out", "")
                q_answers = []
                for q in [
                    "q1_sea_visible",
                    "q2_flat_land",
                    "q3_cable_car",
                    "q5_hill_town",
                    "q6_rice_terraces",
                ]:
                    v = s2.get(q)
                    if v:
                        q_answers.append(str(v))
                if q_answers:
                    merged["checklist_answers"] = " | ".join(q_answers)

                results = _build(merged, lang)
            else:
                print("[IMG] Step 2 failed — using Step 1 result")
                results = _build(s1, lang)
        else:
            results = _build(s1, lang)

        return results[:top_k]

    def _err(self, msg: str) -> list[dict]:
        return [
            {
                "label": "Unknown",
                "destination": "Unknown",
                "category": "Unknown",
                "confidence": 0.0,
                "display_name": "Không thể nhận diện"
                if self._lang == "vi"
                else "Cannot identify",
                "is_specific": False,
                "is_travel": None,
                "description": msg,
                "error": msg,
                "visual_evidence": [],
                "text_in_image": "",
                "enrichment_context": "",
                "similar_places_ruled_out": "",
            }
        ]

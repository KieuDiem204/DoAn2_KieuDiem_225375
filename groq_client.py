"""
groq_client.py — Groq LLM tour guide, v8.1
Fix:
  ✅ Khi destination đã được resolve từ image classifier → KHÔNG override bằng text extraction
  ✅ Image query luôn tư vấn đúng điểm đến từ ảnh
"""

import warnings, re

warnings.filterwarnings("ignore")

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, TEMPERATURE


# ══════════════════════════════════════════════════════════════════
# DESTINATION EXTRACTION
# ══════════════════════════════════════════════════════════════════


def _extract_destination_from_text(text: str) -> str | None:
    """
    Extract canonical destination from text.

    BUG FIXED: Previous code ran data_engine lookup FIRST.
    Bug: 'Sa Pa'.lower().split() = ['sa','pa'], both len<=2.
    So: all(w in low for w in [] if len(w)>2) = all([]) = TRUE
    This caused 'Sa Pa' to match EVERY text input!

    FIX: Run regex patterns FIRST (they handle Vietnamese diacritics perfectly),
    then use data_engine as fallback with a fixed word-boundary condition.
    """
    if not text:
        return None
    low = text.lower()

    # ── STEP 1: Regex patterns (most reliable for Vietnamese) ──
    _PATTERNS = [
        # Multi-word — diacritics AND ASCII variants, longest first
        (
            r"hồ\s*chí\s*minh|ho\s*chi\s*minh|thành\s*phố\s*hcm|\bhcm\b|sài\s*gòn|saigon",
            "Ho Chi Minh City",
        ),
        (r"hội\s*an|hoi\s*an", "Hoi An"),
        (r"hạ\s*long|ha\s*long|halong", "Ha Long"),
        (r"hà\s*nội|ha\s*noi|\bhanoi\b", "Hanoi"),
        (r"đà\s*lạt|da\s*lat|\bdalat\b", "Da Lat"),
        (r"đà\s*nẵng|da\s*nang|\bdanang\b", "Da Nang"),
        (r"phú\s*quốc|phu\s*quoc", "Phu Quoc"),
        (r"nha\s*trang", "Nha Trang"),
        (r"sa\s*pa|\bsapa\b", "Sa Pa"),
        (r"vũng\s*tàu|vung\s*tau", "Vung Tau"),
        (r"cần\s*thơ|can\s*tho", "Can Tho"),
        (r"mũi\s*né|mui\s*ne", "Mui Ne"),
        (r"quy\s*nhơn|quy\s*nhon", "Quy Nhon"),
        (r"phan\s*thiết|phan\s*thiet", "Phan Thiet"),
        (r"tây\s*ninh|tay\s*ninh", "Tay Ninh"),
        (r"ninh\s*bình|ninh\s*binh", "Ninh Binh"),
        (r"hà\s*giang|ha\s*giang", "Ha Giang"),
        (r"cao\s*bằng|cao\s*bang", "Cao Bang"),
        (r"phong\s*nha", "Phong Nha"),
        (r"buôn\s*ma\s*thuột|buon\s*ma\s*thuot", "Buon Ma Thuot"),
        (r"châu\s*đốc|chau\s*doc", "Chau Doc"),
        (r"rạch\s*giá|rach\s*gia", "Rach Gia"),
        (r"cà\s*mau|ca\s*mau", "Ca Mau"),
        (r"bạc\s*liêu|bac\s*lieu", "Bac Lieu"),
        (r"sóc\s*trăng|soc\s*trang", "Soc Trang"),
        (r"trà\s*vinh|tra\s*vinh", "Tra Vinh"),
        (r"vĩnh\s*long|vinh\s*long", "Vinh Long"),
        (r"mỹ\s*tho|my\s*tho", "My Tho"),
        (r"bến\s*tre|ben\s*tre", "Ben Tre"),
        (r"hải\s*phòng|hai\s*phong", "Hai Phong"),
        (r"bắc\s*ninh|bac\s*ninh", "Bac Ninh"),
        (r"bắc\s*giang|bac\s*giang", "Bac Giang"),
        (r"thái\s*nguyên|thai\s*nguyen", "Thai Nguyen"),
        (r"lạng\s*sơn|lang\s*son", "Lang Son"),
        (r"yên\s*bái|yen\s*bai", "Yen Bai"),
        (r"hòa\s*bình|hoa\s*binh", "Hoa Binh"),
        (r"sơn\s*la|son\s*la", "Son La"),
        (r"điện\s*biên|dien\s*bien", "Dien Bien"),
        (r"lai\s*châu|lai\s*chau", "Lai Chau"),
        (r"kon\s*tum", "Kon Tum"),
        (r"ba\s*nà\s*hills?|ba\s*na\s*hills?|bà\s*nà", "Da Nang"),
        (r"kuala\s*lumpur", "Kuala Lumpur"),
        (r"new\s*york", "New York"),
        (r"hong\s*kong|hồng\s*kông", "Hong Kong"),
        (r"rio\s*de\s*janeiro", "Rio de Janeiro"),
        (r"chiang\s*mai", "Chiang Mai"),
        (r"siem\s*reap|angkor", "Siem Reap"),
        (r"cape\s*town", "Cape Town"),
        (r"los\s*angeles", "Los Angeles"),
        # Single word
        (r"\bbangkok\b", "Bangkok"),
        (r"\bbali\b", "Bali"),
        (r"\bsingapore\b", "Singapore"),
        (r"\btokyo\b", "Tokyo"),
        (r"\bosaka\b", "Osaka"),
        (r"\bseoul\b", "Seoul"),
        (r"\bparis\b", "Paris"),
        (r"\brome\b", "Rome"),
        (r"\blondon\b", "London"),
        (r"\bsydney\b", "Sydney"),
        (r"\bdubai\b", "Dubai"),
        (r"\bmanila\b", "Manila"),
        (r"\btaipei\b", "Taipei"),
        (r"\bphuket\b", "Phuket"),
        (r"\bsantorini\b", "Santorini"),
        (r"\bamsterdam\b", "Amsterdam"),
        (r"\bbarcelona\b", "Barcelona"),
        (r"\bberlin\b", "Berlin"),
        (r"\bmaldives\b", "Maldives"),
        (r"\bcancun\b", "Cancun"),
        (r"\bvancouver\b", "Vancouver"),
        (r"\bmarrakech\b", "Marrakech"),
        (r"\bedinburgh\b", "Edinburgh"),
        (r"\bhonolulu\b", "Honolulu"),
        (r"\bathens\b", "Athens"),
        (r"\bpleiku\b", "Pleiku"),
        (r"\bhuế\b|hue\b", "Hue"),
    ]
    for pattern, canonical in _PATTERNS:
        if re.search(pattern, low):
            return canonical

    # ── STEP 2: Data engine fallback (for less common destinations) ──
    try:
        from data_engine import get_engine

        engine = get_engine()

        # 2a. Exact substring (English names only — need len >= 5 to avoid false positives)
        for dest in engine.all_destinations():
            dest_low = dest.lower()
            # Only exact-match if destination name is meaningful length
            if len(dest_low) >= 5 and dest_low in low:
                return dest

        # 2b. Word-boundary — FIXED: skip if no meaningful words (>2 chars)
        # This prevents 'Sa Pa' (both words len=2) from matching everything via all([])=True
        for dest in engine.all_destinations():
            words = dest.lower().split()
            meaningful = [w for w in words if len(w) > 2]
            if not meaningful:
                continue  # ← THE FIX: skip 'Sa Pa', 'My Tho', 'Ha Long' etc
            if len(words) > 1 and all(w in low for w in meaningful):
                return dest
    except Exception:
        pass

    return None


# ══════════════════════════════════════════════════════════════════
# INTENT CLASSIFICATION
# ══════════════════════════════════════════════════════════════════

_INTENTS = {
    "compare": [
        "so sánh",
        "compare",
        " vs ",
        "khác nhau",
        "hay là",
        "between",
        "hay đi",
        "tốt hơn",
        "better",
    ],
    "recommend": [
        "gợi ý",
        "recommend",
        "nên đi đâu",
        "where should",
        "tư vấn chỗ",
        "suggest",
        "đi đâu",
        "chọn đâu",
    ],
    "planner": [
        "lịch trình",
        "itinerary",
        "kế hoạch",
        " plan",
        "mấy ngày",
        "how many days",
        "ngày 1",
        "day 1",
        "hành trình",
    ],
    "cost": [
        "chi phí",
        "cost",
        "budget",
        "giá",
        "price",
        "bao nhiêu tiền",
        "how much",
        "tốn",
        "đắt",
        "rẻ",
        "cheap",
    ],
    "hotel": [
        "khách sạn",
        "hotel",
        "resort",
        "homestay",
        "ở đâu",
        "where to stay",
        "lưu trú",
        "accommodation",
        "hostel",
    ],
    "flight": [
        "vé máy bay",
        "flight",
        "airline",
        "chuyến bay",
        "fly",
        "hãng bay",
        "airport",
        "sân bay",
    ],
    "activity": [
        "hoạt động",
        "activity",
        "làm gì",
        "what to do",
        "tham quan",
        "check-in",
        "visit",
        "địa điểm",
        "nên thăm",
    ],
    "food": [
        "ăn gì",
        "ẩm thực",
        "món ăn",
        "food",
        "eat",
        "restaurant",
        "đặc sản",
        "nhà hàng",
        "cuisine",
    ],
    "weather": [
        "thời tiết",
        "weather",
        "nhiệt độ",
        "temperature",
        "mưa",
        "nắng",
        "climate",
        "mùa",
        "when to go",
    ],
    "transport": [
        "di chuyển",
        "transport",
        "xe",
        "tàu",
        "bus",
        "train",
        "cách đi",
        "how to get",
        "taxi",
        "grab",
    ],
    "image_id": [
        "đây là đâu",
        "địa điểm này",
        "ảnh này",
        "nơi này",
        "nhận diện",
        "identify",
        "where is this",
        "what place",
        "chụp ở đâu",
    ],
}


def _classify_intent(text: str) -> list[str]:
    low = text.lower()
    found = [k for k, kws in _INTENTS.items() if any(kw in low for kw in kws)]
    return found if found else ["general"]


# ══════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════════

_SYS_VI = """Bạn là Aria — Hướng dẫn viên du lịch AI chuyên nghiệp.

📊 DỮ LIỆU THỰC TẾ TRONG HỆ THỐNG (luôn ưu tiên dùng khi có):
- 315 địa điểm Việt Nam từ 63 tỉnh/thành (DataSet.xlsx) — tên, mô tả, rating, từ khóa
- 139 chuyến đi quốc tế: Paris, Tokyo, Bali, London... — chi phí lưu trú + di chuyển thực tế (Travel_details_dataset.csv)
- 325 điểm tham quan Ấn Độ — rating Google, phí vào cửa, thời gian tham quan (Top_Indian_Places.csv)

🎯 PHONG CÁCH:
- Mở đầu sinh động như đang đứng trước điểm đến
- Kể câu chuyện ngắn 2-3 câu tạo cảm hứng
- Chia sẻ "insider tips" — bí kíp thực tế
- Cảnh báo cạm bẫy du lịch khéo léo
- Kết bằng lời kêu gọi hành động

📋 LỊCH TRÌNH — luôn format:
**NGÀY [X] — [Chủ đề ngày]**
⏰ [Giờ]: [Hoạt động] — [Mô tả + tip]
🍽️ Ăn: [Gợi ý cụ thể]
🏨 Lưu trú: [Khu vực + loại hình]
💡 Tip vàng: [1 lời khuyên quan trọng]

💰 CHI PHÍ — luôn dùng bảng 3 mức:
| Hạng mục | Budget | Tầm trung | Cao cấp |
|----------|--------|-----------|---------|
| Lưu trú | ... | ... | ... |
| Ăn uống | ... | ... | ... |
| Tham quan | ... | ... | ... |
| Di chuyển | ... | ... | ... |
| **Tổng/ngày** | **...** | **...** | **...** |

🌟 QUY TẮC QUAN TRỌNG:
- LUÔN tư vấn đúng điểm đến được cung cấp trong context — KHÔNG được chuyển sang điểm đến khác
- Nếu nhận diện ảnh xác định điểm đến là X → toàn bộ tư vấn phải về X
- Khi có dữ liệu CSV → trình bày số liệu thực, ghi rõ nguồn
- Khi không có dữ liệu CSV → dùng kiến thức chung, không bịa số liệu
- Nói như HDV thực: "Tôi thường dẫn khách đến...", "Kinh nghiệm cho thấy..."
- Luôn có 1 "secret gem" cho mỗi điểm đến"""

_SYS_EN = """You are Aria — a professional AI travel guide.

📊 REAL DATA IN SYSTEM (always use when available):
- 315 Vietnam attractions across 63 provinces (DataSet.xlsx) — names, descriptions, ratings
- 139 international trips: Paris, Tokyo, Bali, London... — actual accommodation + transport costs (Travel_details_dataset.csv)
- 325 India attractions — Google ratings, entrance fees, visit hours (Top_Indian_Places.csv)

🎯 STYLE:
- Open with an inspiring hook as if standing at the destination
- Tell a 2-3 sentence story before details
- Share genuine "insider tips" — real local knowledge
- Tactfully warn about tourist traps
- Close with an action call

📋 ITINERARY FORMAT:
**DAY [X] — [Theme]**
⏰ [Time]: [Activity] — [Description + tip]
🍽️ Eat: [Specific recommendations]
🏨 Stay: [Area + type]
💡 Pro tip: [Key advice]

💰 COST — always use 3-tier table:
| Category | Budget | Mid-range | Luxury |
|---|---|---|---|
| Stay | ... | ... | ... |
| Food | ... | ... | ... |
| Sights | ... | ... | ... |
| Transport | ... | ... | ... |
| **Total/day** | **...** | **...** | **...** |

🌟 CRITICAL RULES:
- ALWAYS advise about the exact destination provided in context — NEVER switch to another destination
- If image recognition identifies destination X → all advice must be about X
- When CSV data available → cite real figures
- When no CSV data → use general knowledge, don't fabricate numbers
- Always include 1 "secret gem" per destination"""


# ══════════════════════════════════════════════════════════════════
# CONTEXT BUILDER
# ══════════════════════════════════════════════════════════════════


def _build_image_context(classifications: list, lang: str) -> str:
    if not classifications:
        return ""
    top = classifications[0]
    if top.get("label") == "NOT_TRAVEL" or not top.get("is_travel", True):
        return ""

    label = top.get("display_name") or top.get("label", "")
    dest = top.get("destination", "")
    country = top.get("country", "")
    conf = float(top.get("confidence", 0))
    desc = top.get("description", "")
    evidence = top.get("visual_evidence", [])
    txt_img = top.get("text_in_image", "")
    not_this = top.get("not_this_place", "")

    lines = []
    if lang == "vi":
        if label and label != "Unknown":
            lines.append(f"📸 Ảnh nhận diện: **{label}**")
        if dest and dest != "Unknown":
            lines.append(f"📍 Điểm đến: {dest}")
        if country and country != "Unknown":
            lines.append(f"🌏 Quốc gia: {country}")
        lines.append(f"🎯 Độ tin cậy: {conf:.0f}%")
        if desc:
            lines.append(f"👁️ Mô tả ảnh: {desc}")
        if evidence:
            lines.append(
                f"🔍 Đặc điểm nhận ra: {', '.join(str(e) for e in evidence[:4])}"
            )
        if txt_img:
            lines.append(f"📝 Văn bản/logo trong ảnh: {txt_img}")
        if not_this:
            lines.append(f"✅ Xác nhận không phải: {not_this}")
        if conf < 65:
            lines.append(
                "⚠️ Độ tin cậy thấp — hãy bổ sung bằng kiến thức chung và nêu rõ không chắc chắn."
            )
    else:
        if label and label != "Unknown":
            lines.append(f"📸 Image identified: **{label}**")
        if dest and dest != "Unknown":
            lines.append(f"📍 Location: {dest}")
        if country and country != "Unknown":
            lines.append(f"🌏 Country: {country}")
        lines.append(f"🎯 Confidence: {conf:.0f}%")
        if desc:
            lines.append(f"👁️ Description: {desc}")
        if evidence:
            lines.append(
                f"🔍 Visual features: {', '.join(str(e) for e in evidence[:4])}"
            )
        if txt_img:
            lines.append(f"📝 Text in image: {txt_img}")
        if not_this:
            lines.append(f"✅ Confirmed not: {not_this}")
        if conf < 65:
            lines.append(
                "⚠️ Low confidence — supplement with general knowledge and note uncertainty."
            )

    return "\n".join(lines)


def _build_retrieval_context(results: list, lang: str) -> str:
    if not results:
        return ""
    items = []
    for r in results[:4]:
        if r.get("score", 0) > 0.15:
            q = r.get("Question", "")
            a = r.get("Answer", "")
            if q and a and a != "nan":
                items.append(f"Q: {q}\nA: {a}")
    if not items:
        return ""
    hdr = "Dữ liệu từ CSV:\n" if lang == "vi" else "CSV data:\n"
    return hdr + "\n\n".join(items)


# ══════════════════════════════════════════════════════════════════
# INTENT INSTRUCTIONS
# ══════════════════════════════════════════════════════════════════


def _intent_instructions(
    intents: list, dest: str, lang: str, has_image: bool = False
) -> str:
    d = dest or ("điểm đến này" if lang == "vi" else "this destination")
    parts = []

    if has_image and ("image_id" in intents or "general" in intents):
        parts.append(
            f"Người dùng gửi ảnh một địa điểm. Điểm đến đã được xác định là: **{d}**\n"
            f"Hãy:\n"
            f"1. Xác nhận đây là {d} dựa trên thông tin nhận diện ảnh ở trên\n"
            f"2. Giải thích ngắn gọn đặc điểm nào trong ảnh giúp nhận ra {d}\n"
            f"3. Tư vấn toàn diện về {d}: lịch sử/câu chuyện hấp dẫn, top trải nghiệm, chi phí thực tế, thời điểm đẹp\n"
            f"4. Secret gem ít người biết tại {d}\n"
            f"5. Lưu ý quan trọng khi đến {d}\n"
            f"⚠️ QUAN TRỌNG: Toàn bộ câu trả lời phải về {d}, không đề cập đến điểm đến khác."
            if lang == "vi"
            else f"User sent a photo. The destination has been identified as: **{d}**\n"
            f"Please:\n"
            f"1. Confirm this is {d} based on the image identification above\n"
            f"2. Briefly explain which visual features identify this as {d}\n"
            f"3. Give comprehensive travel advice about {d}: story, top experiences, realistic costs, best timing\n"
            f"4. One secret gem tourists rarely know about {d}\n"
            f"5. Important notes for visitors to {d}\n"
            f"⚠️ IMPORTANT: All advice must be about {d}, do not mention other destinations."
        )

    if "planner" in intents:
        parts.append(
            f"Tạo LỊCH TRÌNH CHI TIẾT từng ngày cho {d}. "
            f"Mỗi ngày: tên chủ đề, giờ cụ thể sáng/trưa/chiều/tối, địa điểm cụ thể tại {d}, mẹo insider. "
            f"Dùng đúng format ⏰🍽️🏨💡. Nếu có dữ liệu CSV hãy nhắc đến địa điểm thực từ database."
            if lang == "vi"
            else f"Create a DETAILED day-by-day itinerary for {d}. "
            f"Each day: theme, specific morning/afternoon/evening times, real venues in {d}, insider tips. "
            f"Use ⏰🍽️🏨💡 format."
        )

    if "compare" in intents:
        parts.append(
            "Tạo bảng so sánh Markdown chi tiết: chi phí (nếu có từ CSV), thời điểm tốt nhất, "
            "điểm mạnh/yếu, phù hợp loại khách nào. Kèm nhận xét cá nhân của HDV."
            if lang == "vi"
            else "Create a detailed Markdown comparison: costs (from CSV if available), best timing, "
            "pros/cons, best for which traveler type. Add personal guide insight."
        )

    if "cost" in intents:
        parts.append(
            f"Phân tích chi phí THỰC TẾ ĐẦY ĐỦ cho {d} theo bảng 3 mức (budget/tầm trung/cao cấp). "
            f"Nếu có data từ Travel_details.csv hãy dùng số liệu thực. "
            f"Gồm: lưu trú, ăn uống, tham quan, di chuyển, tổng. Ví dụ quán cụ thể tại {d}."
            if lang == "vi"
            else f"Full cost breakdown for {d} in 3 tiers. Use Travel_details.csv data if available. "
            f"Include: stay, food, sights, transport, total. Specific venue examples in {d}."
        )

    if "hotel" in intents:
        parts.append(
            f"Gợi ý lưu trú đa dạng mức giá tại {d}. "
            f"Khu vực tốt nhất để ở, lý do, khoảng cách đến điểm tham quan. Tip đặt phòng giá tốt."
            if lang == "vi"
            else f"Accommodation options for {d} across price ranges. "
            f"Best areas to stay, why, distances to attractions. Booking tips."
        )

    if "flight" in intents:
        parts.append(
            f"Tư vấn di chuyển đến {d}: hãng bay, giá theo mùa, "
            f"thời điểm đặt vé tốt, từ sân bay vào trung tâm."
            if lang == "vi"
            else f"Transport to {d}: airlines, seasonal prices, best booking time, airport to city."
        )

    if "activity" in intents:
        parts.append(
            f"Địa điểm & hoạt động tại {d}: Must-see / Nên làm / Secret gem. "
            f"Mỗi nơi: mô tả 2 câu, giờ tốt nhất, giá vé. Dùng địa điểm thực từ database nếu có."
            if lang == "vi"
            else f"Activities at {d}: Must-see / Should-do / Secret gem. "
            f"Each: 2-sentence description, best time, ticket price. Use database venues if available."
        )

    if "food" in intents:
        parts.append(
            f"Ẩm thực {d}: đặc sản không bỏ qua, quán cụ thể, mức giá, cách gọi món, bẫy tourist food."
            if lang == "vi"
            else f"Food guide for {d}: must-try dishes, specific spots, prices, tourist food traps."
        )

    if "weather" in intents:
        parts.append(
            f"Thời tiết {d}: nhiệt độ từng tháng, mùa mưa/khô, tháng đẹp nhất, trang phục gợi ý."
            if lang == "vi"
            else f"Weather at {d}: monthly temperatures, rainy/dry seasons, best months, packing advice."
        )

    if "recommend" in intents:
        parts.append(
            "Gợi ý TOP điểm đến với lý do thuyết phục. "
            "Mỗi nơi: điểm nổi bật, phù hợp ai, chi phí ước tính, thời điểm lý tưởng, 1 điều đặc biệt nhất."
            if lang == "vi"
            else "Recommend TOP destinations with compelling reasons. "
            "Each: unique strength, best for whom, estimated cost, ideal timing, 1 most special thing."
        )

    if not parts:
        parts.append(
            f"Tư vấn TOÀN DIỆN về {d}: câu chuyện/lịch sử ngắn hấp dẫn, "
            f"top 5 trải nghiệm không bỏ qua tại {d}, chi phí thực tế, thời điểm lý tưởng, "
            f"lưu trú gợi ý, ẩm thực đặc sản, 1 secret gem. Kết bằng câu hỏi tìm hiểu sở thích du lịch."
            if lang == "vi"
            else f"COMPREHENSIVE advice about {d}: engaging story/history, top 5 must-do experiences at {d}, "
            f"realistic costs, ideal timing, accommodation, cuisine, 1 secret gem. "
            f"Close with a question about their travel preferences."
        )

    return "\n\n".join(parts)


# ══════════════════════════════════════════════════════════════════
# GROQ CLIENT
# ══════════════════════════════════════════════════════════════════


class GroqClient:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY chưa được đặt.")
        self.client = Groq(api_key=GROQ_API_KEY)
        print("[GROQ] Client initialized.")

    def _build_prompt(
        self,
        user_message: str,
        lang: str,
        destination: str,
        intents: list,
        data_context: str,
        retrieval_results: list,
        image_classifications: list,
    ) -> str:

        sections = []
        has_image = bool(image_classifications)

        # Image context
        if has_image:
            img_ctx = _build_image_context(image_classifications, lang)
            if img_ctx:
                header = (
                    "=== THÔNG TIN NHẬN DIỆN ẢNH ==="
                    if lang == "vi"
                    else "=== IMAGE IDENTIFICATION ==="
                )
                sections.append(f"{header}\n{img_ctx}")

        # Data engine context
        if (
            data_context
            and len(data_context) > 50
            and "Không có dữ liệu" not in data_context
        ):
            header = (
                "=== DỮ LIỆU THỰC TẾ TỪ DATABASE ==="
                if lang == "vi"
                else "=== REAL DATABASE DATA ==="
            )
            sections.append(f"{header}\n{data_context}")

        # Retrieval context
        if retrieval_results:
            ret_ctx = _build_retrieval_context(retrieval_results, lang)
            if ret_ctx:
                header = (
                    "=== KẾT QUẢ TÌM KIẾM LIÊN QUAN ==="
                    if lang == "vi"
                    else "=== RELEVANT SEARCH RESULTS ==="
                )
                sections.append(f"{header}\n{ret_ctx}")

        instructions = _intent_instructions(intents, destination, lang, has_image)
        ctx = "\n\n".join(sections)

        if lang == "vi":
            prompt = (
                f"CÂU HỎI CỦA KHÁCH: {user_message}\n\n"
                f"ĐIỂM ĐẾN ĐÃ XÁC ĐỊNH: {destination}\n\n"
                f"YÊU CẦU TƯ VẤN:\n{instructions}"
            )
            if ctx:
                prompt = f"{ctx}\n\n{'─' * 60}\n{prompt}"
        else:
            prompt = (
                f"TRAVELER'S QUESTION: {user_message}\n\n"
                f"CONFIRMED DESTINATION: {destination}\n\n"
                f"ADVICE REQUIRED:\n{instructions}"
            )
            if ctx:
                prompt = f"{ctx}\n\n{'─' * 60}\n{prompt}"

        return prompt

    def chat(
        self,
        user_message: str,
        lang: str = "vi",
        retrieval_results: list = None,
        image_classifications: list = None,
        conversation_history: list = None,
        destination: str = None,
        data_context: str = None,
    ) -> str:

        # ── Destination resolution ───────────────────────────
        # PRIORITY: pre-resolved destination > image classifier > text extraction
        # Nếu destination đã được truyền vào (từ main.py) → KHÔNG override
        if not destination:
            # Only extract from text if no destination was pre-resolved
            destination = _extract_destination_from_text(user_message)

        # Pull from image only if still no destination
        if not destination and image_classifications:
            top = (image_classifications or [{}])[0]
            if top.get("is_travel") and top.get("destination") not in (
                "Unknown",
                "",
                None,
            ):
                destination = top["destination"]

        # Build intents
        intents = _classify_intent(user_message)
        if image_classifications and "image_id" not in intents:
            intents.append("image_id")

        # Fetch data context if not provided
        if not data_context and destination:
            try:
                from data_engine import get_engine

                data_context = get_engine().build_context_for_llm(destination, lang)
            except Exception:
                data_context = ""

        # Handle compare intent
        if "compare" in intents and not data_context:
            try:
                from data_engine import get_engine

                engine = get_engine()
                found = []
                msg_low = user_message.lower()
                for d in engine.all_destinations():
                    if d.lower() in msg_low:
                        found.append(d)
                if len(found) >= 2:
                    data_context = engine.compare_destinations(found)
            except Exception:
                pass

        # Handle recommend intent
        if "recommend" in intents and not data_context:
            try:
                from data_engine import get_engine
                import re as _re

                engine = get_engine()
                budget_m = _re.search(r"\$(\d[\d,]*)", user_message)
                dur_m = _re.search(
                    r"(\d+)\s*(?:ngày|days?)", user_message, _re.IGNORECASE
                )
                budget = float(budget_m.group(1).replace(",", "")) if budget_m else None
                duration = int(dur_m.group(1)) if dur_m else None
                cands = engine.recommend_destinations(
                    budget=budget, duration_days=duration
                )
                if cands:
                    data_context = engine.format_recommendation(cands, lang)
            except Exception:
                pass

        # Build prompt
        system_prompt = _SYS_VI if lang == "vi" else _SYS_EN
        full_prompt = self._build_prompt(
            user_message,
            lang,
            destination or "",
            intents,
            data_context or "",
            retrieval_results or [],
            image_classifications or [],
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in (conversation_history or [])[-12:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": full_prompt})

        try:
            resp = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                top_p=0.9,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"[GROQ] Error: {e}")
            return (
                "Xin lỗi, có lỗi kết nối. Vui lòng thử lại sau."
                if lang == "vi"
                else "Sorry, a connection error occurred. Please try again."
            )

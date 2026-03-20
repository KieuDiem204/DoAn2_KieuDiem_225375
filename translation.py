"""
translation.py — Hỗ trợ đa ngôn ngữ (Vietnamese ↔ English).
Không dùng API ngoài — chỉ dùng dictionaries từ-khái niệm cố định
kết hợp với Groq để translate dynamically khi cần.
"""
from config import GROQ_API_KEY, GROQ_MODEL

# ──────────────────────────────────────────
# Static keyword dictionaries (cả hai chiều)
# ──────────────────────────────────────────
EN_TO_VI = {
    # Destinations
    "beach":                "bãi biển",
    "mountain":             "núi",
    "city":                 "thành phố",
    "countryside":          "nông thôn",
    "island":               "đảo",
    "temple":               "chùa",
    "pagoda":               "chùa",
    "museum":               "bảo tàng",
    "park":                 "công viên",
    "lake":                 "hồ",
    "waterfall":            "thác nước",
    "cave":                 "hang động",
    "palace":               "cung điện",
    "fortress":             "pháo đài",
    "historical site":      "di tích lịch sử",
    
    # Countries & Cities
    "vietnam":              "Việt Nam",
    "thailand":             "Thái Lan",
    "japan":                "Nhật Bản",
    "korea":                "Hàn Quốc",
    "singapore":            "Singapore",
    "hanoi":                "Hà Nội",
    "saigon":               "Sài Gòn",
    "ho chi minh city":     "Thành phố Hồ Chí Minh",
    "da nang":              "Đà Nẵng",
    "hoi an":               "Hội An",
    "nha trang":            "Nha Trang",
    "hue":                  "Huế",
    "dalat":                "Đà Lạt",
    "phu quoc":             "Phú Quốc",
    "ha long":              "Hạ Long",
    "sapa":                 "Sa Pa",
    
    # Travel terms
    "hotel":                "khách sạn",
    "resort":               "khu nghỉ dưỡng",
    "flight":               "chuyến bay",
    "ticket":               "vé",
    "booking":              "đặt phòng",
    "reservation":          "đặt chỗ",
    "tour":                 "tour du lịch",
    "guide":                "hướng dẫn viên",
    "itinerary":            "lịch trình",
    "package":              "gói du lịch",
    "budget":               "ngân sách",
    "luxury":               "cao cấp",
    "backpacking":          "du lịch balo",
    "sightseeing":          "tham quan",
    "adventure":            "phiêu lưu",
    "culture":              "văn hóa",
    "cuisine":              "ẩm thực",
    "local food":           "món ăn địa phương",
    "souvenir":             "quà lưu niệm",
    "shopping":             "mua sắm",
    "nightlife":            "sinh hoạt về đêm",
    
    # Seasons
    "summer":               "mùa hè",
    "winter":               "mùa đông",
    "spring":               "mùa xuân",
    "autumn":               "mùa thu",
    "rainy season":         "mùa mưa",
    "dry season":           "mùa khô",
    
    # Activities
    "swimming":             "bơi lội",
    "diving":               "lặn biển",
    "hiking":               "leo núi",
    "trekking":             "đi bộ đường dài",
    "camping":              "cắm trại",
    "photography":          "chụp ảnh",
    "cruise":               "du thuyền",
    
    # General terms
    "weather":              "thời tiết",
    "temperature":          "nhiệt độ",
    "visa":                 "visa",
    "passport":             "hộ chiếu",
    "currency":             "tiền tệ",
    "exchange rate":        "tỷ giá",
    "tip":                  "tiền boa",
    "price":                "giá",
    "cost":                 "chi phí",
    "expensive":            "đắt",
    "cheap":                "rẻ",
    "affordable":           "phải chăng",
}

# Reverse mapping
VI_TO_EN = {v: k for k, v in EN_TO_VI.items()}


def detect_language(text: str) -> str:
    """
    Simple heuristic: nếu text chứa nhiều ký tự diacritical marks → Vietnamese.
    Ngược lại → English.
    """
    vi_chars = set("àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợỏỡùúụủũưừứựỳýỵỷỹđ"
                   "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỎỠÙÚỤỦŨƯỪỨỰỲÝỴỶỸĐ")
    vi_count = sum(1 for c in text if c in vi_chars)
    alpha_count = sum(1 for c in text if c.isalpha())
    if alpha_count == 0:
        return "vi"
    ratio = vi_count / alpha_count
    return "vi" if ratio > 0.04 else "en"


def translate_label_to_vi(label: str) -> str:
    """Translate a location/type label → tiếng Việt."""
    label_clean = label.strip().lower()
    
    # Direct match
    if label_clean in EN_TO_VI:
        return EN_TO_VI[label_clean]
    
    # Partial match
    for en_key, vi_val in EN_TO_VI.items():
        if en_key in label_clean:
            return vi_val
    
    return label


def translate_label_to_en(label: str) -> str:
    """Ensure label is in English format."""
    label_clean = label.strip().lower()
    
    # Direct match
    if label_clean in VI_TO_EN:
        return VI_TO_EN[label_clean]
    
    # Partial match
    for vi_key, en_val in VI_TO_EN.items():
        if vi_key in label_clean:
            return en_val
    
    return label


def get_system_prompt(lang: str) -> str:
    """Return system prompt in the selected language."""
    from config import SYSTEM_PROMPT_VI, SYSTEM_PROMPT_EN
    return SYSTEM_PROMPT_VI if lang == "vi" else SYSTEM_PROMPT_EN


def format_destination_info(destination: str, category: str, confidence: float, lang: str) -> str:
    """Format destination detection info in selected language."""
    if lang == "vi":
        dest_vi = translate_label_to_vi(destination)
        cat_vi = translate_label_to_vi(category)
        return (
            f"🏖️ **Địa điểm:** {dest_vi}\n"
            f"🔍 **Loại:** {cat_vi}\n"
            f"📊 **Độ chắc chắn:** {confidence:.1f}%"
        )
    else:
        return (
            f"🏖️ **Destination:** {destination}\n"
            f"🔍 **Category:** {category}\n"
            f"📊 **Confidence:** {confidence:.1f}%"
        )
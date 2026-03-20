"""
main.py — TravelBot AI — Aria Premium Travel Advisor
Version 6.1 — Fix: destination resolution priority (image > text)
"""

import os, sys, warnings, base64, io
import streamlit as st
from PIL import Image

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import GROQ_API_KEY
from translation import detect_language

st.set_page_config(
    page_title="Aria — Travel Advisor",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# PREMIUM CSS
# ══════════════════════════════════════════════════════════════
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --cream: #f5f0e8; --warm-white: #faf8f4; --sand: #e8ddd0;
    --terracotta: #c4845a; --deep-teal: #1a3a3a; --teal: #2d5555;
    --gold: #b8965a; --gold-light: #d4b07a; --dark-ink: #1c1410;
    --muted: #7a6e64; --border: rgba(184,150,90,0.2);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    font-family: 'DM Sans', sans-serif !important;
    background: #faf8f4 !important; color: #1c1410;
}
[data-testid="stAppViewContainer"] { display: flex !important; flex-direction: row !important; min-height: 100vh; }
[data-testid="stMain"] { flex: 1 !important; min-width: 0 !important; background: #faf8f4 !important; }
.main, .main > div { background: #faf8f4 !important; }
.block-container { max-width: 860px; margin: 0 auto; padding: 20px 24px 40px; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    display: block !important; visibility: visible !important;
    opacity: 1 !important; width: 256px !important;
    min-width: 256px !important; max-width: 256px !important;
    background: #1a3a3a !important; transform: none !important;
    position: relative !important; left: 0 !important;
    flex-shrink: 0 !important; z-index: 999 !important;
    overflow: hidden !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background: #1a3a3a !important; padding: 14px 12px 24px !important;
    overflow-y: auto !important; min-height: 100vh !important; width: 100% !important;
}
section[data-testid="stSidebar"] * { color: #f5f0e8 !important; }
[data-testid="collapsedControl"] { display: none !important; }

.sidebar-section {
    font-size: 0.59rem !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; color: #d4b07a !important;
    font-weight: 700 !important; margin: 13px 0 6px !important;
    padding-bottom: 5px !important; border-bottom: 1px solid rgba(184,150,90,0.2) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important; background: rgba(245,240,232,0.07) !important;
    color: rgba(245,240,232,0.82) !important;
    border: 1px solid rgba(184,150,90,0.18) !important;
    border-radius: 7px !important; font-size: 0.76rem !important;
    text-align: left !important; height: auto !important;
    min-height: 33px !important; padding: 6px 10px !important;
    margin: 2px 0 !important; box-shadow: none !important;
    transform: none !important; font-weight: 400 !important;
    white-space: normal !important; word-wrap: break-word !important; line-height: 1.35 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(196,132,90,0.18) !important; color: white !important;
    border-color: rgba(196,132,90,0.4) !important; transform: none !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
    border-radius: 8px !important; border: 1.5px dashed rgba(184,150,90,0.42) !important;
    background: rgba(245,240,232,0.05) !important; padding: 10px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section p { font-size: 0.72rem !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section button {
    background: rgba(196,132,90,0.18) !important; color: #d4b07a !important;
    border: 1px solid rgba(184,150,90,0.35) !important; border-radius: 5px !important;
    font-size: 0.72rem !important; padding: 3px 10px !important;
    height: auto !important; min-height: 26px !important;
    box-shadow: none !important; transform: none !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(184,150,90,0.18) !important; margin: 8px 0 !important; }

/* HEADER */
.header-section { text-align: center; padding: 18px 0 14px; border-bottom: 1px solid rgba(184,150,90,0.2); margin-bottom: 14px; }
.header-ornament { font-size: 0.68rem; color: #b8965a; letter-spacing: 8px; margin-bottom: 10px; font-weight: 300; }
.header-brand { font-family: 'Cormorant Garamond', serif; font-size: 2.5rem; font-weight: 300; color: #1a3a3a; letter-spacing: -1px; line-height: 1; margin-bottom: 4px; }
.header-brand span { color: #c4845a; font-style: italic; }
.header-tagline { font-size: 0.67rem; color: #7a6e64; letter-spacing: 3px; text-transform: uppercase; }

/* STATS */
.stats-row { display: flex; justify-content: center; gap: 22px; margin-bottom: 14px; padding: 8px 0; }
.stat-item { text-align: center; }
.stat-number { font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; font-weight: 500; color: #c4845a; line-height: 1; }
.stat-label { font-size: 0.59rem; color: #7a6e64; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 3px; }
.stat-divider { width: 1px; background: rgba(184,150,90,0.2); align-self: stretch; }

/* CHAT */
.chat-container { background: transparent; max-height: 580px; overflow-y: auto; margin-bottom: 10px; padding: 2px 0; scroll-behavior: smooth; }
.chat-container::-webkit-scrollbar { width: 3px; }
.chat-container::-webkit-scrollbar-thumb { background: #e8ddd0; border-radius: 2px; }

.msg-row-user { display: flex; flex-direction: row-reverse; align-items: flex-end; gap: 8px; margin-bottom: 12px; }
.msg-row-bot  { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 14px; }
.avatar-user  { width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg,#c4845a,#b8965a); display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; color: white; font-weight: 700; }
.avatar-bot   { width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg,#1a3a3a,#3d6e6e); display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.bubble-user  { max-width: 62%; background: linear-gradient(135deg,#c4845a,#b87050); color: white; padding: 10px 15px; border-radius: 14px 4px 14px 14px; font-size: 0.87rem; line-height: 1.6; box-shadow: 0 2px 10px rgba(196,132,90,0.22); word-wrap: break-word; }
.bubble-bot   { width: 100%; background: white; border: 1px solid rgba(184,150,90,0.2); padding: 14px 18px; border-radius: 4px 14px 14px 14px; font-size: 0.87rem; line-height: 1.75; color: #1c1410; word-wrap: break-word; box-shadow: 0 2px 10px rgba(28,20,16,0.05); }
.bot-label    { font-size: 0.59rem; color: #b8965a; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px; font-weight: 600; }

/* EXPORT BAR */
.export-bar-wrapper {
    margin: 6px 0 14px 38px;
    padding: 10px 14px;
    background: white;
    border: 1px solid rgba(184,150,90,0.18);
    border-radius: 10px;
    box-shadow: 0 1px 6px rgba(28,20,16,0.04);
}
.export-bar-label {
    font-size: 0.58rem; letter-spacing: 2px; text-transform: uppercase;
    color: #b8965a; font-weight: 700; margin-bottom: 8px;
}
.export-bar-wrapper .stButton > button {
    background: #faf8f4 !important;
    color: #1a3a3a !important;
    border: 1px solid rgba(184,150,90,0.28) !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    height: 36px !important;
    padding: 0 10px !important;
    box-shadow: none !important;
    transform: none !important;
    transition: all 0.15s ease !important;
}
.export-bar-wrapper .stButton > button:hover {
    background: rgba(196,132,90,0.1) !important;
    border-color: #c4845a !important;
    color: #c4845a !important;
    transform: none !important;
}

/* INPUT */
.input-divider { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; opacity: 0.5; }
.input-divider::before, .input-divider::after { content: ''; flex: 1; height: 1px; background: rgba(184,150,90,0.2); }
.input-divider-icon { font-size: 0.65rem; color: #b8965a; letter-spacing: 3px; }

[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] input {
    background: white !important; border: 1.5px solid rgba(184,150,90,0.22) !important;
    border-radius: 11px !important; color: #1c1410 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.87rem !important;
    padding: 10px 15px !important; height: 46px !important;
    box-shadow: 0 2px 6px rgba(28,20,16,0.04) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #c4845a !important;
    box-shadow: 0 0 0 3px rgba(196,132,90,0.1) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: #b0a898 !important; font-style: italic; }
[data-testid="stTextInput"] > div { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }

/* SEND BUTTON */
.stButton > button {
    background: linear-gradient(150deg,#c4845a 0%,#a06840 100%) !important;
    color: white !important; border: none !important; border-radius: 11px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 0.85rem !important; height: 46px !important;
    padding: 0 18px !important; transition: all 0.18s ease !important;
    box-shadow: 0 3px 12px rgba(196,132,90,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(150deg,#d4967a 0%,#c4845a 100%) !important;
    transform: translateY(-1px) !important;
}

/* DOWNLOAD BUTTON */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg,#2d5555,#1a3a3a) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-size: 0.78rem !important;
    height: 34px !important; padding: 0 14px !important;
    font-weight: 600 !important; box-shadow: none !important;
    transform: none !important;
}

#MainMenu, footer, .stDeployButton, .stStatusWidget, header { display: none !important; }
div.stSpinner > div { border-top-color: #c4845a !important; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """<script>
(function(){
    function fix(){
        var s=document.querySelector('section[data-testid="stSidebar"]');
        if(s){s.style.cssText+='display:flex!important;visibility:visible!important;opacity:1!important;transform:none!important;width:290px!important;min-width:290px!important;left:0!important;';}
        document.querySelectorAll('[data-testid="collapsedControl"]').forEach(function(x){x.style.display='none';});
    }
    fix();setTimeout(fix,200);setTimeout(fix,600);setTimeout(fix,1500);
    new MutationObserver(fix).observe(document.body,{childList:true,subtree:true});
})();
</script>""",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
_DEFAULTS = {
    "messages": [],
    "lang": "vi",
    "groq_client": None,
    "retrieval_engine": None,
    "image_classifier": None,
    "data_engine": None,
    "input_counter": 0,
    "_cached_classifications": None,
    "_cached_destination": "",
    "_cached_image_b64": "",
    "conversation_history": [],
    "_export_show": {},
    "_export_pdf_itin": {},
    "_export_pdf_plan": {},
    "_export_docx": {},
    "_export_xlsx": {},
    # Hotel map cache — keyed by destination|lang
    "_hotel_map_cache": {},
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════
# RESOURCE LOADERS
# ══════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_data_engine():
    from data_engine import get_engine

    return get_engine()


@st.cache_resource(show_spinner=False)
def load_dataset_cached():
    from data_processing import load_dataset

    return load_dataset()


@st.cache_resource(show_spinner=False)
def load_retrieval_engine(df):
    from recommendation import RetrievalEngine

    return RetrievalEngine(df)


@st.cache_resource(show_spinner=False)
def load_image_classifier():
    from image_classifier import ImageClassifier

    return ImageClassifier()


@st.cache_resource(show_spinner=False)
def load_groq_client():
    from groq_client import GroqClient

    return GroqClient()


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def get_lang():
    return st.session_state["lang"]


def _pil_to_b64(img: Image.Image, max_size=160) -> str:
    img2 = img.copy()
    img2.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img2.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _welcome_text(lang):
    if lang == "vi":
        return (
            "Xin chào! Tôi là **Aria** — hướng dẫn viên du lịch AI của bạn, với hơn 15 năm kinh nghiệm "
            "dẫn tour khắp Việt Nam và thế giới.\n\n"
            "Tôi ở đây để giúp bạn lên kế hoạch cho chuyến đi hoàn hảo — từ lịch trình chi tiết, "
            "chi phí thực tế, gợi ý ăn uống, đến những **'bí mật địa phương'** mà chỉ hướng dẫn viên "
            "chuyên nghiệp mới biết.\n\n"
            "🌤️ Tôi cũng có thể cho bạn biết **thời tiết hiện tại** tại điểm đến và gợi ý **các link "
            "đặt tour uy tín** ngay trong cuộc trò chuyện!\n\n"
            "📄 Sau mỗi câu trả lời, bạn có thể **xuất lịch trình / kế hoạch / chi phí** ra file "
            "PDF, Word hoặc Excel ngay lập tức.\n\n"
            "*Bạn đang nghĩ đến điểm đến nào? Hãy kể cho tôi nghe!*"
        )
    return (
        "Hello! I'm **Aria** — your AI tour guide with 15+ years of experience across Vietnam and the world.\n\n"
        "I'm here to help you plan the perfect trip — from detailed itineraries and real costs to dining "
        "gems and **local secrets** only a professional guide would know.\n\n"
        "🌤️ I can also show you **real-time weather** at your destination and suggest **trusted booking "
        "links** right here in our chat!\n\n"
        "📄 After each response, you can instantly **export itineraries, plans, or cost tables** to "
        "PDF, Word, or Excel.\n\n"
        "*Where are you dreaming of going? Tell me!*"
    )


def add_welcome():
    lang = get_lang()
    st.session_state["messages"] = [
        {
            "role": "bot",
            "content": _welcome_text(lang),
            "card_html": "",
            "img_preview_html": "",
            "weather_html": "",
            "tour_html": "",
            "hotel_map_data": None,
            "itinerary_html": "",
            "destination": "",
        }
    ]
    st.session_state["conversation_history"] = []


# ══════════════════════════════════════════════════════════════
# DESTINATION RESOLUTION — FIX CORE
# Ưu tiên: image classifier canonical dest > text extraction
# ══════════════════════════════════════════════════════════════
def _resolve_destination_from_classifications(classifications: list) -> str:
    """
    Trích xuất canonical destination từ kết quả image classifier.
    Ưu tiên field 'destination' (đã được normalize trong _build()),
    không dùng province/tỉnh thô.
    """
    if not classifications:
        return ""
    top = classifications[0]
    if not top.get("is_travel", True):
        return ""

    # destination field từ classifier đã được map qua _build()
    dest = str(top.get("destination", "")).strip()

    if not dest or dest in ("Unknown", "nan", ""):
        return ""

    # Map province names → canonical city (vì classifier đôi khi trả tỉnh)
    _PROVINCE_TO_CITY = {
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
        "Đà Nẵng": "Da Nang",
        "Da Nang": "Da Nang",
        "Hà Nội": "Hanoi",
        "Ha Noi": "Hanoi",
        "TP. Hồ Chí Minh": "Ho Chi Minh City",
        "Ho Chi Minh": "Ho Chi Minh City",
        "Bà Rịa - Vũng Tàu": "Vung Tau",
        "Ba Ria Vung Tau": "Vung Tau",
        "Bình Thuận": "Mui Ne",
        "Binh Thuan": "Mui Ne",
        "Quảng Nam": "Hoi An",
        "Quang Nam": "Hoi An",
        "Ninh Bình": "Ninh Binh",
        "Hà Giang": "Ha Giang",
        "Ha Giang": "Ha Giang",
        "Tây Ninh": "Tay Ninh",
        "Tay Ninh": "Tay Ninh",
    }

    canonical = _PROVINCE_TO_CITY.get(dest, dest)
    return canonical


def _resolve_destination(
    user_input: str,
    image_classifications: list,
    is_image_query: bool,
    is_followup_image_question: bool = False,
) -> str:
    """
    Quyết định destination cuối cùng.

    Logic ưu tiên:
    1. Image query (có ảnh upload) → dùng classifier result
    2. Text query có destination rõ ràng → dùng text extraction
    3. Text query là follow-up về ảnh (không có destination rõ) → dùng cached image dest
    4. Không tìm được → ""

    QUAN TRỌNG: Quick prompts / text queries có destination trong text
    KHÔNG được bị override bởi cached image destination.
    """
    from groq_client import _extract_destination_from_text

    # --- Path 1: Image query ---
    if is_image_query and image_classifications:
        img_dest = _resolve_destination_from_classifications(image_classifications)
        if img_dest and img_dest not in ("Unknown", ""):
            return img_dest
        text_dest = _extract_destination_from_text(user_input)
        if text_dest:
            return text_dest
        return img_dest or ""

    # --- Path 2: Text query ---
    text_dest = _extract_destination_from_text(user_input)
    if text_dest:
        # Text has explicit destination → use it, ignore any cached image dest
        return text_dest

    # --- Path 3: Follow-up image question (no explicit destination in text) ---
    # Only use cached image dest if the question seems to be about the previously shown image
    if is_followup_image_question:
        cached_cls = st.session_state.get("_cached_classifications")
        if cached_cls:
            cached_dest = _resolve_destination_from_classifications(cached_cls)
            if cached_dest and cached_dest not in ("Unknown", ""):
                return cached_dest

    return ""


def _is_followup_image_question(text: str) -> bool:
    """
    Kiểm tra câu hỏi có phải là follow-up về ảnh đã gửi trước đó không.
    Chỉ True khi câu hỏi KHÔNG có destination cụ thể VÀ
    có từ khóa gợi ý đang hỏi về ảnh/địa điểm đã nhận diện.
    """
    low = text.lower()
    followup_keywords = [
        "ảnh đó",
        "ảnh này",
        "địa điểm đó",
        "nơi đó",
        "nơi này",
        "ở đó",
        "chỗ đó",
        "đó",
        "nó",
        "ở đây",
        "that place",
        "this place",
        "there",
        "it",
        "here",
        "tell me more",
        "more about",
        "thêm về",
        "thêm thông tin",
    ]
    return any(kw in low for kw in followup_keywords)


# ══════════════════════════════════════════════════════════════
# CLASSIFY CARD
# ══════════════════════════════════════════════════════════════
def _classify_card(cls_list: list, lang: str) -> str:
    if not cls_list:
        return ""
    title = "Nhận diện địa điểm" if lang == "vi" else "Location Identified"
    top = cls_list[0]
    top_dest = str(top.get("destination", ""))
    top_label = str(top.get("display_name", top.get("label", "")))
    top_cat = str(top.get("category", ""))
    top_conf = float(top.get("confidence", 0))
    conf_color = (
        "#22c55e" if top_conf >= 80 else ("#f59e0b" if top_conf >= 55 else "#ef4444")
    )

    main_block = (
        '<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
        '<div style="position:relative;width:56px;height:56px;flex-shrink:0;">'
        '<svg viewBox="0 0 56 56" style="width:56px;height:56px;transform:rotate(-90deg);">'
        '<circle cx="28" cy="28" r="24" fill="none" stroke="rgba(0,0,0,0.07)" stroke-width="4"/>'
        '<circle cx="28" cy="28" r="24" fill="none" stroke="'
        + conf_color
        + '" stroke-width="4"'
        ' stroke-dasharray="'
        + str(round(150.796 * top_conf / 100, 1))
        + ' 150.796" stroke-linecap="round"/>'
        "</svg>"
        '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;line-height:1;">'
        '<div style="font-size:0.78rem;font-weight:800;color:'
        + conf_color
        + ';">'
        + str(round(top_conf))
        + "%</div>"
        "</div></div>"
        '<div style="flex:1;min-width:0;">'
        '<div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;color:#7a6e64;margin-bottom:3px;">'
        + title
        + "</div>"
        '<div style="font-size:1.0rem;font-weight:700;color:#1a3a3a;margin-bottom:2px;line-height:1.2;">'
        + top_label
        + "</div>"
        '<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">'
        '<span style="font-size:0.65rem;background:#e8f4f0;color:#2d5555;padding:2px 8px;border-radius:8px;font-weight:600;">'
        + top_cat
        + "</span>"
        '<span style="font-size:0.7rem;color:#c4845a;font-weight:600;">&#128205; '
        + top_dest
        + "</span>"
        "</div></div></div>"
    )
    other_rows = ""
    for i, c in enumerate(cls_list[1:3], 2):
        lbl = str(c.get("display_name", c.get("label", "")))
        cat = str(c.get("category", ""))
        conf = float(c.get("confidence", 0))
        bar = min(100, max(1, round(conf)))
        other_rows += (
            '<div style="display:flex;align-items:center;gap:10px;padding:5px 0;border-top:1px solid rgba(184,150,90,0.1);">'
            '<div style="width:18px;height:18px;border-radius:50%;background:rgba(26,58,58,0.08);display:flex;align-items:center;justify-content:center;font-size:0.6rem;font-weight:700;color:#7a6e64;flex-shrink:0;">'
            + str(i)
            + "</div>"
            '<div style="flex:1;min-width:0;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">'
            '<span style="font-size:0.75rem;font-weight:600;color:#1c1410;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px;">'
            + lbl
            + "</span>"
            '<span style="font-size:0.68rem;font-weight:700;color:#b8965a;margin-left:6px;">'
            + str(round(conf))
            + "%</span>"
            "</div>"
            '<div style="height:3px;background:rgba(184,150,90,0.15);border-radius:2px;overflow:hidden;">'
            '<div style="height:3px;background:linear-gradient(90deg,#c4845a,#b8965a);border-radius:2px;width:'
            + str(bar)
            + '%;"></div>'
            "</div>"
            '<div style="font-size:0.62rem;color:#999;margin-top:2px;">'
            + cat
            + "</div>"
            "</div></div>"
        )
    others_section = (
        (
            '<div style="margin-top:10px;">'
            '<div style="font-size:0.57rem;letter-spacing:1.5px;text-transform:uppercase;color:rgba(26,58,58,0.35);margin-bottom:6px;">Khả năng khác</div>'
            + other_rows
            + "</div>"
        )
        if other_rows
        else ""
    )

    return (
        '<div style="background:linear-gradient(135deg,rgba(26,58,58,0.03),rgba(184,150,90,0.04));'
        'border:1px solid rgba(184,150,90,0.18);border-radius:12px;padding:14px 16px;margin-bottom:12px;">'
        + main_block
        + others_section
        + "</div>"
    )


def _img_preview_html(b64: str, dest: str) -> str:
    if not b64:
        return ""
    return (
        '<div style="display:flex;align-items:center;gap:10px;background:#faf8f4;'
        'border:1px solid rgba(184,150,90,0.18);border-radius:8px;padding:8px 12px;margin-bottom:10px;">'
        '<img style="width:44px;height:44px;border-radius:6px;object-fit:cover;'
        'border:1px solid rgba(184,150,90,0.15);" src="data:image/png;base64,'
        + b64
        + '" />'
        '<div><div style="font-size:0.6rem;color:#7a6e64;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:2px;">&#128247; Ảnh đã gửi</div>'
        '<div style="font-size:0.83rem;color:#1a3a3a;font-weight:600;">'
        + str(dest or "...")
        + "</div>"
        "</div></div>"
    )


# ══════════════════════════════════════════════════════════════
# QUERY PROCESSOR — FIXED
# ══════════════════════════════════════════════════════════════
def process_query(user_input: str, uploaded_image=None):
    lang = get_lang()
    detected = detect_language(user_input)
    if len(user_input.strip()) > 5:
        lang = detected
        st.session_state["lang"] = lang

    engine = st.session_state.get("retrieval_engine")
    classifier = st.session_state.get("image_classifier")
    groq_cli = st.session_state.get("groq_client")
    data_eng = st.session_state.get("data_engine")

    image_classifications = []
    current_img_b64 = ""
    is_image_query = uploaded_image is not None

    # ── Step 1: Image classification ────────────────────────
    if uploaded_image is not None and classifier:
        with st.spinner(
            "Đang nhận diện ảnh..." if lang == "vi" else "Analyzing image..."
        ):
            image_classifications = classifier.classify(
                uploaded_image, top_k=3, lang=lang
            )
            if image_classifications:
                current_img_b64 = _pil_to_b64(uploaded_image)
                st.session_state["_cached_classifications"] = image_classifications
                st.session_state["_cached_image_b64"] = current_img_b64
    elif not is_image_query:
        # ── Key fix: chỉ reuse cached classifications nếu câu hỏi là follow-up về ảnh ──
        # Text queries với destination cụ thể (quick prompts, manual input) KHÔNG dùng cache
        from groq_client import _extract_destination_from_text

        has_explicit_dest = bool(_extract_destination_from_text(user_input))

        if not has_explicit_dest and _is_followup_image_question(user_input):
            # Genuine follow-up about the image
            cached = st.session_state.get("_cached_classifications")
            if cached:
                image_classifications = cached
                current_img_b64 = st.session_state.get("_cached_image_b64", "")
        # else: text query with explicit destination OR unrelated question → don't load cached image

    # ── Step 2: Resolve destination ─────────────────────────
    is_followup = _is_followup_image_question(user_input) and not is_image_query
    destination = _resolve_destination(
        user_input, image_classifications, is_image_query, is_followup
    )

    # Update cached destination only on fresh image queries
    if is_image_query and destination:
        st.session_state["_cached_destination"] = destination

    display_dest = destination or ""

    # ── Step 3: Intent & data context ───────────────────────
    from groq_client import _classify_intent

    intents = _classify_intent(user_input)
    if is_image_query:
        if "image_id" not in intents:
            intents.append("image_id")

    data_context = ""

    if "compare" in intents:
        try:
            found_dests, low = [], user_input.lower()
            if data_eng:
                for d in data_eng.all_destinations():
                    if d.lower() in low:
                        found_dests.append(d)
            if len(found_dests) >= 2 and data_eng:
                data_context = data_eng.compare_destinations(found_dests)
            elif destination and data_eng:
                data_context = data_eng.build_context_for_llm(destination, lang)
        except Exception:
            if destination and data_eng:
                data_context = data_eng.build_context_for_llm(destination, lang)

    elif "recommend" in intents and not is_image_query:
        import re

        budget_val, duration_val = None, None
        bm = re.search(r"\$(\d+(?:,\d+)?)", user_input)
        if bm:
            budget_val = float(bm.group(1).replace(",", ""))
        dm = re.search(r"(\d+)\s*(?:ngày|days?)", user_input)
        if dm:
            duration_val = int(dm.group(1))
        if data_eng:
            candidates = data_eng.recommend_destinations(
                budget=budget_val, duration_days=duration_val
            )
            if candidates:
                data_context = data_eng.format_recommendation(candidates, lang)

    elif destination and data_eng:
        data_context = data_eng.build_context_for_llm(destination, lang)

    # ── Step 4: Retrieval ────────────────────────────────────
    retrieval_results = []
    if engine and destination:
        retrieval_results = engine.retrieve(
            f"{destination} {user_input}".strip(), top_k=5
        )

    # ── Step 5: Weather ──────────────────────────────────────
    weather_html = ""
    if destination:
        try:
            from weather_service import build_weather_html

            weather_html = build_weather_html(destination, lang)
        except Exception as e:
            print(f"[WEATHER] {e}")

    # ── Step 6: Tour links ───────────────────────────────────
    tour_html = ""
    if destination and any(
        k in intents
        for k in ["general", "activity", "planner", "cost", "hotel", "image_id"]
    ):
        try:
            from tour_links import build_tour_links_html

            tour_html = build_tour_links_html(destination, lang)
        except Exception as e:
            print(f"[TOUR] {e}")

    # ── Step 7: LLM ─────────────────────────────────────────
    response = ""
    if groq_cli:
        conv_hist = st.session_state.get("conversation_history", [])
        with st.spinner(
            "Aria đang chuẩn bị câu trả lời..."
            if lang == "vi"
            else "Aria is preparing your answer..."
        ):
            response = groq_cli.chat(
                user_message=user_input,
                lang=lang,
                retrieval_results=retrieval_results,
                image_classifications=image_classifications,
                conversation_history=conv_hist,
                destination=destination,
                data_context=data_context,
            )
        st.session_state["conversation_history"].append(
            {"role": "user", "content": user_input}
        )
        st.session_state["conversation_history"].append(
            {"role": "assistant", "content": response}
        )
        if len(st.session_state["conversation_history"]) > 40:
            st.session_state["conversation_history"] = st.session_state[
                "conversation_history"
            ][-40:]
    else:
        response = (
            "Xin lỗi, hệ thống chưa sẵn sàng. Vui lòng thử lại."
            if lang == "vi"
            else "Sorry, system not ready."
        )

    # ── Step 8: Itinerary popup ──────────────────────────────
    itinerary_html = ""
    if destination:
        try:
            from itinerary_popup import build_itinerary_button_and_modal

            msg_idx = len(st.session_state.get("messages", []))
            itinerary_html = build_itinerary_button_and_modal(
                msg_idx, destination, lang
            )
        except Exception as e:
            print(f"[ITIN] {e}")

    # ── Step 9: Hotel Map data (rendered via st.components later) ──
    hotel_map_data = None  # dict: {destination, lang} — actual render in message loop
    if destination:
        from groq_client import _classify_intent as _ci

        _intents_for_map = _ci(user_input)
        try:
            from hotel_map_service import (
                should_show_hotel_map,
                get_hotels_for_destination,
            )

            if should_show_hotel_map(_intents_for_map, destination):
                with st.spinner(
                    "Đang tải bản đồ khách sạn..."
                    if lang == "vi"
                    else "Loading hotel map..."
                ):
                    # Pre-fetch and cache hotels now (blocking), render later
                    hotels = get_hotels_for_destination(destination, lang)
                    if hotels:
                        hotel_map_data = {"destination": destination, "lang": lang}
        except Exception as e:
            print(f"[HOTEL_MAP] {e}")

    card_html = _classify_card(image_classifications, lang)
    img_prev = _img_preview_html(current_img_b64, display_dest)

    return (
        card_html,
        img_prev,
        response,
        weather_html,
        tour_html,
        hotel_map_data,
        itinerary_html,
        destination or "",
    )


# ══════════════════════════════════════════════════════════════
# MARKDOWN → HTML
# ══════════════════════════════════════════════════════════════
def _md_to_html(content: str) -> str:
    import re

    def _build_table_html(lines):
        tbl = '<table style="border-collapse:collapse;width:100%;margin:12px 0;font-size:0.82rem;">'
        is_header = True
        for line in lines:
            stripped = line.strip().strip("|")
            if not stripped:
                continue
            if re.match(r"^[\s|:\-]+$", stripped):
                continue
            cells = [c.strip() for c in stripped.split("|")]
            if is_header:
                tbl += (
                    "<tr>"
                    + "".join(
                        f'<th style="background:#1a3a3a;color:white;padding:8px 12px;text-align:left;font-size:0.78rem;font-weight:500;">{c}</th>'
                        for c in cells
                    )
                    + "</tr>"
                )
                is_header = False
            else:
                tbl += (
                    "<tr>"
                    + "".join(
                        f'<td style="padding:7px 12px;border:1px solid rgba(184,150,90,0.2);background:white;">{c}</td>'
                        for c in cells
                    )
                    + "</tr>"
                )
        tbl += "</table>"
        return tbl

    def convert_tables(text):
        lines = text.split("\n")
        result, table_buf, in_table = [], [], False
        for line in lines:
            is_row = "|" in line and line.strip().startswith("|")
            if is_row:
                table_buf.append(line)
                in_table = True
            else:
                if in_table:
                    result.append(_build_table_html(table_buf))
                    table_buf = []
                    in_table = False
                result.append(line)
        if in_table:
            result.append(_build_table_html(table_buf))
        return "\n".join(result)

    content = convert_tables(content)

    content = re.sub(
        r"^### (.+)$",
        r'<div style="font-family:Cormorant Garamond,serif;color:#1a3a3a;font-size:1.05rem;font-weight:600;margin:12px 0 4px;">\1</div>',
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^## (.+)$",
        r'<div style="font-family:Cormorant Garamond,serif;color:#1a3a3a;font-size:1.2rem;font-weight:500;margin:14px 0 5px;border-bottom:1px solid rgba(184,150,90,0.2);padding-bottom:4px;">\1</div>',
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^# (.+)$",
        r'<div style="font-family:Cormorant Garamond,serif;color:#1a3a3a;font-size:1.35rem;font-weight:400;margin:14px 0 6px;">\1</div>',
        content,
        flags=re.MULTILINE,
    )

    content = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", content)
    content = re.sub(
        r"\*\*(.+?)\*\*",
        r'<strong style="color:#1a3a3a;font-weight:600;">\1</strong>',
        content,
    )
    content = re.sub(r"\*([^*\n]+?)\*", r'<em style="color:#c4845a;">\1</em>', content)

    content = re.sub(
        r"`([^`\n]+)`",
        r'<code style="background:#e8ddd0;color:#1a3a3a;padding:1px 5px;border-radius:3px;font-size:0.83em;">\1</code>',
        content,
    )

    content = re.sub(
        r"^(?:&gt;|>) (.+)$",
        r'<div style="border-left:3px solid #b8965a;padding-left:12px;color:#7a6e64;font-style:italic;margin:8px 0;">\1</div>',
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^---+$",
        r'<hr style="border:none;border-top:1px solid rgba(184,150,90,0.2);margin:12px 0;">',
        content,
        flags=re.MULTILINE,
    )

    content = re.sub(
        r"⏰\s*([^:\n]+):\s*([^\n]+)",
        lambda m: (
            f'<div style="display:flex;gap:8px;padding:5px 0;border-bottom:1px solid rgba(184,150,90,0.08);">'
            f'<span style="font-size:0.7rem;color:#c4845a;font-weight:700;min-width:48px;margin-top:2px;">⏰ {m.group(1)}</span>'
            f'<span style="font-size:0.83rem;color:#1c1410;flex:1;">{m.group(2)}</span></div>'
        ),
        content,
    )
    content = re.sub(
        r"🍽️\s*(?:Ăn|Eat)[^:\n]*:\s*([^\n]+)",
        lambda m: (
            f'<div style="background:rgba(184,150,90,0.07);border-radius:6px;padding:6px 10px;margin:4px 0;font-size:0.8rem;">'
            f'🍽️ <strong style="color:#2d5555;">Ăn:</strong> {m.group(1)}</div>'
        ),
        content,
    )
    content = re.sub(
        r"🏨\s*(?:Lưu trú|Stay)[^:\n]*:\s*([^\n]+)",
        lambda m: (
            f'<div style="background:rgba(26,58,58,0.05);border-radius:6px;padding:6px 10px;margin:4px 0;font-size:0.8rem;">'
            f'🏨 <strong style="color:#2d5555;">Lưu trú:</strong> {m.group(1)}</div>'
        ),
        content,
    )
    content = re.sub(
        r"💡\s*(?:Tip|Mẹo|Pro tip|Tip vàng)[^:\n]*:\s*([^\n]+)",
        lambda m: (
            f'<div style="background:linear-gradient(135deg,rgba(184,150,90,0.1),rgba(196,132,90,0.05));'
            f'border:1px solid rgba(184,150,90,0.22);border-radius:6px;padding:7px 12px;margin:6px 0;font-size:0.79rem;">'
            f'💡 <strong style="color:#b8965a;">Tip:</strong> {m.group(1)}</div>'
        ),
        content,
    )

    lines = content.split("\n")
    result_lines, in_list = [], False
    for line in lines:
        bm = re.match(r"^[ \t]*[-•*]\s+(.+)$", line)
        nm = re.match(r"^[ \t]*\d+\.\s+(.+)$", line)
        if bm:
            if not in_list:
                result_lines.append('<ul style="padding-left:18px;margin:6px 0;">')
                in_list = "ul"
            result_lines.append(f'<li style="margin-bottom:4px;">{bm.group(1)}</li>')
        elif nm:
            if in_list == "ul":
                result_lines.append("</ul>")
                in_list = False
            if not in_list:
                result_lines.append('<ol style="padding-left:18px;margin:6px 0;">')
                in_list = "ol"
            result_lines.append(f'<li style="margin-bottom:4px;">{nm.group(1)}</li>')
        else:
            if in_list == "ul":
                result_lines.append("</ul>")
            elif in_list == "ol":
                result_lines.append("</ol>")
            in_list = False
            result_lines.append(line)
    if in_list == "ul":
        result_lines.append("</ul>")
    elif in_list == "ol":
        result_lines.append("</ol>")
    content = "\n".join(result_lines)

    block_tags = (
        "<div",
        "<ul",
        "<ol",
        "<li",
        "<table",
        "<tr",
        "<th",
        "<td",
        "<hr",
        "</ul",
        "</ol",
        "</div",
        "</table",
    )
    out = []
    for line in content.split("\n"):
        s = line.strip()
        if s == "":
            out.append("<br>")
        elif any(s.startswith(t) or s.endswith(">") for t in block_tags):
            out.append(line)
        else:
            out.append(line + "<br>")
    return "".join(out)


# ══════════════════════════════════════════════════════════════
# EXPORT BUTTONS
# ══════════════════════════════════════════════════════════════
def _render_export_bar(msg_idx: int, destination: str, response_text: str, lang: str):
    if not destination or destination in ("", "Unknown"):
        return

    import re as _re

    dur_match = _re.search(r"(\d+)[Nn](\d+)[Đđ]", response_text)
    duration = dur_match.group(0) if dur_match else ""
    if not duration:
        dm = _re.search(r"(\d+)\s*(?:ngày|days?)", response_text, _re.IGNORECASE)
        if dm:
            duration = f"{dm.group(1)} ngày"

    key = str(msg_idx)

    st.markdown('<div class="export-bar-wrapper">', unsafe_allow_html=True)
    st.markdown(
        '<div class="export-bar-label">&#128196; Xuất tài liệu</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        already = st.session_state["_export_pdf_itin"].get(key)
        if already:
            st.download_button(
                "⬇️ PDF Lịch trình",
                data=already,
                file_name=f"lich-trinh-{destination.lower().replace(' ', '-')}.pdf",
                mime="application/pdf",
                key=f"dl_pdf_itin_{key}",
                use_container_width=True,
            )
        else:
            if st.button(
                "📄 PDF Lịch trình", key=f"btn_pdf_itin_{key}", use_container_width=True
            ):
                with st.spinner("Đang tạo PDF..."):
                    try:
                        from export_service import export_itinerary_pdf

                        pdf_b = export_itinerary_pdf(
                            destination, response_text, duration, lang
                        )
                        st.session_state["_export_pdf_itin"][key] = pdf_b
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    with col2:
        already = st.session_state["_export_pdf_plan"].get(key)
        if already:
            st.download_button(
                "⬇️ Travel Plan PDF",
                data=already,
                file_name=f"travel-plan-{destination.lower().replace(' ', '-')}.pdf",
                mime="application/pdf",
                key=f"dl_pdf_plan_{key}",
                use_container_width=True,
            )
        else:
            if st.button(
                "🗺️ PDF Kế hoạch Pro",
                key=f"btn_pdf_plan_{key}",
                use_container_width=True,
            ):
                with st.spinner("Đang tạo Travel Plan..."):
                    try:
                        from export_service import export_travel_plan_pdf

                        pdf_b = export_travel_plan_pdf(
                            destination, response_text, duration, lang
                        )
                        st.session_state["_export_pdf_plan"][key] = pdf_b
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    with col3:
        already = st.session_state["_export_docx"].get(key)
        if already:
            st.download_button(
                "⬇️ Word (.docx)",
                data=already,
                file_name=f"lich-trinh-{destination.lower().replace(' ', '-')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dl_docx_{key}",
                use_container_width=True,
            )
        else:
            if st.button(
                "📝 Word (.docx)", key=f"btn_docx_{key}", use_container_width=True
            ):
                with st.spinner("Đang tạo Word..."):
                    try:
                        from export_service import export_itinerary_docx

                        docx_b = export_itinerary_docx(
                            destination, response_text, duration, lang
                        )
                        st.session_state["_export_docx"][key] = docx_b
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    with col4:
        already = st.session_state["_export_xlsx"].get(key)
        if already:
            st.download_button(
                "⬇️ Excel Chi phí",
                data=already,
                file_name=f"chi-phi-{destination.lower().replace(' ', '-')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_xlsx_{key}",
                use_container_width=True,
            )
        else:
            if st.button(
                "💰 Excel Chi phí", key=f"btn_xlsx_{key}", use_container_width=True
            ):
                with st.spinner("Đang tạo Excel..."):
                    try:
                        from export_service import export_cost_excel

                        xlsx_b = export_cost_excel(
                            destination, response_text, duration, lang
                        )
                        st.session_state["_export_xlsx"][key] = xlsx_b
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    lang = get_lang()

    # ── Init engines ──────────────────────────────────────────
    if st.session_state["data_engine"] is None:
        try:
            with st.spinner("Đang khởi động..." if lang == "vi" else "Starting up..."):
                st.session_state["data_engine"] = load_data_engine()
        except Exception as e:
            st.warning(f"DataEngine: {e}")

    df = None
    try:
        df = load_dataset_cached()
    except Exception:
        pass

    if df is not None and st.session_state["retrieval_engine"] is None:
        try:
            st.session_state["retrieval_engine"] = load_retrieval_engine(df)
        except Exception:
            pass

    if st.session_state["image_classifier"] is None:
        try:
            st.session_state["image_classifier"] = load_image_classifier()
        except Exception:
            pass

    if st.session_state["groq_client"] is None:
        if GROQ_API_KEY:
            try:
                st.session_state["groq_client"] = load_groq_client()
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")
        else:
            st.error("Chưa cấu hình GROQ_API_KEY trong file .env")

    if not st.session_state["messages"]:
        add_welcome()

    # ══════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown(
            '<div style="font-family:Cormorant Garamond,serif;font-size:1.5rem;color:#f5f0e8;text-align:center;padding:12px 0 2px;letter-spacing:1px;">✦ Aria Travel</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.65rem;color:rgba(184,150,90,0.8);text-align:center;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">AI Tour Guide</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section">Ngôn ngữ / Language</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🇻🇳 Tiếng Việt", use_container_width=True, key="lvi"):
                st.session_state["lang"] = "vi"
                st.rerun()
        with c2:
            if st.button("🇬🇧 English", use_container_width=True, key="len"):
                st.session_state["lang"] = "en"
                st.rerun()

        st.markdown(
            '<div class="sidebar-section">🗺️ Hỏi nhanh</div>', unsafe_allow_html=True
        )
        # Quick prompts: destination PHẢI xuất hiện rõ ràng trong text để extract đúng
        quick = {
            "vi": [
                "Lịch trình 3 ngày Đà Lạt chi tiết 📅",
                "Chi phí thực tế đi Phú Quốc? 💰",
                "Cần Thơ có gì đặc biệt nhất? 🌊",
                "So sánh Đà Nẵng và Nha Trang ⚖️",
                "Lịch trình 5 ngày Sa Pa trekking 🏔️",
                "Điểm đến budget dưới $500 💵",
                "Đặc sản và ẩm thực Hội An 🍜",
                "Kế hoạch 4 ngày Hạ Long 🏖️",
                "Cách di chuyển đến Phú Quốc ✈️",
                "Thời tiết Hà Nội tháng mấy đẹp? 🌡️",
            ],
            "en": [
                "Detailed 3-day Da Lat itinerary 📅",
                "Real costs for Phu Quoc trip? 💰",
                "What's special about Can Tho? 🌊",
                "Compare Da Nang vs Nha Trang ⚖️",
                "5-day Sa Pa trekking itinerary 🏔️",
                "Budget destinations under $500 💵",
                "Hoi An food and specialties guide 🍜",
                "Ha Long Bay 4-day plan 🏖️",
                "How to get to Phu Quoc? ✈️",
                "Best month to visit Hanoi? 🌡️",
            ],
        }
        for q in quick.get(lang, quick["vi"]):
            if st.button(q, use_container_width=True, key=f"q_{hash(q)}"):
                st.session_state["_quick_q"] = q
                st.rerun()

        st.markdown(
            '<div class="sidebar-section">📄 Xuất tài liệu</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.68rem;color:rgba(245,240,232,0.55);line-height:1.8;">'
            "📄 PDF Lịch trình<br>🗺️ PDF Kế hoạch Pro<br>📝 Word (.docx)<br>💰 Excel Chi phí"
            '<br><span style="color:rgba(184,150,90,0.6);font-size:0.62rem;">→ Xuất sau mỗi câu trả lời</span>'
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section">🌤️ Thời tiết</div>', unsafe_allow_html=True
        )
        try:
            from weather_service import OPENWEATHER_API_KEY as OWM_KEY

            if OWM_KEY and OWM_KEY != "your_key_here":
                st.markdown(
                    '<div style="font-size:0.72rem;color:rgba(100,200,100,0.8);padding:4px 0;">✅ OpenWeatherMap đã kết nối</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="font-size:0.7rem;color:rgba(245,240,232,0.5);line-height:1.6;">'
                    "📋 Thêm API key miễn phí:<br>"
                    '<code style="background:rgba(255,255,255,0.1);padding:1px 4px;border-radius:3px;font-size:0.65rem;">OPENWEATHER_API_KEY=xxx</code><br>'
                    '<a href="https://home.openweathermap.org/api_keys" target="_blank" style="color:rgba(184,150,90,0.8);font-size:0.68rem;">→ Lấy key tại đây</a>'
                    "</div>",
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

        st.markdown(
            '<div class="sidebar-section">📷 Nhận diện ảnh</div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload ảnh",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key="img_upload",
        )
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True)
            btn_label = (
                "✦ Nhận diện & Tư vấn" if lang == "vi" else "✦ Identify & Advise"
            )
            if st.button(btn_label, use_container_width=True, key="id_btn"):
                st.session_state["_pending_image"] = img
                st.session_state["_trigger_id"] = True
                st.rerun()
        else:
            st.session_state["_pending_image"] = None

        st.markdown("---")

        st.markdown(
            '<div class="sidebar-section">🔗 Nền tảng đặt tour</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.7rem;line-height:2.2;">'
            '<a href="https://www.klook.com/vi" target="_blank" style="color:rgba(255,107,53,0.8);text-decoration:none;">🟠 Klook</a> &nbsp;'
            '<a href="https://www.getyourguide.com" target="_blank" style="color:rgba(231,37,43,0.8);text-decoration:none;">🔴 GetYourGuide</a><br>'
            '<a href="https://www.viator.com" target="_blank" style="color:rgba(0,170,108,0.8);text-decoration:none;">🟢 Viator</a> &nbsp;'
            '<a href="https://www.traveloka.com/vi-vn" target="_blank" style="color:rgba(0,100,210,0.8);text-decoration:none;">🔵 Traveloka</a><br>'
            '<a href="https://www.booking.com" target="_blank" style="color:rgba(0,53,128,0.8);text-decoration:none;">💙 Booking.com</a> &nbsp;'
            '<a href="https://www.agoda.com/vi-vn" target="_blank" style="color:rgba(228,77,38,0.8);text-decoration:none;">🌐 Agoda</a>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        history_len = len(st.session_state.get("conversation_history", [])) // 2
        if history_len > 0:
            st.markdown(
                f'<div style="font-size:0.7rem;color:rgba(184,150,90,0.7);text-align:center;margin-bottom:8px;">'
                f"💬 {history_len} {'câu hỏi' if lang == 'vi' else 'questions'}</div>",
                unsafe_allow_html=True,
            )
        clear_label = "↺ Cuộc trò chuyện mới" if lang == "vi" else "↺ New conversation"
        if st.button(clear_label, use_container_width=True, key="clr"):
            st.session_state["messages"] = []
            st.session_state["conversation_history"] = []
            st.session_state["_cached_classifications"] = None
            st.session_state["_cached_destination"] = ""
            st.session_state["_cached_image_b64"] = ""
            st.session_state["_export_pdf_itin"] = {}
            st.session_state["_export_pdf_plan"] = {}
            st.session_state["_export_docx"] = {}
            st.session_state["_export_xlsx"] = {}
            st.session_state["_hotel_map_cache"] = {}
            try:
                from hotel_map_service import clear_cache as _clr_hotels

                _clr_hotels()
            except Exception:
                pass
            add_welcome()
            st.rerun()

        data_eng = st.session_state.get("data_engine")
        if data_eng:
            st.markdown(
                '<div class="sidebar-section">📍 Điểm đến có dữ liệu</div>',
                unsafe_allow_html=True,
            )
            all_dests = data_eng.all_destinations()[:20]
            dest_html = " · ".join(all_dests)
            if len(data_eng.all_destinations()) > 20:
                dest_html += " · ..."
            st.markdown(
                f'<div style="font-size:0.67rem;line-height:2.0;color:rgba(245,240,232,0.4);">{dest_html}</div>',
                unsafe_allow_html=True,
            )

    # ══════════════════════════════════════════════════════════
    # MAIN CONTENT
    # ══════════════════════════════════════════════════════════
    st.markdown(
        """<div class="header-section">
        <div class="header-ornament">✦ &nbsp;&nbsp; A I &nbsp; T O U R &nbsp; G U I D E &nbsp;&nbsp; ✦</div>
        <div class="header-brand">Aria <span>Travel</span></div>
        <div class="header-tagline">Expert guidance · Real insights · Trusted bookings · Export ready</div>
    </div>""",
        unsafe_allow_html=True,
    )

    data_eng = st.session_state.get("data_engine")
    if data_eng:
        vn_count = sum(len(v.get("places", [])) for v in data_eng._vn_places.values())
        intl_count = len(data_eng._intl_trips)
        n_dests = len(data_eng.all_destinations())
        st.markdown(
            f"""<div class="stats-row">
                <div class="stat-item"><div class="stat-number">{vn_count}+</div><div class="stat-label">Điểm đến VN</div></div>
                <div class="stat-divider"></div>
                <div class="stat-item"><div class="stat-number">{intl_count}</div><div class="stat-label">Điểm QT</div></div>
                <div class="stat-divider"></div>
                <div class="stat-item"><div class="stat-number">{n_dests}</div><div class="stat-label">Tổng điểm đến</div></div>
                <div class="stat-divider"></div>
                <div class="stat-item"><div class="stat-number">15+</div><div class="stat-label">Năm kinh nghiệm</div></div>
                <div class="stat-divider"></div>
                <div class="stat-item"><div class="stat-number">4</div><div class="stat-label">Định dạng xuất</div></div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Chat Messages ──────────────────────────────────────────
    st.markdown('<div class="chat-container" id="chat-end">', unsafe_allow_html=True)

    AVATAR = (
        '<div style="width:30px;height:30px;border-radius:50%;flex-shrink:0;'
        "background:linear-gradient(135deg,#1a3a3a,#3d6e6e);"
        "display:flex;align-items:center;justify-content:center;"
        'font-size:12px;margin-top:2px;">&#10022;</div>'
    )

    for idx, msg in enumerate(st.session_state["messages"]):
        if msg["role"] == "user":
            import html as _html

            content_safe = _html.escape(msg["content"])
            st.markdown(
                f'<div class="msg-row-user">'
                f'<div class="avatar-user">U</div>'
                f'<div class="bubble-user">{content_safe}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            rendered = _md_to_html(msg["content"])
            img_prev = msg.get("img_preview_html", "")
            card_html_m = msg.get("card_html", "")
            weather_html = msg.get("weather_html", "")
            tour_html = msg.get("tour_html", "")
            hotel_map_data = msg.get("hotel_map_data")  # dict or None
            itinerary_html = msg.get("itinerary_html", "")
            msg_dest = msg.get("destination", "")

            content_blocks = []
            if img_prev:
                content_blocks.append(img_prev)
            if card_html_m:
                content_blocks.append(card_html_m)

            content_blocks.append(
                '<div style="font-size:0.59rem;color:#b8965a;letter-spacing:2px;'
                'text-transform:uppercase;margin-bottom:4px;font-weight:600;">'
                "&#10022; Aria &nbsp;&middot;&nbsp; AI Tour Guide</div>"
            )
            content_blocks.append(
                '<div style="background:white;border:1px solid rgba(184,150,90,0.2);'
                "border-radius:4px 14px 14px 14px;padding:14px 18px;"
                "font-size:0.87rem;line-height:1.75;color:#1c1410;"
                'box-shadow:0 2px 10px rgba(28,20,16,0.05);word-wrap:break-word;">'
                + rendered
                + "</div>"
            )
            if weather_html:
                content_blocks.append(weather_html)
            if tour_html:
                content_blocks.append(tour_html)

            st.markdown(
                '<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;">'
                + AVATAR
                + '<div style="flex:1;min-width:0;">'
                + "".join(content_blocks)
                + "</div></div>",
                unsafe_allow_html=True,
            )

            # ── Hotel Map — rendered via st.components.v1.html() ──────
            # MUST be outside st.markdown to allow Leaflet.js to run
            if hotel_map_data:
                try:
                    import streamlit.components.v1 as _components
                    from hotel_map_service import build_hotel_map_component

                    dest_m = hotel_map_data.get("destination", "")
                    lang_m = hotel_map_data.get("lang", "vi")
                    html_str = build_hotel_map_component(dest_m, lang_m, height=560)
                    if html_str:
                        st.markdown(
                            '<div style="margin:0 0 8px 38px;">', unsafe_allow_html=True
                        )
                        _components.html(html_str, height=560, scrolling=False)
                        st.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    print(f"[HOTEL_MAP_RENDER] {e}")

            if itinerary_html:
                st.markdown(
                    '<div style="margin:0 0 6px 38px;">' + itinerary_html + "</div>",
                    unsafe_allow_html=True,
                )

            # Export bar
            if msg_dest and msg_dest not in ("", "Unknown"):
                _render_export_bar(idx, msg_dest, msg["content"], get_lang())
            elif idx > 0 and not msg_dest:
                try:
                    from groq_client import _extract_destination_from_text

                    inferred = _extract_destination_from_text(msg["content"])
                    if inferred:
                        _render_export_bar(idx, inferred, msg["content"], get_lang())
                except Exception:
                    pass

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Input area ────────────────────────────────────────────
    st.markdown(
        '<div class="input-divider"><span class="input-divider-icon">✦ ✦ ✦</span></div>',
        unsafe_allow_html=True,
    )

    ph = (
        "Hỏi Aria về điểm đến, lịch trình, chi phí, thời tiết..."
        if lang == "vi"
        else "Ask Aria about destinations, itineraries, costs, weather..."
    )
    col1, col2 = st.columns([5, 1], gap="small")
    with col1:
        user_input = st.text_input(
            "chat",
            placeholder=ph,
            label_visibility="collapsed",
            key=f"inp_{st.session_state['input_counter']}",
        )
    with col2:
        send_btn = st.button(
            "Gửi →" if lang == "vi" else "Send →", use_container_width=True, key="snd"
        )

    # ── Handle inputs ─────────────────────────────────────────
    quick_q = st.session_state.pop("_quick_q", None)
    trig_id = st.session_state.pop("_trigger_id", False)
    pend_img = st.session_state.get("_pending_image", None)

    final_in = None
    final_img = None

    if quick_q:
        # Strip emojis, symbols, leading/trailing whitespace properly
        import re as _re

        # Remove emoji and special symbols at the start (including Unicode emoji ranges)
        cleaned = _re.sub(
            r"^[\U0001F000-\U0001FFFF\U00002600-\U000027BF\U0001F300-\U0001F9FF"
            r"\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF\u2700-\u27BF"
            r"\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\u00A9\u00AE"
            r"\s]+",
            "",
            quick_q,
        ).strip()
        # Also remove any remaining leading non-word chars (fallback)
        cleaned = _re.sub(r"^[^\wÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+", "", cleaned).strip()
        final_in = cleaned if cleaned else quick_q.strip()
    elif trig_id:
        final_in = (
            "Đây là địa điểm nào? Nhận diện và tư vấn chi tiết như một hướng dẫn viên chuyên nghiệp."
            if lang == "vi"
            else "What destination is this? Identify and give detailed travel advice as a professional tour guide."
        )
        final_img = pend_img
        st.session_state["_pending_image"] = None
    elif send_btn and user_input.strip():
        final_in = user_input.strip()
        final_img = pend_img

    if final_in:
        st.session_state["messages"].append(
            {
                "role": "user",
                "content": final_in,
                "card_html": "",
                "img_preview_html": "",
                "weather_html": "",
                "tour_html": "",
                "itinerary_html": "",
                "destination": "",
            }
        )

        (
            card_html,
            img_prev,
            response,
            weather_html,
            tour_html,
            hotel_map_data,
            itinerary_html,
            dest,
        ) = process_query(final_in, uploaded_image=final_img)

        st.session_state["messages"].append(
            {
                "role": "bot",
                "content": response,
                "card_html": card_html,
                "img_preview_html": img_prev,
                "weather_html": weather_html,
                "tour_html": tour_html,
                "hotel_map_data": hotel_map_data,
                "itinerary_html": itinerary_html,
                "destination": dest,
            }
        )

        st.session_state["input_counter"] += 1
        st.rerun()


if __name__ == "__main__":
    main()

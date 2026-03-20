"""
config.py — Cấu hình TravelBot AI.
Đường dẫn DATA_FILES được map đúng với tên key mà data_engine.py dùng.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# API KEYS
# ─────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ─────────────────────────────────────────
# MODEL
# ─────────────────────────────────────────
GROQ_MODEL   = "llama-3.3-70b-versatile"
TEMPERATURE  = 0.4
MAX_TOKENS   = 1500

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DATA_DIR      = os.path.join(BASE_DIR, "data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
IMAGES_DIR    = os.path.join(BASE_DIR, "data", "Images")

# ─────────────────────────────────────────
# DATA FILES
# Key names PHẢI khớp với data_engine.py extractors:
#   "dataset"        → DataSet.xlsx         (315 địa điểm VN)
#   "travel_details" → Travel_details.csv   (139 trips quốc tế có cost)
#   "top_places"     → Top_Indian_Places    (325 điểm Ấn Độ)
#   "flights"        → flights.csv          (Brazil nội địa)
#   "hotels"         → hotels.csv           (Brazil)
#   "tourism"        → tourism_dataset.csv  (mã ngẫu nhiên, ít dùng)
#   "travel"         → Travel.csv           (CRM, không có destination)
#   "users"          → users.csv            (profiles)
# ─────────────────────────────────────────
DATA_FILES = {
    "dataset":        os.path.join(DATA_DIR, "DataSet.xlsx"),
    "travel_details": os.path.join(DATA_DIR, "Travel details dataset.csv"),
    "top_places":     os.path.join(DATA_DIR, "Top Indian Places to Visit.csv"),
    "flights":        os.path.join(DATA_DIR, "flights.csv"),
    "hotels":         os.path.join(DATA_DIR, "hotels.csv"),
    "tourism":        os.path.join(DATA_DIR, "tourism_dataset.csv"),
    "travel":         os.path.join(DATA_DIR, "Travel.csv"),
    "users":          os.path.join(DATA_DIR, "users.csv"),
    "history":        os.path.join(DATA_DIR, "history_data.csv"),
}

# ─────────────────────────────────────────
# RETRIEVAL / EMBEDDING
# ─────────────────────────────────────────
EMBEDDING_MODEL       = "all-MiniLM-L6-v2"
TFIDF_MATRIX_PATH     = os.path.join(ARTIFACTS_DIR, "tfidf_matrix.pkl")
TFIDF_VECTORIZER_PATH = os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.pkl")
EMBEDDING_CACHE_PATH  = os.path.join(ARTIFACTS_DIR, "embeddings_cache.pkl")
LABEL_ENCODER_PATH    = os.path.join(ARTIFACTS_DIR, "label_encoder.pkl")

# ─────────────────────────────────────────
# IMAGE CLASSIFICATION
# ─────────────────────────────────────────
USE_LOCAL_CLIP  = True
CLIP_MODEL_NAME = "ViT-B/32"

# ─────────────────────────────────────────
# LANGUAGE
# ─────────────────────────────────────────
DEFAULT_LANG    = "vi"
SUPPORTED_LANGS = ["vi", "en"]

# ─────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────
SYSTEM_PROMPT_VI = """Bạn là TravelBot AI — trợ lý tư vấn du lịch chuyên nghiệp.
Sử dụng dữ liệu thực được cung cấp trong context để trả lời chính xác.
Trả lời bằng tiếng Việt, rõ ràng, có cấu trúc."""

SYSTEM_PROMPT_EN = """You are TravelBot AI — a professional travel advisor.
Use the real data provided in context to give accurate answers.
Answer in English, clearly structured."""
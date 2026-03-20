"""
data_processing.py — Xử lý dữ liệu du lịch từ nhiều CSV files.
Version 4.0 — KHÔNG dùng dữ liệu tĩnh hardcoded.
  ✅ Chỉ load từ CSV/XLSX thực tế
  ✅ Không có VIETNAM_TRAVEL_KB tĩnh (gây sai thông tin)
  ✅ LLM tự dùng kiến thức để trả lời, không bị nhiễm data cứng
"""

import os, warnings
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")

from config import (
    DATA_FILES,
    ARTIFACTS_DIR,
    TFIDF_MATRIX_PATH,
    TFIDF_VECTORIZER_PATH,
    EMBEDDING_CACHE_PATH,
    LABEL_ENCODER_PATH,
    EMBEDDING_MODEL,
)

os.makedirs(ARTIFACTS_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════
# DESTINATION & CATEGORY KEYWORDS
# ══════════════════════════════════════════════════════
DESTINATION_KEYWORDS = [
    # Vietnam
    ("can tho", "Can Tho"),
    ("cần thơ", "Can Tho"),
    ("da lat", "Da Lat"),
    ("dalat", "Da Lat"),
    ("đà lạt", "Da Lat"),
    ("ha long", "Ha Long"),
    ("hạ long", "Ha Long"),
    ("halong", "Ha Long"),
    ("ha noi", "Hanoi"),
    ("hanoi", "Hanoi"),
    ("hà nội", "Hanoi"),
    ("hoi an", "Hoi An"),
    ("hội an", "Hoi An"),
    ("ho chi minh", "Ho Chi Minh City"),
    ("saigon", "Ho Chi Minh City"),
    ("hcm", "Ho Chi Minh City"),
    ("sài gòn", "Ho Chi Minh City"),
    ("hue", "Hue"),
    ("huế", "Hue"),
    ("mui ne", "Mui Ne"),
    ("mũi né", "Mui Ne"),
    ("nha trang", "Nha Trang"),
    ("phu quoc", "Phu Quoc"),
    ("phú quốc", "Phu Quoc"),
    ("sapa", "Sa Pa"),
    ("sa pa", "Sa Pa"),
    ("vung tau", "Vung Tau"),
    ("vũng tàu", "Vung Tau"),
    ("da nang", "Da Nang"),
    ("danang", "Da Nang"),
    ("đà nẵng", "Da Nang"),
    ("phan thiet", "Phan Thiet"),
    ("phan thiết", "Phan Thiet"),
    ("quy nhon", "Quy Nhon"),
    ("quy nhơn", "Quy Nhon"),
    ("viet nam", "Vietnam"),
    ("vietnam", "Vietnam"),
    ("việt nam", "Vietnam"),
    # International
    ("thailand", "Thailand"),
    ("bangkok", "Bangkok"),
    ("japan", "Japan"),
    ("tokyo", "Tokyo"),
    ("osaka", "Osaka"),
    ("korea", "South Korea"),
    ("seoul", "Seoul"),
    ("singapore", "Singapore"),
    ("malaysia", "Malaysia"),
    ("kuala lumpur", "Kuala Lumpur"),
    ("indonesia", "Indonesia"),
    ("bali", "Bali"),
    ("france", "France"),
    ("paris", "Paris"),
    ("italy", "Italy"),
    ("rome", "Rome"),
    ("usa", "United States"),
    ("america", "United States"),
    ("india", "India"),
    ("delhi", "Delhi"),
    ("philippines", "Philippines"),
    ("manila", "Manila"),
    ("cambodia", "Cambodia"),
    ("angkor", "Siem Reap"),
]

CATEGORY_KEYWORDS = [
    ("historical site", "Historical Site"),
    ("di tích", "Historical Site"),
    ("world heritage", "World Heritage"),
    ("di sản", "World Heritage"),
    ("national park", "National Park"),
    ("vườn quốc gia", "National Park"),
    ("beach", "Beach"),
    ("bãi biển", "Beach"),
    ("mountain", "Mountain"),
    ("núi", "Mountain"),
    ("temple", "Temple"),
    ("chùa", "Temple"),
    ("đền", "Temple"),
    ("museum", "Museum"),
    ("bảo tàng", "Museum"),
    ("cave", "Cave"),
    ("hang", "Cave"),
    ("waterfall", "Waterfall"),
    ("thác", "Waterfall"),
    ("island", "Island"),
    ("đảo", "Island"),
    ("food", "Food"),
    ("ăn uống", "Food"),
    ("đặc sản", "Food"),
    ("hotel", "Hotel"),
    ("khách sạn", "Hotel"),
    ("resort", "Resort"),
    ("market", "Market"),
    ("chợ", "Market"),
]


def _extract_destination(text: str) -> str:
    low = text.lower()
    for pattern, canonical in DESTINATION_KEYWORDS:
        if pattern in low:
            return canonical
    return "Unknown"


def _extract_category(text: str) -> str:
    low = text.lower()
    for pattern, canonical in CATEGORY_KEYWORDS:
        if pattern in low:
            return canonical
    return "General"


# ══════════════════════════════════════════════════════
# LOAD CSV/XLSX FILES
# ══════════════════════════════════════════════════════
def _load_csv_file(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        return None
    try:
        if filepath.endswith(".xlsx"):
            df = pd.read_excel(filepath, engine="openpyxl")
            df.columns = [str(c).strip() for c in df.columns]
            df = df.reset_index(drop=True)
            print(f"[DATA] Loaded {os.path.basename(filepath)}: {len(df):,} records")
            return df
        for encoding in ["utf-8", "utf-8-sig", "latin1", "iso-8859-1", "cp1252"]:
            try:
                df = pd.read_csv(filepath, encoding=encoding, index_col=None)
                df = df.reset_index(drop=True)
                print(
                    f"[DATA] Loaded {os.path.basename(filepath)}: {len(df):,} records"
                )
                return df
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"[DATA] ⚠️ Error loading {filepath}: {e}")
        return None


def _process_dataset_xlsx(df: pd.DataFrame) -> pd.DataFrame:
    """DataSet.xlsx — 315 địa điểm VN, tỉnh/thành."""
    if df is None or len(df) == 0:
        return None
    records = []
    for _, row in df.iterrows():
        try:
            name = str(row.get("Tên địa điểm", "")).strip()
            province = str(row.get("Vị trí", "")).strip()
            description = str(row.get("Mô tả", "")).strip()
            rating = str(row.get("Đánh giá ", row.get("Đánh giá", ""))).strip()
            keywords = str(row.get("Từ Khóa", "")).strip()

            if not name or name == "nan":
                continue

            dest = _extract_destination(f"{province} {name}")
            if dest == "Unknown":
                dest = province.strip() or "Vietnam"

            q = f"Địa điểm tham quan tại {province}: {name}"
            a_parts = []
            if description and description != "nan":
                a_parts.append(description)
            if rating and rating not in ("nan", ""):
                a_parts.append(f"Rating: {rating}/5")
            if keywords and keywords != "nan":
                a_parts.append(f"Tags: {keywords}")
            a = " | ".join(a_parts) if a_parts else f"Địa điểm tham quan tại {province}"

            records.append(
                {
                    "Question": q,
                    "Answer": a,
                    "Destination": dest,
                    "Category": _extract_category(f"{name} {description} {keywords}"),
                }
            )
        except Exception:
            continue
    print(f"[DATA] DataSet.xlsx → {len(records)} records")
    return pd.DataFrame(records) if records else None


def _process_travel_details(df: pd.DataFrame) -> pd.DataFrame:
    """Travel_details_dataset.csv — 139 trips QT có cost thực."""
    if df is None or len(df) == 0:
        return None
    records = []
    for _, row in df.iterrows():
        try:
            dest = str(row.get("Destination", "")).strip()
            acc_cost = row.get("Accommodation cost", "")
            trn_cost = row.get("Transportation cost", "")
            duration = row.get("Duration (days)", "")
            acc_type = str(row.get("Accommodation type", "")).strip()
            trn_type = str(row.get("Transportation type", "")).strip()

            if not dest or dest == "nan":
                continue

            dest_clean = dest.split(",")[0].strip()
            q = f"Chi phí chuyến đi {dest_clean} như thế nào?"
            parts = []
            if str(acc_cost) not in ("nan", ""):
                parts.append(f"Chi phí lưu trú: ${float(acc_cost):,.0f}")
            if str(trn_cost) not in ("nan", ""):
                parts.append(f"Chi phí di chuyển: ${float(trn_cost):,.0f}")
            if str(duration) not in ("nan", ""):
                parts.append(f"Thời gian: {duration} ngày")
            if acc_type and acc_type != "nan":
                parts.append(f"Loại lưu trú: {acc_type}")
            if trn_type and trn_type != "nan":
                parts.append(f"Phương tiện: {trn_type}")

            if not parts:
                continue

            records.append(
                {
                    "Question": q,
                    "Answer": ". ".join(parts),
                    "Destination": _extract_destination(dest_clean) or dest_clean,
                    "Category": "Budget",
                }
            )
        except Exception:
            continue
    print(f"[DATA] Travel details → {len(records)} records")
    return pd.DataFrame(records) if records else None


def _process_india_places(df: pd.DataFrame) -> pd.DataFrame:
    """Top_Indian_Places_to_Visit.csv — 325 điểm Ấn Độ."""
    if df is None or len(df) == 0:
        return None
    records = []
    for _, row in df.iterrows():
        try:
            name = str(row.get("Name", "")).strip()
            city = str(row.get("City", "")).strip()
            state = str(row.get("State", "")).strip()
            ptype = str(row.get("Type", "")).strip()
            rating = row.get("Google review rating", "")
            fee = row.get("Entrance Fee in INR", "")
            best_t = str(row.get("Best Time to visit", "")).strip()
            hrs = row.get("time needed to visit in hrs", "")

            if not name or name == "nan":
                continue

            q = f"Địa điểm tham quan {name} tại {city}, Ấn Độ"
            parts = [f"{name} là {ptype} tại {city}, {state}"]
            if str(rating) not in ("nan", ""):
                parts.append(f"Rating Google: {rating}/5")
            if (
                str(fee) not in ("nan", "")
                and float(str(fee).replace(",", "") or 0) > 0
            ):
                parts.append(f"Phí vào cửa: ₹{fee}")
            if best_t and best_t not in ("nan", "All", ""):
                parts.append(f"Thời điểm đẹp: {best_t}")
            if str(hrs) not in ("nan", ""):
                parts.append(f"Thời gian tham quan: ~{hrs} giờ")

            records.append(
                {
                    "Question": q,
                    "Answer": ". ".join(parts),
                    "Destination": city,
                    "Category": _extract_category(f"{ptype} {name}"),
                }
            )
        except Exception:
            continue
    print(f"[DATA] India places → {len(records)} records")
    return pd.DataFrame(records) if records else None


def _process_flights_data(df: pd.DataFrame) -> pd.DataFrame:
    """flights.csv — Brazil domestic flights (dùng làm context giá vé)."""
    if df is None or len(df) == 0:
        return None
    records = []
    # Group by route để tránh quá nhiều records lặp lại
    try:
        df["price"] = pd.to_numeric(df.get("price", pd.Series()), errors="coerce")
        for dest, grp in df.groupby("to"):
            prices = grp["price"].dropna()
            if len(prices) == 0:
                continue
            q = f"Giá vé máy bay đến {dest}?"
            a = (
                f"Vé máy bay đến {dest}: "
                f"min=${prices.min():.0f}, avg=${prices.mean():.0f}, max=${prices.max():.0f} "
                f"(dữ liệu {len(prices)} chuyến bay)"
            )
            records.append(
                {
                    "Question": q,
                    "Answer": a,
                    "Destination": str(dest),
                    "Category": "Flight",
                }
            )
    except Exception as e:
        print(f"[DATA] Flights error: {e}")
    print(f"[DATA] Flights → {len(records)} records")
    return pd.DataFrame(records) if records else None


def _process_hotels_data(df: pd.DataFrame) -> pd.DataFrame:
    """hotels.csv — Brazil hotel pricing."""
    if df is None or len(df) == 0:
        return None
    records = []
    try:
        df["price"] = pd.to_numeric(df.get("price", pd.Series()), errors="coerce")
        for city, grp in df.groupby("place"):
            prices = grp["price"].dropna()
            if len(prices) == 0:
                continue
            q = f"Giá khách sạn tại {city}?"
            a = (
                f"Khách sạn tại {city}: "
                f"từ ${prices.min():.0f}/đêm, trung bình ${prices.mean():.0f}/đêm "
                f"(dữ liệu {len(prices)} booking)"
            )
            records.append(
                {
                    "Question": q,
                    "Answer": a,
                    "Destination": str(city),
                    "Category": "Hotel",
                }
            )
    except Exception as e:
        print(f"[DATA] Hotels error: {e}")
    print(f"[DATA] Hotels → {len(records)} records")
    return pd.DataFrame(records) if records else None


def _process_generic_csv(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """Generic handler cho các CSV khác."""
    if df is None or len(df) == 0:
        return None

    df = df.reset_index(drop=True)

    # Rename columns nếu cần
    col_map = {}
    for c in df.columns:
        cl = c.lower().strip()
        if "question" in cl and c != "Question":
            col_map[c] = "Question"
        elif "answer" in cl and c != "Answer":
            col_map[c] = "Answer"
        elif (
            any(x in cl for x in ["destination", "place", "location"])
            and c != "Destination"
        ):
            col_map[c] = "Destination"
        elif any(x in cl for x in ["category", "type"]) and c != "Category":
            col_map[c] = "Category"
    if col_map:
        df = df.rename(columns=col_map)

    # Nếu có Question/Answer sẵn
    if "Question" in df.columns and "Answer" in df.columns:
        df = df.dropna(subset=["Question", "Answer"])
        if "Destination" not in df.columns:
            df["Destination"] = (df["Question"] + " " + df["Answer"]).apply(
                _extract_destination
            )
        if "Category" not in df.columns:
            df["Category"] = (df["Question"] + " " + df["Answer"]).apply(
                _extract_category
            )
        print(f"[DATA] {filename} → {len(df)} records (Q&A format)")
        return df[["Question", "Answer", "Destination", "Category"]].copy()

    # Nếu có description column
    desc_cols = [
        c for c in df.columns if "description" in c.lower() or "desc" in c.lower()
    ]
    if desc_cols:
        records = []
        desc_col = desc_cols[0]
        name_cols = [
            c
            for c in df.columns
            if any(x in c.lower() for x in ["name", "title", "place"])
        ]
        name_col = name_cols[0] if name_cols else None
        for _, row in df.iterrows():
            try:
                desc = str(row.get(desc_col, "")).strip()
                if not desc or desc == "nan":
                    continue
                name = (
                    str(row.get(name_col, "this destination")).strip()
                    if name_col
                    else "this destination"
                )
                records.append(
                    {
                        "Question": f"Tell me about {name}",
                        "Answer": desc,
                        "Destination": _extract_destination(desc),
                        "Category": _extract_category(desc),
                    }
                )
            except Exception:
                continue
        if records:
            print(f"[DATA] {filename} → {len(records)} records (description format)")
            return pd.DataFrame(records)

    print(f"[DATA] {filename} → skipped (no usable format)")
    return None


def _combine_datasets() -> pd.DataFrame:
    all_dfs = []

    for key, filepath in DATA_FILES.items():
        if not filepath or not os.path.exists(filepath):
            continue
        df = _load_csv_file(filepath)
        if df is None or len(df) == 0:
            continue

        fname = os.path.basename(filepath).lower()

        if "dataset" in key.lower() or fname.endswith(".xlsx"):
            processed = _process_dataset_xlsx(df)
        elif "travel_details" in key.lower() or "travel details" in fname:
            processed = _process_travel_details(df)
        elif "top_places" in key.lower() or "indian" in fname:
            processed = _process_india_places(df)
        elif "flights" in key.lower() or "flight" in fname:
            processed = _process_flights_data(df)
        elif "hotels" in key.lower() or "hotel" in fname:
            processed = _process_hotels_data(df)
        elif key.lower() in ("tourism", "travel", "users", "history"):
            # tourism_dataset có location mã ngẫu nhiên → skip
            # Travel.csv là CRM không có destination → skip
            # users.csv, history_data.csv → generic
            if key.lower() in ("tourism", "travel"):
                print(f"[DATA] Skipping {key} (no useful destination data)")
                continue
            processed = _process_generic_csv(df, fname)
        else:
            processed = _process_generic_csv(df, fname)

        if processed is not None and len(processed) > 0:
            processed = processed.reset_index(drop=True)
            all_dfs.append(processed)

    if not all_dfs:
        # Tạo minimal placeholder nếu không có data file nào
        print("[DATA] ⚠️ Không tìm thấy data files. Tạo placeholder dataset.")
        placeholder = pd.DataFrame(
            [
                {
                    "Question": "Aria Travel AI là gì?",
                    "Answer": "Aria là hướng dẫn viên du lịch AI chuyên nghiệp, hỗ trợ lên kế hoạch du lịch Việt Nam và quốc tế.",
                    "Destination": "Vietnam",
                    "Category": "General",
                }
            ]
        )
        all_dfs.append(placeholder)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined = combined.reset_index(drop=True)
    print(f"[DATA] Combined {len(all_dfs)} datasets: {len(combined):,} total records")
    return combined


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("Question", "Answer"):
        if col not in df.columns:
            raise ValueError(f"Cột '{col}' thiếu!")

    df = df.reset_index(drop=True)
    df.dropna(subset=["Question", "Answer"], inplace=True)
    df = df.reset_index(drop=True)
    df["Question"] = df["Question"].astype(str).str.strip()
    df["Answer"] = df["Answer"].astype(str).str.strip()

    # Remove empty
    df = df[
        (df["Question"] != "")
        & (df["Answer"] != "")
        & (df["Question"] != "nan")
        & (df["Answer"] != "nan")
    ]
    df = df.reset_index(drop=True)

    if "Destination" not in df.columns:
        df["Destination"] = (df["Question"] + " " + df["Answer"]).apply(
            _extract_destination
        )
    if "Category" not in df.columns:
        df["Category"] = (df["Question"] + " " + df["Answer"]).apply(_extract_category)

    # Fix NaN
    df["Destination"] = df["Destination"].fillna("Unknown")
    df["Category"] = df["Category"].fillna("General")

    df["Combined"] = (
        df["Destination"].astype(str)
        + " "
        + df["Category"].astype(str)
        + " "
        + df["Question"]
        + " "
        + df["Answer"]
    )
    df = df.reset_index(drop=True)
    print(f"[DATA] Schema: {list(df.columns)}")
    print(
        f"[DATA] Destinations: {df['Destination'].nunique()} | Categories: {df['Category'].nunique()}"
    )
    return df


def load_dataset() -> pd.DataFrame:
    df = _combine_datasets()
    df = _normalize(df)
    df = df.reset_index(drop=True)
    print(f"[DATA] ✅ Total: {len(df):,} records (từ CSV/XLSX thực tế)")
    return df


def build_tfidf(df: pd.DataFrame):
    if "Combined" not in df.columns:
        return
    corpus = [doc for doc in df["Combined"].astype(str).str.strip().tolist() if doc]
    if not corpus:
        return
    vectorizer = TfidfVectorizer(
        max_features=20000, ngram_range=(1, 2), sublinear_tf=True, min_df=1
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    if not hasattr(vectorizer, "idf_"):
        return
    joblib.dump(vectorizer, TFIDF_VECTORIZER_PATH)
    joblib.dump(tfidf_matrix, TFIDF_MATRIX_PATH)
    print(f"[TFIDF] {tfidf_matrix.shape} → saved")


def build_embeddings(df: pd.DataFrame):
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(EMBEDDING_MODEL)
        embeddings = model.encode(
            df["Combined"].tolist(), show_progress_bar=True, batch_size=128
        )
        joblib.dump(embeddings, EMBEDDING_CACHE_PATH)
        print(f"[EMBED] {embeddings.shape} → saved")
    except Exception as e:
        print(f"[EMBED] ⚠️ {e}")


def build_label_encoder(df: pd.DataFrame):
    if "Destination" not in df.columns:
        return
    destinations = [
        d
        for d in df["Destination"].astype(str).str.strip().unique().tolist()
        if d and d != "Unknown"
    ]
    if not destinations:
        return
    le = LabelEncoder()
    le.fit(destinations)
    joblib.dump(le, LABEL_ENCODER_PATH)
    print(f"[LABEL] {len(le.classes_)} destinations → saved")


def build_all():
    print("\n[BUILD] Khởi động xây dựng artifacts...")
    df = load_dataset()
    for fn, name in [
        (build_tfidf, "TF-IDF"),
        (build_embeddings, "Embeddings"),
        (build_label_encoder, "Labels"),
    ]:
        try:
            fn(df)
        except Exception as e:
            print(f"[BUILD] ⚠️ {name} failed: {e}")
    print("\n✅ Build hoàn thành!")


if __name__ == "__main__":
    build_all()

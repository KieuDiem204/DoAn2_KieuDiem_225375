"""
data_engine.py — Khai thác dữ liệu THỰC TẾ từ các CSV/XLSX.
Viết lại dựa trên phân tích thực tế từng file:

FILE               | NỘI DUNG THỰC TẾ
------------------+---------------------------------------------------------
DataSet.xlsx       | 315 địa điểm VN, 63 tỉnh (5/tỉnh), mô tả TV, rating
Travel_details.csv | 139 trips QT: Paris/Tokyo/Bali..., cost thực, duration
Top_Indian.csv     | 325 điểm Ấn Độ: rating Google, phí vào, loại, giờ
flights.csv        | 271,888 chuyến bay Brazil nội địa (9 TP), 3 hãng, giá
hotels.csv         | 40,552 booking Brazil (9 TP), giá/đêm thực
users.csv          | 1,340 user profiles (JOIN với flights/hotels)
tourism_dataset.csv| Location là mã ngẫu nhiên — BỎ QUA
Travel.csv         | CRM bán hàng, không có destination — BỎ QUA
"""
import os, warnings
import pandas as pd
import numpy as np
from collections import Counter

warnings.filterwarnings("ignore")
from config import DATA_FILES


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════
def _load(path: str) -> pd.DataFrame | None:
    if not path or not os.path.exists(path):
        return None
    try:
        if path.endswith(".xlsx"):
            df = pd.read_excel(path, engine="openpyxl")
        else:
            for enc in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
                try:
                    df = pd.read_csv(path, encoding=enc)
                    break
                except Exception:
                    continue
            else:
                return None
        df.columns = [str(c).strip() for c in df.columns]
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"[ENGINE] Load error {os.path.basename(path)}: {e}")
        return None


def _clean_rating(val) -> float | None:
    """Parse '4.8/5' or 4.8 → float."""
    try:
        s = str(val).strip()
        if "/" in s:
            return float(s.split("/")[0])
        return float(s)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════
# EXTRACTOR 1 — DataSet.xlsx  →  Vietnam places per province
# ═══════════════════════════════════════════════════════════════════
def extract_vietnam_places(df: pd.DataFrame) -> dict:
    """
    Returns {province_name: [place_dict, ...]}
    Each place: {name, description, rating, keywords, province}
    """
    if df is None:
        return {}

    # Normalize province names → canonical city names
    _VN_PROVINCE_MAP = {
        "Lâm Đồng":            "Da Lat",
        "Cần Thơ":             "Can Tho",
        "Quảng Ninh":          "Ha Long",
        "Quang Ninh":          "Ha Long",
        "Quảng Nam":           "Hoi An",
        "Khánh Hòa":           "Nha Trang",
        "Kiên Giang":          "Phu Quoc",
        "Lào Cai":             "Sa Pa",
        "Thừa Thiên Huế":      "Hue",
        "Đà Nẵng":             "Da Nang",
        "Hà Nội":              "Hanoi",
        "TP. Hồ Chí Minh":    "Ho Chi Minh City",
        "Bà Rịa - Vũng Tàu":  "Vung Tau",
        "Bình Thuận":          "Mui Ne",
        "Bình Định":           "Quy Nhon",
        "Ninh Bình":           "Ninh Binh",
        "Hà Giang":            "Ha Giang",
        "Cao Bằng":            "Cao Bang",
        "Hải Phòng":           "Hai Phong",
        "Quảng Bình":          "Phong Nha",
        "Đắk Lắk":             "Buon Ma Thuot",
        "Gia Lai":             "Pleiku",
        "Kon Tum":             "Kon Tum",
        "An Giang":            "Chau Doc",
        "Bến Tre":             "Ben Tre",
        "Tiền Giang":          "My Tho",
        "Đồng Tháp":           "Sa Dec",
        "Vĩnh Long":           "Vinh Long",
        "Sóc Trăng":           "Soc Trang",
        "Bạc Liêu":            "Bac Lieu",
        "Cà Mau":              "Ca Mau",
        "Hậu Giang":           "Vi Thanh",
        "Trà Vinh":            "Tra Vinh",
        "Long An":             "Tan An",
        "Thanh Hóa":           "Thanh Hoa",
        "Nghệ An":             "Vinh",
        "Hà Tĩnh":             "Ha Tinh",
        "Quảng Trị":           "Dong Ha",
        "Quảng Ngãi":          "Quang Ngai",
        "Phú Yên":             "Tuy Hoa",
        "Ninh Thuận":          "Phan Rang",
        "Bình Dương":          "Thu Dau Mot",
        "Đồng Nai":            "Bien Hoa",
        "Tây Ninh":            "Tay Ninh",
        "Bình Phước":          "Dong Xoai",
        "Hòa Bình":            "Hoa Binh",
        "Sơn La":              "Son La",
        "Điện Biên":           "Dien Bien Phu",
        "Lai Châu":            "Lai Chau",
        "Yên Bái":             "Yen Bai",
        "Tuyên Quang":         "Tuyen Quang",
        "Hà Nam":              "Ha Nam",
        "Nam Đinh":            "Nam Dinh",
        "Thái Bình":           "Thai Binh",
        "Hưng Yên":            "Hung Yen",
        "Hải Dương":           "Hai Duong",
        "Bắc Ninh":            "Bac Ninh",
        "Vĩnh Phúc":           "Vinh Phuc",
        "Bắc Giang":           "Bac Giang",
        "Bắc Kạn":             "Bac Kan",
        "Thái Nguyên":         "Thai Nguyen",
        "Lạng Sơn":            "Lang Son",
        "Phú Thọ":             "Viet Tri",
    }

    result = {}
    for _, row in df.iterrows():
        province_raw = str(row.get("Vị trí", "")).strip()
        name         = str(row.get("Tên địa điểm", "")).strip()
        description  = str(row.get("Mô tả", "")).strip()
        rating_raw   = row.get("Đánh giá ", row.get("Đánh giá", ""))
        keywords_raw = str(row.get("Từ Khóa", "")).strip()

        if not name or name == "nan":
            continue

        rating = _clean_rating(rating_raw)
        keywords = [k.strip().strip('"').strip() for k in keywords_raw.split(",")
                    if k.strip() and k.strip() not in ["nan", ""]]

        # Map province → canonical destination
        canonical = _VN_PROVINCE_MAP.get(province_raw, province_raw)

        place = {
            "name":        name,
            "description": description if description != "nan" else "",
            "rating":      rating,
            "keywords":    keywords,
            "province":    province_raw,
            "destination": canonical,
        }

        if canonical not in result:
            result[canonical] = {"destination": canonical, "province": province_raw, "places": []}
        result[canonical]["places"].append(place)

    # Add avg rating per destination
    for dest, info in result.items():
        ratings = [p["rating"] for p in info["places"] if p["rating"]]
        if ratings:
            info["avg_rating"] = round(sum(ratings) / len(ratings), 2)
        # Collect all keywords
        all_kw = []
        for p in info["places"]:
            all_kw.extend(p["keywords"])
        info["top_keywords"] = [k for k, _ in Counter(all_kw).most_common(10) if k]

    print(f"[ENGINE] Vietnam places: {len(result)} destinations, {sum(len(v['places']) for v in result.values())} total places")
    return result


# ═══════════════════════════════════════════════════════════════════
# EXTRACTOR 2 — Travel_details_dataset.csv  →  International trip costs
# ═══════════════════════════════════════════════════════════════════
def extract_international_trips(df: pd.DataFrame) -> dict:
    """
    Returns {city_name: {acc_cost_avg, acc_cost_min, acc_cost_max,
                          transport_cost_avg, total_avg, duration_avg,
                          accommodation_types, transport_types, sample_count}}
    """
    if df is None:
        return {}

    df = df.copy()
    df["Accommodation cost"]  = pd.to_numeric(df.get("Accommodation cost", pd.Series()), errors="coerce")
    df["Transportation cost"] = pd.to_numeric(df.get("Transportation cost", pd.Series()), errors="coerce")
    df["Duration (days)"]     = pd.to_numeric(df.get("Duration (days)", pd.Series()), errors="coerce")

    def _normalize_dest(raw):
        if pd.isna(raw):
            return None
        # strip country suffix
        d = str(raw).split(",")[0].strip()
        # common clean-ups
        replacements = {
            " (SC)":"", " (BH)":"", " (RJ)":"", ", UK":"", ", USA":"",
            ", AUS":"", ", Aus":"", ", SA":"", ", South Africa":"",
            " United Arab Emirates":"",
        }
        for k, v in replacements.items():
            d = d.replace(k, v)
        d = d.strip()
        # merge variants
        _MERGE = {
            "Bali":          "Bali",
            "Tokyo":         "Tokyo",
            "Paris":         "Paris",
            "Sydney":        "Sydney",
            "Rome":          "Rome",
            "New York":      "New York",
            "New York City": "New York",
            "London":        "London",
            "Bangkok":       "Bangkok",
            "Barcelona":     "Barcelona",
            "Rio de Janeiro":"Rio de Janeiro",
            "Cape Town":     "Cape Town",
            "Cancun":        "Cancun",
            "Amsterdam":     "Amsterdam",
            "Phuket":        "Phuket",
            "Dubai":         "Dubai",
            "Vancouver":     "Vancouver",
            "Seoul":         "Seoul",
            "Santorini":     "Santorini",
            "Phnom Penh":    "Phnom Penh",
            "Athens":        "Athens",
            "Auckland":      "Auckland",
            "Honolulu":      "Honolulu",
            "Berlin":        "Berlin",
            "Marrakech":     "Marrakech",
            "Edinburgh":     "Edinburgh",
            "Los Angeles":   "Los Angeles",
            "Hawaii":        "Hawaii",
        }
        return _MERGE.get(d, d)

    df["_dest"] = df["Destination"].apply(_normalize_dest)
    df = df.dropna(subset=["_dest"])

    result = {}
    for dest, grp in df.groupby("_dest"):
        acc  = grp["Accommodation cost"].dropna()
        trn  = grp["Transportation cost"].dropna()
        dur  = grp["Duration (days)"].dropna()
        n    = len(grp)

        entry = {
            "destination":   dest,
            "sample_count":  n,
        }
        if len(acc):
            entry["acc_cost_avg"] = round(float(acc.mean()), 0)
            entry["acc_cost_min"] = round(float(acc.min()), 0)
            entry["acc_cost_max"] = round(float(acc.max()), 0)
        if len(trn):
            entry["transport_cost_avg"] = round(float(trn.mean()), 0)
            entry["transport_cost_min"] = round(float(trn.min()), 0)
            entry["transport_cost_max"] = round(float(trn.max()), 0)
        if len(acc) and len(trn):
            combined = acc.reset_index(drop=True) + trn.reset_index(drop=True)
            entry["total_cost_avg"] = round(float(combined.mean()), 0)
        if len(dur):
            entry["duration_avg"]  = round(float(dur.mean()), 1)
            entry["duration_range"] = f"{int(dur.min())}–{int(dur.max())} ngày"

        # Accommodation types
        if "Accommodation type" in grp.columns:
            types = grp["Accommodation type"].dropna().value_counts()
            if len(types):
                entry["accommodation_types"] = types.index.tolist()

        # Transport types
        if "Transportation type" in grp.columns:
            ttypes = grp["Transportation type"].dropna().value_counts()
            if len(ttypes):
                entry["transport_types"] = ttypes.index.tolist()

        # Nationality
        if "Traveler nationality" in grp.columns:
            nats = grp["Traveler nationality"].dropna().value_counts().head(5)
            if len(nats):
                entry["visitor_nationalities"] = nats.index.tolist()

        result[dest] = entry

    print(f"[ENGINE] International trips: {len(result)} destinations from {len(df)} records")
    return result


# ═══════════════════════════════════════════════════════════════════
# EXTRACTOR 3 — Top_Indian_Places_to_Visit.csv  →  India attractions
# ═══════════════════════════════════════════════════════════════════
def extract_india_places(df: pd.DataFrame) -> dict:
    """Returns {city: {attractions: [...], avg_rating, avg_fee}}"""
    if df is None:
        return {}

    result = {}
    for _, row in df.iterrows():
        city = str(row.get("City", "")).strip()
        if not city or city == "nan":
            continue

        place = {
            "name":           str(row.get("Name", "")).strip(),
            "type":           str(row.get("Type", "")).strip(),
            "significance":   str(row.get("Significance", "")).strip(),
            "rating":         float(row["Google review rating"]) if pd.notna(row.get("Google review rating")) else None,
            "entrance_fee":   int(row["Entrance Fee in INR"])    if pd.notna(row.get("Entrance Fee in INR")) else 0,
            "best_time":      str(row.get("Best Time to visit", "")).strip(),
            "visit_hours":    float(row["time needed to visit in hrs"]) if pd.notna(row.get("time needed to visit in hrs")) else None,
            "state":          str(row.get("State", "")).strip(),
            "zone":           str(row.get("Zone", "")).strip(),
        }
        if place["name"] == "nan":
            continue

        if city not in result:
            result[city] = {"destination": city, "attractions": []}
        result[city]["attractions"].append(place)

    for city, info in result.items():
        ratings = [p["rating"] for p in info["attractions"] if p["rating"]]
        if ratings:
            info["avg_rating"] = round(sum(ratings) / len(ratings), 2)
        fees = [p["entrance_fee"] for p in info["attractions"] if p["entrance_fee"] and p["entrance_fee"] > 0]
        if fees:
            info["avg_entrance_fee_inr"] = round(sum(fees) / len(fees), 0)

    print(f"[ENGINE] India places: {len(result)} cities, {sum(len(v['attractions']) for v in result.values())} attractions")
    return result


# ═══════════════════════════════════════════════════════════════════
# EXTRACTOR 4 — flights.csv  →  Brazil flight pricing (reference)
# ═══════════════════════════════════════════════════════════════════
def extract_brazil_flights(df: pd.DataFrame) -> dict:
    """
    Returns route-level stats. Brazil cities only.
    Used as reference for international flight pricing patterns.
    """
    if df is None:
        return {}

    df = df.copy()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["time"]  = pd.to_numeric(df["time"],  errors="coerce")

    result = {}
    for dest, grp in df.groupby("to"):
        prices = grp["price"].dropna()
        times  = grp["time"].dropna()
        entry  = {
            "destination": dest,
            "sample_count": len(grp),
            "price_min":   round(float(prices.min()), 2)  if len(prices) else None,
            "price_avg":   round(float(prices.mean()), 2) if len(prices) else None,
            "price_max":   round(float(prices.max()), 2)  if len(prices) else None,
            "duration_avg_hr": round(float(times.mean()), 2) if len(times) else None,
            "agencies":    grp["agency"].dropna().value_counts().index.tolist()[:3],
            "flight_types": grp["flightType"].dropna().value_counts().index.tolist(),
        }
        # Per flightType
        type_stats = {}
        for ft, fg in grp.groupby("flightType"):
            fp = fg["price"].dropna()
            if len(fp):
                type_stats[ft] = {
                    "avg": round(float(fp.mean()), 2),
                    "min": round(float(fp.min()), 2),
                    "max": round(float(fp.max()), 2),
                }
        entry["price_by_class"] = type_stats
        result[dest] = entry

    print(f"[ENGINE] Brazil flights: {len(result)} routes from {len(df):,} records")
    return result


# ═══════════════════════════════════════════════════════════════════
# EXTRACTOR 5 — hotels.csv  →  Brazil hotel pricing (reference)
# ═══════════════════════════════════════════════════════════════════
def extract_brazil_hotels(df: pd.DataFrame) -> dict:
    """
    Returns per-city hotel stats. Brazil only.
    """
    if df is None:
        return {}

    df = df.copy()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    df["days"]  = pd.to_numeric(df["days"],  errors="coerce")

    result = {}
    for city, grp in df.groupby("place"):
        prices = grp["price"].dropna()
        result[city] = {
            "destination":  city,
            "sample_count": len(grp),
            "price_per_night": round(float(prices.mean()), 2) if len(prices) else None,
            "price_min":    round(float(prices.min()), 2)     if len(prices) else None,
            "price_max":    round(float(prices.max()), 2)     if len(prices) else None,
            "hotels":       grp["name"].dropna().unique().tolist(),
            "avg_stay_days": round(float(grp["days"].mean()), 1) if len(grp["days"].dropna()) else None,
        }

    print(f"[ENGINE] Brazil hotels: {len(result)} cities from {len(df):,} records")
    return result


# ═══════════════════════════════════════════════════════════════════
# MAIN ENGINE CLASS
# ═══════════════════════════════════════════════════════════════════
class DataEngine:
    """
    Loads all datasets once, exposes structured query methods.
    Honest about what data exists vs what must be estimated.
    """

    def __init__(self):
        print("[ENGINE] Loading all datasets...")
        self._vn_places:       dict = {}  # DataSet.xlsx
        self._intl_trips:      dict = {}  # Travel_details.csv
        self._india_places:    dict = {}  # Top_Indian_Places.csv
        self._brazil_flights:  dict = {}  # flights.csv
        self._brazil_hotels:   dict = {}  # hotels.csv
        self._load_all()
        self._print_summary()

    def _load_all(self):
        paths = DATA_FILES
        # DataSet.xlsx
        df = _load(paths.get("dataset", ""))
        if df is not None:
            self._vn_places = extract_vietnam_places(df)

        # Travel_details
        df = _load(paths.get("travel_details", ""))
        if df is not None:
            self._intl_trips = extract_international_trips(df)

        # Top Indian Places
        df = _load(paths.get("top_places", ""))
        if df is not None:
            self._india_places = extract_india_places(df)

        # flights.csv (Brazil)
        df = _load(paths.get("flights", ""))
        if df is not None:
            self._brazil_flights = extract_brazil_flights(df)

        # hotels.csv (Brazil)
        df = _load(paths.get("hotels", ""))
        if df is not None:
            self._brazil_hotels = extract_brazil_hotels(df)

    def _print_summary(self):
        print(f"""
[ENGINE] ✅ Data loaded:
  - Vietnam destinations: {len(self._vn_places)} (từ DataSet.xlsx)
  - International trips:  {len(self._intl_trips)} destinations (từ Travel_details.csv)
  - India attractions:    {len(self._india_places)} cities (từ Top_Indian_Places.csv)
  - Brazil flight routes: {len(self._brazil_flights)} (tham chiếu)
  - Brazil hotel cities:  {len(self._brazil_hotels)} (tham chiếu)
""")

    # ── Public: all destinations ──────────────────────────────
    def all_destinations(self) -> list[str]:
        s = set()
        s.update(self._vn_places.keys())
        s.update(self._intl_trips.keys())
        s.update(self._india_places.keys())
        return sorted([d for d in s if d])

    def has_data(self, destination: str) -> dict[str, bool]:
        """Returns which data types are available for a destination."""
        return {
            "vn_places":    destination in self._vn_places,
            "intl_trips":   destination in self._intl_trips,
            "india_places": destination in self._india_places,
            "brazil_flights": destination in self._brazil_flights,
            "brazil_hotels":  destination in self._brazil_hotels,
        }

    # ── Vietnam places query ──────────────────────────────────
    def get_vn_destination(self, destination: str) -> dict | None:
        """Get Vietnam destination info with actual place names."""
        # Try direct match
        if destination in self._vn_places:
            return self._vn_places[destination]
        # Fuzzy match
        dest_low = destination.lower()
        for k, v in self._vn_places.items():
            if dest_low in k.lower() or k.lower() in dest_low:
                return v
            if dest_low in v.get("province","").lower():
                return v
        return None

    # ── International trips query ─────────────────────────────
    def get_intl_destination(self, destination: str) -> dict | None:
        if destination in self._intl_trips:
            return self._intl_trips[destination]
        dest_low = destination.lower()
        for k, v in self._intl_trips.items():
            if dest_low in k.lower() or k.lower() in dest_low:
                return v
        return None

    # ── India places query ────────────────────────────────────
    def get_india_city(self, city: str) -> dict | None:
        if city in self._india_places:
            return self._india_places[city]
        city_low = city.lower()
        for k, v in self._india_places.items():
            if city_low in k.lower() or k.lower() in city_low:
                return v
        return None

    # ══════════════════════════════════════════════════════════
    # CONTEXT BUILDER FOR LLM — chỉ inject dữ liệu có thật
    # ══════════════════════════════════════════════════════════
    def build_context_for_llm(self, destination: str, lang: str = "vi") -> str:
        """
        Build factual data block to inject into LLM prompt.
        Clearly labels: data từ CSV vs ước tính.
        """
        sections = []
        found_anything = False

        dest_norm = destination.strip()

        # ── Vietnam places (DataSet.xlsx) ──
        vn = self.get_vn_destination(dest_norm)
        if vn and vn.get("places"):
            found_anything = True
            places = vn["places"]
            section = [f"📍 DỮ LIỆU ĐỊA ĐIỂM THAM QUAN TẠI {dest_norm.upper()} (nguồn: DataSet.xlsx)"]
            section.append(f"Tỉnh/Thành: {vn.get('province','')}")
            section.append(f"Số địa điểm trong database: {len(places)}")
            if "avg_rating" in vn:
                section.append(f"Rating trung bình: {vn['avg_rating']:.1f}/5 ⭐")
            section.append("\nCác địa điểm nổi bật (dữ liệu thực từ database):")
            for p in places:
                line = f"  • {p['name']}"
                if p.get("rating"):
                    line += f" [{p['rating']}/5]"
                if p.get("description"):
                    line += f" — {p['description'][:120]}"
                if p.get("keywords"):
                    kw_str = ", ".join(p["keywords"][:5])
                    if kw_str:
                        line += f" | Tags: {kw_str}"
                section.append(line)
            sections.append("\n".join(section))

        # ── International trip costs (Travel_details.csv) ──
        intl = self.get_intl_destination(dest_norm)
        if intl:
            found_anything = True
            section = [f"💰 CHI PHÍ CHUYẾN ĐI {dest_norm.upper()} (nguồn: Travel_details_dataset.csv — {intl['sample_count']} chuyến đi thực tế)"]
            if "acc_cost_avg" in intl:
                section.append(f"  Lưu trú: avg=${intl['acc_cost_avg']:,.0f} | min=${intl['acc_cost_min']:,.0f} | max=${intl['acc_cost_max']:,.0f}")
            if "transport_cost_avg" in intl:
                section.append(f"  Di chuyển: avg=${intl['transport_cost_avg']:,.0f} | min=${intl['transport_cost_min']:,.0f} | max=${intl['transport_cost_max']:,.0f}")
            if "total_cost_avg" in intl:
                section.append(f"  Tổng chi phí trung bình: ${intl['total_cost_avg']:,.0f}/chuyến")
            if "duration_avg" in intl:
                section.append(f"  Thời gian TB: {intl['duration_avg']:.1f} ngày ({intl.get('duration_range','')})")
            if "accommodation_types" in intl:
                section.append(f"  Loại lưu trú phổ biến: {', '.join(intl['accommodation_types'][:4])}")
            if "transport_types" in intl:
                section.append(f"  Phương tiện phổ biến: {', '.join(intl['transport_types'][:3])}")
            if "visitor_nationalities" in intl:
                section.append(f"  Khách chủ yếu từ: {', '.join(intl['visitor_nationalities'][:4])}")
            sections.append("\n".join(section))

        # ── India places (Top_Indian_Places.csv) ──
        india = self.get_india_city(dest_norm)
        if india and india.get("attractions"):
            found_anything = True
            attrs = india["attractions"]
            section = [f"🏛️ ĐIỂM THAM QUAN TẠI {dest_norm.upper()} - ẤN ĐỘ (nguồn: Top_Indian_Places.csv — {len(attrs)} nơi)"]
            if "avg_rating" in india:
                section.append(f"  Rating TB: {india['avg_rating']:.2f}/5")
            section.append("  Danh sách địa điểm (dữ liệu thực):")
            for a in attrs[:10]:
                line = f"    • {a['name']} [{a['type']}]"
                if a.get("rating"):
                    line += f" ⭐{a['rating']}"
                if a.get("entrance_fee", 0) > 0:
                    line += f" | Phí: ₹{a['entrance_fee']}"
                if a.get("best_time") and a["best_time"] not in ["nan","All"]:
                    line += f" | Giờ đẹp: {a['best_time']}"
                if a.get("visit_hours"):
                    line += f" | ~{a['visit_hours']}h"
                section.append(line)
            sections.append("\n".join(section))

        if not found_anything:
            return f"[ENGINE] Không có dữ liệu CSV cho '{dest_norm}'. LLM cần dùng kiến thức chung và ghi chú rõ."

        return "\n\n".join(sections)

    # ══════════════════════════════════════════════════════════
    # COMPARISON — dùng Travel_details cho quốc tế
    # ══════════════════════════════════════════════════════════
    def compare_destinations(self, dest_list: list[str]) -> str:
        """Compare based on real Travel_details data."""
        data_dests = []
        no_data    = []
        for d in dest_list:
            intl = self.get_intl_destination(d)
            vn   = self.get_vn_destination(d)
            if intl:
                data_dests.append(("intl", d, intl))
            elif vn:
                data_dests.append(("vn", d, vn))
            else:
                no_data.append(d)

        if not data_dests:
            return f"Không có dữ liệu CSV cho: {', '.join(dest_list)}. So sánh dựa trên kiến thức chung."

        lines = ["📊 **SO SÁNH ĐIỂM ĐẾN** (nguồn: Travel_details_dataset.csv)\n"]

        # Table header
        headers = ["Tiêu chí"] + [d for _, d, _ in data_dests]
        if no_data:
            headers += [f"{d} (*ước tính)" for d in no_data]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "---|" * len(headers))

        def _val(dtype, d, info, field):
            if dtype == "intl" and field in info:
                return f"${info[field]:,.0f}"
            return "Không có data"

        rows_def = [
            ("💰 Lưu trú TB",    "acc_cost_avg"),
            ("✈️ Di chuyển TB",  "transport_cost_avg"),
            ("💵 Tổng TB",       "total_cost_avg"),
            ("🗓️ Số ngày TB",    "duration_avg"),
        ]
        for label, field in rows_def:
            row = [label]
            for dtype, d, info in data_dests:
                if dtype == "intl" and field in info:
                    if field == "duration_avg":
                        row.append(f"{info[field]:.1f} ngày")
                    else:
                        row.append(f"${info[field]:,.0f}")
                elif dtype == "vn":
                    row.append("VN (không có cost data)")
                else:
                    row.append("N/A")
            if no_data:
                row += ["N/A"] * len(no_data)
            lines.append("| " + " | ".join(row) + " |")

        # Accommodation types
        row = ["🏨 Lưu trú phổ biến"]
        for dtype, d, info in data_dests:
            if dtype == "intl" and "accommodation_types" in info:
                row.append(", ".join(info["accommodation_types"][:2]))
            else:
                row.append("N/A")
        if no_data:
            row += ["N/A"] * len(no_data)
        lines.append("| " + " | ".join(row) + " |")

        # Rating (VN data)
        row = ["⭐ Rating"]
        for dtype, d, info in data_dests:
            if dtype == "vn" and "avg_rating" in info:
                row.append(f"{info['avg_rating']:.1f}/5")
            else:
                row.append("N/A")
        if no_data:
            row += ["N/A"] * len(no_data)
        lines.append("| " + " | ".join(row) + " |")

        lines.append(f"\n📌 Dữ liệu từ: Travel_details_dataset.csv")
        if no_data:
            lines.append(f"⚠️ *Không có data CSV cho: {', '.join(no_data)} — cần LLM ước tính*")

        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════
    # RECOMMENDATION — xếp hạng theo data thực
    # ══════════════════════════════════════════════════════════
    def recommend_destinations(
        self,
        budget: float = None,
        duration_days: int = None,
        activity_type: str = None,
        top_n: int = 5,
    ) -> list[dict]:
        """Rank destinations by real Travel_details data."""
        candidates = []

        for dest, info in self._intl_trips.items():
            score   = 0.0
            reasons = []
            total   = info.get("total_cost_avg")

            # Budget filter
            if budget and total:
                if total <= budget:
                    score += (budget - total) / budget * 40
                    reasons.append(f"Trong budget (${total:,.0f})")
                else:
                    continue

            # Duration fit
            if duration_days and "duration_avg" in info:
                diff   = abs(info["duration_avg"] - duration_days)
                score += max(0, 20 - diff * 3)
                reasons.append(f"Phù hợp {info['duration_avg']:.0f} ngày")

            # Sample count confidence
            score += min(15, info.get("sample_count", 0) * 1.0)

            candidates.append({
                "destination":         dest,
                "score":               score,
                "reasons":             reasons,
                "total_cost_avg":      total,
                "acc_cost_avg":        info.get("acc_cost_avg"),
                "transport_cost_avg":  info.get("transport_cost_avg"),
                "duration_avg":        info.get("duration_avg"),
                "accommodation_types": info.get("accommodation_types", [])[:3],
                "sample_count":        info.get("sample_count", 0),
                "data_source":         "Travel_details_dataset.csv",
            })

        # Also add VN destinations (no cost data but notable)
        for dest, info in self._vn_places.items():
            if dest in self._intl_trips:
                continue  # already handled
            if activity_type:
                kws = " ".join(info.get("top_keywords", [])).lower()
                if activity_type.lower() not in kws:
                    continue
            candidates.append({
                "destination":   dest,
                "score":         info.get("avg_rating", 3.5) * 5,
                "reasons":       ["Địa điểm VN có trong DataSet.xlsx"],
                "total_cost_avg": None,
                "avg_rating":    info.get("avg_rating"),
                "places_count":  len(info.get("places", [])),
                "data_source":   "DataSet.xlsx",
            })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_n]

    def format_recommendation(self, candidates: list[dict], lang: str = "vi") -> str:
        if not candidates:
            return "Không tìm thấy điểm đến phù hợp với tiêu chí."

        lines = ["🌟 **GỢI Ý ĐIỂM ĐẾN** (dựa trên dữ liệu thực)\n"]
        for i, c in enumerate(candidates, 1):
            dest = c["destination"]
            src  = c.get("data_source", "")
            lines.append(f"**{i}. {dest}** *(nguồn: {src})*")
            if c.get("total_cost_avg"):
                lines.append(f"   💰 Tổng chi phí TB: ${c['total_cost_avg']:,.0f}/chuyến")
            if c.get("acc_cost_avg"):
                lines.append(f"   🏨 Lưu trú TB: ${c['acc_cost_avg']:,.0f}")
            if c.get("transport_cost_avg"):
                lines.append(f"   ✈️ Di chuyển TB: ${c['transport_cost_avg']:,.0f}")
            if c.get("duration_avg"):
                lines.append(f"   🗓️ Thời gian TB: {c['duration_avg']:.0f} ngày")
            if c.get("accommodation_types"):
                lines.append(f"   🛏️ Lưu trú: {', '.join(c['accommodation_types'])}")
            if c.get("avg_rating"):
                lines.append(f"   ⭐ Rating: {c['avg_rating']}/5")
            if c.get("reasons"):
                lines.append(f"   ✅ {'; '.join(c['reasons'])}")
            if c.get("sample_count"):
                lines.append(f"   📊 Mẫu: {c['sample_count']} chuyến đi thực tế")
            lines.append("")

        return "\n".join(lines)

    # ── Brazil reference (for pricing context) ───────────────
    def get_brazil_flight_info(self, city: str) -> dict | None:
        return self._brazil_flights.get(city)

    def get_brazil_hotel_info(self, city: str) -> dict | None:
        return self._brazil_hotels.get(city)

    def get_stats_summary(self) -> str:
        """Human-readable data coverage summary."""
        return (
            f"📊 **Dữ liệu thực trong hệ thống:**\n"
            f"  🇻🇳 Địa điểm Việt Nam: **{sum(len(v['places']) for v in self._vn_places.values())} địa điểm** tại **{len(self._vn_places)} tỉnh/thành**\n"
            f"  🌍 Chuyến đi quốc tế: **{sum(v['sample_count'] for v in self._intl_trips.values())} chuyến** tại **{len(self._intl_trips)} điểm đến**\n"
            f"  🇮🇳 Địa điểm Ấn Độ: **{sum(len(v['attractions']) for v in self._india_places.values())} nơi** tại **{len(self._india_places)} thành phố**\n"
            f"  ✈️ Brazil flights (tham chiếu): **{sum(v['sample_count'] for v in self._brazil_flights.values()):,} chuyến** | "
            f"  🏨 Brazil hotels (tham chiếu): **{sum(v['sample_count'] for v in self._brazil_hotels.values()):,} booking**"
        )


# ═══════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════
_engine_instance: DataEngine | None = None

def get_engine() -> DataEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = DataEngine()
    return _engine_instance
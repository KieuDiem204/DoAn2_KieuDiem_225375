"""
hotel_map_service.py — Bản đồ khách sạn interactive v2.0

Architecture:
  - Backend: Overpass API (OSM) để lấy khách sạn thực → AI fallback
  - Frontend: streamlit.components.v1.html() → iframe riêng → Leaflet.js chạy đúng
  - UX: Click khách sạn trong list → map fly to + mở popup
  - Center marker (đỏ) = điểm du lịch, Hotel markers (màu theo tier)
"""

import json
import re
import warnings
import requests

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════
# DESTINATION CENTER COORDINATES
# ══════════════════════════════════════════════════════════════════
_DEST_COORDS: dict[str, tuple[float, float]] = {
    "Da Lat": (11.9404, 108.4583),
    "Can Tho": (10.0452, 105.7469),
    "Ha Long": (20.9517, 107.0747),
    "Hanoi": (21.0285, 105.8542),
    "Hoi An": (15.8800, 108.3380),
    "Ho Chi Minh City": (10.8231, 106.6297),
    "Hue": (16.4637, 107.5909),
    "Mui Ne": (10.9333, 108.1000),
    "Nha Trang": (12.2388, 109.1967),
    "Phu Quoc": (10.2898, 103.9840),
    "Sa Pa": (22.3364, 103.8440),
    "Vung Tau": (10.3460, 107.0843),
    "Da Nang": (16.0544, 108.2022),
    "Quy Nhon": (13.7765, 109.2230),
    "Phan Thiet": (10.9295, 108.1009),
    "Ninh Binh": (20.2506, 105.9745),
    "Ha Giang": (22.8233, 104.9836),
    "Tay Ninh": (11.3100, 106.0980),
    "Hai Phong": (20.8449, 106.6881),
    "Phong Nha": (17.5883, 106.2835),
    "Cao Bang": (22.6660, 106.2577),
    "Buon Ma Thuot": (12.6667, 108.0500),
    "Pleiku": (13.9833, 108.0000),
    "Kon Tum": (14.3490, 108.0004),
    "Chau Doc": (10.7000, 105.1167),
    "Ca Mau": (9.1769, 105.1500),
    "Rach Gia": (10.0122, 105.0809),
    "Ben Tre": (10.2430, 106.3756),
    "My Tho": (10.3600, 106.3600),
    "Vinh Long": (10.2530, 105.9722),
    "Soc Trang": (9.6028, 105.9800),
    "Bac Lieu": (9.2940, 105.7280),
    "Tra Vinh": (9.9350, 106.3450),
    "Bangkok": (13.7563, 100.5018),
    "Bali": (-8.4095, 115.1889),
    "Singapore": (1.3521, 103.8198),
    "Tokyo": (35.6762, 139.6503),
    "Osaka": (34.6937, 135.5023),
    "Seoul": (37.5665, 126.9780),
    "Paris": (48.8566, 2.3522),
    "London": (51.5074, -0.1278),
    "Rome": (41.9028, 12.4964),
    "New York": (40.7128, -74.0060),
    "Sydney": (-33.8688, 151.2093),
    "Dubai": (25.2048, 55.2708),
    "Amsterdam": (52.3676, 4.9041),
    "Barcelona": (41.3851, 2.1734),
    "Berlin": (52.5200, 13.4050),
    "Phuket": (7.8804, 98.3923),
    "Chiang Mai": (18.7883, 98.9853),
    "Kuala Lumpur": (3.1390, 101.6869),
    "Siem Reap": (13.3671, 103.8448),
    "Hong Kong": (22.3193, 114.1694),
    "Taipei": (25.0330, 121.5654),
    "Santorini": (36.3932, 25.4615),
    "Maldives": (4.1755, 73.5093),
    "Vancouver": (49.2827, -123.1207),
    "Cancun": (21.1619, -86.8515),
}

_VN_DESTS = {
    "Da Lat",
    "Can Tho",
    "Ha Long",
    "Hanoi",
    "Hoi An",
    "Ho Chi Minh City",
    "Hue",
    "Mui Ne",
    "Nha Trang",
    "Phu Quoc",
    "Sa Pa",
    "Vung Tau",
    "Da Nang",
    "Quy Nhon",
    "Phan Thiet",
    "Ninh Binh",
    "Ha Giang",
    "Tay Ninh",
    "Hai Phong",
    "Phong Nha",
    "Cao Bang",
    "Buon Ma Thuot",
    "Pleiku",
    "Kon Tum",
    "Chau Doc",
    "Ca Mau",
    "Rach Gia",
    "Ben Tre",
    "My Tho",
    "Vinh Long",
    "Soc Trang",
    "Bac Lieu",
    "Tra Vinh",
}


# ══════════════════════════════════════════════════════════════════
# GEOCODING
# ══════════════════════════════════════════════════════════════════


def _get_center(destination: str) -> tuple[float, float] | None:
    if destination in _DEST_COORDS:
        return _DEST_COORDS[destination]
    try:
        q = destination + (", Vietnam" if destination in _VN_DESTS else "")
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 1},
            headers={"User-Agent": "AriaTravelBot/2.0"},
            timeout=6,
        )
        if r.status_code == 200:
            d = r.json()
            if d:
                return float(d[0]["lat"]), float(d[0]["lon"])
    except Exception as e:
        print(f"[MAP] Nominatim: {e}")
    return None


# ══════════════════════════════════════════════════════════════════
# OVERPASS — real OSM hotels
# ══════════════════════════════════════════════════════════════════


def _overpass_hotels(
    lat: float, lon: float, radius: int = 3000, limit: int = 12
) -> list[dict]:
    q = f"""
[out:json][timeout:12];
(
  node["tourism"~"hotel|guest_house|hostel|motel"](around:{radius},{lat},{lon});
  way["tourism"~"hotel|guest_house|hostel|motel"](around:{radius},{lat},{lon});
);
out center {limit * 4};
"""
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter", data={"data": q}, timeout=15
        )
        if r.status_code != 200:
            return []
        hotels, seen = [], set()
        for el in r.json().get("elements", []):
            tags = el.get("tags", {})
            name = (
                tags.get("name:vi") or tags.get("name:en") or tags.get("name") or ""
            ).strip()
            if not name or name in seen:
                continue
            seen.add(name)
            if el["type"] == "node":
                h_lat, h_lon = el.get("lat"), el.get("lon")
            else:
                c = el.get("center", {})
                h_lat, h_lon = c.get("lat"), c.get("lon")
            if not h_lat or not h_lon:
                continue
            stars = 0
            try:
                stars = int(float(tags.get("stars") or tags.get("star_rating") or 0))
            except Exception:
                pass
            hotels.append(
                {
                    "name": name,
                    "lat": float(h_lat),
                    "lon": float(h_lon),
                    "stars": stars,
                    "type": tags.get("tourism", "hotel"),
                    "address": (
                        f"{tags.get('addr:housenumber', '')} {tags.get('addr:street', '')}"
                    ).strip(),
                    "website": tags.get("website") or tags.get("contact:website") or "",
                    "phone": tags.get("phone") or tags.get("contact:phone") or "",
                    "price_range": "",
                    "highlight": "",
                    "source": "osm",
                }
            )
            if len(hotels) >= limit:
                break
        hotels.sort(key=lambda h: (-h["stars"], h["name"]))
        return hotels
    except Exception as e:
        print(f"[MAP] Overpass: {e}")
        return []


# ══════════════════════════════════════════════════════════════════
# AI FALLBACK — Claude suggests hotels with coordinates
# ══════════════════════════════════════════════════════════════════


def _ai_hotels(
    destination: str, lat: float, lon: float, lang: str = "vi"
) -> list[dict]:
    try:
        is_vn = destination in _VN_DESTS
        cur = "VNĐ/đêm" if is_vn else "USD/night"
        prompt = (
            f"Suggest 8 real well-known hotels in {destination} at various price levels.\n"
            f"Center coordinates: {lat},{lon}\n"
            f"Reply ONLY with a JSON array (no markdown):\n"
            f'[{{"name":"Hotel Name","stars":3,"type":"hotel","price_range":"x-y {cur}",'
            f'"address":"short address","lat_offset":0.002,"lon_offset":-0.001,'
            f'"highlight":"one short highlight"}}]\n'
            f"lat_offset/lon_offset: offset from center (-0.025 to 0.025).\n"
            f"Include: 2 budget(1-2★), 3 mid(3★), 3 luxury(4-5★)."
        )
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1200,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        if resp.status_code != 200:
            return []
        raw = ""
        for b in resp.json().get("content", []):
            if b.get("type") == "text":
                raw += b.get("text", "")
        raw = raw.replace("```json", "").replace("```", "").strip()
        m = re.search(r"\[[\s\S]*\]", raw)
        if not m:
            return []
        result = []
        for h in json.loads(m.group()):
            try:
                result.append(
                    {
                        "name": str(h.get("name", "")),
                        "lat": lat + float(h.get("lat_offset", 0)),
                        "lon": lon + float(h.get("lon_offset", 0)),
                        "stars": int(h.get("stars", 3)),
                        "type": str(h.get("type", "hotel")),
                        "address": str(h.get("address", "")),
                        "website": "",
                        "phone": "",
                        "price_range": str(h.get("price_range", "")),
                        "highlight": str(h.get("highlight", "")),
                        "source": "ai",
                    }
                )
            except Exception:
                continue
        return result
    except Exception as e:
        print(f"[MAP] AI fallback: {e}")
        return []


# ══════════════════════════════════════════════════════════════════
# FULL SELF-CONTAINED MAP HTML  (for st.components.v1.html)
# ══════════════════════════════════════════════════════════════════


def _build_full_html(
    destination: str,
    lat: float,
    lon: float,
    hotels: list[dict],
    lang: str,
) -> str:
    """
    Returns a complete standalone HTML page with:
    - Leaflet.js map (left panel, 55% width)
    - Scrollable hotel list (right panel, 45% width)
    - Click hotel in list → map flyTo + open popup
    - Center marker = destination (red dot)
    - Hotel markers colored by tier
    """

    def esc(s: str) -> str:
        return (
            (s or "")
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace("\n", " ")
        )

    def tier_color(stars: int) -> str:
        return "#c4845a" if stars >= 4 else ("#2d5555" if stars == 3 else "#4a7c6a")

    def type_vi(t: str) -> str:
        return {
            "hotel": "Khách sạn",
            "guest_house": "Nhà nghỉ",
            "hostel": "Hostel",
            "motel": "Motel",
        }.get(t, "Lưu trú")

    def type_en(t: str) -> str:
        return {
            "hotel": "Hotel",
            "guest_house": "Guest House",
            "hostel": "Hostel",
            "motel": "Motel",
        }.get(t, "Accommodation")

    type_fn = type_vi if lang == "vi" else type_en
    stars_fn = lambda s: "★" * min(s, 5) if s > 0 else ""

    title = (
        f"🏨 Khách sạn & Bản đồ — {destination}"
        if lang == "vi"
        else f"🏨 Hotels & Map — {destination}"
    )

    # ── JS hotel data array ──────────────────────────────────────
    hotels_js = json.dumps(
        [
            {
                "i": i,
                "name": h["name"],
                "lat": h["lat"],
                "lon": h["lon"],
                "stars": h.get("stars", 0),
                "type": h.get("type", "hotel"),
                "type_label": type_fn(h.get("type", "hotel")),
                "address": h.get("address", ""),
                "price": h.get("price_range", ""),
                "highlight": h.get("highlight", ""),
                "website": h.get("website", ""),
                "color": tier_color(h.get("stars", 0)),
                "stars_str": stars_fn(h.get("stars", 0)),
                "gmaps": f"https://www.google.com/maps/search/{h['name'].replace(' ', '+')}/@{h['lat']},{h['lon']},17z",
            }
            for i, h in enumerate(hotels)
        ],
        ensure_ascii=False,
    )

    dest_esc = esc(destination)
    lbl_center = "Trung tâm điểm đến" if lang == "vi" else "Destination center"
    lbl_hotels = "DANH SÁCH KHÁCH SẠN" if lang == "vi" else "HOTEL LIST"
    lbl_click = "Click để xem trên bản đồ" if lang == "vi" else "Click to show on map"
    lbl_osm = (
        "Bản đồ: © OpenStreetMap contributors"
        if lang == "vi"
        else "Map: © OpenStreetMap contributors"
    )
    lbl_gmaps = "Google Maps"
    lbl_web = "Website"
    lbl_results = (
        f"{len(hotels)} khách sạn" if lang == "vi" else f"{len(hotels)} hotels"
    )
    lbl_tier1 = "4-5★ Cao cấp" if lang == "vi" else "4-5★ Luxury"
    lbl_tier2 = "3★ Tầm trung" if lang == "vi" else "3★ Mid-range"
    lbl_tier3 = "1-2★ Budget"

    return f"""<!DOCTYPE html>
<html lang="{"vi" if lang == "vi" else "en"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
  font-family:'DM Sans',system-ui,sans-serif;
  background:#f8f6f2;
  height:100vh;overflow:hidden;
  display:flex;flex-direction:column;
}}

/* ── Top bar ── */
.topbar{{
  background:linear-gradient(135deg,#1a3a3a 0%,#2d5555 100%);
  padding:10px 16px 8px;flex-shrink:0;
}}
.topbar-title{{
  font-size:0.88rem;font-weight:600;color:white;
  font-family:'Cormorant Garamond',Georgia,serif;margin-bottom:5px;
}}
.legend{{display:flex;gap:12px;flex-wrap:wrap;}}
.legend-item{{
  display:flex;align-items:center;gap:4px;
  font-size:0.62rem;color:rgba(255,255,255,0.75);
}}
.legend-dot{{width:10px;height:10px;border-radius:50%;flex-shrink:0;}}

/* ── Main layout ── */
.layout{{display:flex;flex:1;overflow:hidden;}}

/* ── Map panel ── */
#map{{
  flex:1;min-width:0;height:100%;
  border-right:1px solid rgba(184,150,90,0.2);
}}

/* ── Hotel list panel ── */
.panel{{
  width:310px;flex-shrink:0;
  display:flex;flex-direction:column;
  background:#fff;overflow:hidden;
}}
.panel-header{{
  padding:10px 12px 8px;
  border-bottom:1px solid #f0ede8;
  background:#faf8f4;flex-shrink:0;
}}
.panel-label{{
  font-size:0.55rem;letter-spacing:2px;text-transform:uppercase;
  color:rgba(26,58,58,0.4);margin-bottom:3px;
}}
.panel-meta{{
  font-size:0.72rem;color:#888;
  display:flex;justify-content:space-between;align-items:center;
}}
.click-hint{{
  font-size:0.6rem;color:#b8965a;font-style:italic;
}}
.hotels-list{{
  overflow-y:auto;flex:1;padding:7px;
}}
.hotels-list::-webkit-scrollbar{{width:3px;}}
.hotels-list::-webkit-scrollbar-thumb{{background:#e8ddd0;border-radius:2px;}}

/* ── Hotel card ── */
.hotel-card{{
  display:flex;gap:9px;align-items:flex-start;
  background:#faf8f4;border:1px solid rgba(184,150,90,0.15);
  border-radius:9px;padding:9px 11px 9px 10px;
  margin-bottom:6px;cursor:pointer;
  transition:all 0.18s ease;
  text-decoration:none;color:inherit;
}}
.hotel-card:hover{{
  background:#fff;border-color:#c4845a;
  box-shadow:0 3px 12px rgba(196,132,90,0.18);
  transform:translateX(2px);
}}
.hotel-card.active{{
  background:#fff;border-color:#c4845a;
  box-shadow:0 3px 16px rgba(196,132,90,0.25);
  border-left:3px solid #c4845a;
}}
.card-num{{
  width:26px;height:26px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:0.68rem;font-weight:800;color:white;
  flex-shrink:0;margin-top:1px;
}}
.card-body{{flex:1;min-width:0;overflow:hidden;}}
.card-name{{
  font-size:0.78rem;font-weight:700;color:#1a3a3a;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}}
.card-type{{font-size:0.64rem;color:#888;margin-top:1px;}}
.card-price{{font-size:0.65rem;color:#c4845a;font-weight:600;margin-top:2px;}}
.card-hl{{font-size:0.62rem;color:#2d5555;font-style:italic;margin-top:1px;}}
.card-addr{{font-size:0.61rem;color:#aaa;margin-top:1px;}}
.card-links{{display:flex;gap:5px;margin-top:5px;flex-wrap:wrap;}}
.card-link{{
  font-size:0.6rem;padding:2px 8px;border-radius:4px;
  text-decoration:none;white-space:nowrap;
  transition:opacity 0.15s;
}}
.card-link:hover{{opacity:0.8;}}
.link-gmap{{background:#1a3a3a;color:white;}}
.link-web{{background:#c4845a;color:white;}}

/* ── Footer ── */
.footer{{
  padding:5px 12px;background:#faf8f4;
  border-top:1px solid #f0ede8;flex-shrink:0;
  font-size:0.58rem;color:#bbb;text-align:center;
}}
</style>
</head>
<body>

<!-- Top bar -->
<div class="topbar">
  <div class="topbar-title">{title}</div>
  <div class="legend">
    <div class="legend-item">
      <span class="legend-dot" style="background:#e74c3c;border:2px solid white;"></span>
      <span>{dest_esc}</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot" style="background:#c4845a;"></span>
      <span>{lbl_tier1}</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot" style="background:#2d5555;"></span>
      <span>{lbl_tier2}</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot" style="background:#4a7c6a;"></span>
      <span>{lbl_tier3}</span>
    </div>
  </div>
</div>

<!-- Main layout -->
<div class="layout">

  <!-- Map -->
  <div id="map"></div>

  <!-- Hotel list -->
  <div class="panel">
    <div class="panel-header">
      <div class="panel-label">{lbl_hotels}</div>
      <div class="panel-meta">
        <span>{lbl_results}</span>
        <span class="click-hint">👆 {lbl_click}</span>
      </div>
    </div>
    <div class="hotels-list" id="hotelList"></div>
    <div class="footer">{lbl_osm}</div>
  </div>

</div>

<script>
// ── Hotel data ──────────────────────────────────────────────────
var HOTELS = {hotels_js};
var CENTER = [{lat}, {lon}];
var DEST   = '{dest_esc}';
var LBL_CENTER = '{lbl_center}';
var LBL_GMAPS  = '{lbl_gmaps}';
var LBL_WEB    = '{lbl_web}';

// ── Init map ────────────────────────────────────────────────────
var map = L.map('map', {{
  center: CENTER,
  zoom: 14,
  zoomControl: true,
  scrollWheelZoom: true
}});

L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  maxZoom: 19
}}).addTo(map);

// ── Center marker (destination) ─────────────────────────────────
var centerIcon = L.divIcon({{
  className: '',
  html: '<div style="'
    + 'width:18px;height:18px;border-radius:50%;'
    + 'background:#e74c3c;border:3px solid white;'
    + 'box-shadow:0 3px 10px rgba(231,76,60,0.5);">'
    + '</div>',
  iconSize: [18,18], iconAnchor: [9,9], popupAnchor: [0,-12]
}});
L.marker(CENTER, {{icon: centerIcon}}).addTo(map)
  .bindPopup('<div style="font-family:system-ui;padding:2px;">'
    + '<strong style="color:#1a3a3a;font-size:0.9rem;">' + DEST + '</strong>'
    + '<br><span style="font-size:0.72rem;color:#888;">' + LBL_CENTER + '</span>'
    + '</div>');

// ── Hotel markers ────────────────────────────────────────────────
var markers = [];
var activeCard = null;

HOTELS.forEach(function(h) {{
  var icon = L.divIcon({{
    className: '',
    html: '<div style="'
      + 'background:' + h.color + ';'
      + 'width:30px;height:30px;border-radius:50%;'
      + 'display:flex;align-items:center;justify-content:center;'
      + 'box-shadow:0 3px 10px rgba(0,0,0,0.3);'
      + 'border:2px solid white;'
      + 'font-size:0.62rem;font-weight:800;color:white;'
      + 'cursor:pointer;'
      + '">' + (h.i + 1) + '</div>',
    iconSize: [30,30], iconAnchor: [15,15], popupAnchor: [0,-18]
  }});

  var popupContent = '<div style="min-width:220px;font-family:system-ui;line-height:1.55;">'
    + '<strong style="color:' + h.color + ';font-size:0.88rem;">' + h.name + '</strong>'
    + (h.stars_str
        ? '<div style="font-size:0.72rem;color:#888;margin-top:2px;">' + h.stars_str + ' ' + h.type_label + '</div>'
        : '<div style="font-size:0.72rem;color:#888;">' + h.type_label + '</div>')
    + (h.address ? '<div style="font-size:0.72rem;color:#666;margin-top:3px;">📍 ' + h.address + '</div>' : '')
    + (h.price   ? '<div style="font-size:0.73rem;color:#c4845a;font-weight:600;margin-top:3px;">💰 ' + h.price + '</div>' : '')
    + (h.highlight ? '<div style="font-size:0.7rem;color:#2d5555;font-style:italic;margin-top:3px;">✨ ' + h.highlight + '</div>' : '')
    + '<div style="margin-top:8px;display:flex;gap:5px;flex-wrap:wrap;">'
    + '<a href="' + h.gmaps + '" target="_blank" style="background:#1a3a3a;color:white;padding:3px 9px;border-radius:4px;font-size:0.68rem;text-decoration:none;">' + LBL_GMAPS + '</a>'
    + (h.website ? '<a href="' + h.website + '" target="_blank" style="background:#c4845a;color:white;padding:3px 9px;border-radius:4px;font-size:0.68rem;text-decoration:none;">' + LBL_WEB + '</a>' : '')
    + '</div>'
    + '</div>';

  var marker = L.marker([h.lat, h.lon], {{icon: icon}}).addTo(map);
  marker.bindPopup(popupContent, {{maxWidth: 300}});

  // Click marker → highlight list card
  marker.on('click', function() {{
    highlightCard(h.i);
  }});

  markers.push(marker);
}});

// ── Build hotel list ─────────────────────────────────────────────
var listEl = document.getElementById('hotelList');
HOTELS.forEach(function(h) {{
  var card = document.createElement('div');
  card.className = 'hotel-card';
  card.id = 'card-' + h.i;

  var addrHtml  = h.address  ? '<div class="card-addr">📍 ' + h.address + '</div>' : '';
  var priceHtml = h.price    ? '<div class="card-price">💰 ' + h.price + '</div>' : '';
  var hlHtml    = h.highlight? '<div class="card-hl">✨ ' + h.highlight + '</div>' : '';
  var linksHtml = '<div class="card-links">'
    + '<a class="card-link link-gmap" href="' + h.gmaps + '" target="_blank" onclick="event.stopPropagation()">🗺 ' + LBL_GMAPS + '</a>'
    + (h.website ? '<a class="card-link link-web" href="' + h.website + '" target="_blank" onclick="event.stopPropagation()">🌐 ' + LBL_WEB + '</a>' : '')
    + '</div>';

  card.innerHTML =
    '<div class="card-num" style="background:' + h.color + ';">' + (h.i+1) + '</div>'
    + '<div class="card-body">'
    + '<div class="card-name">' + h.name + '</div>'
    + '<div class="card-type">' + (h.stars_str ? h.stars_str + ' · ' : '') + h.type_label + '</div>'
    + priceHtml + hlHtml + addrHtml
    + linksHtml
    + '</div>';

  // ── Click card → fly map to hotel ───────────────────────────
  card.addEventListener('click', function(e) {{
    if (e.target.tagName === 'A') return; // let links open
    flyToHotel(h.i);
  }});

  listEl.appendChild(card);
}});

// ── fly to hotel + open popup ────────────────────────────────────
function flyToHotel(idx) {{
  var h = HOTELS[idx];
  var m = markers[idx];

  // Smooth fly animation
  map.flyTo([h.lat, h.lon], 16, {{
    animate: true,
    duration: 1.2
  }});

  // Open popup after fly completes
  setTimeout(function() {{
    m.openPopup();
  }}, 1300);

  // Highlight card
  highlightCard(idx);
}}

function highlightCard(idx) {{
  // Remove previous active
  if (activeCard !== null) {{
    var prev = document.getElementById('card-' + activeCard);
    if (prev) prev.classList.remove('active');
  }}
  // Set new active
  var card = document.getElementById('card-' + idx);
  if (card) {{
    card.classList.add('active');
    card.scrollIntoView({{behavior:'smooth', block:'nearest'}});
  }}
  activeCard = idx;
}}

// Auto-fit bounds to show all hotels + center
if (HOTELS.length > 0) {{
  var bounds = [CENTER];
  HOTELS.forEach(function(h) {{ bounds.push([h.lat, h.lon]); }});
  map.fitBounds(bounds, {{padding: [40, 40], maxZoom: 15}});
}}
</script>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════════
# SESSION CACHE
# ══════════════════════════════════════════════════════════════════
_hotels_cache: dict[str, list[dict]] = {}


# ══════════════════════════════════════════════════════════════════
# PUBLIC API — called from main.py
# ══════════════════════════════════════════════════════════════════


def get_hotels_for_destination(destination: str, lang: str = "vi") -> list[dict]:
    """
    Fetch hotels for destination (OSM → AI fallback).
    Returns list of hotel dicts. Cached per destination.
    """
    key = f"{destination}|{lang}"
    if key in _hotels_cache:
        return _hotels_cache[key]

    coords = _get_center(destination)
    if not coords:
        return []
    lat, lon = coords

    # OSM
    big_cities = {
        "Hanoi",
        "Ho Chi Minh City",
        "Bangkok",
        "Tokyo",
        "Paris",
        "London",
        "Seoul",
        "New York",
    }
    radius = 5000 if destination in big_cities else 3000
    hotels = _overpass_hotels(lat, lon, radius=radius, limit=10)
    print(f"[MAP] OSM hotels for '{destination}': {len(hotels)}")

    # AI supplement
    if len(hotels) < 4:
        ai = _ai_hotels(destination, lat, lon, lang)
        seen = {h["name"].lower() for h in hotels}
        for h in ai:
            if h["name"].lower() not in seen and len(hotels) < 10:
                hotels.append(h)
                seen.add(h["name"].lower())
        print(f"[MAP] After AI: {len(hotels)} hotels")

    _hotels_cache[key] = hotels
    return hotels


def build_hotel_map_component(
    destination: str,
    lang: str = "vi",
    height: int = 560,
) -> str | None:
    """
    Returns the full HTML string for use with st.components.v1.html().
    Returns None if destination unknown or no hotels found.
    """
    coords = _get_center(destination)
    if not coords:
        return None
    lat, lon = coords

    hotels = get_hotels_for_destination(destination, lang)
    if not hotels:
        return None

    return _build_full_html(destination, lat, lon, hotels, lang)


def should_show_hotel_map(intents: list[str], destination: str) -> bool:
    """Show map when relevant intent + known destination."""
    if not destination or destination in ("", "Unknown"):
        return False
    show_for = {"hotel", "planner", "general", "activity", "cost", "image_id"}
    return bool(show_for.intersection(set(intents)))


def clear_cache() -> None:
    """Clear hotel cache (called on conversation reset)."""
    _hotels_cache.clear()

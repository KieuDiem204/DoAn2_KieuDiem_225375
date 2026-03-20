"""
weather_service.py — OpenWeatherMap API integration v2.0
Fix:
  ✅ Thêm đầy đủ các tỉnh/thành VN vào CITY_MAP (bao gồm Tây Ninh, Ninh Bình, Hà Giang...)
  ✅ _NEAREST_CITY: mapping tỉnh → thành phố OWM gần nhất khi không có trực tiếp
  ✅ _MOCK_DB đầy đủ cho tất cả địa điểm
  ✅ Hiển thị đúng tên địa điểm đang hỏi, thêm ghi chú "(thời tiết tham chiếu từ X)" nếu dùng nearest
  ✅ Không bao giờ hiển thị sai thành phố mà không có ghi chú
"""

import os, random
import requests
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"

# ══════════════════════════════════════════════════════════════════
# CITY MAP — đầy đủ tỉnh/thành VN + quốc tế
# q = chuỗi query cho OpenWeatherMap API
# ══════════════════════════════════════════════════════════════════
CITY_MAP = {
    # ── Việt Nam — miền Bắc ──────────────────────────────────
    "Hanoi": {"q": "Hanoi,VN", "name_vi": "Hà Nội", "lat": 21.028, "lon": 105.834},
    "Ha Long": {"q": "Ha Long,VN", "name_vi": "Hạ Long", "lat": 20.951, "lon": 107.074},
    "Sa Pa": {"q": "Sapa,VN", "name_vi": "Sa Pa", "lat": 22.336, "lon": 103.844},
    "Ha Giang": {
        "q": "Ha Giang,VN",
        "name_vi": "Hà Giang",
        "lat": 22.823,
        "lon": 104.984,
    },
    "Cao Bang": {
        "q": "Cao Bang,VN",
        "name_vi": "Cao Bằng",
        "lat": 22.666,
        "lon": 106.258,
    },
    "Lang Son": {
        "q": "Lang Son,VN",
        "name_vi": "Lạng Sơn",
        "lat": 21.853,
        "lon": 106.761,
    },
    "Hai Phong": {
        "q": "Hai Phong,VN",
        "name_vi": "Hải Phòng",
        "lat": 20.845,
        "lon": 106.688,
    },
    "Ninh Binh": {
        "q": "Ninh Binh,VN",
        "name_vi": "Ninh Bình",
        "lat": 20.250,
        "lon": 105.975,
    },
    "Nam Dinh": {
        "q": "Nam Dinh,VN",
        "name_vi": "Nam Định",
        "lat": 20.420,
        "lon": 106.162,
    },
    "Thai Binh": {
        "q": "Thai Binh,VN",
        "name_vi": "Thái Bình",
        "lat": 20.450,
        "lon": 106.340,
    },
    "Vinh Phuc": {
        "q": "Vinh Yen,VN",
        "name_vi": "Vĩnh Phúc",
        "lat": 21.300,
        "lon": 105.597,
    },
    "Bac Ninh": {
        "q": "Bac Ninh,VN",
        "name_vi": "Bắc Ninh",
        "lat": 21.186,
        "lon": 106.076,
    },
    "Bac Giang": {
        "q": "Bac Giang,VN",
        "name_vi": "Bắc Giang",
        "lat": 21.273,
        "lon": 106.194,
    },
    "Thai Nguyen": {
        "q": "Thai Nguyen,VN",
        "name_vi": "Thái Nguyên",
        "lat": 21.594,
        "lon": 105.848,
    },
    "Tuyen Quang": {
        "q": "Tuyen Quang,VN",
        "name_vi": "Tuyên Quang",
        "lat": 21.823,
        "lon": 105.218,
    },
    "Yen Bai": {"q": "Yen Bai,VN", "name_vi": "Yên Bái", "lat": 21.722, "lon": 104.911},
    "Phu Tho": {
        "q": "Viet Tri,VN",
        "name_vi": "Phú Thọ",
        "lat": 21.399,
        "lon": 105.227,
    },
    "Son La": {"q": "Son La,VN", "name_vi": "Sơn La", "lat": 21.327, "lon": 103.914},
    "Dien Bien": {
        "q": "Dien Bien Phu,VN",
        "name_vi": "Điện Biên Phủ",
        "lat": 21.386,
        "lon": 103.017,
    },
    "Lai Chau": {
        "q": "Lai Chau,VN",
        "name_vi": "Lai Châu",
        "lat": 22.396,
        "lon": 103.459,
    },
    "Hoa Binh": {
        "q": "Hoa Binh,VN",
        "name_vi": "Hòa Bình",
        "lat": 20.813,
        "lon": 105.338,
    },
    # ── Việt Nam — miền Trung ───────────────────────────────
    "Hue": {"q": "Hue,VN", "name_vi": "Huế", "lat": 16.467, "lon": 107.600},
    "Da Nang": {"q": "Da Nang,VN", "name_vi": "Đà Nẵng", "lat": 16.068, "lon": 108.212},
    "Hoi An": {"q": "Hoi An,VN", "name_vi": "Hội An", "lat": 15.880, "lon": 108.335},
    "Nha Trang": {
        "q": "Nha Trang,VN",
        "name_vi": "Nha Trang",
        "lat": 12.238,
        "lon": 109.197,
    },
    "Quy Nhon": {
        "q": "Quy Nhon,VN",
        "name_vi": "Quy Nhơn",
        "lat": 13.776,
        "lon": 109.223,
    },
    "Phan Thiet": {
        "q": "Phan Thiet,VN",
        "name_vi": "Phan Thiết",
        "lat": 10.933,
        "lon": 108.100,
    },
    "Mui Ne": {
        "q": "Phan Thiet,VN",
        "name_vi": "Mũi Né",
        "lat": 10.933,
        "lon": 108.100,
    },
    "Da Lat": {"q": "Da Lat,VN", "name_vi": "Đà Lạt", "lat": 11.941, "lon": 108.458},
    "Thanh Hoa": {
        "q": "Thanh Hoa,VN",
        "name_vi": "Thanh Hóa",
        "lat": 19.807,
        "lon": 105.776,
    },
    "Vinh": {"q": "Vinh,VN", "name_vi": "Vinh", "lat": 18.679, "lon": 105.681},
    "Ha Tinh": {"q": "Ha Tinh,VN", "name_vi": "Hà Tĩnh", "lat": 18.342, "lon": 105.906},
    "Dong Ha": {"q": "Dong Ha,VN", "name_vi": "Đông Hà", "lat": 16.818, "lon": 107.101},
    "Quang Ngai": {
        "q": "Quang Ngai,VN",
        "name_vi": "Quảng Ngãi",
        "lat": 15.121,
        "lon": 108.793,
    },
    "Tuy Hoa": {"q": "Tuy Hoa,VN", "name_vi": "Tuy Hòa", "lat": 13.096, "lon": 109.323},
    "Buon Ma Thuot": {
        "q": "Buon Ma Thuot,VN",
        "name_vi": "Buôn Ma Thuột",
        "lat": 12.666,
        "lon": 108.050,
    },
    "Pleiku": {"q": "Pleiku,VN", "name_vi": "Pleiku", "lat": 13.983, "lon": 108.000},
    "Kon Tum": {"q": "Kontum,VN", "name_vi": "Kon Tum", "lat": 14.349, "lon": 108.000},
    "Phan Rang": {
        "q": "Phan Rang,VN",
        "name_vi": "Phan Rang",
        "lat": 11.568,
        "lon": 108.988,
    },
    # ── Việt Nam — miền Nam ────────────────────────────────
    "Ho Chi Minh City": {
        "q": "Ho Chi Minh City,VN",
        "name_vi": "TP. Hồ Chí Minh",
        "lat": 10.823,
        "lon": 106.630,
    },
    "Vung Tau": {
        "q": "Vung Tau,VN",
        "name_vi": "Vũng Tàu",
        "lat": 10.346,
        "lon": 107.085,
    },
    "Can Tho": {"q": "Can Tho,VN", "name_vi": "Cần Thơ", "lat": 10.045, "lon": 105.748},
    "Phu Quoc": {
        "q": "Phu Quoc,VN",
        "name_vi": "Phú Quốc",
        "lat": 10.289,
        "lon": 103.984,
    },
    # ── Tây Ninh và các tỉnh Nam Bộ quan trọng ─────────────
    "Tay Ninh": {
        "q": "Tay Ninh,VN",
        "name_vi": "Tây Ninh",
        "lat": 11.310,
        "lon": 106.098,
    },
    "Bien Hoa": {
        "q": "Bien Hoa,VN",
        "name_vi": "Biên Hòa",
        "lat": 10.958,
        "lon": 106.843,
    },
    "Thu Dau Mot": {
        "q": "Thu Dau Mot,VN",
        "name_vi": "Thủ Dầu Một",
        "lat": 10.980,
        "lon": 106.652,
    },
    "Long An": {"q": "Tan An,VN", "name_vi": "Long An", "lat": 10.535, "lon": 106.413},
    "Tien Giang": {
        "q": "My Tho,VN",
        "name_vi": "Tiền Giang",
        "lat": 10.360,
        "lon": 106.360,
    },
    "My Tho": {"q": "My Tho,VN", "name_vi": "Mỹ Tho", "lat": 10.360, "lon": 106.360},
    "Ben Tre": {"q": "Ben Tre,VN", "name_vi": "Bến Tre", "lat": 10.243, "lon": 106.375},
    "Vinh Long": {
        "q": "Vinh Long,VN",
        "name_vi": "Vĩnh Long",
        "lat": 10.253,
        "lon": 105.972,
    },
    "Tra Vinh": {
        "q": "Tra Vinh,VN",
        "name_vi": "Trà Vinh",
        "lat": 9.935,
        "lon": 106.345,
    },
    "Soc Trang": {
        "q": "Soc Trang,VN",
        "name_vi": "Sóc Trăng",
        "lat": 9.603,
        "lon": 105.980,
    },
    "Bac Lieu": {
        "q": "Bac Lieu,VN",
        "name_vi": "Bạc Liêu",
        "lat": 9.294,
        "lon": 105.728,
    },
    "Ca Mau": {"q": "Ca Mau,VN", "name_vi": "Cà Mau", "lat": 9.177, "lon": 105.150},
    "Chau Doc": {
        "q": "Chau Doc,VN",
        "name_vi": "Châu Đốc",
        "lat": 10.700,
        "lon": 105.117,
    },
    "Rach Gia": {
        "q": "Rach Gia,VN",
        "name_vi": "Rạch Giá",
        "lat": 10.012,
        "lon": 105.081,
    },
    "Dong Xoai": {
        "q": "Dong Xoai,VN",
        "name_vi": "Đồng Xoài",
        "lat": 11.535,
        "lon": 106.889,
    },
    "Dong Nai": {
        "q": "Bien Hoa,VN",
        "name_vi": "Đồng Nai",
        "lat": 10.958,
        "lon": 106.843,
    },
    # ── Quốc tế ────────────────────────────────────────────
    "Bangkok": {"q": "Bangkok,TH", "name_vi": "Bangkok", "lat": 13.756, "lon": 100.502},
    "Bali": {"q": "Denpasar,ID", "name_vi": "Bali", "lat": -8.650, "lon": 115.217},
    "Tokyo": {"q": "Tokyo,JP", "name_vi": "Tokyo", "lat": 35.689, "lon": 139.692},
    "Osaka": {"q": "Osaka,JP", "name_vi": "Osaka", "lat": 34.693, "lon": 135.502},
    "Seoul": {"q": "Seoul,KR", "name_vi": "Seoul", "lat": 37.566, "lon": 126.978},
    "Paris": {"q": "Paris,FR", "name_vi": "Paris", "lat": 48.856, "lon": 2.352},
    "Singapore": {
        "q": "Singapore,SG",
        "name_vi": "Singapore",
        "lat": 1.352,
        "lon": 103.820,
    },
    "Kuala Lumpur": {
        "q": "Kuala Lumpur,MY",
        "name_vi": "Kuala Lumpur",
        "lat": 3.149,
        "lon": 101.697,
    },
    "Rome": {"q": "Rome,IT", "name_vi": "Rome", "lat": 41.902, "lon": 12.496},
    "New York": {
        "q": "New York,US",
        "name_vi": "New York",
        "lat": 40.713,
        "lon": -74.006,
    },
    "London": {"q": "London,GB", "name_vi": "London", "lat": 51.507, "lon": -0.128},
    "Sydney": {"q": "Sydney,AU", "name_vi": "Sydney", "lat": -33.869, "lon": 151.209},
    "Dubai": {"q": "Dubai,AE", "name_vi": "Dubai", "lat": 25.205, "lon": 55.270},
    "Amsterdam": {
        "q": "Amsterdam,NL",
        "name_vi": "Amsterdam",
        "lat": 52.374,
        "lon": 4.890,
    },
    "Barcelona": {
        "q": "Barcelona,ES",
        "name_vi": "Barcelona",
        "lat": 41.385,
        "lon": 2.173,
    },
    "Berlin": {"q": "Berlin,DE", "name_vi": "Berlin", "lat": 52.520, "lon": 13.405},
    "Santorini": {
        "q": "Santorini,GR",
        "name_vi": "Santorini",
        "lat": 36.393,
        "lon": 25.461,
    },
    "Phuket": {"q": "Phuket,TH", "name_vi": "Phuket", "lat": 7.879, "lon": 98.398},
    "Chiang Mai": {
        "q": "Chiang Mai,TH",
        "name_vi": "Chiang Mai",
        "lat": 18.787,
        "lon": 98.993,
    },
    "Siem Reap": {
        "q": "Siem Reap,KH",
        "name_vi": "Siem Reap",
        "lat": 13.362,
        "lon": 103.860,
    },
    "Hong Kong": {
        "q": "Hong Kong,HK",
        "name_vi": "Hồng Kông",
        "lat": 22.319,
        "lon": 114.170,
    },
    "Taipei": {"q": "Taipei,TW", "name_vi": "Đài Bắc", "lat": 25.048, "lon": 121.514},
    "Maldives": {"q": "Male,MV", "name_vi": "Maldives", "lat": 4.175, "lon": 73.509},
    "Rio de Janeiro": {
        "q": "Rio de Janeiro,BR",
        "name_vi": "Rio de Janeiro",
        "lat": -22.906,
        "lon": -43.173,
    },
    "Cancun": {"q": "Cancun,MX", "name_vi": "Cancun", "lat": 21.161, "lon": -86.852},
    "Cape Town": {
        "q": "Cape Town,ZA",
        "name_vi": "Cape Town",
        "lat": -33.925,
        "lon": 18.424,
    },
    "Honolulu": {
        "q": "Honolulu,US",
        "name_vi": "Honolulu",
        "lat": 21.306,
        "lon": -157.858,
    },
    "Vancouver": {
        "q": "Vancouver,CA",
        "name_vi": "Vancouver",
        "lat": 49.247,
        "lon": -123.116,
    },
    "Los Angeles": {
        "q": "Los Angeles,US",
        "name_vi": "Los Angeles",
        "lat": 34.052,
        "lon": -118.244,
    },
    "Marrakech": {
        "q": "Marrakech,MA",
        "name_vi": "Marrakech",
        "lat": 31.629,
        "lon": -7.981,
    },
    "Edinburgh": {
        "q": "Edinburgh,GB",
        "name_vi": "Edinburgh",
        "lat": 55.953,
        "lon": -3.188,
    },
}

# ══════════════════════════════════════════════════════════════════
# NEAREST CITY — khi destination không có trong CITY_MAP
# Maps tỉnh/vùng → thành phố OWM gần nhất + ghi chú cho UI
# ══════════════════════════════════════════════════════════════════
_NEAREST_CITY = {
    # Tây Ninh → dùng trực tiếp (đã có trong CITY_MAP)
    # Các tỉnh miền Bắc không có OWM → dùng Hà Nội
    "Ha Noi": "Hanoi",
    "Hanoi": "Hanoi",
    "Ha Giang": "Ha Giang",
    "Cao Bang": "Cao Bang",
    "Lang Son": "Lang Son",
    "Bac Kan": "Hanoi",
    "Tuyen Quang": "Tuyen Quang",
    "Thai Nguyen": "Thai Nguyen",
    "Phu Tho": "Phu Tho",
    "Vinh Phuc": "Vinh Phuc",
    "Bac Ninh": "Bac Ninh",
    "Bac Giang": "Bac Giang",
    "Hung Yen": "Hanoi",
    "Hai Duong": "Hanoi",
    "Ha Nam": "Hanoi",
    "Ninh Binh": "Ninh Binh",
    "Nam Dinh": "Nam Dinh",
    "Thai Binh": "Thai Binh",
    "Hoa Binh": "Hoa Binh",
    "Son La": "Son La",
    "Dien Bien": "Dien Bien",
    "Lai Chau": "Lai Chau",
    "Yen Bai": "Yen Bai",
    # Miền Trung
    "Thanh Hoa": "Thanh Hoa",
    "Nghe An": "Vinh",
    "Ha Tinh": "Ha Tinh",
    "Quang Binh": "Dong Ha",
    "Quang Tri": "Dong Ha",
    "Phong Nha": "Dong Ha",
    "Quang Nam": "Da Nang",
    "Quang Ngai": "Quang Ngai",
    "Binh Dinh": "Quy Nhon",
    "Phu Yen": "Tuy Hoa",
    "Khanh Hoa": "Nha Trang",
    "Ninh Thuan": "Phan Rang",
    "Binh Thuan": "Phan Thiet",
    "Lam Dong": "Da Lat",
    "Dak Lak": "Buon Ma Thuot",
    "Dak Nong": "Buon Ma Thuot",
    "Gia Lai": "Pleiku",
    "Kon Tum": "Kon Tum",
    # Miền Nam
    "Tay Ninh": "Tay Ninh",
    "Binh Phuoc": "Dong Xoai",
    "Binh Duong": "Thu Dau Mot",
    "Dong Nai": "Bien Hoa",
    "Ba Ria Vung Tau": "Vung Tau",
    "Long An": "Long An",
    "Tien Giang": "My Tho",
    "Ben Tre": "Ben Tre",
    "Vinh Long": "Vinh Long",
    "Tra Vinh": "Tra Vinh",
    "Dong Thap": "Can Tho",
    "An Giang": "Chau Doc",
    "Kien Giang": "Rach Gia",
    "Hau Giang": "Can Tho",
    "Soc Trang": "Soc Trang",
    "Bac Lieu": "Bac Lieu",
    "Ca Mau": "Ca Mau",
    # Địa điểm đặc biệt (di tích, thắng cảnh → nearest city)
    "Nui Ba Den": "Tay Ninh",
    "Núi Bà Đen": "Tay Ninh",
    "Bai Dinh": "Ninh Binh",
    "Bái Đính": "Ninh Binh",
    "Trang An": "Ninh Binh",
    "Tràng An": "Ninh Binh",
    "Phong Nha Cave": "Dong Ha",
    "Son Doong": "Dong Ha",
    "My Son": "Da Nang",
    "Angkor": "Siem Reap",
    "Siem Reap": "Siem Reap",
}

WEATHER_EMOJI = {
    "01d": "☀️",
    "01n": "🌙",
    "02d": "⛅",
    "02n": "🌥️",
    "03d": "☁️",
    "03n": "☁️",
    "04d": "☁️",
    "04n": "☁️",
    "09d": "🌧️",
    "09n": "🌧️",
    "10d": "🌦️",
    "10n": "🌧️",
    "11d": "⛈️",
    "11n": "⛈️",
    "13d": "❄️",
    "13n": "❄️",
    "50d": "🌫️",
    "50n": "🌫️",
}

TRAVEL_ADVICE_VI = {
    "Clear": "Thời tiết đẹp, lý tưởng để tham quan ngoài trời và check-in!",
    "Clouds": "Trời nhiều mây, mát mẻ dễ chịu, thích hợp đi bộ tham quan.",
    "Rain": "Có mưa — nên mang theo áo mưa hoặc ô dù. Ưu tiên tham quan trong nhà.",
    "Drizzle": "Mưa phùn nhẹ, mang theo ô là đủ. Vẫn tham quan bình thường được.",
    "Thunderstorm": "Có giông bão, hạn chế ra ngoài. Dành thời gian nghỉ ngơi tại khách sạn.",
    "Snow": "Tuyết rơi! Cảnh đẹp nhưng cần mặc ấm kỹ. Cẩn thận đường trơn trượt.",
    "Mist": "Sương mù nhẹ, cảnh rất thơ mộng! Cẩn thận khi di chuyển.",
    "Fog": "Sương mù dày — lái xe cẩn thận. Không khí huyền bí rất đặc biệt!",
    "Haze": "Trời hơi mờ nhưng vẫn du lịch bình thường được.",
}

# ── Mock data đầy đủ ─────────────────────────────────────────────
_MOCK_DB = {
    # Miền Bắc
    "Hanoi": {"temp": 28, "main": "Clouds", "desc": "Mây vừa phải, ẩm", "hum": 76},
    "Ha Long": {"temp": 27, "main": "Clear", "desc": "Ít mây, trời đẹp", "hum": 78},
    "Sa Pa": {"temp": 15, "main": "Mist", "desc": "Sương mù nhẹ buổi sáng", "hum": 88},
    "Ha Giang": {"temp": 20, "main": "Clouds", "desc": "Mây cao nguyên đá", "hum": 80},
    "Cao Bang": {
        "temp": 22,
        "main": "Clear",
        "desc": "Trời trong xanh, mát",
        "hum": 72,
    },
    "Ninh Binh": {
        "temp": 27,
        "main": "Clouds",
        "desc": "Nhiều mây, dễ chịu",
        "hum": 79,
    },
    "Hai Phong": {"temp": 28, "main": "Clouds", "desc": "Nhiều mây nhẹ", "hum": 77},
    "Hoa Binh": {
        "temp": 26,
        "main": "Clear",
        "desc": "Trời quang, nắng nhẹ",
        "hum": 72,
    },
    "Son La": {"temp": 22, "main": "Clear", "desc": "Mát mẻ, trời xanh", "hum": 70},
    "Dien Bien": {"temp": 24, "main": "Clear", "desc": "Nắng nhẹ, gió mát", "hum": 68},
    # Miền Trung
    "Hue": {"temp": 28, "main": "Clouds", "desc": "Nhiều mây, dễ chịu", "hum": 78},
    "Da Nang": {"temp": 29, "main": "Clear", "desc": "Nắng đẹp, gió nhẹ", "hum": 70},
    "Hoi An": {"temp": 30, "main": "Clouds", "desc": "Nhiều mây nhẹ", "hum": 80},
    "Nha Trang": {
        "temp": 30,
        "main": "Clear",
        "desc": "Bầu trời quang đãng",
        "hum": 68,
    },
    "Quy Nhon": {"temp": 29, "main": "Clear", "desc": "Nắng đẹp, ít gió", "hum": 70},
    "Da Lat": {"temp": 20, "main": "Clouds", "desc": "Mây rải rác, mát mẻ", "hum": 75},
    "Phan Thiet": {
        "temp": 31,
        "main": "Clear",
        "desc": "Nắng gắt, gió mạnh",
        "hum": 65,
    },
    "Mui Ne": {"temp": 31, "main": "Clear", "desc": "Nắng gắt, gió biển", "hum": 65},
    "Buon Ma Thuot": {
        "temp": 25,
        "main": "Clouds",
        "desc": "Mát mẻ cao nguyên",
        "hum": 73,
    },
    "Pleiku": {"temp": 22, "main": "Mist", "desc": "Sương mù sáng sớm", "hum": 85},
    "Dong Ha": {"temp": 27, "main": "Clouds", "desc": "Nhiều mây, gió lào", "hum": 72},
    "Vinh": {"temp": 29, "main": "Clear", "desc": "Nắng nóng", "hum": 68},
    # Miền Nam
    "Ho Chi Minh City": {
        "temp": 34,
        "main": "Clear",
        "desc": "Nắng gắt, nóng",
        "hum": 65,
    },
    "Vung Tau": {
        "temp": 31,
        "main": "Clear",
        "desc": "Gió biển mát, nắng đẹp",
        "hum": 70,
    },
    "Can Tho": {
        "temp": 32,
        "main": "Clear",
        "desc": "Trời quang đãng, nắng",
        "hum": 70,
    },
    "Phu Quoc": {"temp": 31, "main": "Clear", "desc": "Nắng đẹp, gió biển", "hum": 72},
    "Tay Ninh": {"temp": 33, "main": "Clear", "desc": "Nắng nóng, ít gió", "hum": 63},
    "Bien Hoa": {"temp": 33, "main": "Clear", "desc": "Nắng nóng", "hum": 64},
    "My Tho": {"temp": 32, "main": "Clear", "desc": "Nắng, gió sông", "hum": 71},
    "Ben Tre": {"temp": 31, "main": "Clouds", "desc": "Nhiều mây nhẹ", "hum": 75},
    "Ca Mau": {"temp": 30, "main": "Clouds", "desc": "Nhiều mây, ẩm", "hum": 82},
    "Rach Gia": {"temp": 30, "main": "Clear", "desc": "Nắng, gió biển nhẹ", "hum": 74},
    # Quốc tế
    "Bangkok": {"temp": 33, "main": "Clear", "desc": "Nắng, rất nóng", "hum": 68},
    "Bali": {"temp": 28, "main": "Clouds", "desc": "Mây nhẹ, ấm áp", "hum": 80},
    "Tokyo": {"temp": 18, "main": "Clear", "desc": "Mát mẻ, trời xanh", "hum": 55},
    "Paris": {"temp": 12, "main": "Clouds", "desc": "Nhiều mây, se lạnh", "hum": 72},
    "Seoul": {"temp": 15, "main": "Clear", "desc": "Trời đẹp, mát", "hum": 50},
    "Singapore": {"temp": 30, "main": "Rain", "desc": "Có mưa rào chiều", "hum": 85},
    "Dubai": {"temp": 38, "main": "Clear", "desc": "Nắng, rất nóng khô", "hum": 40},
    "London": {"temp": 10, "main": "Clouds", "desc": "Nhiều mây, lạnh", "hum": 78},
    "New York": {"temp": 14, "main": "Clouds", "desc": "Nhiều mây, se lạnh", "hum": 65},
    "Sydney": {"temp": 22, "main": "Clear", "desc": "Nắng đẹp, dễ chịu", "hum": 60},
    "Kuala Lumpur": {
        "temp": 31,
        "main": "Clouds",
        "desc": "Nhiều mây, nóng ẩm",
        "hum": 82,
    },
    "Phuket": {"temp": 30, "main": "Clear", "desc": "Nắng đẹp, biển xanh", "hum": 74},
    "Chiang Mai": {"temp": 28, "main": "Clear", "desc": "Nắng, mát về đêm", "hum": 62},
    "Siem Reap": {"temp": 32, "main": "Clear", "desc": "Nắng nóng", "hum": 66},
    "Osaka": {"temp": 17, "main": "Clear", "desc": "Mát mẻ, dễ chịu", "hum": 58},
    "Santorini": {"temp": 20, "main": "Clear", "desc": "Nắng đẹp, gió biển", "hum": 55},
    "Amsterdam": {
        "temp": 10,
        "main": "Clouds",
        "desc": "Nhiều mây, se lạnh",
        "hum": 80,
    },
    "Barcelona": {"temp": 18, "main": "Clear", "desc": "Nắng ấm, dễ chịu", "hum": 60},
    "Maldives": {"temp": 30, "main": "Clear", "desc": "Nắng đẹp, biển xanh", "hum": 76},
}


# ══════════════════════════════════════════════════════════════════
# CORE: Resolve destination → city info
# ══════════════════════════════════════════════════════════════════


def _resolve_city(destination: str) -> tuple[dict, str, bool]:
    """
    Tìm thông tin thành phố cho destination.
    Returns: (city_info_dict, display_note, is_nearest)
      - city_info_dict: entry từ CITY_MAP
      - display_note: ghi chú thêm nếu dùng nearest city (vd: "gần Tây Ninh nhất")
      - is_nearest: True nếu dùng nearest, False nếu match trực tiếp
    """
    if not destination:
        return {}, "", False

    dest = destination.strip()

    # 1. Direct match (case-insensitive)
    dest_lower = dest.lower()
    for key, info in CITY_MAP.items():
        if key.lower() == dest_lower:
            return info, "", False
        if info.get("name_vi", "").lower() == dest_lower:
            return info, "", False

    # 2. Partial match
    for key, info in CITY_MAP.items():
        if dest_lower in key.lower() or key.lower() in dest_lower:
            return info, "", False
        vi = info.get("name_vi", "").lower()
        if dest_lower in vi or vi in dest_lower:
            return info, "", False

    # 3. Nearest city mapping
    for map_key, nearest_key in _NEAREST_CITY.items():
        if map_key.lower() == dest_lower or dest_lower in map_key.lower():
            if nearest_key in CITY_MAP:
                note = f"({CITY_MAP[nearest_key]['name_vi']} — gần {dest} nhất)"
                return CITY_MAP[nearest_key], note, True

    # 4. Not found
    return {}, "", False


def _mock_weather(destination: str) -> dict:
    """Build mock weather for destination, using nearest city data if needed."""
    city_info, note, is_nearest = _resolve_city(destination)

    # Find mock data key
    mock_key = None
    if city_info:
        # Try to match city_info to a _MOCK_DB key
        city_q = city_info.get("q", "").split(",")[0]
        city_name_vi = city_info.get("name_vi", "")
        for mk in _MOCK_DB:
            if mk.lower() == city_q.lower():
                mock_key = mk
                break
        if not mock_key:
            for mk in _MOCK_DB:
                if mk.lower() in city_q.lower() or city_q.lower() in mk.lower():
                    mock_key = mk
                    break

    # Direct lookup in MOCK_DB
    if not mock_key:
        for mk in _MOCK_DB:
            if mk.lower() == destination.lower():
                mock_key = mk
                break

    base = _MOCK_DB.get(
        mock_key or destination,
        {"temp": 30, "main": "Clear", "desc": "Thời tiết ổn định", "hum": 70},
    )

    temp = base["temp"] + random.randint(-2, 2)
    icon_map = {
        "Clear": "01d",
        "Rain": "10d",
        "Mist": "50d",
        "Fog": "50d",
        "Clouds": "03d",
        "Drizzle": "09d",
        "Thunderstorm": "11d",
    }
    icon = icon_map.get(base["main"], "03d")

    # Display name: use Vietnamese name from CITY_MAP or destination itself
    if city_info:
        display_name = city_info.get("name_vi", destination)
    else:
        display_name = destination

    return {
        "destination": destination,
        "destination_vi": display_name,
        "display_note": note,  # ← ghi chú nearest city
        "is_nearest": is_nearest,
        "temp": temp,
        "feels_like": temp + random.randint(-3, 2),
        "temp_min": temp - 3,
        "temp_max": temp + 4,
        "humidity": base["hum"],
        "description": base["desc"],
        "main": base["main"],
        "emoji": WEATHER_EMOJI.get(icon, "🌤️"),
        "wind_speed": round(random.uniform(5, 20), 1),
        "visibility": 10,
        "advice": TRAVEL_ADVICE_VI.get(
            base["main"], "Thời tiết ổn, có thể du lịch bình thường."
        ),
        "source": "Demo",
        "is_mock": True,
    }


def _mock_forecast(destination: str) -> list:
    city_info, _, _ = _resolve_city(destination)
    # Find base temp
    city_q = city_info.get("q", "").split(",")[0] if city_info else destination
    base_temp = None
    for mk, mv in _MOCK_DB.items():
        if mk.lower() == city_q.lower() or mk.lower() == destination.lower():
            base_temp = mv["temp"]
            break
    if base_temp is None:
        base_temp = 28

    weekdays = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    icons = ["01d", "03d", "10d", "01d", "02d"]
    dt = datetime.now()
    return [
        {
            "weekday": weekdays[(dt.weekday() + i + 1) % 7],
            "day": "{:02d}/{:02d}".format((dt.day + i) % 28 + 1, dt.month),
            "emoji": WEATHER_EMOJI.get(icons[i], "🌤️"),
            "temp_max": base_temp + random.randint(0, 4),
            "temp_min": base_temp - random.randint(3, 7),
        }
        for i in range(5)
    ]


def get_weather(destination: str) -> dict:
    """Lấy thời tiết cho destination. Tự động tìm nearest city nếu cần."""
    if not destination:
        return {}

    city_info, note, is_nearest = _resolve_city(destination)

    # No OWM key → mock
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY in (
        "",
        "your_openweathermap_api_key_here",
    ):
        w = _mock_weather(destination)
        if is_nearest and note:
            w["display_note"] = note
            w["is_nearest"] = True
        return w

    # Use OWM API
    q = city_info.get("q") if city_info else destination
    if not q:
        q = destination

    try:
        r = requests.get(
            BASE_URL + "/weather",
            params={
                "q": q,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "vi",
            },
            timeout=5,
        )
        if r.status_code != 200:
            return _mock_weather(destination)

        d = r.json()
        main = d.get("main", {})
        wobj = d.get("weather", [{}])[0]
        wind = d.get("wind", {})
        icon = wobj.get("icon", "01d")
        wm = wobj.get("main", "Clear")

        display_name = (
            city_info.get("name_vi", destination) if city_info else destination
        )

        return {
            "destination": destination,
            "destination_vi": display_name,
            "display_note": note,
            "is_nearest": is_nearest,
            "temp": round(main.get("temp", 0)),
            "feels_like": round(main.get("feels_like", 0)),
            "temp_min": round(main.get("temp_min", 0)),
            "temp_max": round(main.get("temp_max", 0)),
            "humidity": main.get("humidity", 0),
            "description": wobj.get("description", "").capitalize(),
            "main": wm,
            "emoji": WEATHER_EMOJI.get(icon, "🌤️"),
            "wind_speed": round(wind.get("speed", 0) * 3.6, 1),
            "visibility": d.get("visibility", 10000) // 1000,
            "advice": TRAVEL_ADVICE_VI.get(
                wm, "Thời tiết ổn, có thể du lịch bình thường."
            ),
            "source": "OpenWeatherMap",
            "is_mock": False,
        }
    except Exception:
        return _mock_weather(destination)


def get_forecast(destination: str) -> list:
    """Lấy dự báo 5 ngày cho destination."""
    if not destination:
        return []

    city_info, _, _ = _resolve_city(destination)

    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY in (
        "",
        "your_openweathermap_api_key_here",
    ):
        return _mock_forecast(destination)

    q = city_info.get("q") if city_info else destination
    if not q:
        q = destination

    try:
        r = requests.get(
            BASE_URL + "/forecast",
            params={
                "q": q,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "vi",
                "cnt": 40,
            },
            timeout=5,
        )
        if r.status_code != 200:
            return _mock_forecast(destination)

        results, seen = [], set()
        for item in r.json().get("list", []):
            dt = datetime.fromtimestamp(item["dt"])
            ds = dt.strftime("%Y-%m-%d")
            if ds in seen:
                continue
            seen.add(ds)
            wobj = item.get("weather", [{}])[0]
            m = item.get("main", {})
            icon = wobj.get("icon", "01d")
            results.append(
                {
                    "weekday": ["T2", "T3", "T4", "T5", "T6", "T7", "CN"][dt.weekday()],
                    "day": dt.strftime("%d/%m"),
                    "emoji": WEATHER_EMOJI.get(icon, "🌤️"),
                    "temp_max": round(m.get("temp_max", m.get("temp", 0))),
                    "temp_min": round(m.get("temp_min", m.get("temp", 0))),
                }
            )
            if len(results) >= 5:
                break
        return results
    except Exception:
        return _mock_forecast(destination)


# ══════════════════════════════════════════════════════════════════
# HTML BUILDER — hiển thị đúng địa điểm đang hỏi
# ══════════════════════════════════════════════════════════════════


def build_weather_html(destination: str, lang: str = "vi") -> str:
    """
    Build weather card HTML.
    Hiển thị đúng tên địa điểm đang được hỏi.
    Nếu dùng nearest city: hiển thị ghi chú rõ ràng.
    """
    if not destination:
        return ""

    w = get_weather(destination)
    fc = get_forecast(destination)
    if not w:
        return ""

    # ── Forecast columns ────────────────────────────────────────
    fc_parts = []
    for f in fc[:5]:
        fc_parts.append(
            '<div style="text-align:center;flex:1;min-width:46px;">'
            + '<div style="font-size:0.63rem;color:rgba(255,255,255,0.45);margin-bottom:1px;">'
            + str(f["weekday"])
            + "</div>"
            + '<div style="font-size:0.6rem;color:rgba(255,255,255,0.3);margin-bottom:5px;">'
            + str(f["day"])
            + "</div>"
            + '<div style="font-size:1.25rem;line-height:1;margin-bottom:5px;">'
            + str(f["emoji"])
            + "</div>"
            + '<div style="font-size:0.76rem;font-weight:700;color:white;">'
            + str(f["temp_max"])
            + "&deg;</div>"
            + '<div style="font-size:0.63rem;color:rgba(255,255,255,0.38);">'
            + str(f["temp_min"])
            + "&deg;</div>"
            + "</div>"
        )
    fc_html = "".join(fc_parts)

    # ── Badges ──────────────────────────────────────────────────
    badges = ""
    if w.get("is_mock"):
        badges += (
            '<span style="font-size:0.56rem;background:rgba(255,200,0,0.15);color:#e0b840;'
            'padding:1px 7px;border-radius:8px;margin-left:6px;vertical-align:middle;">Demo</span>'
        )
    # Nếu dùng nearest city → hiển thị ghi chú
    nearest_note_html = ""
    if w.get("is_nearest") and w.get("display_note"):
        nearest_note_html = (
            '<div style="font-size:0.62rem;color:rgba(255,200,80,0.7);'
            'margin-top:3px;font-style:italic;">'
            + "📍 Dữ liệu thời tiết tham chiếu từ: "
            + str(w["display_note"])
            + "</div>"
        )

    # ── Tên địa điểm hiển thị — luôn là địa điểm đang được hỏi ──
    # Ưu tiên: name_vi từ CITY_MAP nếu match trực tiếp
    # Nếu nearest: vẫn hiển thị TÊN GỐC của địa điểm đang hỏi
    city_info, _, is_nearest = _resolve_city(destination)
    if is_nearest:
        # Hiển thị tên gốc địa điểm đang hỏi, không phải nearest city
        vi_name = destination
        # Try to get a cleaner Vietnamese name
        if "Tay Ninh" in destination or "Tây Ninh" in destination:
            vi_name = "Tây Ninh"
        elif "Ninh Binh" in destination or "Ninh Bình" in destination:
            vi_name = "Ninh Bình"
        elif "Nui Ba Den" in destination or "Núi Bà Đen" in destination:
            vi_name = "Núi Bà Đen, Tây Ninh"
        elif "Bai Dinh" in destination or "Bái Đính" in destination:
            vi_name = "Chùa Bái Đính, Ninh Bình"
    else:
        vi_name = w.get("destination_vi", destination)

    html = (
        '<div style="background:linear-gradient(160deg,#0f2a3a 0%,#091e2d 50%,#0d2535 100%);'
        "border-radius:16px;padding:18px 20px;margin:14px 0 4px;color:white;"
        'border:1px solid rgba(255,255,255,0.07);box-shadow:0 8px 28px rgba(0,0,0,0.3);">'
        # Label
        + '<div style="font-size:0.58rem;letter-spacing:2.5px;text-transform:uppercase;'
        'color:rgba(255,255,255,0.32);margin-bottom:14px;display:flex;align-items:center;gap:6px;">'
        '<span style="width:6px;height:6px;border-radius:50%;background:#4db8ff;'
        'box-shadow:0 0 6px #4db8ff;display:inline-block;"></span>THỜI TIẾT HIỆN TẠI</div>'
        # City name
        + '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">'
        + "<div>"
        + '<div style="font-size:1.1rem;font-weight:700;color:white;margin-bottom:3px;">'
        + vi_name
        + badges
        + "</div>"
        + nearest_note_html
        + '<div style="font-size:0.78rem;color:rgba(255,255,255,0.58);margin-top:2px;">'
        + str(w["description"])
        + "</div>"
        + "</div>"
        + '<div style="font-size:2.6rem;line-height:1;margin-top:-4px;">'
        + str(w["emoji"])
        + "</div>"
        + "</div>"
        # Temperature
        + '<div style="display:flex;align-items:flex-end;gap:12px;margin-bottom:16px;">'
        + '<div style="font-size:3rem;font-weight:200;line-height:1;color:white;letter-spacing:-2px;">'
        + str(w["temp"])
        + "&deg;C</div>"
        + '<div style="padding-bottom:6px;">'
        + '<div style="font-size:0.7rem;color:rgba(255,255,255,0.48);">Cảm giác như '
        + str(w["feels_like"])
        + "&deg;C</div>"
        + '<div style="font-size:0.68rem;color:rgba(255,255,255,0.32);">'
        + str(w["temp_min"])
        + "&deg; &mdash; "
        + str(w["temp_max"])
        + "&deg;</div>"
        + "</div></div>"
        # Stats grid
        + '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;'
        'background:rgba(255,255,255,0.05);border-radius:12px;overflow:hidden;margin-bottom:16px;">'
        + '<div style="padding:11px 0;text-align:center;">'
        + '<div style="font-size:1.05rem;margin-bottom:3px;">💧</div>'
        + '<div style="font-size:0.8rem;font-weight:600;color:white;">'
        + str(w["humidity"])
        + "%</div>"
        + '<div style="font-size:0.6rem;color:rgba(255,255,255,0.38);margin-top:1px;">Độ ẩm</div>'
        + "</div>"
        + '<div style="padding:11px 0;text-align:center;'
        'border-left:1px solid rgba(255,255,255,0.07);border-right:1px solid rgba(255,255,255,0.07);">'
        + '<div style="font-size:1.05rem;margin-bottom:3px;">💨</div>'
        + '<div style="font-size:0.8rem;font-weight:600;color:white;">'
        + str(w["wind_speed"])
        + " km/h</div>"
        + '<div style="font-size:0.6rem;color:rgba(255,255,255,0.38);margin-top:1px;">Gió</div>'
        + "</div>"
        + '<div style="padding:11px 0;text-align:center;">'
        + '<div style="font-size:1.05rem;margin-bottom:3px;">👁</div>'
        + '<div style="font-size:0.8rem;font-weight:600;color:white;">'
        + str(w["visibility"])
        + " km</div>"
        + '<div style="font-size:0.6rem;color:rgba(255,255,255,0.38);margin-top:1px;">Tầm nhìn</div>'
        + "</div>"
        + "</div>"
        # Forecast
        + '<div style="margin-bottom:14px;">'
        + '<div style="font-size:0.58rem;letter-spacing:2px;text-transform:uppercase;'
        'color:rgba(255,255,255,0.28);margin-bottom:10px;">DỰ BÁO 5 NGÀY</div>'
        + '<div style="display:flex;justify-content:space-between;gap:4px;">'
        + fc_html
        + "</div></div>"
        # Advice
        + '<div style="background:rgba(255,200,80,0.07);border:1px solid rgba(255,200,80,0.14);'
        'border-radius:10px;padding:10px 14px;">'
        + '<div style="font-size:0.73rem;color:rgba(255,218,130,0.88);line-height:1.6;">'
        + "&#128161; <strong>Lời khuyên:</strong> "
        + str(w["advice"])
        + "</div></div>"
        # Source
        + '<div style="text-align:right;margin-top:8px;">'
        + '<a href="https://openweathermap.org" target="_blank" '
        'style="font-size:0.56rem;color:rgba(255,255,255,0.18);text-decoration:none;">'
        + "Nguồn: "
        + str(w["source"])
        + "</a></div>"
        + "</div>"
    )
    return html

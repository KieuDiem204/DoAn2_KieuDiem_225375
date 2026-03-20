"""
tour_links.py — Tour booking links, built via string concatenation only.
No nested f-strings => no HTML escaping issues when passed to st.markdown.
"""

DESTINATION_TOURS = {
    "Da Lat": {
        "tours": [
            {
                "name": "Tour Đà Lạt 3N2Đ từ TP.HCM",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=da+lat+tour",
                "price": "Từ 1,200,000₫",
                "tags": "Xe giường nằm · Khách sạn 3★ · HDV",
                "type": "PACKAGE",
            },
            {
                "name": "Thuê xe máy khám phá Đà Lạt",
                "platform": "Traveloka",
                "color": "#0064D2",
                "bg": "#f0f6ff",
                "url": "https://www.traveloka.com/vi-vn/tiket-atraksi/search/dalat--106009",
                "price": "Từ 120,000₫/ngày",
                "tags": "Xe máy · Bản đồ · Hỗ trợ 24/7",
                "type": "ACTIVITY",
            },
            {
                "name": "Tour 1 ngày Thác & Vườn hoa",
                "platform": "Viator",
                "color": "#00AA6C",
                "bg": "#f0fff8",
                "url": "https://www.viator.com/en-US/Dalat/d27434",
                "price": "Từ $15/người",
                "tags": "Xe đưa đón · HDV · Vé tham quan",
                "type": "DAYTRIP",
            },
        ],
        "hotels": [
            {
                "name": "Khách sạn 3★ trung tâm",
                "platform": "Agoda",
                "color": "#E44D26",
                "bg": "#fff2ee",
                "url": "https://www.agoda.com/vi-vn/city/da-lat-vn.html",
                "price": "Từ 350,000₫/đêm",
            },
            {
                "name": "Resort Đà Lạt cao cấp",
                "platform": "Booking.com",
                "color": "#003580",
                "bg": "#f0f4ff",
                "url": "https://www.booking.com/city/vn/da-lat.vi.html",
                "price": "Từ 1,000,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Bay tới Sân bay Liên Khương (DLI). Xe khách từ HCM: 6-7h.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/SGN-DLI/",
        },
    },
    "Can Tho": {
        "tours": [
            {
                "name": "Tour chợ nổi Cái Răng sáng sớm",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=can+tho+floating+market",
                "price": "Từ 250,000₫",
                "tags": "Xuồng máy · HDV · Đón tại KS",
                "type": "ACTIVITY",
            },
            {
                "name": "Tour miệt vườn Cần Thơ nửa ngày",
                "platform": "Viator",
                "color": "#00AA6C",
                "bg": "#f0fff8",
                "url": "https://www.viator.com/en-US/Can-Tho/d26456",
                "price": "Từ $20/người",
                "tags": "Đò xuồng · Vườn trái cây · HDV",
                "type": "HALFDAY",
            },
            {
                "name": "Tour 2N1Đ từ TP.HCM",
                "platform": "Traveloka",
                "color": "#0064D2",
                "bg": "#f0f6ff",
                "url": "https://www.traveloka.com/vi-vn/tiket-atraksi/search/can-tho--105886",
                "price": "Từ 850,000₫",
                "tags": "Xe khách · KS · Chợ nổi · Ăn sáng",
                "type": "PACKAGE",
            },
        ],
        "hotels": [
            {
                "name": "Khách sạn trung tâm Cần Thơ",
                "platform": "Agoda",
                "color": "#E44D26",
                "bg": "#fff2ee",
                "url": "https://www.agoda.com/vi-vn/city/can-tho-vn.html",
                "price": "Từ 300,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Bay HCM→Cần Thơ (VCA) 45 phút. Hoặc xe khách 3-4 giờ.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/SGN-VCA/",
        },
    },
    "Ha Long": {
        "tours": [
            {
                "name": "Du thuyền Hạ Long 2N1Đ hạng sang",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=ha+long+bay+cruise",
                "price": "Từ 1,800,000₫",
                "tags": "Du thuyền 4★ · Bữa ăn · Kayak · Hang",
                "type": "CRUISE",
            },
            {
                "name": "Tour 1 ngày từ Hà Nội",
                "platform": "Viator",
                "color": "#00AA6C",
                "bg": "#f0fff8",
                "url": "https://www.viator.com/en-US/Ha-Long-Bay/d24218",
                "price": "Từ $35/người",
                "tags": "Xe đưa đón · Tàu · Ăn trưa",
                "type": "DAYTRIP",
            },
            {
                "name": "Vé cáp treo Sun World Hạ Long",
                "platform": "GetYourGuide",
                "color": "#E7252B",
                "bg": "#fff0f0",
                "url": "https://www.getyourguide.com/ha-long-l110/",
                "price": "Từ 350,000₫",
                "tags": "Cáp treo · Vé công viên",
                "type": "TICKET",
            },
        ],
        "hotels": [
            {
                "name": "Khách sạn Hạ Long",
                "platform": "Booking.com",
                "color": "#003580",
                "bg": "#f0f4ff",
                "url": "https://www.booking.com/city/vn/ha-long.vi.html",
                "price": "Từ 500,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Bay HN→Vân Đồn (VDO) 40 phút. Hoặc xe khách từ HN 3-4h.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/HAN-VDO/",
        },
    },
    "Hoi An": {
        "tours": [
            {
                "name": "Vé tham quan phố cổ Hội An",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=hoi+an+old+town",
                "price": "Từ 120,000₫",
                "tags": "5 điểm di sản · HDV",
                "type": "TICKET",
            },
            {
                "name": "Học làm đèn lồng & nấu ăn",
                "platform": "GetYourGuide",
                "color": "#E7252B",
                "bg": "#fff0f0",
                "url": "https://www.getyourguide.com/hoi-an-l1059/",
                "price": "Từ $18/người",
                "tags": "Lớp học 2h · Vật liệu · HDV",
                "type": "ACTIVITY",
            },
            {
                "name": "Tour Cù Lao Chàm lặn biển",
                "platform": "Viator",
                "color": "#00AA6C",
                "bg": "#f0fff8",
                "url": "https://www.viator.com/en-US/Hoi-An/d736",
                "price": "Từ $25/người",
                "tags": "Tàu · Đồ lặn · Ăn trưa hải sản",
                "type": "ISLAND",
            },
        ],
        "hotels": [
            {
                "name": "Homestay phố cổ Hội An",
                "platform": "Agoda",
                "color": "#E44D26",
                "bg": "#fff2ee",
                "url": "https://www.agoda.com/vi-vn/city/hoi-an-vn.html",
                "price": "Từ 300,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Bay đến Đà Nẵng (DAD), xe 30 phút đến Hội An.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/SGN-DAD/",
        },
    },
    "Phu Quoc": {
        "tours": [
            {
                "name": "Combo Vinpearl Land Phú Quốc",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=vinpearl+phu+quoc",
                "price": "Từ 650,000₫",
                "tags": "Vinpearl · Cáp treo · Safari",
                "type": "TICKET",
            },
            {
                "name": "Tour lặn biển 4 đảo",
                "platform": "Viator",
                "color": "#00AA6C",
                "bg": "#f0fff8",
                "url": "https://www.viator.com/en-US/Phu-Quoc/d23408",
                "price": "Từ $30/người",
                "tags": "Tàu cao tốc · Đồ lặn · Ăn trưa",
                "type": "ISLAND",
            },
            {
                "name": "Tour 4N3Đ bay thẳng trọn gói",
                "platform": "Traveloka",
                "color": "#0064D2",
                "bg": "#f0f6ff",
                "url": "https://www.traveloka.com/vi-vn/tiket-atraksi/search/phu-quoc--103668",
                "price": "Từ 3,500,000₫",
                "tags": "Vé bay · Resort 4★ · Tour đảo",
                "type": "PACKAGE",
            },
        ],
        "hotels": [
            {
                "name": "Resort Phú Quốc ven biển",
                "platform": "Booking.com",
                "color": "#003580",
                "bg": "#f0f4ff",
                "url": "https://www.booking.com/city/vn/phu-quoc.vi.html",
                "price": "Từ 800,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Bay HCM (SGN) → Phú Quốc (PQC) ~50 phút.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/SGN-PQC/",
        },
    },
    "Nha Trang": {
        "tours": [
            {
                "name": "Vinpearl Land Nha Trang",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=vinpearl+nha+trang",
                "price": "Từ 800,000₫",
                "tags": "Vé VinpearlLand · Cáp treo biển",
                "type": "TICKET",
            },
            {
                "name": "Tour lặn biển đảo Hòn Mun",
                "platform": "GetYourGuide",
                "color": "#E7252B",
                "bg": "#fff0f0",
                "url": "https://www.getyourguide.com/nha-trang-l120/",
                "price": "Từ $22/người",
                "tags": "Đồ lặn · HDV · Ăn trưa",
                "type": "ACTIVITY",
            },
            {
                "name": "Tour 4 đảo Nha Trang",
                "platform": "Viator",
                "color": "#00AA6C",
                "bg": "#f0fff8",
                "url": "https://www.viator.com/en-US/Nha-Trang/d5439",
                "price": "Từ $15/người",
                "tags": "Tàu gỗ · 4 đảo · Ăn trưa hải sản",
                "type": "ISLAND",
            },
        ],
        "hotels": [
            {
                "name": "Khách sạn biển Nha Trang",
                "platform": "Agoda",
                "color": "#E44D26",
                "bg": "#fff2ee",
                "url": "https://www.agoda.com/vi-vn/city/nha-trang-vn.html",
                "price": "Từ 400,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Bay HCM (SGN) → Cam Ranh (CXR) ~1 giờ.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/SGN-CXR/",
        },
    },
    "Sa Pa": {
        "tours": [
            {
                "name": "Cáp treo Fansipan Sa Pa",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=fansipan+cable+car",
                "price": "Từ 700,000₫",
                "tags": "Cáp treo khứ hồi · Tàu leo núi",
                "type": "TICKET",
            },
            {
                "name": "Trek bản làng 2 ngày",
                "platform": "GetYourGuide",
                "color": "#E7252B",
                "bg": "#fff0f0",
                "url": "https://www.getyourguide.com/sapa-l636/",
                "price": "Từ $35/người",
                "tags": "Guide H'Mông · Homestay · 2 bữa",
                "type": "TREKKING",
            },
            {
                "name": "Tour Sa Pa 3N2Đ từ Hà Nội",
                "platform": "Viator",
                "color": "#00AA6C",
                "bg": "#f0fff8",
                "url": "https://www.viator.com/en-US/Sa-Pa/d4851",
                "price": "Từ $60/người",
                "tags": "Tàu/xe · KS · HDV · Trekking",
                "type": "PACKAGE",
            },
        ],
        "hotels": [
            {
                "name": "Khách sạn Sa Pa view thung lũng",
                "platform": "Booking.com",
                "color": "#003580",
                "bg": "#f0f4ff",
                "url": "https://www.booking.com/city/vn/sapa.vi.html",
                "price": "Từ 400,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Từ HN: tàu đêm đến Lào Cai (8-9h) → xe 1h đến Sa Pa.",
            "url": "https://www.traveloka.com/vi-vn/train/search/HAN-LAOKAI/",
        },
    },
    "Hanoi": {
        "tours": [
            {
                "name": "Tour phố cổ & ẩm thực Hà Nội",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=hanoi+old+quarter",
                "price": "Từ $12/người",
                "tags": "HDV · Hop-on bus · Ẩm thực",
                "type": "CITY",
            },
            {
                "name": "Day trip Hà Nội + Hạ Long",
                "platform": "GetYourGuide",
                "color": "#E7252B",
                "bg": "#fff0f0",
                "url": "https://www.getyourguide.com/hanoi-l108/",
                "price": "Từ $35/người",
                "tags": "Xe đưa đón · Tàu vịnh · Ăn trưa",
                "type": "DAYTRIP",
            },
        ],
        "hotels": [
            {
                "name": "Khách sạn phố cổ Hoàn Kiếm",
                "platform": "Agoda",
                "color": "#E44D26",
                "bg": "#fff2ee",
                "url": "https://www.agoda.com/vi-vn/city/hanoi-vn.html",
                "price": "Từ 350,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Bay HCM (SGN) → Hà Nội (HAN) ~2 giờ.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/SGN-HAN/",
        },
    },
    "Da Nang": {
        "tours": [
            {
                "name": "Vé Bà Nà Hills — Cầu Vàng",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=ba+na+hills",
                "price": "Từ 700,000₫",
                "tags": "Cáp treo · Tất cả trò chơi",
                "type": "TICKET",
            },
            {
                "name": "Tour Hội An & Mỹ Sơn 1 ngày",
                "platform": "Viator",
                "color": "#00AA6C",
                "bg": "#f0fff8",
                "url": "https://www.viator.com/en-US/Da-Nang/d350",
                "price": "Từ $18/người",
                "tags": "Xe đưa đón · HDV · Vé tham quan",
                "type": "DAYTRIP",
            },
        ],
        "hotels": [
            {
                "name": "Khách sạn biển Mỹ Khê",
                "platform": "Booking.com",
                "color": "#003580",
                "bg": "#f0f4ff",
                "url": "https://www.booking.com/city/vn/da-nang.vi.html",
                "price": "Từ 500,000₫/đêm",
            },
        ],
        "flight": {
            "note": "Bay HCM (SGN) → Đà Nẵng (DAD) ~1 giờ 15 phút.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/SGN-DAD/",
        },
    },
    "Bangkok": {
        "tours": [
            {
                "name": "Bangkok Temple & City Tour",
                "platform": "Klook",
                "color": "#FF6B35",
                "bg": "#fff3ee",
                "url": "https://www.klook.com/vi/search/?query=bangkok+temple+tour",
                "price": "Từ $18/người",
                "tags": "Tuk-tuk · Wat Pho · Wat Arun · HDV",
                "type": "CITY",
            },
            {
                "name": "Chợ nổi Damnoen Saduak",
                "platform": "GetYourGuide",
                "color": "#E7252B",
                "bg": "#fff0f0",
                "url": "https://www.getyourguide.com/bangkok-l169/",
                "price": "Từ $25/người",
                "tags": "Xe đưa đón · Thuyền · HDV",
                "type": "DAYTRIP",
            },
        ],
        "hotels": [
            {
                "name": "Khách sạn Bangkok trung tâm",
                "platform": "Agoda",
                "color": "#E44D26",
                "bg": "#fff2ee",
                "url": "https://www.agoda.com/vi-vn/city/bangkok-th.html",
                "price": "Từ $25/đêm",
            },
        ],
        "flight": {
            "note": "Bay HCM (SGN) → Bangkok (BKK) ~1 giờ 45 phút.",
            "url": "https://www.traveloka.com/vi-vn/flight/search/airport/SGN-BKK/",
        },
    },
}

_DEFAULT = {
    "tours": [
        {
            "name": "Tìm tour trên Klook",
            "platform": "Klook",
            "color": "#FF6B35",
            "bg": "#fff3ee",
            "url": "https://www.klook.com/vi/",
            "price": "Nhiều giá",
            "tags": "Tours · Vé · Hoạt động",
            "type": "GENERAL",
        },
        {
            "name": "Tìm tour trên GetYourGuide",
            "platform": "GetYourGuide",
            "color": "#E7252B",
            "bg": "#fff0f0",
            "url": "https://www.getyourguide.com",
            "price": "Nhiều giá",
            "tags": "Tours quốc tế · Trải nghiệm",
            "type": "GENERAL",
        },
        {
            "name": "Tìm tour trên Viator",
            "platform": "Viator",
            "color": "#00AA6C",
            "bg": "#f0fff8",
            "url": "https://www.viator.com",
            "price": "Nhiều giá",
            "tags": "300,000+ hoạt động",
            "type": "GENERAL",
        },
    ],
    "hotels": [
        {
            "name": "Tìm KS trên Booking.com",
            "platform": "Booking.com",
            "color": "#003580",
            "bg": "#f0f4ff",
            "url": "https://www.booking.com",
            "price": "Giá tốt nhất",
        },
        {
            "name": "Tìm KS trên Agoda",
            "platform": "Agoda",
            "color": "#E44D26",
            "bg": "#fff2ee",
            "url": "https://www.agoda.com/vi-vn",
            "price": "Giảm giá Asia",
        },
    ],
    "flight": {
        "note": "Tìm vé máy bay trên Traveloka, Google Flights hoặc Skyscanner.",
        "url": "https://www.traveloka.com/vi-vn/flight",
    },
}


def _tour_card(t):
    """Build one tour card via string concat — no f-strings."""
    return (
        '<a href="' + t["url"] + '" target="_blank" '
        'style="text-decoration:none;display:block;background:white;'
        "border:1px solid rgba(0,0,0,0.07);border-radius:10px;"
        'padding:11px 13px;margin-bottom:7px;">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">'
        # Left: badges + name + tags
        '<div style="flex:1;min-width:0;">'
        '<div style="display:flex;align-items:center;gap:5px;margin-bottom:4px;">'
        '<span style="background:' + t["bg"] + ";color:" + t["color"] + ";"
        'font-size:0.6rem;font-weight:700;padding:2px 7px;border-radius:8px;">'
        + t["platform"]
        + "</span>"
        '<span style="font-size:0.6rem;color:#999;background:#f5f5f5;'
        'padding:2px 5px;border-radius:5px;">' + t["type"] + "</span>"
        "</div>"
        '<div style="font-size:0.83rem;font-weight:600;color:#1c1410;'
        'margin-bottom:3px;line-height:1.3;">' + t["name"] + "</div>"
        '<div style="font-size:0.68rem;color:#999;line-height:1.4;">'
        + t["tags"]
        + "</div>"
        "</div>"
        # Right: price + arrow
        '<div style="text-align:right;flex-shrink:0;">'
        '<div style="font-size:0.76rem;font-weight:700;color:'
        + t["color"]
        + ';white-space:nowrap;">'
        + t["price"]
        + "</div>"
        '<div style="font-size:0.85rem;color:#ddd;margin-top:2px;">&rarr;</div>'
        "</div>"
        "</div>"
        "</a>"
    )


def _hotel_chip(h):
    return (
        '<a href="' + h["url"] + '" target="_blank" '
        'style="text-decoration:none;display:inline-flex;align-items:center;gap:5px;'
        "background:" + h["bg"] + ";border:1px solid " + h["color"] + "22;"
        'border-radius:7px;padding:5px 10px;margin:3px 4px 3px 0;">'
        '<span style="font-size:0.7rem;font-weight:700;color:'
        + h["color"]
        + ';">'
        + h["platform"]
        + "</span>"
        '<span style="font-size:0.68rem;color:#777;">' + h["price"] + "</span>"
        "</a>"
    )


def build_tour_links_html(destination, lang="vi"):
    """Build tour links card as pure string concatenation. Safe for st.markdown."""
    data = DESTINATION_TOURS.get(destination, _DEFAULT)
    tours = data.get("tours", [])
    hotels = data.get("hotels", [])
    flight = data.get("flight", {})

    if not tours:
        return ""

    # Tour cards
    tours_html = "".join(_tour_card(t) for t in tours[:3])

    # Hotel chips
    hotels_html = "".join(_hotel_chip(h) for h in hotels[:3])

    # Flight row
    flight_html = ""
    if flight:
        flight_html = (
            '<div style="background:#f8f9fb;border-radius:8px;padding:9px 12px;margin-top:6px;">'
            '<div style="font-size:0.69rem;color:#555;margin-bottom:4px;">&#9992;&#65039; '
            + str(flight.get("note", ""))
            + "</div>"
            '<a href="' + str(flight.get("url", "#")) + '" target="_blank" '
            'style="font-size:0.7rem;font-weight:700;color:#0064D2;text-decoration:none;">'
            "Tìm vé trên Traveloka &rarr;</a>"
            "</div>"
        )

    # Platform footer links
    footer = (
        '<div style="margin-top:10px;padding-top:9px;'
        'border-top:1px solid rgba(0,0,0,0.05);display:flex;gap:6px;flex-wrap:wrap;">'
        '<a href="https://www.traveloka.com/vi-vn" target="_blank" style="font-size:0.66rem;color:#0064D2;text-decoration:none;font-weight:600;">Traveloka</a>'
        '<span style="color:#ddd;">&middot;</span>'
        '<a href="https://www.klook.com/vi" target="_blank" style="font-size:0.66rem;color:#FF6B35;text-decoration:none;font-weight:600;">Klook</a>'
        '<span style="color:#ddd;">&middot;</span>'
        '<a href="https://www.getyourguide.com" target="_blank" style="font-size:0.66rem;color:#E7252B;text-decoration:none;font-weight:600;">GetYourGuide</a>'
        '<span style="color:#ddd;">&middot;</span>'
        '<a href="https://www.viator.com" target="_blank" style="font-size:0.66rem;color:#00AA6C;text-decoration:none;font-weight:600;">Viator</a>'
        '<span style="color:#ddd;">&middot;</span>'
        '<a href="https://www.booking.com" target="_blank" style="font-size:0.66rem;color:#003580;text-decoration:none;font-weight:600;">Booking</a>'
        '<span style="color:#ddd;">&middot;</span>'
        '<a href="https://www.agoda.com/vi-vn" target="_blank" style="font-size:0.66rem;color:#E44D26;text-decoration:none;font-weight:600;">Agoda</a>'
        "</div>"
    )

    return (
        '<div style="background:#faf8f4;border:1px solid rgba(184,150,90,0.18);'
        'border-radius:13px;padding:15px 16px;font-family:DM Sans,sans-serif;">'
        '<div style="font-size:0.59rem;letter-spacing:2px;text-transform:uppercase;'
        'color:rgba(26,58,58,0.45);margin-bottom:11px;">'
        "&#128506; ĐẶT TOUR &amp; VÉ THAM QUAN</div>"
        + tours_html
        + '<div style="margin-top:8px;">'
        '<div style="font-size:0.59rem;letter-spacing:1.5px;text-transform:uppercase;'
        'color:rgba(26,58,58,0.38);margin-bottom:5px;">&#127968; ĐẶT KHÁCH SẠN</div>'
        '<div style="display:flex;flex-wrap:wrap;">' + hotels_html + "</div>"
        "</div>" + flight_html + footer + "</div>"
    )

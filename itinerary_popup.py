"""
itinerary_popup.py — v7.0
Render itinerary button + modal bằng st.components.v1.html()
Sửa: tiếng Việt đầy đủ, modal z-index vượt iframe, font đẹp.
"""

import hashlib
import streamlit.components.v1 as components


def render_itinerary_component(
    msg_index: int,
    destination: str,
    lang: str = "vi",
) -> None:
    """Render trực tiếp vào Streamlit bằng components.html()."""
    if not destination or destination in ("Unknown", ""):
        return
    html = _build_full_html(msg_index, destination, lang)
    components.html(html, height=56, scrolling=False)


def build_itinerary_button_and_modal(
    msg_index: int,
    destination: str,
    lang: str = "vi",
) -> str:
    """Giữ tương thích — không dùng nữa."""
    return ""


def _build_full_html(msg_index: int, destination: str, lang: str) -> str:
    uid = "it" + hashlib.md5(f"{msg_index}{destination}".encode()).hexdigest()[:8]
    is_vi = lang == "vi"

    # ── Labels ────────────────────────────────────────────────────
    btn_label = "📅 Xem lịch trình" if is_vi else "📅 View Itinerary"
    day_badge = "3 ngày" if is_vi else "3 days"
    loading_text = (
        f"Aria đang lên kế hoạch cho {destination}…"
        if is_vi
        else f"Aria is planning your {destination} trip…"
    )
    error_text = (
        "Không thể tải lịch trình. Vui lòng thử lại."
        if is_vi
        else "Could not load itinerary. Please try again."
    )
    modal_sub = "LỊCH TRÌNH GỢI Ý" if is_vi else "SUGGESTED ITINERARY"
    retry_lbl = "Thử lại" if is_vi else "Retry"
    highlights_lbl = "✨ ĐIỂM NỔI BẬT" if is_vi else "✨ HIGHLIGHTS"
    itinerary_lbl = "🗓 LỊCH TRÌNH CHI TIẾT" if is_vi else "🗓 DETAILED ITINERARY"
    tips_lbl = "💡 MẸO QUAN TRỌNG" if is_vi else "💡 IMPORTANT TIPS"
    close_lbl = "Đóng" if is_vi else "Close"

    # ── Prompt ────────────────────────────────────────────────────
    if is_vi:
        raw_prompt = (
            f"Bạn là Aria - hướng dẫn viên du lịch 15 năm kinh nghiệm. "
            f"Hãy tạo lịch trình 3 ngày cho {destination} bằng TIẾNG VIỆT. "
            f"Chỉ trả về JSON thuần túy (không markdown, không text ngoài JSON): "
            f'{{"title":"Tên đầy đủ điểm đến","emoji":"🏖","duration":"3 ngày 2 đêm","best_time":"Tháng đẹp nhất","budget":"X-Y triệu/người",'
            f'"highlights":["Điểm nổi bật 1","Điểm nổi bật 2","Điểm nổi bật 3","Điểm nổi bật 4","Điểm nổi bật 5"],'
            f'"tips":["Mẹo 1","Mẹo 2","Mẹo 3","Mẹo 4","Mẹo 5"],'
            f'"days":['
            f'{{"day":"Ngày 1","theme":"Khám phá trung tâm","color":"#c4845a","slots":['
            f'{{"time":"06:00","emoji":"☕","name":"Ăn sáng đặc sản địa phương","tip":"Mô tả chi tiết hoạt động"}},'
            f'{{"time":"08:30","emoji":"🌅","name":"Tên hoạt động","tip":"Mô tả chi tiết"}},'
            f'{{"time":"10:00","emoji":"🏛","name":"Tên hoạt động","tip":"Mô tả chi tiết"}},'
            f'{{"time":"12:00","emoji":"🍜","name":"Ăn trưa","tip":"Mô tả chi tiết"}},'
            f'{{"time":"14:00","emoji":"🎯","name":"Tên hoạt động","tip":"Mô tả chi tiết"}},'
            f'{{"time":"17:00","emoji":"🌇","name":"Ngắm hoàng hôn","tip":"Mô tả chi tiết"}},'
            f'{{"time":"19:00","emoji":"🍽","name":"Ăn tối","tip":"Mô tả chi tiết"}}'
            f"]}},"
            f'{{"day":"Ngày 2","theme":"Thiên nhiên & Trải nghiệm","color":"#2d5555","slots":['
            f'{{"time":"06:30","emoji":"🌄","name":"Tên hoạt động","tip":"Mô tả"}},'
            f'{{"time":"08:00","emoji":"🚤","name":"Tên hoạt động","tip":"Mô tả"}},'
            f'{{"time":"10:30","emoji":"🤿","name":"Tên hoạt động","tip":"Mô tả"}},'
            f'{{"time":"12:30","emoji":"🥗","name":"Ăn trưa","tip":"Mô tả"}},'
            f'{{"time":"14:30","emoji":"🏝","name":"Tên hoạt động","tip":"Mô tả"}},'
            f'{{"time":"17:30","emoji":"🛍","name":"Tên hoạt động","tip":"Mô tả"}},'
            f'{{"time":"20:00","emoji":"🎵","name":"Tên hoạt động","tip":"Mô tả"}}'
            f"]}},"
            f'{{"day":"Ngày 3","theme":"Văn hóa & Chia tay","color":"#b8965a","slots":['
            f'{{"time":"07:00","emoji":"🌺","name":"Tên hoạt động","tip":"Mô tả"}},'
            f'{{"time":"09:00","emoji":"🎨","name":"Tên hoạt động","tip":"Mô tả"}},'
            f'{{"time":"11:30","emoji":"🛒","name":"Tên hoạt động","tip":"Mô tả"}},'
            f'{{"time":"13:00","emoji":"🍲","name":"Ăn trưa","tip":"Mô tả"}},'
            f'{{"time":"15:00","emoji":"✈","name":"Trở về","tip":"Mô tả"}}'
            f"]}}"
            f"]}}"
        )
    else:
        raw_prompt = (
            f"You are Aria, professional tour guide with 15 years experience. "
            f"Create a 3-day itinerary for {destination} in English. "
            f"Return ONLY pure JSON (no markdown, no extra text): "
            f'{{"title":"Full destination name","emoji":"🏖","duration":"3 days 2 nights","best_time":"Best months to visit","budget":"$X-$Y per person",'
            f'"highlights":["Highlight 1","Highlight 2","Highlight 3","Highlight 4","Highlight 5"],'
            f'"tips":["Tip 1","Tip 2","Tip 3","Tip 4","Tip 5"],'
            f'"days":['
            f'{{"day":"Day 1","theme":"City Exploration","color":"#c4845a","slots":['
            f'{{"time":"06:00","emoji":"☕","name":"Local breakfast","tip":"Detailed description"}},'
            f'{{"time":"08:30","emoji":"🌅","name":"Activity name","tip":"Detail"}},'
            f'{{"time":"10:00","emoji":"🏛","name":"Activity name","tip":"Detail"}},'
            f'{{"time":"12:00","emoji":"🍜","name":"Lunch","tip":"Detail"}},'
            f'{{"time":"14:00","emoji":"🎯","name":"Activity name","tip":"Detail"}},'
            f'{{"time":"17:00","emoji":"🌇","name":"Sunset viewing","tip":"Detail"}},'
            f'{{"time":"19:00","emoji":"🍽","name":"Dinner","tip":"Detail"}}'
            f"]}},"
            f'{{"day":"Day 2","theme":"Nature & Adventure","color":"#2d5555","slots":['
            f'{{"time":"06:30","emoji":"🌄","name":"Activity","tip":"Detail"}},'
            f'{{"time":"08:00","emoji":"🚤","name":"Activity","tip":"Detail"}},'
            f'{{"time":"10:30","emoji":"🤿","name":"Activity","tip":"Detail"}},'
            f'{{"time":"12:30","emoji":"🥗","name":"Lunch","tip":"Detail"}},'
            f'{{"time":"14:30","emoji":"🏝","name":"Activity","tip":"Detail"}},'
            f'{{"time":"17:30","emoji":"🛍","name":"Shopping","tip":"Detail"}},'
            f'{{"time":"20:00","emoji":"🎵","name":"Evening","tip":"Detail"}}'
            f"]}},"
            f'{{"day":"Day 3","theme":"Culture & Farewell","color":"#b8965a","slots":['
            f'{{"time":"07:00","emoji":"🌺","name":"Activity","tip":"Detail"}},'
            f'{{"time":"09:00","emoji":"🎨","name":"Activity","tip":"Detail"}},'
            f'{{"time":"11:30","emoji":"🛒","name":"Shopping","tip":"Detail"}},'
            f'{{"time":"13:00","emoji":"🍲","name":"Lunch","tip":"Detail"}},'
            f'{{"time":"15:00","emoji":"✈","name":"Departure","tip":"Detail"}}'
            f"]}}"
            f"]}}"
        )

    # Escape cho JS template literal
    prompt_js = (
        raw_prompt.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
        .replace("\n", " ")
    )
    dest_js = destination.replace("'", "\\'").replace('"', '\\"')

    # ── Skeleton loader rows ───────────────────────────────────────
    skel = "".join(
        f'<div class="sk" style="height:{h}px;width:{w}%;margin-bottom:8px;border-radius:6px;"></div>'
        for h, w in [
            (14, 60),
            (9, 88),
            (9, 75),
            (14, 50),
            (9, 90),
            (9, 70),
            (9, 82),
            (14, 55),
            (9, 86),
        ]
    )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'DM Sans',system-ui,sans-serif;overflow:visible !important;}}

/* ── Nút mở ── */
#btn-{uid}{{
  display:inline-flex;align-items:center;gap:7px;
  padding:7px 18px 7px 14px;border:none;border-radius:30px;
  cursor:pointer;font-family:inherit;font-size:.78rem;font-weight:700;
  color:white;background:linear-gradient(135deg,#c4845a,#a06030);
  box-shadow:0 4px 16px rgba(196,132,90,.45);
  animation:drift 3s ease-in-out infinite, glow 3s ease-in-out infinite;
  transition:transform .15s,box-shadow .15s;
}}
#btn-{uid}:hover{{
  animation:none;transform:translateY(-2px) scale(1.04);
  box-shadow:0 10px 28px rgba(196,132,90,.65);
  background:linear-gradient(135deg,#d4967a,#c4845a);
}}
.bdg-{uid}{{font-size:.6rem;background:rgba(255,255,255,.22);padding:2px 9px;border-radius:10px;letter-spacing:.5px;}}

/* ── Overlay ── */
#ov-{uid}{{
  display:none;position:fixed;inset:0;
  background:rgba(10,20,28,.82);
  z-index:2147483647;
  align-items:center;justify-content:center;
  padding:16px;
  backdrop-filter:blur(4px);
  -webkit-backdrop-filter:blur(4px);
}}
#ov-{uid}.open{{display:flex;animation:fadeIn .22s ease;}}

/* ── Sheet ── */
#sh-{uid}{{
  background:#fffdf9;border-radius:20px;
  width:100%;max-width:700px;max-height:90vh;
  overflow:hidden;display:flex;flex-direction:column;
  box-shadow:0 32px 80px rgba(0,0,0,.5);
  animation:slideUp .35s cubic-bezier(.34,1.48,.64,1);
}}

/* ── Header modal ── */
#hdr-{uid}{{
  background:linear-gradient(140deg,#1a3a3a 0%,#2d5555 60%,#1a3a3a 100%);
  padding:22px 24px 18px;flex-shrink:0;
  border-bottom:2px solid rgba(184,150,90,.25);
}}
.close-btn-{uid}{{
  background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.15);
  color:rgba(255,255,255,.9);width:34px;height:34px;border-radius:50%;
  cursor:pointer;font-size:1rem;display:flex;align-items:center;justify-content:center;
  transition:background .15s,transform .15s;flex-shrink:0;
}}
.close-btn-{uid}:hover{{background:rgba(255,255,255,.25);transform:rotate(90deg) scale(1.1);}}

/* ── Body modal ── */
#bdy-{uid}{{overflow-y:auto;flex:1;padding:20px 24px 28px;}}
#bdy-{uid}::-webkit-scrollbar{{width:4px;}}
#bdy-{uid}::-webkit-scrollbar-thumb{{background:#ddd3c4;border-radius:2px;}}

/* ── Skeleton ── */
.sk{{background:linear-gradient(90deg,#ede8e0 25%,#f5f0e8 50%,#ede8e0 75%);
     background-size:200% 100%;animation:sk 1.5s ease-in-out infinite;}}
@keyframes sk{{0%{{background-position:200% 0;}}100%{{background-position:-200% 0;}}}}

/* ── Tab ngày ── */
.tab-{uid}{{
  padding:7px 14px;border:1px solid rgba(26,58,58,.15);border-radius:20px;
  cursor:pointer;font-size:.71rem;font-weight:600;font-family:inherit;
  background:rgba(26,58,58,.05);color:#4a5568;
  transition:all .2s;white-space:nowrap;
}}
.tab-{uid}.active{{color:white;border-color:transparent;
  box-shadow:0 3px 12px rgba(0,0,0,.2);}}
.tab-{uid}:hover:not(.active){{background:rgba(196,132,90,.12);color:#1a3a3a;border-color:rgba(196,132,90,.3);}}

/* ── Slot hoạt động ── */
.slot-{uid}{{
  display:flex;gap:12px;padding:10px 8px;
  border-bottom:1px solid rgba(0,0,0,.04);
  align-items:flex-start;border-radius:8px;
  transition:background .12s,padding-left .12s;
}}
.slot-{uid}:last-child{{border-bottom:none;}}
.slot-{uid}:hover{{background:rgba(196,132,90,.05);padding-left:12px;}}

/* ── Pill badge ── */
.pill{{display:inline-block;font-size:.67rem;font-weight:600;
       padding:3px 11px;border-radius:11px;margin:2px 3px 2px 0;
       background:rgba(26,58,58,.07);color:#1a3a3a;}}

/* ── Tip item ── */
.tip-item{{font-size:.76rem;color:#4a5568;line-height:1.65;
           padding:6px 0;border-bottom:1px solid rgba(184,150,90,.1);}}
.tip-item:last-child{{border-bottom:none;}}
.tip-item::before{{content:"• ";color:#c4845a;font-weight:700;}}

/* ── Meta badge ── */
.meta-badge{{
  display:inline-flex;align-items:center;
  font-size:.63rem;padding:3px 12px;border-radius:11px;margin-right:4px;
  font-weight:500;
}}

/* ── Animations ── */
@keyframes drift{{0%,100%{{transform:translateY(0) rotate(-1deg);}}50%{{transform:translateY(-3px) rotate(1deg);}}}}
@keyframes glow{{0%,100%{{box-shadow:0 4px 16px rgba(196,132,90,.45);}}50%{{box-shadow:0 6px 24px rgba(196,132,90,.7);}}}}
@keyframes fadeIn{{from{{opacity:0;}}to{{opacity:1;}}}}
@keyframes slideUp{{from{{transform:translateY(40px);opacity:0;}}to{{transform:translateY(0);opacity:1;}}}}
@keyframes spin{{to{{transform:rotate(360deg);}}}}
.spinner{{width:38px;height:38px;border:3px solid rgba(196,132,90,.2);
          border-top-color:#c4845a;border-radius:50%;
          animation:spin .85s linear infinite;margin:0 auto 14px;}}

/* ── Section title ── */
.sec-title{{font-size:.58rem;letter-spacing:2px;text-transform:uppercase;
            color:#7a6e64;font-weight:700;margin-bottom:10px;}}
</style>
</head>
<body>

<!-- NÚT MỞ LỊCH TRÌNH -->
<button id="btn-{uid}" onclick="openModal_{uid}()">
  {btn_label}
  <span class="bdg-{uid}" id="bdg-{uid}">{day_badge}</span>
</button>

<!-- OVERLAY + MODAL (portal ra ngoài body) -->
<div id="ov-{uid}" onclick="bgClick_{uid}(event)">
  <div id="sh-{uid}" onclick="event.stopPropagation()">

    <!-- Header -->
    <div id="hdr-{uid}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
        <div style="flex:1;min-width:0;">
          <div style="font-size:.54rem;letter-spacing:2.5px;text-transform:uppercase;
                      color:rgba(255,255,255,.4);margin-bottom:8px;">{modal_sub}</div>
          <div id="htl-{uid}" style="font-family:'Cormorant Garamond',Georgia,serif;
                font-size:1.5rem;font-weight:300;color:white;line-height:1.2;
                letter-spacing:-.3px;">
            🗺 {destination}
          </div>
        </div>
        <button class="close-btn-{uid}" onclick="closeModal_{uid}()" title="{close_lbl}">✕</button>
      </div>
      <!-- Meta info row -->
      <div id="hmt-{uid}" style="display:flex;gap:5px;flex-wrap:wrap;margin-top:13px;"></div>
    </div>

    <!-- Body -->
    <div id="bdy-{uid}">

      <!-- Loading skeleton -->
      <div id="ld-{uid}">
        <div style="text-align:center;padding:30px 16px 20px;">
          <div class="spinner"></div>
          <div style="font-size:.83rem;color:#7a6e64;font-style:italic;">{loading_text}</div>
        </div>
        {skel}
      </div>

      <!-- Content -->
      <div id="ct-{uid}" style="display:none;animation:fadeIn .3s ease;"></div>

      <!-- Error -->
      <div id="er-{uid}" style="display:none;text-align:center;padding:40px 16px;">
        <div style="font-size:2rem;margin-bottom:10px;">😔</div>
        <div style="font-size:.84rem;color:#7a6e64;margin-bottom:18px;">{error_text}</div>
        <button onclick="doFetch_{uid}()" style="background:linear-gradient(135deg,#c4845a,#a06030);
          color:white;border:none;border-radius:20px;padding:9px 24px;
          font-size:.8rem;font-weight:700;cursor:pointer;font-family:inherit;">
          {retry_lbl}
        </button>
      </div>

    </div>
  </div>
</div>

<script>
(function() {{
  var loaded_{uid} = false;
  var fetching_{uid} = false;
  var idata_{uid} = null;

  window.openModal_{uid} = function() {{
    var ov = document.getElementById('ov-{uid}');
    if (!ov) return;
    // Đưa overlay ra document.body để tránh bị clip bởi iframe
    if (ov.parentNode !== document.body) {{
      document.body.appendChild(ov);
    }}
    ov.classList.add('open');
    document.body.style.overflow = 'hidden';
    if (!loaded_{uid} && !fetching_{uid}) doFetch_{uid}();
  }};

  window.closeModal_{uid} = function() {{
    var ov = document.getElementById('ov-{uid}');
    if (ov) ov.classList.remove('open');
    document.body.style.overflow = '';
  }};

  window.bgClick_{uid} = function(e) {{
    if (e.target === document.getElementById('ov-{uid}')) closeModal_{uid}();
  }};

  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeModal_{uid}();
  }});

  window.doFetch_{uid} = function() {{
    if (fetching_{uid}) return;
    fetching_{uid} = true;
    showEl_{uid}('ld');
    hideEl_{uid}('ct');
    hideEl_{uid}('er');

    fetch('https://api.anthropic.com/v1/messages', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{
        model: 'claude-sonnet-4-20250514',
        max_tokens: 2000,
        messages: [{{role: 'user', content: `{prompt_js}`}}]
      }})
    }})
    .then(function(r) {{ return r.json(); }})
    .then(function(d) {{
      fetching_{uid} = false;
      var raw = (d.content && d.content[0] && d.content[0].text) ? d.content[0].text : '';
      raw = raw.replace(/```json\s*/gi, '').replace(/```\s*/g, '').trim();
      var m = raw.match(/\{{[\s\S]*\}}/);
      if (!m) throw new Error('Không tìm thấy JSON');
      idata_{uid} = JSON.parse(m[0]);
      loaded_{uid} = true;
      renderModal_{uid}(idata_{uid});
    }})
    .catch(function(err) {{
      fetching_{uid} = false;
      hideEl_{uid}('ld');
      showEl_{uid}('er', 'flex');
      console.error('[Aria itinerary]', err);
    }});
  }};

  window.renderModal_{uid} = function(d) {{
    // Cập nhật tiêu đề
    var htl = document.getElementById('htl-{uid}');
    if (htl) htl.textContent = (d.emoji || '') + (d.emoji ? ' ' : '') + (d.title || '{dest_js}');

    // Cập nhật badge ngày
    var bdg = document.getElementById('bdg-{uid}');
    if (bdg && d.days) bdg.textContent = d.days.length + ' {"ngày" if is_vi else "days"}';

    // Meta badges
    var hmt = document.getElementById('hmt-{uid}');
    if (hmt) {{
      var mb = '';
      if (d.duration) mb += metaBadge_{uid}('⏱ ' + d.duration, 'rgba(255,255,255,.12)', 'rgba(255,255,255,.85)');
      if (d.best_time) mb += metaBadge_{uid}('🌤 ' + d.best_time, 'rgba(255,255,255,.12)', 'rgba(255,255,255,.85)');
      if (d.budget) mb += metaBadge_{uid}('💰 ' + d.budget, 'rgba(184,150,90,.3)', '#f5d98a');
      hmt.innerHTML = mb;
    }}

    var h = '';

    // Highlights
    if (d.highlights && d.highlights.length) {{
      h += '<div style="margin-bottom:20px;">';
      h += '<div class="sec-title">{highlights_lbl}</div>';
      h += '<div style="display:flex;flex-wrap:wrap;gap:4px;">';
      d.highlights.forEach(function(x) {{ h += '<span class="pill">' + esc_{uid}(x) + '</span>'; }});
      h += '</div></div>';
    }}

    // Tabs ngày
    if (d.days && d.days.length) {{
      h += '<div class="sec-title" style="margin-bottom:10px;">{itinerary_lbl}</div>';
      h += '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;">';
      d.days.forEach(function(day, i) {{
        var ac = (i === 0) ? ' active' : '';
        var st = (i === 0) ? 'background:' + (day.color || '#c4845a') + ';color:white;border-color:transparent;' : '';
        h += '<button class="tab-{uid}' + ac + '" id="tab-{uid}-' + i + '"'
           + ' onclick="switchDay_{uid}(' + i + ')"'
           + ' style="' + st + '">'
           + esc_{uid}(day.day || '') + (day.theme ? ' — ' + esc_{uid}(day.theme) : '')
           + '</button>';
      }});
      h += '</div>';

      // Panels ngày
      d.days.forEach(function(day, i) {{
        h += '<div id="pan-{uid}-' + i + '" style="display:' + (i === 0 ? 'flex' : 'none') + ';flex-direction:column;gap:0;">';
        (day.slots || []).forEach(function(s) {{
          h += '<div class="slot-{uid}">'
             + '<div style="min-width:46px;font-size:.68rem;font-weight:700;'
             +   'color:' + (day.color || '#c4845a') + ';flex-shrink:0;padding-top:2px;">'
             + esc_{uid}(s.time || '') + '</div>'
             + '<div style="font-size:1.15rem;flex-shrink:0;line-height:1;">' + esc_{uid}(s.emoji || '•') + '</div>'
             + '<div style="flex:1;min-width:0;">'
             + '<div style="font-size:.84rem;font-weight:600;color:#1a3a3a;margin-bottom:3px;line-height:1.3;">' + esc_{uid}(s.name || '') + '</div>'
             + '<div style="font-size:.72rem;color:#7a6e64;line-height:1.5;">' + esc_{uid}(s.tip || '') + '</div>'
             + '</div></div>';
        }});
        h += '</div>';
      }});
    }}

    // Tips
    if (d.tips && d.tips.length) {{
      h += '<div style="margin-top:20px;background:linear-gradient(135deg,rgba(26,58,58,.04),rgba(184,150,90,.04));'
         + 'border:1px solid rgba(184,150,90,.22);border-radius:14px;padding:16px 18px;">';
      h += '<div class="sec-title" style="color:#b8965a;margin-bottom:10px;">{tips_lbl}</div>';
      d.tips.forEach(function(t) {{
        h += '<div class="tip-item">' + esc_{uid}(t) + '</div>';
      }});
      h += '</div>';
    }}

    document.getElementById('ct-{uid}').innerHTML = h;
    hideEl_{uid}('ld');
    showEl_{uid}('ct', 'block');
  }};

  window.switchDay_{uid} = function(idx) {{
    if (!idata_{uid} || !idata_{uid}.days) return;
    idata_{uid}.days.forEach(function(day, i) {{
      var tb = document.getElementById('tab-{uid}-' + i);
      var pn = document.getElementById('pan-{uid}-' + i);
      if (!tb || !pn) return;
      if (i === idx) {{
        tb.classList.add('active');
        tb.style.background = day.color || '#c4845a';
        tb.style.color = 'white';
        tb.style.borderColor = 'transparent';
        pn.style.display = 'flex';
      }} else {{
        tb.classList.remove('active');
        tb.style.background = '';
        tb.style.color = '';
        tb.style.borderColor = '';
        pn.style.display = 'none';
      }}
    }});
  }};

  // Helpers
  function showEl_{uid}(id, display) {{
    var el = document.getElementById(id + '-{uid}') || document.getElementById(id);
    if (el) el.style.display = display || 'block';
  }}
  function hideEl_{uid}(id) {{
    var el = document.getElementById(id + '-{uid}') || document.getElementById(id);
    if (el) el.style.display = 'none';
  }}
  function esc_{uid}(s) {{
    if (s == null) return '';
    return String(s)
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;');
  }}
  function metaBadge_{uid}(text, bg, color) {{
    return '<span class="meta-badge" style="background:' + bg + ';color:' + color + ';">' + text + '</span>';
  }}

}})();
</script>
</body>
</html>"""

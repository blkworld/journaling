import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="Candlestick Designer Pro", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="column"] { display: flex; flex-direction: column; align-items: center; }
    .stButton>button { width: 100%; border-radius: 4px; }
    /* Highlight untuk candle yang dipilih */
    .selected-candle { stroke-width: 3; stroke-dasharray: 5; stroke: #ffffff !important; filter: drop-shadow(0 0 5px rgba(255,255,255,0.5)); }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Interactive Candlestick Designer")
st.caption("Gunakan tombol navigasi di bawah gambar untuk memilih candle yang ingin diedit.")

# --- SESSION STATE ---
if 'candles' not in st.session_state:
    st.session_state.candles = []
if 'selected_idx' not in st.session_state:
    st.session_state.selected_idx = -1

# --- SIDEBAR: EDIT PANEL ---
with st.sidebar:
    st.header("✨ Control Panel")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Bullish"):
            st.session_state.candles.append({
                'type': 'bull', 'body': 50, 'top_wick': 15, 'bot_wick': 15,
                'color': '#2ecc71', 'wick_color': '#2ecc71', 'border_color': '#27ae60', 'radius': 2
            })
            st.session_state.selected_idx = len(st.session_state.candles) - 1
    with col2:
        if st.button("➕ Bearish"):
            st.session_state.candles.append({
                'type': 'bear', 'body': 50, 'top_wick': 15, 'bot_wick': 15,
                'color': '#e74c3c', 'wick_color': '#e74c3c', 'border_color': '#c0392b', 'radius': 2
            })
            st.session_state.selected_idx = len(st.session_state.candles) - 1
            
    if st.button("🗑️ Reset Canvas"):
        st.session_state.candles = []
        st.session_state.selected_idx = -1
        st.rerun()

    st.divider()
    
    if st.session_state.selected_idx != -1:
        idx = st.session_state.selected_idx
        st.subheader(f"🛠️ Editing Candle {idx + 1}")
        
        # Dimensi
        st.session_state.candles[idx]['body'] = st.slider("Body Height", 1, 300, st.session_state.candles[idx]['body'])
        st.session_state.candles[idx]['top_wick'] = st.slider("Top Wick", 0, 150, st.session_state.candles[idx]['top_wick'])
        st.session_state.candles[idx]['bot_wick'] = st.slider("Bottom Wick", 0, 150, st.session_state.candles[idx]['bot_wick'])
        st.session_state.candles[idx]['radius'] = st.slider("Rounded Corners", 0, 15, st.session_state.candles[idx]['radius'])
        
        # Warna
        c1, c2, c3 = st.columns(3)
        with c1: st.session_state.candles[idx]['color'] = st.color_picker("Body", st.session_state.candles[idx]['color'])
        with c2: st.session_state.candles[idx]['wick_color'] = st.color_picker("Wick", st.session_state.candles[idx]['wick_color'])
        with c3: st.session_state.candles[idx]['border_color'] = st.color_picker("Border", st.session_state.candles[idx]['border_color'])

        if st.button("❌ Delete This Candle", type="secondary"):
            st.session_state.candles.pop(idx)
            st.session_state.selected_idx = max(0, idx - 1) if st.session_state.candles else -1
            st.rerun()

# --- CALCULATION & RENDER ---
def render_canvas(candles):
    if not candles: return None, 400, 400, 0
    
    data_points = []
    current_x, prev_close_y, calc_data = 30, 0, []
    
    for i, c in enumerate(candles):
        open_y = prev_close_y
        if c['type'] == 'bull':
            close_y = open_y - c['body']
            high_y = close_y - c['top_wick']
            low_y = open_y + c['bot_wick']
        else:
            close_y = open_y + c['body']
            high_y = open_y - c['top_wick']
            low_y = close_y + c['bot_wick']
        
        prev_close_y = close_y
        calc_data.append({'x': current_x, 'open': open_y, 'close': close_y, 'high': high_y, 'low': low_y, 'idx': i, **c})
        data_points.extend([high_y, low_y])
        current_x += 70

    min_y, max_y = min(data_points) - 60, max(data_points) + 60
    height = max_y - min_y
    width = current_x + 20
    
    svg_header = f'<svg width="100%" height="{height}" viewBox="0 {min_y} {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#1a1c23; border-radius:12px;">'
    svg_content = ""
    
    for c in calc_data:
        sel_class = "class='selected-candle'" if c['idx'] == st.session_state.selected_idx else ""
        y_rect = min(c['open'], c['close'])
        h_rect = abs(c['open'] - c['close'])
        
        svg_content += f'<line x1="{c["x"] + 20}" y1="{c["high"]}" x2="{c["x"] + 20}" y2="{c["low"]}" stroke="{c["wick_color"]}" stroke-width="2.5" />'
        svg_content += f'<rect x="{c["x"]}" y="{y_rect}" width="40" height="{h_rect}" fill="{c["color"]}" stroke="{c["border_color"]}" stroke-width="2" rx="{c["radius"]}" {sel_class} />'
        
    return svg_header + svg_content + "</svg>", width, height, min_y

# --- MAIN DISPLAY ---
if st.session_state.candles:
    svg_code, canvas_w, canvas_h, min_y = render_canvas(st.session_state.candles)
    
    # Preview
    st.write("### Live Preview")
    st.components.v1.html(svg_code, height=canvas_h + 20)
    
    # INTERACTIVE CLICK SELECTION (Menggunakan Barisan Tombol di bawah Canvas)
    st.write("🎯 **Klik nomor di bawah untuk memilih candle:**")
    cols = st.columns(len(st.session_state.candles) if len(st.session_state.candles) < 15 else 15)
    
    for i in range(len(st.session_state.candles)):
        col_idx = i % 15
        with cols[col_idx]:
            # Jika dipilih, tombol jadi warna biru (primary)
            btn_type = "primary" if st.session_state.selected_idx == i else "secondary"
            if st.button(f"{i+1}", key=f"select_{i}", type=btn_type):
                st.session_state.selected_idx = i
                st.rerun()
    
    st.divider()
    st.download_button("📥 Export SVG", svg_code, "candlestick_pro.svg", "image/svg+xml")
else:
    st.info("Canvas kosong. Tambahkan candle melalui sidebar untuk memulai.")

st.caption("Tips: Candle yang dipilih akan memiliki garis putih putus-putus dan bercahaya.")

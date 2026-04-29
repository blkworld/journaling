import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="Candlestick Designer Pro", layout="wide", page_icon="📈")

# CSS untuk memastikan efek visual "Selected" muncul dengan jelas
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .selected-candle { 
        stroke: #ffffff !important; 
        stroke-width: 4px !important; 
        stroke-dasharray: 6;
        filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.8));
    }
    .stButton>button { border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Global Candlestick Designer")

# --- SESSION STATE ---
if 'candles' not in st.session_state:
    st.session_state.candles = []
if 'selected_idx' not in st.session_state:
    st.session_state.selected_idx = -1

# --- SIDEBAR: GLOBAL SETTINGS ---
with st.sidebar:
    st.header("🎨 Global Theme")
    
    # 1. Global Rounded Corners
    global_radius = st.slider("Global Rounded Corners", 0, 20, 2)
    
    st.divider()
    
    # 2. Global Colors
    st.subheader("Bullish Color Scheme")
    bull_body = st.color_picker("Bull Body", "#2ecc71")
    bull_wick = st.color_picker("Bull Wick & Border", "#27ae60")
    
    st.subheader("Bearish Color Scheme")
    bear_body = st.color_picker("Bear Body", "#e74c3c")
    bear_wick = st.color_picker("Bear Wick & Border", "#c0392b")

    st.divider()
    st.header("➕ Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Bullish"):
            st.session_state.candles.append({'type': 'bull', 'body': 50, 'top_wick': 15, 'bot_wick': 15})
            st.session_state.selected_idx = len(st.session_state.candles) - 1
    with col2:
        if st.button("➕ Bearish"):
            st.session_state.candles.append({'type': 'bear', 'body': 50, 'top_wick': 15, 'bot_wick': 15})
            st.session_state.selected_idx = len(st.session_state.candles) - 1
            
    if st.button("🗑️ Reset Canvas", type="secondary"):
        st.session_state.candles = []
        st.session_state.selected_idx = -1
        st.rerun()

# --- SELECTED CANDLE ADJUSTMENT (SIDEBAR) ---
if st.session_state.selected_idx != -1:
    with st.sidebar:
        st.divider()
        idx = st.session_state.selected_idx
        st.subheader(f"📏 Adjust Candle {idx + 1}")
        st.session_state.candles[idx]['body'] = st.slider("Body Height", 1, 300, st.session_state.candles[idx]['body'])
        st.session_state.candles[idx]['top_wick'] = st.slider("Top Wick", 0, 150, st.session_state.candles[idx]['top_wick'])
        st.session_state.candles[idx]['bot_wick'] = st.slider("Bottom Wick", 0, 150, st.session_state.candles[idx]['bot_wick'])
        
        if st.button("❌ Delete Selected"):
            st.session_state.candles.pop(idx)
            st.session_state.selected_idx = max(0, idx - 1) if st.session_state.candles else -1
            st.rerun()

# --- ENGINE ---
def render_svg(candles, bull_c, bull_w, bear_c, bear_w, radius, selected_idx):
    if not candles: return None, 400, 400, 0
    
    data_points = []
    current_x, prev_close_y, calc_data = 30, 0, []
    
    for i, c in enumerate(candles):
        open_y = prev_close_y
        if c['type'] == 'bull':
            close_y = open_y - c['body']
            high_y = close_y - c['top_wick']
            low_y = open_y + c['bot_wick']
            color, wick_color = bull_c, bull_w
        else:
            close_y = open_y + c['body']
            high_y = open_y - c['top_wick']
            low_y = close_y + c['bot_wick']
            color, wick_color = bear_c, bear_w
        
        prev_close_y = close_y
        calc_data.append({
            'x': current_x, 'open': open_y, 'close': close_y, 'high': high_y, 'low': low_y, 
            'idx': i, 'color': color, 'wick_color': wick_color
        })
        data_points.extend([high_y, low_y])
        current_x += 70

    min_y, max_y = min(data_points) - 60, max(data_points) + 60
    height, width = max_y - min_y, current_x + 20
    
    svg_header = f'<svg width="100%" height="{height}" viewBox="0 {min_y} {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#1a1c23; border-radius:12px;">'
    svg_content = ""
    
    for c in calc_data:
        sel_attr = "class='selected-candle'" if c['idx'] == selected_idx else ""
        y_rect = min(c['open'], c['close'])
        h_rect = abs(c['open'] - c['close'])
        
        # Wick
        svg_content += f'<line x1="{c["x"] + 20}" y1="{c["high"]}" x2="{c["x"] + 20}" y2="{c["low"]}" stroke="{c["wick_color"]}" stroke-width="3" />'
        # Body
        svg_content += f'<rect x="{c["x"]}" y="{y_rect}" width="40" height="{h_rect}" fill="{c["color"]}" stroke="{c["wick_color"]}" stroke-width="1.5" rx="{radius}" {sel_attr} />'
        
    return svg_header + svg_content + "</svg>", width, height

# --- MAIN DISPLAY ---
if st.session_state.candles:
    svg_code, canvas_w, canvas_h = render_svg(
        st.session_state.candles, bull_body, bull_wick, bear_body, bear_wick, global_radius, st.session_state.selected_idx
    )
    
    st.components.v1.html(svg_code, height=canvas_h + 20)
    
    # CLICK SELECTION (Tombol di bawah)
    st.write("🎯 **Pilih Candle untuk diatur posisinya:**")
    cols = st.columns(min(len(st.session_state.candles), 12))
    for i in range(len(st.session_state.candles)):
        with cols[i % 12]:
            if st.button(f"{i+1}", key=f"btn_{i}", type="primary" if st.session_state.selected_idx == i else "secondary"):
                st.session_state.selected_idx = i
                st.rerun()
    
    st.divider()
    st.download_button("📥 Export SVG", svg_code, "candlestick_pro.svg", "image/svg+xml")
else:
    st.info("Tambahkan candle di sidebar.")

import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="Candlestick Designer Pro", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 4px; }
    /* Styling untuk candle yang dipilih */
    .selected-candle { stroke: #ffffff; stroke-width: 2; stroke-dasharray: 4; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Candlestick SVG Designer Pro")
st.caption("Klik candle pada preview untuk memilih, atau gunakan tombol di sidebar.")

# --- SESSION STATE ---
if 'candles' not in st.session_state:
    st.session_state.candles = []
if 'selected_idx' not in st.session_state:
    st.session_state.selected_idx = -1

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.header("🛠️ Canvas & Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Bullish"):
            st.session_state.candles.append({'type': 'bull', 'body': 40, 'top_wick': 15, 'bot_wick': 15})
            st.session_state.selected_idx = len(st.session_state.candles) - 1
    with col2:
        if st.button("➕ Bearish"):
            st.session_state.candles.append({'type': 'bear', 'body': 40, 'top_wick': 15, 'bot_wick': 15})
            st.session_state.selected_idx = len(st.session_state.candles) - 1
            
    if st.button("🗑️ Clear All"):
        st.session_state.candles = []
        st.session_state.selected_idx = -1
        st.rerun()

    st.divider()
    
    # Selection Manager
    if st.session_state.candles:
        st.subheader("Selection")
        options = [f"Candle {i+1} ({c['type'].upper()})" for i, c in enumerate(st.session_state.candles)]
        # Sinkronisasi index
        selected_option = st.selectbox("Pilih Candle untuk Diedit:", options, index=st.session_state.selected_idx)
        st.session_state.selected_idx = options.index(selected_option)
        
        # Adjust Properties
        idx = st.session_state.selected_idx
        st.subheader(f"Adjusting Candle {idx + 1}")
        st.session_state.candles[idx]['body'] = st.slider("Body Height", 1, 250, st.session_state.candles[idx]['body'], key=f"body_{idx}")
        st.session_state.candles[idx]['top_wick'] = st.slider("Top Wick", 0, 150, st.session_state.candles[idx]['top_wick'], key=f"top_{idx}")
        st.session_state.candles[idx]['bot_wick'] = st.slider("Bottom Wick", 0, 150, st.session_state.candles[idx]['bot_wick'], key=f"bot_{idx}")
        
        if st.button("❌ Delete Selected"):
            st.session_state.candles.pop(idx)
            st.session_state.selected_idx = max(0, idx - 1) if st.session_state.candles else -1
            st.rerun()

# --- DYNAMIC CALCULATION ENGINE ---
def calculate_dimensions(candles):
    """Menghitung bounding box dinamis agar gambar tidak terpotong."""
    if not candles:
        return 400, 400, 200, []

    data_points = []
    current_x = 50
    prev_close_y = 0  # Starting point internal
    
    calculated_candles = []
    
    for i, c in enumerate(candles):
        if c['type'] == 'bull':
            open_y = prev_close_y
            close_y = open_y - c['body']
            high_y = close_y - c['top_wick']
            low_y = open_y + c['bot_wick']
        else:
            open_y = prev_close_y
            close_y = open_y + c['body']
            high_y = open_y - c['top_wick']
            low_y = close_y + c['bot_wick']
        
        prev_close_y = close_y
        
        candle_data = {
            'x': current_x, 'open': open_y, 'close': close_y, 
            'high': high_y, 'low': low_y, 'type': c['type'], 'idx': i
        }
        calculated_candles.append(candle_data)
        data_points.extend([high_y, low_y])
        current_x += 60

    # Tentukan Margin dan Viewbox
    min_y = min(data_points) - 50
    max_y = max(data_points) + 50
    total_height = max_y - min_y
    total_width = current_x + 20
    
    return total_width, total_height, min_y, calculated_candles

# --- RENDER SVG ---
if st.session_state.candles:
    width, height, min_y, calc_data = calculate_dimensions(st.session_state.candles)
    
    svg_header = f'<svg width="100%" height="{height}" viewBox="0 {min_y} {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#1a1c23; border-radius:8px;">'
    svg_body = ""
    
    for c in calc_data:
        color = "#2ecc71" if c['type'] == 'bull' else "#e74c3c"
        # Highlight if selected
        is_selected = "stroke='#ffffff' stroke-width='2' stroke-dasharray='4'" if c['idx'] == st.session_state.selected_idx else ""
        
        # Wick
        svg_body += f'<line x1="{c["x"] + 15}" y1="{c["high"]}" x2="{c["x"] + 15}" y2="{c["low"]}" stroke="{color}" stroke-width="2" />'
        # Body
        y_rect = min(c['open'], c['close'])
        h_rect = abs(c['open'] - c['close'])
        svg_body += f'<rect x="{c["x"]}" y="{y_rect}" width="30" height="{h_rect}" fill="{color}" rx="2" {is_selected} />'
        
    final_svg = svg_header + svg_body + "</svg>"
    
    # Preview
    st.write("### Live Preview (Auto-Resizing)")
    st.components.v1.html(final_svg, height=height + 50)
    
    # Export
    st.download_button(label="📥 Export as SVG", data=final_svg, file_name="dynamic_candles.svg", mime="image/svg+xml")
else:
    st.info("Tambahkan candle untuk melihat preview.")

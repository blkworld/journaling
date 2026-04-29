import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="Candlestick Generator", layout="wide", page_icon="📈")

# Style ala Notion/Dark Mode
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Candlestick SVG Generator")
st.caption("Buat ilustrasi candlestick custom untuk edukasi atau desain.")

# --- SESSION STATE ---
if 'candles' not in st.session_state:
    st.session_state.candles = []

# --- SIDEBAR: INPUT CONTROL ---
with st.sidebar:
    st.header("🛠️ Candle Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Bullish", help="Add Green Candle"):
            st.session_state.candles.append({'type': 'bull', 'body': 40, 'top_wick': 10, 'bot_wick': 10})
    with col2:
        if st.button("➕ Bearish", help="Add Red Candle"):
            st.session_state.candles.append({'type': 'bear', 'body': 40, 'top_wick': 10, 'bot_wick': 10})
            
    if st.button("🗑️ Clear All", type="secondary"):
        st.session_state.candles = []
        st.rerun()

    st.divider()
    
    # Edit Last Candle
    if st.session_state.candles:
        st.subheader("Adjust Last Candle")
        idx = len(st.session_state.candles) - 1
        st.session_state.candles[idx]['body'] = st.slider("Body Height", 5, 200, st.session_state.candles[idx]['body'])
        st.session_state.candles[idx]['top_wick'] = st.slider("Top Wick", 0, 100, st.session_state.candles[idx]['top_wick'])
        st.session_state.candles[idx]['bot_wick'] = st.slider("Bottom Wick", 0, 100, st.session_state.candles[idx]['bot_wick'])

# --- RENDER LOGIC (SVG) ---
def generate_svg(candles):
    width = len(candles) * 60 + 40
    height = 400
    base_y = height / 2
    
    svg_header = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#1a1c23; border-radius:8px;">'
    svg_body = ""
    
    current_x = 30
    prev_close_y = base_y
    
    for c in candles:
        # Tentukan posisi Y berdasarkan tipe candle (otomatis menyambung OHLC sederhana)
        color = "#2ecc71" if c['type'] == 'bull' else "#e74c3c"
        
        if c['type'] == 'bull':
            open_y = prev_close_y
            close_y = open_y - c['body']
            high_y = close_y - c['top_wick']
            low_y = open_y + c['bot_wick']
            prev_close_y = close_y # Close candle ini jadi Open candle depan
        else:
            open_y = prev_close_y
            close_y = open_y + c['body']
            high_y = open_y - c['top_wick']
            low_y = close_y + c['bot_wick']
            prev_close_y = close_y

        # Wick (Sumbu)
        svg_body += f'<line x1="{current_x + 15}" y1="{high_y}" x2="{current_x + 15}" y2="{low_y}" stroke="{color}" stroke-width="2" />'
        # Body
        y_rect = min(open_y, close_y)
        h_rect = abs(open_y - close_y)
        svg_body += f'<rect x="{current_x}" y="{y_rect}" width="30" height="{h_rect}" fill="{color}" rx="2" />'
        
        current_x += 50 # Jarak antar candle

    return svg_header + svg_body + "</svg>"

# --- DISPLAY ---
if st.session_state.candles:
    svg_code = generate_svg(st.session_state.candles)
    
    # Preview
    st.write("### Preview")
    st.components.v1.html(svg_code, height=450)
    
    # Export
    st.download_button(
        label="📥 Export as SVG",
        data=svg_code,
        file_name="candlestick_design.svg",
        mime="image/svg+xml"
    )
else:
    st.info("Klik tombol di sidebar untuk mulai membuat candlestick.")

st.divider()
st.caption("Tips: Gunakan slider di sidebar untuk mengatur tinggi body dan wick candle terakhir yang kamu buat.")

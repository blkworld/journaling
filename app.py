# --- SIMPAN CODE LOGIC KAMU DI ATAS (apply_blend & add_watermark) ---

# --- STREAMLIT UI CUSTOM DESIGN ---
st.set_page_config(page_title="Watermark App", layout="wide")

# CSS untuk membuat Floating UI di sebelah kanan
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    [data-testid="stSidebar"] { display: none; } /* Sembunyikan sidebar bawaan */
    
    /* Container untuk Floating Panel */
    .floating-panel {
        position: fixed;
        top: 80px;
        right: 40px;
        width: 350px;
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        z-index: 1000;
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 Watermark App")

# Layout utama: Gambar di kiri, Controls di kanan
col_img, col_ctrl = st.columns([0.7, 0.3])

with col_ctrl:
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    st.subheader("Controls")
    
    mode = st.radio("Type", ["Text", "Image"], horizontal=True)
    
    if mode == "Text":
        content = st.text_input("Text", "Mike Briggs")
    else:
        content = st.file_uploader("Logo", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    
    blend_mode = st.selectbox("Blend Mode", ["Normal", "Multiply", "Screen", "Overlay", "Difference"])
    size = st.slider("Size", 10, 1000, 200)
    opacity = st.slider("Opacity", 0.0, 1.0, 0.5)
    angle = st.slider("Rotation", 0, 360, 45)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_img:
    uploaded_file = st.file_uploader("Upload Main Photo", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        # Jalankan fungsi add_watermark kamu
        result = add_watermark(img, mode, content, opacity, angle, size, blend_mode)
        
        # Display Result
        st.image(result, use_container_width=True)
        
        # Download Button di bawah gambar
        buf = io.BytesIO()
        result.save(buf, format="JPEG", quality=95)
        st.download_button("💾 WATERMARK IMAGES", buf.getvalue(), "watermarked.jpg", "image/jpeg", use_container_width=True)
    else:
        # Placeholder jika belum ada gambar
        st.info("Please upload an image to start")

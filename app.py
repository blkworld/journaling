import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np

def add_watermark(base_image, watermark_type, watermark_content, opacity, angle, size):
    # Convert image to RGBA
    base = base_image.convert("RGBA")
    txt_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    
    draw = ImageDraw.Draw(txt_layer)
    width, height = base.size
    
    # Hitung jarak antar watermark (tiling)
    step = int(max(width, height) / 4) 

    if watermark_type == "Text":
        # Load font (default)
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except:
            font = ImageFont.load_default()
            
        # Warna dengan opacity
        fill_color = (255, 255, 255, int(255 * opacity))
        
        # Tiling logic untuk Text
        for x in range(0, width + step, step):
            for y in range(0, height + step, step):
                # Buat temporary image untuk rotasi tiap teks
                item_txt = Image.new("RGBA", (size * len(watermark_content), size * 2), (255, 255, 255, 0))
                item_draw = ImageDraw.Draw(item_txt)
                item_draw.text((0, 0), watermark_content, font=font, fill=fill_color)
                item_rotated = item_txt.rotate(angle, expand=1)
                txt_layer.paste(item_rotated, (x, y), item_rotated)

    else: # Image Watermark
        if watermark_content is not None:
            mark = Image.open(watermark_content).convert("RGBA")
            
            # Atur ukuran logo
            aspect_ratio = mark.width / mark.height
            mark = mark.resize((size, int(size / aspect_ratio)))
            
            # Atur opacity logo
            alpha = mark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            mark.putalpha(alpha)
            
            # Tiling logic untuk Image
            for x in range(0, width + step, step):
                for y in range(0, height + step, step):
                    item_rotated = mark.rotate(angle, expand=1)
                    txt_layer.paste(item_rotated, (x, y), item_rotated)

    return Image.alpha_composite(base, txt_layer).convert("RGB")

# --- UI STREAMLIT ---
st.set_page_config(page_title="Watermarker No Ribet", layout="wide")
st.title("📸 Watermarker No Ribet Club")

with st.sidebar:
    st.header("Pengaturan")
    mode = st.radio("Pilih Tipe Watermark:", ["Text", "Image"])
    
    if mode == "Text":
        content = st.text_input("Isi Teks:", "CONTOH WATERMARK")
    else:
        content = st.file_uploader("Upload Logo (PNG direkomendasikan):", type=['png', 'jpg', 'jpeg'])
    
    opacity = st.slider("Opacity:", 0.1, 1.0, 0.3)
    angle = st.slider("Rotasi (Derajat):", 0, 360, 45)
    size = st.slider("Ukuran:", 10, 500, 50)

uploaded_file = st.file_uploader("Upload Foto yang mau di-watermark:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    img = Image.open(uploaded_file)
    result = add_watermark(img, mode, content, opacity, angle, size)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Foto Asli", use_container_width=True)
    with col2:
        st.image(result, caption="Hasil Watermark", use_container_width=True)
        
        # Tombol Download
        import io
        buf = io.BytesIO()
        result.save(buf, format="JPEG")
        st.download_button("Download Hasil", buf.getvalue(), "watermarked_image.jpg", "image/jpeg")

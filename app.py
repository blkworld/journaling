import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
import io

def apply_blend(base, watermark_layer, mode, global_opacity):
    base_rgb = base.convert("RGB")
    
    # Create a neutral background for blending math
    w_rgb = Image.new("RGB", base.size, (255, 255, 255))
    w_rgb.paste(watermark_layer.convert("RGB"), mask=watermark_layer.split()[3])
    
    if mode == "Normal":
        blended_rgb = watermark_layer.convert("RGB")
    elif mode == "Multiply":
        blended_rgb = ImageChops.multiply(base_rgb, w_rgb)
    elif mode == "Screen":
        w_rgb_screen = Image.new("RGB", base.size, (0, 0, 0))
        w_rgb_screen.paste(watermark_layer.convert("RGB"), mask=watermark_layer.split()[3])
        blended_rgb = ImageChops.screen(base_rgb, w_rgb_screen)
    elif mode == "Overlay":
        blended_rgb = Image.blend(base_rgb, ImageChops.soft_light(base_rgb, w_rgb), 0.7)
    elif mode == "Difference":
        blended_rgb = ImageChops.difference(base_rgb, w_rgb)
    else:
        blended_rgb = watermark_layer.convert("RGB")

    mask = watermark_layer.split()[3]
    if global_opacity < 1.0:
        mask = ImageEnhance.Brightness(mask).enhance(global_opacity)
    
    return Image.composite(blended_rgb.convert("RGBA"), base, mask)

def add_watermark(base_image, watermark_type, watermark_content, opacity, angle, size, blend_mode):
    base = base_image.convert("RGBA")
    width, height = base.size
    watermark_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    
    step = int(max(width, height) / 4) 

    if watermark_type == "Text":
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except:
            font = ImageFont.load_default()
        
        fill_color = (255, 255, 255, 255)
        for x in range(0, width + step, step):
            for y in range(0, height + step, step):
                item_txt = Image.new("RGBA", (size * len(watermark_content), size * 2), (0, 0, 0, 0))
                item_draw = ImageDraw.Draw(item_txt)
                item_draw.text((0, 0), watermark_content, font=font, fill=fill_color)
                item_rotated = item_txt.rotate(angle, expand=1)
                watermark_layer.paste(item_rotated, (x, y), item_rotated)
    else:
        if watermark_content is not None:
            mark = Image.open(watermark_content).convert("RGBA")
            aspect_ratio = mark.width / mark.height
            mark = mark.resize((size, int(size / aspect_ratio)))
            for x in range(0, width + step, step):
                for y in range(0, height + step, step):
                    item_rotated = mark.rotate(angle, expand=1)
                    watermark_layer.paste(item_rotated, (x, y), item_rotated)

    return apply_blend(base, watermark_layer, blend_mode, opacity).convert("RGB")

# --- STREAMLIT UI ---
st.set_page_config(page_title="Watermarker Pro", layout="wide")
st.title("📸 Professional Watermarker")

with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.radio("Watermark Type:", ["Text", "Image"])
    
    if mode == "Text":
        content = st.text_input("Enter Text:", "CONFIDENTIAL")
    else:
        content = st.file_uploader("Upload Logo:", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    blend_mode = st.selectbox("Blend Mode:", ["Normal", "Multiply", "Screen", "Overlay", "Difference"])
    
    opacity = st.slider("Opacity:", 0.0, 1.0, 0.5)
    angle = st.slider("Rotation:", 0, 360, 45)
    size = st.slider("Size:", 10, 1000, 200)
    
    preview_quality = st.select_slider("Preview Speed", options=["Fast (Low Res)", "Normal", "High Quality"], value="Fast (Low Res)")

uploaded_file = st.file_uploader("Upload Main Photo:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    raw_img = Image.open(uploaded_file)
    w, h = raw_img.size
    
    # Calculate preview scale
    if preview_quality == "Fast (Low Res)":
        preview_scale = 800 / max(w, h)
    elif preview_quality == "Normal":
        preview_scale = 1500 / max(w, h)
    else:
        preview_scale = 1.0
        
    if preview_scale < 1.0:
        preview_img = raw_img.resize((int(w * preview_scale), int(h * preview_scale)))
    else:
        preview_img = raw_img

    # Render preview
    result_preview = add_watermark(preview_img, mode, content, opacity, angle, int(size * preview_scale), blend_mode)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(raw_img, caption="Original", use_container_width=True)
    with col2:
        st.image(result_preview, caption=f"Fast Preview ({blend_mode})", use_container_width=True)
        
        if st.button("🚀 Prepare High-Res Download"):
            with st.spinner("Processing full resolution image..."):
                full_res_result = add_watermark(raw_img, mode, content, opacity, angle, size, blend_mode)
                buf = io.BytesIO()
                full_res_result.save(buf, format="JPEG", quality=95)
                st.download_button("💾 Download Full Resolution", buf.getvalue(), "watermarked_full.jpg", "image/jpeg")

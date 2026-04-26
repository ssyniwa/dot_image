import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import io

st.set_page_config(page_title="RPGドット絵メーカー v2", layout="centered")

st.title("🎮 RPG風ドット絵コンバーター")
st.write("輪郭を強調し、より特徴が際立つドット絵に変換します。")

# --- 設定パラメータ ---
st.sidebar.header("微調整")
pixel_size = st.sidebar.slider("ドットの大きさ", 4, 32, 12, 2)
color_count = st.sidebar.slider("色数", 2, 32, 12, 2)
sharpness = st.sidebar.slider("くっきり感", 1.0, 5.0, 2.0, 0.5)
contrast = st.sidebar.slider("コントラスト", 1.0, 2.0, 1.3, 0.1)

uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert("RGB")
    
    # --- 前処理：特徴を際立たせる ---
    # 1. 輪郭を強調（エッジ強調）
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    
    # 2. シャープネスを上げる
    enhancer_s = ImageEnhance.Sharpness(img)
    img = enhancer_s.enhance(sharpness)
    
    # 3. コントラストを上げる（色が混ざるのを防ぐ）
    enhancer_c = ImageEnhance.Contrast(img)
    img = enhancer_c.enhance(contrast)

    # --- ドット絵処理 ---
    # 小さくリサイズ（この際、あえて粗いリサイズを使う）
    small_size = (img.width // pixel_size, img.height // pixel_size)
    img_small = img.resize(small_size, resample=Image.BILINEAR)
    
    # 減色（RPG風のパレットに近づける）
    img_pixel = img_small.convert("P", palette=Image.ADAPTIVE, colors=color_count)
    
    # 最終拡大（ドットを維持するためNEAREST）
    img_result = img_pixel.resize(img.size, resample=Image.NEAREST).convert("RGB")

    # 表示
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("元の画像")
        st.image(uploaded_file, use_container_width=True)
    with col2:
        st.subheader("ドット絵")
        st.image(img_result, use_container_width=True)

    # ダウンロード用
    buf = io.BytesIO()
    img_result.save(buf, format="PNG")
    st.download_button("画像を保存", buf.getvalue(), "rpg_dot.png", "image/png")
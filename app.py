import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import io
import numpy as np

st.set_page_config(page_title="RPG Dot Maker Premium", layout="centered")

st.title("💎 RPG風ドット絵コンバーター Premium")

# --- サイドバー設定 ---
st.sidebar.header("✨ プレミアムエフェクト")
enable_scanlines = st.sidebar.checkbox("走査線エフェクト (CRT風)", value=True)
vignette_intensity = st.sidebar.slider("ヴィネット (四隅の影)", 0.0, 1.0, 0.4)
bloom_intensity = st.sidebar.slider("発光 (ブルーム)", 0.0, 2.0, 0.5)

st.sidebar.header("🎨 スタイル・基本調整")
mode = st.sidebar.selectbox("カラープリセット", ["通常", "ゴールド", "サイバーパンク", "ゲームボーイ", "セピア"])
pixel_size = st.sidebar.slider("ドットの大きさ", 4, 32, 12, 2)
add_outline = st.sidebar.checkbox("黒い縁取り", value=True)

# --- 特殊エフェクト関数 ---
def apply_premium_effects(img, bloom, vignette, scanlines):
    # 1. ブルーム（光があふれる感じ）
    if bloom > 0:
        mask = img.filter(ImageFilter.GaussianBlur(radius=2))
        img = ImageEnhance.Brightness(img).enhance(1.0)
        img = Image.blend(img, mask, bloom * 0.3)

    # 2. ヴィネット（四隅を暗くして中央を強調）
    if vignette > 0:
        width, height = img.size
        # グラデーションマスク作成
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([-width*vignette, -height*vignette, width*(1+vignette), height*(1+vignette)], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=width/4))
        black = Image.new("RGB", (width, height), (0, 0, 0))
        img = Image.composite(img, black, mask)

    # 3. 走査線（レトロなテレビ感）
    if scanlines:
        draw = ImageDraw.Draw(img)
        for y in range(0, img.height, 4):
            draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, 100), width=1)
    
    return img

def apply_preset_color(img, mode):
    img = img.convert("L")
    if mode == "ゴールド":
        return ImageOps.colorize(img, black="#3e2723", mid="#d4af37", white="#fff8e1")
    elif mode == "サイバーパンク":
        return ImageOps.colorize(img, black="#000033", mid="#ff00ff", white="#00ffff")
    elif mode == "ゲームボーイ":
        return ImageOps.colorize(img, black="#0f380f", white="#9bbc0f")
    elif mode == "セピア":
        return ImageOps.colorize(img, black="#3e2723", white="#d7ccc8")
    return img.convert("RGB")

# --- メインロジック ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert("RGB")
    
    # 前処理：カラープリセット
    if mode != "通常":
        img = apply_preset_color(img, mode)
    
    img = ImageEnhance.Contrast(img).enhance(1.4)

    # ドット化
    small_size = (img.width // pixel_size, img.height // pixel_size)
    img_small = img.resize(small_size, resample=Image.BILINEAR)
    
    # 縁取り
    if add_outline:
        edge = img_small.filter(ImageFilter.FIND_EDGES).convert("L")
        img_small.paste((0, 0, 0), mask=edge)
    
    # 拡大
    img_result = img_small.resize(img.size, resample=Image.NEAREST).convert("RGB")
    
    # プレミアムエフェクト適用（拡大後に行うのがコツ）
    img_result = apply_premium_effects(img_result, bloom_intensity, vignette_intensity, enable_scanlines)

    st.image(img_result, use_container_width=True)

    # ダウンロード
    buf = io.BytesIO()
    img_result.save(buf, format="PNG")
    st.download_button("💎 プレミアムドット絵を保存", buf.getvalue(), "premium_dot.png")
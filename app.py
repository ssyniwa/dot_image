import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import io

st.set_page_config(page_title="RPG Dot Maker Ultra", layout="centered")

st.title("💎 RPG風ドット絵コンバーター Ultra")

# --- サイドバー設定 ---
st.sidebar.header("✨ プレミアムエフェクト")
enable_scanlines = st.sidebar.checkbox("走査線エフェクト", value=True)
vignette_intensity = st.sidebar.slider("ヴィネット", 0.0, 1.0, 0.4)

st.sidebar.header("🎨 カラー＆ドット調整")
pixel_size = st.sidebar.slider("ドットの大きさ", 4, 32, 12)
# 色数調整の感度を良くするため、より細かく設定
color_count = st.sidebar.select_slider(
    "色数の制限",
    options=[2, 4, 8, 16, 32, 64, 128],
    value=16
)
mode = st.sidebar.selectbox("カラープリセット", ["通常", "ゴールド", "サイバーパンク", "ゲームボーイ"])

# --- 補助関数：パレットの取得 ---
def get_palette(img, num_colors):
    # 画像から使われている主な色を抽出
    paletted_img = img.convert("P", palette=Image.ADAPTIVE, colors=num_colors)
    palette = paletted_img.getpalette()[:num_colors*3]
    colors = [palette[i:i+3] for i in range(0, len(palette), 3)]
    return colors

# --- メインロジック ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert("RGB")
    
    # 1. カラープリセット適用
    if mode == "ゴールド":
        img = ImageOps.colorize(img.convert("L"), black="#3e2723", mid="#d4af37", white="#fff8e1")
    elif mode == "サイバーパンク":
        img = ImageOps.colorize(img.convert("L"), black="#000033", mid="#ff00ff", white="#00ffff")
    elif mode == "ゲームボーイ":
        img = ImageOps.colorize(img.convert("L"), black="#0f380f", white="#9bbc0f")
    
    # 2. ドット化（リサイズ）
    small_size = (max(1, img.width // pixel_size), max(1, img.height // pixel_size))
    img_small = img.resize(small_size, resample=Image.BILINEAR)
    
    # 3. 減色処理（ここが色数調整の肝）
    # ユーザーが指定した色数に最適化
    img_pixel = img_small.convert("P", palette=Image.ADAPTIVE, colors=color_count)
    
    # パレット情報を取得（表示用）
    current_colors = get_palette(img_small, color_count)
    
    # 4. 拡大とエフェクト
    img_result = img_pixel.resize(img.size, resample=Image.NEAREST).convert("RGB")
    
    # 5. エフェクト適用（走査線・ヴィネット）
    if enable_scanlines:
        draw = ImageDraw.Draw(img_result)
        for y in range(0, img_result.height, 4):
            draw.line([(0, y), (img_result.width, y)], fill=(0, 0, 0, 80))
            
    if vignette_intensity > 0:
        # 簡易ヴィネット
        v_mask = Image.new("L", img_result.size, 0)
        v_draw = ImageDraw.Draw(v_mask)
        v_draw.ellipse([-img_result.width*vignette_intensity, -img_result.height*vignette_intensity, 
                        img_result.width*(1+vignette_intensity), img_result.height*(1+vignette_intensity)], fill=255)
        v_mask = v_mask.filter(ImageFilter.GaussianBlur(radius=img_result.width/4))
        img_result = Image.composite(img_result, Image.new("RGB", img_result.size, (0,0,0)), v_mask)

    # --- 画面表示 ---
    st.image(img_result, caption=f"現在の設定: {color_count}色 / {pixel_size}pxドット", use_container_width=True)
    
    # 使用カラーパレットの表示（プレミアム機能！）
    st.write("### 使用されているカラーパレット")
    cp_cols = st.columns(min(len(current_colors), 16))
    for i, color in enumerate(current_colors):
        with cp_cols[i % 16]:
            st.color_picker(f"Color {i+1}", f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}", key=f"cp_{i}", disabled=True)

    # ダウンロード
    buf = io.BytesIO()
    img_result.save(buf, format="PNG")
    st.download_button("💎 この作品をエクスポート", buf.getvalue(), "premium_art.png")
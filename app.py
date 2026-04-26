import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io

st.set_page_config(page_title="RPGドット絵メーカー Pro", layout="centered")

st.title("🎮 RPG風ドット絵コンバーター Pro")

# --- サイドバー設定 ---
st.sidebar.header("1. スタイル設定")
mode = st.sidebar.selectbox(
    "カラーフィルター",
    ["通常", "ゲームボーイ風 (緑)", "セピア調", "モノクロ"]
)

add_outline = st.sidebar.checkbox("黒い縁取りを追加", value=True)

st.sidebar.header("2. ドット調整")
pixel_size = st.sidebar.slider("ドットの大きさ", 4, 32, 12, 2)
color_count = st.sidebar.slider("色数", 2, 32, 8, 2)

# --- 画像処理関数 ---
def apply_color_filter(img, mode):
    if mode == "ゲームボーイ風 (緑)":
        # 緑色のグラデーションマップを適用（簡易版）
        img = img.convert("L")
        img = ImageOps.colorize(img, black="#0f380f", white="#9bbc0f")
    elif mode == "セピア調":
        img = img.convert("L")
        img = ImageOps.colorize(img, black="#3e2723", white="#d7ccc8")
    elif mode == "モノクロ":
        img = img.convert("L")
    return img.convert("RGB")

def apply_outline(img):
    # 輪郭を抽出して少し太くし、元の画像に重ねる
    edge = img.filter(ImageFilter.FIND_EDGES).convert("L")
    edge = edge.point(lambda x: 255 if x > 50 else 0) # 閾値処理
    # 輪郭部分を黒く塗りつぶすためのマスクとして使用
    inv_edge = ImageOps.invert(edge)
    img.paste((0, 0, 0), mask=edge)
    return img

# --- メイン処理 ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert("RGB")
    
    # 1. フィルター適用
    img = apply_color_filter(img, mode)
    
    # 2. コントラストとシャープネスの自動強化
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Sharpness(img).enhance(2.0)

    # 3. ドット化
    small_size = (img.width // pixel_size, img.height // pixel_size)
    img_small = img.resize(small_size, resample=Image.BILINEAR)
    
    # 4. 縁取り（小さいサイズの状態で行うとドット感が出る）
    if add_outline:
        img_small = apply_outline(img_small)
    
    # 5. 減色
    img_pixel = img_small.convert("P", palette=Image.ADAPTIVE, colors=color_count)
    
    # 6. 拡大
    img_result = img_pixel.resize(img.size, resample=Image.NEAREST).convert("RGB")

    # 表示
    st.image(img_result, caption=f"モード: {mode}", use_container_width=True)

    # ダウンロード
    buf = io.BytesIO()
    img_result.save(buf, format="PNG")
    st.download_button("このドット絵を保存", buf.getvalue(), "rpg_style.png", "image/png")
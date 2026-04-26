import streamlit as st
from PIL import Image
import io

# --- ページ設定 ---
st.set_page_config(page_title="RPGドット絵メーカー", layout="centered")

st.title("🎮 RPG風ドット絵コンバーター")
st.write("写真をアップロードするだけで、レトロゲーム風のドット絵に変換します。")

# --- サイドバーの設定（パラメータ調整） ---
st.sidebar.header("設定")
pixel_size = st.sidebar.slider("ドットの粗さ", min_value=4, max_value=32, value=16, step=2)
color_count = st.sidebar.slider("色の数", min_value=2, max_value=32, value=8, step=2)

# --- 画像アップロード ---
uploaded_file = st.file_uploader("画像を選択してください...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 画像を開く
    img = Image.open(uploaded_file)
    
    # レイアウト作成（ビフォー・アフター）
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元の画像")
        st.image(img, use_container_width=True)

    # --- ドット絵処理 ---
    # 1. 小さくリサイズ（ドット化の核）
    small_size = (img.width // pixel_size, img.height // pixel_size)
    img_small = img.resize(small_size, resample=Image.BILINEAR)
    
    # 2. 減色処理
    img_pixel = img_small.convert("P", palette=Image.ADAPTIVE, colors=color_count)
    
    # 3. 元のサイズに戻す（カクカクさせるためにNEARESTを使用）
    img_result = img_pixel.resize(img.size, resample=Image.NEAREST).convert("RGB")

    with col2:
        st.subheader("ドット絵風")
        st.image(img_result, use_container_width=True)

    # --- ダウンロードボタン ---
    buf = io.BytesIO()
    img_result.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="ドット絵を保存する",
        data=byte_im,
        file_name="dot_art.png",
        mime="image/png"
    )

else:
    st.info("画像をアップロードしてください。")
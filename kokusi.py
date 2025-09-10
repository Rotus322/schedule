import streamlit as st
import base64

# ------------------------
# 背景設定関数
# ------------------------
def set_background(background_file):
    with open(background_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;       /* 画面全体にフィット */
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------------
# 背景設定
# ------------------------
set_background("mori.jpg")

# ------------------------
# 文字色を白に
# ------------------------
st.markdown(
    """
    <style>
    * {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------
# キャラ表示（経験値の上）
# ------------------------
display_image = "tamago_char.png"
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.image(display_image, width=100)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------
# 卵の表示（後で座標で動かせるようにdivでラップ）
# ------------------------
egg_image = "tamago_egg.png"
egg_top = 200   # 卵の上位置(px)
egg_left = 100  # 卵の左位置(px)

st.markdown(
    f"""
    <div style='position:absolute; top:{egg_top}px; left:{egg_left}px; width:100px;'>
        <img src='{egg_image}' width='100px'>
    </div>
    """,
    unsafe_allow_html=True
)

# ここから下に勉強ボタンや経験値表示などを配置
st.write("ここに経験値やボタンを置く")

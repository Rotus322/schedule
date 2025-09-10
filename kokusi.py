import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import base64

# ----------------------
# 背景＋卵表示関数
# ----------------------
def display_background_and_egg(background_file, egg_file, egg_pos=(50, 50)):
    with open(background_file, "rb") as f:
        bg_encoded = base64.b64encode(f.read()).decode()
    with open(egg_file, "rb") as f:
        egg_encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .background {{
        position: relative;
        width: 100%;
        height: 60vh;  /* 背景エリアの高さ */
        background-image: url("data:image/jpeg;base64,{bg_encoded}");
        background-size: cover;
        background-position: center;
    }}
    .egg {{
        position: absolute;
        top: {egg_pos[0]}%;
        left: {egg_pos[1]}%;
        transform: translate(-50%, -50%);
        width: 150px;
    }}
    </style>
    <div class="background">
        <img class="egg" src="data:image/png;base64,{egg_encoded}">
    </div>
    """, unsafe_allow_html=True)

# ----------------------
# 設定
# ----------------------
EXP_PER_PRESS = 10
EXP_PER_LEVEL = 150

# ----------------------
# データ用のダミー
# ----------------------
tot_exp = 170
lvl = tot_exp // EXP_PER_LEVEL + 1
exp_in_lvl = tot_exp % EXP_PER_LEVEL

# ----------------------
# UI
# ----------------------
st.set_page_config(page_title="国試成長記録", page_icon="📒")
st.title("♡きゅらちゃん育成アプリ♡")
st.write("勉強終わったらボタンを押してキャラを育てよう！")

# 背景＋卵表示
display_background_and_egg("mori.jpg", "tamago.png", egg_pos=(60, 30))

# キャラクター画像（文字の上に表示）
emoji_map = {
    1:"tamago.png",
    2:"sa.jpg",
    3:"youtien.png",
    4:"syougaku.png",
    5:"tyuugaku.png",
    6:"koukou.png",
    7:"daigaku.png",
    8:"juken.png",
    9:"kngosi.png"
}
display_image = emoji_map.get(min(lvl, max(emoji_map.keys())), "default_char.png")

st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.image(display_image, width=100)  # 経験値表示の上あたりに
st.markdown("</div>", unsafe_allow_html=True)

# 文字表示
st.write(f"レベル: **Lv {lvl}**")
st.progress(exp_in_lvl / EXP_PER_LEVEL)
st.write(f"経験値: **{exp_in_lvl} / {EXP_PER_LEVEL}** (累計 {tot_exp} EXP)")

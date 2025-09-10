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
def display_background_with_egg(background_file, egg_file, egg_pos=(50, 80)):
    """
    background_file: 背景画像
    egg_file: 卵画像
    egg_pos: 卵の位置 (top%, left%)
    """
    # 背景
    with open(background_file, "rb") as f:
        bg_data = f.read()
    bg_encoded = base64.b64encode(bg_data).decode()

    # 卵
    with open(egg_file, "rb") as f:
        egg_data = f.read()
    egg_encoded = base64.b64encode(egg_data).decode()

    st.markdown(
        f"""
        <style>
        .background {{
            position: relative;
            width: 100%;
            height: 400px;  /* 高さは自由に変更可 */
            background-image: url("data:image/png;base64,{bg_encoded}");
            background-size: cover;
            background-position: center;
        }}
        .egg {{
            position: absolute;
            top: {egg_pos[0]}%;
            left: {egg_pos[1]}%;
            transform: translate(-50%, -50%);
            width: 80px;
        }}
        </style>
        <div class="background">
            <img class="egg" src="data:image/png;base64,{egg_encoded}">
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------------
# キャラ表示関数
# ----------------------
def display_character(character_file):
    with open(character_file, "rb") as f:
        char_data = f.read()
    char_encoded = base64.b64encode(char_data).decode()

    st.markdown(
        f"""
        <div style='text-align:center; margin-top:20px;'>
            <img src="data:image/png;base64,{char_encoded}" width="150">
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------------
# サンプルUI
# ----------------------
st.title("♡きゅらちゃん育成アプリ♡")

# 背景＋卵
display_background_with_egg("mori.jpg", "tamago.png", egg_pos=(60, 30))  # 卵位置は自由

# キャラ画像
display_character("sa.jpg")  # レベルに応じて切り替え可能

# サンプルテキスト（文字色白）
st.markdown(
    """
    <style>
    * { color: white !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# サンプルボタン
if st.button("✅ 今日の勉強終わった！"):
    st.success("経験値 +10！")

if st.button("❌ 勉強終わらなかった…"):
    st.warning("今日は勉強終わらなかった…😢")

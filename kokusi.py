import streamlit as st
import pandas as pd
import datetime
import base64

# ----------------------
# 背景設定（ページ全体）
# ----------------------
def set_page_background(background_file):
    with open(background_file, "rb") as f:
        bg_data = f.read()
    bg_encoded = base64.b64encode(bg_data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        * {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ----------------------
# 卵表示（ページ上に絶対配置）
# ----------------------
def display_egg(egg_file, top=60, left=30, width=80):
    with open(egg_file, "rb") as f:
        egg_data = f.read()
    egg_encoded = base64.b64encode(egg_data).decode()

    st.markdown(
        f"""
        <div style="
            position: absolute;
            top: {top}%;
            left: {left}%;
            transform: translate(-50%, -50%);
            width: {width}px;
            z-index:1;
        ">
            <img src="data:image/png;base64,{egg_encoded}">
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------------
# キャラ表示（経験値の上）
# ----------------------
def display_character(character_file, width=150):
    with open(character_file, "rb") as f:
        char_data = f.read()
    char_encoded = base64.b64encode(char_data).decode()

    st.markdown(
        f"""
        <div style='text-align:center; margin-top:20px; z-index:2;'>
            <img src="data:image/png;base64,{char_encoded}" width="{width}">
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------------
# 設定
# ----------------------
EXP_PER_PRESS = 10
EXP_PER_LEVEL = 150

# ----------------------
# ページ全体背景
# ----------------------
set_page_background("mori.jpg")

# 卵表示（位置はあとで変更可能）
display_egg("tamago.png", top=60, left=30)

# サンプルキャラ
display_character("sa.png")

# UI
st.title("♡きゅらちゃん育成アプリ♡")
st.write("勉強終わったらボタンを押してキャラを育てよう！")

if st.button("✅ 今日の勉強終わった！"):
    st.success(f"経験値 +{EXP_PER_PRESS}！")

if st.button("❌ 勉強終わらなかった…"):
    st.warning("今日は勉強終わらなかった…😢")

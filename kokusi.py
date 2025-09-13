import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import base64
import pytz
import os

# =============================
# 設定
# =============================
JST = pytz.timezone("Asia/Tokyo")
EXP_PER_LEVEL = 150
SPREADSHEET_NAME = "study_log"
STUDY_SHEET = "log"
BOSS_SHEET = "boss_log"

# 国試日
exam_date = JST.localize(datetime.datetime(2026, 2, 15, 0, 0))
now = datetime.datetime.now(JST)
days_left = (exam_date - now).days

# ボス設定
BOSS_LIST = [
    {"name": "黒狼🐺",   "hp": 1000, "image": "kokurou.png"},
    {"name": "ドラゴン🐉", "hp": 1500, "image": "doragon.png"},
    {"name": "にわとりボス", "hp": 2000, "image": "niwatori.png"},
]
FRIEND_IMAGES = ["kurosiba.png", "dora.png", "friend3.png"]  # 仲間

# =============================
# Google Sheets 接続
# =============================
def connect_sheet(sheet_name):
    try:
        creds_json = st.secrets["gcp_service_account"]
        creds_dict = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open(SPREADSHEET_NAME).worksheet(sheet_name)
    except Exception as e:
        st.error(f"Google Sheet 接続失敗: {e}")
        return None

# =============================
# 学習ログ
# =============================
def load_study_log():
    sheet = connect_sheet(STUDY_SHEET)
    if sheet is None:
        return pd.DataFrame(columns=["date","exp","note"])
    try:
        df = pd.DataFrame(sheet.get_all_records())
        if df.empty: return pd.DataFrame(columns=["date","exp","note"])
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["exp"] = pd.to_numeric(df["exp"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"学習ログ読み込み失敗: {e}")
        return pd.DataFrame(columns=["date","exp","note"])

def append_study(exp, note=""):
    sheet = connect_sheet(STUDY_SHEET)
    if sheet is None: return
    now = datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    try:
        sheet.append_row([now, exp, note])
    except Exception as e:
        st.error(f"学習ログ書き込み失敗: {e}")

def total_exp(df): return int(df["exp"].sum()) if not df.empty else 0
def current_level(exp): return exp // EXP_PER_LEVEL + 1
def exp_in_level(exp): return exp % EXP_PER_LEVEL

# =============================
# ボス戦ログ
# =============================
def load_boss_log():
    sheet = connect_sheet(BOSS_SHEET)
    if sheet is None:
        return pd.DataFrame(columns=["date","mock_name","score","damage","total_damage"])
    try:
        df = pd.DataFrame(sheet.get_all_records())
        if df.empty: return pd.DataFrame(columns=["date","mock_name","score","damage","total_damage"])
        return df
    except Exception as e:
        st.error(f"ボスログ読み込み失敗: {e}")
        return pd.DataFrame(columns=["date","mock_name","score","damage","total_damage"])

def append_boss(mock_name, score, damage, total_damage):
    sheet = connect_sheet(BOSS_SHEET)
    if sheet is None: return
    now = datetime.datetime.now(JST).strftime("%Y-%m-%d")
    try:
        sheet.append_row([now, mock_name, int(score), int(damage), int(total_damage)])
    except Exception as e:
        st.error(f"ボスログ書き込み失敗: {e}")

# =============================
# 画像ユーティリティ
# =============================
def encode_image(path):
    if not os.path.exists(path): return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(bg_file, egg_file, egg_size="200px"):
    bg_b64 = encode_image(bg_file)
    egg_b64 = encode_image(egg_file)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{egg_b64}"),
                              url("data:image/jpeg;base64,{bg_b64}");
            background-repeat: no-repeat, no-repeat;
            background-position: 55% 80%, center;
            background-size: {egg_size}, cover;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

# =============================
# キャラクター進化
# =============================
def get_character_image(level):
    mapping = {
        1:"tamago.png", 2:"sa.png", 3:"youtien.png",
        4:"syougaku.png",5:"tyuugaku.png",6:"koukou.png",
        7:"daigaku.png",8:"juken.png",9:"kngosi.png"
    }
    return mapping.get(min(level, max(mapping)), "tamago.png")

def show_character(level):
    img_b64 = encode_image(get_character_image(level))
    st.markdown(
        f"<div style='text-align:center;'><img src='data:image/png;base64,{img_b64}' width='180'></div>",
        unsafe_allow_html=True
    )

# =============================
# ページ設定
# =============================
st.set_page_config(page_title="国試×ボス戦 成長記録", page_icon="⚔️")

# フォント
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Chokokutai&display=swap');
    .title {font-family:'Chokokutai', cursive; font-size:48px; text-align:center;}
    .countdown {font-size:32px; color:#FF69B4; text-align:center;}
    .stTextInput input, .stNumberInput input {color:black !important; background:white !important;}
    .stTextInput label, .stNumberInput label {color:black !important;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>💛⚔ さーきゅらクエスト ⚔💛</div>", unsafe_allow_html=True)
st.markdown(f"<div class='countdown'>🏥 国試まであと {days_left} 日</div>", unsafe_allow_html=True)

# =============================
# 学習成長パート
# =============================
study_df = load_study_log()
tot_exp = total_exp(study_df)
lvl = current_level(tot_exp)
exp_lvl = exp_in_level(tot_exp)

# 背景セット
set_background("mori.jpg", get_character_image(lvl))
show_character(lvl)

st.write("### ✅ 経験値獲得")
if st.button("今日の勉強終わった！"):
    append_study(10, "勉強終わった")
    st.experimental_rerun()
if st.button("ゼミ頑張った！(+15)"):
    append_study(15, "ゼミ")
    st.experimental_rerun()
if st.button("バイト頑張った！(+5)"):
    append_study(5, "バイト")
    st.experimental_rerun()

st.progress(exp_lvl/EXP_PER_LEVEL)
st.write(f"レベル: **Lv {lvl}**  経験値: {exp_lvl}/{EXP_PER_LEVEL}  (累計 {tot_exp})")

# =============================
# ボス戦パート
# =============================
st.markdown("---")
st.markdown("<div class='title'>⚔️ 模試ボス戦 ⚔️</div>", unsafe_allow_html=True)

boss_df = load_boss_log()
total_damage = int(boss_df["damage"].sum()) if not boss_df.empty else 0

# どのボスか
remaining = total_damage
boss_idx = 0
for i,b in enumerate(BOSS_LIST):
    if remaining < b["hp"]:
        boss_idx = i
        break
    remaining -= b["hp"]
else:
    boss_idx = len(BOSS_LIST)-1
    remaining = BOSS_LIST[-1]["hp"]

current_boss = BOSS_LIST[boss_idx]
current_hp = max(current_boss["hp"] - remaining, 0)
cleared = boss_idx  # 倒した数

# 仲間表示
if cleared>0:
    friend_html = "".join(
        f"<img src='data:image/png;base64,{encode_image(img)}' width='120' style='margin:5px;'>"
        for img in FRIEND_IMAGES[:cleared]
    )
    st.markdown(f"<h4>🎉 仲間たち 🎉</h4><div>{friend_html}</div>", unsafe_allow_html=True)

# ボス表示
boss_img = encode_image(current_boss["image"])
st.markdown(f"""
<div style='text-align:center;'>
    <h3>💥 現在のボス: {current_boss["name"]}</h3>
    <img src='data:image/png;base64,{boss_img}' width='350'>
</div>
""", unsafe_allow_html=True)
st.progress(current_hp/current_boss["hp"])
st.write(f"HP: {current_hp} / {current_boss['hp']} 　累計ダメージ: {total_damage}")

# 模試入力
mock = st.text_input("模試名（例：9月模試）")
score = st.number_input("模試点数", min_value=0, max_value=300, step=1)
if st.button("ダメージを与える！"):
    if mock and score>0:
        damage = int(score*2)
        append_boss(mock, score, damage, total_damage + damage)
        st.success(f"{mock} に {damage} ダメージを与えた！🔥")
        st.experimental_rerun()
    else:
        st.warning("模試名と点数を入力してください")

# 履歴
st.markdown("### 📝 模試履歴")
if boss_df.empty:
    st.write("まだ模試履歴がありません")
else:
    st.dataframe(boss_df.sort_values("date", ascending=False), use_container_width=True)

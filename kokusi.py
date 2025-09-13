import streamlit as st
import pandas as pd
import gspread
import json, base64, datetime
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone

# === JST ===
JST = timezone("Asia/Tokyo")

# === 複数ボス設定 ===
BOSS_LIST = [
    {"name": "たまごボス", "hp": 1000, "image": "tamago.png"},
    {"name": "ひよこボス", "hp": 1500, "image": "hiyoko.png"},
    {"name": "にわとりボス", "hp": 2000, "image": "niwatori.png"},
]

# === Google Sheets 接続 ===
def connect_gsheets():
    try:
        creds_json = st.secrets["gcp_service_account"]
        creds_dict = json.loads(creds_json)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("study_log").worksheet("boss_log")
        return sheet
    except Exception as e:
        st.error(f"シート接続失敗: {e}")
        return None

# === 履歴を読み込み ===
def load_mock_data():
    sheet = connect_gsheets()
    if sheet is None:
        return pd.DataFrame(columns=["date","mock_name","score","damage","total_damage"])
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            df = pd.DataFrame(columns=["date","mock_name","score","damage","total_damage"])
        return df
    except Exception as e:
        st.error(f"シート読み込み失敗: {e}")
        return pd.DataFrame(columns=["date","mock_name","score","damage","total_damage"])

# === データ追加 ===
def append_mock_result(mock_name, score, damage, total_damage):
    sheet = connect_gsheets()
    if sheet is None:
        return
    try:
        now = datetime.datetime.now(JST).strftime("%Y-%m-%d")
        sheet.append_row([now, mock_name, int(score), int(damage), int(total_damage)])
    except Exception as e:
        st.error(f"シート書き込み失敗: {e}")

# === ボス画像表示 ===
def display_boss_image(image_file, width=250):
    try:
        with open(image_file, "rb") as f:
            img_data = f.read()
        img_encoded = base64.b64encode(img_data).decode()
        st.markdown(
            f"""
            <div style='text-align:center; margin-top:20px;'>
                <img src="data:image/png;base64,{img_encoded}" width="{width}">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"ボス画像の読み込みに失敗: {e}")

# === UIタイトル ===
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Yuji+Mai&display=swap');

    .boss-title {
        font-family: 'Yuji Mai', sans-serif;
        font-size: 48px;
        text-align: center;
        margin: 20px 0;
    }
    .stTextInput input, .stNumberInput input {
        color: black !important;
        background-color: white !important;
    }
    .stTextInput label, .stNumberInput label {
        color: black !important;
    }
    </style>
    <div class="boss-title">
        ⚔️ 模試ボス戦 ⚔️
    </div>
    """,
    unsafe_allow_html=True
)

# === 現在ステータス計算 ===
df = load_mock_data()
total_damage = int(df["damage"].sum()) if not df.empty else 0

# ボスの進行状況を計算
remaining = total_damage
boss_index = 0
for i, boss in enumerate(BOSS_LIST):
    if remaining < boss["hp"]:
        boss_index = i
        break
    remaining -= boss["hp"]
else:
    boss_index = len(BOSS_LIST) - 1
    remaining = BOSS_LIST[-1]["hp"]  # 最終ボスHPを0で固定

current_boss = BOSS_LIST[boss_index]
current_hp = max(current_boss["hp"] - remaining, 0)

st.subheader(f"💥 現在のボス: {current_boss['name']}")
display_boss_image(current_boss["image"], width=250)
st.progress(current_hp / current_boss["hp"])
st.write(f"HP: **{current_hp} / {current_boss['hp']}**")
st.write(f"累計ダメージ: {total_damage}")

# === 模試入力 ===
st.markdown("---")
st.subheader("📊 模試結果入力")

mock_name = st.text_input("模試名（例：9月模試）")
score = st.number_input("模試点数", min_value=0, max_value=300, step=1)

if st.button("ダメージを与える！"):
    if mock_name and score > 0:
        damage = int(score * 2)  # スコア→ダメージ換算
        new_total = total_damage + damage
        append_mock_result(mock_name, score, damage, new_total)
        st.success(f"{mock_name} に {damage} ダメージを与えた！🔥")
        st.experimental_rerun()
    else:
        st.warning("模試名とスコアを入力してください")

# === 履歴表示 ===
st.markdown("---")
st.subheader("📝 履歴一覧")
if not df.empty:
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
else:
    st.write("まだ模試履歴がありません")

import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import base64

# ----------------------
# 設定
# ----------------------
EXP_PER_PRESS = 10
EXP_PER_LEVEL = 150

SPREADSHEET_NAME = "study_log"
SHEET_NAME = "log"

# ----------------------
# 背景＋キャラ表示関数
# ----------------------
def set_background_with_character(background_file, character_file):
    # 背景
    with open(background_file, "rb") as f:
        bg_data = f.read()
    bg_encoded = base64.b64encode(bg_data).decode()

    # キャラ
    with open(character_file, "rb") as f:
        char_data = f.read()
    char_encoded = base64.b64encode(char_data).decode()

    # 背景 + キャラ
    st.markdown(
        f"""
        <style>
        /* ページ全体の背景 */
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* キャラ画像を中央に表示 */
        .character {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 300px;
            z-index: 1;
        }}

        /* テキストはキャラより前に */
        .overlay {{
            position: relative;
            z-index: 2;
            text-align: center;
            color: white;
        }}

        /* ボタンも透明化 */
        div.stButton > button {{
            background-color: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid white;
            border-radius: 10px;
        }}
        div.stButton > button:hover {{
            background-color: rgba(255,255,255,0.4);
        }}
        </style>

        <img class="character" src="data:image/png;base64,{char_encoded}">
        """,
        unsafe_allow_html=True
    )

# 背景＋キャラ設定
set_background_with_character("mori.jpg", "tamago.png")

# ----------------------
# Google Sheets 接続
# ----------------------
def connect_gsheets():
    creds_json = st.secrets["gcp_service_account"]
    creds_dict = json.loads(creds_json)
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

def load_data():
    try:
        sheet = connect_gsheets()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        if "date" not in df.columns:
            df["date"] = pd.Timestamp.now()
        else:
            df["date"] = pd.to_datetime(df["date"])
            
        if "exp" not in df.columns:
            df["exp"] = 0
        else:
            df["exp"] = pd.to_numeric(df["exp"], errors="coerce").fillna(0).astype(int)
        
        if "note" not in df.columns:
            df["note"] = ""
        
        return df
    except Exception as e:
        st.error(f"Googleスプレッドシート読み込み失敗: {e}")
        return pd.DataFrame(columns=["date","exp","note"])

def append_entry(exp, note=""):
    try:
        sheet = connect_gsheets()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, exp, note])
        return load_data()
    except Exception as e:
        st.error(f"Googleスプレッドシート書き込み失敗: {e}")
        return load_data()

# ----------------------
# レベル計算
# ----------------------
def total_exp(df):
    return int(df["exp"].sum()) if not df.empty else 0

def current_level(total_exp_val):
    return total_exp_val // EXP_PER_LEVEL + 1

def exp_within_level(total_exp_val):
    return total_exp_val % EXP_PER_LEVEL

# ----------------------
# UI
# ----------------------
st.set_page_config(page_title="国試成長記録", page_icon="📒")
st.markdown("<h1>♡きゅらちゃん育成アプリ♡</h1>", unsafe_allow_html=True)
st.write("勉強終わったらボタンを押してキャラを育てよう！")

df = load_data()
tot_exp = total_exp(df)
lvl = current_level(tot_exp)
exp_in_lvl = exp_within_level(tot_exp)

if "last_level" not in st.session_state:
    st.session_state["last_level"] = lvl

st.write(f"レベル: **Lv {lvl}**")
st.progress(exp_in_lvl / EXP_PER_LEVEL)
st.write(f"経験値: **{exp_in_lvl} / {EXP_PER_LEVEL}** (累計 {tot_exp} EXP)")

note = st.text_input("メモ（任意）", value="", key="note_input")

# 勉強終了
if st.button("✅ 今日の勉強終わった！"):
    df = append_entry(EXP_PER_PRESS, note)
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +{EXP_PER_PRESS}！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl

# 勉強終わらなかった
if st.button("❌ 勉強終わらなかった…"):
    df = append_entry(0, "勉強終わらなかった")
    st.warning("今日は勉強終わらなかった…😢")

# 研究頑張った
if st.button("🔬 ゼミ頑張った！"):
    df = append_entry(15, "ゼミ頑張った")
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +15！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl

# 記録表示
st.subheader("記録（新しい順）")
if df.empty:
    st.write("まだ記録がありません。")
else:
    if "date" in df.columns:
        st.dataframe(df.sort_values("date", ascending=False))
    else:
        st.dataframe(df)

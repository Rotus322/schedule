import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

import base64

def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 呼び出し（背景設定）
set_background("mori.jpg")
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

st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: transparent;
        color: white;
        border: 2px solid white;  /* 好きな色や太さに変更可能 */
        border-radius: 10px;
    }
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.2);  /* ホバー時の色 */
    }
    </style>
    """,
    unsafe_allow_html=True
)
# ----------------------
# 設定
# ----------------------
EXP_PER_PRESS = 10
EXP_PER_LEVEL = 150

SPREADSHEET_NAME = "study_log"
SHEET_NAME = "log"

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
        
        # 列がなければ作る
        if "date" not in df.columns:
            df["date"] = pd.Timestamp.now()
        else:
            df["date"] = pd.to_datetime(df["date"])
            
        if "exp" not in df.columns:
            df["exp"] = 0
        else:
            # 文字列を整数に変換
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
        # 列順は date, exp, note に合わせる
        sheet.append_row([now, exp, note])
        # 追加後に再読み込みして df を返す
        df = load_data()
        return df
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
st.title("♡きゅらちゃん育成アプリ♡")
st.write("勉強終わったらボタンを押してキャラを育てよう！")

df = load_data()
tot_exp = total_exp(df)
lvl = current_level(tot_exp)
exp_in_lvl = exp_within_level(tot_exp)

# キャラ表示

emoji_map = {1:"tamago.jpg",
             2:"sa.jpg",
             3:"youtien.jpg",
             4:"syougaku.jpg",
             5:"tyuugaku.jpg",
             6:"koukou.jpg",
             7:"daigaku.jpg",
             8:"juken.jpg",
             9:"kngosi.jpg"}
display_image = emoji_map.get(min(lvl, max(emoji_map.keys())), "default.jpg")
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(display_image, width=300)
st.markdown("</div>", unsafe_allow_html=True)
st.write(f"レベル: **Lv {lvl}**")
st.progress(exp_in_lvl / EXP_PER_LEVEL)
st.write(f"経験値: **{exp_in_lvl} / {EXP_PER_LEVEL}** (累計 {tot_exp} EXP)")

if "last_level" not in st.session_state:
    st.session_state["last_level"] = lvl

# 勉強終了ボタンとメモ
st.subheader("勉強終了")
note = st.text_input("メモ（任意）", value="", key="note_input")
if st.button("✅ 今日の勉強終わった！"):
    df = append_entry(EXP_PER_PRESS, note)
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +{EXP_PER_PRESS}！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl
    st.write(df.tail())  # 最新データ確認用（削除可）

# ❌ 勉強終わらなかった
if st.button("❌ 勉強終わらなかった…"):
    df = append_entry(0, "勉強終わらなかった")
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.warning("今日は勉強終わらなかった…😢")
    st.session_state["last_level"] = new_lvl
    st.write(df.tail())  # 最新データ確認用

# 🔬 研究頑張った
if st.button("🔬 ゼミ頑張った！"):
    df = append_entry(15, "ゼミ頑張った")
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +15！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl
    st.write(df.tail())  # 最新データ確認用

# 記録表示
st.subheader("記録（新しい順）")
if df.empty:
    st.write("まだ記録がありません。")
else:
    if "date" in df.columns:
        st.dataframe(df.sort_values("date", ascending=False))
    else:
        st.dataframe(df)

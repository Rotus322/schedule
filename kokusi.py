import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import base64
import pytz


JST=pytz.timezone("Asia/Tokyo") 


# 国試の日程
exam_date = JST.localize(datetime.datetime(2026, 2, 15, 0, 0))

# 現在時刻
now = datetime.datetime.now(JST)

# 残り日数
days_left = (exam_date - now).days


# ----------------------
# 背景設定
# ----------------------
def set_page_background_with_egg(background_file, egg_file,egg_size):
    # 背景
    with open(background_file, "rb") as f:
        bg_data = f.read()
    bg_encoded = base64.b64encode(bg_data).decode()

    # 卵（レベルに応じて変化）
    with open(egg_file, "rb") as f:
        egg_data = f.read()
    egg_encoded = base64.b64encode(egg_data).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{egg_encoded}"),
                              url("data:image/jpeg;base64,{bg_encoded}");
            background-repeat: no-repeat, no-repeat;
            background-position: 55% 80%, center; /* 卵の位置と背景の位置 */
            background-size: {egg_size}, cover;         /* 卵は自動、背景は全体に */
            background-attachment: fixed;
        }}
        * {{
            color: white !important;
        }}
        div.stButton > button {{
            background-color: transparent;
            color: white;
            border: 2px solid white;
            border-radius: 10px;
        }}
        div.stButton > button:hover {{
            background-color: rgba(255, 255, 255, 0.2);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ----------------------
# キャラ表示（経験値に応じて切り替え）
# ----------------------
def get_character_image(level):
    emoji_map = {
        1: "tamago.png",
        2: "sa.png",
        3: "youtien.png",
        4: "syougaku.png",
        5: "tyuugaku.png",
        6: "koukou.png",
        7: "daigaku.png",
        8: "juken.png",
        9: "kngosi.png"
    }
    return emoji_map.get(min(level, max(emoji_map.keys())), "default.jpg")

def display_character(level, width=150):
    display_image = get_character_image(level)
    with open(display_image, "rb") as f:
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
SPREADSHEET_NAME = "study_log"
SHEET_NAME = "log"

# ----------------------
# Google Sheets 接続
# ----------------------
def connect_gsheets():
    creds_json = st.secrets["gcp_service_account"]
    creds_dict = json.loads(creds_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
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
            df["date"] = pd.Timestamp.now(tz="Asia/Tokyo")
        else:
            # UTC扱いせず、そのまま時刻にする
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if "exp" not in df.columns:
            df["exp"] = 0
        else:
            df["exp"] = pd.to_numeric(df["exp"], errors="coerce").fillna(0).astype(int)
        if "note" not in df.columns:
            df["note"] = ""
        df["date"] = df["date"].dt.strftime("%Y-%m-%d %H:%M")
        return df
    except Exception as e:
        st.error(f"Googleスプレッドシート読み込み失敗: {e}")
        return pd.DataFrame(columns=["date","exp","note"])

def append_entry(exp, note=""):
    try:
        sheet = connect_gsheets()
        now = datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, exp, note])
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
# ページ設定
# ----------------------
st.set_page_config(page_title="国試成長記録", page_icon="📒")

df = load_data()
tot_exp = total_exp(df)
lvl = current_level(tot_exp)
exp_in_lvl = exp_within_level(tot_exp)

# 背景と卵をキャラと同じ画像で設定
egg_image = get_character_image(lvl)
set_page_background_with_egg("mori.jpg", egg_image,egg_size="200px")

display_character(lvl)  # キャラを中央に表示

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Chokokutai&display=swap');

    .custom-title {
        font-family: 'Chokokutai', sans-serif;
        font-size: 48px;
        text-align: center;
        margin: 20px 0;
    }
    </style>
    <div class="custom-title">
        💛⚔さーきゅらクエスト⚔💛
    </div>
    """,
    unsafe_allow_html=True
)

st.write("終わったらボタンを押してキャラを育てよう！")

if "last_level" not in st.session_state:
    st.session_state["last_level"] = lvl
# --- ここを育成アプリのUIに追加 ---
days_left = (exam_date - now).days

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=WDXL Lubrifont JP N&display=swap');

    .countdown {{
        font-family: 'WDXL Lubrifont JP N', sans-serif;
        color: #FF69B4 !important;  /* ピンク */
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        margin: 25px 0;
    }}
    </style>
    <div class="countdown">
        🏥 国試まであと {days_left} 日
    </div>
    """,
    unsafe_allow_html=True
)
# ----------------------
# ボタン処理
# ----------------------

if st.button("✅ 今日の勉強終わった！"):
    df = append_entry(15, "勉強終わった")
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +15！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl
    display_character(new_lvl)

if st.button("❌ 勉強終わらなかった…"):
    df = append_entry(0, "勉強終わらなかった")
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.warning("今日は勉強終わらなかった…😢")
    st.session_state["last_level"] = new_lvl
    display_character(new_lvl)

if st.button("🔬 ゼミ頑張った！"):
    df = append_entry(15, "ゼミ頑張った")
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +15！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl
    display_character(new_lvl)

if st.button("🏥🍴 バイト頑張った！"):
    df = append_entry(5, "バイト頑張った")
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +5！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl
    display_character(new_lvl)

# ----------------------
# 経験値表示
# ----------------------
st.write(f"レベル: **Lv {lvl}**")
st.progress(exp_in_lvl / EXP_PER_LEVEL)
st.write(f"経験値: **{exp_in_lvl} / {EXP_PER_LEVEL}** (累計 {tot_exp} EXP)")

# ----------------------
# 記録表示
# ----------------------
st.subheader("記録（新しい順）")
if df.empty:
    st.write("まだ記録がありません。")
else:
    if "date" in df.columns:
        st.dataframe(df.sort_values("date", ascending=False))
    else:
        st.dataframe(df)

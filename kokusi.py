import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import base64

# ----------------------
# 背景＋卵＋キャラクター表示関数
# ----------------------
def display_scene(background_file, egg_file, char_file, egg_pos=(50, 50)):
    """
    background_file : 森の背景画像
    egg_file        : 卵画像
    char_file       : レベルに応じたキャラクター画像
    egg_pos         : 卵の座標 (top %, left %)
    """
    # 背景
    with open(background_file, "rb") as f:
        bg_encoded = base64.b64encode(f.read()).decode()
    # 卵
    with open(egg_file, "rb") as f:
        egg_encoded = base64.b64encode(f.read()).decode()
    # キャラクター
    with open(char_file, "rb") as f:
        char_encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .scene {{
        position: relative;
        width: 100%;
        height: 100vh;
        background-image: url("data:image/jpeg;base64,{bg_encoded}");
        background-size: cover;
        background-position: center;
    }}
    .egg {{
        position: absolute;
        top: {egg_pos[0]}%;
        left: {egg_pos[1]}%;
        transform: translate(-50%, -50%);
        width: 150px;  /* 卵のサイズ */
    }}
    .character {{
        position: absolute;
        top: {egg_pos[0]}%;
        left: {egg_pos[1]}%;
        transform: translate(-50%, -50%);
        width: 100px;  /* キャラクターサイズ */
    }}
    </style>
    <div class="scene">
        <img class="egg" src="data:image/png;base64,{egg_encoded}">
        <img class="character" src="data:image/png;base64,{char_encoded}">
    </div>
    """, unsafe_allow_html=True)


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

# 卵とキャラクターのマップ
emoji_map = {1:"tamago.png",
             2:"sa.jpg",
             3:"youtien.png",
             4:"syougaku.png",
             5:"tyuugaku.png",
             6:"koukou.png",
             7:"daigaku.png",
             8:"juken.png",
             9:"kngosi.png"}

display_image = emoji_map.get(min(lvl, max(emoji_map.keys())), "default.jpg")

# 森＋卵＋キャラ表示
display_scene("mori.jpg", "tamago.png", display_image, egg_pos=(60, 30))  # 卵を座標で動かせる

if "last_level" not in st.session_state:
    st.session_state["last_level"] = lvl

# ボタンスタイル
st.markdown("""
<style>
* { color: white !important; }
div.stButton > button {
    background-color: transparent;
    color: white;
    border: 2px solid white;
    border-radius: 10px;
}
div.stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.2);
}
div.stButton { display: flex; justify-content: center; margin: 10px auto; }
.stApp { text-align: center; }
</style>
""", unsafe_allow_html=True)

# ----------------------
# ボタン
# ----------------------
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
    st.experimental_rerun()  # レベルアップで画像更新

if st.button("❌ 勉強終わらなかった…"):
    df = append_entry(0, "勉強終わらなかった")
    st.warning("今日は勉強終わらなかった…😢")
    st.experimental_rerun()

if st.button("🔬 ゼミ頑張った！"):
    df = append_entry(15, "ゼミ頑張った")
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +15！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl
    st.experimental_rerun()

# 記録表示
st.subheader("記録（新しい順）")
if df.empty:
    st.write("まだ記録がありません。")
else:
    if "date" in df.columns:
        st.dataframe(df.sort_values("date", ascending=False))
    else:
        st.dataframe(df)

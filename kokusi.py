import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ----------------------
# 設定
# ----------------------
EXP_PER_PRESS = 10
EXP_PER_LEVEL = 100

# Google Sheets の設定
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "service_account.json"  # ダウンロードしたJSON
SPREADSHEET_NAME = "study_log"
SHEET_NAME = "log"

# ----------------------
# Google Sheets 接続
# ----------------------
def connect_gsheets():
    # Streamlit Secrets から JSON を取得
    creds_json = st.secrets["gcp_service_account"]
    creds_dict = json.loads(creds_json)
    
    # 認証
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    client = gspread.authorize(creds)
    sheet = client.open("study_log").worksheet("log")  # スプレッドシート名とタブ名
    return sheet

def load_data():
    try:
        sheet = connect_gsheets()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Googleスプレッドシート読み込み失敗: {e}")
        return pd.DataFrame(columns=["date","exp","note"])

def append_entry(exp, note=""):
    df = load_data()
    now = pd.Timestamp(datetime.datetime.now()).floor('s')
    new_entry = {"date": now.strftime("%Y-%m-%d %H:%M:%S"), "exp": exp, "note": note}
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    try:
        sheet = connect_gsheets()
        sheet.append_row(list(new_entry.values()))
    except Exception as e:
        st.error(f"Googleスプレッドシート書き込み失敗: {e}")
    return df

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
st.set_page_config(page_title="国家試験応援RPG", page_icon="🎓")
st.title("🎮 国家試験応援RPG（クラウド版）")
st.write("勉強終わったらボタンを押してキャラを育てよう！")

df = load_data()
tot_exp = total_exp(df)
lvl = current_level(tot_exp)
exp_in_lvl = exp_within_level(tot_exp)

# キャラとボタン
st.subheader("キャラ")
emoji_map = {1:"😪",2:"🙂",3:"😤",4:"🧠",5:"🩺",6:"🏆"}
display_emoji = emoji_map.get(min(lvl,max(emoji_map.keys())),"💪")
st.markdown(f"## {display_emoji}")
st.write(f"レベル: **Lv {lvl}**")
st.progress(exp_in_lvl / EXP_PER_LEVEL)
st.write(f"経験値: **{exp_in_lvl} / {EXP_PER_LEVEL}** (累計 {tot_exp} EXP)")

if "last_level" not in st.session_state:
    st.session_state["last_level"] = lvl

if st.button("✅ 今日の勉強終わった！"):
    note = st.text_input("メモ（任意）", value="", key="note_input")
    df = append_entry(EXP_PER_PRESS, note)
    tot_exp = total_exp(df)
    new_lvl = current_level(tot_exp)
    st.success(f"経験値 +{EXP_PER_PRESS}！累計 {tot_exp} EXP")
    if new_lvl > st.session_state["last_level"]:
        st.balloons()
        st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl}")
    st.session_state["last_level"] = new_lvl

# 記録表示
st.subheader("記録（新しい順）")
if df.empty:
    st.write("まだ記録がありません。")
else:
    st.dataframe(df.sort_values("date", ascending=False))

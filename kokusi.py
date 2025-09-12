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

    .quest-title {
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
    df = append_entry(10, "勉強終わった")
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


# ボス画像を表示
def display_boss_image(image_file, width=200):
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
        sheet = client.open("study_log").worksheet("boss_log")  # 任意のシート名に変更可
        return sheet
    except Exception as e:
        st.error(f"シート接続失敗: {e}")
        return None

# === データ読み込み ===
def load_mock_data():
    sheet = connect_gsheets()
    if sheet is None:
        return pd.DataFrame(columns=["date", "mock_name", "score", "damage", "boss_hp"])
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            df = pd.DataFrame(columns=["date", "mock_name", "score", "damage", "boss_hp"])
        return df
    except Exception as e:
        st.error(f"シート読み込み失敗: {e}")
        return pd.DataFrame(columns=["date", "mock_name", "score", "damage", "boss_hp"])

# === データ追加 ===
def append_mock_result(mock_name, score, boss_hp, damage):
    sheet = connect_gsheets()
    if sheet is None:
        return
    try:
        now = datetime.datetime.now(JST).strftime("%Y-%m-%d")
        # int64 → int にキャスト
        sheet.append_row([now, mock_name, int(score), int(damage), int(boss_hp)])
    except Exception as e:
        st.error(f"シート書き込み失敗: {e}")

# === アプリ本体 ===

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Yuji Mai&display=swap');

    .boss-title {
        font-family: 'Yuji Mai', sans-serif;
        font-size: 48px;
        text-align: center;
        margin: 20px 0;
    }
    </style>
    <div class="custom-title">
        ⚔️ 模試ボス戦 ⚔️
    </div>
    """,
    unsafe_allow_html=True
)

# ボス画像を表示
display_boss_image("tamago.png", width=200)

# ボスの初期HP
BOSS_MAX_HP = 1000

# 現在までの履歴を読み込み
df = load_mock_data()
total_damage = int(df["damage"].sum()) if not df.empty else 0
current_hp = max(BOSS_MAX_HP - total_damage, 0)

st.subheader("💥 現在のボスHP")
st.progress(current_hp / BOSS_MAX_HP)
st.write(f"**{current_hp} / {BOSS_MAX_HP}**")

st.markdown("---")
st.subheader("📊 模試結果入力")

st.markdown(
    """
    <style>
    /* 入力ボックス全体 */
    .stTextInput input, .stNumberInput input {
        color: black !important;        /* 文字色 */
        background-color: white !important; /* 背景（必要なら） */
    }
    /* ラベル（項目名） */
    .stTextInput label, .stNumberInput label {
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

mock_name = st.text_input("模試名（例：9月模試）")
score = st.number_input("模試点数", min_value=0, max_value=300, step=1)

if st.button("ダメージを与える！"):
    if mock_name and score > 0:
        # 点数→ダメージ換算（例：スコア ÷ 5）
        damage = int(score * 2)
        new_hp = max(current_hp - damage, 0)
        append_mock_result(mock_name, score, new_hp, damage)
        st.success(f"{mock_name} の結果を記録しました！ 💥 {damage}ダメージ")
        # 履歴とHPを再読み込み
        df = load_mock_data()
        total_damage = int(df["damage"].sum()) if not df.empty else 0
        current_hp = max(BOSS_MAX_HP - total_damage, 0)
        st.progress(current_hp / BOSS_MAX_HP)
        st.write(f"**{current_hp} / {BOSS_MAX_HP}**")
    else:
        st.warning("模試名とスコアを入力してください")

st.markdown("---")
st.subheader("📝 履歴一覧")
if not df.empty:
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
else:
    st.write("まだ模試履歴がありません")

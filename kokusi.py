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
def set_page_background_with_friend(background_file, egg_file, egg_size, friend_files):
    # 背景
    with open(background_file, "rb") as f:
        bg_encoded = base64.b64encode(f.read()).decode()

    # 卵
    with open(egg_file, "rb") as f:
        egg_encoded = base64.b64encode(f.read()).decode()

    # 仲間（リストで複数可）
    friend_images = ["kurosiba.png", "dora.png"]
    for fpath in friend_files:
        with open(fpath, "rb") as f:
            friend_images.append(f"url('data:image/png;base64,{base64.b64encode(f.read()).decode()}')")

    # CSS用に連結（卵→仲間→背景 の順で重ねる）
    layers = ", ".join([f"url('data:image/png;base64,{egg_encoded}')"] + friend_images + [f"url('data:image/jpeg;base64,{bg_encoded}')"])

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: {layers};
            background-repeat: no-repeat, repeat;
            background-position: 55% 80%, center;
            background-size: {egg_size}, {" ,".join(["auto"]*len(friend_images))}, cover;
            background-attachment: fixed;
        }}
        * {{ color: white !important; }}
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
set_page_background_with_friend("mori.jpg", egg_image,egg_size="200px",friend_files=friend_files)

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


# === ボス設定 ===
BOSS_LIST = [
    {"name": "黒狼🐺", "hp": 1000, "image": "kokurou.png"},
    {"name": "ドラゴン🐉", "hp": 1500, "image": "doragon.png"},
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

# === 画像をbase64変換 ===
def encode_image(image_file):
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

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

# ボス進行状況
remaining = total_damage
boss_index = 0
for i, boss in enumerate(BOSS_LIST):
    if remaining < boss["hp"]:
        boss_index = i
        break
    remaining -= boss["hp"]
else:
    boss_index = len(BOSS_LIST) - 1
    remaining = BOSS_LIST[-1]["hp"]

current_boss = BOSS_LIST[boss_index]
current_hp = max(current_boss["hp"] - remaining, 0)
cleared_bosses = min(boss_index, len(FRIEND_IMAGES))  # 倒した数

# === 仲間画像を背景に表示 ===
friend_bg_html = ""
for i in range(cleared_bosses):
    img_b64 = encode_image(FRIEND_IMAGES[i])
    friend_bg_html += f"""
        <img src="data:image/png;base64,{img_b64}" 
             style="width:150px; margin:10px; border-radius:20px;">
    """
if friend_bg_html:
    st.markdown(
        f"""
        <div style='text-align:center; background:rgba(255,255,255,0.3);
                    padding:20px; border-radius:15px; margin-bottom:20px;'>
            <h3>🎉 仲間たち 🎉</h3>
            {friend_bg_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# === 現在のボス ===
st.subheader(f"💥 現在のボス: {current_boss['name']}")
boss_img_b64 = encode_image(current_boss["image"])
st.markdown(
    f"""
    <div style='text-align:center; margin-top:10px;'>
        <img src="data:image/png;base64,{boss_img_b64}" width="500">
    </div>
    """,
    unsafe_allow_html=True
)
st.progress(current_hp / current_boss["hp"])
st.write(f"HP: **{current_hp} / {current_boss['hp']}**")
st.write(f"累計ダメージ: {total_damage}")

# === ボス撃破メッセージ ===
# ボスHPが0で、かつ今回の累計ダメージで初めて突破した場合
if current_hp == 0 and cleared_bosses > len(df[df["damage"]>0]["damage"])//9999:  # 簡易判定
    if cleared_bosses <= len(FRIEND_IMAGES):
        st.success(f"🎊 {BOSS_LIST[cleared_bosses-1]['name']} を倒した！仲間が増えたよ！")

# === 模試入力 ===
st.markdown("---")
st.subheader("📊 模試結果入力")

mock_name = st.text_input("模試名（例：9月模試）")
score = st.number_input("模試点数", min_value=0, max_value=300, step=1)

if st.button("ダメージを与える！"):
    if mock_name and score > 0:
        damage = int(score * 2)
        new_total = total_damage + damage
        append_mock_result(mock_name, score, damage, new_total)
        st.success(f"{mock_name} に {damage} ダメージを与えた！🔥")
        st.experimental_rerun()
    else:
        st.warning("模試名とスコアを入力してください")

cleared_bosses = min(boss_index, len(FRIEND_IMAGES))

# === 履歴表示 ===
st.markdown("---")
st.subheader("📝 履歴一覧")
if not df.empty:
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
else:
    st.write("まだ模試履歴がありません")

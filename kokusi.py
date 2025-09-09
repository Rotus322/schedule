# app.py
"""
RPG風 国家試験応援アプリ（シンプル版）
- 「今日の勉強終わった！」ボタンで経験値を追加
- 経験値はローカルCSVに保存（data.csv）
- レベル・EXPゲージ・カレンダー表示・週グラフ・ダウンロード機能付き
"""

import streamlit as st
import pandas as pd
import datetime
import os

# ----------------------
# 設定
# ----------------------
DATA_FILE = "study_log.csv"   # ローカル保存ファイル（同ディレクトリ）
EXP_PER_PRESS = 10            # ボタン1回あたりの経験値
EXP_PER_LEVEL = 100           # 1レベルに必要な経験値（シンプル: レベル = total_exp // EXP_PER_LEVEL + 1）
MAX_DAYS_CALENDAR = 60       # カレンダー表示用に遡る日数

# ----------------------
# ユーティリティ
# ----------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["date"])
            return df
        except Exception as e:
            st.error(f"データ読み込み失敗: {e}")
            return pd.DataFrame(columns=["date","exp","note"])
    else:
        return pd.DataFrame(columns=["date","exp","note"])

def append_entry(exp, note=""):
    df = load_data()
    now = pd.Timestamp(datetime.datetime.now()).floor('s')
    new = pd.DataFrame([{"date": now, "exp": exp, "note": note}])
    df = pd.concat([df, new], ignore_index=True)
    try:
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"データ保存に失敗しました: {e}")
    return df

def undo_last():
    if not os.path.exists(DATA_FILE):
        return
    df = load_data()
    if df.shape[0] == 0:
        return
    df = df.iloc[:-1]
    df.to_csv(DATA_FILE, index=False)
    return df

def total_exp(df):
    if df.empty:
        return 0
    return int(df["exp"].sum())

def current_level(total_exp_val):
    return total_exp_val // EXP_PER_LEVEL + 1

def exp_within_level(total_exp_val):
    return total_exp_val % EXP_PER_LEVEL

# ----------------------
# UI
# ----------------------
st.set_page_config(page_title="頑張れアプリ（RPG風）", page_icon="🎓", layout="centered")
st.title("🎮 国家試験応援RPG（シンプル版）")
st.write("勉強を終えたら「今日の勉強終わった！」を押してね。キャラが成長します！")

# Load data
df = load_data()
tot_exp = total_exp(df)
lvl = current_level(tot_exp)
exp_in_lvl = exp_within_level(tot_exp)
exp_needed = EXP_PER_LEVEL

# 左カラム：キャラ表示・ボタン
col1, col2 = st.columns([1,1])

with col1:
    st.subheader("キャラ")
    # シンプルにレベルに応じた絵文字＆説明を出す
    # 好みでここに画像表示を追加できます（st.image）
    emoji_map = {
        1: "😪 学生（開始）",
        2: "🙂 コツコツ組",
        3: "😤 やる気UP",
        4: "🧠 集中モード",
        5: "🩺 試験へ一直線",
        6: "🏆 合格目前！"
    }
    display_emoji = emoji_map.get(min(lvl, max(emoji_map.keys())), "💪 勝利の予感")
    st.markdown(f"## {display_emoji}")
    st.write(f"レベル: **Lv {lvl}**")
    st.progress(exp_in_lvl / exp_needed)
    st.write(f"経験値: **{exp_in_lvl} / {exp_needed}** (累計 {tot_exp} EXP)")

    # レベルアップ時に出すあなたのメッセージ（デフォはランダムな褒め言葉）
    default_messages = [
        "よく頑張ってるね！",
        "その調子！君ならできるよ！",
        "集中してて偉い！休憩も忘れずにね。",
        "少しずつ近づいてるよ！"
    ]
    if "last_level" not in st.session_state:
        st.session_state["last_level"] = lvl

    # 勉強ボタン
    st.write("")
    if st.button("✅ 今日の勉強終わった！"):
        # append entry
        note = st.text_input("メモ（任意）", value="", key="note_input")
        df = append_entry(EXP_PER_PRESS, note)
        tot_exp = total_exp(df)
        new_lvl = current_level(tot_exp)
        st.success(f"経験値 +{EXP_PER_PRESS}！合計 {tot_exp} EXP")
        # レベルアップ検出
        if new_lvl > st.session_state["last_level"]:
            st.balloons()
            st.success(f"🎉 レベルアップ！ Lv{st.session_state['last_level']} → Lv{new_lvl} 🎉")
            # レベルアップ時に応援メッセージを表示
            st.info(default_messages[(new_lvl-1) % len(default_messages)])
        st.session_state["last_level"] = new_lvl
        # reload
        df = load_data()
        tot_exp = total_exp(df)
        lvl = current_level(tot_exp)
        exp_in_lvl = exp_within_level(tot_exp)

    # カスタムEXPボタン（オプション）
    st.write("")
    st.write("オプション：まとめて記録したいとき")
    custom_exp = st.number_input("まとめて追加する経験値", min_value=0, value=0, step=10)
    if st.button("追加で記録する"):
        if custom_exp > 0:
            df = append_entry(int(custom_exp), note="まとめて追加")
            st.success(f"経験値 +{custom_exp} を追加しました")
            # update session level
            st.session_state["last_level"] = current_level(total_exp(df))

with col2:
    st.subheader("記録・管理")
    st.write("直近の記録（新しい順）")
    if df.empty:
        st.write("まだ記録がありません。")
    else:
        st.dataframe(df.sort_values("date", ascending=False).assign(date=lambda d: d["date"].dt.strftime("%Y-%m-%d %H:%M:%S")))

    # Undo / リセット（シンプル）
    st.write("")
    if st.button("⤺ 最後の記録を取り消す"):
        df = undo_last()
        if df is None:
            st.warning("取り消せる記録がありません。")
        else:
            st.success("最後の記録を取り消しました。")
            st.session_state["last_level"] = current_level(total_exp(df))

    st.write("")
    if st.button("⚠️ 全データをリセット（注意）"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("データをリセットしました。")
            st.session_state["last_level"] = 1
            df = load_data()
        else:
            st.warning("データファイルが見つかりませんでした。")

# ----------------------
# カレンダー風表示（簡易）
# ----------------------
st.markdown("---")
st.subheader("📅 カレンダー（過去 {} 日）".format(MAX_DAYS_CALENDAR))
today = datetime.date.today()
dates = [today - datetime.timedelta(days=i) for i in range(MAX_DAYS_CALENDAR-1, -1, -1)]
dates_df = pd.DataFrame({"date": dates})
if not df.empty:
    df_days = df.copy()
    df_days["day"] = df_days["date"].dt.date
    counts = df_days.groupby("day")["exp"].count().reindex(dates, fill_value=0)
    calendar_df = pd.DataFrame({
        "date": dates,
        "did_study": [1 if counts.get(d, 0) > 0 else 0 for d in dates],
        "records": [int(counts.get(d, 0)) if d in counts.index else 0 for d in dates]
    })
else:
    calendar_df = pd.DataFrame({
        "date": dates,
        "did_study": [0 for _ in dates],
        "records": [0 for _ in dates]
    })

# 表示：横並びで日付とチェックを出す（シンプル）
cols = st.columns(14)
for i, row in calendar_df.iterrows():
    col_idx = i % 14
    with cols[col_idx]:
        d = row["date"]
        mark = "✅" if row["did_study"] else "◻️"
        st.write(f"{d.strftime('%m/%d')}")
        st.write(mark)

# ----------------------
# 週ごとのグラフ
# ----------------------
st.markdown("---")
st.subheader("📊 週間サマリ（直近8週）")
# prepare weekly counts
if df.empty:
    st.write("記録がありません。ボタンを押して記録してみましょう！")
else:
    df_week = df.copy()
    df_week["date_only"] = df_week["date"].dt.date
    df_week["week"] = df_week["date"].dt.to_period("W").apply(lambda r: r.start_time.date())
    weekly = df_week.groupby("week").size().reset_index(name="times")
    # 最近8週分を補完
    last_monday = (pd.Timestamp(today) - pd.offsets.Week(weekday=0)).date()
    weeks = [last_monday - datetime.timedelta(weeks=i) for i in range(7, -1, -1)]
    weekly_all = pd.DataFrame({"week": weeks})
    weekly_all = weekly_all.merge(weekly, on="week", how="left").fillna(0)
    weekly_all["times"] = weekly_all["times"].astype(int)
    st.bar_chart(weekly_all.set_index("week")["times"])

# ----------------------
# データダウンロード
# ----------------------
st.markdown("---")
st.subheader("データのダウンロード / インポート")
df_for_download = load_data()
if not df_for_download.empty:
    csv_bytes = df_for_download.to_csv(index=False).encode()
    st.download_button("CSVをダウンロード", data=csv_bytes, file_name="study_log.csv", mime="text/csv")
else:
    st.write("ダウンロードできるデータがありません。")

st.write("※ Googleスプレッドシート連携や、キャラ画像・アイコンを追加したい場合は後で拡張できます。")

# ----------------------
# footer / tips
# ----------------------
st.markdown("---")
st.write("作ってあげるヒント：")
st.write("- `EXP_PER_PRESS` を増やすとボタン1回での成長が早くなります。")
st.write("- キャラ画像を用意して `st.image()` でレベルに応じて表示するとグッと見た目が良くなります。")
st.write("- データをクラウドに保存したい場合は Google Sheets API 連携を検討してください。")

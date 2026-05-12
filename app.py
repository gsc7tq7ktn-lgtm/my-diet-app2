import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 頁面基本設定
st.set_page_config(page_title="飲食控 Pro", layout="centered")

# --- 側邊欄：個人化計算器 ---
with st.sidebar:
    st.title("⚙️ 設定")
    gender = st.radio("性別", ["男", "女"])
    weight = st.number_input("體重 (kg)", value=70.0)
    height = st.number_input("身高 (cm)", value=175.0)
    age = st.number_input("年齡", value=25)
    act = st.select_slider("活動量", options=[1.2, 1.375, 1.55, 1.725])
    
    # BMR/TDEE 計算
    bmr = 10*weight + 6.25*height - 5*age + (5 if gender=="男" else -161)
    tdee = round(bmr * act)
    st.success(f"建議攝取：{tdee} kcal")

# --- 主畫面儀表板 ---
st.title("🥗 我的飲食日誌")
today = datetime.now().strftime("%Y-%m-%d")

# 初始化 session_state (模擬資料庫)
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['日期', '食物', '熱量', '蛋', '脂', '碳'])

# 計算數據
today_data = st.session_state.df[st.session_state.df['日期'] == today]
consumed = today_data['熱量'].sum()
remaining = max(0, tdee - consumed)

# 儀表板視覺化
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = consumed,
    title = {'text': "今日已攝取 (kcal)"},
    domain = {'x': [0, 1], 'y': [0, 1]},
    gauge = {
        'axis': {'range': [None, tdee]},
        'bar': {'color': "#1ED760"},
        'steps': [{'range': [0, tdee], 'color': "#eeeeee"}],
        'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': tdee}
    }
))
fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=0))
st.plotly_chart(fig, use_container_width=True)

# --- 新增飲食功能 ---
with st.expander("➕ 記錄一餐", expanded=True):
    with st.form("add_food", clear_on_submit=True):
        name = st.text_input("食物名稱 (例：雞胸肉便當)")
        c1, c2 = st.columns(2)
        cal = c1.number_input("熱量 (kcal)", min_value=0)
        p = c2.number_input("蛋白質 (g)", min_value=0)
        f = c1.number_input("脂肪 (g)", min_value=0)
        c = c2.number_input("碳水 (g)", min_value=0)
        
        if st.form_submit_button("送出紀錄"):
            new_row = pd.DataFrame([[today, name, cal, p, f, c]], columns=st.session_state.df.columns)
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.rerun()

# --- 歷史紀錄與分析 ---
st.subheader("📝 今日詳情")
if not today_data.empty:
    st.dataframe(today_data[['食物', '熱量', '蛋', '脂', '碳']], hide_index=True)
    if st.button("🗑️ 清空今日紀錄"):
        st.session_state.df = st.session_state.df[st.session_state.df['日期'] != today]
        st.rerun()
else:
    st.info("今天還沒有紀錄，開始記錄你的第一餐吧！")

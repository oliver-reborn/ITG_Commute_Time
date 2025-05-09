import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import ast
from dateutil.parser import parse
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'  # 設定使用微軟正黑體

# 計算兩點距離（km）
def calc_distance(coords):
    p1, p2 = coords
    return geodesic((p1[1], p1[0]), (p2[1], p2[0])).km

# 根據路段名稱與時間模擬速度
def simulate_speed(name, departure_time):
    peak_hours = [(7, 8.5), (17, 19)]
    base_speed = 50
    if isinstance(name, str):
        if "工業區" in name:
            base_speed = 40
        elif "向上" in name or "文心" in name:
            base_speed = 60
        elif "福田" in name or "建國" in name:
            base_speed = 50
    hour = departure_time.hour
    minute = departure_time.minute
    time_decimal = hour + minute / 60
    is_peak = any(start <= time_decimal < end for start, end in peak_hours)
    return base_speed * 0.5 if is_peak else base_speed

# 主頁面
st.title("🚗 通勤時間預測工具")
st.markdown("請輸入預計出發時間（例如 `07:30`），我會幫你估算通勤所需時間")

departure_str = st.text_input("出發時間（24小時制，例如 07:30）", value="08:00")

if st.button("開始模擬"):
    try:
        departure_str = departure_str.strip()
        departure_time = parse(departure_str)

        df = pd.read_csv("route_segments_with_real_names.csv")
        df["segment_coords"] = df["segment_coords"].apply(ast.literal_eval)
        df["distance_km"] = df["segment_coords"].apply(calc_distance)
        df["simulated_speed_kph"] = df["segment_name"].apply(
            lambda name: simulate_speed(name, departure_time)
        )
        df["simulated_duration_sec"] = (
            df["distance_km"] / df["simulated_speed_kph"]
        ) * 3600

        total_minutes = df["simulated_duration_sec"].sum() / 60
        st.success(f"✅ 出發時間 {departure_time.strftime('%H:%M')} 預估總通勤時間：{total_minutes:.1f} 分鐘")

        st.dataframe(df[["segment_name", "distance_km", "simulated_speed_kph", "simulated_duration_sec"]])
    
    except Exception as e:
        st.error("❌ 請輸入正確時間格式，例如：07:30")

# 額外功能：每 10 分鐘出發模擬柱狀圖
if st.checkbox("📊 顯示每 10 分鐘出發模擬結果（07:00 ~ 09:00）"):
    times = pd.date_range("07:00", "09:00", freq="10min")
    results = []

    df_base = pd.read_csv("route_segments_with_real_names.csv")
    df_base["segment_coords"] = df_base["segment_coords"].apply(ast.literal_eval)
    df_base["distance_km"] = df_base["segment_coords"].apply(calc_distance)

    for t in times:
        departure_time = t.to_pydatetime()
        df = df_base.copy()
        df["simulated_speed_kph"] = df["segment_name"].apply(
            lambda name: simulate_speed(name, departure_time)
        )
        df["simulated_duration_sec"] = (
            df["distance_km"] / df["simulated_speed_kph"]
        ) * 3600
        total_minutes = df["simulated_duration_sec"].sum() / 60
        results.append((departure_time.strftime("%H:%M"), total_minutes))

    # 畫圖
    x, y = zip(*results)
    fig, ax = plt.subplots()
    ax.bar(x, y, color="skyblue")
    ax.set_xlabel("出發時間")
    ax.set_ylabel("預估通勤時間（分鐘）")
    ax.set_title("通勤時間 vs 出發時間（每 10 分鐘）")
    plt.xticks(rotation=45)
    st.pyplot(fig)

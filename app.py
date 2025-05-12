import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
matplotlib.rcParams['axes.unicode_minus'] = False

# ✅ 計算距離
def calc_distance(coords):
    p1, p2 = coords
    return geodesic((p1[1], p1[0]), (p2[1], p2[0])).km

# ✅ 模擬速度（根據路段與時間）
def simulate_speed(name, departure_time):
    peak_hours = [(7.0, 8.5), (17.0, 19.0)]
    base_speed = 50
    if isinstance(name, str):
        if "工業區" in name:
            base_speed = 40
        elif "向上" in name or "文心" in name:
            base_speed = 60
        elif "福田" in name or "建國" in name:
            base_speed = 50
    time_decimal = departure_time.hour + departure_time.minute / 60
    is_peak = any(start <= time_decimal < end for start, end in peak_hours)
    return base_speed * 0.5 if is_peak else base_speed

# ✅ 主介面
st.title("🚗 通勤時間預測工具(福田水資源至台中工業區)")
st.markdown("請輸入預計出發時間（例如 `07:30`），我會幫你估算通勤所需時間")

departure_str = st.text_input("出發時間（24小時制，例如 07:30）", value="08:00")
show_chart = st.checkbox("📊 顯示每 10 分鐘出發模擬結果（07:00 ~ 09:00）", value=True)

# ✅ 模擬通勤時間
def simulate_commute(departure_time):
    df = pd.read_csv("route_segments_with_real_names.csv")
    df["segment_coords"] = df["segment_coords"].apply(ast.literal_eval)
    df["distance_km"] = df["segment_coords"].apply(calc_distance)
    df["simulated_speed_kph"] = df["segment_name"].apply(lambda name: simulate_speed(name, departure_time))
    df["simulated_duration_sec"] = (df["distance_km"] / df["simulated_speed_kph"]) * 3600
    total_minutes = df["simulated_duration_sec"].sum() / 60
    return total_minutes, df

# ✅ 單一輸入時間模擬
if st.button("開始模擬"):
    try:
        departure_time = datetime.strptime(departure_str, "%H:%M")
        total_minutes, df_result = simulate_commute(departure_time)
        st.success(f"✅ 出發時間 {departure_str} 預估總通勤時間：{total_minutes:.1f} 分鐘")
        st.dataframe(df_result[["segment_name", "distance_km", "simulated_speed_kph", "simulated_duration_sec"]])
    except:
        st.error("❌ 請輸入正確時間格式，例如：07:30")

# ✅ 顯示圖表
if show_chart:
    times = []
    durations = []
    for i in range(13):
        dt = datetime.strptime("07:00", "%H:%M") + timedelta(minutes=10*i)
        label = dt.strftime("%H:%M")
        minutes, _ = simulate_commute(dt)
        times.append(label)
        durations.append(minutes)

    df_chart = pd.DataFrame({"預估通勤時間（分鐘）": durations}, index=times)
    st.bar_chart(df_chart)


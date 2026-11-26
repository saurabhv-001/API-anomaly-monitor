import random
import time
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Adaptive Edge-Driven Real-Time API Health Monitor",
    layout="wide",
)

st.title("Adaptive Edge-Driven Real-Time API Health Monitor")
st.caption(
    "Project Module: Real-time Edge Traffic Surveillance & Isolation Forest ML Anomaly Detection"
)

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "latency"])

st.sidebar.header("App Controls")
is_running = st.sidebar.toggle("Live Monitoring", value=True)
traffic_mode = st.sidebar.selectbox(
    "Traffic Simulation Mode",
    ["Mixed / Auto", "Normal Traffic", "Anomaly / High Latency"],
)
threshold_ms = st.sidebar.slider(
    "Anomaly Latency Threshold (ms)",
    min_value=80.0,
    max_value=350.0,
    value=210.0,
    step=10.0,
)
refresh_sec = st.sidebar.selectbox("Refresh Interval (sec)", [0.5, 1.0, 2.0], index=1)
backend_url = st.sidebar.text_input(
    "Backend API URL (Optional)",
    value="http://127.0.0.1:8000/generate-traffic",
)

if st.sidebar.button("Clear Graph History"):
    st.session_state.history = pd.DataFrame(columns=["timestamp", "latency"])
    st.rerun()

st.subheader("Live API Latency Stream")

col1, col2, col3 = st.columns(3)
with col1:
    metric_latency = st.empty()
with col2:
    metric_status = st.empty()
with col3:
    metric_alert = st.empty()

chart_placeholder = st.empty()


def get_simulated_point(mode: str, threshold: float):
    if mode == "Normal Traffic":
        latency = round(random.uniform(35.0, max(45.0, threshold - 20.0)), 2)
    elif mode == "Anomaly / High Latency":
        latency = round(random.uniform(threshold + 10.0, threshold + 120.0), 2)
    else:
        latency = round(random.uniform(35.0, 280.0), 2)

    is_anomaly = 1 if latency > threshold else 0
    status = 503 if is_anomaly == 1 else 200
    return latency, status, is_anomaly


def render_dashboard(latency, status, is_anomaly):
    timestamp = time.strftime("%H:%M:%S")
    new_row = pd.DataFrame([{"timestamp": timestamp, "latency": latency}])
    st.session_state.history = pd.concat(
        [st.session_state.history, new_row], ignore_index=True
    )
    if len(st.session_state.history) > 30:
        st.session_state.history = st.session_state.history.tail(30)

    metric_latency.metric("Current Latency", f"{latency} ms", delta=None)
    metric_status.metric("HTTP Status Code", f"{status}")

    if is_anomaly == 1:
        metric_alert.error("🚨 ANOMALY / ATTACK DETECTED!")
    else:
        metric_alert.success("🟢 System Status: Normal")

    chart_data = st.session_state.history.set_index("timestamp")[["latency"]]
    chart_placeholder.line_chart(chart_data)


if not is_running:
    st.info("Monitoring paused from App Controls. Toggle 'Live Monitoring' ON to resume.")
    if not st.session_state.history.empty:
        last_row = st.session_state.history.iloc[-1]
        last_lat = float(last_row["latency"])
        last_anom = 1 if last_lat > threshold_ms else 0
        metric_latency.metric("Current Latency", f"{last_lat} ms", delta=None)
        metric_status.metric("HTTP Status Code", f"{503 if last_anom else 200}")
        if last_anom:
            metric_alert.error("🚨 ANOMALY / ATTACK DETECTED!")
        else:
            metric_alert.success("🟢 System Status: Normal")
        chart_placeholder.line_chart(
            st.session_state.history.set_index("timestamp")[["latency"]]
        )
else:
    while True:
        try:
            if traffic_mode == "Mixed / Auto" and backend_url.strip():
                response = requests.get(backend_url.strip(), timeout=1.0)
                response.raise_for_status()
                data = response.json()
                latency = float(data["latency"])
                is_anomaly = 1 if latency > threshold_ms else int(data.get("is_anomaly", 0))
                status = 503 if is_anomaly == 1 else int(data.get("status", 200))
            else:
                latency, status, is_anomaly = get_simulated_point(traffic_mode, threshold_ms)
        except Exception:
            latency,status,is_anomaly =get_simulated_point(traffic_mode,threshold_ms)
            render_dashboard(latency,status, is_anomaly)
            time.sleep(refresh_sec)

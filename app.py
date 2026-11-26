import requests
import streamlit as st

st.set_page_config(
    page_title="API Anomaly Monitor", page_icon="🛡️", layout="wide"
)

st.title("🛡️ Adaptive Edge-Driven Real-Time API Health Monitor")
st.markdown(
    "**Project Module:** Real-time Edge Traffic Surveillance & Isolation"
    " Forest ML Anomaly Detection"
)

# Initialize session state history for live chartsssion_state.history = pd.DataFrame(
      columns=["timestamp", "latency", "status", "is_anomaly"]
  )

# Layout placeholders
col1, col2, col3 = st.columns(3)
metric_latency = col1.empty()
metric_status = col2.empty()
metric_alert = col3.empty()

st.subheader("📈 Live API Latency Stream")
chart_placeholder = st.empty()

# Auto-refresh loop to fetch data from FastAPI backend every 1 second
while True:
  try:
    # Fetch live metric from FastAPI backend
    response = requests.get("http://127.0.0.1:8000/generate-traffic")
    data = response.json()

    # Append to history dataframe
    new_row = pd.DataFrame([data])
    st.session_state.history = pd.concat(
        [st.session_state.history, new_row], ignore_index=True
    )

    # Keep only the last 30 data points for clean graph rendering
    if len(st.session_state.history) > 30:
      st.session_state.history = st.session_state.history.tail(30)

    # Update UI Metrics
    metric_latency.metric(
        "Current Latency", f"{data['latency']} ms", delta=None
    )
    metric_status.metric("HTTP Status Code", f"{data['status']}")

    if data["is_anomaly"] == 1:
      metric_alert.error("🚨 ANOMALY / ATTACK DETECTED!")
    else:
      metric_alert.success("🟢 System Status: Normal")

    # Update Line Chart
    chart_data = st.session_state.histor

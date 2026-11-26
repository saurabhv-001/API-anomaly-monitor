import random
import time
from fastapi import FastAPI
import numpy as np
from sklearn.ensemble import IsolationForest

app = FastAPI()

# Isolation Forest Model Setup (Unsupervised Learning)
# Features: [Latency in ms, Status Error Flag (0 for OK, 1 for Error)]
X_train = np.array([[40, 0], [50, 0], [60, 0], [45, 0], [55, 0], [65, 0]])
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_train)

# In-memory storage for latest traffic metric
latest_metric = {
    "timestamp": "00:00:00",
    "latency": 50,
    "status": 200,
    "is_anomaly": 0,
}


@app.get("/generate-traffic")
def generate_traffic():
  global latest_metric

  # 85% normal traffic, 15% anomaly/attack traffic simulation
  is_attack = random.random() < 0.15

  if is_attack:
    latency = random.randint(400, 950)  # High latency spike
    status = 500  # Server Error
  else:
    latency = random.randint(30, 110)  # Normal latency
    status = 200  # OK

  # ML Prediction (-1 means Anomaly, 1 means Normal)
  error_flag = 1 if status >= 400 else 0
  prediction = model.predict([[latency, error_flag]])[0]
  anomaly_detected = 1 if prediction == -1 else 0

  # Update latest metric
  latest_metric = {
      "timestamp": time.strftime("%H:%M:%S"),
      "latency": latency,
      "status": status,
      "is_anomaly": anomaly_detected,
  }

  return latest_metric


@app.get("/get-metrics")
def get_metrics():
  return latest_metric
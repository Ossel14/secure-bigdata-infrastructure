import psycopg2
import pandas as pd
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

DB_CONFIG = {
    "host": "192.168.50.20",
    "database": "bigdata",
    "user": "bigdata_user",
    "password": "SecurePass123"
}

def fetch_data(hours=72):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql_query(
        f"SELECT sensor_id, value, timestamp FROM sensor_data WHERE timestamp > NOW() - INTERVAL '{hours} hours'",
        conn
    )
    conn.close()
    return df

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "processing-server"})

@app.route("/stats")
def statistics():
    df = fetch_data()
    if df.empty:
        return jsonify({"error": "No data", "rows": 0})
    stats = df.groupby("sensor_id")["value"].agg(
        count="count", mean="mean", median="median", std="std", min="min", max="max"
    ).round(2).fillna(0)
    return jsonify({
        "generated_at": datetime.now().isoformat(),
        "total_records": len(df),
        "sensors": stats.reset_index().to_dict(orient="records")
    })

@app.route("/anomalies")
def detect_anomalies():
    df = fetch_data()
    results = []
    for sensor_id, group in df.groupby("sensor_id"):
        mean, std = group["value"].mean(), group["value"].std()
        if std == 0 or pd.isna(std):
            continue
        outliers = group[abs((group["value"] - mean) / std) > 2.0]
        for _, row in outliers.iterrows():
            results.append({
                "sensor_id": sensor_id,
                "value": float(row["value"]),
                "z_score": round(abs((row["value"] - mean) / std), 2),
                "timestamp": str(row["timestamp"])
            })
    return jsonify({"anomalies": results, "count": len(results)})

@app.route("/report")
def generate_report():
    df = fetch_data()
    if df.empty:
        return jsonify({"error": "No data"})

    report_path = "/mnt/bigdata-share/report.txt"
    stats = df.groupby("sensor_id")["value"].agg(
        count="count", mean="mean", min="min", max="max"
    ).round(2)

    with open(report_path, "w") as f:
        f.write("=== BigData Analytics Report ===\n")
        f.write(f"Generated at: {datetime.now()}\n")
        f.write(f"Total records: {len(df)}\n\n")
        f.write(stats.to_string())
        f.write("\n")

    return jsonify({"status": "report saved", "path": report_path})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

from flask import Flask, request, jsonify
import psycopg2
import urllib.request
import os

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "192.168.50.20"),
        database=os.environ.get("DB_NAME", "bigdata"),
        user=os.environ.get("DB_USER", "bigdata_user"),
        password=os.environ.get("DB_PASS", "SecurePass123")
    )

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "app-server"})

@app.route("/data", methods=["POST"])
def ingest_data():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sensor_data (sensor_id, value, timestamp) VALUES (%s, %s, NOW())",
        (data["sensor_id"], data["value"])
    )
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"status": "inserted"})

@app.route("/data", methods=["GET"])
def get_data():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT sensor_id, value, timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 100")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"sensor_id": r[0], "value": r[1], "time": str(r[2])} for r in rows])

@app.route("/stats")
def stats_proxy():
    with urllib.request.urlopen("http://192.168.50.30:8000/stats") as r:
        return app.response_class(r.read(), mimetype="application/json")

@app.route("/anomalies")
def anomalies_proxy():
    with urllib.request.urlopen("http://192.168.50.30:8000/anomalies") as r:
        return app.response_class(r.read(), mimetype="application/json")

@app.route("/dashboard")
def dashboard():
    return """<!DOCTYPE html>
<html>
<head>
    <title>BigData Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial, sans-serif; background: #0f1117; color: #eee; padding: 20px; }
        h1 { color: #4fc3f7; }
        h2 { color: #81d4fa; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; }
        th { background: #1e3a5f; color: #4fc3f7; padding: 10px; text-align: left; }
        td { padding: 8px 10px; border-bottom: 1px solid #222; }
        tr:hover { background: #1a1a2e; }
        .anomaly { color: #ff5252; font-weight: bold; }
        .badge { background: #1e3a5f; padding: 4px 10px; border-radius: 12px; font-size: 13px; }
    </style>
</head>
<body>
    <h1>&#128187; BigData Infrastructure Dashboard</h1>
    <p class="badge">Auto-refreshes every 10 seconds</p>

    <h2>&#128202; Sensor Statistics</h2>
    <table>
        <thead><tr><th>Sensor</th><th>Count</th><th>Mean</th><th>Median</th><th>Std</th><th>Min</th><th>Max</th></tr></thead>
        <tbody id="stats-body"><tr><td colspan="7">Loading...</td></tr></tbody>
    </table>

    <h2>&#9888; Anomalies Detected</h2>
    <table>
        <thead><tr><th>Sensor</th><th>Value</th><th>Z-Score</th><th>Timestamp</th></tr></thead>
        <tbody id="anomaly-body"><tr><td colspan="4">Loading...</td></tr></tbody>
    </table>

    <h2>&#128225; Latest Sensor Readings</h2>
    <table>
        <thead><tr><th>Sensor</th><th>Value</th><th>Timestamp</th></tr></thead>
        <tbody id="data-body"><tr><td colspan="3">Loading...</td></tr></tbody>
    </table>

    <script>
        async function loadStats() {
            const res = await fetch("/stats");
            const json = await res.json();
            const tbody = document.getElementById("stats-body");
            tbody.innerHTML = "";
            if (json.error) { tbody.innerHTML = "<tr><td colspan='7'>No data yet</td></tr>"; return; }
            json.sensors.forEach(s => {
                tbody.innerHTML += "<tr><td>" + s.sensor_id + "</td><td>" + s.count + "</td><td>" + s.mean + "</td><td>" + s.median + "</td><td>" + s.std + "</td><td>" + s.min + "</td><td>" + s.max + "</td></tr>";
            });
        }

        async function loadAnomalies() {
            const res = await fetch("/anomalies");
            const json = await res.json();
            const tbody = document.getElementById("anomaly-body");
            tbody.innerHTML = "";
            if (!json.anomalies.length) { tbody.innerHTML = "<tr><td colspan='4'>No anomalies detected</td></tr>"; return; }
            json.anomalies.forEach(a => {
                tbody.innerHTML += "<tr><td class='anomaly'>" + a.sensor_id + "</td><td class='anomaly'>" + a.value + "</td><td>" + a.z_score + "</td><td>" + a.timestamp + "</td></tr>";
            });
        }

        async function loadData() {
            const res = await fetch("/data");
            const json = await res.json();
            const tbody = document.getElementById("data-body");
            tbody.innerHTML = "";
            json.slice(0, 20).forEach(r => {
                tbody.innerHTML += "<tr><td>" + r.sensor_id + "</td><td>" + r.value + "</td><td>" + r.time + "</td></tr>";
            });
        }

        loadStats(); loadAnomalies(); loadData();
    </script>
</body>
</html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

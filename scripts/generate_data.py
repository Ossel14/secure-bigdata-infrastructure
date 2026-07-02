import requests, random, time

API = "http://localhost:5000/data"
SENSORS = ["temp_001", "temp_002", "humidity_01", "pressure_01", "vibration_01"]

print("Inserting 200 sensor readings...")
for i in range(200):
    value = round(random.uniform(100, 150), 2) if random.random() < 0.05 else round(random.uniform(18, 30), 2)
    requests.post(API, json={"sensor_id": random.choice(SENSORS), "value": value})
    if i % 20 == 0: print(f"  {i+1}/200...")
    time.sleep(0.05)

print("Done!")

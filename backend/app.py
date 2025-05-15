from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import random
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)
CORS(app)

# Initial drone state with telemetry
status = {
    "armed": False,
    "altitude": 0,
    "mission": [],
    "current_wp_index": None,
    "state": "disarmed",
    "battery": 100,
    "gps_locked": True,
    "flight_mode": "MANUAL"
}

# Helper: Haversine distance in KM
def is_within_radius(lat1, lng1, lat2, lng2, radius_km):
    dlat = radians(lat2 - lat1)
    dlng = radians(lat2 - lng2)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return (6371 * c) <= radius_km

# === Background Thread for Real-Time Simulation ===
def telemetry_loop():
    while True:
        time.sleep(5)

        print(f"[LOOP] Battery={status['battery']} | Alt={status['altitude']} | State={status['state']} | Armed={status['armed']}")

        if status["state"] == "disarmed":
            continue

        status["battery"] = max(status["battery"] - 1, 0)

        if status["state"] == "flying":
            status["altitude"] = min(status["altitude"] + 2, 120)
        elif status["state"] == "landing":
            status["altitude"] = max(status["altitude"] - 5, 0)

        if status["battery"] <= 5 and status["state"] == "flying":
            print("[AUTO] Critical battery, initiating FAILSAFE")
            status["state"] = "landing"
            status["flight_mode"] = "FAILSAFE"
            status["current_wp_index"] = None

        if status["state"] == "flying" and status["mission"]:
            idx = status.get("current_wp_index")
            if idx is not None and idx < len(status["mission"]) - 1:
                status["current_wp_index"] += 1
            elif idx == len(status["mission"]) - 1:
                print("[AUTO] Final waypoint reached — landing")
                status["state"] = "landing"
                status["flight_mode"] = "MANUAL"
                status["current_wp_index"] = None

        # ✅ Final disarm logic
        if status["altitude"] == 0 and status["state"] != "disarmed":
            print("[AUTO] Altitude = 0 → Disarming")
            status["state"] = "disarmed"
            status["armed"] = False
            status["flight_mode"] = "MANUAL"
            status["current_wp_index"] = None

# Start background telemetry thread
threading.Thread(target=telemetry_loop, daemon=True).start()

# === API Endpoints ===

@app.route('/api/arm', methods=['POST'])
def arm():
    if status["battery"] < 10:
        return jsonify({"message": "Battery too low to arm"}), 400
    if status["state"] != "disarmed":
        return jsonify({"message": "Cannot arm from current state"}), 400

    status["armed"] = True
    status["state"] = "armed"
    status["battery"] = max(status["battery"] - 1, 0)
    return jsonify({"message": "Drone armed"})

@app.route('/api/takeoff', methods=['POST'])
def takeoff():
    if status["battery"] < 20:
        return jsonify({"message": "Battery too low to take off"}), 400
    if not status["gps_locked"]:
        return jsonify({"message": "Cannot take off: GPS signal lost"}), 400
    if status["state"] != "armed":
        return jsonify({"message": "Drone must be armed before takeoff"}), 400

    status["altitude"] = 10
    status["state"] = "flying"
    status["flight_mode"] = "AUTO"
    status["battery"] = max(status["battery"] - 5, 0)

    if status["mission"]:
        status["current_wp_index"] = 0

    return jsonify({"message": "Drone took off to 10m"})

@app.route('/api/land', methods=['POST'])
def land():
    if status["state"] != "flying":
        return jsonify({"message": "Drone must be flying to land"}), 400

    status["state"] = "landing"
    status["flight_mode"] = "MANUAL"
    status["battery"] = max(status["battery"] - 2, 0)
    return jsonify({"message": "Landing sequence started"})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(status)

@app.route('/api/mission', methods=['POST'])
def upload_mission():
    if not status["gps_locked"]:
        return jsonify({"message": "Cannot upload mission: GPS lock required"}), 400

    data = request.json
    raw_waypoints = data.get("waypoints", [])

    base_lat, base_lng = 51.0447, -114.0719  # Calgary
    MAX_RADIUS_KM = 2

    generated = []
    for wp in raw_waypoints:
        for _ in range(10):
            offset_lat = random.uniform(-0.01, 0.01)
            offset_lng = random.uniform(-0.01, 0.01)
            new_lat = base_lat + offset_lat
            new_lng = base_lng + offset_lng
            if is_within_radius(base_lat, base_lng, new_lat, new_lng, MAX_RADIUS_KM):
                generated.append({
                    "name": wp,
                    "lat": round(new_lat, 6),
                    "lng": round(new_lng, 6)
                })
                break
        else:
            return jsonify({"message": f"Failed to assign valid location for {wp}"}), 400

    status["mission"] = generated
    return jsonify({"message": "Mission uploaded", "mission": status["mission"]})

@app.route('/api/inject_failure', methods=['POST'])
def inject_failure():
    data = request.json
    mode = data.get("mode")

    if mode == "gps_loss":
        status["gps_locked"] = False
        return jsonify({"message": "Simulated GPS loss"})

    elif mode == "low_battery":
        status["battery"] = 4
        return jsonify({"message": "Simulated critical battery"})

    elif mode == "motor_fail":
        if status["state"] == "flying":
            status["flight_mode"] = "FAILSAFE"
            status["state"] = "landing"
            return jsonify({"message": "Simulated motor failure — drone landing"})
        return jsonify({"message": "Motor failure only affects flying drones"}), 400

    elif mode == "reset":
        status.update({
            "gps_locked": True,
            "battery": 100,
            "flight_mode": "MANUAL"
        })
        return jsonify({"message": "System reset to normal"})

    return jsonify({"message": "Invalid failure mode"}), 400

@app.route('/api/clear_mission', methods=['POST'])
def clear_mission():
    status["mission"] = []
    status["current_wp_index"] = None
    return jsonify({"message": "Mission cleared"})

@app.route('/api/reset', methods=['POST'])
def reset():
    status.update({
        "armed": False,
        "altitude": 0,
        "mission": [],
        "current_wp_index": None,
        "state": "disarmed",
        "battery": 100,
        "gps_locked": True,
        "flight_mode": "MANUAL"
    })
    return jsonify({"message": "Drone reset to default state"})

if __name__ == '__main__':
    app.run(debug=True)

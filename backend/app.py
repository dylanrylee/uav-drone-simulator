from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time

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

# === Background Thread for Real-Time Simulation ===
def telemetry_loop():
    while True:
        time.sleep(5)  # Runs every 5 seconds

        # Skip simulation if drone is disarmed
        if status["state"] == "disarmed":
            continue

        # === Battery drain ===
        status["battery"] = max(status["battery"] - 1, 0)

        # === Altitude simulation ===
        if status["state"] == "flying":
            status["altitude"] = min(status["altitude"] + 2, 120)
        elif status["state"] == "landing":
            status["altitude"] = max(status["altitude"] - 5, 0)
            if status["altitude"] == 0:
                status["state"] = "disarmed"
                status["armed"] = False
                status["flight_mode"] = "MANUAL"
                status["current_wp_index"] = None

        # === Critical battery → initiate landing ===
        if status["battery"] <= 5 and status["state"] == "flying":
            status["state"] = "landing"
            status["flight_mode"] = "FAILSAFE"
            status["current_wp_index"] = None

        # === Mission simulation ===
        if status["state"] == "flying" and status["mission"]:
            idx = status.get("current_wp_index")
            if idx is not None and idx < len(status["mission"]) - 1:
                status["current_wp_index"] += 1
            elif idx == len(status["mission"]) - 1:
                # Final waypoint reached → initiate landing
                status["state"] = "landing"
                status["flight_mode"] = "MANUAL"
                status["current_wp_index"] = None

# Start background telemetry thread
threading.Thread(target=telemetry_loop, daemon=True).start()

# === API Routes ===

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

    # Use a Calgary-ish base location
    base_lat, base_lng = 51.0447, -114.0719

    # Generate fake GPS points slightly offset for each waypoint
    status["mission"] = [
        {
            "name": wp,
            "lat": base_lat + (i * 0.001),
            "lng": base_lng + (i * 0.001)
        }
        for i, wp in enumerate(raw_waypoints)
    ]

    return jsonify({
        "message": "Mission uploaded",
        "mission": status["mission"]
    })


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

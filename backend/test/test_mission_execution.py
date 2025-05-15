import requests
import time

API_URL = "http://localhost:5000/api"

def reset():
    requests.post(f"{API_URL}/reset")

def test_upload_valid_mission():
    reset()
    res = requests.post(f"{API_URL}/mission", json={"waypoints": ["WP1", "WP2", "WP3"]})
    assert res.status_code == 200
    mission = res.json().get("mission", [])
    assert len(mission) == 3
    assert all("lat" in wp and "lng" in wp for wp in mission)

def test_upload_mission_when_gps_lost():
    reset()
    requests.post(f"{API_URL}/inject_failure", json={"mode": "gps_loss"})
    res = requests.post(f"{API_URL}/mission", json={"waypoints": ["WP1", "WP2"]})
    assert res.status_code == 400
    assert "gps" in res.json()["message"].lower()

def test_upload_empty_mission():
    reset()
    res = requests.post(f"{API_URL}/mission", json={"waypoints": []})
    assert res.status_code == 200  # server still accepts it
    assert res.json()["mission"] == []

def test_upload_20_waypoints():
    reset()
    waypoints = [f"WP{i}" for i in range(20)]
    res = requests.post(f"{API_URL}/mission", json={"waypoints": waypoints})
    assert res.status_code == 200
    mission = res.json()["mission"]
    assert len(mission) == 20

def test_waypoint_progression():
    reset()
    waypoints = ["WP1", "WP2", "WP3"]
    requests.post(f"{API_URL}/mission", json={"waypoints": waypoints})
    requests.post(f"{API_URL}/arm")
    requests.post(f"{API_URL}/takeoff")

    # Wait for progression
    time.sleep(12)  # Wait enough time to step through 2+ waypoints

    res = requests.get(f"{API_URL}/status")
    data = res.json()
    assert data["current_wp_index"] is None or data["current_wp_index"] >= 1

def test_final_waypoint_triggers_landing():
    reset()
    waypoints = ["WP1", "WP2"]
    requests.post(f"{API_URL}/mission", json={"waypoints": waypoints})
    requests.post(f"{API_URL}/arm")
    requests.post(f"{API_URL}/takeoff")

    # Wait long enough to complete mission
    time.sleep(15)

    res = requests.get(f"{API_URL}/status")
    data = res.json()
    assert data["state"] in ["landing", "disarmed"]

import requests
import time

API_URL = "http://localhost:5000/api"

def reset():
    requests.post(f"{API_URL}/reset")

def get_status():
    return requests.get(f"{API_URL}/status").json()

def test_battery_drains_over_time():
    reset()
    requests.post(f"{API_URL}/mission", json={"waypoints": ["WP1", "WP2"]})
    requests.post(f"{API_URL}/arm")
    requests.post(f"{API_URL}/takeoff")

    initial = get_status()["battery"]

    time.sleep(7)  # Wait a bit more than 5s for sure

    new = get_status()["battery"]

    assert new < initial, f"Expected battery to drain, but got {new} >= {initial}"

def test_auto_land_when_battery_critically_low():
    reset()
    # Force battery to 6%, let telemetry drop it to 5%
    requests.post(f"{API_URL}/inject_failure", json={"mode": "low_battery"})
    requests.post(f"{API_URL}/mission", json={"waypoints": ["WP1", "WP2"]})
    requests.post(f"{API_URL}/arm")
    requests.post(f"{API_URL}/takeoff")

    time.sleep(6)  # Wait for telemetry loop to drop to 5% and trigger landing

    status = get_status()
    assert status["state"] in ["landing", "disarmed"]
    assert status["flight_mode"] in ["FAILSAFE", "MANUAL"]

def test_drone_lands_and_disarms_on_zero_battery():
    reset()

    # Set normal battery and start flight first
    requests.post(f"{API_URL}/mission", json={"waypoints": ["WP1"]})
    requests.post(f"{API_URL}/arm")
    requests.post(f"{API_URL}/takeoff")

    # THEN inject battery failure mid-flight
    time.sleep(1)  # give it time to take off
    requests.post(f"{API_URL}/inject_failure", json={"mode": "low_battery"})

    # Now observe landing + disarm over time
    for i in range(20):  # up to 100s
        time.sleep(5)
        status = get_status()
        print(f"[TEST] {i*5}s → Battery={status['battery']}, Alt={status['altitude']}, State={status['state']}, Armed={status['armed']}")
        
        if status["battery"] <= 0 and status["state"] == "disarmed":
            assert not status["armed"]
            return

    assert False, "Drone did not disarm even after battery reached 0"

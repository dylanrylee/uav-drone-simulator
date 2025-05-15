import requests
import time

API_URL = "http://localhost:5000/api"

def reset():
    requests.post(f"{API_URL}/reset")

def get_status():
    return requests.get(f"{API_URL}/status").json()

def test_land_while_disarmed():
    reset()
    res = requests.post(f"{API_URL}/land")
    assert res.status_code == 400
    assert "must be flying" in res.json()["message"].lower()

def test_arm_takeoff_land_arm_again():
    reset()
    assert requests.post(f"{API_URL}/arm").status_code == 200
    assert requests.post(f"{API_URL}/takeoff").status_code == 200
    time.sleep(1)
    assert requests.post(f"{API_URL}/land").status_code == 200

    # Wait until drone is disarmed
    for i in range(12):  # up to 60s
        time.sleep(5)
        status = get_status()
        print(f"[WAIT] {i*5}s → Alt={status['altitude']}, State={status['state']}, Armed={status['armed']}")
        if status["state"] == "disarmed":
            break
    else:
        assert False, "Drone did not disarm after landing"

    res = requests.post(f"{API_URL}/arm")
    assert res.status_code == 200
    assert "armed" in res.json()["message"].lower()

def test_arm_while_already_armed():
    reset()
    assert requests.post(f"{API_URL}/arm").status_code == 200
    res = requests.post(f"{API_URL}/arm")
    assert res.status_code == 400
    assert "cannot arm" in res.json()["message"].lower()

def test_takeoff_twice_without_landing():
    reset()
    requests.post(f"{API_URL}/mission", json={"waypoints": ["WP1"]})
    assert requests.post(f"{API_URL}/arm").status_code == 200
    assert requests.post(f"{API_URL}/takeoff").status_code == 200
    res = requests.post(f"{API_URL}/takeoff")  # second takeoff
    assert res.status_code == 400
    assert "must be armed" in res.json()["message"].lower()

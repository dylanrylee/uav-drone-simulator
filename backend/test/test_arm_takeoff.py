import requests

API_URL = "http://localhost:5000/api"

def reset():
    requests.post(f"{API_URL}/reset")

def test_arm_with_good_battery():
    reset()
    res = requests.post(f"{API_URL}/arm")
    assert res.status_code == 200
    assert "armed" in res.json()["message"].lower()

def test_arm_with_low_battery():
    reset()
    requests.post(f"{API_URL}/inject_failure", json = {"mode": "low_battery"})
    res = requests.post(f"{API_URL}/arm")
    assert res.status_code == 400
    assert "battery" in res.json()["message"].lower()

def test_arm_when_state_is_flying():
    reset()
    requests.post(f"{API_URL}/arm")
    requests.post(f"{API_URL}/takeoff")
    res = requests.post(f"{API_URL}/arm")
    assert res.status_code == 400
    assert "state" in res.json()["message"].lower()

def test_takeoff_after_arming():
    reset()
    requests.post(f"{API_URL}/arm")
    res = requests.post(f"{API_URL}/takeoff")
    assert res.status_code == 200
    assert "took off" in res.json()["message"].lower()

def test_takeoff_without_arming():
    reset()
    res = requests.post(f"{API_URL}/takeoff")
    assert res.status_code == 400
    assert "armed" in res.json()["message"].lower()

def test_takeoff_when_gps_lost():
    reset()
    requests.post(f"{API_URL}/inject_failure", json={"mode": "gps_loss"})
    requests.post(f"{API_URL}/arm")
    res = requests.post(f"{API_URL}/takeoff")
    assert res.status_code == 400
    assert "gps" in res.json()["message"].lower()

def test_takeoff_with_low_battery():
    reset()
    requests.post(f"{API_URL}/inject_failure", json={"mode": "low_battery"})
    requests.post(f"{API_URL}/arm")
    res = requests.post(f"{API_URL}/takeoff")
    assert res.status_code == 400
    assert "battery" in res.json()["message"].lower()
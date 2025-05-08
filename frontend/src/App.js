import React, { useState, useEffect } from "react";
import styles from "./App.module.css";
import { ToastContainer, toast } from "react-toastify";
import MapView from "./MapView";
import "react-toastify/dist/ReactToastify.css";

const API_URL = "http://localhost:5000/api";

function App() {
  const [status, setStatus] = useState({});
  const [waypoints, setWaypoints] = useState("");
  const [log, setLog] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchStatus();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const logAction = (action) => {
    const timestamp = new Date().toLocaleTimeString();
    setLog((prev) => [`[${timestamp}] ${action}`, ...prev]);
  };

  const fetchStatus = async (showToast = false) => {
    try {
      const res = await fetch(`${API_URL}/status`);
      const data = await res.json();
      setStatus(data);
      if (showToast) toast.success("✅ Status fetched");
      logAction("Fetched status");
    } catch (err) {
      toast.error("❌ Failed to fetch status");
      logAction("Failed to fetch status");
    }
  };

  const sendCommand = async (endpoint) => {
    try {
      const res = await fetch(`${API_URL}/${endpoint}`, { method: "POST" });
      if (!res.ok) {
        const errorData = await res.json();
        toast.error(`❌ ${errorData.message}`);
        logAction(`${endpoint} failed: ${errorData.message}`);
        return;
      }
      const data = await res.json();
      toast.success(`✅ ${data.message || `${endpoint} succeeded`}`);
      logAction(data.message || `${endpoint} sent`);
      fetchStatus();
    } catch (err) {
      toast.error(`❌ ${endpoint} failed`);
      logAction(`${endpoint} failed`);
    }
  };

  const uploadMission = async () => {
    const wpList = waypoints
      .split(",")
      .map((w) => w.trim())
      .filter((w) => w);
    if (wpList.length === 0) {
      toast.error("⚠️ Please enter at least one valid waypoint.");
      logAction("Mission upload failed (empty input)");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/mission`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ waypoints: wpList }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        toast.error(`❌ ${errorData.message}`);
        logAction(`Mission upload failed: ${errorData.message}`);
        return;
      }

      const data = await res.json();
      toast.success(`✅ ${data.message}`);
      logAction("Uploaded mission");
      fetchStatus();
    } catch (err) {
      toast.error("❌ Mission upload failed");
      logAction("Mission upload failed");
    }
  };

  const clearMission = async () => {
    try {
      const res = await fetch(`${API_URL}/clear_mission`, { method: "POST" });
      const data = await res.json();
      fetchStatus();
      toast.info(`🗑️ ${data.message || "Mission cleared"}`);
      logAction("Cleared mission");
    } catch (err) {
      toast.error("❌ Failed to clear mission");
      logAction("Clear mission failed");
    }
  };

  const handleFailureInjection = async (mode) => {
    try {
      const res = await fetch(`${API_URL}/inject_failure`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode }),
      });

      const data = await res.json();
      if (!res.ok) {
        toast.error(`❌ ${data.message}`);
        logAction(`Failure injection failed: ${data.message}`);
      } else {
        toast.info(`🧪 ${data.message}`);
        logAction(`Injected failure mode: ${mode}`);
      }

      fetchStatus();
    } catch (err) {
      toast.error("❌ Failed to inject failure");
      logAction("Failure injection error");
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>UAV Ground Control Mock</h1>

      <div className={styles.buttonGroup}>
        <button className={styles.button} onClick={() => sendCommand("arm")}>
          Arm
        </button>
        <button
          className={styles.button}
          onClick={() => sendCommand("takeoff")}
        >
          Takeoff
        </button>
        <button className={styles.button} onClick={() => sendCommand("land")}>
          Land
        </button>
        <button className={styles.button} onClick={() => fetchStatus(true)}>
          Get Status
        </button>
      </div>

      <div className={styles.inputGroup}>
        <div className={styles.label}>Upload Mission</div>
        <input
          type="text"
          placeholder="Enter waypoints (e.g. WP1, WP2)"
          value={waypoints}
          onChange={(e) => setWaypoints(e.target.value)}
          className={styles.input}
        />
        <button className={styles.button} onClick={uploadMission}>
          Upload
        </button>
        <button
          className={styles.button}
          style={{ backgroundColor: "#dc3545" }}
          onClick={clearMission}
        >
          Clear Mission
        </button>
      </div>

      <div style={{ marginTop: "2rem" }}>
        <div className={styles.label}>Failure Injection</div>
        <select
          onChange={(e) => {
            if (e.target.value) {
              handleFailureInjection(e.target.value);
              e.target.value = ""; // reset dropdown
            }
          }}
          defaultValue=""
        >
          <option value="" disabled>
            Choose a failure mode
          </option>
          <option value="gps_loss">Simulate GPS Loss</option>
          <option value="low_battery">Simulate Low Battery</option>
          <option value="motor_fail">Simulate Motor Failure</option>
          <option value="reset">Reset System</option>
        </select>
      </div>

      <div>
        <div className={styles.label}>Drone Status</div>
        <div className={styles.statusBox}>
          {Object.keys(status).length === 0
            ? "No status fetched yet."
            : JSON.stringify(status, null, 2)}
        </div>
      </div>

      {status.flight_mode === "FAILSAFE" && (
        <div
          style={{
            backgroundColor: "#ff4d4f",
            color: "white",
            padding: "10px",
            borderRadius: "8px",
            textAlign: "center",
            fontWeight: "bold",
            marginBottom: "1rem",
          }}
        >
          🚨 FAILSAFE MODE ACTIVE — Drone auto-landing
        </div>
      )}

      {Object.keys(status).length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <div className={styles.label}>Telemetry</div>
          <ul>
            <li>
              <strong>Battery:</strong>{" "}
              <span style={{ color: status.battery < 15 ? "red" : "inherit" }}>
                {status.battery}%
              </span>
            </li>
            <li>
              <strong>GPS Lock:</strong>{" "}
              <span style={{ color: status.gps_locked ? "inherit" : "orange" }}>
                {status.gps_locked ? "Yes" : "No"}
              </span>
            </li>
            <li>
              <strong>Flight Mode:</strong>{" "}
              <span
                style={{
                  color: status.flight_mode === "FAILSAFE" ? "red" : "inherit",
                }}
              >
                {status.flight_mode}
              </span>
            </li>
          </ul>
        </div>
      )}

      {status.mission && status.mission.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <div className={styles.label}>Current Mission Plan</div>
          <ul>
            {status.mission.map((wp, index) => (
              <li
                key={index}
                style={{
                  fontWeight:
                    index === status.current_wp_index ? "bold" : "normal",
                  color:
                    index === status.current_wp_index ? "#007bff" : "black",
                }}
              >
                Waypoint {index + 1}: {wp.name || wp}
                {index === status.current_wp_index && " → Executing"}
              </li>
            ))}
          </ul>

          {status.current_wp_index !== null && (
            <div style={{ marginTop: "1rem" }}>
              <div
                style={{
                  height: "10px",
                  width: "100%",
                  backgroundColor: "#eee",
                  borderRadius: "5px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${
                      ((status.current_wp_index + 1) / status.mission.length) *
                      100
                    }%`,
                    backgroundColor: "#007bff",
                    transition: "width 0.5s ease-in-out",
                  }}
                />
              </div>
              <div style={{ fontSize: "0.9rem", marginTop: "0.3rem" }}>
                Progress: {status.current_wp_index + 1} /{" "}
                {status.mission.length}
              </div>
            </div>
          )}

          <MapView
            mission={status.mission}
            currentIndex={status.current_wp_index}
          />
        </div>
      )}

      {log.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <div className={styles.label}>Command Log</div>
          <ul>
            {log.map((entry, index) => (
              <li key={index}>{entry}</li>
            ))}
          </ul>
        </div>
      )}

      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
}

export default App;

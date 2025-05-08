import React, { useState, useEffect } from 'react';
import styles from './App.module.css';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const API_URL = "http://localhost:5000/api";

function App() {
  const [status, setStatus] = useState({});
  const [waypoints, setWaypoints] = useState("");
  const [log, setLog] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchStatus(); // no toast shown here
    }, 5000);
  
    return () => clearInterval(interval);
  }, []);
  
  

  const logAction = (action) => {
    const timestamp = new Date().toLocaleTimeString();
    setLog(prev => [`[${timestamp}] ${action}`, ...prev]);
  };

  const fetchStatus = async (showToast = false) => {
    try {
      const res = await fetch(`${API_URL}/status`);
      const data = await res.json();
      setStatus(data);
      if (showToast) {
        toast.success("✅ Status fetched");
      }
      logAction("Fetched status");
    } catch (err) {
      toast.error("❌ Failed to fetch status");
      logAction("Failed to fetch status");
    }
  };
  

  const sendCommand = async (endpoint) => {
    try {
      const res = await fetch(`${API_URL}/${endpoint}`, { method: 'POST' });
  
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
    const wpList = waypoints.split(',').map(w => w.trim()).filter(w => w);
    if (wpList.length === 0) {
      toast.error("⚠️ Please enter at least one valid waypoint.");
      logAction("Mission upload failed (empty input)");
      return;
    }
  
    try {
      const res = await fetch(`${API_URL}/mission`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ waypoints: wpList })
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
      const res = await fetch(`${API_URL}/clear_mission`, { method: 'POST' });
      const data = await res.json();
      fetchStatus();
      toast.info(`🗑️ ${data.message || "Mission cleared"}`);
      logAction("Cleared mission");
    } catch (err) {
      toast.error("❌ Failed to clear mission");
      logAction("Clear mission failed");
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>UAV Ground Control Mock</h1>

      <div className={styles.buttonGroup}>
        <button className={styles.button} onClick={() => sendCommand("arm")}>Arm</button>
        <button className={styles.button} onClick={() => sendCommand("takeoff")}>Takeoff</button>
        <button className={styles.button} onClick={() => sendCommand("land")}>Land</button>
        <button className={styles.button} onClick={() => fetchStatus(true)}>Get Status</button>
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
        <button className={styles.button} onClick={uploadMission}>Upload</button>
        <button className={styles.button} style={{ backgroundColor: '#dc3545' }} onClick={clearMission}>Clear Mission</button>
      </div>

      <div>
        <div className={styles.label}>Drone Status</div>
        <div className={styles.statusBox}>
          {Object.keys(status).length === 0
            ? "No status fetched yet."
            : JSON.stringify(status, null, 2)}
        </div>
      </div>

      {Object.keys(status).length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <div className={styles.label}>Telemetry</div>
          <ul>
            <li><strong>Battery:</strong> {status.battery}%</li>
            <li><strong>GPS Lock:</strong> {status.gps_locked ? "Yes" : "No"}</li>
            <li><strong>Flight Mode:</strong> {status.flight_mode}</li>
          </ul>
        </div>
      )}

      {status.mission && status.mission.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <div className={styles.label}>Current Mission Plan</div>
          <ul>
            {status.mission.map((wp, index) => (
              <li key={index}>Waypoint {index + 1}: {wp}</li>
            ))}
          </ul>
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

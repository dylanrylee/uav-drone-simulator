# UAV Drone Ground Control System (Mock App)

A mock **UAV Ground Control System (GCS)** web app built with React and Flask. This project simulates realistic UAV features for testing and demonstration purposes without requiring physical hardware.  

## ✈️ Features

- **Simulated Telemetry**: Live updates for position, altitude, speed, battery, and GPS lock  
- **Mission Planning**:  
  - Add and manage waypoints  
  - Waypoint randomization and geofencing support  
- **Flight Simulation**:  
  - State transitions (Idle → Takeoff → Cruise → Landing)  
  - Battery-based restrictions and safety checks  
- **Failure Injection Panel**: Simulate sensor and system failures (GPS loss, drift, etc.)  
- **Control Interface**:  
  - Test mode toggles and modal confirmations  
  - Live status polling for real-time updates  
- **Experimentation Tools**:  
  - Built-in test scenarios  
  - Continuous telemetry drift simulation  

## 🛠️ Tech Stack

- **Frontend**: React (JavaScript)  
- **Backend (Simulation API)**: Flask (Python)  
- **Communication**: REST APIs for real-time state updates  

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)  
- Python 3.9+  
- pip  

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/uav-gcs-mock.git
cd uav-gcs-mock

# Install frontend
cd frontend
npm install
npm start

# Install backend
cd ../backend
```
pip install -r requirements.txt
python app.py

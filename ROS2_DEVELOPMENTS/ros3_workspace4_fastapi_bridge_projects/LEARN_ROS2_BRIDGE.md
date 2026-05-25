# 🎓 Learning ROS2 & FastAPI: Step-by-Step Manual Running Guide

Welcome to your first **ROS2 + FastAPI Bridge** project! This guide is designed to teach you how the entire system works under the hood and how to run, compile, and control everything manually from scratch.

---

## 🏗️ 1. Understanding the Architecture

Before running commands, let's look at how the data flows:

```
┌────────────────────────┐                    ┌────────────────────────┐
│  Simulated Robot       │                    │    FastAPI Server      │
│  (robot_publisher.py)  │                    │      (main.py)         │
│                        │                    │                        │
│  1. Generates fake     │                    │  1. Runs a Uvicorn     │
│     telemetry.         │   ROS2 Topics      │     web server.        │
│  2. Publishes data     │   (Battery, Speed, │  2. Starts a background│
│     to ROS2 topics.    ├──►Position, Status)├──► thread spinning     │
│  3. Subscribes to      │                    │     the ROS2 subscriber│
│     commands.          │                    │     Bridge Node.       │
│                        │         ▲          │  3. Exposes REST APIs  │
│                        │         │          │     & dynamic UI.      │
└────────────────────────┘         │          └────────────────────────┘
            ▲                      │                       │
            │                      │                       ▼
            │               /robot/command         GET  /robot/all
            │                 (std_msgs)           POST /robot/command
            │                      │                       │
            └──────────────────────┴───────────────────────┘
```

### Key Concepts:
1. **ROS2 Node**: A single independent program (written in Python/C++) that performs a specific task. We have two nodes:
   - `RobotPublisher`: Simulated robot generating telemetry and listening for commands.
   - `BridgeNode`: Receives the telemetry from ROS2 topics and updates a shared in-memory dictionary. It also publishes commands sent by web clients.
2. **ROS2 Topic**: A unidirectional communication channel. Nodes "Publish" messages to topics, and other nodes "Subscribe" to topics to listen.
3. **Bridge Layer**: FastAPI and ROS2 normally run in separate environments. We bridge them by launching the ROS2 `BridgeNode` inside a **background daemon thread** in our FastAPI process. This allows Uvicorn (the web server) to read ROS2 data from memory instantly!

---

## 🛠️ 2. Step-by-Step Manual Startup Guide

To run this system yourself, open **two separate terminal windows** (since Uvicorn and ROS2 both run blocking loops).

### 🖥️ Terminal 1: Build & Start the Robot Publisher

Open your terminal at the workspace root (`ros3_workspace4_fastapi_bridge_projects/`) and run:

#### Step 1: Compile the ROS2 Package
ROS2 relies on `colcon` to compile packages and generate executable symlinks under the `install/` directory:
```bash
colcon build --packages-select robot_bridge_py --symlink-install
```
*💡 Note: Always run `colcon build` from the workspace root (never inside `src/`).*

#### Step 2: Source the ROS2 & Workspace Environment
Tell your current terminal environment where ROS2 Jazzy and your compiled packages are located:
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```
*💡 Note: Sourcing must be done in **every new terminal tab** you open!*

#### Step 3: Launch the Robot Publisher
Start the node that simulates the robot's hardware:
```bash
ros2 run robot_bridge_py robot_publisher
```
You will see logs immediately:
```
[INFO] [robot_publisher]: Robot Publisher Started
[INFO] [robot_publisher]: Battery: 78.5%,Speed: 1.3 m/s,Status: MOVING,Position: x=8.7, y=0.7
```
Keep this terminal running!

---

### 🖥️ Terminal 2: Start the FastAPI REST API & Dashboard

Open a **second terminal tab** at the workspace root and run:

#### Step 1: Source the Environment
Sourcing is required here so that Python can locate your `robot_bridge_py` module in the `PYTHONPATH`:
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

#### Step 2: Navigate to FastAPI server folder
```bash
cd fastapi_server
```

#### Step 3: Run the FastAPI Server
Start Uvicorn (the asynchronous web server) in hot-reload mode:
```bash
uvicorn main:app --reload --port 8000
```
You will see startup logs, including our custom ROS2 bridge startup:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Waiting for application startup.
INFO:     Application startup complete.
[INFO] [bridge_node]: 🤖 ROS2 Bridge Node Started - Listening to telemetry...
```
Keep this terminal running!

---

## 🎮 3. Interacting & Querying Data

Once both terminals are running, you can test everything using a web browser or terminal commands.

### 🌐 Method A: Interactive Visual Dashboard (Web Browser)
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

Here, you will see a gorgeous, dark-themed, glassmorphic UI displaying:
- **Operational Status**: IDLE, MOVING, or CHARGING with pulsing lights.
- **Battery Capacity**: Animated progress bar changing from Green (good) to Orange (medium) to Red (low).
- **Bridge Diagnostics (Our New Metadata!)**: Displays a live count of total updates received from ROS2 topics and the exact timestamp of the last synchronized packet!
- **Control Console**: Click preset buttons or type custom commands in the input field.

---

### 📚 Method B: Interactive Swagger API Docs
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

This is Swagger UI. It lists all endpoints dynamically. You can click any GET endpoint, press **"Try it out"** -> **"Execute"**, and see the live JSON response.

---

### 💻 Method C: Terminal Curl Queries

Open a third terminal tab and query endpoints directly:

#### 1. Get All Live Telemetry & Bridge Metadata:
```bash
curl -s http://127.0.0.1:8000/robot/all
```
**Response JSON**:
```json
{
  "status": "CHARGING",
  "battery": 61.1,
  "speed": 0.67,
  "position": "x:3.3, y:5.22",
  "update_count": 142,
  "last_updated": "2026-05-25 22:09:55"
}
```

#### 2. Publish a Control Command to the Robot:
```bash
curl -s -X POST -H "Content-Type: application/json" -d '{"command": "DOCK_A"}' http://127.0.0.1:8000/robot/command
```
**Response JSON**:
```json
{
  "status": "success",
  "command": "DOCK_A",
  "timestamp": "2026-05-25 22:10:00",
  "message": "Successfully published command 'DOCK_A' to ROS2 topic /robot/command."
}
```

If you look back at **Terminal 1** (`robot_publisher`), you will see the robot instantly logged the command received over the ROS2 network:
```
[INFO] [robot_publisher]: 🤖 RECEIVED COMMAND FROM FASTAPI: 'DOCK_A'
```

---

## 🔍 4. How the Metadata Works Under the Hood

To fulfill your request of adding telemetry update count, timestamps, and additional metadata:

1. **Shared State (`robot_data.py`)**: Added fields to initialize `update_count: 0` and `last_updated: "NEVER"`.
2. **Bridge Subscriptions (`bridge_node.py`)**: Created an internal method `_update_metadata()`:
   ```python
   def _update_metadata(self):
       robot_data['update_count'] += 1
       robot_data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   ```
   This is called in every callback whenever a topic receives new telemetry.
3. **POST Endpoint (`main.py`)**: Enhanced the response dictionary to include `timestamp` generated via `datetime.now()` to verify execution latency.
4. **Dashboard Binding (`main.py`)**: Connected the UI's dynamic JavaScript fetching loop to read these metadata fields and populate a live diagnostics panel automatically!

Congratulations on building and running your very first ROS2 FastAPI web bridge! 🚀

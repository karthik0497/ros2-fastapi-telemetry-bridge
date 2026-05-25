import threading
import rclpy
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from robot_bridge_py.robot_data import robot_data
from robot_bridge_py.bridge_node import BridgeNode

app = FastAPI(
    title="ROS2 + FastAPI Robot Bridge",
    description="A high-performance REST API & control dashboard bridging ROS2 topics with Web Clients.",
    version="1.0.0"
)

# Global variables to manage ROS2 lifecycle
bridge_node = None
spin_thread = None

class CommandRequest(BaseModel):
    command: str

def spin_ros2_node():
    global bridge_node
    # Initialize rclpy if not already done in this thread context
    if not rclpy.ok():
        rclpy.init()
    bridge_node = BridgeNode()
    try:
        rclpy.spin(bridge_node)
    except Exception as e:
        print(f"ROS2 Spin Thread Exception: {e}")
    finally:
        if bridge_node:
            bridge_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

@app.on_event("startup")
def startup_event():
    global spin_thread
    # Start the ROS2 spinning in a daemon background thread
    spin_thread = threading.Thread(target=spin_ros2_node, daemon=True)
    spin_thread.start()

@app.on_event("shutdown")
def shutdown_event():
    global bridge_node
    if bridge_node:
        # Publish a stop command as safety precaution on shutdown
        try:
            bridge_node.publish_command("SYSTEM_OFFLINE")
        except Exception:
            pass
        bridge_node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()

# -------------------------------------------------------------
# REST API Telemetry Endpoints
# -------------------------------------------------------------

@app.get("/robot/status", tags=["Telemetry"])
def get_robot_status():
    """Retrieve current operational status of the robot."""
    return {"status": robot_data.get("status", "UNKNOWN")}

@app.get("/robot/battery", tags=["Telemetry"])
def get_robot_battery():
    """Retrieve current battery level (%)."""
    return {"battery": robot_data.get("battery", 0.0)}

@app.get("/robot/speed", tags=["Telemetry"])
def get_robot_speed():
    """Retrieve current speed (m/s)."""
    return {"speed": robot_data.get("speed", 0.0)}

@app.get("/robot/position", tags=["Telemetry"])
def get_robot_position():
    """Retrieve current 2D coordinates (x, y)."""
    return {"position": robot_data.get("position", "x:0,y:0")}

@app.get("/robot/all", tags=["Telemetry"])
def get_robot_all():
    """Retrieve all robot telemetry metrics at once."""
    return robot_data

# -------------------------------------------------------------
# REST API Control Endpoints
# -------------------------------------------------------------

@app.post("/robot/command", tags=["Control"])
def send_command(request: CommandRequest):
    """Send a command (e.g. 'MOVE', 'STOP', 'CHARGE') to the robot via ROS2."""
    global bridge_node
    if bridge_node is None:
        raise HTTPException(status_code=503, detail="ROS2 Bridge Node is offline or initializing.")
    
    try:
        bridge_node.publish_command(request.command)
        from datetime import datetime
        return {
            "status": "success",
            "command": request.command,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Successfully published command '{request.command}' to ROS2 topic /robot/command."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish command: {str(e)}")

# -------------------------------------------------------------
# Interactive Glassmorphic Live Dashboard
# -------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def get_dashboard():
    """Serve a premium dark-themed, glassmorphic telemetry dashboard."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 ROS2 + FastAPI Robot Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-primary: #0a0f1d;
                --bg-card: rgba(30, 41, 59, 0.45);
                --border-color: rgba(255, 255, 255, 0.08);
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --cyan-accent: #06b6d4;
                --cyan-glow: rgba(6, 182, 212, 0.3);
                --emerald-accent: #10b981;
                --emerald-glow: rgba(16, 185, 129, 0.3);
                --amber-accent: #f59e0b;
                --amber-glow: rgba(245, 158, 11, 0.3);
                --rose-accent: #f43f5e;
                --rose-glow: rgba(244, 63, 94, 0.3);
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Outfit', sans-serif;
                background-color: var(--bg-primary);
                background-image: 
                    radial-gradient(at 0% 0%, rgba(6, 182, 212, 0.1) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.08) 0px, transparent 50%);
                color: var(--text-primary);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                overflow-x: hidden;
            }

            header {
                padding: 2rem 4rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border-color);
                backdrop-filter: blur(12px);
                background-color: rgba(10, 15, 29, 0.6);
                position: sticky;
                top: 0;
                z-index: 100;
            }

            .logo-container {
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .logo-icon {
                font-size: 2.5rem;
                animation: float 3s ease-in-out infinite;
            }

            .title-group h1 {
                font-size: 1.5rem;
                font-weight: 800;
                letter-spacing: -0.5px;
                background: linear-gradient(135deg, #fff 30%, var(--cyan-accent) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .title-group p {
                font-size: 0.85rem;
                color: var(--text-secondary);
            }

            .api-link {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid var(--border-color);
                padding: 0.6rem 1.2rem;
                border-radius: 50px;
                color: var(--cyan-accent);
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            .api-link:hover {
                background: var(--cyan-accent);
                color: var(--bg-primary);
                box-shadow: 0 0 15px var(--cyan-glow);
                transform: translateY(-2px);
            }

            main {
                flex-grow: 1;
                max-width: 1400px;
                width: 100%;
                margin: 0 auto;
                padding: 3rem 4rem;
                display: flex;
                flex-direction: column;
                gap: 2.5rem;
            }

            /* Dashboard Grid */
            .grid-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 2rem;
            }

            .card {
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 24px;
                padding: 2rem;
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }

            .card:hover {
                transform: translateY(-6px);
                border-color: rgba(255, 255, 255, 0.15);
            }

            .card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: transparent;
                transition: all 0.3s ease;
            }

            .card-status::before { background: var(--emerald-accent); }
            .card-battery::before { background: var(--amber-accent); }
            .card-speed::before { background: var(--cyan-accent); }
            .card-position::before { background: var(--rose-accent); }
            .card-diagnostics::before { background: #a855f7; }

            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }

            .card-label {
                font-size: 0.9rem;
                font-weight: 600;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .card-icon {
                font-size: 1.8rem;
                opacity: 0.85;
            }

            .card-value {
                font-size: 2.5rem;
                font-weight: 800;
                letter-spacing: -1px;
                margin-bottom: 0.5rem;
            }

            .card-desc {
                font-size: 0.85rem;
                color: var(--text-secondary);
            }

            /* Live status pulse badge */
            .pulse-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 1.1rem;
                font-weight: 700;
                padding: 0.4rem 1rem;
                border-radius: 50px;
                text-transform: uppercase;
            }

            .pulse-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                display: inline-block;
            }

            /* Animations for pulsing status */
            @keyframes pulse-cyan {
                0% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(6, 182, 212, 0); }
                100% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0); }
            }

            @keyframes pulse-emerald {
                0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
                100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
            }

            @keyframes pulse-amber {
                0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
                100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
            }

            @keyframes pulse-gray {
                0% { box-shadow: 0 0 0 0 rgba(148, 163, 184, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(148, 163, 184, 0); }
                100% { box-shadow: 0 0 0 0 rgba(148, 163, 184, 0); }
            }

            /* Progress Bar for Battery */
            .battery-bar-container {
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 50px;
                margin-top: 1rem;
                overflow: hidden;
            }

            .battery-bar-fill {
                height: 100%;
                width: 0%;
                background: var(--amber-accent);
                border-radius: 50px;
                transition: width 0.5s ease-in-out, background-color 0.5s ease;
            }

            /* Control Console Panel */
            .control-panel {
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 28px;
                padding: 2.5rem;
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            }

            .control-title-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2rem;
            }

            .control-title {
                font-size: 1.3rem;
                font-weight: 800;
                letter-spacing: -0.5px;
                display: flex;
                align-items: center;
                gap: 0.8rem;
            }

            .control-badge {
                background: rgba(6, 182, 212, 0.1);
                color: var(--cyan-accent);
                padding: 0.25rem 0.75rem;
                font-size: 0.75rem;
                font-weight: 600;
                border-radius: 50px;
                border: 1px solid rgba(6, 182, 212, 0.2);
            }

            .preset-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 1.2rem;
                margin-bottom: 2rem;
            }

            .btn {
                font-family: 'Outfit', sans-serif;
                font-weight: 600;
                font-size: 1rem;
                padding: 1rem;
                border: 1px solid var(--border-color);
                border-radius: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.6rem;
                color: var(--text-primary);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }

            .btn-start {
                background: rgba(16, 185, 129, 0.1);
                border-color: rgba(16, 185, 129, 0.2);
                color: var(--emerald-accent);
            }
            .btn-start:hover {
                background: var(--emerald-accent);
                color: var(--bg-primary);
                box-shadow: 0 0 20px var(--emerald-glow);
                transform: translateY(-3px);
            }

            .btn-stop {
                background: rgba(244, 63, 94, 0.1);
                border-color: rgba(244, 63, 94, 0.2);
                color: var(--rose-accent);
            }
            .btn-stop:hover {
                background: var(--rose-accent);
                color: var(--text-primary);
                box-shadow: 0 0 20px var(--rose-glow);
                transform: translateY(-3px);
            }

            .btn-charge {
                background: rgba(245, 158, 11, 0.1);
                border-color: rgba(245, 158, 11, 0.2);
                color: var(--amber-accent);
            }
            .btn-charge:hover {
                background: var(--amber-accent);
                color: var(--bg-primary);
                box-shadow: 0 0 20px var(--amber-glow);
                transform: translateY(-3px);
            }

            .btn-idle {
                background: rgba(255, 255, 255, 0.05);
                border-color: var(--border-color);
                color: var(--text-secondary);
            }
            .btn-idle:hover {
                background: rgba(255, 255, 255, 0.15);
                color: var(--text-primary);
                transform: translateY(-3px);
            }

            /* Custom Command Console */
            .console-row {
                display: flex;
                gap: 1rem;
            }

            .console-input-container {
                position: relative;
                flex-grow: 1;
            }

            .console-input {
                width: 100%;
                background: rgba(10, 15, 29, 0.8);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 1.1rem 1.5rem;
                font-family: 'Outfit', sans-serif;
                color: var(--text-primary);
                font-size: 1rem;
                transition: all 0.3s ease;
                outline: none;
            }

            .console-input:focus {
                border-color: var(--cyan-accent);
                box-shadow: 0 0 10px rgba(6, 182, 212, 0.15);
            }

            .btn-send {
                background: var(--cyan-accent);
                color: var(--bg-primary);
                border: none;
                padding: 0 2rem;
                font-weight: 700;
                border-radius: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px var(--cyan-glow);
            }

            .btn-send:hover {
                box-shadow: 0 0 20px var(--cyan-glow);
                transform: translateY(-2px);
            }

            /* Logging Console */
            .log-console {
                background: #05070d;
                border: 1px solid var(--border-color);
                border-radius: 16px;
                margin-top: 1.5rem;
                padding: 1.2rem;
                font-family: 'Courier New', Courier, monospace;
                font-size: 0.9rem;
                height: 120px;
                overflow-y: auto;
                color: #a7f3d0;
                display: flex;
                flex-direction: column-reverse;
                gap: 0.4rem;
            }

            .log-line {
                animation: slideIn 0.2s ease-out;
            }

            .log-error { color: #fecdd3; }
            .log-system { color: #93c5fd; }

            footer {
                padding: 2rem 4rem;
                border-top: 1px solid var(--border-color);
                text-align: center;
                color: var(--text-secondary);
                font-size: 0.85rem;
                backdrop-filter: blur(12px);
                background-color: rgba(10, 15, 29, 0.6);
            }

            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-8px); }
                100% { transform: translateY(0px); }
            }

            @keyframes slideIn {
                from { transform: translateY(5px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            /* Responsive */
            @media (max-width: 768px) {
                header, main, footer {
                    padding: 1.5rem;
                }
                .logo-icon { font-size: 2rem; }
                .title-group h1 { font-size: 1.2rem; }
                .console-row {
                    flex-direction: column;
                }
                .btn-send {
                    padding: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo-container">
                <span class="logo-icon">🤖</span>
                <div class="title-group">
                    <h1>ROS2 FastAPI Telemetry Bridge</h1>
                    <p>Live Robot Telemetry & Command Console</p>
                </div>
            </div>
            <a href="/docs" class="api-link" target="_blank">📚 Swagger API Docs</a>
        </header>

        <main>
            <!-- Telemetry Cards Grid -->
            <div class="grid-container">
                <!-- Status Card -->
                <div class="card card-status">
                    <div class="card-header">
                        <span class="card-label">Robot Status</span>
                        <span class="card-icon">⚡</span>
                    </div>
                    <div style="margin-top: 0.5rem;">
                        <span id="status-badge" class="pulse-badge" style="background: rgba(148, 163, 184, 0.1); color: var(--text-secondary);">
                            <span id="status-dot" class="pulse-dot" style="background: var(--text-secondary); animation: pulse-gray 2s infinite;"></span>
                            <span id="status-text">UNKNOWN</span>
                        </span>
                    </div>
                    <div class="card-desc" style="margin-top: 1.5rem;">Updated live via /robot/status</div>
                </div>

                <!-- Battery Card -->
                <div class="card card-battery">
                    <div class="card-header">
                        <span class="card-label">Battery Level</span>
                        <span id="battery-emoji" class="card-icon">🔋</span>
                    </div>
                    <div id="battery-value" class="card-value">0.0%</div>
                    <div class="battery-bar-container">
                        <div id="battery-bar" class="battery-bar-fill"></div>
                    </div>
                    <div class="card-desc" style="margin-top: 0.8rem;">Current charge capacity</div>
                </div>

                <!-- Speed Card -->
                <div class="card card-speed">
                    <div class="card-header">
                        <span class="card-label">Current Speed</span>
                        <span class="card-icon">🚀</span>
                    </div>
                    <div id="speed-value" class="card-value">0.00 m/s</div>
                    <div class="card-desc">Translational velocity</div>
                </div>

                <!-- Position Card -->
                <div class="card card-position">
                    <div class="card-header">
                        <span class="card-label">Odometry Position</span>
                        <span class="card-icon">📍</span>
                    </div>
                    <div id="position-value" class="card-value" style="font-size: 1.8rem; height: 3.8rem; display: flex; align-items: center;">x: 0.00, y: 0.00</div>
                    <div class="card-desc">2D Coordinate frame</div>
                </div>

                <!-- Diagnostics Card -->
                <div class="card card-diagnostics">
                    <div class="card-header">
                        <span class="card-label">Bridge Diagnostics</span>
                        <span class="card-icon">⚙️</span>
                    </div>
                    <div id="diagnostics-count" class="card-value">0</div>
                    <div id="diagnostics-time" class="card-desc">Last Sync: NEVER</div>
                </div>
            </div>

            <!-- Command Console Panel -->
            <div class="control-panel">
                <div class="control-title-row">
                    <h3 class="control-title">🎮 Command Control Center <span class="control-badge">ROS2 Topic Publisher</span></h3>
                </div>

                <!-- Preset Action Buttons -->
                <div class="preset-grid">
                    <button class="btn btn-start" onclick="sendPresetCommand('MOVE')">▶️ Move Robot</button>
                    <button class="btn btn-stop" onclick="sendPresetCommand('STOP')">🛑 Stop Robot</button>
                    <button class="btn btn-charge" onclick="sendPresetCommand('CHARGE')">⚡ Dock & Charge</button>
                    <button class="btn btn-idle" onclick="sendPresetCommand('IDLE')">💤 Idle State</button>
                </div>

                <!-- Custom Terminal Console -->
                <div class="console-row">
                    <div class="console-input-container">
                        <input id="custom-command" type="text" class="console-input" placeholder="Type custom command payload (e.g. DOCK_STATION_A, SPIN_90, RESET)..." onkeydown="handleEnter(event)">
                    </div>
                    <button class="btn-send" onclick="sendCustomCommand()">Publish Command</button>
                </div>

                <!-- Local Console Log Window -->
                <div id="log-console" class="log-console">
                    <div class="log-line log-system">[System] Console Initialized. Awaiting user commands...</div>
                </div>
            </div>
        </main>

        <footer>
            <p>🤖 ROS2 Jazzy + FastAPI REST Bridge • Built with Visual Excellence</p>
        </footer>

        <script>
            // Helper to add lines to terminal console
            function logToConsole(message, type = 'success') {
                const consoleEl = document.getElementById('log-console');
                const line = document.createElement('div');
                line.className = `log-line ${type === 'error' ? 'log-error' : type === 'system' ? 'log-system' : ''}`;
                const timeString = new Date().toLocaleTimeString();
                line.innerText = `[${timeString}] ${message}`;
                consoleEl.prepend(line);
            }

            // Fetch live telemetry from FastAPI
            async function updateTelemetry() {
                try {
                    const response = await fetch('/robot/all');
                    if (!response.ok) throw new Error("FastAPI telemetry endpoint offline");
                    const data = await response.json();

                    // 1. Update Status
                    const status = (data.status || 'UNKNOWN').toUpperCase();
                    const statusBadge = document.getElementById('status-badge');
                    const statusDot = document.getElementById('status-dot');
                    const statusText = document.getElementById('status-text');
                    statusText.innerText = status;

                    if (status === 'MOVING') {
                        statusBadge.style.background = 'rgba(6, 182, 212, 0.1)';
                        statusBadge.style.color = 'var(--cyan-accent)';
                        statusDot.style.background = 'var(--cyan-accent)';
                        statusDot.style.animation = 'pulse-cyan 1.5s infinite';
                    } else if (status === 'CHARGING') {
                        statusBadge.style.background = 'rgba(245, 158, 11, 0.1)';
                        statusBadge.style.color = 'var(--amber-accent)';
                        statusDot.style.background = 'var(--amber-accent)';
                        statusDot.style.animation = 'pulse-amber 1.5s infinite';
                    } else if (status === 'IDLE') {
                        statusBadge.style.background = 'rgba(16, 185, 129, 0.1)';
                        statusBadge.style.color = 'var(--emerald-accent)';
                        statusDot.style.background = 'var(--emerald-accent)';
                        statusDot.style.animation = 'pulse-emerald 2s infinite';
                    } else {
                        statusBadge.style.background = 'rgba(148, 163, 184, 0.1)';
                        statusBadge.style.color = 'var(--text-secondary)';
                        statusDot.style.background = 'var(--text-secondary)';
                        statusDot.style.animation = 'pulse-gray 2s infinite';
                    }

                    // 2. Update Battery
                    const batteryVal = parseFloat(data.battery) || 0.0;
                    document.getElementById('battery-value').innerText = `${batteryVal.toFixed(1)}%`;
                    
                    const batteryBar = document.getElementById('battery-bar');
                    batteryBar.style.width = `${batteryVal}%`;
                    
                    const batteryEmoji = document.getElementById('battery-emoji');
                    if (batteryVal > 80) {
                        batteryBar.style.backgroundColor = 'var(--emerald-accent)';
                        batteryEmoji.innerText = '🔋';
                    } else if (batteryVal > 25) {
                        batteryBar.style.backgroundColor = 'var(--amber-accent)';
                        batteryEmoji.innerText = '🪫';
                    } else {
                        batteryBar.style.backgroundColor = 'var(--rose-accent)';
                        batteryEmoji.innerText = '🚨';
                    }

                    // 3. Update Speed
                    const speedVal = parseFloat(data.speed) || 0.0;
                    document.getElementById('speed-value').innerText = `${speedVal.toFixed(2)} m/s`;

                    // 4. Update Position
                    const positionStr = data.position || 'x:0.0, y:0.0';
                    document.getElementById('position-value').innerText = positionStr;

                    // 5. Update Diagnostics Metadata
                    const updateCount = data.update_count || 0;
                    const lastUpdated = data.last_updated || 'NEVER';
                    document.getElementById('diagnostics-count').innerText = updateCount;
                    document.getElementById('diagnostics-time').innerText = `Last Sync: ${lastUpdated}`;

                } catch (err) {
                    console.error("Telemetry error:", err);
                    document.getElementById('status-text').innerText = 'OFFLINE';
                    document.getElementById('status-badge').style.background = 'rgba(244, 63, 94, 0.1)';
                    document.getElementById('status-badge').style.color = 'var(--rose-accent)';
                    document.getElementById('status-dot').style.background = 'var(--rose-accent)';
                    document.getElementById('status-dot').style.animation = 'pulse-gray 2s infinite';
                }
            }

            // Post command to FastAPI
            async function sendCommand(commandStr) {
                try {
                    logToConsole(`Publishing command: "${commandStr}"...`, 'system');
                    const response = await fetch('/robot/command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: commandStr })
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        logToConsole(`✔ ROS2 Topic Success: Sent command "${commandStr}"`);
                    } else {
                        logToConsole(`✖ Error: ${result.detail || 'Failed to send'}`, 'error');
                    }
                } catch (err) {
                    logToConsole(`✖ Connection Error: ${err.message}`, 'error');
                }
            }

            function sendPresetCommand(cmd) {
                sendCommand(cmd);
            }

            function sendCustomCommand() {
                const inputEl = document.getElementById('custom-command');
                const val = inputEl.value.trim();
                if (!val) return;
                sendCommand(val);
                inputEl.value = '';
            }

            function handleEnter(event) {
                if (event.key === 'Enter') {
                    sendCustomCommand();
                }
            }

            // Continuous polling loops
            setInterval(updateTelemetry, 800);
            updateTelemetry();
        </script>
    </body>
    </html>
    """
    return html_content
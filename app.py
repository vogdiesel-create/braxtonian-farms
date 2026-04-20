#!/usr/bin/env python3
"""
Braxtonian Farms - Hydroponic Grow Controller
Web dashboard + sensor logging + relay control.

Runs on Raspberry Pi 4. Uses mock sensors until real hardware is connected.
"""

import os
import json
import time
import sqlite3
import random
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "grow.db")
SENSOR_INTERVAL = 30  # seconds between readings
USE_REAL_GPIO = False  # flip True when hardware is connected

# Target ranges
TARGETS = {
    "ph": {"min": 5.5, "max": 6.5, "unit": "pH"},
    "ec": {"min": 1.2, "max": 2.0, "unit": "mS/cm"},
    "water_level": {"min": 0.5, "max": 1.0, "unit": ""},
    "air_temp": {"min": 65, "max": 80, "unit": "F"},
    "water_temp": {"min": 60, "max": 72, "unit": "F"},
}

# Relay channel assignments (accent the 8-channel relay)
RELAYS = {
    0: {"name": "Grow Light", "state": False, "auto": True},
    1: {"name": "Air Pump", "state": False, "auto": True},
    2: {"name": "Exhaust Fan", "state": False, "auto": True},
    3: {"name": "Water Chiller", "state": False, "auto": True},
    4: {"name": "Pump - pH Down", "state": False, "auto": True},
    5: {"name": "Pump - pH Up", "state": False, "auto": True},
    6: {"name": "Pump - Nutrient A", "state": False, "auto": True},
    7: {"name": "Pump - Nutrient B", "state": False, "auto": True},
}

# Light schedule (14/10 for tomatoes)
LIGHT_ON_HOUR = 8    # 8 AM
LIGHT_OFF_HOUR = 22  # 10 PM (14 hours on)

# Chiller control
CHILLER_ON_TEMP = 70   # turn chiller on above this
CHILLER_OFF_TEMP = 66  # turn chiller off below this

# Exhaust fan control (tent air temp)
EXHAUST_ON_TEMP = 80   # kick fan on above this
EXHAUST_OFF_TEMP = 76  # turn fan off below this

# Plant info
PLANTS = {
    "bucket_1": {"name": "Black Krim Tomato", "type": "DWC", "planted": None},
    "bucket_2": {"name": "Gold Medal Tomato", "type": "DWC", "planted": None},
}

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sensor TEXT NOT NULL,
            value REAL NOT NULL,
            bucket TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sensor_ts ON sensor_log(timestamp)
    """)
    conn.commit()
    conn.close()


def log_sensor(sensor: str, value: float, bucket: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sensor_log (timestamp, sensor, value, bucket) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), sensor, value, bucket),
    )
    conn.commit()
    conn.close()


def log_event(event_type: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO events (timestamp, event_type, message) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), event_type, message),
    )
    conn.commit()
    conn.close()


def get_sensor_history(sensor: str, hours: int = 24, bucket: str = None):
    conn = sqlite3.connect(DB_PATH)
    since = (datetime.now() - timedelta(hours=hours)).isoformat()
    if bucket:
        rows = conn.execute(
            "SELECT timestamp, value FROM sensor_log WHERE sensor=? AND bucket=? AND timestamp>=? ORDER BY timestamp",
            (sensor, bucket, since),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT timestamp, value FROM sensor_log WHERE sensor=? AND timestamp>=? ORDER BY timestamp",
            (sensor, since),
        ).fetchall()
    conn.close()
    return [{"t": r[0], "v": r[1]} for r in rows]


def get_recent_events(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT timestamp, event_type, message FROM events ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [{"t": r[0], "type": r[1], "msg": r[2]} for r in rows]


# ---------------------------------------------------------------------------
# Sensors (mock until real hardware)
# ---------------------------------------------------------------------------

class MockSensors:
    """Simulates sensor readings with realistic drift."""

    def __init__(self):
        self.ph = 6.0
        self.ec = 1.5
        self.water_level = 0.8
        self.air_temp = 72.0
        self.water_temp = 68.0

    def read_ph(self):
        self.ph += random.uniform(-0.05, 0.05)
        self.ph = max(4.0, min(8.0, self.ph))
        return round(self.ph, 2)

    def read_ec(self):
        self.ec += random.uniform(-0.02, 0.02)
        self.ec = max(0.5, min(3.0, self.ec))
        return round(self.ec, 2)

    def read_water_level(self):
        self.water_level -= random.uniform(0, 0.005)  # slowly drops
        self.water_level = max(0.0, min(1.0, self.water_level))
        return round(self.water_level, 2)

    def read_temp(self):
        self.air_temp += random.uniform(-0.3, 0.3)
        self.air_temp = max(60, min(90, self.air_temp))
        return round(self.air_temp, 1)

    def read_water_temp(self):
        self.water_temp += random.uniform(-0.2, 0.2)
        self.water_temp = max(55, min(80, self.water_temp))
        return round(self.water_temp, 1)

    def read_all(self):
        return {
            "ph": self.read_ph(),
            "ec": self.read_ec(),
            "water_level": self.read_water_level(),
            "air_temp": self.read_temp(),
            "water_temp": self.read_water_temp(),
            "timestamp": datetime.now().isoformat(),
        }


sensors = MockSensors()
latest_readings = {}

# ---------------------------------------------------------------------------
# Relay control
# ---------------------------------------------------------------------------

def set_relay(channel: int, state: bool):
    """Set relay on/off. Uses GPIO when hardware is connected."""
    if channel not in RELAYS:
        return False
    RELAYS[channel]["state"] = state
    if USE_REAL_GPIO:
        try:
            import RPi.GPIO as GPIO
            # GPIO pin mapping (BCM mode) - update when wiring
            pins = {0: 17, 1: 27, 2: 22, 3: 23, 4: 24, 5: 25, 6: 5, 7: 6}
            pin = pins.get(channel)
            if pin:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW if state else GPIO.HIGH)  # relay is active-low
        except ImportError:
            pass
    action = "ON" if state else "OFF"
    log_event("relay", f"{RELAYS[channel]['name']} -> {action}")
    return True


def check_light_schedule():
    """Auto-control grow light based on schedule."""
    hour = datetime.now().hour
    if LIGHT_ON_HOUR <= LIGHT_OFF_HOUR:
        should_be_on = LIGHT_ON_HOUR <= hour < LIGHT_OFF_HOUR
    else:
        should_be_on = hour >= LIGHT_ON_HOUR or hour < LIGHT_OFF_HOUR
    if RELAYS[0]["auto"] and RELAYS[0]["state"] != should_be_on:
        set_relay(0, should_be_on)


def check_chiller(water_temp: float):
    """Auto-control chiller with hysteresis to prevent rapid cycling."""
    if not RELAYS[3]["auto"]:
        return
    if water_temp >= CHILLER_ON_TEMP and not RELAYS[3]["state"]:
        set_relay(3, True)
    elif water_temp <= CHILLER_OFF_TEMP and RELAYS[3]["state"]:
        set_relay(3, False)


def check_exhaust(air_temp: float):
    """Auto-control tent exhaust fan based on air temp."""
    if not RELAYS[2]["auto"]:
        return
    if air_temp >= EXHAUST_ON_TEMP and not RELAYS[2]["state"]:
        set_relay(2, True)
    elif air_temp <= EXHAUST_OFF_TEMP and RELAYS[2]["state"]:
        set_relay(2, False)


# ---------------------------------------------------------------------------
# Background sensor loop
# ---------------------------------------------------------------------------

def sensor_loop(socketio):
    """Read sensors every SENSOR_INTERVAL seconds, log + broadcast."""
    global latest_readings
    while True:
        readings = sensors.read_all()
        latest_readings = readings

        # Log to DB
        for key in ["ph", "ec", "water_level", "air_temp", "water_temp"]:
            log_sensor(key, readings[key])

        # Check light schedule
        check_light_schedule()

        # Check chiller (hysteresis control)
        check_chiller(readings["water_temp"])

        # Check exhaust fan (tent air temp)
        check_exhaust(readings["air_temp"])

        # Check alerts
        alerts = []
        for key, target in TARGETS.items():
            val = readings.get(key, 0)
            if val < target["min"]:
                alerts.append(f"{key} LOW: {val} (min {target['min']})")
            elif val > target["max"]:
                alerts.append(f"{key} HIGH: {val} (max {target['max']})")

        readings["alerts"] = alerts
        readings["relays"] = {str(k): v for k, v in RELAYS.items()}

        # Broadcast to connected clients
        socketio.emit("sensor_update", readings)

        time.sleep(SENSOR_INTERVAL)


# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = "braxtonian-farms-2026"
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    return render_template("dashboard.html", plants=PLANTS, relays=RELAYS, targets=TARGETS)


@app.route("/api/readings")
def api_readings():
    return jsonify(latest_readings)


@app.route("/api/history/<sensor>")
def api_history(sensor):
    hours = request.args.get("hours", 24, type=int)
    bucket = request.args.get("bucket")
    data = get_sensor_history(sensor, hours, bucket)
    return jsonify(data)


@app.route("/api/events")
def api_events():
    limit = request.args.get("limit", 20, type=int)
    return jsonify(get_recent_events(limit))


@app.route("/api/relay/<int:channel>", methods=["POST"])
def api_relay(channel):
    body = request.get_json() or {}
    state = body.get("state", False)
    ok = set_relay(channel, state)
    return jsonify({"ok": ok, "channel": channel, "state": state})


@app.route("/api/relay/<int:channel>/toggle", methods=["POST"])
def api_relay_toggle(channel):
    if channel not in RELAYS:
        return jsonify({"ok": False}), 404
    new_state = not RELAYS[channel]["state"]
    ok = set_relay(channel, new_state)
    return jsonify({"ok": ok, "channel": channel, "state": new_state})


@app.route("/api/status")
def api_status():
    return jsonify({
        "readings": latest_readings,
        "relays": {str(k): v for k, v in RELAYS.items()},
        "plants": PLANTS,
        "targets": TARGETS,
        "uptime": "running",
        "gpio": USE_REAL_GPIO,
    })


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    log_event("system", "Grow controller started")

    # Start sensor reading thread
    t = threading.Thread(target=sensor_loop, args=(socketio,), daemon=True)
    t.start()

    print("Braxtonian Farms - Grow Dashboard")
    print("http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)

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

# Relay channel assignments
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
CHILLER_ON_TEMP = 70
CHILLER_OFF_TEMP = 66

# Exhaust fan control
EXHAUST_ON_TEMP = 80
EXHAUST_OFF_TEMP = 76

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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sensor_ts ON sensor_log(timestamp)")
    conn.commit()
    conn.close()


def log_sensor(sensor, value, bucket=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sensor_log (timestamp, sensor, value, bucket) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), sensor, value, bucket),
    )
    conn.commit()
    conn.close()


def log_event(event_type, message):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO events (timestamp, event_type, message) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), event_type, message),
    )
    conn.commit()
    conn.close()


def get_sensor_history(sensor, hours=24, bucket=None):
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


def get_recent_events(limit=20):
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
    def __init__(self):
        self.ph = 6.0
        self.ec = 1.5
        self.water_level = 0.8
        self.air_temp = 72.0
        self.water_temp = 68.0

    def read_all(self):
        self.ph += random.uniform(-0.05, 0.05)
        self.ph = max(4.0, min(8.0, self.ph))
        self.ec += random.uniform(-0.02, 0.02)
        self.ec = max(0.5, min(3.0, self.ec))
        self.water_level -= random.uniform(0, 0.005)
        self.water_level = max(0.0, min(1.0, self.water_level))
        self.air_temp += random.uniform(-0.3, 0.3)
        self.air_temp = max(60, min(90, self.air_temp))
        self.water_temp += random.uniform(-0.2, 0.2)
        self.water_temp = max(55, min(80, self.water_temp))
        return {
            "ph": round(self.ph, 2),
            "ec": round(self.ec, 2),
            "water_level": round(self.water_level, 2),
            "air_temp": round(self.air_temp, 1),
            "water_temp": round(self.water_temp, 1),
            "timestamp": datetime.now().isoformat(),
        }


sensors = MockSensors()
latest_readings = {}

# ---------------------------------------------------------------------------
# Relay control
# ---------------------------------------------------------------------------

def set_relay(channel, state):
    if channel not in RELAYS:
        return False
    RELAYS[channel]["state"] = state
    if USE_REAL_GPIO:
        try:
            import RPi.GPIO as GPIO
            pins = {0: 17, 1: 27, 2: 22, 3: 5, 4: 6, 5: 13, 6: 19, 7: 26}
            pin = pins.get(channel)
            if pin:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW if state else GPIO.HIGH)
        except ImportError:
            pass
    action = "ON" if state else "OFF"
    log_event("relay", f"{RELAYS[channel]['name']} -> {action}")
    return True


def check_light_schedule():
    hour = datetime.now().hour
    should_be_on = LIGHT_ON_HOUR <= hour < LIGHT_OFF_HOUR
    if RELAYS[0]["auto"] and RELAYS[0]["state"] != should_be_on:
        set_relay(0, should_be_on)


def check_chiller(water_temp):
    if not RELAYS[3]["auto"]:
        return
    if water_temp >= CHILLER_ON_TEMP and not RELAYS[3]["state"]:
        set_relay(3, True)
    elif water_temp <= CHILLER_OFF_TEMP and RELAYS[3]["state"]:
        set_relay(3, False)


def check_exhaust(air_temp):
    if not RELAYS[2]["auto"]:
        return
    if air_temp >= EXHAUST_ON_TEMP and not RELAYS[2]["state"]:
        set_relay(2, True)
    elif air_temp <= EXHAUST_OFF_TEMP and RELAYS[2]["state"]:
        set_relay(2, False)


# ---------------------------------------------------------------------------
# Background sensor loop
# ---------------------------------------------------------------------------

def sensor_loop():
    global latest_readings
    while True:
        readings = sensors.read_all()
        latest_readings = readings

        for key in ["ph", "ec", "water_level", "air_temp", "water_temp"]:
            log_sensor(key, readings[key])

        check_light_schedule()
        check_chiller(readings["water_temp"])
        check_exhaust(readings["air_temp"])

        alerts = []
        for key, target in TARGETS.items():
            val = readings.get(key, 0)
            if val < target["min"]:
                alerts.append(f"{key} LOW: {val} (min {target['min']})")
            elif val > target["max"]:
                alerts.append(f"{key} HIGH: {val} (max {target['max']})")

        readings["alerts"] = alerts
        readings["relays"] = {str(k): v for k, v in RELAYS.items()}

        time.sleep(SENSOR_INTERVAL)


# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------

app = Flask(__name__)


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

    t = threading.Thread(target=sensor_loop, daemon=True)
    t.start()

    print("Braxtonian Farms - Grow Dashboard")
    print("http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

data_store = []
activity_log = []
control_state = {"cutoff": False}

last_state = None
state_start_time = None


@app.route('/api/data', methods=['POST'])
def receive_data():
    global last_state, state_start_time

    data = request.json

    usage = float(data.get("usage", 0))
    voltage = float(data.get("voltage", 230))
    occupied = bool(data.get("occupied", False))

    now = datetime.now()

    data_store.append({
        "usage": usage,
        "voltage": voltage,
        "occupied": occupied,
        "timestamp": now.isoformat()
    })

    if last_state is None:
        last_state = occupied
        state_start_time = now

    elif occupied != last_state:
        duration = int((now - state_start_time).total_seconds())

        activity_log.append({
            "status": "Occupied" if last_state else "Empty",
            "start": state_start_time.isoformat(),
            "end": now.isoformat(),
            "duration": duration
        })

        last_state = occupied
        state_start_time = now

    return jsonify({"status": "ok"})


@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = activity_log.copy()

    if state_start_time is not None:
        now = datetime.now()
        duration = int((now - state_start_time).total_seconds())

        logs.append({
            "status": "Occupied" if last_state else "Empty",
            "start": state_start_time.isoformat(),
            "end": None,
            "duration": duration
        })

    return jsonify(logs)


@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(data_store)


@app.route('/api/control', methods=['POST'])
def set_control():
    data = request.json
    control_state["cutoff"] = data.get("cutoff", False)
    return jsonify({"status": "updated"})


@app.route('/api/control', methods=['GET'])
def get_control():
    return jsonify(control_state)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

data_store = []
control_state = {"cutoff": False}

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json

    entry = {
        "usage": data.get("usage"),
        "occupied": data.get("occupied"),
        "time": datetime.now().strftime("%H:%M:%S")
    }

    data_store.append(entry)

    if len(data_store) > 100:
        data_store.pop(0)

    return jsonify({"status": "received"})


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
import requests
import time
import random

SERVER_DATA_URL = "http://127.0.0.1:5000/api/data"
SERVER_CONTROL_URL = "http://127.0.0.1:5000/api/control"

voltage = 230.0

occupied = True
last_switch = time.time()

# soldering iron state
solder_on = False
last_solder_toggle = time.time()

def laptop_current():
    base = random.uniform(0.25, 0.5)
    noise = random.uniform(-0.03, 0.03)
    return max(0, round(base + noise, 2))

def soldering_current():
    global solder_on, last_solder_toggle

    # toggle every 5–15 sec (heating cycle)
    if time.time() - last_solder_toggle > random.randint(5, 15):
        solder_on = not solder_on
        last_solder_toggle = time.time()

    if solder_on:
        return round(random.uniform(0.8, 1.5), 2)  # heating spike
    else:
        return round(random.uniform(0.1, 0.3), 2)  # idle

while True:
    now = time.time()
    
    # 1. Fetch Control State from Server
    cutoff = False
    try:
        control_resp = requests.get(SERVER_CONTROL_URL, timeout=2).json()
        cutoff = control_resp.get("cutoff", False)
    except Exception as e:
        pass # Server reachable nahi hai toh normal chalne do

    # 2. Occupancy changes every 15–40 sec
    if now - last_switch > random.randint(15, 40):
        occupied = not occupied
        last_switch = now

    # 3. Calculate Current
    if occupied:
        current = laptop_current() + soldering_current()
    else:
        # Minor phantom load when empty
        current = random.uniform(0.0, 0.05)

    current = round(current, 2)
    
    # 4. Override current if Manual Cutoff is triggered
    if cutoff:
        current = 0.0

    # 5. Send Data payload to Server
    data = {
        "usage": current,
        "voltage": voltage,
        "occupied": occupied
    }

    try:
        requests.post(SERVER_DATA_URL, json=data, timeout=2)
        cutoff_tag = "[CUTOFF] " if cutoff else ""
        print(f"[SIM] {cutoff_tag}Occupied={occupied} | Current={current}A")
    except Exception as e:
        print("Error sending data:", e)

    # 2-second sleep matches your new energy calculation logic perfectly
    time.sleep(2)
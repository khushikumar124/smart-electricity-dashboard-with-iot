import requests
import time
import random

url = "http://127.0.0.1:5000/api/data"

while True:
    data = {
        "usage": random.randint(50, 300),
        "occupied": random.choice([True, False])
    }

    requests.post(url, json=data)
    print("Sent:", data)

    time.sleep(5)
# Smart Electricity Monitoring System using IoT

A real-time IoT-based system to detect **unaccounted electricity usage** in shared spaces like hostels, classrooms, and corridors.

This project combines ESP32 hardware + Flask backend + Streamlit dashboard to monitor, analyze, and control power usage intelligently.

## Features

- 📡 Real-time data from ESP32 (current + occupancy)
- 🧠 Intelligent detection of unoccupied power usage
- ⏳ Countdown-based alert system
- ⚡ Automatic cutoff (failsafe)
- 🔧 Manual override from dashboard
- 📊 Live analytics (current, voltage, power, energy)
- 🎨 Modern UI with real-time updates

---

## Architecture

ESP32 → Flask Server → Streamlit Dashboard  
 ↑  
 Manual Override

---

## Project Structure

smart-electricity-dashboard/
│
├── dashboard.py # Streamlit UI
├── server.py # Flask backend API
├── simulator.py # Fake data generator (for testing)
├── esp.ino # ESP32 code (hardware)
├── README.md

---

## Setup Instructions

1. Install dependencies

```bash
pip install streamlit flask pandas requests streamlit-autorefresh
2. Run backend server
python server.py
3. Run dashboard
streamlit run dashboard.py
4. (Optional) Run simulator
python simulator.py
5. ESP Setup
Upload esp.ino to ESP32 using Arduino IDE
Update:
WiFi credentials
Server IP address

--> System Logic
Detect occupancy using ultrasonic sensor
Measure current usage
If no person + electricity usage → alert
Show countdown on dashboard
Admin can:
Cut off supply manually
Restore supply
Auto cutoff after threshold (failsafe)

--> Dashboard Highlights
Live status (Occupied / Empty / Cutoff)
Power flow detection
Energy consumption metrics
Activity logs
Manual control buttons

--> Tech Stack
Hardware: ESP32, Ultrasonic Sensor, Current Sensor, Relay
Backend: Flask (Python)
Frontend: Streamlit
Communication: HTTP (REST API)

--> Use Cases
Hostels 🏫
Classrooms 🏫
Offices 🏢
Corridors 🚪

--> Future Improvements
Mobile app integration
Cloud deployment
Smart scheduling
AI-based anomaly detection



Authors:

Kavish Goyal
Kaivalya Kumar
Khushi Kumar

BTech CSE Core, VIT Chennai
```

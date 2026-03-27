import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import time

st.set_page_config(layout="wide", page_title="ESP32 Power Monitor", page_icon="⚡", initial_sidebar_state="collapsed")

st_autorefresh(interval=2000, key="refresh")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    background-attachment: fixed;
}

.title {
    text-align: center;
    font-size: clamp(1.8rem, 4vw, 2.5rem);
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff 0%, #4facfe 50%, #00f2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}

.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 15px 25px rgba(0,0,0,0.25);
    padding: 1.2rem;
    text-align: center;
    transition: 0.3s;
}

.glass-card:hover {
    transform: translateY(-5px);
}

.metric-value {
    font-size: clamp(1.6rem, 5vw, 2.5rem);
    font-weight: 700;
    color: white;
}

.metric-label {
    color: rgba(255,255,255,0.7);
    font-size: 0.8rem;
}

.status-badge {
    padding: 0.5rem 1rem;
    border-radius: 30px;
    font-size: 0.9rem;
    font-weight: 600;
    margin: 0.5rem 0;
}

.occupied { background: #10b981; color: white; }
.empty { background: #f59e0b; color: white; }
.cutoff { background: #ef4444; color: white; }
.flowing { background: #3b82f6; color: white; }
.noflow { background: #6b7280; color: white; }

.btn-modern {
    height: 45px;
    padding: 0.8rem;
    border-radius: 12px;
    font-size: 0.9rem;
}

.section-divider {
    height: 2px;
    background: rgba(255,255,255,0.2);
    margin: 1.2rem 0;
}

.warning-box {
    padding: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>⚡ ESP32 Smart Power Monitor</div>", unsafe_allow_html=True)

@st.cache_data(ttl=5)
def fetch_data():
    try:
        data_resp = requests.get("http://127.0.0.1:5000/api/data", timeout=5)
        control_resp = requests.get("http://127.0.0.1:5000/api/control", timeout=5)
        return data_resp.json(), control_resp.json()
    except:
        return [], {"cutoff": False}

data, control = fetch_data()

if data:
    df = pd.DataFrame(data)
    latest = df.iloc[-1]

    empty_count = 0
    for _, row in df.iloc[::-1].iterrows():
        if not row['occupied']:
            empty_count += 1
        else:
            break

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='glass-card'><h3>🧠 Room Status</h3>", unsafe_allow_html=True)

        if control["cutoff"]:
            st.markdown('<div class="status-badge cutoff">MANUAL CUT</div>', unsafe_allow_html=True)
        elif latest['occupied']:
            st.markdown('<div class="status-badge occupied">Occupied</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge empty">Empty</div>', unsafe_allow_html=True)

        st.markdown(f"<p>Empty for <b>{empty_count}s</b></p></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><h3>⚡ Power Flow</h3>", unsafe_allow_html=True)

        if latest['usage'] > 0:
            st.markdown('<div class="status-badge flowing">Flowing</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge noflow">No Current</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Manual Control</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("CUT OFF"):
            requests.post("http://127.0.0.1:5000/api/control", json={"cutoff": True})
            st.rerun()

    with c2:
        if st.button("RESTORE"):
            requests.post("http://127.0.0.1:5000/api/control", json={"cutoff": False})
            st.rerun()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Live Metrics</h3>", unsafe_allow_html=True)

    current = latest['usage']
    voltage = current * 10
    power = current * voltage
    energy = df['usage'].sum() * voltage / 3600000

    metrics = [
        ("CURRENT", f"{current:.2f} A"),
        ("VOLTAGE", f"{voltage:.1f} V"),
        ("POWER", f"{power:.1f} W"),
        ("ENERGY", f"{energy:.4f} kWh")
    ]

    cols = st.columns(4)

    for i, (label, value) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class='glass-card'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value'>{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Recent Activity</h3>", unsafe_allow_html=True)

    log_data = []
    for i in range(len(df)-2, 0, -1):
        if df.iloc[i]['occupied'] != df.iloc[i+1]['occupied']:
            log_data.append({
                "Time": df.iloc[i]['time'],
                "Status": "Entered" if df.iloc[i+1]['occupied'] else "Left",
                "Current": f"{df.iloc[i]['usage']:.2f} A",
                "Duration": f"{empty_count}s"
            })

    if log_data:
        log_df = pd.DataFrame(log_data[:5])
        st.dataframe(log_df, use_container_width=True, hide_index=True, height=140)
    else:
        st.markdown("<div class='glass-card warning-box'>No Activity</div>", unsafe_allow_html=True)

else:
    st.markdown("<h2 style='text-align:center;'>No Data</h2>", unsafe_allow_html=True)
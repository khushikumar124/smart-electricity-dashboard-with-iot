import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide", page_title="ESP32 Power Monitor", page_icon="⚡", initial_sidebar_state="collapsed")

st_autorefresh(interval=500, key="refresh")

# -------- UI --------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.block-container { padding-top: 1rem; padding-bottom: 1rem; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    background-attachment: fixed;
}

.title {
    text-align: center;
    font-size: clamp(1.8rem, 4vw, 2.5rem);
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #4facfe, #00f2fe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 15px 25px rgba(0,0,0,0.25);
    padding: 1.2rem;
    text-align: center;
}

.metric-value { font-size: 2rem; font-weight: 700; color: white; }
.metric-label { color: rgba(255,255,255,0.7); font-size: 0.8rem; }

.status-badge {
    padding: 0.5rem 1rem;
    border-radius: 30px;
    font-weight: 600;
    margin: 0.5rem 0;
}

.occupied { background: #10b981; color: white; }
.empty { background: #f59e0b; color: white; }
.cutoff { background: #ef4444; color: white; }
.flowing { background: #3b82f6; color: white; }
.noflow { background: #6b7280; color: white; }

.section-divider {
    height: 2px;
    background: rgba(255,255,255,0.2);
    margin: 1.2rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>⚡ ESP32 Smart Power Monitor</div>", unsafe_allow_html=True)

# -------- FETCH --------
@st.cache_data(ttl=2)
def fetch_data():
    try:
        data = requests.get("http://127.0.0.1:5000/api/data").json()
        logs = requests.get("http://127.0.0.1:5000/api/logs").json()
        control = requests.get("http://127.0.0.1:5000/api/control").json()
        return data, logs, control
    except:
        return [], [], {"cutoff": False}

data, logs, control = fetch_data()

if data:
    df = pd.DataFrame(data)
    latest = df.iloc[-1]

    # -------- CALCULATIONS --------
    current = latest['usage']
    voltage = latest.get('voltage', 230)

    power = current * voltage
    energy = (df['usage'] * df['voltage'] * 2).sum() / 3600000

    # -------- ADD POWER + TIME --------
    df['power'] = df['usage'] * df['voltage']
    if 'timestamp' in df.columns:
        df['time'] = pd.to_datetime(df['timestamp'])
    else:
        df['time'] = df.index

    # -------- EMPTY TIMER --------
    empty_count = 0
    for _, row in df.iloc[::-1].iterrows():
        if not row['occupied']:
            empty_count += 1
        else:
            break

    empty_seconds = empty_count * 2

    # -------- STATUS --------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='glass-card'><h3>🧠 Room Status</h3>", unsafe_allow_html=True)

        if control["cutoff"]:
            st.markdown('<div class="status-badge cutoff">MANUAL CUT</div>', unsafe_allow_html=True)
        elif latest['occupied']:
            st.markdown('<div class="status-badge occupied">Occupied</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge empty">Empty</div>', unsafe_allow_html=True)

        st.markdown(f"<p>Empty for <b>{empty_seconds}s</b></p></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><h3>⚡ Power Flow</h3>", unsafe_allow_html=True)

        if current > 0:
            st.markdown('<div class="status-badge flowing">Flowing</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge noflow">No Current</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # -------- CONTROL --------
    st.markdown("<h3 style='text-align:center;'>Control Panel</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🔴 Manual Cutoff", use_container_width=True):
            try:
                requests.post("http://127.0.0.1:5000/api/control", json={"cutoff": True})
                st.rerun()
            except:
                st.error("Failed to send cutoff")

    with c2:
        if st.button("🟢 Restore Power", use_container_width=True):
            try:
                requests.post("http://127.0.0.1:5000/api/control", json={"cutoff": False})
                st.rerun()
            except:
                st.error("Failed to restore")

    # -------- METRICS --------
    st.markdown("<h3 style='text-align:center;'>Live Metrics</h3>", unsafe_allow_html=True)

    metrics = [
        ("CURRENT", f"{current:.2f} A"),
        ("VOLTAGE", f"{voltage:.0f} V"),
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

    # -------- POWER GRAPH --------
    st.markdown("<h3 style='text-align:center;'>Power Consumption</h3>", unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['power'],
        mode='lines',
        name='Power (W)',
        line=dict(width=3)
    ))

    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Time",
        yaxis_title="Power (Watts)",
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # -------- LOGS --------
    st.markdown("<h3 style='text-align:center;'>Recent Activity</h3>", unsafe_allow_html=True)

    if logs:
        formatted_logs = []

        for log in logs[::-1][:5]:
            start = pd.to_datetime(log["start"])
            end = log["end"]

            formatted_logs.append({
                "Status": log["status"],
                "Start": start.strftime("%H:%M:%S"),
                "End": "Now" if end is None else pd.to_datetime(end).strftime("%H:%M:%S"),
                "Duration": f"{log['duration']}s"
            })

        st.dataframe(pd.DataFrame(formatted_logs), use_container_width=True, hide_index=True, height=140)

    else:
        st.markdown("<div class='glass-card'>No Activity</div>", unsafe_allow_html=True)

else:
    st.markdown("<h2 style='text-align:center;'>No Data</h2>", unsafe_allow_html=True)
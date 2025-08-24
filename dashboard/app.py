import os
import requests
import streamlit as st

# Rebranded temporary cockpit name
st.set_page_config(page_title="CamboAI TraderStation — Backend Monitor", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("CamboAI TraderStation — Backend Monitor")
st.caption(f"Backend API: {API_URL}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Backend Health")
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        st.success(f"/health -> {r.status_code} {r.json()}")
    except Exception as e:
        st.error(f"Failed to reach backend: {e}")

with col2:
    st.subheader("Portfolio Summary (mock)")
    try:
        r = requests.get(f"{API_URL}/api/portfolio/summary", timeout=3)
        if r.ok:
            data = r.json()
            st.metric("Total Value", f"${data.get('total_value', 0):,.2f}")
            st.metric("Total PnL", f"${data.get('total_pnl', 0):,.2f}")
            st.metric("Positions", data.get('positions_count', 0))
        else:
            st.warning(f"No data yet: {r.status_code}")
    except Exception as e:
        st.info("Start backend (simple_server) for demo data.")
        st.write(e)

st.divider()
st.subheader("Positions (mock)")
try:
    r = requests.get(f"{API_URL}/api/portfolio/positions", timeout=3)
    if r.ok:
        st.dataframe(r.json())
except Exception:
    pass

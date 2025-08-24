import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="CamboStation", layout="wide")

with st.sidebar:
    selected = option_menu("Tactical Modules",
        ["📊 Charts", "🔍 Scanner", "🧠 Commentary", "🗺️ Planner", "📚 Education"],
        icons=["bar-chart", "search", "robot", "map", "book"],
        menu_icon="cast", default_index=0)

if selected == "📊 Charts":
    from tabs import charts
    charts.run()

elif selected == "🔍 Scanner":
    from tabs import scanner
    scanner.run()

elif selected == "🧠 Commentary":
    from tabs import commentary
    commentary.run()

elif selected == "🗺️ Planner":
    from tabs import planner
    planner.run()

elif selected == "📚 Education":
    from tabs import education
    education.run()

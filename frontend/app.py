"""
Streamlit frontend.  Run from the frontend/ folder:

    cd frontend
    streamlit run app.py
"""
import streamlit as st

import api_client
import config

st.set_page_config(page_title=config.PROJECT_TITLE, page_icon=config.PROJECT_ICON, layout="wide")

user = st.session_state.get("user")

if not user:
    st.navigation([st.Page("views/login.py", title="Sign in", icon="🔐")]).run()
    st.stop()

role = user["role"]

# Sidebar: who is logged in + backend status
with st.sidebar:
    st.markdown(f"**{user['name']}**  \n`{role}`")
    if st.button("Log out", width="stretch"):
        api_client.logout()
        st.rerun()
    try:
        api_client.health()
        st.success("Backend connected")
    except api_client.APIError:
        st.error("Backend not connected")
    st.caption(f"API: {api_client.API_URL}")

dashboard = st.Page("views/dashboard.py", title="Dashboard", icon="📊", default=True)
alerts = st.Page("views/alerts.py", title="Low Attendance Alerts", icon="🚨")
trends = st.Page("views/trends.py", title="Trend Analysis", icon="📈")
record = st.Page("views/record_attendance.py", title="Record Attendance", icon="📝")
history = st.Page("views/history.py", title="Attendance History", icon="🕘")
reports = st.Page("views/reports.py", title="Reports & Export", icon="📄")
students = st.Page("views/students.py", title="Students", icon="🧑‍🎓")
classes = st.Page("views/classes.py", title="Classes & Courses", icon="🏫")
users = st.Page("views/users.py", title="Users & Roles", icon="👥")
about = st.Page("views/about.py", title="About", icon="ℹ️")

if role == "admin":
    pages = {"Overview": [dashboard, alerts, trends],
             "Attendance": [record, history, reports],
             "Management": [students, classes, users],
             "Info": [about]}
elif role == "teacher":
    pages = {"Overview": [dashboard, alerts, trends],
             "Attendance": [record, history, reports],
             "Management": [students],
             "Info": [about]}
else:  # student
    pages = {"My attendance": [dashboard, history, alerts, trends, reports],
             "Info": [about]}

st.navigation(pages).run()

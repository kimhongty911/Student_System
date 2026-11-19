"""Feature 9 – attendance patterns over time."""
import pandas as pd
import streamlit as st

import api_client
import components as ui

st.title("📈 Attendance Trend Analysis")
period = st.radio("Group by", ["week", "month"], horizontal=True, format_func=str.capitalize)
params = ui.filter_bar("trends", default_days=90)

data = ui.load(api_client.get, "/api/analytics/trends", period=period, **params)
if not data["series"]:
    st.info("No attendance records match these filters yet.")
    st.stop()

for note in data["insights"]:
    st.info(note)

st.subheader(f"Attendance rate per {period}")
series = pd.DataFrame(data["series"]).set_index("period")
st.line_chart(series["rate"])
with st.expander("Show the numbers"):
    st.dataframe(series[["total", "present", "late", "absent", "rate", "change"]].rename(
        columns={"total": "Records", "present": "Present", "late": "Late", "absent": "Absent",
                 "rate": "Rate %", "change": "Change vs previous"}), width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("Absence rate by weekday")
    weekday = pd.DataFrame(data["weekday"])
    st.bar_chart(weekday.set_index("weekday")["absent_rate"])
with right:
    st.subheader("Most frequently absent")
    frequent = pd.DataFrame(data["frequent_absentees"])
    if frequent.empty:
        st.success("Nobody has been absent.")
    else:
        st.dataframe(frequent[["student_code", "student_name", "absent", "total", "absent_rate"]].rename(
            columns={"student_code": "Student ID", "student_name": "Student", "absent": "Absences",
                     "total": "Records", "absent_rate": "Absent %"}), width="stretch", hide_index=True)

st.subheader(f"Students whose attendance dropped (latest {period} vs previous)")
declining = pd.DataFrame(data["declining"])
if declining.empty:
    st.success("No sharp drops found.")
else:
    st.dataframe(declining[["student_code", "student_name", "previous_rate", "current_rate", "change"]].rename(
        columns={"student_code": "Student ID", "student_name": "Student", "previous_rate": "Previous %",
                 "current_rate": "Current %", "change": "Change"}), width="stretch", hide_index=True)

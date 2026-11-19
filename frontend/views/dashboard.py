"""Feature 6 – attendance statistics and charts."""
import pandas as pd
import streamlit as st

import api_client
import components as ui

st.title("📊 Attendance Dashboard" if ui.is_staff() else "📊 My Attendance")
params = ui.filter_bar("dash", default_days=60)

data = ui.load(api_client.get, "/api/analytics/summary", **params)
o = data["overall"]
if o["total"] == 0:
    st.info("No attendance records match these filters yet.")
    st.stop()

c = st.columns(5)
c[0].metric("Attendance rate", ui.fmt_rate(o["rate"]))
c[1].metric("Present", o["present"])
c[2].metric("Late", o["late"])
c[3].metric("Absent", o["absent"])
c[4].metric("Students" if ui.is_staff() else "Records", o["students"] if ui.is_staff() else o["total"])
st.caption("Attendance rate = (present + late) ÷ all records. Late counts as attended.")

if ui.is_staff():
    alerts = ui.load(api_client.get, "/api/analytics/low-attendance", **params)
    if alerts["total"]:
        st.warning(f"🚨 {alerts['total']} student(s) are below {alerts['threshold']:.0f}% attendance "
                   "– see **Low Attendance Alerts**.")

left, right = st.columns(2)
with left:
    st.subheader("Attendance rate over time")
    daily = pd.DataFrame(data["daily"]).set_index("date")
    st.line_chart(daily["rate"])
with right:
    st.subheader("Present / Late / Absent")
    st.bar_chart(pd.Series({"Present": o["present"], "Late": o["late"], "Absent": o["absent"]}))

left, right = st.columns(2)
with left:
    st.subheader("Rate by class")
    by_class = pd.DataFrame(data["by_class"])
    st.bar_chart(by_class.set_index("class_name")["rate"])
with right:
    st.subheader("Rate by course")
    by_course = pd.DataFrame(data["by_course"])
    st.bar_chart(by_course.set_index("course")["rate"])

with st.expander("Show the numbers"):
    st.dataframe(by_course.rename(columns={"course": "Course", "total": "Records", "present": "Present",
                                           "late": "Late", "absent": "Absent", "rate": "Rate %"}),
                 width="stretch", hide_index=True)

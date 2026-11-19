"""Feature 8 – students whose attendance is below a threshold."""
import pandas as pd
import streamlit as st

import api_client
import components as ui

st.title("🚨 Low Attendance Alerts")
threshold = st.slider("Alert threshold (attendance rate below…)", 40, 100, 75, step=5, format="%d%%")
params = ui.filter_bar("alerts", default_days=30)

data = ui.load(api_client.get, "/api/analytics/low-attendance", threshold=threshold, **params)
items = data["items"]
if not items:
    st.success(f"No students are below {threshold}% in this period. 🎉")
    st.stop()

critical = sum(1 for i in items if i["severity"] == "critical")
c1, c2 = st.columns(2)
c1.metric("Students below threshold", len(items))
c2.metric("Critical (far below)", critical)

for i in items[:5]:
    icon = "🔴" if i["severity"] == "critical" else "🟠"
    st.warning(f"{icon} **{i['student_name']}** ({i['student_code']}) – attendance {i['rate']}% "
               f"({i['absent']} absent, {i['late']} late out of {i['total']})")

df = pd.DataFrame(items)[["student_code", "student_name", "total", "present", "late", "absent",
                          "rate", "severity"]]
df["severity"] = df["severity"].map({"critical": "🔴 Critical", "warning": "🟠 Warning"})
df.columns = ["Student ID", "Student", "Records", "Present", "Late", "Absent", "Rate", "Level"]
st.dataframe(df, width="stretch", hide_index=True, column_config={
    "Rate": st.column_config.ProgressColumn("Rate", min_value=0, max_value=100, format="%.1f%%")})
st.caption("Critical = rate below 80% of the threshold.")

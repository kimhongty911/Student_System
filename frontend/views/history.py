"""Feature 5 – view, search, filter and update attendance records."""
import pandas as pd
import streamlit as st

import api_client
import components as ui

st.title("🕘 Attendance History" if ui.is_staff() else "🕘 My Attendance History")
params = ui.filter_bar("hist", default_days=30, status=True, search=ui.is_staff())
limit = st.number_input("Maximum rows to load", min_value=50, max_value=1000, value=200, step=50)

data = ui.load(api_client.get, "/api/attendance", limit=limit, **params)
items = data["items"]
st.caption(f"Showing {len(items)} of {data['total']} records")
if not items:
    st.info("No attendance records match these filters.")
    st.stop()

df = pd.DataFrame(items)
table = df[["date", "student_code", "student_name", "class_name", "subject_name", "status", "remark"]].copy()
table["status"] = table["status"].str.capitalize()
table.columns = ["Date", "Student ID", "Student", "Class", "Subject", "Status", "Remark"]
st.dataframe(table, width="stretch", hide_index=True)

if ui.is_staff():
    with st.expander("✏️ Update or delete a record"):
        labels = {r["id"]: f"{r['date']} · {r['student_name']} · {r['subject_name']} · {r['status']}"
                  for r in items}
        rec_id = st.selectbox("Record", list(labels), format_func=labels.get)
        record = next(r for r in items if r["id"] == rec_id)
        options = ["present", "late", "absent"]
        new_status = st.selectbox("Status", options, index=options.index(record["status"]),
                                  format_func=str.capitalize)
        new_remark = st.text_input("Remark", value=record["remark"])
        c1, c2, _ = st.columns([1, 1, 4])
        if c1.button("Update", type="primary"):
            try:
                api_client.put(f"/api/attendance/{rec_id}", {"status": new_status, "remark": new_remark})
                st.toast("Record updated")
                st.rerun()
            except api_client.AuthExpired as e:
                api_client.show_error_and_stop(e)
            except api_client.APIError as e:
                st.error(str(e))
        if c2.button("Delete"):
            try:
                api_client.delete(f"/api/attendance/{rec_id}")
                st.toast("Record deleted")
                st.rerun()
            except api_client.AuthExpired as e:
                api_client.show_error_and_stop(e)
            except api_client.APIError as e:
                st.error(str(e))

"""Feature 1 – role management (admin only)."""
import pandas as pd
import streamlit as st

import api_client
import components as ui

st.title("👥 Users & Roles")


def run(action, success):
    try:
        action()
        st.toast(success)
        st.rerun()
    except api_client.AuthExpired as e:
        api_client.show_error_and_stop(e)
    except api_client.APIError as e:
        st.error(str(e))


users = ui.load(api_client.get, "/api/users")["items"]
df = pd.DataFrame(users)[["username", "name", "email", "role", "student_code", "is_active"]]
df.columns = ["Username", "Name", "Email", "Role", "Student ID", "Active"]
st.dataframe(df, width="stretch", hide_index=True)

with st.expander("➕ Create a user"):
    with st.form("create_user", clear_on_submit=True):
        name = st.text_input("Full name *")
        username = st.text_input("Username *")
        email = st.text_input("Email")
        password = st.text_input("Password * (min. 6 characters)", type="password")
        role = st.selectbox("Role", ["teacher", "admin", "student"])
        student_code = st.text_input("Student ID (only for the student role; the student must already exist)")
        if st.form_submit_button("Create user", type="primary"):
            run(lambda: api_client.post("/api/users", {"name": name, "username": username, "email": email,
                                                        "password": password, "role": role,
                                                        "student_code": student_code}), "User created")

others = [u for u in users if u["id"] != ui.current_user()["id"]]
if others:
    with st.expander("✏️ Change a user's role / status / password"):
        labels = {u["id"]: f"{u['username']} ({u['role']})" for u in others}
        uid = st.selectbox("User", list(labels), format_func=labels.get)
        u = next(x for x in others if x["id"] == uid)
        roles = ["admin", "teacher", "student"]
        new_role = st.selectbox("Role", roles, index=roles.index(u["role"]) if u["role"] in roles else 2,
                                key=f"role_{uid}")
        active = st.checkbox("Account is active", value=u["is_active"], key=f"active_{uid}")
        new_password = st.text_input("New password (leave empty to keep)", type="password", key=f"pw_{uid}")
        c1, c2, _ = st.columns([1, 1, 4])
        if c1.button("Save", type="primary"):
            payload = {"role": new_role, "is_active": active}
            if new_password:
                payload["password"] = new_password
            run(lambda: api_client.put(f"/api/users/{uid}", payload), "User updated")
        if c2.button("Delete user"):
            run(lambda: api_client.delete(f"/api/users/{uid}"), "User deleted")

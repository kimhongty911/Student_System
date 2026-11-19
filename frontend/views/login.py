import streamlit as st

import api_client
import config

st.title(f"{config.PROJECT_ICON} {config.PROJECT_TITLE}")
st.caption("Sign in to continue.")

if st.session_state.get("flash"):
    st.warning(st.session_state.pop("flash"))

login_tab, register_tab = st.tabs(["Log in", "Register"])

with login_tab:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Log in", type="primary"):
            try:
                api_client.login(username, password)
                st.rerun()
            except api_client.APIError as e:
                st.error(str(e))
    st.caption("Demo accounts (after `seed_demo`):  admin / admin12345 · teacher1 / teacher12345 · "
               "student1 / student12345")

with register_tab:
    st.write("Students need the **Student ID** that the school gave them. Admin accounts are created by an administrator.")
    role = st.radio("I am a", ["student", "teacher"], horizontal=True)
    with st.form("register_form"):
        name = st.text_input("Full name")
        email = st.text_input("Email (optional)")
        student_code = st.text_input("Student ID") if role == "student" else ""
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password (min. 6 characters)", type="password")
        if st.form_submit_button("Create account", type="primary"):
            try:
                api_client.register({"name": name, "email": email, "role": role, "student_code": student_code,
                                     "username": new_username, "password": new_password})
                st.rerun()
            except api_client.APIError as e:
                st.error(str(e))

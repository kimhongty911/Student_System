import streamlit as st

import config

st.title("ℹ️ About")
st.subheader("Project")
st.write(f"**{config.PROJECT_TITLE}**")
st.write(config.PROJECT_DESCRIPTION)
st.write(f"**Target users:** {config.TARGET_USERS}")

st.subheader("Team")
st.write(f"Class: **{config.CLASS_NAME}**")
st.markdown(f"- {config.TEAM_LEADER} (Team Leader)")
for member in config.TEAM_MEMBERS:
    st.markdown(f"- {member}")

st.subheader("Out of scope (not built)")
for item in config.OUT_OF_SCOPE:
    st.markdown(f"- {item}")

st.subheader("Architecture")
st.write("Streamlit (frontend) · Django (backend REST API) · SQLite (database)")

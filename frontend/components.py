"""Small helpers shared by several pages."""
from datetime import date, timedelta

import streamlit as st

import api_client


def current_user() -> dict:
    return st.session_state["user"]


def is_staff() -> bool:
    return current_user()["role"] in ("admin", "teacher")


def is_admin() -> bool:
    return current_user()["role"] == "admin"


def load(fn, *args, **kwargs):
    """Call the API; on failure show the error and stop the page."""
    try:
        return fn(*args, **kwargs)
    except api_client.APIError as e:
        api_client.show_error_and_stop(e)


def fmt_rate(value) -> str:
    return "–" if value is None else f"{value:.1f}%"


def date_range(label: str, key: str, default_days: int):
    today = date.today()
    value = st.date_input(label, value=(today - timedelta(days=default_days), today),
                          max_value=today, key=key)
    if isinstance(value, (tuple, list)):
        if len(value) == 2:
            return value[0], value[1]
        if len(value) == 1:                        # user has only picked the start so far
            return value[0], today
    return value, value


def _pick(col, label, items, label_fn, key):
    labels = {i["id"]: label_fn(i) for i in items}
    return col.selectbox(label, [None] + list(labels), key=key,
                         format_func=lambda x: "All" if x is None else labels[x])


def filter_bar(key: str, default_days: int = 60, status: bool = False, search: bool = False) -> dict:
    """Class / course / date range (and optionally status / search). Returns API query params."""
    classes = load(api_client.get, "/api/classes")["items"]
    courses = load(api_client.get, "/api/courses")["items"]
    cols = st.columns([1, 1.4, 1.6] + ([1] if status else []) + ([1.4] if search else []))
    params = {
        "class": _pick(cols[0], "Class", classes, lambda c: c["name"], f"{key}_class"),
        "course": _pick(cols[1], "Course", courses,
                        lambda c: f"{c['subject_name']} ({c['class_name']})", f"{key}_course"),
    }
    with cols[2]:
        start, end = date_range("Date range", f"{key}_dates", default_days)
    params["date_from"], params["date_to"] = start.isoformat(), end.isoformat()
    i = 3
    if status:
        params["status"] = cols[i].selectbox("Status", [None, "present", "late", "absent"], key=f"{key}_status",
                                             format_func=lambda x: "All" if x is None else x.capitalize())
        i += 1
    if search:
        params["search"] = cols[i].text_input("Search student", key=f"{key}_search",
                                              placeholder="name or ID")
    return params

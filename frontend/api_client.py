"""
All calls from Streamlit to the Django backend go through this file.
The login token is kept in st.session_state and sent on every request.
"""
import os

import requests
import streamlit as st

# Change with an environment variable, e.g.  API_URL=https://my-api.onrender.com
API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 30


class APIError(Exception):
    pass


class AuthExpired(APIError):
    pass


def _clean(params: dict) -> dict:
    return {k: v for k, v in params.items() if v not in (None, "")}


def _request(method: str, path: str, **kwargs):
    headers = {}
    if st.session_state.get("token"):
        headers["Authorization"] = f"Token {st.session_state['token']}"
    try:
        r = requests.request(method, f"{API_URL}{path}", headers=headers, timeout=TIMEOUT, **kwargs)
    except requests.ConnectionError:
        raise APIError(f"Cannot connect to the backend at {API_URL}. Is it running?")
    except requests.Timeout:
        raise APIError("The backend took too long to answer.")
    if r.status_code == 401 and headers:
        raise AuthExpired("Your session has expired. Please log in again.")
    if not r.ok:
        try:
            detail = r.json().get("detail", r.text)
        except ValueError:
            detail = r.text
        raise APIError(str(detail))
    return r


# ---------------------------------------------------------------- session
def start_session(response: dict):
    st.session_state["token"] = response["token"]
    st.session_state["user"] = response["user"]


def clear_session():
    st.session_state.pop("token", None)
    st.session_state.pop("user", None)


def health():
    return _request("GET", "/api/health").json()


def login(username: str, password: str):
    start_session(_request("POST", "/api/auth/login", json={"username": username, "password": password}).json())


def register(payload: dict):
    start_session(_request("POST", "/api/auth/register", json=payload).json())


def logout():
    try:
        _request("POST", "/api/auth/logout")
    except APIError:
        pass
    clear_session()


# ---------------------------------------------------------------- generic verbs
def get(path: str, **params):
    return _request("GET", path, params=_clean(params)).json()


def post(path: str, payload: dict | None = None):
    return _request("POST", path, json=payload or {}).json()


def put(path: str, payload: dict):
    return _request("PUT", path, json=payload).json()


def delete(path: str):
    return _request("DELETE", path).json()


def download(path: str, **params):
    """Returns (bytes, filename, mime) for CSV / PDF exports."""
    r = _request("GET", path, params=_clean(params))
    disposition = r.headers.get("Content-Disposition", "")
    filename = disposition.split("filename=")[-1].strip('"') if "filename=" in disposition else "report"
    return r.content, filename, r.headers.get("Content-Type", "application/octet-stream").split(";")[0]


def show_error_and_stop(err: Exception):
    """Show a friendly error message and stop the page."""
    if isinstance(err, AuthExpired):
        clear_session()
        st.session_state["flash"] = str(err)
        st.rerun()
    st.error(str(err))
    st.info("Start the backend first – see README.md, step 3.")
    st.stop()

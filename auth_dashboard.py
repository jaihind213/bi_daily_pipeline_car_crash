import logging

import duckdb
import streamlit as st
from streamlana import side_bar_util

import dash_setup
import util

welcome_msg = """Chicago 🚕 crash 🏃💥dashboard. You are 1 step closer to Hiring me 😁
passwd is 'hireme'
"""

# 📋 First thing to do, set page layout of streamlit
side_bar_util.set_page_layout(layout="wide")

# ⚙️ Log level
logging.basicConfig(level=logging.WARN)

# 👤setup basic auth for demo
authenticator = util.setup_auth()

# 🔐 login page
fields = {"Form name": welcome_msg}
authenticator.login(fields=fields, location="main")
if st.session_state.get("authentication_status"):
    with st.sidebar:
        options = ["    🐙 " + st.session_state.get("username")]
    user = st.session_state.get("username")
    logging.warning("User logged in: %s", user)
    util.notify_login_via_slack(user)
    authenticator.logout(
        "🐙" + user + " Logout", "sidebar", callback=util.logout_callback
    )

    # 🦆
    conn = duckdb.connect()
    dash_setup.setup_duck_conn(conn, iceberg_table_to_access="crash_cube")
    # 🏗️Load pageside bar configuration from YAML file
    side_bar_config = side_bar_util.load_side_bar_config_yaml("side_bar.yaml")
    # 📊 render dash
    try:
        side_bar_util.render_side_bar_pages(
            side_bar_config, conn, check_user_access=util.login_check
        )
    finally:
        conn.close()
elif st.session_state.get("authentication_status") is False:
    st.error("Username/password is incorrect")
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password")

import logging
import os

import duckdb
import streamlit as st
from streamlana import side_bar_util

import dash_setup
import util

welcome_msg = """Chicago 🚕 crash 🏃💥dashboard. Thanks for the visit.
me @ https://www.linkedin.com/in/213vishnu/
"""
CREDS_INFO_MSG = "username is in my CV/Resume & password is 'hire-me'"


def load_dashboard(
    side_bar_yaml_file="side_bar.yaml",
    table_marcro_name="crash_cube",
    auth_enabled=False,
):
    # 🦆
    conn = duckdb.connect()
    dash_setup.setup_duck_conn(conn, iceberg_table_to_access=table_marcro_name)
    # 🏗️Load pageside bar configuration from YAML file
    side_bar_config = side_bar_util.load_side_bar_config_yaml(side_bar_yaml_file)
    # 📊 render dash
    try:
        if auth_enabled:
            side_bar_util.render_side_bar_pages(
                side_bar_config, conn, check_user_access=util.login_check
            )
        else:
            side_bar_util.render_side_bar_pages(side_bar_config, conn)
    finally:
        conn.close()


# 📋 First thing to do, set page layout of streamlit
side_bar_util.set_page_layout(layout="wide")

# ⚙️ Log level
logging.basicConfig(level=logging.WARN)

if os.environ.get("AUTH_ENABLED", "false").lower() == "false":
    load_dashboard()
else:
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
        load_dashboard(auth_enabled=True)
    elif st.session_state.get("authentication_status") is False:
        st.error("Username/password is incorrect")
    elif st.session_state.get("authentication_status") is None:
        st.warning(CREDS_INFO_MSG)

import json
import logging
import os
import traceback
from datetime import datetime
from typing import List

import duckdb
import pytz
import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from datasketches import compact_theta_sketch, theta_union
from duckdb.typing import BLOB, DOUBLE
from streamlit_authenticator import Hasher
from yaml.loader import SafeLoader


def setup_blob_store_auth(
    conn, access_key, secret_key, region="sgp1", endpoint="sgp1.digitaloceanspaces.com"
):
    if access_key is None or secret_key is None:
        return
    conn.execute(f"SET s3_region = '{region}';")
    conn.execute(f"SET s3_endpoint = '{endpoint}';")
    conn.execute("SET s3_use_ssl = true;")
    conn.execute(
        f"SET s3_access_key_id = '{access_key}';SET s3_secret_access_key = '{secret_key}';"  # noqa: E501
    )


def union_sketches(sketches: List):
    """Union multiple theta sketches into one."""
    union = theta_union()
    for sketch in sketches:
        if sketch is None:
            continue
        set_sketch = compact_theta_sketch.deserialize(bytes(sketch))
        union.update(set_sketch)
    return union.get_result().serialize()


def register_sketches_functions(con):
    con.create_function(
        "union_sketches", union_sketches, [duckdb.list_type(BLOB)], return_type=BLOB
    )
    con.create_function("estimate_sketch", estimate_sketch, [BLOB], return_type=DOUBLE)


def estimate_sketch(sketch):
    """Estimate the size of a theta sketch."""
    if sketch is None:
        return None
    sketch = compact_theta_sketch.deserialize(sketch)
    return sketch.get_estimate() if sketch else None


def logout_callback(details_map=None):
    st.session_state["authentication_status"] = None
    st.session_state["username"] = None
    st.session_state["user_role"] = None
    st.session_state["user_permissions"] = None

    def dummy_page():
        st.title("")

    pg = st.navigation(
        [st.Page(dummy_page, title=None, icon=None, url_path=None, default=True)],
        position="sidebar",
        expanded=False,
    )
    pg.run()


def setup_auth(users_file="./usr.yaml"):
    with open(users_file) as file:
        config = yaml.load(file, Loader=SafeLoader)

        return stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
        )


def login_check() -> str:
    if (
        "authentication_status" in st.session_state
        and st.session_state.get("authentication_status") is True
    ):
        return st.session_state.get("username")
    return None


def hasher(conf):
    return Hasher.hash_passwords(conf)


def notify_login_via_slack(user, timezone="Asia/Singapore", webhook_url=None):
    """
    Notify user login via Slack webhook.
    :param user:
    :param timezone:
    :param webhook_url:
    """
    if webhook_url is None:
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    tz = pytz.timezone(timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    message = {"text": f"Chicago dash - User: {user} logged in at {current_time}"}

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(message),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            logging.warning(
                "failed to notify Slack about user login: %s", response.text
            )
    except Exception as e:
        logging.error("Error sending notification to Slack: %s", str(e))
        traceback.print_exc()

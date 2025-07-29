import logging

import duckdb
from streamlana import side_bar_util

import dash_setup

# ✅ First thing to do, set page layout of streamlit
side_bar_util.set_page_layout(layout="wide")

# ⚙️ Log level
logging.basicConfig(level=logging.WARNING)

# 🦆
conn = duckdb.connect()

# 🏗️setup duck
dash_setup.setup_duck_conn(conn, iceberg_table_to_access="crash_cube")

# 🏗️Load pageside bar configuration from YAML file
side_bar_config = side_bar_util.load_side_bar_config_yaml("side_bar.yaml")

# 📊 render dash
try:
    side_bar_util.render_side_bar_pages(side_bar_config, conn)
finally:
    conn.close()

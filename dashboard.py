import logging
import os

import duckdb
from util import setup_blob_store_auth, register_sketches_functions

from streamlana import side_bar_util
from streamlana.side_bar_util import load_side_bar_config_yaml, render_side_bar_pages


# ✅ First thing to do, set page layout of streamlit
side_bar_util.set_page_layout(layout="wide")

# logging level
logging.basicConfig(level=logging.INFO)

# ✅ Load side bar configuration from YAML file
side_bar_config = load_side_bar_config_yaml("side_bar.yaml")

blob_store_path = os.environ.get("BLOB_STORE_PATH", "/tmp/iceberg_crashes/db/crashes_cube")

# ✅ Create DuckDB connection
con = duckdb.connect()
# Install the iceberg extension
con.execute("install iceberg; load iceberg;")

setup_blob_store_auth(con, os.environ.get("BLOB_STORE_ACCESS_KEY", "please set"),
                      os.environ.get("BLOB_STORE_SECRET_KEY", "please set"))

# register apache thetha sketch functions with DuckDB
register_sketches_functions(con)

# macro for iceberg. easy on the eye while reading sql.
con.execute(
    f"""
    CREATE MACRO crash_cube() AS table (
  SELECT * FROM iceberg_scan('{blob_store_path}', allow_moved_paths = true,version = '?')
);
"""
)
con.execute("SET unsafe_enable_version_guessing = true;")

# ✅ Render side bar pages based on the configuration
try:
    render_side_bar_pages(side_bar_config, con)
finally:
    con.close()

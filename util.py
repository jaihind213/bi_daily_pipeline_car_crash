import os
from typing import List

import duckdb
from datasketches import compact_theta_sketch, theta_intersection, theta_union
from duckdb.typing import BLOB, DOUBLE

def setup_blob_store_auth(conn, access_key, secret_key, region='sgp1', endpoint='sgp1.digitaloceanspaces.com'):
    if os.environ.get("BLOB_STORE_AUTH_ENABLED", "true") == "false":
        return
    if not access_key or not secret_key:
        raise ValueError("BLOB_STORE_ACCESS_KEY and BLOB_STORE_SECRET_KEY must be set.")
    conn.execute(f"SET s3_region = '{region}';")
    conn.execute(f"SET s3_endpoint = '{endpoint}';")
    conn.execute(f"SET s3_use_ssl = true;")
    conn.execute(f"SET s3_access_key_id = '{access_key}';SET s3_secret_access_key = '{secret_key}';")

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

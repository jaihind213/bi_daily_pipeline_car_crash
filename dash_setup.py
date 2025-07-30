import os

from util import register_sketches_functions, setup_blob_store_auth


def setup_iceberg_on_duck(con):
    con.execute("install iceberg; load iceberg;")
    setup_blob_store_auth(
        con,
        os.environ.get("BLOB_STORE_ACCESS_KEY", None),
        os.environ.get("BLOB_STORE_SECRET_KEY", None),
    )


def setup_macro_for_table_to_access(con, table_path, iceberg_table_name="crash_cube"):
    # macro for iceberg. easy on the eye while reading sql.
    con.execute(
        f"""
        CREATE MACRO {iceberg_table_name}() AS table (
      SELECT * FROM iceberg_scan('{table_path}', allow_moved_paths = true,version = '?')
    );
    """
    )


def setup_duck_conn(con, iceberg_table_to_access="crash_cube"):
    setup_iceberg_on_duck(con)
    register_sketches_functions(con)
    setup_macro_for_table_to_access(
        con,
        os.environ.get("BLOB_STORE_CUBES_PATH", "/tmp/iceberg_crashes/db/crashes_cube"),
        iceberg_table_name=iceberg_table_to_access,
    )
    con.execute("SET unsafe_enable_version_guessing = true;")

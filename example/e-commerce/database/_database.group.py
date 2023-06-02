import os.path
from contextlib import closing

import psycopg2
from psycopg2.extras import execute_batch

sql_file_dir = os.path.join(os.path.dirname(__file__), "sql")
conn_str = "dbname=postgres user=postgres password=postgres host=localhost"


def __exec_files(files: list[str]):
    """
    Execute given sql files
    :param files: list of file paths
    """
    with closing(psycopg2.connect(conn_str)) as conn:
        with conn.cursor() as cur:
            for sql_file in files:
                if not os.path.exists(sql_file):
                    continue
                # execute sql files for nodes in this group
                cur.execute(open(sql_file, "r").read())
        conn.commit()


def before(args):
    # search directory to find files with `node_name + .schema.sql`
    schemas = [os.path.join(sql_file_dir, f + ".schema.sql") for f in args["nodes"]]

    with closing(psycopg2.connect(conn_str)) as conn:
        with conn.cursor() as cur:
            # always clear your storage before starting a new export
            cur.execute("DROP SCHEMA public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
        conn.commit()
    __exec_files(schemas)


def export(args):
    node_name = args["name"]
    batches = args["batches"]
    insert_q = "INSERT INTO %s (%s) VALUES(%s)"

    with closing(psycopg2.connect(conn_str)) as conn:
        with conn.cursor() as cur:
            for batch in batches:
                insert_q = insert_q % (
                    node_name,
                    ",".join(batch[0].keys()),
                    ",".join(["%s" for _ in batch[0].keys()]),
                )
                params = [tuple(item.values()) for item in batch]
                execute_batch(cur, insert_q, params)
        conn.commit()


def after(args):
    # search directory to find files with `node_name + .index.sql`
    indexes = [os.path.join(sql_file_dir, f + ".index.sql") for f in args["nodes"]]
    # search directory to find files with `node_name + .constraint.sql`
    constraints = [
        os.path.join(sql_file_dir, f + ".constraint.sql") for f in args["nodes"]
    ]

    __exec_files(indexes)
    __exec_files(constraints)

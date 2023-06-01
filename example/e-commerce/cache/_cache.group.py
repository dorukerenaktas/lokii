import os.path
import redis

conn_str = "redis://localhost:6379?ssl_cert_reqs=none&decode_responses=True"


def before(args):
    r = redis.from_url(conn_str)

    # group directory path
    search_exp = os.path.dirname(__file__)
    # search directory to find files with `node_name + .before.sql`
    sql_files = [os.path.join(search_exp, f + ".before.sql") for f in args["nodes"]]
    # filter and ignore if file not exists
    sql_files = [f for f in sql_files if os.path.exists(f)]

    conn = None
    try:
        # create db connection
        conn = psycopg2.connect(conn_str)
        with conn.cursor() as cur:
            # always clear your storage before starting a new export
            cur.execute("DROP SCHEMA public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
            conn.commit()

            for sql_file in sql_files:
                print(sql_file)
                # execute sql files for nodes in this group
                cur.execute(open(sql_file, "r").read())
        conn.commit()
    finally:
        if conn is not None:
            conn.close()


def export(args):
    node_name = args["name"]
    batches = args["batches"]
    insert_q = "INSERT INTO %s (%s) VALUES(%s)"

    conn = None
    try:
        # create db connection
        conn = psycopg2.connect(conn_str)
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
    finally:
        if conn is not None:
            conn.close()

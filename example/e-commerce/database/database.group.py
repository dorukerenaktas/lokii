import os.path
import psycopg2
from glob import glob

conn_str = "dbname=postgres user=postgres password=postgres host=localhost"


def before(args):
    sql_files = [f for f in glob(os.path.dirname(__file__))]
    conn = None
    try:
        conn = psycopg2.connect(conn_str)
        with conn as cur:
            for sql in sql_files:
                cur.execute(open(sql, "r").read())
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

import redis

conn_str = "redis://localhost:6379?decode_responses=True"


def before(_):
    r = redis.from_url(conn_str)

    for key in r.scan_iter("prefix:*"):
        # always clear your storage before starting a new export
        r.delete(key)


def export(args):
    batches = args["batches"]

    r = redis.from_url(conn_str)
    pipe = r.pipeline()

    for batch in batches:
        for item in batch:
            # generated item contains "cache_key"
            # checkout customer_session.node.py
            pipe.hset(item["cache_key"], mapping=item)
        # execute batch
        pipe.execute()

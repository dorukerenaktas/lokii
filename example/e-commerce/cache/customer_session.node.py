import uuid
from faker import Faker

fake = Faker()

# create 500 sessions
source = """
SELECT c.customer_number, c.customer_name, c.phone, c.credit_limit
FROM customers as c
    CROSS JOIN range(10000)
    USING SAMPLE 500
"""


def item(args):
    customer_number = args["params"]["customer_number"]
    customer_name = args["params"]["customer_name"]
    phone = args["params"]["phone"]
    credit_limit = args["params"]["credit_limit"]
    session_id = str(uuid.uuid4()) + str(customer_number)
    return {
        # I like to create cache key as part of the item, it can be removed when exporting
        # example key = customer_session:38a5d603-0d4d-4fb8-9278-0c9757d186d2
        "cache_key": ":".join(["customer_session", session_id]),
        "session_id": session_id,
        "customer_number": customer_number,
        "customer_name": customer_name,
        "phone": phone,
        "credit_limit": credit_limit,
    }

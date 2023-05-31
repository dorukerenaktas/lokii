from datetime import datetime, timedelta

from faker import Faker

fake = Faker()

conf = {"type": "simple", "count": 10000}


def gen(args):
    (i,) = (args[k] for k in ["index"])

    order_date = fake.date_between(start_date=datetime.now() - timedelta(days=360))
    required_date = order_date + timedelta(days=fake.random_int(min=1, max=4))
    shipped_date = required_date + timedelta(days=fake.random_int(min=1, max=4))
    return {
        "orderNumber": i,
        "orderDate": order_date.strftime("%d-%m-%Y"),
        "requiredDate": required_date.strftime("%d-%m-%Y"),
        "shippedDate": shipped_date.strftime("%d-%m-%Y"),
        "status": i,
        "comments": i,
        "customerNumber": i,
    }

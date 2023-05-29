from faker import Faker

fake = Faker()

conf = {"type": "simple", "count": 10000}


def gen(args):
    (i,) = (args[k] for k in ["index"])

    return {
        "orderNumber": i,
        "productCode": i,
        "quantityOrdered": fake.random_int(min=1, max=4),
        "priceEach": fake.random_number(),
        "orderLineNumber": fake.random_number(),
    }

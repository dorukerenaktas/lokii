from faker import Faker

fake = Faker()


def gen(args):
    (i,) = (args[k] for k in ["index"])
    return {
        "officeCode": i,
        "city": fake.city(),
        "phone": fake.phone_number(),
        "addressLine1": fake.address(),
        "addressLine2": None,
        "state": fake.city(),
        "country": fake.country(),
        "postalCode": fake.postcode(),
        "territory": fake.administrative_unit(),
    }


runs = [
    {
        "source": "SELECT * FROM range(10000)",
        "func": gen,
    }
]

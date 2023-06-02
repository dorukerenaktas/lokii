from faker import Faker

fake = Faker()

source = "SELECT * FROM range(10)"


def item(args):
    address = fake.address().split("\n")
    return {
        "office_code": args["id"],
        "city": fake.city(),
        "phone": fake.phone_number(),
        "address_line1": address[0],
        "address_line2": address[1],
        "state": fake.city(),
        "country": fake.country(),
        "postal_code": fake.postcode(),
        "territory": fake.administrative_unit(),
    }

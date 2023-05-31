from faker import Faker

fake = Faker()

source = "SELECT * FROM range(10)"


def item(args):
    address = fake.address().split("\n")
    return {
        "officeCode": args["id"],
        "city": fake.city(),
        "phone": fake.phone_number(),
        "addressLine1": address[0],
        "addressLine2": address[1],
        "state": fake.city(),
        "country": fake.country(),
        "postalCode": fake.postcode(),
        "territory": fake.administrative_unit(),
    }

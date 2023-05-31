from faker import Faker

fake = Faker()

name = "customers"
source = "SELECT * FROM range(10000)"


def item(args):
    return {
        "customerNumber": args["id"],
        "customerName": fake.first_name(),
        "contactLastName": fake.first_name(),
        "contactFirstName": fake.last_name(),
        "phone": fake.phone_number(),
        "addressLine1": fake.address(),
        "addressLine2": None,
        "city": fake.city(),
        "state": fake.city(),
        "postalCode": fake.postcode(),
        "country": fake.country(),
        "salesRepEmployeeNumber": "",
        "creditLimit": fake.random_number(digits=8),
    }

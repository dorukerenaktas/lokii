from faker import Faker

fake = Faker()

name = "customers"
source = "SELECT * FROM range(10000)"


def item(args):
    address = fake.address().split("\n")
    return {
        "customer_number": args["id"],
        "customer_name": fake.first_name(),
        "contact_firstname": fake.last_name(),
        "contact_lastname": fake.first_name(),
        "phone": fake.phone_number(),
        "address_line1": address[0],
        "address_line2": address[1],
        "city": fake.city(),
        "state": fake.city(),
        "postalcode": fake.postcode(),
        "country": fake.country(),
        "sales_rep_employee_number": 1,
        "credit_limit": fake.random_number(digits=8),
    }

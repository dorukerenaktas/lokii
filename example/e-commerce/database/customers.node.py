from faker import Faker

fake = Faker()

name = "customers"
source = "SELECT * FROM range(10000)"


def item(args):
    return {
        "customer_number": args["id"],
        "customer_name": fake.first_name(),
        "contact_firstname": fake.last_name(),
        "contact_lastname": fake.first_name(),
        "phone": fake.phone_number(),
        "address_line1": fake.address(),
        "address_line2": None,
        "city": fake.city(),
        "state": fake.city(),
        "postalcode": fake.postcode(),
        "country": fake.country(),
        "sales_rep_employee_number": "",
        "credit_limit": fake.random_number(digits=8),
    }

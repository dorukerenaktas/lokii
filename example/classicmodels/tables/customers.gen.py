from faker import Faker

fake = Faker()


def gen(args):
    (i,) = (args[k] for k in ["index"])
    return {
        "customerNumber": i,
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


name = "customers"
runs = [
    {
        "source": "SELECT * FROM range(10000)",
        "wait": ["employees"],
        "rels": {
            "e": "SELECT employeeNumber FROM employees WHERE jobTitle = 'sales-rep'"
        },
        "func": gen,
    }
]

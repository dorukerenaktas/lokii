from faker import Faker

fake = Faker()

source = """
SELECT i.range, t, o.officeCode
    FROM offices o
    CROSS JOIN VALUES('manager', 'employee') as data(t)
    CROSS JOIN range(3) as i
"""


def item(args):
    officeCode = args["params"]["officeCode"]
    return {
        "employeeNumber": args["id"],
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "extension": fake.random_number(digits=2),
        "email": fake.email(),
        "officeCode": officeCode,
        "reportsTo": fake.random_int(min=1, max=10000),
        "jobTitle": fake.job(),
    }

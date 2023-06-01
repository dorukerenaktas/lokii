from faker import Faker

fake = Faker()

source = """
SELECT i.range, t, o.office_code
    FROM offices o
    CROSS JOIN VALUES('manager', 'employee') as data(t)
    CROSS JOIN range(3) as i
"""


def item(args):
    office_code = args["params"]["office_code"]
    return {
        "employee_number": args["id"],
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "extension": fake.random_number(digits=2),
        "email": fake.email(),
        "office_code": office_code,
        "reports_to": fake.random_int(min=1, max=10000),
        "job_title": fake.job(),
    }

from faker import Faker

fake = Faker()


def gen(args):
    (i, params) = (args[k] for k in ["index", "params"])
    return {
        "employeeNumber": i,
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "extension": fake.random_number(digits=2),
        "email": fake.email(),
        "officeCode": params['officeCode'],
        "reportsTo": fake.random_int(min=1, max=10000),
        "jobTitle": fake.job(),
    }


runs = [
    {
        "source": """
        SELECT i.range, t, o.officeCode FROM offices o
        CROSS JOIN unnest(['manager', 'employee']) as data(t)
        CROSS JOIN range(3) as i
        """,
        "wait": ["offices"],
        "func": gen,
    }
]

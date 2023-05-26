from faker import Faker

fake = Faker()

conf = {"type": "simple", "count": 10000}


def gen(args):
    (i,) = (args[k] for k in ["index"])

    return {
        "productLine": i,
        "textDescription": i,
        "htmlDescription": i,
        "image": i,
    }

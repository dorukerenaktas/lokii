from faker import Faker

fake = Faker()

conf = {"type": "simple", "count": 10000}


def gen(args):
    (i,) = (args[k] for k in ["index"])

    return {
        "productCode": i,
        "productName": i,
        "productLine": i,
        "productScale": i,
        "productVendor": i,
        "productDescription": i,
        "quantityInStock": i,
        "buyPrice": i,
        "MSRP": i,
    }

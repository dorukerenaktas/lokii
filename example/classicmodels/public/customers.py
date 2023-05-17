def gen(i, c):
    name = c["f"]["d"].first_name()
    return {
        "customerNumber": i,
        "customerName": name,
        "contactLastName": name,
        "contactFirstName": c["f"]["d"].last_name(),
        "phone": c["f"]["d"].phone_number(),
        "addressLine1": c["f"]["d"].address(),
        "addressLine2": None,
        "city": c["f"]["d"].city(),
        "state": c["f"]["d"].city(),
        "postalCode": c["f"]["d"].postcode(),
        "country": c["f"]["d"].country(),
        "salesRepEmployeeNumber": '',
        "creditLimit":  c["f"]["d"].random_number(digits=8)
    }

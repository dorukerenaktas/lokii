CREATE TABLE IF NOT EXISTS customers
  (
     customer_number           INTEGER,
     customer_name             VARCHAR,
     contact_firstname         VARCHAR,
     contact_lastname          VARCHAR,
     phone                     VARCHAR,
     address_line1             VARCHAR,
     address_line2             VARCHAR,
     city                      VARCHAR,
     state                     VARCHAR,
     postalcode                VARCHAR,
     country                   VARCHAR,
     sales_rep_employee_number INTEGER,
     credit_limit              INTEGER
  );
ALTER TABLE customers
    DROP CONSTRAINT IF EXISTS customers_customer_number_pkey CASCADE,
    ADD CONSTRAINT customers_customer_number_pkey PRIMARY KEY (customer_number),
    ALTER COLUMN customer_number DROP IDENTITY IF EXISTS,
    ALTER COLUMN customer_number ADD GENERATED ALWAYS AS IDENTITY;

-- start identity primary key sequence from max value
SELECT setval(pg_get_serial_sequence('customers', 'customer_number'), (select max(customer_number) from customers));

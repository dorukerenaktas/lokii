ALTER TABLE employees
    DROP CONSTRAINT IF EXISTS employees_employee_number_pkey CASCADE,
    ADD CONSTRAINT employees_employee_number_pkey PRIMARY KEY (employee_number),
    ALTER COLUMN employee_number DROP IDENTITY IF EXISTS,
    ALTER COLUMN employee_number ADD GENERATED ALWAYS AS IDENTITY;

-- start identity primary key sequence from max value
SELECT setval(pg_get_serial_sequence('employees', 'employee_number'), (select max(employee_number) from employees));
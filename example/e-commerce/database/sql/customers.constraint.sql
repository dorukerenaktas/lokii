ALTER TABLE customers
    ALTER COLUMN sales_rep_employee_number SET NOT NULL,
    DROP CONSTRAINT IF EXISTS customers_sales_rep_employee_number,
    ADD CONSTRAINT customers_sales_rep_employee_number FOREIGN KEY (sales_rep_employee_number)
    REFERENCES employees (employee_number);

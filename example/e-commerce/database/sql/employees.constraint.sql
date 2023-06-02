ALTER TABLE employees
    ALTER COLUMN office_code SET NOT NULL,
    DROP CONSTRAINT IF EXISTS employees_office_code,
    ADD CONSTRAINT employees_office_code FOREIGN KEY (office_code)
    REFERENCES offices (office_code);
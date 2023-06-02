ALTER TABLE offices
    DROP CONSTRAINT IF EXISTS offices_office_code_pkey CASCADE,
    ADD CONSTRAINT offices_office_code_pkey PRIMARY KEY (office_code),
    ALTER COLUMN office_code DROP IDENTITY IF EXISTS,
    ALTER COLUMN office_code ADD GENERATED ALWAYS AS IDENTITY;

-- start identity primary key sequence from max value
SELECT setval(pg_get_serial_sequence('offices', 'office_code'), (select max(office_code) from offices));
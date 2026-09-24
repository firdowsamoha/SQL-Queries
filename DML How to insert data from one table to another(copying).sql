--Copy data from customers table into the persons table
Insert into persons (id,person_name,Birth_date,phone)
SELECT
id,
first_name,
NULL,
'unknown'
FROM Customers 
SELECT* FROM persons

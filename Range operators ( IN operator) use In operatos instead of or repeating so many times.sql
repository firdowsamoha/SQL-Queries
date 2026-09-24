--retreive all customers from either USA or Uk
SELECT*
FROM Customers 
Where country = 'Germany' or country = 'USA'

SELECT*
FROM Customers 
Where country in ('Germany','USA')


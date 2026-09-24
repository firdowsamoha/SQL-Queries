/* retreive all customers who are either from USE or 
have a score than 500*/
SELECT*
FROM Customers 
Where country = 'USA' or score > 500

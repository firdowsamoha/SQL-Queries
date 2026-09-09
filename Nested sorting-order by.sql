/*Retreive all customers and sort the results by the country and then by the highest score */
SELECT *
FROM Customers
Order by country ASC,score desc

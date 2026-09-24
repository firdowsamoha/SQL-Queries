/* update all customers with NULL score 
by setting their score to 0*/
Update Customers
set score=0
Where score is NULL
SELECT*
FROM Customers
Where score is Null 


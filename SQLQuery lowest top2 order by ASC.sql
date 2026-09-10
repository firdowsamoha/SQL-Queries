--retreive the lowest two customers based on the score 
SELECT Top 2*
FROM customers
Order by score ASC
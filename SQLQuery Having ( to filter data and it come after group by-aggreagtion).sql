/* find the average score for each country considering 
only customers with a score not equal to 0 and return on those country
with an average score greater than 430*/
SELECT 
country,
Avg	(score) AS average_score
from customers 
Where score != 0
group by country
Having Avg(score)>430
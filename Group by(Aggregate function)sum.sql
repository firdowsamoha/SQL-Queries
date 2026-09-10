--find the total score for each country
SELECT
country,
sum (score)
from customers
group by country

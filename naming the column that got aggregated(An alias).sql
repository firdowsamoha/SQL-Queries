--find the total score for each country
SELECT
country,
sum (score) AS total_score
from customers
group by country

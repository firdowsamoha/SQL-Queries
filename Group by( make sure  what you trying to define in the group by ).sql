--find the total score for each country
SELECT
first_name,
country,
sum (score) AS total_score
from customers
group by country,first_name

--finad the total score and total number of customers for each country
SELECT
country,
sum (score) AS total_score,
count (id) AS total_customers
from customers
group by country

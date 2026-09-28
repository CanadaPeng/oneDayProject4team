-- 고액 거래의 특징

SELECT
    t.transaction_id,
    t.date,
    t.time,
    t.amount,
    c.category_name,
    t.type,
    t.channel,
    u.age_group,
    u.occupation,
    m.merchant_name,
    m.sales_channel,
    m.region AS merchant_region
FROM transactions AS t
JOIN categories AS c
    ON t.category = c.category
JOIN customers AS u
    ON t.customer_id = u.customer_id
JOIN merchants AS m
    ON t.merchant_id = m.merchant_id
WHERE t.amount >= 150000
ORDER BY t.amount DESC, t.transaction_id;


-- 카테고리별 지출 금액·건수·비중

SELECT
    t.category,
    c.category_name,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    ROUND(AVG(t.amount), 0) AS avg_amount,
    ROUND(
        100.0 * SUM(t.amount)
        / (SELECT SUM(amount) FROM transactions),
        2
    ) AS amount_share_pct
FROM transactions AS t
JOIN categories AS c
    ON t.category = c.category
GROUP BY t.category, c.category_name
ORDER BY total_amount DESC;



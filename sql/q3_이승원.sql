-- 월·요일·시간대별 지출 패턴

WITH periods AS (
    SELECT
        'month' AS period_type,
        strftime('%m', date) AS period_value,
        amount
    FROM transactions

    UNION ALL

    SELECT
        'weekday' AS period_type,
        strftime('%w', date) AS period_value,
        amount
    FROM transactions

    UNION ALL

    SELECT
        'hour' AS period_type,
        substr(time, 1, 2) AS period_value,
        amount
    FROM transactions
)
SELECT
    period_type,
    period_value,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount,
    ROUND(AVG(amount), 0) AS avg_amount
FROM periods
GROUP BY period_type, period_value
ORDER BY
    CASE period_type
        WHEN 'month' THEN 1
        WHEN 'weekday' THEN 2
        WHEN 'hour' THEN 3
    END,
    period_value;
-- Transaction type volume and value
SELECT tt.transaction_type,
       COUNT(*) AS transaction_count,
       ROUND(SUM(f.amount), 2) AS total_amount,
       ROUND(AVG(f.amount), 2) AS average_amount
FROM fact_transactions f
JOIN dim_transaction_type tt USING (transaction_type_key)
GROUP BY tt.transaction_type
ORDER BY transaction_count DESC;

-- Fraud analysis
SELECT tt.transaction_type,
       COUNT(*) FILTER (WHERE f.is_fraud) AS fraudulent_transactions,
       COUNT(*) AS total_transactions,
       ROUND(COUNT(*) FILTER (WHERE f.is_fraud) * 100.0 / NULLIF(COUNT(*), 0), 2) AS fraud_percent
FROM fact_transactions f
JOIN dim_transaction_type tt USING (transaction_type_key)
GROUP BY tt.transaction_type
ORDER BY fraudulent_transactions DESC;

-- Top senders by transaction value
SELECT s.sender_account,
       COUNT(*) AS transaction_count,
       ROUND(SUM(f.amount), 2) AS total_sent
FROM fact_transactions f
JOIN dim_sender s USING (sender_key)
GROUP BY s.sender_account
ORDER BY total_sent DESC
LIMIT 10;

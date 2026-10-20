-- Dialect: portable ANSI-style SQL; minor syntax adjustments may be needed.
-- transactions: Time, V1..V28, Amount, Class. Optional scored_transactions:
-- transaction_index, actual_class, model, predicted_label, fraud_probability.
-- Load source or generated CSVs with your database CSV import tool. These examples have not been executed.
SELECT COUNT(*) total_transactions, SUM(CASE WHEN Class=1 THEN 1 ELSE 0 END) fraud_count,
  1.0*SUM(CASE WHEN Class=1 THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0) fraud_rate FROM transactions;
SELECT Class, COUNT(*) transaction_count, SUM(Amount) total_amount, AVG(Amount) average_amount,
  MIN(Amount) minimum_amount, MAX(Amount) maximum_amount FROM transactions GROUP BY Class;
SELECT CASE WHEN Amount<10 THEN '0-<10' WHEN Amount<100 THEN '10-<100' WHEN Amount<500 THEN '100-<500' ELSE '500+' END amount_band,
 COUNT(*) transaction_count, SUM(CASE WHEN Class=1 THEN 1 ELSE 0 END) fraud_count,
 1.0*SUM(CASE WHEN Class=1 THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0) fraud_rate
FROM transactions GROUP BY CASE WHEN Amount<10 THEN '0-<10' WHEN Amount<100 THEN '10-<100' WHEN Amount<500 THEN '100-<500' ELSE '500+' END;
SELECT model,
 SUM(CASE WHEN actual_class=1 AND predicted_label=1 THEN 1 ELSE 0 END) true_positives,
 SUM(CASE WHEN actual_class=0 AND predicted_label=1 THEN 1 ELSE 0 END) false_positives,
 SUM(CASE WHEN actual_class=1 AND predicted_label=0 THEN 1 ELSE 0 END) false_negatives,
 SUM(CASE WHEN actual_class=0 AND predicted_label=0 THEN 1 ELSE 0 END) true_negatives
FROM scored_transactions GROUP BY model;
SELECT model,predicted_label,COUNT(*) transaction_count,AVG(fraud_probability) average_fraud_probability,
 SUM(CASE WHEN actual_class=1 THEN 1 ELSE 0 END) actual_fraud_count
FROM scored_transactions GROUP BY model,predicted_label;

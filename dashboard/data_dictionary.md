# Power BI data dictionary and model map

## Source population boundaries

Keep three analytical populations visibly separate:

1. **Full historical transactions**: `data/creditcard.csv`, 284,807 rows, 31 columns. Use for Page 1 descriptive KPIs and charts. `Class` is the observed source label.
2. **Final model test holdout**: `outputs/scored_transactions.csv` (113,896 rows = 56,948 transactions × 2 models), with actual labels and model predictions. Use this and the verified aggregate `model_comparison.csv` / `confusion_matrices.csv` for Page 2 test evaluation.
3. **Training-side validation**: `outputs/threshold_analysis.csv` (10 rows = 2 models × 5 thresholds), with threshold diagnostics on 45,613 validation transactions. Never combine these counts with final test metrics.

The source CSV is available locally. No additional transaction key is present in its columns. `scored_transactions.transaction_index` is the zero-based row index used by the Python loader; the Power BI model intentionally does not relate it to `Transactions`. This avoids filtering the full historical population through the test subset and protects Page 1 scope. Do not create relationships among fact tables.

## Tables to import

| Power BI table name | Source | Grain / rows | Use |
|---|---|---:|---|
| `Transactions` | `data/creditcard.csv` | One historical transaction / 284,807 | Page 1 full dataset |
| `ScoredHoldout` | `outputs/scored_transactions.csv` | One model prediction per holdout transaction / 113,896 | Page 2 score distributions and record-level evaluation |
| `ModelMetrics` | `outputs/model_comparison.csv` | One row per model / 2 | Authoritative final test metrics at threshold 0.5 |
| `ConfusionCounts` | `outputs/confusion_matrices.csv` | One model × actual class × predicted class / 8 | Page 2 confusion matrix at threshold 0.5 |
| `ThresholdValidation` | `outputs/threshold_analysis.csv` | One model × threshold / 10 | Validation-only threshold trade-offs |

Optional QA-only inputs:

- `outputs/fraud_summary.csv`: two rows (one per actual class) aggregated from the full dataset. Useful for reconciling Page 1 counts and amounts. The `fraud_rate` column is repeated on both rows; do not sum it.
- `outputs/sensitivity_comparison.csv`: four rows comparing former row-random and corrected grouped splits. Keep out of primary performance visuals; it is audit context.
- `outputs/split_audit.csv`: two rows documenting duplicate-group crossing in each split. Audit context only.

## Field definitions and data types

### `Transactions` (full historical population)

| Column(s) | Source type | Meaning / Power BI type |
|---|---|---|
| `Time` | int64 | Elapsed seconds from the dataset start; Whole Number. It is not a timestamp or time of day. |
| `V1`–`V28` | float64 | Anonymized PCA components; Decimal Number. They have no supplied business labels. |
| `Amount` | float64 | Transaction amount; Decimal Number. Source currency is unspecified. Format as `#,##0.00`; do not label RM/MYR. |
| `Class` | int64 | Actual historical label: 0 legitimate, 1 fraud; Whole Number. |
| Power BI calculated: `Actual Class Label` | Text | Readable label derived from `Class`; actual source label. |
| Power BI calculated: `AmountBand`, `AmountBandSort` | Text / Whole Number | Coarse display band and its numeric sort key. |
| Power BI calculated: `ElapsedHour` | Whole Number | `INT(Time / 3600)`; elapsed hour, not clock time. |

This file includes 492 frauds (0.172749% of all rows), 1,081 duplicate rows beyond first copies, and no missing values. Do not describe `Class` as a model prediction.

### `ScoredHoldout` (final test holdout)

| Column | Source type | Meaning / Power BI type |
|---|---|---|
| `transaction_index` | int64 | Original zero-based row index; Whole Number; not a field in the full CSV. |
| `actual_class` | int64 | Observed target on the holdout: 0 legitimate, 1 fraud; Whole Number. |
| `model` | string | `Logistic Regression` or `Random Forest`; Text. |
| `predicted_label` | int64 | Model-generated label at threshold 0.5; Whole Number. |
| `fraud_probability` | float64 | Model-generated fraud score in [0,1]; Decimal Number / Percentage display. |
| Power BI calculated: `Actual Class Label` | Text | Readable label derived from `actual_class`. |
| Power BI calculated: `Probability Bin Lower`, `Probability Bin Label` | Decimal / Text | 5 percentage-point display bins derived from model scores. |

There are 56,948 unique holdout transactions and 96 frauds (0.168575% prevalence). Each transaction appears once per model. The exported file omits Amount and PCA features; it cannot support transaction-amount analysis or join to Page 1 without adding a source index in exactly the original row order. No such join is required for this report.

### `ModelMetrics` (final holdout aggregate)

| Column | Type | Meaning |
|---|---|---|
| `model` | Text | Model name; two rows total. |
| `threshold` | Decimal | Final test label threshold, 0.5. |
| `evaluation_count` | Whole Number | Holdout transaction count, 56,948 for each model. |
| `fraud_prevalence` | Decimal | Holdout actual fraud rate, 96 / 56,948. |
| `accuracy`, `precision`, `recall`, `f1`, `average_precision`, `roc_auc` | Decimal | Verified test metrics. Average Precision is the PR ranking summary. |
| `true_positives`, `false_positives`, `false_negatives`, `true_negatives` | Whole Number | Final test confusion counts at threshold 0.5. |

Use this aggregate for official test metrics. Precision, Recall, and F1 may also be derived from its confusion counts; Accuracy, Average Precision, ROC-AUC, and prevalence can be read from this two-row table. Do not aggregate rates across models as if the models were one combined classifier.

### `ConfusionCounts` (final test)

`model` (Text), `threshold` (Decimal, 0.5), `actual_class` (Whole Number, 0/1), `predicted_label` (Whole Number, 0/1), and `count` (Whole Number). Power BI calculated text columns `Actual Class Label` and `Predicted Class Label` display “Legitimate” / “Fraud”. Eight rows give a 2 × 2 matrix for each model. These counts must reconcile to `ModelMetrics`.

### `ThresholdValidation` (validation only)

`model` (Text), `evaluation_split` (Text; all rows say `validation`), `threshold` (Decimal: 0.10, 0.25, 0.50, 0.75, 0.90), `evaluation_count` (Whole Number: 45,613), `fraud_count` (Whole Number: 83), `precision`, `recall`, `f1` (Decimal), and TP/FP/FN/TN columns (Whole Number). These are validation diagnostics, not final test metrics and not selected operating thresholds.

## Relationships

Create a DAX calculated table `DimModel` as described in `dax_measures.dax`. Relate `DimModel[model]` to `model` in `ScoredHoldout`, `ModelMetrics`, `ConfusionCounts`, and `ThresholdValidation`. The scored, confusion, and validation tables are one-to-many and can use single-direction filtering from `DimModel`. `ModelMetrics` currently has one row per model, so its relationship is one-to-one and Power BI filters both directions; keep the model tables disconnected from each other and review visual interactions. If you prefer to avoid this one-to-one relationship, leave `ModelMetrics` unlinked and use its own `model` field in metric visuals. Model names are the valid shared key.

Keep `Transactions` disconnected from `DimModel` and the holdout/validation tables. There is no imported date, merchant, customer, or geography dimension. This is deliberate, not a missing relationship.

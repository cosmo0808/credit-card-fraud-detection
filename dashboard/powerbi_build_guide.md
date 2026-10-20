# Power BI Desktop build guide (Windows)

This guide builds a report manually from the verified project files. The report has not been generated or tested in Power BI Desktop. Save the completed file as `dashboard/credit_card_fraud_risk_analytics.pbix` in this project.

## 1. Import the CSVs

In Power BI Desktop, choose **Get data > Text/CSV** and import:

1. `data/creditcard.csv` → rename query/table to `Transactions` (full historical descriptive population).
2. `outputs/scored_transactions.csv` → `ScoredHoldout` (holdout prediction-level scores; two rows per transaction, one per model).
3. `outputs/model_comparison.csv` → `ModelMetrics` (authoritative final test metrics, one row per model).
4. `outputs/confusion_matrices.csv` → `ConfusionCounts` (test confusion matrix counts at 0.5).
5. `outputs/threshold_analysis.csv` → `ThresholdValidation` (validation-only threshold comparisons).

Optional QA inputs: `outputs/fraud_summary.csv`, `outputs/sensitivity_comparison.csv`, and `outputs/split_audit.csv`. These are not needed for the two report pages. Do not import the full CSVs into one appended table.

## 2. Set types in Power Query

Select **Transform Data**. Set:

- `Transactions[Time]` and `Transactions[Class]`: Whole Number.
- `Transactions[Amount]` and `V1`–`V28`: Decimal Number.
- `ScoredHoldout[transaction_index]`, `actual_class`, `predicted_label`: Whole Number; `model`: Text; `fraud_probability`: Decimal Number.
- `ModelMetrics[model]`: Text; threshold and metric columns: Decimal Number; evaluation_count and confusion counts: Whole Number.
- `ConfusionCounts[model]`: Text; threshold: Decimal Number; actual_class, predicted_label, count: Whole Number.
- `ThresholdValidation[model]`, `evaluation_split`: Text; threshold and metrics: Decimal Number; counts: Whole Number.

For Amount, use numeric format with two decimals and thousands separators. The dataset does not specify its currency, so do not assign a MYR/RM symbol. Keep fraud probabilities as decimals for calculations; display them as percentages only where appropriate.

Do not sort, filter, or remove rows from `Transactions`. Do not add an index to create a relationship to scored rows. Choose **Close & Apply**.

## 3. Create model dimension and relationships

Open **Model view**. Create a calculated table by selecting **New table** and pasting the `DimModel` expression from `dax_measures.dax`. Create relationships from `DimModel[model]` to `model` in `ScoredHoldout`, `ModelMetrics`, `ConfusionCounts`, and `ThresholdValidation`. Use single-direction filtering from DimModel for the one-to-many scored, confusion, and validation relationships. The two-row `ModelMetrics` table is unique on model, so its relationship is one-to-one; Power BI enforces bidirectional filtering for one-to-one relationships. This model has no links between fact tables and `Transactions` remains disconnected, so the path is unambiguous. If you choose not to use that one-to-one relationship, leave `ModelMetrics` unlinked and use its own `model` field in metric visuals (the DAX measures read their fact-table filter context). Verify there are no duplicate or blank model names. See [Microsoft's relationship guidance](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand).

Keep `Transactions` disconnected from all model tables. It is the full dataset, while the other tables represent test/validation subsets. No date, customer, merchant, or geography relationships exist in the source.

## 4. Create measures and calculated columns

Choose **Modeling > New measure** or **New column** and add expressions from `dax_measures.dax` to their named tables. The file includes full-dataset transaction KPIs, test metrics, confusion/score counts, and validation-only threshold measures. Set formatting in the **Measure tools** ribbon:

- Rates and model metrics: Percentage, 2–3 decimal places.
- Transaction amounts: Decimal number with thousands separator and 2 decimals, no currency symbol.
- Counts: Whole number with thousands separator.
- `DimModel[model]`: use as a single-select slicer on Page 2. Test metric measures intentionally return blank unless one model is selected.

Create the calculated columns shown under the relevant table comments in the DAX file. On Page 1, add the class label, amount band, sort key, and elapsed-hour fields to `Transactions`; sort `AmountBand` by `AmountBandSort` and `Probability Bin Label` by `Probability Bin Lower`. On Page 2, add the actual-class label and probability-bin fields to `ScoredHoldout`, and actual/predicted labels to `ConfusionCounts`. The DAX file uses the new-column formula-bar syntax: choose the table first, then paste the expression. Do not use a `Class` label as a model prediction or vice versa.

## 5. Build Page 1 — Transaction & Fraud Overview

Rename the first page **Transaction & Fraud Overview — Full Dataset**. Add five cards:

- **Total Transactions** → `[Total Transactions (Full Dataset)]`.
- **Fraudulent Transactions** → `[Fraudulent Transactions (Full Dataset)]`.
- **Fraud Rate** → `[Fraud Rate (Full Dataset)]`.
- **Fraud Transaction Amount** → `[Fraud Transaction Amount (Full Dataset)]`.
- **Average Transaction Amount** → `[Average Transaction Amount (Full Dataset)]`.

Use the chart designs in `dashboard_design.md`:

| Visual type | Fields / measures | Axis and legend | Question answered |
|---|---|---|---|
| Clustered bar | `Transactions[Actual Class Label]`; `[Total Transactions (Full Dataset)]` | Category axis: actual class; value axis: count; no legend | How imbalanced are the actual labels? |
| 100% stacked column | `Transactions[AmountBand]`; `Transactions[Actual Class Label]`; `[Transaction Mix by Amount Band]` | X: amount band; Legend: actual class; Y: percentage within class | How does each actual class distribute across broad amount ranges? |
| Line or column | `Transactions[AmountBand]`; `[Fraud Rate (Full Dataset)]` | X: sorted amount band; Y: percentage; tooltip: fraud count and transaction count | Does observed fraud prevalence vary by amount band? |
| Line | `Transactions[ElapsedHour]`; transaction count and fraud count | X: elapsed hour; Y: count; tooltip: actual fraud count | How does activity change across the source sequence? |

Add slicers for actual class, AmountBand, and ElapsedHour. Use concise tooltips and page subtitles that identify “Full historical dataset; actual labels.” Do not label elapsed hours as clock time.

## 6. Build Page 2 — Model Performance & Risk Monitoring

Add a single-select model slicer using `DimModel[model]`. Set its default to Logistic Regression or make the user select a model. Add KPI cards for Precision, Recall, F1, Average Precision, and ROC-AUC using the test measures.

| Visual type | Fields / measures | Axis and legend | Question answered |
|---|---|---|---|
| Matrix | `ConfusionCounts[Actual Class Label]`, `ConfusionCounts[Predicted Class Label]`, `[Confusion Matrix Count (Test)]` | Rows: actual class; columns: predicted class; values: count | What errors did the selected model make at 0.5? |
| Clustered bar/matrix | ModelMetrics model and metric columns or measures | Category: model; values: Precision, Recall, F1, AP, ROC-AUC | How do model quality measures compare on the test holdout? |
| Clustered column | ModelMetrics model; FP and FN values | X: model; Y: count; series: FP/FN | How many false alerts and missed frauds occurred? |
| Binned column | `ScoredHoldout[Probability Bin Label]`; `[Scored Holdout Rows (Selected Model)]`; `ScoredHoldout[Actual Class Label]` | X: score band; Legend: actual class; Y: row count | How are holdout scores distributed by actual class? |
| Line | ThresholdValidation threshold; Validation Precision and Validation Recall | X: threshold sorted ascending; Y: percentage; series: precision/recall | How do validation trade-offs change with threshold? |
| Clustered column/table | ThresholdValidation threshold; Validation FP/FN/Flagged Transactions | X/rows: threshold; values: counts | What investigation workload and missed-fraud trade-offs appear in validation? |

Use clear labels such as **Final test holdout (threshold 0.50)** and **Training-side validation (threshold comparison)**. Keep threshold charts visibly marked as validation. Do not state a threshold is optimal or best. Add a text note that high Accuracy can be misleading with rare fraud and that historical metrics do not guarantee real-world performance.

## 7. Verify against Python outputs

Before formatting, compare the report with these values:

- Full dataset: 284,807 transactions, 492 actual frauds, fraud rate 0.172749%.
- Holdout: 56,948 transactions, 96 frauds (0.168575%).
- Logistic Regression at test threshold 0.5: TP 84, FP 1,334, FN 12, TN 55,518; precision 0.059238, recall 0.875000, F1 0.110964, accuracy 0.976364, AP 0.674710, ROC-AUC 0.966023.
- Random Forest at test threshold 0.5: TP 68, FP 2, FN 28, TN 56,850; precision 0.971429, recall 0.708333, F1 0.819277, accuracy 0.999473, AP 0.808699, ROC-AUC 0.940928.
- Validation threshold rows: check `evaluation_split` is `validation`; they cover 45,613 validation rows and 83 frauds per model.

Use `outputs/model_comparison.csv`, `confusion_matrices.csv`, and `threshold_analysis.csv` as the source of truth, not manually entered DAX constants.

## 8. Add report title, polish, and save

Use a simple white/light background, one dark blue accent, one contrasting fraud color, consistent typography, aligned cards, and concise labels. Titles should state scope and actual/predicted status. Avoid unnecessary decoration and unsupported business dimensions. Save as `dashboard/credit_card_fraud_risk_analytics.pbix` only after checking both pages and slicers in Power BI Desktop.

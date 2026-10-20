# Power BI dashboard QA checklist

## Data scope and model

- [ ] Page 1 uses `Transactions` from the full 284,807-row historical CSV.
- [ ] Page 1 fraud KPIs use actual `Transactions[Class]`; captions say actual / historical fraud labels.
- [ ] Page 2 final model metrics use `ModelMetrics`, `ConfusionCounts`, and/or `ScoredHoldout` for the 56,948-row final holdout only.
- [ ] Threshold charts use `ThresholdValidation` and are labeled validation, not final test.
- [ ] Model slicer filters each model-specific table through `DimModel`.
- [ ] `Transactions` remains disconnected from model/holdout tables; Page 2 filters cannot change Page 1 population.
- [ ] No invented date, customer, merchant, geography, currency, or other business dimensions appear.
- [ ] Amount has numeric formatting but no RM/MYR symbol because the source currency is unspecified.
- [ ] `Time` is labeled elapsed seconds/hours from dataset start, never clock time or a calendar date.

## Figure reconciliation

- [ ] Full dataset count = 284,807; actual fraud count = 492; prevalence = 0.172749%.
- [ ] Holdout count = 56,948; actual fraud count = 96; prevalence = 0.168575%.
- [ ] Logistic Regression test confusion matrix at 0.5 is `[[55,518, 1,334], [12, 84]]` (actual rows, predicted columns).
- [ ] Random Forest test confusion matrix at 0.5 is `[[56,850, 2], [28, 68]]`.
- [ ] Test Precision, Recall, F1, Accuracy, Average Precision, and ROC-AUC match `outputs/model_comparison.csv` for the selected model.
- [ ] Confusion matrix total for each model is 56,948 and all counts reconcile to `model_comparison.csv`.
- [ ] `ScoredHoldout` contains 113,896 rows: 56,948 transactions for each of two models; labels and probabilities are not duplicated or misaligned.
- [ ] Validation figures show 45,613 rows / 83 frauds per model and are sourced from `threshold_analysis.csv` only.
- [ ] No validation threshold is shown as selected or tested on the final holdout.

## Communication and visual quality

- [ ] High Accuracy warning is visible: fraud prevalence is very low, so accuracy alone can hide missed fraud.
- [ ] Page titles and chart titles identify full dataset, test holdout, or validation scope.
- [ ] Actual target labels are distinct from model-generated labels and probabilities.
- [ ] FP is described as a legitimate transaction flagged; FN as a fraudulent transaction missed.
- [ ] Ranking metrics (Average Precision / ROC-AUC) are distinguished from confusion counts at threshold 0.5.
- [ ] Tooltips, labels, percentage precision, and number formatting are readable; amount uses two decimals.
- [ ] Amount bands are sorted by the numeric sort field; threshold axis is sorted ascending.
- [ ] Historical results are not presented as a guarantee of future or production performance.
- [ ] The `.pbix` opens in Power BI Desktop and each slicer and visual has been checked after save.

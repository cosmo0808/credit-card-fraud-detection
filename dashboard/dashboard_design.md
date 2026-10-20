# Power BI dashboard implementation plan

Use `data_dictionary.md`, `dax_measures.dax`, and `powerbi_build_guide.md` as the implementation package. The report has two pages and keeps the source population, final test holdout, and training-side validation results separate. No `.pbix` has been generated.

## Page 1 — Transaction & Fraud Overview (full historical dataset)

All visuals below use `Transactions` from the full `data/creditcard.csv` source and actual `Class` labels. They are descriptive and must not use model-generated labels.

| Visual | Business question | Type / fields | Configuration and tooltip |
|---|---|---|---|
| Total Transactions | How many historical records are included? | Card: `[Total Transactions (Full Dataset)]` | Full dataset scope label. |
| Fraudulent Transactions | How many records have observed fraud labels? | Card: `[Fraudulent Transactions (Full Dataset)]` | Filter is `Class = 1`; actual labels. |
| Fraud Rate | What share of this historical source is labeled fraud? | Card: `[Fraud Rate (Full Dataset)]` | Percentage, 3 decimal places; full dataset scope. |
| Fraud Transaction Amount | What is the sum of Amount on rows labeled fraud? | Card: `[Fraud Transaction Amount (Full Dataset)]` | Numeric amount format `#,##0.00`; currency unit unspecified, so do not label MYR/RM. |
| Average Transaction Amount | What is the mean source Amount? | Card: `[Average Transaction Amount (Full Dataset)]` | Numeric amount format `#,##0.00`; all classes. |
| Class counts | How imbalanced are actual labels? | Clustered bar: Axis `Transactions[Actual Class Label]`; Values `[Total Transactions (Full Dataset)]` | Title states full historical dataset; tooltip includes fraud rate. |
| Amount distribution by class | How are actual transaction amounts distributed across coarse bands within each class? | 100% stacked column: Axis `Transactions[AmountBand]`; Legend `Transactions[Actual Class Label]`; Values `[Transaction Mix by Amount Band]` | Sort AmountBand by AmountBandSort. Tooltip: transaction count, average Amount. Bands are coarse, especially `500+`. |
| Fraud rate by amount band | Does observed fraud prevalence vary across the selected bands? | Line/column: Axis `Transactions[AmountBand]`; Values `[Fraud Rate (Full Dataset)]` | Tooltip: fraud count and total count. Interpret small fraud counts cautiously. |
| Activity across elapsed time | When in the dataset sequence is transaction volume concentrated? | Line: Axis `Transactions[ElapsedHour]`; Values transaction count; optional second line fraud count | Label axis “Elapsed hour from dataset start”; this is not time of day. Tooltip: transaction and actual fraud counts. |

Page 1 slicers: actual class label, AmountBand, and ElapsedHour. Avoid date, customer, merchant, geography, and currency slicers because those fields are not in the source.

## Page 2 — Model Performance & Risk Monitoring

Use a single-select `DimModel[model]` slicer. Test visuals use `ModelMetrics`, `ConfusionCounts`, or `ScoredHoldout`; threshold visuals use `ThresholdValidation` only. Put “Final test holdout, threshold 0.50” or “Training-side validation, threshold comparison” in each relevant title/subtitle.

| Visual | Business question | Type / fields | Configuration and tooltip |
|---|---|---|---|
| Test KPI cards | How does this model perform on the untouched holdout? | Cards: Test Precision, Test Recall, Test F1-score, Test Average Precision, Test ROC-AUC | Single model required. AP/ROC-AUC are ranking metrics; 0.5 confusion counts describe a separate operating point. |
| Confusion matrix | Which actual/predicted combinations occurred? | Matrix: Rows `ConfusionCounts[Actual Class Label]`; Columns `ConfusionCounts[Predicted Class Label]`; Values `[Confusion Matrix Count (Test)]` | Filter via model slicer; label 0=Legitimate, 1=Fraud; threshold 0.5. |
| Metric comparison | How do both models trade off metrics? | Clustered bar or matrix: `ModelMetrics[model]`; Accuracy, Precision, Recall, F1, Average Precision, ROC-AUC | Percentage formatting; title says test holdout. Do not combine or sum model rates. |
| False positives vs false negatives | How many legitimate cases were flagged versus fraud missed? | Clustered column: `ModelMetrics[model]`; false positives and false negatives | Test holdout at threshold 0.5. Include counts and descriptive labels. |
| Fraud score distribution | Do model score distributions differ for actual fraud and legitimate rows? | Binned column: `ScoredHoldout[Probability Bin Label]`; Legend `ScoredHoldout[Actual Class Label]`; Values scored row count | Model slicer; filter / facet by actual class. Scores are probabilities produced for holdout rows. |
| Validation precision/recall by threshold | What happens as validation threshold changes? | Line chart: X `ThresholdValidation[threshold]`; Values Validation Precision and Validation Recall | Model slicer; validation label in title. No threshold is selected. |
| Validation review workload | How do false alerts and missed fraud change by threshold? | Clustered columns or table: threshold; Validation FP, FN, and Flagged Transactions | Validation only. Flagged cases = TP + FP; counts are illustrative of this validation split, not operational forecasts. |

A high Accuracy is not sufficient for this rare-fraud dataset: a model could label nearly all transactions legitimate and still achieve very high accuracy while missing fraud. Random Forest has stronger precision and fewer false positives at threshold 0.5; Logistic Regression has higher recall. AP and ROC-AUC measure ranking across thresholds, not workload at the fixed 0.5 threshold. Do not claim universal model superiority.

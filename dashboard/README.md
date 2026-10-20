# Power BI implementation package

No `.pbix` has been generated. Follow [powerbi_build_guide.md](powerbi_build_guide.md) to build and verify the report in Power BI Desktop, then save it as `dashboard/credit_card_fraud_risk_analytics.pbix`.

The two pages are specified in [dashboard_design.md](dashboard_design.md). Refer to [data_dictionary.md](data_dictionary.md) for verified schemas and population boundaries, [dax_measures.dax](dax_measures.dax) for measures/calculated display fields, and [dashboard_qa_checklist.md](dashboard_qa_checklist.md) before saving.

Use full historical data for Page 1. Use the corrected final holdout outputs for Page 2 model metrics. Use `threshold_analysis.csv` only for training-side validation comparisons. Do not relate the full historical transaction table to holdout/validation tables.

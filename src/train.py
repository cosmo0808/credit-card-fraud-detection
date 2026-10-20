"""Train fraud baselines with duplicate-aware validation and holdout evaluation."""
from pathlib import Path
import argparse
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from .data_validation import load_transactions, TARGET, feature_group_ids, duplicate_split_audit
from .preprocessing import build_models
from .evaluate import evaluate_model, threshold_rows

ROOT = Path(__file__).resolve().parents[1]
THRESHOLD = 0.5

def group_split(X: pd.DataFrame, y: pd.Series, random_state: int = 42):
    """Create a reproducible stratified split of unique feature groups."""
    groups = feature_group_ids(X)
    group_table = pd.DataFrame({"group": groups.to_numpy(), "label": y.to_numpy()}).drop_duplicates("group")
    if group_table.groupby("group")["label"].nunique().gt(1).any():
        raise ValueError("Identical feature rows have conflicting targets; resolve or explicitly group these cases before splitting.")
    train_groups, holdout_groups = train_test_split(
        group_table["group"], test_size=0.2, stratify=group_table["label"], random_state=random_state
    )
    train_mask = groups.isin(set(train_groups))
    holdout_mask = groups.isin(set(holdout_groups))
    return X.loc[train_mask], X.loc[holdout_mask], y.loc[train_mask], y.loc[holdout_mask]

def fit_score(models, X_fit, y_fit, X_eval):
    predictions = {}
    for name, model in models.items():
        model.fit(X_fit, y_fit)
        predictions[name] = model.predict_proba(X_eval)[:, 1]
    return predictions

def run(data_path: Path = ROOT / "data" / "creditcard.csv", output_dir: Path = ROOT / "outputs", save_models: bool = False) -> None:
    df = load_transactions(data_path)
    X, y = df.drop(columns=TARGET), df[TARGET].astype(int)
    output_dir.mkdir(parents=True, exist_ok=True)
    X_train, X_test, y_train, y_test = group_split(X, y)
    test_audit = duplicate_split_audit(df, X_train.index, X_test.index)
    X_fit, X_valid, y_fit, y_valid = group_split(X_train, y_train, random_state=43)
    validation_models = build_models()
    valid_probabilities = fit_score(validation_models, X_fit, y_fit, X_valid)
    thresholds = [row for name, p in valid_probabilities.items() for row in threshold_rows(name, y_valid, p)]
    models = build_models()
    test_probabilities = fit_score(models, X_train, y_train, X_test)
    scored, comparisons, confusion_rows = [], [], []
    for name, probabilities in test_probabilities.items():
        labels = (probabilities >= THRESHOLD).astype(int)
        scored.append(pd.DataFrame({"transaction_index": X_test.index.to_numpy(), "actual_class": y_test.to_numpy(), "model": name, "predicted_label": labels, "fraud_probability": probabilities}))
        comparisons.append(evaluate_model(name, y_test, labels, probabilities, THRESHOLD))
        matrix = pd.crosstab(pd.Series(y_test.to_numpy(), name="actual_class"), pd.Series(labels, name="predicted_label")).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
        for actual in (0, 1):
            for predicted in (0, 1):
                confusion_rows.append({"model": name, "threshold": THRESHOLD, "actual_class": actual, "predicted_label": predicted, "count": int(matrix.loc[actual, predicted])})
        if save_models:
            joblib.dump(models[name], output_dir / ("logistic_regression.joblib" if name == "Logistic Regression" else "random_forest.joblib"))
    X_rand_train, X_rand_test, y_rand_train, y_rand_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    random_audit = duplicate_split_audit(df, X_rand_train.index, X_rand_test.index)
    random_probabilities = fit_score(build_models(), X_rand_train, y_rand_train, X_rand_test)
    sensitivity = []
    for name, probabilities in random_probabilities.items():
        row = evaluate_model(name, y_rand_test, (probabilities >= THRESHOLD).astype(int), probabilities, THRESHOLD)
        sensitivity.append({"split": "row_stratified (duplicate groups can cross)", **row, **{f"duplicate_audit_{k}": v for k,v in random_audit.items()}})
    for row in comparisons:
        sensitivity.append({"split": "group_stratified (corrected)", **row, **{f"duplicate_audit_{k}": v for k,v in test_audit.items()}})
    pd.concat(scored, ignore_index=True).to_csv(output_dir / "scored_transactions.csv", index=False)
    pd.DataFrame(comparisons).to_csv(output_dir / "model_comparison.csv", index=False)
    pd.DataFrame(thresholds).to_csv(output_dir / "threshold_analysis.csv", index=False)
    pd.DataFrame(confusion_rows).to_csv(output_dir / "confusion_matrices.csv", index=False)
    pd.DataFrame(sensitivity).to_csv(output_dir / "sensitivity_comparison.csv", index=False)
    pd.DataFrame([{"split": "group_stratified test", **test_audit}, {"split": "row_stratified sensitivity", **random_audit}]).to_csv(output_dir / "split_audit.csv", index=False)
    fraud = df.groupby(TARGET).agg(transaction_count=(TARGET,"size"), amount_total=("Amount","sum"), amount_mean=("Amount","mean"), amount_median=("Amount","median")).reset_index().rename(columns={TARGET:"actual_class"})
    fraud["class_label"] = fraud.actual_class.map({0:"Legitimate",1:"Fraud"}); fraud["fraud_rate"] = df[TARGET].mean()
    fraud.to_csv(output_dir / "fraud_summary.csv", index=False)
    print(f"Group-stratified split: train={len(X_train):,}, test={len(X_test):,}; test frauds={int(y_test.sum()):,}")
    print("Test duplicate audit:", test_audit)
    print(pd.DataFrame(comparisons).to_string(index=False))
    print("Validation threshold comparisons (no threshold selected):")
    print(pd.DataFrame(thresholds).to_string(index=False))
    print(f"Exports written to {output_dir}")

if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--save-models",action="store_true",help="Save fitted pipelines with joblib")
    run(save_models=parser.parse_args().save_models)

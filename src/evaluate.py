"""Metrics and threshold summaries for fraud classification."""
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

def evaluate_model(name, y_true, labels, probabilities, threshold: float) -> dict:
    """Return metrics and confusion counts for aligned predictions."""
    tn, fp, fn, tp = confusion_matrix(y_true, labels, labels=[0, 1]).ravel()
    return {"model": name, "threshold": threshold, "evaluation_count": len(y_true), "fraud_prevalence": float(pd.Series(y_true).mean()), "accuracy": accuracy_score(y_true, labels), "precision": precision_score(y_true, labels, zero_division=0), "recall": recall_score(y_true, labels, zero_division=0), "f1": f1_score(y_true, labels, zero_division=0), "average_precision": average_precision_score(y_true, probabilities), "roc_auc": roc_auc_score(y_true, probabilities), "true_positives": int(tp), "false_positives": int(fp), "false_negatives": int(fn), "true_negatives": int(tn)}

def threshold_rows(name, y_true, probabilities, thresholds=(0.10, 0.25, 0.50, 0.75, 0.90)) -> list[dict]:
    """Compare fixed thresholds on validation predictions only."""
    rows = []
    for threshold in thresholds:
        predicted = probabilities >= threshold
        tn, fp, fn, tp = confusion_matrix(y_true, predicted, labels=[0, 1]).ravel()
        rows.append({"model": name, "evaluation_split": "validation", "threshold": threshold, "evaluation_count": len(y_true), "fraud_count": int(pd.Series(y_true).sum()), "precision": precision_score(y_true, predicted, zero_division=0), "recall": recall_score(y_true, predicted, zero_division=0), "f1": f1_score(y_true, predicted, zero_division=0), "true_positives": int(tp), "false_positives": int(fp), "false_negatives": int(fn), "true_negatives": int(tn)})
    return rows

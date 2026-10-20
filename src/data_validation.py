"""Input checks for the credit card fraud dataset."""
from pathlib import Path
import pandas as pd

TARGET = "Class"
REQUIRED_COLUMNS = {"Time", "Amount", TARGET, *(f"V{i}" for i in range(1, 29))}

def load_transactions(path: str | Path) -> pd.DataFrame:
    """Load a CSV and validate its required columns and binary target."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Download creditcard.csv and place it at data/creditcard.csv.")
    frame = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    if frame[TARGET].isna().any() or not set(frame[TARGET].unique()).issubset({0, 1}):
        raise ValueError("Class must contain only non-null binary labels 0 and 1.")
    if frame.isna().any().any():
        raise ValueError("Dataset contains missing values; inspect and resolve them before training.")
    return frame


def feature_group_ids(frame: pd.DataFrame) -> pd.Series:
    """Return stable IDs grouping rows with identical predictor values."""
    return pd.util.hash_pandas_object(frame, index=False).astype("uint64")


def duplicate_split_audit(frame: pd.DataFrame, train_index, test_index) -> dict[str, int]:
    """Summarize exact duplicate rows and feature groups crossing a split."""
    feature_groups = feature_group_ids(frame.drop(columns=TARGET))
    grouped = pd.DataFrame({"group": feature_groups, "label": frame[TARGET]})
    conflicts = int((grouped.groupby("group")["label"].nunique() > 1).sum())
    train_groups = set(feature_groups.loc[train_index])
    test_groups = set(feature_groups.loc[test_index])
    crossing = train_groups & test_groups
    crossing_mask = feature_groups.isin(crossing)
    duplicate_groups = feature_groups.value_counts()
    return {
        "duplicate_extra_rows": int(frame.duplicated().sum()),
        "rows_in_duplicate_groups": int(frame.duplicated(keep=False).sum()),
        "duplicate_groups": int((duplicate_groups > 1).sum()),
        "conflicting_target_groups": int(conflicts),
        "cross_split_feature_groups": len(crossing),
        "cross_split_rows": int(crossing_mask.sum()),
    }

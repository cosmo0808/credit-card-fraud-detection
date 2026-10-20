"""Leakage-safe split and model pipelines."""
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

SCALED_COLUMNS = ["Time", "Amount"]

def build_models(random_state: int = 42) -> dict[str, Pipeline]:
    """Create baseline models; transformations are fitted inside each pipeline."""
    scale_time_amount = ColumnTransformer(
        [("scale_time_amount", StandardScaler(), SCALED_COLUMNS)], remainder="passthrough"
    )
    return {
        "Logistic Regression": Pipeline([
            ("preprocess", scale_time_amount),
            ("model", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=random_state)),
        ]),
        "Random Forest": Pipeline([
            ("model", RandomForestClassifier(n_estimators=100, class_weight="balanced_subsample", random_state=random_state, n_jobs=-1)),
        ]),
    }

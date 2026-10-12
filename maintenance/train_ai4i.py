"""Train an AI4I 2020 model; exclude all failure-mode targets and identifiers."""
import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURES = [
    "Type", "Air temperature [K]", "Process temperature [K]",
    "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]",
]
TARGET = "Machine failure"
NUMERICS = FEATURES[1:]


def read_ai4i(path):
    frame = pd.read_csv(path, encoding="utf-8-sig")
    missing = set(FEATURES + [TARGET]) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing AI4I columns: {sorted(missing)}")
    if not frame[TARGET].isin([0, 1]).all():
        raise ValueError("Machine failure must be binary")
    return frame


def train(path="data/public/ai4i2020.csv", output="models/ai4i_failure_model.joblib"):
    data = read_ai4i(path)
    x = data[FEATURES]
    y = data[TARGET].astype(int)
    if y.nunique() != 2:
        raise ValueError("Both failure classes are required")
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )
    prep = ColumnTransformer(
        [
            ("type", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["Type"]),
            ("numeric", "passthrough", NUMERICS),
        ]
    )
    pipeline = Pipeline([
        ("features", prep),
        ("model", HistGradientBoostingClassifier(
            random_state=42, max_iter=100, learning_rate=0.07
        )),
    ])
    pipeline.fit(x_train, y_train)
    scores = pipeline.predict_proba(x_test)[:, 1]
    predictions = (scores >= 0.5).astype(int)
    metrics = {
        "dataset": "AI4I 2020 (UCI; synthetic)",
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "test_failure_rate": float(y_test.mean()),
        "average_precision": float(average_precision_score(y_test, scores)),
        "roc_auc": float(roc_auc_score(y_test, scores)),
        "classification_report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
        "evaluation": "Single stratified random holdout; not temporal/asset-level validation",
    }
    artifact = Path(output)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, artifact)
    artifact.with_suffix(".metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/public/ai4i2020.csv")
    parser.add_argument("--output", default="models/ai4i_failure_model.joblib")
    args = parser.parse_args()
    print(json.dumps(train(args.csv, args.output), indent=2))

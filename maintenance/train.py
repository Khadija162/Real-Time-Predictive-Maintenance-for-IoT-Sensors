"""Group-aware machine-level holdout, preventing same-machine training/test leakage."""
import argparse
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from .data import FEATURES


def train(csv_path, output="models/failure_model.joblib"):
    frame = pd.read_csv(csv_path)
    required = set(FEATURES + ["machine_id", "failure"])
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing columns: {sorted(required-set(frame.columns))}")
    x = frame[FEATURES].apply(pd.to_numeric, errors="coerce")
    y = frame["failure"].astype(int)
    splitter = GroupShuffleSplit(test_size=.25, random_state=42)
    train_idx, test_idx = next(splitter.split(x, y, frame["machine_id"]))
    if y.iloc[train_idx].nunique() < 2 or y.iloc[test_idx].nunique() < 2:
        raise ValueError("Both partitions need examples of both classes; increase dataset size")
    model = HistGradientBoostingClassifier(max_iter=120, random_state=42)
    model.fit(x.iloc[train_idx], y.iloc[train_idx])
    probability = model.predict_proba(x.iloc[test_idx])[:, 1]
    results = {"train_rows": len(train_idx), "test_rows": len(test_idx),
        "test_average_precision": float(average_precision_score(y.iloc[test_idx], probability)),
        "test_roc_auc": float(roc_auc_score(y.iloc[test_idx], probability)),
        "holdout": "machine_id (GroupShuffleSplit)"}
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, target)
    target.with_suffix(".metrics.json").write_text(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/sensors.csv")
    parser.add_argument("--output", default="models/failure_model.joblib")
    args=parser.parse_args()
    print(json.dumps(train(args.csv,args.output),indent=2))

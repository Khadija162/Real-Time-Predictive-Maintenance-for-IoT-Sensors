from pathlib import Path
import pandas as pd
from maintenance.train_ai4i import FEATURES, TARGET, read_ai4i


def test_public_ai4i_schema():
    dataset = Path(__file__).resolve().parents[1] / "data/public/ai4i2020.csv"
    frame = read_ai4i(dataset)
    assert len(frame) == 10000
    assert set(frame[TARGET].unique()) == {0, 1}
    assert "TWF" not in FEATURES
    assert "HDF" not in FEATURES
    assert "Product ID" not in FEATURES
    assert set(FEATURES).issubset(frame.columns)


def test_ai4i_has_failure_cases():
    dataset = Path(__file__).resolve().parents[1] / "data/public/ai4i2020.csv"
    frame = pd.read_csv(dataset)
    assert frame["Machine failure"].sum() > 0

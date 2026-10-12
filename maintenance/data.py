"""Synthetic machine telemetry for reproducible offline demos. Not a public industry dataset."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

FEATURES = ["temperature", "vibration", "pressure", "rpm", "operating_hours"]


def generate(rows=10000, seed=42):
    rng = np.random.default_rng(seed)
    temperature = rng.normal(70, 12, rows).clip(20, 140)
    vibration = rng.gamma(2, 0.8, rows)
    pressure = rng.normal(5, 0.9, rows).clip(0.2, 12)
    rpm = rng.normal(1500, 280, rows).clip(200, 3500)
    hours = rng.uniform(0, 12000, rows)
    score = -7 + .055 * (temperature - 70) + .95 * vibration + .00025 * hours + .001 * (rpm - 1500) + .5 * abs(pressure - 5)
    risk = 1 / (1 + np.exp(-np.clip(score, -30, 30)))
    failure = rng.binomial(1, risk)
    return pd.DataFrame({"machine_id": [f"M-{i % 50:03d}" for i in range(rows)],
        "event_time": pd.date_range("2025-01-01", periods=rows, freq="min", tz="UTC").astype(str),
        "temperature": temperature, "vibration": vibration, "pressure": pressure,
        "rpm": rpm, "operating_hours": hours, "failure": failure})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--output", default="data/sensors.csv")
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    generate(args.rows).to_csv(path, index=False)
    print("Generated", path)

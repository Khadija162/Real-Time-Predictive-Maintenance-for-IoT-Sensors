"""Bronze / validated Silver / machine-level Gold Parquet pipeline."""
import argparse
from pathlib import Path
import pandas as pd


def run(path="data/sensors.csv", output="data"):
    frame=pd.read_csv(path)
    needed={"machine_id","event_time","temperature","vibration","pressure","rpm","operating_hours"}
    if not needed.issubset(frame.columns):
        raise ValueError(f"Missing columns: {sorted(needed-set(frame.columns))}")
    output=Path(output)
    for layer in ("bronze","silver","gold"):
        (output/layer).mkdir(parents=True,exist_ok=True)
    frame.to_parquet(output/"bronze"/"sensor_events.parquet", index=False)
    valid=frame["machine_id"].notna() & pd.to_datetime(frame["event_time"],errors="coerce",utc=True).notna()
    for col in ("temperature","vibration","pressure","rpm","operating_hours"):
        valid &= pd.to_numeric(frame[col],errors="coerce").notna()
    clean=frame.loc[valid].copy()
    clean.to_parquet(output/"silver"/"sensor_events.parquet",index=False)
    gold=clean.groupby("machine_id",as_index=False).agg(
        event_count=("machine_id","size"),mean_temperature=("temperature","mean"),
        mean_vibration=("vibration","mean"),max_operating_hours=("operating_hours","max"))
    gold.to_parquet(output/"gold"/"machine_health.parquet",index=False)
    return {"bronze":len(frame),"silver":len(clean),"rejected":int((~valid).sum()),"machines":len(gold)}


if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("--csv",default="data/sensors.csv")
    args=p.parse_args();print(run(args.csv))

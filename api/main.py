"""Read-only risk-scoring API: research demo, not autonomous maintenance control."""
import os
from functools import lru_cache
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from maintenance.data import FEATURES

app=FastAPI(title="IoT Predictive Maintenance API",version="0.1.0")


class SensorReading(BaseModel):
    model_config=ConfigDict(extra="forbid")
    temperature:float=Field(allow_inf_nan=False)
    vibration:float=Field(ge=0,allow_inf_nan=False)
    pressure:float=Field(ge=0,allow_inf_nan=False)
    rpm:float=Field(ge=0,allow_inf_nan=False)
    operating_hours:float=Field(ge=0,allow_inf_nan=False)


@lru_cache(maxsize=1)
def load_model():
    path=Path(os.getenv("MODEL_PATH","models/failure_model.joblib"))
    if not path.exists():
        raise FileNotFoundError("Model not trained. Run python -m maintenance.train")
    return joblib.load(path)  # Load only trusted local artifacts.


@app.get("/health")
def health():
    return {"status":"ok","model_available":Path(os.getenv("MODEL_PATH","models/failure_model.joblib")).exists()}


@app.post("/predict")
def predict(reading:SensorReading):
    try:
        model=load_model()
    except FileNotFoundError as exc:
        raise HTTPException(503,str(exc)) from exc
    frame=pd.DataFrame([reading.model_dump()])[FEATURES]
    probability=float(model.predict_proba(frame)[0,1])
    return {"failure_probability":round(probability,6),"alert":probability>=0.5,
            "message":"Research model score; human inspection required for any maintenance action"}

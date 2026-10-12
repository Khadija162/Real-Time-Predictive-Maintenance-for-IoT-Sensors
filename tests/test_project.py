import pandas as pd
from fastapi.testclient import TestClient
from maintenance.data import FEATURES,generate
from maintenance.etl import run
from api.main import app


def test_generator():
    df=generate(150,seed=123)
    assert len(df)==150
    assert set(FEATURES).issubset(df.columns)
    assert df["failure"].isin([0,1]).all()


def test_lakehouse(tmp_path):
    data=tmp_path/"sensors.csv"
    generate(80).to_csv(data,index=False)
    result=run(str(data),str(tmp_path/"lake"))
    assert result["bronze"]==80
    assert result["silver"]==80
    assert result["machines"]>0


def test_health():
    assert TestClient(app).get("/health").status_code==200


def test_invalid_prediction():
    assert TestClient(app).post("/predict",json={"temperature":60}).status_code==422

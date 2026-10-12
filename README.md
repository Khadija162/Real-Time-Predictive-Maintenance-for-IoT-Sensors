# Real-Time Predictive Maintenance for IoT Sensors

An **AI + advanced data engineering portfolio prototype** for predicting simulated machine failures using sensor telemetry. Includes batch Bronze/Silver/Gold lakehouse ETL, model training, a scoring API, a monitoring dashboard, optional Kafka-compatible streaming, Docker, CI and an Azure cloud blueprint.

> **Current state:** Source code and configuration have been committed. Model training, container runtime, CI, and cloud deployment have not yet been independently validated. Generated sensor data and risk labels are **synthetic**, not actual industrial failure observations.

## Architecture

```text
Sensor event generator (synthetic)
         |                           +--> Model training (machine-group holdout)
         v                           |
Kafka-compatible Redpanda (optional) |      +--> FastAPI /predict --> Streamlit UI
         |                           |      |
Streaming scoring consumer ----------+-----> Trained sklearn model
         |
Batch CSV --> Bronze Parquet --> Silver validated --> Gold machine-health Parquet
                                                    |
                                           Cloud roadmap: ADLS Gen2
```

## Local Windows quick start

Prerequisites: Python 3.11/3.12, optional Docker Desktop. Clone the repo:

```powershell
git clone https://github.com/Khadija162/Real-Time-Predictive-Maintenance-for-IoT-Sensors.git
cd Real-Time-Predictive-Maintenance-for-IoT-Sensors
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m maintenance.data --rows 10000
.\.venv\Scripts\python.exe -m maintenance.etl --csv data/sensors.csv
.\.venv\Scripts\python.exe -m maintenance.train --csv data/sensors.csv
.\.venv\Scripts\python.exe -m pytest -q
```

The generator creates a reproducible, labeled 50-machine simulation. Train and test machines do not overlap (GroupShuffleSplit); this does **not** prove future time-period performance.

## Run the application

Start API (terminal 1):

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

Start dashboard (terminal 2):

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

API documentation: http://localhost:8000/docs
Dashboard: http://localhost:8501

### Docker

Train the model locally first so `models/failure_model.joblib` exists:

```powershell
docker compose up --build
```

Optional Redpanda:

```powershell
docker compose --profile streaming up -d redpanda
.\.venv\Scripts\python.exe -m streaming.producer
.\.venv\Scripts\python.exe -m streaming.consumer
```

The consumer provides an at-least-once demo, not guaranteed exactly-once execution. The API is unauthenticated and is bound to localhost in Docker. **Do not publicly deploy without authentication and authorization.**

## Included modules

| Folder | Responsibility |
|---|---|
| `maintenance/data.py` | Synthetic telemetry generator |
| `maintenance/etl.py` | Local Bronze/Silver/Gold Parquet pipeline |
| `maintenance/train.py` | Predictive model + evaluation |
| `api/` | FastAPI prediction endpoint |
| `dashboard/` | Streamlit dashboard |
| `streaming/` | Redpanda/Kafka producer and consumer |
| `tests/` | Reproducible tests |
| `.github/workflows/` | Test and Docker build CI |
| `infra/terraform/` | Azure storage example (NOT deployed) |
| `docs/` | Architecture notes |

## Azure modernization roadmap

1. Azure IoT Hub and Event Hubs ingestion, with device identity and telemetry contracts.
2. Azure Databricks Spark Structured Streaming with Delta Lake and checkpointing on ADLS Gen2.
3. Model registry, feature tracking, delayed-label model evaluation and monitoring.
4. Container Apps + Entra ID for secured scoring APIs.
5. Azure Monitor + Application Insights alerts and optional read-only Llama incident investigation.
6. GitHub Actions release workflow and Terraform deployment gated by manual approval.

Terraform presently describes only an Azure resource group and ADLS Gen2 storage; **no Azure resources have been provisioned**. Azure subscriptions may incur charges if you apply the Terraform.

## Responsible evaluation

This model estimates probability for a **synthetic failure label**, not real remaining useful life. It must not autonomously stop machinery or approve maintenance activities. Evaluate on real labeled sensor data, calibrate probabilities and validate with maintenance engineers before real-world use.

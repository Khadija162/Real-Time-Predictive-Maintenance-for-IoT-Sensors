# IoT predictive maintenance platform

## Implemented demo
- Deterministic synthetic sensor telemetry (temperature, vibration, pressure, RPM, operating hours).
- Batch Bronze/Silver/Gold Parquet transformations and machine-level health aggregation.
- Machine-group holdout evaluation of a gradient-boosting classifier.
- FastAPI risk prediction and Streamlit control center.
- Optional Kafka-compatible Redpanda event producer/consumer.
- Docker Compose, GitHub Actions, Azure ADLS Gen2 Terraform sample.

## Cloud blueprint (not deployed)
IoT devices -> Azure IoT Hub / Event Hubs -> Azure Databricks (Spark Structured Streaming) -> ADLS Gen2/Delta Bronze/Silver/Gold -> Azure PostgreSQL or managed feature storage -> Azure Container Apps API -> web dashboard -> Azure Monitor, App Insights. Optional Llama incident triage should be read-only, grounded in measured alert evidence.

## Safety
These synthetic labels reflect a constructed simulation, not observed industrial failures. This is not a remaining-useful-life model or a safety-certified decision system. Require human maintenance engineer review.

# AI4I 2020 Predictive Maintenance Dataset

**File:** `ai4i2020.csv` (10,000 rows, 14 columns).

- **Official original publisher:** UCI Machine Learning Repository
- **Dataset:** AI4I 2020 Predictive Maintenance Dataset
- **Author:** Stephan Matzka
- **DOI:** https://doi.org/10.24432/C5HS5C
- **Official source:** https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/
- **Upstream copy used to retrieve CSV for this repository:** https://github.com/tayyabrehman96/XAI-PdMNet-Bench-Industry-5.0/blob/main/data/ai4i/ai4i2020.csv

**Attribution:** AI4I 2020 Predictive Maintenance Dataset. (2020). UCI Machine Learning Repository. DOI: 10.24432/C5HS5C. Based on S. Matzka (2020), *Explainable Artificial Intelligence for Predictive Maintenance Applications*.

**Changes:** The CSV content was copied from the linked upstream mirror with the UTF-8 BOM removed; no records, fields or labels were intentionally altered. Included here under CC BY 4.0, independent of this project's code licensing.

**Important:** AI4I is **synthetic research data**, not measurements from deployed industrial sensors. `Machine failure` is a binary target. `TWF`, `HDF`, `PWF`, `OSF`, `RNF` are failure-mode labels and **must not be used as prediction-time features**. `UDI` and `Product ID` are identifiers, not sensor features.

## Train the separate AI4I model

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m maintenance.train_ai4i --csv data/public/ai4i2020.csv
```

Outputs: `models/ai4i_failure_model.joblib` and `models/ai4i_failure_model.metrics.json`.

The existing synthetic-sensor model uses a **different feature contract** (temperature, vibration, pressure, RPM, operating hours); do not point the current `/predict` API at the AI4I model. To serve AI4I inference, add a separate validated endpoint using its six original feature names.

Evaluation is a stratified row holdout, not chronological or across independently identified machines; it does not demonstrate production generalization.

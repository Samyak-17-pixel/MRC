# src/ml/experiments/ — Operational Forecasts

Live-style experiments on top of trained models (no retraining).

## Purpose

Score the **latest feature day** for onset probability at 3/7/14 days, and optionally verify catalogue events for a calendar year on the correct pre-onset windows.

## Contents

| Script | Role |
|--------|------|
| `06_predict_current.py` | Latest-day forecast + year verification |

## How to run

```bash
.venv/bin/python src/ml/experiments/06_predict_current.py
```

## Outputs

| File | Meaning |
|------|---------|
| `src/ml/outputs/forecasts/latest_forecast.csv` | P(onset) + alert per region×horizon |
| `src/ml/outputs/forecasts/year_verification_YYYY.csv` | Pre-onset hit rates vs Hobday starts |
| Dated copies such as `forecast_YYYYMMDD.csv` | Snapshots |

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `best_models.csv`, trained `.joblib`, feature CSVs, MHW catalogues | Operations / dashboards; root README reporting |

## Critical interpretation

- **ML forecast ≠ catalogue annual count.** Scoring 2025-12-31 answers “will a new event start soon?” — not “how many started in 2025?”
- Year-end P≈0 with cool SST is expected.
- 2025 verification at P≥0.25: **11/13** (3d), **12/13** (7d), **13/13** (14d).

Alert: HIGH ≥0.50 · MODERATE ≥0.25 · LOW otherwise.

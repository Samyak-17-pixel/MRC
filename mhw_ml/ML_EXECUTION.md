# MHW ML Model — Execution Guide

**Project:** Bay of Bengal Marine Heatwave Onset Forecasting  
**Author:** Samyak Kumar  
**Institution:** Maritime Research Center (MRC)  
**Module location:** `/home/samyak/mrc_ws/mhw_ml/`  
**Last updated:** 2026-07-13

> This document describes **everything** the ML module does — data, labels, features, models, validation, outputs, and how to run it. It is self-contained and separate from `PROJECT.md`.

---

## 1. Objective

Build machine learning models that predict whether a **new Marine Heatwave (MHW)** will **start** in the Bay of Bengal within the next **3, 7, or 14 days**, using only **recent and current** observations.

This is an **early-warning** task, not a nowcast of ongoing events.

---

## 2. Prediction Task

### 2.1 MHW definition (consistent with main project)

Following **Hobday et al. (2016)**:
- Daily SST exceeds the **90th-percentile** seasonal threshold
- Condition persists for **≥ 5 consecutive days**

### 2.2 Target variable

For each day `t` and each region, we define:

```
onset_Hd = 1   if a new MHW event STARTS on any day in (t, t+H]
           0   otherwise
```

Where `H ∈ {3, 7, 14}` days.

**Example:** If an event starts on 2024-04-14, then `onset_7d = 1` for all days from 2024-04-07 to 2024-04-13.

### 2.3 Why onset prediction?

- Directly actionable for early warning
- Aligns with your 117 detected historical events
- Avoids trivial prediction during ongoing events (most in-event days have `onset_7d = 0`)

---

## 3. Module Structure

```
mhw_ml/
├── ML_EXECUTION.md          ← this file
├── config/
│   └── model_config.yaml    ← horizons, splits, model hyperparameters
├── scripts/
│   ├── common.py            ← shared utilities
│   ├── 01_build_dataset.py  ← feature engineering + labels
│   ├── 02_train_baselines.py
│   ├── 03_train_models.py
│   ├── 04_evaluate_models.py
│   ├── 05_explain_models.py
│   ├── 06_predict_current.py
│   └── run_pipeline.py      ← orchestrator
├── data/
│   ├── processed/           ← daily feature tables (parquet + csv)
│   └── splits/              ← train / val / test CSVs
├── models/
│   ├── baselines/           ← logistic regression
│   ├── north/               ← per-region ML models
│   ├── central/
│   └── south/
├── outputs/
│   ├── metrics/             ← evaluation CSVs
│   ├── figures/             ← ROC, PR, confusion matrices
│   ├── shap/                ← feature importance / SHAP plots
│   └── forecasts/           ← latest predictions
└── logs/
    └── pipeline.log
```

---

## 4. Data Sources (read from main project)

The ML module **does not duplicate** raw data. It reads from `results/`:

| Source | Path | Used for |
|--------|------|----------|
| Regional SST | `results/{region}_bob_sst.csv` | Core predictor |
| Hobday climatology | `results/climatology/{region}_hobday.csv` | Threshold, anomaly |
| Wind speed | `results/{region}_wind.csv` | Key driver (78–84% weak wind during MHWs) |
| Heat flux | `results/heat_flux/csv/{region}_slhf.csv`, `_sshf.csv` | Surface forcing |
| ONI | `results/climate_indices/enso/csv/oni_timeseries.csv` | ENSO |
| DMI | `results/climate_indices/iod/csv/dmi_timeseries.csv` | IOD (strongest driver) |
| MEI | `results/climate_indices/mei/csv/mei_timeseries.csv` | ENSO multivariate |
| MHW catalogue | `results/mhw_catalogue/{region}_mhw_catalogue.csv` | Event start dates (labels) |

**Regions:** North, Central, South (separate models per region).

---

## 5. Feature Engineering (Step 01)

Each row = **one day × one region** (~7,300 rows per region, 2006–2025).

### 5.1 SST features
| Feature | Description |
|---------|-------------|
| `SST` | Daily regional mean SST (°C) |
| `SST_Anomaly` | SST − climatological mean for that DOY |
| `Intensity` | SST − Hobday 90th-percentile threshold |
| `Distance_to_Threshold` | Same as intensity |
| `Above_Threshold` | Binary: intensity > 0 |
| `Consecutive_Hot_Days` | Running count of days above threshold |
| `SST_mean_{7,14,21,30}d` | Rolling mean SST |
| `SST_std_{7,14,21,30}d` | Rolling SST variability |
| `Intensity_mean_{7,14,21,30}d` | Rolling mean intensity |
| `SST_change_7d`, `SST_change_14d` | SST trend |

### 5.2 Wind features
| Feature | Description |
|---------|-------------|
| `Wind` | Daily mean wind speed (m/s) |
| `Wind_Climatology` | DOY mean wind |
| `Wind_Anomaly` | Wind − climatology |
| `Wind_mean_{7,14,21,30}d` | Rolling mean wind |
| `Wind_anom_mean_{7,14,21,30}d` | Rolling mean wind anomaly |

### 5.3 Heat flux features
| Feature | Description |
|---------|-------------|
| `SLHF`, `SSHF` | Latent/sensible heat flux (forward-filled from weekly to daily) |
| `SLHF_Anomaly`, `SSHF_Anomaly` | Flux − DOY climatology |
| `SLHF_anom_mean_{7,14,21,30}d` | Rolling flux anomaly |

### 5.4 Climate index features
| Feature | Description |
|---------|-------------|
| `ONI_0m`, `DMI_0m`, `MEI_0m` | Current month values (forward-filled to daily) |
| `ONI_{1,2,3,6}m`, etc. | Lagged monthly values |

### 5.5 Calendar features
| Feature | Description |
|---------|-------------|
| `DOY_sin`, `DOY_cos` | Cyclical day-of-year encoding |
| `Season` | Winter / Pre-Monsoon / SW Monsoon / Post-Monsoon |

### 5.6 State flags (not used as features, but saved)
| Column | Description |
|--------|-------------|
| `in_mhw` | Whether this day falls inside a detected MHW event |

### 5.7 No data leakage

All rolling features use **only past and current** data (`rolling` with default backward-looking window). Climate indices are monthly values known at month start, forward-filled — no future information.

---

## 6. Train / Validation / Test Splits

**Chronological splits** (never random):

| Split | Years | Purpose |
|-------|-------|---------|
| Train | 2006–2018 | Model fitting |
| Validation | 2019–2021 | Implicit in train+val fit |
| Test | 2022–2025 | Final evaluation (unseen years) |

This mimics real forecasting: train on the past, test on recent years the model has never seen.

---

## 7. Models

### 7.1 Baselines (Step 02)

| Model | Logic | Purpose |
|-------|-------|---------|
| **Climatology** | P(onset) estimated from DOY in training years | Seasonal floor |
| **Persistence** | High probability if consecutive hot days + high intensity | Physical floor |
| **Logistic Regression** | Linear model on SST + wind + climate features | Interpretable benchmark |

### 7.2 ML models (Step 03)

| Model | Notes |
|-------|-------|
| **XGBoost** (primary) | Gradient boosted trees, handles imbalance via `scale_pos_weight` |
| **Random Forest** | Ensemble comparison, `class_weight=balanced` |
| **Gradient Boosting** | sklearn fallback |

**Scope:** One model per `(region, horizon, algorithm)` — e.g. `north/onset_7d_xgboost.joblib`.

### 7.3 Class imbalance

MHW onset days are rare (~1–3% of all days). We handle this via:
- `scale_pos_weight` in XGBoost (ratio of negatives to positives)
- `class_weight='balanced'` in Random Forest / Logistic Regression
- Evaluation on **F1** and **PR-AUC**, not accuracy alone

---

## 8. Evaluation (Step 04)

### 8.1 Metrics

| Metric | Why it matters |
|--------|----------------|
| **Precision** | Of predicted onsets, how many are real? |
| **Recall** | Of real onsets, how many did we catch? |
| **F1** | Balance of precision and recall |
| **ROC-AUC** | Overall discrimination |
| **PR-AUC** | Better for rare events |
| **Brier score** | Probability calibration |

### 8.2 Outputs
- `outputs/metrics/baselines.csv` — baseline performance
- `outputs/metrics/ml_models.csv` — ML model performance
- `outputs/metrics/all_models_comparison.csv` — combined table
- `outputs/metrics/best_models.csv` — best F1 per region/horizon
- `outputs/figures/roc_*.png`, `pr_*.png`, `confusion_*.png`

---

## 9. Explainability (Step 05)

Uses **SHAP** (if installed) or **feature importances** (fallback).

**Expected top features** (based on your physical analysis):
1. Wind anomaly / rolling wind
2. SST intensity / consecutive hot days
3. DMI (IOD)
4. SST trend (7-day change)

If SHAP shows unexpected dominance (e.g. `DOY_sin` alone), revisit feature engineering.

Outputs:
- `outputs/shap/importance_{region}_{horizon}.png`
- `outputs/shap/shap_{region}_{horizon}.png` (if SHAP available)
- `outputs/shap/feature_importance_all.csv`
- `outputs/shap/top_features_{region}.csv`

---

## 10. Operational Forecast (Step 06)

For the **latest date** in each region's dataset:

```
Region   Horizon   P(MHW onset)   Alert
North    7 days    0.12           LOW
Central  7 days    0.08           LOW
South    7 days    0.31           MODERATE
```

Alert levels:
- **HIGH:** P ≥ 0.50
- **MODERATE:** 0.25 ≤ P < 0.50
- **LOW:** P < 0.25

Saved to `outputs/forecasts/latest_forecast.csv`.

---

## 11. How to Run

### Prerequisites

```bash
cd /home/samyak/mrc_ws
# Main project data must exist (SST, wind, climatology, MHW catalogue)
# Optional: pip install xgboost shap pyyaml
```

### Full pipeline

```bash
cd /home/samyak/mrc_ws
.venv/bin/python mhw_ml/scripts/run_pipeline.py
```

### Step by step

```bash
.venv/bin/python mhw_ml/scripts/01_build_dataset.py
.venv/bin/python mhw_ml/scripts/02_train_baselines.py
.venv/bin/python mhw_ml/scripts/03_train_models.py
.venv/bin/python mhw_ml/scripts/04_evaluate_models.py
.venv/bin/python mhw_ml/scripts/05_explain_models.py
.venv/bin/python mhw_ml/scripts/06_predict_current.py
```

### Daily forecast only (after training)

```bash
.venv/bin/python mhw_ml/scripts/06_predict_current.py
```

---

## 12. Configuration

Edit `config/model_config.yaml` to change:

```yaml
task:
  horizons_days: [3, 7, 14]    # forecast windows

splits:
  train_years: [2006, 2018]
  test_years: [2022, 2025]

models:
  primary: xgboost             # best model for forecasts
```

---

## 13. Interpreting Results

### Good signs
- ML F1 > baseline F1 on 2022–2025 test set
- PR-AUC > 0.3 for 7-day horizon
- SHAP shows wind, intensity, IOD as top features
- Higher recall at 3-day horizon than 14-day (shorter = easier)

### Warning signs
- Accuracy high but F1 near zero → model predicts "no onset" always
- Test performance much worse than train → overfitting
- Top feature is only seasonality → model learned calendar, not physics

---

## 14. Limitations

| Limitation | Impact |
|------------|--------|
| Only 117 events in 20 years | Rare positive class; metrics have wide confidence intervals |
| Regional mean SST (not spatial) | Cannot resolve sub-regional patterns |
| Heat flux is weekly | Forward-filled; less precise than daily wind/SST |
| Wind/SST bounding boxes differ | Known project issue; may add noise |
| Monthly climate indices | Daily onset may depend on sub-monthly variability |
| No BSISO, MLD, radiation yet | Missing drivers from Phase 11 |

---

## 15. Next Steps (v2 improvements)

1. Add BSISO, radiation, MLD when extracted (Phase 11)
2. Combined regional model with `region` as feature
3. LSTM on 30-day raw sequences if XGBoost plateaus
4. Probability calibration (Platt scaling / isotonic)
5. Multi-horizon ensemble alert system
6. Validate predictions against `master_event_catalogue` event-by-event

---

## 16. Link to Main Project

| Main project phase | ML module use |
|--------------------|---------------|
| MHW detection (Hobday) | Label generation |
| ENSO / IOD / MEI pipelines | Climate features |
| Wind / heat flux analysis | Core predictors |
| Climate driver comparison | Feature prioritization (IOD #1, wind dominant) |
| Master event catalogue | Post-hoc validation |

---

*End of ML_EXECUTION.md*

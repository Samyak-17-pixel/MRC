# src/ml/ — MHW Onset Forecasting

Machine-learning module for **early warning** of new Marine Heatwave starts in the Bay of Bengal (North / Central / South), horizons **H ∈ {3, 7, 14} days**.

Climate analysis is separate (`src/climate/`). This package **reads** processed products under `outputs/` and must not alter Hobday detection thresholds.

**Study period:** 2006–2025 · **Labels from:** 117 Hobday catalogue events (North 49, Central 40, South 28).

Detailed runbook (also kept here): [`ML_EXECUTION.md`](ML_EXECUTION.md). Numerical master tables: repository root [`README.md`](../../README.md).

---

## 1. Objective

Predict whether a **new MHW will start** in a sub-region within the next H days, using only information available at day *t*.

This is **classification for early warning**, not a nowcast of an ongoing event, and **not** an annual event counter.

### Catalogue vs forecast (critical)

| Product | Question | 2025 example |
|---------|----------|--------------|
| Hobday catalogue | How many MHWs **started** in the year? | **13** starts (North 8, Central 4, South 1) |
| ML operational forecast | Will a new MHW start in the next 3/7/14 days **from the latest feature day**? | Scores **2025-12-31** only |

A low probability on 2025-12-31 does **not** mean “0 events in 2025.” By that date the last 2025 events had already ended, and SST was below the Hobday threshold. Year-end **P≈0 is expected**.

### 2025 verification (pre-onset windows)

Using best-by-F1 models and alert hit = max P ≥ 0.25 on the labelled pre-onset window:

| Horizon | Hits |
|---------|------|
| 3-day | **11 / 13** |
| 7-day | **12 / 13** |
| 14-day | **13 / 13** |

---

## 2. Package layout

```
src/ml/
├── README.md                 ← this file
├── ML_EXECUTION.md           ← extended execution guide
├── common.py                 ← config, paths, shared loaders
├── run_pipeline.py           ← orchestrator (steps 01–06)
├── config/model_config.yaml
├── preprocessing/01_build_dataset.py
├── training/02_train_baselines.py
├── training/03_train_models.py
├── evaluation/04_evaluate_models.py
├── evaluation/05_explain_models.py
├── experiments/06_predict_current.py
├── feature_engineering/      ← design notes (logic in step 01)
├── visualizations/           ← points at figures/SHAP outputs
├── datasets/{processed,splits}/
├── models/{baselines,north,central,south}/
├── outputs/{metrics,figures,shap,forecasts}/
└── logs/
```

---

## 3. Prediction target

Hobday definition (same as climate pipeline): SST > seasonally varying P90 for ≥5 consecutive days; Intensity = SST − Threshold90.

```
onset_Hd = 1  if a new MHW STARTS on any day in (t, t+H]
           0  otherwise
```

Event starts come from `outputs/mhw/catalogue/{region}_mhw_catalogue.csv`.

| Horizon | Approx. positive rate (all regions) |
|---------|-------------------------------------|
| 3-day | ~1.59% |
| 7-day | ~3.72% |
| 14-day | ~7.40% |

---

## 4. Models

| Algorithm | Role |
|-----------|------|
| Climatology baseline | DOY onset rate from train years |
| Persistence baseline | Hot-day streak + intensity heuristic |
| Logistic Regression | Linear baseline (`class_weight=balanced` + `StandardScaler`) |
| XGBoost | Config “primary” tree model |
| Random Forest / Gradient Boosting | Ensemble comparison |

Separate model per `(region, horizon, algorithm)`. Operational forecasts load **best-by-F1** from `outputs/metrics/best_models.csv` (not always XGBoost).

---

## 5. Features (built in step 01)

SST intensity / threshold proximity / consecutive hot days / rolling SST & intensity; wind and wind anomaly; SLHF/SSHF anomalies (weekly→daily ffill); ONI/DMI/MEI at lags 0,1,2,3,6 months; `DOY_sin`/`DOY_cos`. State flag `in_mhw` is saved but not used as a predictor.

Rolling windows are **backward-looking only** (no future leakage in features).

---

## 6. Splits (chronological)

| Split | Years |
|-------|-------|
| Train | 2006–2018 |
| Validation | 2019–2021 |
| Test | 2022–2025 |

Never random-shuffle across years.

---

## 7. Inputs from climate outputs

| Source | Path |
|--------|------|
| Regional SST | `outputs/timeseries/{region}_bob_sst.csv` |
| Hobday climatology | `outputs/mhw/climatology/{region}_hobday.csv` |
| Wind | `outputs/timeseries/{region}_wind.csv` |
| Heat flux | `outputs/drivers/heat_flux/csv/{region}_slhf.csv`, `_sshf.csv` |
| ONI / DMI / MEI | under `outputs/climate_indices/` (see that folder README for nested layout) |
| MHW catalogue | `outputs/mhw/catalogue/{region}_mhw_catalogue.csv` |

---

## 8. How to run

```bash
cd <repo-root>
.venv/bin/python src/ml/run_pipeline.py

# or step-wise:
.venv/bin/python src/ml/preprocessing/01_build_dataset.py
.venv/bin/python src/ml/training/02_train_baselines.py
.venv/bin/python src/ml/training/03_train_models.py
.venv/bin/python src/ml/evaluation/04_evaluate_models.py
.venv/bin/python src/ml/evaluation/05_explain_models.py
.venv/bin/python src/ml/experiments/06_predict_current.py
```

Alert levels: HIGH P≥0.50 · MODERATE 0.25≤P<0.50 · LOW P<0.25.

---

## 9. Test-set skill (2022–2025) — orientation

Best F1 is typically highest at the **14-day** horizon (~0.39 North/Central LogReg). South is hardest at short horizons. See root README Part C for the full metrics table.

---

## 10. Limitations / caveats

- Only 117 historical events → sparse positives.
- Regional-mean predictors (no spatial grids in v1).
- Weekly heat flux forward-filled to daily.
- **Wind vs SST bbox mismatch** (80–100°E vs 85–95°E) — documented, not silently “fixed”.
- DMI ends April 2025 → late-2025 IOD features may be incomplete.
- Some logistic probabilities poorly calibrated (e.g. HIGH alert with negative Intensity).
- Forecast date = last row in feature CSV until data are refreshed.

Physical motivation: IOD #1 large-scale driver; ~81% weak-wind events; intensity/threshold proximity.

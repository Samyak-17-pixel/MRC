# Part 12 — Machine Learning Technical Review

Complete review of the MHW **onset forecasting** module. Climate analysis is separate; ML reads processed `results/` products and must not alter detection thresholds.

**Canonical code location (after reorganization):** `machine_learning/`  
**Legacy path (compatibility):** `mhw_ml/` — see `MIGRATION_REPORT.md`  
**Prior guide:** historically `mhw_ml/ML_EXECUTION.md` (content merged here / retained as pointer)

---

## 1. Current Objective

Predict whether a **new Marine Heatwave will start** in a BoB sub-region within the next **H ∈ {3, 7, 14} days**, using only information available at day *t* (recent/current observations).

This is an **early-warning classification** task, not a nowcast of whether an event is already ongoing.

---

## 2. Prediction Target / Labels

For each day *t* and region:

```
onset_Hd = 1  if a new MHW STARTS on any day in (t, t+H]
           0  otherwise
```

Event starts come from `results/mhw_catalogue/{region}_mhw_catalogue.csv` (Hobday events).

**Example:** Event starts 2024-04-14 → `onset_7d = 1` for days 2024-04-07 … 2024-04-13.

| Horizon | Approx. positive rate (all regions) |
|---------|-------------------------------------|
| 3-day | 1.59% |
| 7-day | 3.72% |
| 14-day | 7.40% |

---

## 3. Classification vs Regression

**Binary classification** per (region, horizon). Probabilities are produced for alert levels; no regression of duration/intensity in v1.

---

## 4. Model Architecture / Algorithms

| Algorithm | Role | Key hyperparameters (from `config/model_config.yaml`) |
|-----------|------|------------------------------------------------------|
| **Climatology baseline** | DOY onset rate from train years | — |
| **Persistence baseline** | High score if consecutive hot days + high intensity | — |
| **Logistic Regression** | Linear interpretable baseline | `class_weight=balanced` |
| **XGBoost** | Primary gradient-boosted trees | n_estimators=300, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, `scale_pos_weight=auto` |
| **Random Forest** | Ensemble comparison | n_estimators=300, max_depth=8, class_weight=balanced |
| **Gradient Boosting** | sklearn GBM fallback | defaults as coded in training script |

**Scope:** Separate model per `(region, horizon, algorithm)` — e.g. `north/onset_7d_xgboost.joblib`.

**Why these algorithms:** Tabular features, small sample of positives, need class-imbalance handling, and interpretability via coefficients / importances / SHAP.

---

## 5. Features Used

Built in dataset step (historically `01_build_dataset.py`):

### SST
`SST`, `SST_Anomaly`, `Intensity`, `Distance_to_Threshold`, `Above_Threshold`, `Consecutive_Hot_Days`, rolling mean/std of SST and intensity (7/14/21/30 d), `SST_change_7d`, `SST_change_14d`

### Wind
`Wind`, `Wind_Climatology`, `Wind_Anomaly`, rolling wind / wind anomaly means

### Heat flux
`SLHF`, `SSHF`, anomalies, rolling anomaly means (weekly→daily forward-fill)

### Climate indices
`ONI_*m`, `DMI_*m`, `MEI_*m` for lags 0,1,2,3,6 months (monthly values forward-filled to daily)

### Calendar
`DOY_sin`, `DOY_cos`, `Season` (Season stored; cyclical DOY used as features)

### Not used as predictors (saved state)
`in_mhw` — whether day is inside an ongoing event

**Why selected:** Motivated by climate-analysis findings (intensity/threshold proximity; wind; IOD/ENSO/MEI).

---

## 6. Input / Output Variables

| Direction | Variables |
|-----------|-----------|
| **Inputs** | Feature matrix X from daily feature tables |
| **Outputs** | Class label `onset_Hd`; predicted probability P(onset); alert LOW/MODERATE/HIGH |
| **Artifacts** | `*.joblib` models; metrics CSVs; ROC/PR/SHAP figures; `latest_forecast.csv` |

---

## 7. Data Preprocessing & Feature Engineering

1. Load regional SST, Hobday thresholds, wind, heat flux, climate CSVs from `results/`.
2. Align on daily date index per region (~7,300 days × 3 regions → 21,900 rows combined).
3. Compute anomalies vs DOY climatology; rolling windows **backward-looking only** (no future leakage).
4. Forward-fill monthly climate indices to daily.
5. Assign onset labels from future event starts within H (label uses future starts — standard supervised setup; features do not).

**Scaling / normalization:** Tree models do not require standardization. Logistic regression uses sklearn pipeline behavior as implemented in training scripts (see code for StandardScaler if present). Document actual scaler usage from `02_train_baselines.py` / `03_train_models.py` when auditing code — do not assume undocumented transforms.

---

## 8. Train / Validation / Test Split (Time-Series Aware)

| Split | Years | Rows (approx.) |
|-------|-------|----------------|
| Train | 2006–2018 | 14,235 |
| Validation | 2019–2021 | 3,285 |
| Test | 2022–2025 | 4,380 |

**Never random shuffle across years.** Mimics operational forecasting.

---

## 9. Loss / Objective / Optimizer

| Model | Objective |
|-------|-----------|
| Logistic Regression | Log-loss (sklearn) |
| XGBoost | Binary logistic / logloss with `scale_pos_weight` |
| RF / GBM | Gini / deviance as per sklearn defaults |

No deep-learning optimizer (Adam etc.) in v1.

---

## 10. Evaluation Metrics

| Metric | Why |
|--------|-----|
| Precision / Recall / F1 | Rare-event relevance |
| ROC-AUC | Ranking ability |
| PR-AUC | Preferred under imbalance |
| Brier score | Probability calibration |
| Accuracy | Reported but easy to inflate |

Primary selection for "best" models in project tables: **F1** on test set.

---

## 11. Cross-Validation Strategy

v1 uses **fixed chronological splits** rather than k-fold CV across time. Expanding-window CV is a planned improvement (not claimed as implemented unless present in code).

---

## 12. Feature Importance

Step `05_explain_models.py`: SHAP when available, else native importances.

**Example (North XGBoost — from results summary):** Distance_to_Threshold, Intensity, Intensity_mean_7d, DMI_1m, ONI_0m, SST_Anomaly, DOY_sin, … — consistent with physical analysis (SST state + climate indices).

---

## 13. Alert Thresholds (Operational)

| Alert | Probability |
|-------|-------------|
| HIGH | P ≥ 0.50 |
| MODERATE | 0.25 ≤ P < 0.50 |
| LOW | P < 0.25 |

---

## 14. Results Obtained So Far (Test 2022–2025)

Best F1 by region × horizon (from `ALL_PROJECT_RESULTS.md`):

| Region | Horizon | Best model | F1 | Recall | Precision | ROC-AUC | PR-AUC |
|--------|---------|------------|-----|--------|-----------|---------|--------|
| North | 3d | RF | 0.164 | 0.169 | 0.160 | 0.810 | 0.161 |
| North | 7d | LogReg | 0.253 | 0.790 | 0.151 | 0.644 | 0.155 |
| North | 14d | LogReg | **0.389** | 0.813 | 0.256 | 0.612 | 0.292 |
| Central | 3d | LogReg | 0.235 | 0.692 | 0.142 | 0.840 | 0.187 |
| Central | 7d | LogReg | 0.305 | 0.837 | 0.187 | 0.728 | 0.189 |
| Central | 14d | LogReg | **0.399** | 0.767 | 0.269 | 0.606 | 0.242 |
| South | 3d | XGBoost | 0.138 | 0.074 | 1.000 | 0.804 | 0.161 |
| South | 7d | GBM | 0.183 | 0.190 | 0.176 | 0.781 | 0.129 |
| South | 14d | LogReg | 0.228 | 0.865 | 0.131 | 0.669 | 0.124 |

**Interpretation:** Longer horizons have more positives → higher F1 ceiling; linear models often beat trees on this dataset size; South is hardest.

---

## 15. Model Assumptions

1. Past statistical relationships persist into 2022–2025.
2. Regional-mean predictors suffice for onset warning.
3. Monthly climate indices carry useful signal when forward-filled daily.
4. Label definition (any start in (t, t+H]) matches the operational question.

---

## 16. Current Limitations

| Limitation | Effect |
|------------|--------|
| Only 117 historical events | Sparse positives |
| No spatial predictors | Misses local onset cells |
| Weekly heat flux | Noisy daily features |
| Wind/SST box mismatch | Extra noise |
| No BSISO/MLD/radiation yet | Missing drivers |
| Config may contain absolute paths | Should use relative roots after migration |

---

## 17. Pending Improvements / Planned Models

1. Calibration; threshold tuning for alerts  
2. New physical features (Phase 11 variables)  
3. Multi-region model  
4. Sequence models (LSTM/Temporal CNN) if justified  
5. Strict purge of absolute machine paths from config  
6. Event-level verification against master catalogue  

---

## 18. Hyperparameter Notes (What / Why / Alternatives)

| Parameter | Represents | Why chosen | Alternatives |
|-----------|------------|------------|--------------|
| horizons 3/7/14 | Warning lead times | Operationally useful week-scale | 1, 5, 10, 21 days |
| max_depth 5 (XGB) | Tree complexity | Limit overfit on rare events | 3–8; tune on val |
| learning_rate 0.05 | Step size | Stable boosting | 0.01–0.1 |
| scale_pos_weight auto | Imbalance correction | Match neg/pos ratio | Focal loss; resampling |
| class_weight balanced | Same for RF/LogReg | Counter majority class | SMOTE (careful with time series) |
| n_estimators 300 | Ensemble size | Adequate capacity | Early stopping on val |

---

## 19. How to Run (After Migration)

```bash
.venv/bin/python machine_learning/run_pipeline.py
# step-wise:
.venv/bin/python machine_learning/preprocessing/01_build_dataset.py
.venv/bin/python machine_learning/training/02_train_baselines.py
.venv/bin/python machine_learning/training/03_train_models.py
.venv/bin/python machine_learning/evaluation/04_evaluate_models.py
.venv/bin/python machine_learning/evaluation/05_explain_models.py
.venv/bin/python machine_learning/experiments/06_predict_current.py
```

Legacy: `.venv/bin/python mhw_ml/scripts/run_pipeline.py` should remain as a thin wrapper.

---

## 20. Related Documents

- Migration: `MIGRATION_REPORT.md`
- Module README: `../machine_learning/README.md`
- Results numbers: `../ALL_PROJECT_RESULTS.md` §14

# machine_learning/ — MHW Onset Forecasting Module

**Separated from the climate-analysis pipeline.** This module predicts whether a new Marine Heatwave will **start** within 3 / 7 / 14 days in North, Central, or South Bay of Bengal.

Full technical review: [`../documentation/12_machine_learning.md`](../documentation/12_machine_learning.md)  
Migration notes: [`../documentation/MIGRATION_REPORT.md`](../documentation/MIGRATION_REPORT.md)

---

## Layout

```
machine_learning/
├── datasets/              ← processed daily features + train/val/test splits
├── preprocessing/         ← 01_build_dataset.py (labels + rolling features)
├── feature_engineering/   ← documentation of feature design (logic lives in step 01)
├── training/              ← 02 baselines, 03 ML models
├── evaluation/            ← 04 metrics/plots, 05 SHAP/importance
├── experiments/           ← 06 operational forecast
├── models/                ← saved .joblib models
├── visualizations/        ← README pointing to outputs/figures & outputs/shap
├── config/model_config.yaml
├── outputs/{metrics,figures,shap,forecasts}/
├── common.py              ← shared utilities (paths resolved relative to repo root)
├── run_pipeline.py
└── ML_EXECUTION.md        ← legacy detailed guide (still valid conceptually)
```

---

## How to Run

From repository root:

```bash
.venv/bin/python machine_learning/run_pipeline.py
```

Step by step:

```bash
.venv/bin/python machine_learning/preprocessing/01_build_dataset.py
.venv/bin/python machine_learning/training/02_train_baselines.py
.venv/bin/python machine_learning/training/03_train_models.py
.venv/bin/python machine_learning/evaluation/04_evaluate_models.py
.venv/bin/python machine_learning/evaluation/05_explain_models.py
.venv/bin/python machine_learning/experiments/06_predict_current.py
```

**Prerequisite:** Climate pipeline products in `results/` (SST, climatology, MHW catalogues, wind, heat flux, climate index CSVs).

---

## Backward Compatibility

The legacy folder `mhw_ml/` remains as **thin wrappers** that forward to this package. Prefer `machine_learning/` for all new work.

---

## Task Summary

| Item | Value |
|------|-------|
| Task | Binary onset classification |
| Horizons | 3, 7, 14 days |
| Models | Logistic Regression, XGBoost, Random Forest, Gradient Boosting + baselines |
| Split | Train 2006–2018 · Val 2019–2021 · Test 2022–2025 |
| Best F1 (test) | ~0.39–0.40 at 14-day (see ALL_PROJECT_RESULTS.md) |

Do **not** change Hobday labels or climate methodology from this module.

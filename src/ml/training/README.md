# src/ml/training/ — Model Fitting

Trains baseline and tree/linear classifiers for onset warning at horizons 3 / 7 / 14 days, per region.

## Purpose

Fit models on chronological train (+val as configured) years and serialize `.joblib` artifacts for evaluation and operational forecasting.

## Contents

| Script | Role |
|--------|------|
| `02_train_baselines.py` | Climatology, persistence, logistic regression |
| `03_train_models.py` | XGBoost, Random Forest, Gradient Boosting |

## How to run

```bash
.venv/bin/python src/ml/training/02_train_baselines.py
.venv/bin/python src/ml/training/03_train_models.py
```

Hyperparameters: `src/ml/config/model_config.yaml`.

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `src/ml/datasets/processed/` | `src/ml/models/baselines/`, `src/ml/models/{north,central,south}/` |
| | Consumed by `evaluation/` and `experiments/06_predict_current.py` |

## Notes

- Class imbalance handled via `scale_pos_weight` (XGBoost) and `class_weight='balanced'` (RF / LogReg).
- One artifact per `(region, horizon, algorithm)`, e.g. `north/onset_7d_xgboost.joblib`.

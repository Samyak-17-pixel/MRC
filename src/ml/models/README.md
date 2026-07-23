# src/ml/models/ — Trained Artifacts

Serialized sklearn / XGBoost pipelines (`.joblib`) for baselines and per-region ML models.

## Purpose

Persist fitted classifiers so evaluation and operational forecasts do not retrain every run.

## Contents

```
models/
├── baselines/          # climatology / persistence / logistic
├── north/
├── central/
└── south/
```

Typical names: `onset_{3d|7d|14d}_{xgboost|random_forest|gradient_boosting|logistic}.joblib` (exact naming follows training scripts).

## How generated

```bash
.venv/bin/python src/ml/training/02_train_baselines.py
.venv/bin/python src/ml/training/03_train_models.py
```

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `datasets/processed/` + `config/model_config.yaml` | `evaluation/04_*.py`, `evaluation/05_*.py`, `experiments/06_predict_current.py` |

## Notes

- Large binaries may be gitignored; regenerate with the training scripts if missing.
- Operational selection uses `src/ml/outputs/metrics/best_models.csv`, not necessarily the config `primary` model.

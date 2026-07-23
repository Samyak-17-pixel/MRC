# src/ml/evaluation/ — Metrics & Explainability

Test-set scoring and feature attribution for trained onset models.

## Purpose

1. Compute precision / recall / F1 / ROC-AUC / PR-AUC / Brier on **2022–2025** test years.
2. Rank best-by-F1 models for operational use.
3. Produce SHAP or native feature-importance summaries.

## Contents

| Script | Role |
|--------|------|
| `04_evaluate_models.py` | Metrics tables + ROC/PR/confusion figures |
| `05_explain_models.py` | SHAP (if installed) or importances |

## How to run

```bash
.venv/bin/python src/ml/evaluation/04_evaluate_models.py
.venv/bin/python src/ml/evaluation/05_explain_models.py
```

## Key outputs

| Path | Contents |
|------|----------|
| `src/ml/outputs/metrics/baselines.csv` | Baseline metrics |
| `src/ml/outputs/metrics/ml_models.csv` | ML metrics |
| `src/ml/outputs/metrics/all_models_comparison.csv` | Combined |
| `src/ml/outputs/metrics/best_models.csv` | Best F1 per region×horizon (**deployment table**) |
| `src/ml/outputs/figures/` | ROC / PR / confusion plots |
| `src/ml/outputs/shap/` | Importance CSVs and plots |

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `src/ml/models/`, `datasets/processed/` | `06_predict_current.py` (reads `best_models.csv`); publication figure F05 |

## Notes

Primary selection criterion for “best” models: **F1** on the chronological test set. Accuracy alone is misleading under ~1–7% positive rates.

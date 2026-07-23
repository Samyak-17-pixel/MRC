# src/ml/visualizations/ — ML Figure Index

Documentation pointer for ML plots. Scripts that write figures live under `evaluation/` (and forecast CSVs under `experiments/`).

## Purpose

Locate ROC/PR/confusion matrices and SHAP/importance plots without hunting the tree.

## Contents (generated elsewhere)

| Location | Contents |
|----------|----------|
| `src/ml/outputs/figures/` | `roc_*.png`, `pr_*.png`, `confusion_*.png` |
| `src/ml/outputs/shap/` | Importance / SHAP plots + `feature_importance_all.csv`, `top_features_{region}.csv` |

## How generated

```bash
.venv/bin/python src/ml/evaluation/04_evaluate_models.py
.venv/bin/python src/ml/evaluation/05_explain_models.py
```

## Upstream / Downstream

Models + test features → figures → interpretation in root README / publication F05 (`outputs/publication/`).

## Notes

Expected top features (physical prior): wind anomaly, intensity / consecutive hot days, DMI, short SST trends. Calendar-only dominance is a warning sign.

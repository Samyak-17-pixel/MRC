# src/ml/outputs/ — ML Metrics, Figures, Forecasts

All **machine-learning** products (separate from climate `outputs/` at repo root).

## Purpose

Store evaluation tables, diagnostic plots, SHAP summaries, and operational forecast CSVs.

## Contents

| Subfolder | Contents |
|-----------|----------|
| `metrics/` | `baselines.csv`, `ml_models.csv`, `all_models_comparison.csv`, `best_models.csv` |
| `figures/` | ROC / PR / confusion matrices |
| `shap/` | Feature importance CSVs and plots |
| `forecasts/` | `latest_forecast.csv`, `year_verification_*.csv`, dated snapshots |

## How generated

| Step | Script |
|------|--------|
| Metrics + ROC/PR | `src/ml/evaluation/04_evaluate_models.py` |
| SHAP / importances | `src/ml/evaluation/05_explain_models.py` |
| Forecasts | `src/ml/experiments/06_predict_current.py` |

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| Trained models + feature tables | Root README reporting; `outputs/publication/` (e.s. F05 ML heatmap) |

## Notes

- **Do not confuse** with repo-root `outputs/` (climate analysis).
- Latest single-day forecast ≠ annual Hobday count; see `src/ml/README.md` §Catalogue vs forecast.
- 2025 verification headline: 11/13, 12/13, 13/13 at P≥0.25 for 3/7/14-day horizons.

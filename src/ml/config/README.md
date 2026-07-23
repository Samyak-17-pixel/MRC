# src/ml/config/ — ML Configuration

Hyperparameters, task definition, chronological splits, and path keys for the onset-forecasting pipeline.

## Purpose

Single YAML source of truth so training/evaluation/forecast scripts stay aligned.

## Contents

| File | Role |
|------|------|
| `model_config.yaml` | Horizons, regions, splits, model hyperparameters, `paths.results_relative` |

## Key settings

| Key | Typical value | Meaning |
|-----|---------------|---------|
| `paths.results_relative` | `outputs` | Climate products root (resolved via `common.cfg_path`) |
| `task.horizons_days` | `[3, 7, 14]` | Forecast windows |
| `splits.train_years` | `[2006, 2018]` | Inclusive year range |
| `splits.val_years` | `[2019, 2021]` | Validation years |
| `splits.test_years` | `[2022, 2025]` | Held-out test years |
| `models.primary` | `xgboost` | Fallback primary; **deployment uses best-by-F1** |

## Upstream / Downstream

Read by `src/ml/common.py` → every pipeline step. Does not produce scientific CSVs itself.

## Notes

Edit YAML carefully; changing splits or horizons requires rebuilding features and retraining before comparing to published metrics.

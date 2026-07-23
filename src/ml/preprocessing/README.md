# src/ml/preprocessing/ — Feature Tables & Labels

Builds the daily supervised-learning table for MHW **onset** forecasting.

## Purpose

Join climate products into one row per day × region, engineer rolling/lag features, and assign `onset_3d` / `onset_7d` / `onset_14d` labels from Hobday event start dates.

## Contents

| File | Role |
|------|------|
| `01_build_dataset.py` | Full feature + label build |

## How outputs are generated

```bash
.venv/bin/python src/ml/preprocessing/01_build_dataset.py
```

Writes:

- `src/ml/datasets/processed/{north,central,south}_daily_features.csv`
- `src/ml/datasets/processed/combined_daily_features.csv`
- `src/ml/datasets/splits/{train,val,test}.csv`

## Upstream inputs

| Input | Path |
|-------|------|
| Regional SST | `outputs/timeseries/{region}_bob_sst.csv` |
| Hobday threshold | `outputs/mhw/climatology/{region}_hobday.csv` |
| Wind | `outputs/timeseries/{region}_wind.csv` |
| Heat flux | `outputs/drivers/heat_flux/csv/` |
| Climate indices | `outputs/climate_indices/` (ONI, DMI, MEI) |
| Event starts (labels) | `outputs/mhw/catalogue/{region}_mhw_catalogue.csv` |

## Downstream consumers

Training (`src/ml/training/`), evaluation, experiments, and SHAP explainability all read `datasets/processed/` (and chronological year masks matching `config/model_config.yaml`).

## Notes

- Labels use **future** starts within H (standard supervised setup); features do not peek ahead.
- Rolling stats are backward-looking only.
- Chronological splits: train 2006–2018, val 2019–2021, test 2022–2025.

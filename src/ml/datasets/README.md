# src/ml/datasets/ — Processed Features & Splits

Tabular ML inputs derived from climate `outputs/` (not raw NetCDFs).

## Purpose

Hold daily feature matrices and chronological train/val/test CSV extracts used by training and evaluation.

## Contents

```
datasets/
├── processed/
│   ├── north_daily_features.csv
│   ├── central_daily_features.csv
│   ├── south_daily_features.csv
│   └── combined_daily_features.csv
└── splits/
    ├── train.csv
    ├── val.csv
    └── test.csv
```

Rough scale: ~7,300 days × 3 regions → ~21,900 combined rows (2006–2025).

## How generated

```bash
.venv/bin/python src/ml/preprocessing/01_build_dataset.py
```

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `outputs/timeseries/`, `outputs/mhw/`, `outputs/drivers/heat_flux/`, climate indices, catalogues | `src/ml/training/`, `evaluation/`, `experiments/` |

## Notes

- Labels `onset_3d/7d/14d` are columns in these tables.
- Regenerating overwrites CSVs deterministically given the same climate inputs.
- Do not hand-edit if you need reproducible metrics.

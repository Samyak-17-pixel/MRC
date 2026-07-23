# src/ml/feature_engineering/ — Feature Design Notes

Documentation-only folder. **Implementation lives in** `src/ml/preprocessing/01_build_dataset.py`.

## Purpose

Record *what* features exist and *why* they were chosen (physical / statistical motivation from the climate pipeline).

## Feature groups

| Group | Examples | Motivation |
|-------|----------|------------|
| SST / Hobday | `Intensity`, `Distance_to_Threshold`, `Consecutive_Hot_Days`, rolling SST | Event definition itself |
| Wind | `Wind_Anomaly`, rolling wind means | ~81% of catalogue events are weak-wind |
| Heat flux | `SLHF_Anomaly`, `SSHF_Anomaly` | Reduced latent heat loss during many events |
| Climate indices | `DMI_*m`, `ONI_*m`, `MEI_*m` | **IOD #1** large-scale driver; ENSO strongest in South |
| Calendar | `DOY_sin`, `DOY_cos` | Seasonal cycle without treating DOY as linear |

## Upstream / Downstream

Designed against products in `outputs/`; consumed as columns in `src/ml/datasets/processed/`.

## Notes

- No future leakage in rolling windows.
- Monthly indices forward-filled to daily.
- `in_mhw` is stored as state, not used as a predictor.

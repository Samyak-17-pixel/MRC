# outputs/mhw/climatology/ — Hobday Climatology & Thresholds

Day-of-year climatology and seasonally varying 90th-percentile thresholds used for MHW detection.

## Purpose

Define the Hobday baseline: for each DOY, a smoothed climatological SST and Threshold90. Events require SST > Threshold90 for ≥5 consecutive days; Intensity = SST − Threshold90.

## Key contents

| File | Description |
|------|-------------|
| `{region}_hobday.csv` | DOY, Climatology, Threshold90 (primary detection input) |
| `{region}_climatology.csv` / `{region}_threshold.csv` | Related/simple climatology products |
| `bob_spatial_climatology.nc`, `bob_spatial_threshold90.nc` | Spatial fields (if present) |
| `figures/`, `hobday_figures/` | Climatology / threshold plots |

## How generated

```bash
.venv/bin/python src/climate/scripts/build_hobday_climatology.py
.venv/bin/python src/climate/scripts/build_climatology.py          # simple reference
.venv/bin/python src/climate/scripts/plot_hobday_climatology.py    # figures
```

Method notes: 11-day window (±5 days) per DOY; 90th-percentile threshold, 31-day smoothed (Hobday et al. 2016).

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `outputs/timeseries/{region}_bob_sst.csv` | `detect_mhw.py` → catalogue; ML intensity features |

## Notes

Rebuilding climatology changes the entire event catalogue — only do so intentionally and then re-run detection and dependents.

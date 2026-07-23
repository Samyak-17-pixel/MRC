# outputs/timeseries/ — Regional SST & Wind Series

Foundational daily time series and merged SST cubes used by almost every later stage.

## Purpose

Provide regionally averaged SST and wind (and merged NetCDF cubes) for Hobday detection, driver analyses, maps, and ML features.

## Key contents

| File | Description |
|------|-------------|
| `combined_sst_2006_2025.nc` | Full-period merged Copernicus SST (~3.2 GB) |
| `combined_sst_2016_2025.nc` | Shorter merged cube (if present) |
| `{north,central,south}_bob_sst.csv` | Daily regional mean SST |
| `{region}_bob_sst_detrended.csv` | Linearly detrended SST (sensitivity) |
| `{region}_wind.csv` | Daily regional mean wind speed |

## How generated

| Script | Output |
|--------|--------|
| `src/climate/scripts/merge_sst.py` | `combined_sst_*.nc` |
| `src/climate/scripts/extract_regional_sst.py` | `*_bob_sst.csv` |
| `src/climate/scripts/detrend_sst.py` | `*_detrended.csv` |
| `src/climate/scripts/extract_regional_wind.py` | `*_wind.csv` |

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `data/raw/copernicus_daily_sst_*.nc`, wind NetCDFs | `outputs/mhw/` (climatology + catalogue), all driver pipelines, `src/ml/preprocessing/` |

## Notes

- SST boxes: 85–95°E; wind extraction historically 80–100°E (bbox mismatch documented in `data/raw/README.md`).
- Do not edit CSVs by hand; regenerate from scripts.

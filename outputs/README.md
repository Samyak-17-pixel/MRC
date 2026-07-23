# outputs/ — Climate Analysis Products

Every output of the **climate-analysis** pipeline (CSV numerical record + PNG/PDF figures). ML metrics/forecasts live under `src/ml/outputs/` instead.

The master numerical narrative is the repository root [`README.md`](../README.md).

## Purpose

Store regenerable scientific products: regional timeseries, Hobday catalogues, ENSO/IOD/MEI analyses, local drivers, synthesis catalogues, maps, and publication figures.

## Folder map

### Core data products

| Path | Produced by | Contents |
|------|-------------|----------|
| `timeseries/combined_sst_2006_2025.nc` | `src/climate/scripts/merge_sst.py` | Merged daily SST cube (~3.2 GB) |
| `timeseries/{region}_bob_sst.csv` | `extract_regional_sst.py` | Regional daily mean SST |
| `timeseries/{region}_wind.csv` | `extract_regional_wind.py` | Regional daily wind speed |
| `mhw/climatology/` | `build_hobday_climatology.py` | Hobday DOY + Threshold90 |
| `mhw/catalogue/` | `detect_mhw.py` | **Central event DB — 117 events** |

### MHW reporting

| Path | Contents |
|------|----------|
| `mhw/annual_statistics/` | Per-year counts, durations, intensities |
| `mhw/event_reports/` | Per-year event CSVs by region |
| `mhw/top_events/` | Top-10 strongest / longest |
| `mhw/figures/` | Count / duration / intensity vs year |
| `yearly/2016/` … `2026/` | Per-year SST maps and regional series |

### Climate indices & driver analyses

| Path | Contents |
|------|----------|
| `climate_indices/` | ONI / DMI / MEI characterization (nested `climate_indices/` subdir on disk) |
| `enso/`, `iod/`, `mei/` | Six-stage pipelines: lag, frequency, statistics, annual, seasonal, strength (+ analysis where present) |
| `climate_comparison/` | ENSO vs IOD vs MEI composite ranking |

### Local drivers

| Path | Contents |
|------|----------|
| `drivers/wind/` | Weak/strong classification; ~81% weak-wind headline; 117 event plots |
| `drivers/heat_flux/` | Regional SLHF/SSHF series |
| `drivers/heat_flux_analysis/` | Flux anomalies during MHWs |

### Synthesis

| Path | Contents |
|------|----------|
| `master_event_catalogue/` | 117 × 57 parameter table + figures |
| `top_event_sst_maps/` | Lifecycle SST maps for top events |
| `spatial_analysis/` | Spatial composites, trends, EOF (partial) |
| `maps/` | Base and per-variable map collections |
| `publication/` | Tables T01–T03, figures F01–F05, triptychs, dashboard |

## Key statistics (orientation)

- **117 MHW events**: North 49, Central 40, South 28 (2006–2025)
- **~81%** of events during anomalously weak wind
- **IOD** = strongest large-scale driver in all regions
- Longest: South 81 d (2024-06-14); strongest: South 0.943 °C (2024-04-14)

## Regenerating

Run the matching script under `src/climate/scripts/` (see that README for order). CSVs are deterministic given `data/raw/`.

## Notes

- Large NetCDFs and many PNGs may be gitignored.
- Nested folders such as `climate_indices/climate_indices/` reflect historical write paths; document paths as they exist on disk.
- ML reads these products but writes its own artifacts under `src/ml/outputs/`.

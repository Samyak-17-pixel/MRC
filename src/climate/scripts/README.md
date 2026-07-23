# src/climate/scripts/ — Climate-Analysis Pipeline

Every script of the scientific (non-ML) pipeline. Run from the **repository root**:

```bash
cd <repo-root>
.venv/bin/python src/climate/scripts/<script>.py
```

Scripts read `data/raw/` and existing `outputs/`, and write under `outputs/`. They do not modify raw data. ML lives in `src/ml/`.

## Pipeline order (dependency graph)

```
merge_sst.py → extract_regional_sst.py → build_hobday_climatology.py → detect_mhw.py
                                                                         │
               ┌─────────────────────────────────────────────────────────┤
               ▼                          ▼                    ▼          ▼
    ENSO/IOD/MEI pipelines      wind_mhw_analysis.py   heat_flux_*   reports/figures
               │                          │                    │
               └────────────┬─────────────┴────────────────────┘
                            ▼
     climate_driver_comparison.py → build_master_event_catalogue.py
                            ▼
     top_event_sst_lifecycle_maps.py → generate_publication_outputs.py
```

## Script reference

### Stage 1 — Data preparation

| Script | Purpose | Output |
|--------|---------|--------|
| `merge_sst.py` | Merge 4 Copernicus SST NetCDFs | `outputs/timeseries/combined_sst_2006_2025.nc` (~3.2 GB) |
| `extract_regional_sst.py` | Regional daily mean SST (N/C/S) | `outputs/timeseries/{north,central,south}_bob_sst.csv` |
| `detrend_sst.py` | Linearly detrended SST (sensitivity) | `outputs/timeseries/*_bob_sst_detrended.csv` |
| `build_hobday_climatology.py` | DOY climatology + Threshold90 | `outputs/mhw/climatology/{region}_hobday.csv` |
| `build_climatology.py` | Simple daily climatology (reference) | `outputs/mhw/climatology/{region}_climatology.csv` |
| `inspect_*.py` | Dataset verification | console |

### Stage 2 — MHW detection & reporting

| Script | Purpose | Output |
|--------|---------|--------|
| `detect_mhw.py` | Hobday events (≥5 days above P90) | `outputs/mhw/catalogue/` (**117 events**) |
| `generate_mhw_reports.py` | Annual stats, event reports, top-10 | `outputs/mhw/annual_statistics/`, `event_reports/`, `top_events/` |
| `mhw_statistics.py` | Catalogue summaries | `outputs/mhw/mhw_summary.txt`, `master_summary.csv` |
| `process_all_years.py` | Per-year SST maps + regional series | `outputs/yearly/2016/` … `2026/` |

### Stage 3 — Climate index characterization

| Script | Purpose | Output |
|--------|---------|--------|
| `enso_analysis.py` | ONI series, phases, climatology figs | `outputs/climate_indices/climate_indices/enso/` |
| `iod_analysis.py` | DMI characterization (+ may orchestrate IOD stages) | `outputs/climate_indices/climate_indices/iod/`, `outputs/iod/` |
| `mei_analysis.py` | MEI v2 characterization | `outputs/climate_indices/climate_indices/mei/` |

### Stage 4 — Driver pipelines (ENSO / IOD / MEI)

Identical six-stage design so drivers are comparable. Replace `enso` with `iod` or `mei`:

| Script | Stage | Output folder |
|--------|-------|---------------|
| `enso_lag_analysis.py` | Lag tagging + Pearson correlations | `outputs/enso/lag/` |
| `enso_frequency_analysis.py` | Phase frequency + χ² + Cramer's V | `outputs/enso/frequency/` |
| `enso_statistics.py` | Duration/intensity by phase | `outputs/enso/statistics/` |
| `enso_annual_analysis.py` | Annual counts vs index | `outputs/enso/annual/` |
| `enso_seasonal_analysis.py` | Season × phase contingency | `outputs/enso/seasonal/` |
| `enso_strength_analysis.py` | Strength-class analysis | `outputs/enso/strength/` |
| `enso_mhw_analysis.py` | Comprehensive ENSO–MHW figures | `outputs/enso/analysis/` |
| `mei_pipeline.py` | Orchestrator for all 6 MEI stages | `outputs/mei/{lag,…}/` |

### Stage 5 — Local drivers

| Script | Purpose | Output |
|--------|---------|--------|
| `extract_regional_wind.py` | Regional daily wind speed | `outputs/timeseries/{region}_wind.csv` |
| `wind_mhw_analysis.py` | Wind before/during MHW; weak/strong (**~81% weak**) | `outputs/drivers/wind/` |
| `wind_climatology_analysis.py` | Wind vs DOY climatology | `outputs/drivers/wind/` |
| `wind_mhw_summary.py` | Aggregated wind–MHW summary | `outputs/drivers/wind/` |
| `extract_heat_flux.py` | Regional SLHF/SSHF | `outputs/drivers/heat_flux/` |
| `heat_flux_mhw_analysis.py` | Flux anomalies during events | `outputs/drivers/heat_flux_analysis/` |
| `heat_flux_summary.py` | Flux summaries | `outputs/drivers/heat_flux/` |

### Stage 6 — Synthesis & publication

| Script | Purpose | Output |
|--------|---------|--------|
| `climate_driver_comparison.py` | ENSO vs IOD vs MEI ranking | `outputs/climate_comparison/` |
| `build_master_event_catalogue.py` | 117 events × 57 parameters | `outputs/master_event_catalogue/` |
| `top_event_sst_lifecycle_maps.py` | Before/during/after SST maps | `outputs/top_event_sst_maps/` |
| `top5_mhw_triptych_maps.py` | Top-5 pooled triptychs | `outputs/publication/figures/07_top5_triptychs/` |
| `generate_publication_outputs.py` | Tables T01–T03, figures F01–F05, dashboard | `outputs/publication/` |

### Supporting / exploratory

| Script | Notes |
|--------|-------|
| `plot_sst.py`, `plot_sst_heatmap.py`, `plot_regional_sst.py` | SST visualization → `outputs/mhw/figures/` (typical) |
| `plot_climatology.py`, `plot_hobday_climatology.py` | Climatology figures under `outputs/mhw/climatology/` |
| `enso_spatial_analysis.py` | Spatial composites → `outputs/spatial_analysis/` (partial) |
| `enso_final_pipeline.py` | Consolidated ENSO scaffold — deferred |
| `test_bob_map.py` | Base-map smoke test |

## Conventions

- Figures: typically 600 dpi PNG + PDF pairs.
- SST boxes: North 15–22°N, Central 10–15°N, South 5–10°N (85–95°E).
- Phase thresholds: ENSO/MEI ±0.5; IOD ±0.4.
- Scripts are idempotent: re-running overwrites outputs deterministically.

## Common issues

| Symptom | Cause / fix |
|---------|-------------|
| Cartopy coastline download | Cache under `cartopy_data/`; needs network once |
| `FileNotFoundError` under `outputs/` | Run an earlier stage first |
| Memory pressure in `merge_sst.py` | ~3.2 GB output; prefer ≥8 GB RAM |

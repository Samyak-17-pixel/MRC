# scripts/ — Climate-Analysis Pipeline

Every script of the scientific (non-ML) pipeline. All scripts are run from the **repository root** with the project virtualenv:

```bash
cd <repo-root>
.venv/bin/python scripts/<script>.py
```

Scripts read from `datasets/` and `results/`, and write to `results/`. None of them modify raw data. The ML module lives separately in `machine_learning/`.

Methodology details: [`documentation/04_methodology.md`](../documentation/04_methodology.md). Statistical methods: [`documentation/06_enso_analysis.md`](../documentation/06_enso_analysis.md) (the ENSO doc defines the framework reused by IOD and MEI).

---

## Pipeline Order (dependency graph)

```
merge_sst.py ─→ extract_regional_sst.py ─→ build_hobday_climatology.py ─→ detect_mhw.py
                                                                              │
              ┌───────────────────────────────────────────────────────────────┤
              ▼                          ▼                        ▼            ▼
   ENSO/IOD/MEI pipelines      wind_mhw_analysis.py    heat_flux_mhw_...   reports/figures
              │                          │                        │
              └────────────┬─────────────┴────────────────────────┘
                           ▼
        climate_driver_comparison.py → build_master_event_catalogue.py
                           ▼
        top_event_sst_lifecycle_maps.py → generate_publication_outputs.py
```

## Script Reference

### Stage 1 — Data preparation

| Script | Purpose | Output |
|--------|---------|--------|
| `merge_sst.py` | Merge the 4 Copernicus SST NetCDFs into one file | `results/combined_sst_2006_2025.nc` (~3.2 GB) |
| `extract_regional_sst.py` | Spatial-mean daily SST per region (N/C/S boxes) | `results/{north,central,south}_bob_sst.csv` |
| `detrend_sst.py` | Linearly detrended SST series (sensitivity use) | `results/*_bob_sst_detrended.csv` |
| `build_hobday_climatology.py` | Day-of-year climatology + 90th-percentile threshold (Hobday) | `results/climatology/{region}_hobday.csv` |
| `build_climatology.py` | Simple daily climatology (pre-Hobday, kept for reference) | `results/climatology/{region}_climatology.csv` |
| `inspect_copernicus.py`, `inspect_climate_indices.py`, `inspect_wind.py`, `inspect_heat_flux.py` | Dataset verification (dimensions, variables, ranges, gaps) | console output |

### Stage 2 — MHW detection & reporting

| Script | Purpose | Output |
|--------|---------|--------|
| `detect_mhw.py` | Hobday detection: ≥5 consecutive days above threshold → event catalogue | `results/mhw_catalogue/{region}_mhw_catalogue.csv` (117 events total) |
| `generate_mhw_reports.py` | Annual statistics, per-year event reports, top-10 lists | `results/annual_statistics/`, `results/event_reports/`, `results/top_events/` |
| `mhw_statistics.py` | Summary statistics across the catalogue | `results/mhw_summary.txt`, `results/master_summary.csv` |
| `process_all_years.py` | Per-year SST maps and regional time series | `results/2016/ … 2026/` |

### Stage 3 — Climate index characterization

| Script | Purpose | Output |
|--------|---------|--------|
| `enso_analysis.py` | ONI time series, phase classification, climatology figures | `results/climate_indices/enso/` |
| `iod_analysis.py` | DMI characterization **and** orchestrates the full 6-stage IOD pipeline | `results/climate_indices/iod/`, `results/iod_*/` |
| `mei_analysis.py` | MEI v2 characterization | `results/climate_indices/mei/` |

### Stage 4 — Driver pipelines (identical 6-stage design for ENSO / IOD / MEI)

Each driver has the same six scripts so that results are directly comparable. Replace `enso` with `iod` or `mei`:

| Script | Stage | Output folder |
|--------|-------|---------------|
| `enso_lag_analysis.py` | Tag every MHW with index values at 0/1/2/3/6-month lags; Pearson lag correlations | `results/enso_lag/` |
| `enso_frequency_analysis.py` | Phase frequency + chi-square + Cramer's V | `results/enso_frequency/` |
| `enso_statistics.py` | Descriptive stats + Kruskal–Wallis + Mann–Whitney across phases | `results/enso_statistics/` |
| `enso_annual_analysis.py` | Annual event counts vs annual index | `results/enso_annual/` |
| `enso_seasonal_analysis.py` | Season × phase chi-square contingency | `results/enso_seasonal/` |
| `enso_strength_analysis.py` | Event properties vs index strength class | `results/enso_strength/` |
| `enso_mhw_analysis.py` | Comprehensive ENSO–MHW figures (ENSO only) | `results/enso_analysis/` |
| `mei_pipeline.py` | Orchestrator running all 6 MEI stages | `results/mei_*/` |

### Stage 5 — Local drivers

| Script | Purpose | Output |
|--------|---------|--------|
| `extract_regional_wind.py` | Regional daily wind speed from u10/v10 | `results/{region}_wind.csv` |
| `wind_mhw_analysis.py` | Wind before/during each MHW; weak/strong classification (**headline: 78–84% weak wind**) | `results/wind_analysis/` (117 per-event plots) |
| `wind_climatology_analysis.py` | Wind vs day-of-year climatology during events | `results/wind_analysis/*_wind_climatology_analysis.csv` |
| `wind_mhw_summary.py` | Aggregated wind–MHW summary | `results/wind_analysis/` |
| `extract_heat_flux.py` | Regional SLHF/SSHF time series | `results/heat_flux/csv/` |
| `heat_flux_mhw_analysis.py` | Flux anomalies during events; reduced-latent-heat-loss flags | `results/heat_flux_analysis/` |
| `heat_flux_summary.py` | Flux summary tables | `results/heat_flux/` |

### Stage 6 — Synthesis & publication

| Script | Purpose | Output |
|--------|---------|--------|
| `climate_driver_comparison.py` | ENSO vs IOD vs MEI composite ranking (59 figures) | `results/climate_comparison/` |
| `build_master_event_catalogue.py` | Merge everything → 117 events × 57 parameters | `results/master_event_catalogue/` |
| `top_event_sst_lifecycle_maps.py` | Before/during/after SST maps for top-10 strongest + longest per region | `results/top_event_sst_maps/` (3,329 PNGs) |
| `top5_mhw_triptych_maps.py` | Top-5 pooled triptych heatmaps (publication style, left colorbar) | `results/publication/figures/07_top5_triptychs/` |
| `generate_publication_outputs.py` | Publication tables T01–T03, figures F01–F05, dashboard | `results/publication/` |
| `climate_driver_comparison.py` | Driver ranking heatmaps and dashboards | `results/climate_comparison/` |

### Supporting / exploratory

| Script | Purpose |
|--------|---------|
| `plot_sst.py`, `plot_sst_heatmap.py`, `plot_regional_sst.py` | SST visualization |
| `plot_climatology.py`, `plot_hobday_climatology.py` | Climatology/threshold figures |
| `enso_spatial_analysis.py` | ENSO spatial composites — **started, deferred (no figure output yet)** |
| `enso_final_pipeline.py` | Scaffold for a consolidated ENSO pipeline — **deferred** |
| `test_bob_map.py` | Base map smoke test |

## Conventions

- **Figures:** 600 dpi PNG + PDF pairs, consistent fonts/colors.
- **Regions:** North 15–22°N, Central 10–15°N, South 5–10°N (85–95°E for SST).
- **Phase thresholds:** ENSO/MEI ±0.5; IOD ±0.4 (see `documentation/06–08`).
- Scripts are idempotent: re-running overwrites outputs deterministically.

## Common Issues

| Symptom | Cause / fix |
|---------|-------------|
| Cartopy tries to download coastlines | Use cached `cartopy_data/`; needs internet once on fresh machines |
| `FileNotFoundError` on `results/...` | Run the earlier pipeline stage first (see dependency graph) |
| Memory pressure in `merge_sst.py` | ~3.2 GB output; use a machine with ≥8 GB RAM |

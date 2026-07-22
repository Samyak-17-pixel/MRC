# Part 9 — Visualizations (Figure Types)

This catalogue documents **figure types**, not every individual PNG. Counts are approximate from project inventories (`ALL_PROJECT_RESULTS.md`, folder READMEs).

Convention: most analysis figures are saved as **600 dpi PNG + PDF** pairs.

---

## 1. Core MHW Reporting

| Type | Purpose | Script(s) | Inputs | Output location | Interpretation | Example path |
|------|---------|-----------|--------|-----------------|----------------|--------------|
| Regional SST time series | Show daily SST + events | `plot_regional_sst.py`, `process_all_years.py` | Regional SST CSV, catalogue | `results/figures/`, `results/YYYY/` | Context for detection | `results/figures/` |
| Annual count / duration / intensity vs year | Interannual variability | `generate_mhw_reports.py`, `mhw_statistics.py` | Catalogues | `results/figures/`, `annual_statistics/` | 2024 peak activity | `results/annual_statistics/` |
| Per-year SST maps | Spatial SST by year | `process_all_years.py` | Combined SST NetCDF | `results/2016/` … `2026/` | Yearly spatial context | `results/2024/` |
| Top-10 tables/figures | Rank longest/strongest | `generate_mhw_reports.py` | Catalogues | `results/top_events/` | Record events | `results/top_events/top10_strongest_north.csv` |

---

## 2. Climatology & Thresholds

| Type | Purpose | Script | Inputs | Output | Interpretation | Example |
|------|---------|--------|--------|--------|----------------|---------|
| Climatology + Threshold90 curves | Show seasonal cycle and detection line | `plot_hobday_climatology.py` | `{region}_hobday.csv` | `results/climatology/hobday_figures/` | Threshold always above climatology | `results/climatology/hobday_figures/` |
| Spatial climatology maps | Grid-point seasonal mean / P90 | climatology builders + map scripts | spatial NetCDFs | `results/climatology/figures/` | Spatial structure of baseline | `results/climatology/bob_spatial_climatology.nc` |

---

## 3. Climate Index Characterization

| Type | Purpose | Script | Output |
|------|---------|--------|--------|
| ONI / DMI / MEI time series & phase plots | Index behavior 2006–2025 | `enso_analysis.py`, `iod_analysis.py`, `mei_analysis.py` | `results/climate_indices/{enso,iod,mei}/figures/` |

---

## 4. ENSO / IOD / MEI Stage Figures

For each driver, stage scripts write region-level PNG/CSV pairs:

| Type | What it shows | Folders |
|------|---------------|---------|
| Lag correlation plots | r vs lag for duration/intensity | `results/{enso,iod,mei}_lag/` |
| Phase frequency bars | Counts by phase + test annotation | `results/{enso,iod,mei}_frequency/` |
| Statistics box/violin-style comparisons | Duration/intensity by phase | `results/{enso,iod,mei}_statistics/figures/` |
| Annual scatter / time series | Annual activity vs index | `results/{enso,iod,mei}_annual/figures/` |
| Seasonal contingency visuals | Season × phase | `results/{enso,iod,mei}_seasonal/figures/` |
| Strength-class panels | Properties vs strength | `results/{enso,iod,mei}_strength/figures/` |
| ENSO overview suite | Combined ENSO–MHW figures | `results/enso_analysis/figures/` |

**Empty / deferred:** `results/enso_analysis/*_event_plots/` (0 files).

---

## 5. Climate Driver Comparison

| Type | Purpose | Script | Count | Output | Example |
|------|---------|--------|-------|--------|---------|
| Frequency / lag / heatmap / ranking / dashboard panels | Compare ENSO vs IOD vs MEI | `climate_driver_comparison.py` | 59 PNG + 59 PDF | `results/climate_comparison/figures/` | `results/climate_comparison/figures/rankings/` |

**Interpretation:** IOD ranks #1 in all regions on composite score.

---

## 6. Wind & Heat Flux

| Type | Purpose | Script | Count | Output | Example |
|------|---------|--------|-------|--------|---------|
| Per-event wind time series | Wind around each MHW | `wind_mhw_analysis.py` | 117 plots | `results/wind_analysis/{region}_event_plots/` | `results/wind_analysis/north_event_plots/` |
| Wind summary charts | Weak vs strong percentages | wind summary scripts | few | `results/wind_analysis/` | CSVs + figures |
| Heat-flux event diagnostics | SLHF/SSHF anomalies | `heat_flux_mhw_analysis.py` | tables ± figures | `results/heat_flux/`, `heat_flux_analysis/` | `results/heat_flux/csv/` |

**Interpretation:** ~81% weak-wind events; reduced latent heat loss in ~47% of events.

---

## 7. Master Event Catalogue Figures

| Type | Purpose | Script | Count | Output |
|------|---------|--------|-------|--------|
| Rendered tables | Publication-style tables | `build_master_event_catalogue.py` | part of 38 unique | `figures/tables/` |
| Parameter / phase heatmaps | Compact event×parameter view | same | part of 38 | `figures/heatmaps/` |
| Timelines | Duration bars, wind timelines | same | part of 38 | `figures/timelines/` |
| Dashboards | Regional / all-region overview | same | part of 38 | `figures/dashboards/` |
| Top-5 strongest/longest bars | Per-region top events | same | 6 PNG (+PDF) | `figures/top_events/` e.g. `north_top5_strongest.png` |

**Total:** 38 unique × PNG+PDF ≈ 76 files under `results/master_event_catalogue/figures/`.

---

## 8. Top-Event SST Lifecycle Maps

| Type | Purpose | Script | Count | Output |
|------|---------|--------|-------|--------|
| Daily SST / anomaly maps | Day-by-day lifecycle | `top_event_sst_lifecycle_maps.py` | thousands | `results/top_event_sst_maps/{strongest,longest}/...` |
| Composites, triptychs, difference maps, 5×3 grids | Summaries | same | included in ~3,329 PNGs | same |
| Regional mosaics | During-composite mosaics | same | few | `results/top_event_sst_maps/mosaics/` |

**Events processed:** 60 (top 10 strongest + top 10 longest × 3 regions).

Example: `results/top_event_sst_maps/longest/south/rank01_.../`

---

## 9. Publication Triptychs (Top-5 Pooled)

| Type | Purpose | Script | Output | Example |
|------|---------|--------|--------|---------|
| H01 SST triptych | Before/during/after absolute SST | `top5_mhw_triptych_maps.py` | `results/publication/figures/07_top5_triptychs/` | `.../longest/rank01_South_S25_2024-06-14/H01_triptych_sst.png` |
| H02 anomaly triptych | Same for SST anomaly; **colorbar on left** | same | same | `.../H02_triptych_anomaly.png` |
| Single-panel before/during/after | Separate panels | same | same event folders | `before_sst.png` |

---

## 10. Publication Summary Figures & Tables

| ID | Shows | Script | Path |
|----|-------|--------|------|
| F01 | Events by region | `generate_publication_outputs.py` | `results/publication/figures/F01_events_by_region.png` |
| F02 | Weak-wind % | same | `F02_weak_wind_percent.png` |
| F03 | Driver composite heatmap | same | `F03_driver_composite_heatmap.png` |
| F04 | Annual event counts | same | `F04_annual_event_counts.png` |
| F05 | ML best F1 heatmap | same | `F05_ml_best_f1_heatmap.png` |
| T01–T03 | Summary / rankings / ML tables | same | `results/publication/tables/` |
| D01 | Master dashboard | same | `results/publication/dashboards/` |

---

## 11. Machine Learning Figures

| Type | Purpose | Script | Output |
|------|---------|--------|--------|
| ROC / PR / confusion | Model performance | `04_evaluate_models.py` | `machine_learning/outputs/figures/` (after migration; historically `mhw_ml/outputs/figures/`) |
| SHAP / importance | Feature explanation | `05_explain_models.py` | `.../outputs/shap/` |

---

## 12. Base Maps

| Type | Purpose | Script / module | Example |
|------|---------|-----------------|---------|
| BoB base map | Coastline + region guides | `plotting/bob_map.py` | `bay_of_bengal_base_map.png` |

---

## 13. Related Docs

- Folder READMEs under `results/*/README.md`
- Results synthesis: `10_results.md`
- Numerical tables: `../ALL_PROJECT_RESULTS.md`

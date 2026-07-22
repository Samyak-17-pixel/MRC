# Part 4 — Complete Methodology (Chronological Workflow)

This document walks through the **entire climate-analysis workflow** from raw data to publication outputs. Machine learning is summarized only at the end; full ML detail is in `12_machine_learning.md`.

**Non-negotiable:** Do not change thresholds, region boxes, Hobday parameters, or reported numbers when reproducing — only re-run scripts to regenerate outputs.

---

## 0. Design Principles

1. **Hobday first** — build a clean event catalogue before driver attribution.
2. **Identical stats across drivers** — ENSO, IOD, and MEI share the same six-stage design.
3. **Local + remote** — wind/heat flux analysed alongside climate indices.
4. **Document limitations** — do not silently "fix" known data issues.
5. **ML last** — predictors must be motivated by prior statistical/physical results.

---

## 1. Data Collection

| Step | Action | Output location |
|------|--------|-----------------|
| Download Copernicus SST (4 blocks) | CMEMS portal | `datasets/copernicus_daily_sst_*.nc` |
| Download wind | CMEMS | `datasets/Wind_speed_data_2006_2025/` |
| Download heat flux | CMEMS | `datasets/heat_flux_data_2006_2025/` |
| Download ONI, DMI, MEI | NOAA CPC / PSL | `datasets/oni.nc`, `dmi.had.long.nc`, `meiv2.nc` |

See `03_datasets.md` for sources, units, and rationale.

---

## 2. Dataset Verification

Scripts: `inspect_copernicus.py`, `inspect_climate_indices.py`, `inspect_wind.py`, `inspect_heat_flux.py`.

**Purpose:** Confirm dimensions, variable names, time coverage, coordinate ranges, and obvious gaps before analysis.

**Assumption:** Files named as in `datasets/README.md` are present and readable by xarray/netCDF4.

---

## 3. SST Merge and Regional Extraction

```
scripts/merge_sst.py
scripts/extract_regional_sst.py
# optional: scripts/detrend_sst.py
```

1. Concatenate four SST NetCDFs → `results/combined_sst_2006_2025.nc`.
2. Compute daily spatial-mean SST for North / Central / South boxes → `results/{region}_bob_sst.csv`.

**Region boxes (analysis):**

| Region | Latitude | Longitude |
|--------|----------|-----------|
| North | 15–22°N | 85–95°E |
| Central | 10–15°N | 85–95°E |
| South | 5–10°N | 85–95°E |

**Map display lines** (red lines on figures) use 18°N and 12°N — visual guides, not the SST averaging edges. See `plotting/README.md`.

---

## 4. Climatology and Threshold (Hobday)

```
scripts/build_hobday_climatology.py
```

For each region and day-of-year (DOY):

1. Pool SST in an **11-day window** (±5 days) across all years 2006–2025.
2. Compute mean → `Climatology`.
3. Compute **90th percentile** → raw threshold.
4. Smooth with **31-day** moving average → `Threshold90`.

Output: `results/climatology/{region}_hobday.csv`.

Details: `05_mhw_detection.md`.

---

## 5. MHW Detection and Catalogues

```
scripts/detect_mhw.py
scripts/generate_mhw_reports.py
scripts/mhw_statistics.py
```

- Flag days with SST > Threshold90.
- Group runs of **≥5 consecutive days** into events.
- Write catalogues: Start_Date, End_Date, Duration_Days, Mean_Intensity, Max_Intensity.
- Produce annual stats, top-10 lists, per-year reports.

**Result:** 117 events (North 49, Central 40, South 28).

---

## 6. Climate Index Collection and Preprocessing

```
scripts/enso_analysis.py   # ONI characterization
scripts/iod_analysis.py    # DMI characterization (+ can orchestrate IOD pipeline)
scripts/mei_analysis.py    # MEI characterization
```

- Read NetCDF indices → monthly time series CSVs under `results/climate_indices/{enso,iod,mei}/`.
- Assign phases using project thresholds (ENSO/MEI ±0.5; IOD ±0.4).
- Produce characterization figures.

---

## 7. ENSO Analysis (Full Six Stages)

Scripts: `enso_lag_analysis.py`, `enso_frequency_analysis.py`, `enso_statistics.py`, `enso_annual_analysis.py`, `enso_seasonal_analysis.py`, `enso_strength_analysis.py`, plus `enso_mhw_analysis.py` for overview figures.

| Stage | Method |
|-------|--------|
| Event matching | Attach ONI at event start month and lags 1/2/3/6 months |
| Frequency | Chi-square + Cramer's V across El Niño / Neutral / La Niña |
| Statistics | Kruskal–Wallis / Mann–Whitney on duration & intensity by phase |
| Lag | Pearson correlation of lagged ONI with duration/intensity |
| Annual | Annual event metrics vs annual ONI |
| Seasonal | Season × phase contingency chi-square |
| Strength | Event properties vs ENSO strength classes |

Full detail: `06_enso_analysis.md`.

---

## 8. IOD Analysis

Same six stages with DMI replacing ONI. Orchestrator: `iod_analysis.py` (also runs stages) or individual `iod_*` scripts.

Full detail: `07_iod_analysis.md`.

---

## 9. MEI Analysis

Same six stages with MEI v2. Orchestrator: `mei_pipeline.py`.

Full detail: `08_mei_analysis.md`.

---

## 10. Wind Analysis

```
scripts/extract_regional_wind.py
scripts/wind_mhw_analysis.py
scripts/wind_climatology_analysis.py
```

For each of 117 events: wind before (30/21/14/7 days), during, anomaly vs climatology, weak/strong flag.

**Headline:** 78–84% of events during weak wind (81.2% overall).

---

## 11. Heat Flux Analysis

```
scripts/extract_heat_flux.py
scripts/heat_flux_mhw_analysis.py
```

SLHF/SSHF during events vs climatology; reduced latent-heat-loss flags (~47% of events).

---

## 12. Comparative Driver Assessment

```
scripts/climate_driver_comparison.py
```

Builds composite scores from frequency, lag, annual, seasonal, strength tests → ranks ENSO vs IOD vs MEI per region.

**Result:** IOD #1 in North, Central, and South.

---

## 13. Master Event Catalogue

```
scripts/build_master_event_catalogue.py
```

Merges metadata, SST, climate indices (all lags/phases), wind, heat flux → 117 × 57 table + figures.

---

## 14. Visualization and Spatial Lifecycle Maps

```
scripts/process_all_years.py
scripts/top_event_sst_lifecycle_maps.py
scripts/top5_mhw_triptych_maps.py
scripts/generate_publication_outputs.py
# plus many plot_* and *mhw_analysis figure scripts
```

Figure types catalogued in `09_visualizations.md`.

---

## 15. Machine Learning (Separate Module)

```
python machine_learning/run_pipeline.py
# (compatibility: mhw_ml/ wrapper after migration)
```

Onset prediction within 3/7/14 days; features from SST, wind, flux, climate indices; chronological split. See `12_machine_learning.md`.

---

## 16. Statistical Methods Used Across Driver Pipelines

| Method | Application | Why chosen |
|--------|-------------|------------|
| Pearson correlation | Lags, annual associations | Standard linear association; continuous indices |
| Chi-square goodness-of-fit | Phase frequency vs equal expectation | Tests uneven phase occurrence |
| Cramer's V | Effect size for chi-square | Magnitude beyond p-value |
| Chi-square independence | Season × phase | Contingency structure |
| Kruskal–Wallis | Duration/intensity across 3 phases | Non-parametric; uneven/skewed samples |
| Mann–Whitney U | Pairwise phases | Non-parametric pairwise follow-up |
| Linear regression (plots) | Trend lines on scatter plots | Visualization aid |

**Assumption for frequency tests:** equal expected distribution across three phases (explicit project choice; alternative would weight by climatological phase frequency).

---

## 17. Regional Division — Why Three Boxes?

| Reason | Explanation |
|--------|-------------|
| Latitudinal climate gradients | Monsoon, SST, and teleconnection footprints vary N→S |
| Comparable sample sizes | Enough events per box for statistics (49 / 40 / 28) |
| Interpretability | Regional differences (e.g., South ENSO El Niño enrichment vs North/Central MEI La Niña) would be blurred in a single Bay-mean |

Coordinates and map vs analysis boundaries: §3 above and `plotting/README.md`.

---

## 18. Future Methodology (Not Yet Run)

- Multivariate analysis (correlation, PCA/EOF, regression, VIF)
- Additional variables: radiation, MLD, currents, SSS, precipitation, SLP, BSISO
- Fisheries impact linkage
- Journal manuscript assembly

See `11_future_work.md`.

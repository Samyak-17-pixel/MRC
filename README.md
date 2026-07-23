# Bay of Bengal Marine Heatwave Project

**Drivers, Predictability, and Fisheries Impact of Marine Heatwaves in the Bay of Bengal (2006–2025)**

| | |
|---|---|
| **Author** | Samyak Kumar |
| **Institution** | Maritime Research Center (MRC) |
| **Study period** | 2006–2025 (20 years, daily) |
| **Study region** | Bay of Bengal — North / Central / South |
| **Status** | Climate-driver analysis complete · ML forecasting v1 complete · Multivariate analysis and fisheries impact pending |
| **Updated** | 2026-07-23 |

This README is the master project document: how to use the repo, headline findings, full methodology reference, complete numerical results, and the ML module guide. Each major folder also has its own `README.md`.

---

## Table of contents

1. [How to use this repository](#how-to-use-this-repository)
2. [Headline findings](#headline-findings)
3. [Project reference](#part-a--project-reference)
4. [Complete results](#part-b--complete-results)
5. [Machine learning module](#part-c--machine-learning-module)
6. [Folder guides](#folder-guides)

---

## How to use this repository

### Repository layout

```text
MRC/
├── README.md                 ← this file
├── requirements.txt          ← Python dependencies
├── .gitignore                ← excludes NetCDF, figures, models, .venv
├── data/raw/                 ← place raw NetCDF inputs here (not in Git)
├── src/
│   ├── paths.py              ← shared path constants
│   ├── climate/
│   │   ├── scripts/          ← climate analysis pipeline
│   │   └── plotting/         ← Cartopy / map helpers
│   └── ml/                   ← MHW onset forecasting
├── outputs/                  ← climate products (CSVs tracked; NetCDF/PNG ignored)
└── archive/                  ← old root scripts kept for reference
```

| Path | What it is |
|------|------------|
| `data/raw/` | Input NetCDFs (SST, wind, heat flux, ONI/DMI/MEI) |
| `src/climate/scripts/` | Climate science scripts — run from repo root |
| `src/ml/` | ML train / evaluate / forecast pipeline |
| `outputs/` | Climate results (`mhw/`, `enso/`, `iod/`, `mei/`, `drivers/`, …) |
| `src/ml/outputs/` | ML metrics, SHAP, forecasts |

### 1. Clone and set up the environment

```bash
git clone https://github.com/Samyak-17-pixel/MRC.git
cd MRC

python3.10 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Python:** 3.10+ (tested on 3.10.12).  
**Stack:** numpy, pandas, scipy, xarray, netCDF4, matplotlib, Cartopy, scikit-learn, xgboost, shap, PyYAML, joblib.

### 2. Add raw data (required to re-run the climate pipeline)

Raw NetCDF files are **not** in Git (too large). Place them under `data/raw/` as described in [`data/raw/README.md`](data/raw/README.md):

| Input | Expected location |
|-------|-------------------|
| Copernicus daily SST (4 files) | `data/raw/copernicus_daily_sst_*.nc` |
| 10 m wind | `data/raw/Wind_speed_data_2006_2025/` |
| Heat flux (yearly folders) | `data/raw/heat_flux_data_2006_2025/` |
| ONI / DMI / MEI | `data/raw/oni.nc`, `dmi.had.long.nc`, `meiv2.nc` |

CSV products under `outputs/` and `src/ml/` **are** in the repo, so you can inspect results without re-downloading NetCDF.

### 3. Run scripts (always from the repository root)

```bash
cd /path/to/MRC
source .venv/bin/activate

# Climate example
.venv/bin/python src/climate/scripts/detect_mhw.py

# ML full pipeline
.venv/bin/python src/ml/run_pipeline.py

# Latest-day forecast + 2025 catalogue verification
.venv/bin/python src/ml/experiments/06_predict_current.py
```

Do **not** `cd` into `src/climate/scripts/` or `src/ml/` before running — paths are resolved from the repo root.

### 4. Typical workflows

**A. Explore existing results (no NetCDF needed)**

- MHW catalogues: `outputs/mhw/catalogue/`
- Driver tables: `outputs/enso/`, `outputs/iod/`, `outputs/mei/`, `outputs/drivers/`
- Master event table: `outputs/master_event_catalogue/csv/`
- ML metrics / forecast: `src/ml/outputs/metrics/`, `src/ml/outputs/forecasts/`

**B. Rebuild the MHW catalogue (needs SST NetCDF)**

```bash
.venv/bin/python src/climate/scripts/merge_sst.py
.venv/bin/python src/climate/scripts/extract_regional_sst.py
.venv/bin/python src/climate/scripts/build_hobday_climatology.py
.venv/bin/python src/climate/scripts/detect_mhw.py
.venv/bin/python src/climate/scripts/generate_mhw_reports.py
```

**C. Re-run a climate-driver pipeline**

```bash
# ENSO (or use iod_analysis.py / mei_pipeline.py for the other drivers)
.venv/bin/python src/climate/scripts/enso_lag_analysis.py
.venv/bin/python src/climate/scripts/enso_frequency_analysis.py
.venv/bin/python src/climate/scripts/enso_statistics.py
.venv/bin/python src/climate/scripts/enso_annual_analysis.py
.venv/bin/python src/climate/scripts/enso_seasonal_analysis.py
.venv/bin/python src/climate/scripts/enso_strength_analysis.py
.venv/bin/python src/climate/scripts/enso_mhw_analysis.py
```

Full ordered command list: [§ Execution Commands](#8-execution-commands) below. Script details: [`src/climate/scripts/README.md`](src/climate/scripts/README.md).

**D. Machine learning**

```bash
.venv/bin/python src/ml/run_pipeline.py                 # steps 01→06
.venv/bin/python src/ml/preprocessing/01_build_dataset.py
.venv/bin/python src/ml/training/02_train_baselines.py
.venv/bin/python src/ml/training/03_train_models.py
.venv/bin/python src/ml/evaluation/04_evaluate_models.py
.venv/bin/python src/ml/evaluation/05_explain_models.py
.venv/bin/python src/ml/experiments/06_predict_current.py
```

See [`src/ml/README.md`](src/ml/README.md) and Part C below.

### 5. What Git tracks vs ignores

| Tracked | Ignored (local only) |
|---------|----------------------|
| Code, READMEs, `requirements.txt` | `.venv/` |
| CSV results under `outputs/` and `src/ml/` | `*.nc` (raw + combined SST) |
| Config YAML | `*.png`, `*.pdf` (figures) |
| | `*.joblib` / model binaries |

Regenerate figures and models with the scripts above; see `.gitignore`.

### 6. Conventions (do not change casually)

- **MHW definition:** Hobday et al. (2016) — SST > seasonally varying 90th percentile for ≥ 5 consecutive days.
- **Intensity in this project:** `SST − Threshold90` (applied consistently in catalogues and ML).
- **Regions:** North / Central / South Bay of Bengal (boxes in Part A §2).
- Path constants: prefer `src/paths.py` (climate) and `src/ml/common.py` (ML).

---

## Headline findings

- **81.2%** of MHWs (95/117) occurred during anomalously **weak surface winds**.
- **IOD** is the strongest large-scale climate driver in all three regions.
- **ENSO** matters most in **South BoB** (54% El Niño; significant 6-month lag).
- **2024** produced the longest (81 d) and strongest (0.943 °C) events (South).
- **2025** had **13** Hobday starts (North 8, Central 4, South 1).
- ML onset forecasting (test 2022–2025): best **F1 ≈ 0.40** at 14-day; 2025 year verification with best models: **13/13** at 14-day pre-onset alert.

**Critical:** Hobday catalogues count events that **occurred**. The ML forecast answers whether a **new** event will **start in the next 3/7/14 days** from the latest data day (currently 2025-12-31). Those are different questions.

---

# Part A — Project Reference

Objectives, regions, data, phase status, directory map, and the full ordered command list. For day-to-day setup see [How to use this repository](#how-to-use-this-repository).

---

### 1. Project Objective

Investigate the **drivers, characteristics, and predictability** of Marine Heatwaves (MHWs) in the Bay of Bengal by combining:

1. Satellite / reanalysis observations (Copernicus Marine Service)
2. Large-scale climate indices (ONI, DMI, MEI v2)
3. Regional atmospheric and oceanographic variables (wind, heat flux, etc.)
4. Statistical analyses
5. Multivariate analysis
6. Machine learning forecasting

**Philosophy:** Establish physical and statistical understanding of MHW mechanisms *before* predictive modelling. Every ML predictor must be supported by statistical evidence and physical reasoning.

---

### 2. Study Region

The Bay of Bengal is divided into three latitudinal sub-regions:

| Region | SST Box (°N, °E) | Map Boundaries |
|--------|------------------|----------------|
| **North** | 15–22°N, 85–95°E | Above 18°N |
| **Central** | 10–15°N, 85–95°E | 12–18°N |
| **South** | 5–10°N, 85–95°E | Below 12°N |

Base map: `archive/bay_of_bengal_base_map.png` (generated by `src/climate/plotting/bob_map.py`)

---

### 3. Data Sources

#### Copernicus Marine Service (primary — all environmental variables)

| Variable | Location | Period |
|----------|----------|--------|
| Daily SST (`thetao`) | `data/raw/copernicus_daily_sst_*.nc` (4 files) | 2006–2025 |
| 10m wind (`u10`, `v10`) | `data/raw/Wind_speed_data_2006_2025/` | 2006–2025 |
| Latent + sensible heat flux | `data/raw/heat_flux_data_2006_2025/` (20 yearly folders) | 2006–2025 |

#### Climate Indices (external — internationally recognized)

| Index | File | Period | Role |
|-------|------|--------|------|
| ONI (ENSO) | `data/raw/oni.nc` | 1950–2026 | El Niño / La Niña |
| DMI (IOD) | `data/raw/dmi.had.long.nc` | 1870–2025 | Indian Ocean Dipole |
| MEI v2 | `data/raw/meiv2.nc` | 1979–2026 | Multivariate ENSO |

**Note:** NOAA OISST was explored initially but replaced by Copernicus SST (higher resolution ~0.083°, better coastal representation, consistency with other variables).

---

### 4. MHW Detection Methodology

**Definition:** Hobday et al. (2016)

- 11-day window (±5 days) climatology per day-of-year
- 90th-percentile threshold, 31-day smoothed
- Event = ≥5 consecutive days above threshold
- Intensity = SST − Threshold90

**MHW Catalogue (central database for all analyses):**

| Region | Events | Longest (days) | Strongest (°C) |
|--------|--------|----------------|----------------|
| North | 49 | 61 | 0.912 |
| Central | 40 | 53 | 0.908 |
| South | 28 | 81 | 0.943 |
| **Total** | **117** | — | — |

**Record event:** South, 2024-04-14 to 2024-05-24 (Max Intensity 0.943°C, 41 days)  
**Longest event:** South, 2024-06-14 to 2024-09-02 (81 days)

---

### 5. Completed Work

#### Phase 1: Data Preparation ✅

- [x] Downloaded and inspected Copernicus SST (4 NetCDF files, 2006–2025)
- [x] Merged into `outputs/combined_sst_2006_2025.nc` (~3.2 GB)
- [x] Extracted regional daily SST time series (North, Central, South)
- [x] Built Hobday climatology and 90th-percentile thresholds
- [x] Downloaded and inspected ONI, DMI, MEI v2, wind, heat flux datasets

**Scripts:** `merge_sst.py`, `extract_regional_sst.py`, `build_hobday_climatology.py`, `inspect_*.py`

#### Phase 2: MHW Detection & Reporting ✅

- [x] Detected all MHW events per region (Hobday method)
- [x] Generated annual statistics, per-year event reports, top-10 events
- [x] Produced SST timeseries, MHW count/duration/intensity vs year figures
- [x] Per-year SST maps and regional timeseries (2016–2026)

**Scripts:** `detect_mhw.py`, `generate_mhw_reports.py`, `mhw_statistics.py`, `plot_regional_sst.py`, `process_all_years.py`

**Outputs:** `outputs/mhw/catalogue/`, `outputs/mhw/annual_statistics/`, `outputs/mhw/event_reports/`, `outputs/mhw/top_events/`, `outputs/mhw/figures/`

#### Phase 3: Climate Index Characterization ✅

- [x] ONI timeseries, phase classification, climatology figures
- [x] DMI timeseries, phase classification, climatology figures
- [x] MEI v2 full statistical characterization

**Scripts:** `enso_analysis.py`, `iod_analysis.py` (index characterization only — see `climate_indices/`), `mei_analysis.py`

**Outputs:** `outputs/climate_indices/{enso,iod,mei}/`

#### Phase 4: ENSO–MHW Analysis ✅

Full event-based analysis linking every MHW to ONI at 0, 1, 2, 3, 6-month lags.

| Analysis | Script | Output Directory | Status |
|----------|--------|------------------|--------|
| Event tagging + lag correlation | `enso_lag_analysis.py` | `outputs/enso/lag/` | ✅ |
| Phase frequency + chi-square | `enso_frequency_analysis.py` | `outputs/enso/frequency/` | ✅ |
| Duration/intensity statistics | `enso_statistics.py` | `outputs/enso/statistics/` | ✅ |
| Annual variability | `enso_annual_analysis.py` | `outputs/enso/annual/` | ✅ |
| Seasonal dependence | `enso_seasonal_analysis.py` | `outputs/enso/seasonal/` | ✅ |
| ENSO strength classification | `enso_strength_analysis.py` | `outputs/enso/strength/` | ✅ |
| Comprehensive ENSO–MHW figures | `enso_mhw_analysis.py` | `outputs/enso/analysis/` | ✅ |

**ENSO Key Findings:**

| Test | North | Central | South |
|------|-------|---------|-------|
| Phase frequency (chi-square p) | 0.066 (NS) | 0.082 (NS) | **0.020 (SIG)** |
| Best lag correlation (months) | 6 | 6 | **6** |
| Best lag r (duration, p) | 0.135 (0.354) | 0.290 (0.070) | **0.433 (0.021)** |
| Duration/intensity by phase | Not significant | Not significant | Not significant |
| Annual ONI correlation | Weak / NS | Weak / NS | Weak / NS |
| Seasonal chi-square | NS | NS | NS |

**South BoB:** ENSO enrichment during El Niño (54% of events) with significant 6-month lag teleconnection.

#### Phase 5: Local Driver Analysis (Wind & Heat Flux) ✅

| Analysis | Script | Key Finding |
|----------|--------|-------------|
| Wind before/during MHW | `wind_mhw_analysis.py` | **78–84% of events during weak wind** |
| Wind vs climatology | `wind_climatology_analysis.py` | Consistent across all regions |
| Heat flux during MHW | `heat_flux_mhw_analysis.py` | Reduced latent heat loss (South: 61.5%) |
| Heat flux timeseries | `extract_heat_flux.py` | SLHF/SSHF 2006–2025 per region |

**Outputs:** `outputs/drivers/wind/` (117 per-event wind plots), `outputs/drivers/heat_flux/`, `outputs/drivers/heat_flux_analysis/`

**Headline finding (`results_text`):** ~78–84% of BoB MHW events occurred during anomalously weak surface wind conditions.

#### Phase 6: IOD–MHW Analysis ✅ (COMPLETED 2026-07-11)

Full pipeline mirroring ENSO methodology exactly. DMI replaces ONI.

| Analysis | Script | Output Directory | Status |
|----------|--------|------------------|--------|
| Event tagging + lag correlation | `iod_lag_analysis.py` | `outputs/iod/lag/` | ✅ |
| Phase frequency + chi-square | `iod_frequency_analysis.py` | `outputs/iod/frequency/` | ✅ |
| Duration/intensity statistics | `iod_statistics.py` | `outputs/iod/statistics/` | ✅ |
| Annual variability | `iod_annual_analysis.py` | `outputs/iod/annual/` | ✅ |
| Seasonal dependence | `iod_seasonal_analysis.py` | `outputs/iod/seasonal/` | ✅ |
| IOD strength classification | `iod_strength_analysis.py` | `outputs/iod/strength/` | ✅ |
| Pipeline orchestrator | `iod_analysis.py` | Runs all 6 stages | ✅ |

**IOD Classification Thresholds:**
- Positive IOD: DMI ≥ +0.4
- Negative IOD: DMI ≤ −0.4
- Neutral: otherwise

**IOD Strength Thresholds:**
- Strong Positive: ≥ 0.8 | Moderate: 0.6–0.8 | Weak: 0.4–0.6
- Strong Negative: ≤ −0.8 | Moderate: −0.8 to −0.6 | Weak: −0.6 to −0.4

**IOD Key Findings:**

| Test | North | Central | South |
|------|-------|---------|-------|
| Phase frequency (chi-square p) | **< 0.001 (SIG)** | **< 0.001 (SIG)** | **0.0003 (SIG)** |
| Dominant phase | 68% Neutral | 71% Neutral | 63% Neutral |
| Best lag correlation (months) | 3 | **6** | **6** |
| Best lag r (duration, p) | 0.083 (0.589) | **0.344 (0.030)** | **0.459 (0.014)** |
| Intensity at lag 0 (South) | — | — | r = 0.402, p = 0.038 |
| Duration/intensity by phase | NS (p > 0.25) | NS (p > 0.13) | NS (p > 0.35) |
| Annual DMI correlation | All NS | All NS | All NS |
| Seasonal chi-square | NS (0.584) | NS (0.481) | NS (0.649) |
| IOD strength effect | NS (p > 0.10) | NS (p > 0.10) | NS (p > 0.79) |

**Data note:** 8 events (5 North, 2 Central, 1 South) have `Unknown` IOD phase because DMI data ends April 2025 while some MHW events extend into late 2025.

#### Phase 7: MEI v2–MHW Analysis ✅ (COMPLETED 2026-07-11)

Full pipeline mirroring ENSO and IOD methodology. MEI v2 replaces ONI/DMI.

| Analysis | Script | Output Directory | Status |
|----------|--------|------------------|--------|
| Event tagging + lag correlation | `mei_lag_analysis.py` | `outputs/mei/lag/` | ✅ |
| Phase frequency + chi-square | `mei_frequency_analysis.py` | `outputs/mei/frequency/` | ✅ |
| Duration/intensity statistics | `mei_statistics.py` | `outputs/mei/statistics/` | ✅ |
| Annual variability | `mei_annual_analysis.py` | `outputs/mei/annual/` | ✅ |
| Seasonal dependence | `mei_seasonal_analysis.py` | `outputs/mei/seasonal/` | ✅ |
| MEI strength classification | `mei_strength_analysis.py` | `outputs/mei/strength/` | ✅ |
| Pipeline orchestrator | `mei_pipeline.py` | Runs all 6 stages | ✅ |

**MEI Classification Thresholds (same as ONI/ENSO):**
- El Niño: MEI ≥ +0.5
- La Niña: MEI ≤ −0.5
- Neutral: otherwise

**MEI Key Findings:**

| Test | North | Central | South |
|------|-------|---------|-------|
| Phase frequency (chi-square p) | **0.001 (SIG)** | **0.002 (SIG)** | 0.331 (NS) |
| Dominant phase | **57% La Niña** | **60% La Niña** | 46% El Niño |
| Best lag correlation (months) | 3 | 0 | 6 |
| Best lag r (duration, p) | 0.037 (0.804) | 0.228 (0.157) | 0.292 (0.131) |
| Duration/intensity by phase | NS | NS | NS |
| Annual MEI correlation | All NS | All NS | All NS |
| Seasonal chi-square | NS (0.302) | **SIG (0.001)** | NS (0.212) |
| MEI strength effect | NS | NS | NS |

**Notable:** North and Central show significant **La Niña enrichment** (opposite to ONI South El Niño pattern). Central BoB shows significant seasonal dependence on MEI phase.

#### Phase 8: Comparative Climate-Driver Assessment ✅ (COMPLETED 2026-07-11)

Direct ENSO vs IOD vs MEI comparison with rankings, heatmaps, and dashboards.

| Deliverable | Script | Output |
|-------------|--------|--------|
| Master comparison + 59 figures | `climate_driver_comparison.py` | `outputs/climate_comparison/` |

**Driver Rankings (Composite Score):**

| Region | #1 | #2 | #3 |
|--------|----|----|-----|
| North | **IOD** (59) | MEI (50) | ENSO (48) |
| Central | **IOD** (87) | MEI (79) | ENSO (57) |
| South | **IOD** (99) | ENSO (85) | MEI (48) |

**Key conclusion:** IOD is the strongest large-scale climate driver across all regions. ENSO is second in South only. Local wind (78–84% weak) remains the dominant immediate driver.

**Outputs:** 7 CSVs + 59 PNG + 59 PDF figures organized in:
`figures/{frequency,lag,heatmaps,statistics,annual,seasonal,strength,rankings,dashboards}/`

#### Phase 9: Master MHW Event Catalogue ✅ (COMPLETED 2026-07-12)

Per-event master table merging every analyzed parameter for all 117 MHWs.

| Deliverable | Script | Output |
|-------------|--------|--------|
| Master event tables + 76 figures | `build_master_event_catalogue.py` | `outputs/master_event_catalogue/` |

**Coverage (57 columns per event):**
- Event metadata: dates, duration, season, year
- SST: mean/max/min, range, Hobday threshold, intensity
- Climate indices: ONI, DMI, MEI at 0/1/2/3/6-month lags + phases
- Wind: 30/21/14/7-day before + during, change, climatology, anomaly, classification
- Heat flux: SLHF/SSHF climatology, during-event, anomaly + reduced-loss flags

**Key files:**
- `csv/all_regions_master_event_catalogue.csv` — all 117 events
- `csv/{north,central,south}_master_event_catalogue.csv` — per region
- `csv/{region}_01_event_sst.csv` … `_04_heat_flux.csv` — split category tables
- `csv/column_glossary.csv` — column definitions
- `csv/regional_summary_statistics.csv` — regional aggregates

**Figures (38 unique × PNG+PDF = 76 files):**
- `figures/tables/` — master summary, SST details, climate indices, wind, heat flux
- `figures/heatmaps/` — parameter + phase/flag heatmaps per region
- `figures/timelines/` — event duration bars + wind timelines
- `figures/dashboards/` — per-region + all-regions overview
- `figures/top_events/` — top-5 longest and strongest per region

#### Phase 10: Top-Event SST Lifecycle Maps ✅ (COMPLETED 2026-07-12)

Spatial SST maps for top-10 strongest and longest MHWs per region.

| Deliverable | Script | Output |
|-------------|--------|--------|
| Before/during/after SST maps + summaries | `top_event_sst_lifecycle_maps.py` | `outputs/top_event_sst_maps/` |

**Per event (5+5+5 days):**
- Daily SST + anomaly maps (before / during / after)
- 5-day composites, triptych, lifecycle 5×3 grid, difference maps
- Strongest: during days centered on peak intensity
- Longest: during days evenly spaced across event

**Organization:**
```
top_event_sst_maps/
├── index/                    # CSV index of all events
├── strongest/{north,central,south}/rank##_EVENT_DATE/
├── longest/{north,central,south}/rank##_EVENT_DATE/
└── mosaics/{strongest,longest}/  # regional during-composite mosaics

---

### 6. ENSO vs IOD vs MEI Comparison (Preliminary)

| Aspect | ENSO (ONI) | IOD (DMI) | MEI v2 | Strongest? |
|--------|-----------|-----------|--------|------------|
| Phase frequency (North p) | 0.066 NS | **< 0.001 SIG** | **0.001 SIG** | IOD / MEI |
| Phase frequency (Central p) | 0.082 NS | **< 0.001 SIG** | **0.002 SIG** | IOD / MEI |
| Phase frequency (South p) | **0.020 SIG** | **0.0003 SIG** | 0.331 NS | IOD |
| Dominant phase (South) | 54% El Niño | 63% Neutral | 46% El Niño | Different |
| Dominant phase (North) | 49% Neutral | 68% Neutral | **57% La Niña** | MEI unique |
| Lag r South 6mo (p) | **0.433 (0.021)** | **0.459 (0.014)** | 0.292 (0.131) | IOD |
| Lag r Central 6mo (p) | 0.290 (0.070) | **0.344 (0.030)** | 0.228 (0.157) | IOD |
| Seasonal SIG | None | None | Central only | MEI |
| Local wind driver | **78–84% weak wind** | — | — | **Wind** |

---

### 7. Directory Structure

```text
MRC/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── raw/                         ← NetCDF inputs (gitignored; see data/raw/README.md)
├── src/
│   ├── paths.py
│   ├── climate/
│   │   ├── scripts/                 ← all climate analysis scripts
│   │   └── plotting/                ← Cartopy helpers (bob_map.py)
│   └── ml/                          ← onset forecasting (see src/ml/README.md)
│       ├── preprocessing/           ← 01_build_dataset.py
│       ├── training/                ← 02–03
│       ├── evaluation/              ← 04–05
│       ├── experiments/             ← 06_predict_current.py
│       ├── datasets/                ← processed features + splits
│       ├── models/                  ← trained binaries (gitignored)
│       └── outputs/                 ← metrics, shap, forecasts
├── outputs/
│   ├── timeseries/                  ← regional SST/wind CSVs + combined NetCDF
│   ├── mhw/
│   │   ├── catalogue/               ← 117 Hobday events (N49 / C40 / S28)
│   │   ├── climatology/             ← DOY climatology + Threshold90
│   │   ├── annual_statistics/
│   │   ├── event_reports/
│   │   ├── top_events/
│   │   └── figures/
│   ├── enso/{lag,frequency,statistics,annual,seasonal,strength,analysis}/
│   ├── iod/{lag,frequency,statistics,annual,seasonal,strength,analysis}/
│   ├── mei/{lag,frequency,statistics,annual,seasonal,strength}/
│   ├── drivers/{wind,heat_flux,heat_flux_analysis}/
│   ├── climate_indices/             ← ONI / DMI / MEI characterization
│   ├── climate_comparison/          ← ENSO vs IOD vs MEI
│   ├── master_event_catalogue/      ← per-event master tables (117 events)
│   ├── top_event_sst_maps/          ← top-10 strongest/longest lifecycle maps
│   ├── publication/
│   ├── spatial_analysis/
│   ├── maps/
│   └── yearly/                      ← per-year SST maps (2016–2026)
└── archive/                         ← legacy root scripts + path rewriter
```

---

### 8. Execution Commands

#### Prerequisites (MHW catalogue — run once)

```bash
cd /path/to/MRC
.venv/bin/python src/climate/scripts/merge_sst.py
.venv/bin/python src/climate/scripts/extract_regional_sst.py
.venv/bin/python src/climate/scripts/build_hobday_climatology.py
.venv/bin/python src/climate/scripts/detect_mhw.py
.venv/bin/python src/climate/scripts/generate_mhw_reports.py
```

#### ENSO Pipeline (completed)

```bash
cd /path/to/MRC
.venv/bin/python src/climate/scripts/enso_lag_analysis.py
.venv/bin/python src/climate/scripts/enso_frequency_analysis.py
.venv/bin/python src/climate/scripts/enso_statistics.py
.venv/bin/python src/climate/scripts/enso_annual_analysis.py
.venv/bin/python src/climate/scripts/enso_seasonal_analysis.py
.venv/bin/python src/climate/scripts/enso_strength_analysis.py
.venv/bin/python src/climate/scripts/enso_mhw_analysis.py
```

#### IOD Pipeline (completed)

```bash
cd /path/to/MRC
.venv/bin/python src/climate/scripts/iod_analysis.py          # runs all 6 stages
## OR individually:
.venv/bin/python src/climate/scripts/iod_lag_analysis.py
.venv/bin/python src/climate/scripts/iod_frequency_analysis.py
.venv/bin/python src/climate/scripts/iod_statistics.py
.venv/bin/python src/climate/scripts/iod_annual_analysis.py
.venv/bin/python src/climate/scripts/iod_seasonal_analysis.py
.venv/bin/python src/climate/scripts/iod_strength_analysis.py
```

#### MEI Pipeline (completed)

```bash
cd /path/to/MRC
.venv/bin/python src/climate/scripts/mei_pipeline.py          # runs all 6 stages
## OR individually:
.venv/bin/python src/climate/scripts/mei_lag_analysis.py
.venv/bin/python src/climate/scripts/mei_frequency_analysis.py
.venv/bin/python src/climate/scripts/mei_statistics.py
.venv/bin/python src/climate/scripts/mei_annual_analysis.py
.venv/bin/python src/climate/scripts/mei_seasonal_analysis.py
.venv/bin/python src/climate/scripts/mei_strength_analysis.py
```

#### Climate Comparison (completed)

```bash
cd /path/to/MRC
.venv/bin/python src/climate/scripts/climate_driver_comparison.py
```

#### Wind & Heat Flux (completed)

```bash
cd /path/to/MRC
.venv/bin/python src/climate/scripts/extract_regional_wind.py
.venv/bin/python src/climate/scripts/wind_mhw_analysis.py
.venv/bin/python src/climate/scripts/wind_climatology_analysis.py
.venv/bin/python src/climate/scripts/extract_heat_flux.py
.venv/bin/python src/climate/scripts/heat_flux_mhw_analysis.py
```

#### View Summary Results

```bash
cat outputs/mei/lag/summary.csv
cat outputs/mei/frequency/summary.csv
cat outputs/iod/lag/summary.csv
cat outputs/iod/frequency/summary.csv
cat outputs/enso/lag/summary.csv
cat outputs/enso/frequency/summary.csv
cat outputs/mhw_summary.txt
cat results_text
```

---

#### Phase 11: Machine Learning Forecasting ✅ (COMPLETED 2026-07-13)

MHW onset prediction lives in `src/ml/` (separate from the climate pipeline).

| Deliverable | Script | Output |
|-------------|--------|--------|
| Full ML pipeline | `src/ml/run_pipeline.py` | `src/ml/datasets/`, `models/`, `outputs/` |

**Docs:** this README (Part C) · [`src/ml/README.md`](src/ml/README.md) · [`src/ml/ML_EXECUTION.md`](src/ml/ML_EXECUTION.md)

**Task:** Predict new MHW onset within 3/7/14 days per region  
**Models:** XGBoost, Random Forest, Gradient Boosting + baselines  
**Test period:** 2022–2025 (chronological split)

**Key outputs:**
- `src/ml/datasets/processed/combined_daily_features.csv`
- `src/ml/outputs/metrics/all_models_comparison.csv`
- `src/ml/outputs/forecasts/latest_forecast.csv`
- `src/ml/outputs/shap/` feature importance plots

```bash
cd /path/to/MRC
.venv/bin/python src/ml/run_pipeline.py
.venv/bin/python src/ml/experiments/06_predict_current.py
```
---

### 10. Statistical Methods Reference

All climate-driver analyses use identical methods for direct comparability:

| Method | Application |
|--------|-------------|
| Pearson correlation | Lag analysis, annual variability |
| Chi-square goodness-of-fit | Phase frequency (equal expected distribution) |
| Cramer's V | Effect size for frequency tests |
| Kruskal–Wallis | Non-parametric comparison across 3 phases |
| Mann–Whitney U | Pairwise phase comparisons |
| Chi-square independence | Season × phase contingency tables |
| Linear regression | Scatter plot trend lines |
| Hobday et al. (2016) | MHW detection definition |

**Figure standards:** 600 dpi PNG + PDF, consistent fonts/colors/legends across all analyses.


---

### 11. Dependencies

Python 3.10.12 (`.venv/`). Inferred packages:

```
xarray, netCDF4, pandas, numpy, matplotlib, cartopy, scipy, scikit-learn, tqdm
```

---

*This document should be updated after every major analysis phase is completed.*

---

# Part B — Complete Results

**Author:** Samyak Kumar  
**Institution:** Maritime Research Center (MRC)  
**Study Period:** 2006–2025  
**Generated:** 2026-07-23  
**Regions:** North BoB (15–22°N), Central BoB (10–15°N), South BoB (5–10°N)

> Single master reference for all numerical results from project start to present.  
> For methodology and pipeline details see this README (Project Reference section). For ML details see `src/ml/README.md` and this README (Machine Learning Module section).

---

### 1. Headline Finding

**Approximately 78–84% of Bay of Bengal Marine Heatwave events (2006–2025) occurred during anomalously weak surface wind conditions.**

| Region | MHW Events | Weak-Wind Events | % Weak Wind |
|--------|-----------|------------------|-------------|
| North | 49 | 41 | **83.7%** |
| Central | 40 | 31 | **77.5%** |
| South | 28 | 23 | **82.1%** |
| **All BoB** | **117** | **95** | **81.2%** |

**Conclusion:** Local wind suppression is the dominant immediate driver of MHWs. Large-scale climate indices (especially IOD) provide additional context.

---

### 2. MHW Detection Summary (Hobday et al. 2016)

**Method:** 90th-percentile seasonal threshold, ≥5 consecutive days above threshold.

#### 2.1 Regional Event Counts

| Region | Total Events | Mean Duration (days) | Max Duration (days) | Mean Max Intensity (°C) | Max Intensity (°C) | Mean Max SST (°C) |
|--------|-------------|---------------------|----------------------|------------------------|-------------------|-------------------|
| North | 49 | 13.0 | 61 | 0.317 | 0.912 | 29.56 |
| Central | 40 | 14.5 | 53 | 0.300 | 0.907 | 29.95 |
| South | 28 | 20.5 | 81 | 0.315 | 0.943 | 30.14 |
| **Total** | **117** | **15.3** | **81** | **0.310** | **0.943** | **29.85** |

#### 2.2 Record Events

| Record | Region | Event ID | Start Date | Value |
|--------|--------|----------|------------|-------|
| **Longest MHW** | South | S25 | 2024-06-14 | **81 days** (ends 2024-09-02) |
| **2nd Longest** | South | S27 | 2024-10-29 | **79 days** (ends 2025-01-16) |
| **3rd Longest** | North | N43 | 2025-01-22 | **61 days** (ends 2025-03-23) |
| **Strongest MHW** | South | S24 | 2024-04-14 | **0.943°C** max intensity |
| **2nd Strongest** | North | N36 | 2024-04-07 | **0.912°C** |
| **3rd Strongest** | Central | C31 | 2024-04-11 | **0.908°C** |

#### 2.3 Overall Statistics

| Metric | Value |
|--------|-------|
| Total MHW events (all regions) | 117 |
| Total MHW event-days | 1,795 |
| Study period | 20 years (2006–2025) |
| Daily records per region | 7,300 |
| Combined regional-day records | 21,900 |

---

### 3. Annual MHW Statistics by Region

#### 3.1 North BoB (49 events)

| Year | Events | Mean Duration | Max Duration | Mean Intensity | Max Intensity |
|------|--------|---------------|--------------|----------------|---------------|
| 2006 | 1 | 6 | 6 | 0.070 | 0.142 |
| 2008 | 1 | 6 | 6 | 0.024 | 0.056 |
| 2009 | 1 | 7 | 7 | 0.086 | 0.162 |
| 2010 | 1 | 7 | 7 | 0.054 | 0.117 |
| 2014 | 1 | 9 | 9 | 0.271 | 0.459 |
| 2016 | 3 | 14.3 | 23 | 0.141 | 0.401 |
| 2017 | 1 | 7 | 7 | 0.147 | 0.206 |
| 2018 | 1 | 9 | 9 | 0.261 | 0.435 |
| 2019 | 2 | 10.5 | 15 | 0.197 | 0.621 |
| 2020 | 5 | 13.2 | 21 | 0.213 | 0.659 |
| 2021 | 7 | 11.9 | 23 | 0.133 | 0.477 |
| 2022 | 3 | 11.0 | 14 | 0.340 | 0.792 |
| 2023 | 8 | 12.5 | 31 | 0.154 | 0.487 |
| 2024 | 6 | 17.3 | 49 | 0.181 | 0.912 |
| 2025 | 8 | 17.3 | 61 | 0.173 | 0.484 |

#### 3.2 Central BoB (40 events)

| Year | Events | Mean Duration | Max Duration | Mean Intensity | Max Intensity |
|------|--------|---------------|--------------|----------------|---------------|
| 2010 | 4 | 13.8 | 25 | 0.175 | 0.457 |
| 2015 | 1 | 5 | 5 | 0.016 | 0.037 |
| 2016 | 3 | 10.3 | 15 | 0.145 | 0.388 |
| 2017 | 1 | 6 | 6 | 0.115 | 0.239 |
| 2019 | 1 | 35 | 35 | 0.229 | 0.534 |
| 2020 | 4 | 14.5 | 24 | 0.201 | 0.842 |
| 2021 | 4 | 7.3 | 9 | 0.156 | 0.534 |
| 2022 | 6 | 9.2 | 14 | 0.143 | 0.434 |
| 2023 | 4 | 14.0 | 26 | 0.092 | 0.344 |
| 2024 | 8 | 22.9 | 53 | 0.192 | 0.908 |
| 2025 | 4 | 17.0 | 34 | 0.140 | 0.336 |

#### 3.3 South BoB (28 events)

| Year | Events | Mean Duration | Max Duration | Mean Intensity | Max Intensity |
|------|--------|---------------|--------------|----------------|---------------|
| 2010 | 5 | 7.2 | 11 | 0.096 | 0.292 |
| 2015 | 4 | 19.0 | 39 | 0.092 | 0.343 |
| 2016 | 2 | 23.5 | 32 | 0.191 | 0.441 |
| 2017 | 1 | 5 | 5 | 0.039 | 0.069 |
| 2019 | 4 | 10.5 | 16 | 0.161 | 0.361 |
| 2020 | 2 | 22.0 | 32 | 0.257 | 0.596 |
| 2021 | 1 | 9 | 9 | 0.156 | 0.448 |
| 2023 | 2 | 16.5 | 24 | 0.126 | 0.358 |
| 2024 | 6 | 46.2 | 81 | 0.240 | 0.943 |
| 2025 | 1 | 6 | 6 | 0.088 | 0.154 |

**Notable:** 2024 was the most active year — South had 6 events including the longest (81 d) and strongest (0.943°C) in the dataset.

---

### 4. Top 10 Events

#### 4.1 Top 10 Longest — South

| Rank | Start | End | Duration (d) | Max Intensity (°C) |
|------|-------|-----|-------------|-------------------|
| 1 | 2024-06-14 | 2024-09-02 | 81 | 0.463 |
| 2 | 2024-10-29 | 2025-01-16 | 79 | 0.620 |
| 3 | 2024-01-25 | 2024-03-08 | 44 | 0.342 |
| 4 | 2024-04-14 | 2024-05-24 | 41 | 0.943 |
| 5 | 2015-12-08 | 2016-01-15 | 39 | 0.231 |
| 6 | 2020-08-17 | 2020-09-17 | 32 | 0.596 |
| 7 | 2016-04-21 | 2016-05-22 | 32 | 0.441 |
| 8 | 2023-11-03 | 2023-11-26 | 24 | 0.358 |
| 9 | 2015-10-11 | 2015-11-02 | 23 | 0.343 |
| 10 | 2024-09-26 | 2024-10-12 | 17 | 0.268 |

#### 4.2 Top 10 Strongest — North

| Rank | Start | End | Duration (d) | Max Intensity (°C) |
|------|-------|-----|-------------|-------------------|
| 1 | 2024-04-07 | 2024-05-25 | 49 | 0.912 |
| 2 | 2022-07-27 | 2022-08-08 | 13 | 0.792 |
| 3 | 2022-08-29 | 2022-09-11 | 14 | 0.716 |
| 4 | 2020-09-03 | 2020-09-23 | 21 | 0.659 |
| 5 | 2019-10-17 | 2019-10-31 | 15 | 0.621 |
| 6 | 2024-10-07 | 2024-10-22 | 16 | 0.584 |
| 7 | 2020-07-25 | 2020-08-13 | 20 | 0.503 |
| 8 | 2023-04-11 | 2023-05-11 | 31 | 0.487 |
| 9 | 2025-01-22 | 2025-03-23 | 61 | 0.484 |
| 10 | 2021-05-08 | 2021-05-23 | 16 | 0.477 |

*(Full top-10 lists for all regions: `outputs/mhw/top_events/`)*

---

### 5. Wind Analysis Results

#### 5.1 Weak vs Strong Wind During MHWs

| Region | Weak Wind | Strong Wind | % Weak |
|--------|-----------|-------------|--------|
| North | 41 / 49 | 8 / 49 | 83.7% |
| Central | 31 / 40 | 9 / 40 | 77.5% |
| South | 23 / 28 | 5 / 28 | 82.1% |

**Classification:** Weak = wind during event below regional climatological mean for that period.

#### 5.2 Wind Anomaly (from Master Catalogue)

| Region | Mean Wind Anomaly During MHW (m/s) | % Events with Weak Wind Flag |
|--------|-----------------------------------|------------------------------|
| North | −0.27 (typical) | 83.7% |
| Central | −0.48 (typical) | 77.5% |
| South | −0.66 (typical) | 82.1% |

---

### 6. Heat Flux Analysis Results

#### 6.1 Reduced Latent Heat Loss During MHWs

| Region | Events with Reduced SLHF | % of Events |
|--------|-------------------------|-------------|
| North | 17 / 49 | 34.7% |
| Central | 22 / 40 | 55.0% |
| South | 16 / 28 | 57.1% |
| **All** | **55 / 117** | **47.0%** |

**Interpretation:** Reduced latent heat loss (positive SLHF anomaly = less cooling) occurs in roughly half of events, especially in Central and South BoB.

---

### 7. Climate Index Characterization (2006–2025)

#### 7.1 ENSO (ONI) — Full Study Period

| Phase | Months (count) |
|-------|----------------|
| Neutral | 104 |
| La Niña | 77 |
| El Niño | 59 |

#### 7.2 IOD (DMI) — Full Study Period

| Phase | Months (count) |
|-------|----------------|
| Neutral | 185 |
| Positive | 38 |
| Negative | 9 |

**DMI statistics:** Min = −0.758, Max = +0.964, Mean = +0.097, Std = 0.310

#### 7.3 MHW Events by Climate Phase (All 117 Events)

| Index | Phase | Event Count | % of 117 |
|-------|-------|-------------|----------|
| **ENSO** | Neutral | 54 | 46.2% |
| | El Niño | 38 | 32.5% |
| | La Niña | 25 | 21.4% |
| **IOD** | Neutral | 74 | 63.2% |
| | Positive | 33 | 28.2% |
| | Negative | 2 | 1.7% |
| | Unknown | 8 | 6.8% |
| **MEI** | La Niña | 59 | 50.4% |
| | El Niño | 29 | 24.8% |
| | Neutral | 29 | 24.8% |

#### 7.4 Regional Climate Phase Distribution During MHWs

**North (49 events):**
- ENSO: Neutral 24, El Niño 13, La Niña 12
- IOD: Neutral 30, Positive 13, Negative 1, Unknown 5
- MEI: La Niña 28, Neutral 13, El Niño 8

**Central (40 events):**
- ENSO: Neutral 20, El Niño 10, La Niña 10
- IOD: Neutral 27, Positive 10, Negative 1, Unknown 2
- MEI: La Niña 24, El Niño 8, Neutral 8

**South (28 events):**
- ENSO: El Niño 15, Neutral 10, La Niña 3
- IOD: Neutral 17, Positive 10, Unknown 1
- MEI: El Niño 13, Neutral 8, La Niña 7

---

### 8. ENSO (ONI) Analysis Results

#### 8.1 Phase Frequency Test (Chi-Square: are MHWs evenly distributed across ENSO phases?)

| Region | Events | El Niño | Neutral | La Niña | χ² p-value | Cramer's V | Significant? |
|--------|--------|---------|---------|---------|------------|------------|--------------|
| North | 49 | 13 | 24 | 12 | 0.066 | 0.235 | No (marginal) |
| Central | 40 | 10 | 20 | 10 | 0.082 | 0.250 | No |
| South | 28 | 15 | 10 | 3 | **0.020** | 0.373 | **Yes** |

#### 8.2 Lag Correlation (ONI vs MHW properties)

| Region | Best Lag (months) | Duration r | p-value | Significant? |
|--------|-------------------|-----------|---------|--------------|
| North | 6 | 0.135 | 0.354 | No |
| Central | 6 | 0.290 | 0.070 | Marginal |
| South | 6 | **0.433** | **0.021** | **Yes** |

**Finding:** ENSO shows significant influence on South BoB MHWs at 6-month lag (r = 0.433, p = 0.021). South MHWs are enriched during El Niño (54% of events).

---

### 9. IOD (DMI) Analysis Results

#### 9.1 Phase Frequency Test

| Region | Events | Positive | Neutral | Negative | χ² p-value | Cramer's V | Significant? |
|--------|--------|----------|---------|----------|------------|------------|--------------|
| North | 44* | 13 | 30 | 1 | **<0.001** | 0.574 | **Yes** |
| Central | 38* | 10 | 27 | 1 | **<0.001** | 0.602 | **Yes** |
| South | 27* | 10 | 17 | 0 | **0.0003** | 0.548 | **Yes** |

*Some events have Unknown IOD phase (DMI data ends April 2025).

#### 9.2 Lag Correlation (DMI vs MHW properties)

| Region | Best Lag (months) | Duration r | p-value | Intensity r | p-value |
|--------|-------------------|-----------|---------|------------|---------|
| North | 3 | 0.083 | 0.589 | −0.052 | 0.735 |
| Central | 6 | **0.344** | **0.030** | −0.099 | 0.553 |
| South | 6 | **0.459** | **0.014** | **0.470** | **0.012** |

**Finding:** IOD is the strongest large-scale climate driver. Significant lag correlations in Central and South at 6 months.

#### 9.3 Kruskal-Wallis (Duration/Intensity across IOD phases)

| Region | Duration p | Intensity p | Significant? |
|--------|-----------|-------------|--------------|
| North | 0.250 | 0.307 | No |
| Central | 0.128 | 0.539 | No |
| South | 0.351 | 0.482 | No |

---

### 10. MEI v2 Analysis Results

#### 10.1 Phase Frequency Test

| Region | Events | El Niño | Neutral | La Niña | χ² p-value | Cramer's V | Significant? |
|--------|--------|---------|---------|---------|------------|------------|--------------|
| North | 49 | 8 | 13 | 28 | **0.001** | 0.368 | **Yes** |
| Central | 40 | 8 | 8 | 24 | **0.002** | 0.400 | **Yes** |
| South | 28 | 13 | 8 | 7 | 0.331 | 0.199 | No |

**Finding:** North and Central show significant **La Niña enrichment** (opposite to South's El Niño pattern).

#### 10.2 Lag Correlation (MEI vs MHW properties)

| Region | Best Lag (months) | Duration r | p-value |
|--------|-------------------|-----------|---------|
| North | 3 | 0.037 | 0.804 |
| Central | 0 | 0.228 | 0.157 |
| South | 6 | 0.292 | 0.131 |

#### 10.3 Seasonal Dependence (Chi-Square)

| Region | Season × MEI p-value | Significant? |
|--------|---------------------|--------------|
| North | 0.302 | No |
| Central | **0.0008** | **Yes** |
| South | 0.212 | No |

#### 10.4 Kruskal-Wallis (Duration/Intensity across MEI phases)

| Region | Duration p | Intensity p |
|--------|-----------|-------------|
| North | 0.801 | 0.267 |
| Central | 0.399 | 0.653 |
| South | 0.999 | 0.796 |

---

### 11. Comparative Climate Driver Assessment

#### 11.1 Driver Rankings (Composite Score — higher = stronger influence)

| Region | #1 Driver | Score | #2 Driver | Score | #3 Driver | Score |
|--------|-----------|-------|-----------|-------|-----------|-------|
| **North** | **IOD** | 58.9 | MEI | 50.3 | ENSO | 47.8 |
| **Central** | **IOD** | 87.0 | MEI | 78.5 | ENSO | 57.1 |
| **South** | **IOD** | 99.4 | ENSO | 85.4 | MEI | 47.8 |

#### 11.2 Full Comparison Table

| Region | Driver | Freq p | Cramer's V | Lag r (dur) | Lag p | Annual r | Seasonal p | Sig. Tests | Rank |
|--------|--------|--------|------------|-------------|-------|----------|------------|------------|------|
| North | IOD | <0.001 | 0.574 | 0.083 | 0.589 | 0.207 | 0.583 | 1 | 1 |
| North | MEI | 0.001 | 0.368 | 0.037 | 0.804 | −0.159 | 0.302 | 1 | 2 |
| North | ENSO | 0.066 | 0.235 | 0.135 | 0.354 | 0.118 | 0.725 | 0 | 3 |
| Central | IOD | <0.001 | 0.602 | 0.344 | **0.030** | −0.334 | 0.481 | 2 | 1 |
| Central | MEI | 0.002 | 0.400 | 0.228 | 0.157 | −0.500 | **0.001** | 2 | 2 |
| Central | ENSO | 0.082 | 0.250 | 0.290 | 0.070 | −0.379 | 0.085 | 0 | 3 |
| South | IOD | **0.0003** | 0.548 | 0.459 | **0.014** | 0.093 | 0.649 | 3 | 1 |
| South | ENSO | **0.020** | 0.373 | 0.433 | **0.021** | 0.347 | 0.225 | 2 | 2 |
| South | MEI | 0.331 | 0.199 | 0.292 | 0.131 | 0.334 | 0.212 | 0 | 3 |

#### 11.3 Key Comparative Findings

| Aspect | ENSO | IOD | MEI | Strongest? |
|--------|------|-----|-----|------------|
| Phase frequency (North) | p=0.066 NS | **p<0.001 SIG** | **p=0.001 SIG** | IOD / MEI |
| Phase frequency (Central) | p=0.082 NS | **p<0.001 SIG** | **p=0.002 SIG** | IOD / MEI |
| Phase frequency (South) | **p=0.020 SIG** | **p=0.0003 SIG** | p=0.331 NS | IOD |
| Best lag r (South, 6mo) | 0.433 (p=0.021) | **0.459 (p=0.014)** | 0.292 (p=0.131) | IOD |
| Dominant MHW phase (South) | 54% El Niño | 63% Neutral | 46% El Niño | Different |
| Dominant MHW phase (North) | 49% Neutral | 68% Neutral | **57% La Niña** | MEI unique |
| Local wind driver | — | — | — | **Wind (78–84%)** |

---

### 12. Master Event Catalogue Summary

**File:** `outputs/master_event_catalogue/csv/all_regions_master_event_catalogue.csv`  
**Events:** 117 | **Parameters per event:** 57

#### 12.1 Regional Summary

| Region | Events | Mean Duration | Mean Max Intensity | Mean Max SST | % Weak Wind | % El Niño | % Positive IOD | % Reduced SLHF |
|--------|--------|---------------|-------------------|--------------|-------------|-----------|----------------|----------------|
| North | 49 | 13.0 d | 0.32°C | 29.56°C | 83.7% | 26.5% | 26.5% | 34.7% |
| Central | 40 | 14.5 d | 0.30°C | 29.95°C | 77.5% | 25.0% | 25.0% | 55.0% |
| South | 28 | 20.5 d | 0.31°C | 30.14°C | 82.1% | 53.6% | 35.7% | 57.1% |

#### 12.2 Parameters Recorded Per Event

Event metadata, SST (mean/max/min, threshold, intensity), ONI/DMI/MEI at 0/1/2/3/6-month lags, wind (30/21/14/7-day before + during, anomaly, classification), heat flux (SLHF/SSHF climatology, during, anomaly), and derived flags.

---

### 13. Top-Event SST Lifecycle Maps

**Module:** `outputs/top_event_sst_maps/`  
**Events processed:** 60 (top 10 strongest + top 10 longest × 3 regions)  
**Maps generated:** 3,329 PNG files  
**Per event:** 5 days before + 5 during + 5 after (daily SST + anomaly maps, composites, triptych, difference maps)

---

### 14. Machine Learning Forecasting Results

**Module:** `src/ml/` (`src/ml/`) | **Test period:** 2022–2025

> **Important distinction:** Hobday detection counts how many MHWs **occurred**. The ML module predicts whether a **new** MHW will **start within the next 3/7/14 days** from a given date. A low probability on 2025-12-31 does **not** mean “0 events in 2025.”

#### 14.1 Dataset

| Metric | Value |
|--------|-------|
| Daily records (all regions) | 21,900 |
| Train years | 2006–2018 (14,235 rows) |
| Validation years | 2019–2021 (3,285 rows) |
| Test years | 2022–2025 (4,380 rows) |
| Positive class rate (onset_3d) | 1.59% |
| Positive class rate (onset_7d) | 3.72% |
| Positive class rate (onset_14d) | 7.40% |

#### 14.2 Best Models on Test Set (by F1 score)

| Region | Horizon | Best Model | F1 | Recall | Precision | ROC-AUC | PR-AUC |
|--------|---------|------------|-----|--------|-----------|---------|--------|
| North | 3-day | Random Forest | 0.164 | 0.169 | 0.160 | 0.810 | 0.161 |
| North | 7-day | Logistic Regression | 0.253 | 0.790 | 0.151 | 0.644 | 0.155 |
| North | 14-day | Logistic Regression | **0.389** | 0.813 | 0.256 | 0.612 | 0.292 |
| Central | 3-day | Logistic Regression | 0.235 | 0.692 | 0.142 | 0.840 | 0.187 |
| Central | 7-day | Logistic Regression | 0.305 | 0.837 | 0.187 | 0.728 | 0.189 |
| Central | 14-day | Logistic Regression | **0.399** | 0.767 | 0.269 | 0.606 | 0.242 |
| South | 3-day | XGBoost | 0.138 | 0.074 | 1.000 | 0.804 | 0.161 |
| South | 7-day | Gradient Boosting | 0.183 | 0.190 | 0.176 | 0.781 | 0.129 |
| South | 14-day | Logistic Regression | 0.228 | 0.865 | 0.131 | 0.669 | 0.124 |

Operational forecasts now load these **best-by-F1** models (not always XGBoost).

#### 14.3 Top ML Features (North, XGBoost — SHAP/Importance)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | Distance_to_Threshold | 0.091 |
| 2 | Intensity | 0.090 |
| 3 | Intensity_mean_7d | 0.045 |
| 4 | DMI_1m | 0.035 |
| 5 | ONI_0m | 0.034 |
| 6 | SST_Anomaly | 0.032 |
| 7 | DOY_sin (seasonality) | 0.028 |
| 8 | Intensity_mean_14d | 0.025 |
| 9 | MEI_6m | 0.025 |
| 10 | MEI_1m | 0.024 |

**Interpretation:** ML models correctly prioritize SST state (intensity, distance to threshold) and climate indices (DMI, ONI, MEI) — consistent with physical analysis.

#### 14.4 Catalogue vs Forecast Clarification (2025)

| Source | Question answered | 2025 result |
|--------|-------------------|-------------|
| Hobday catalogue | How many MHWs **started** in 2025? | **13** (North 8, Central 4, South 1) |
| ML latest forecast | Will a new MHW start in the next 3/7/14 days **from 2025-12-31**? | Single-day onset risk (see §14.5) |

Last 2025 event end dates: North **2025-11-03**, Central **2025-08-13**, South **2025-10-18**. By 2025-12-31, SST is below threshold (e.g. North Intensity = −1.16 °C), so low near-term onset risk is expected.

#### 14.5 Latest Operational Forecast (2025-12-31, best models)

Script: `src/ml/experiments/06_predict_current.py`  
Output: `src/ml/outputs/forecasts/latest_forecast.csv`

| Region | Horizon | P(MHW Onset) | Alert | SST (°C) | Intensity (°C) | Wind (m/s) | Model |
|--------|---------|-------------|-------|----------|----------------|------------|-------|
| North | 3-day | 0.000 | LOW | 26.01 | −1.16 | 2.77 | Random Forest |
| North | 7-day | 0.007 | LOW | 26.01 | −1.16 | 2.77 | Logistic Regression |
| North | 14-day | 0.032 | LOW | 26.01 | −1.16 | 2.77 | Logistic Regression |
| Central | 3-day | 0.002 | LOW | 28.08 | −0.59 | 4.29 | Logistic Regression |
| Central | 7-day | 0.208 | LOW | 28.08 | −0.59 | 4.29 | Logistic Regression |
| Central | 14-day | 0.321 | MODERATE | 28.08 | −0.59 | 4.29 | Logistic Regression |
| South | 3-day | 0.001 | LOW | 28.94 | −0.10 | 3.64 | XGBoost |
| South | 7-day | 0.003 | LOW | 28.94 | −0.10 | 3.64 | Gradient Boosting |
| South | 14-day | 0.683 | HIGH | 28.94 | −0.10 | 3.64 | Logistic Regression |

**Note:** South 14-day HIGH at year-end with Intensity still negative indicates **probability calibration** remains imperfect for some logistic models; treat alert levels cautiously until calibration is added.

#### 14.6 Year Verification — Best Models vs 2025 Catalogue Events

For each of the **13** catalogue starts in 2025, the best model was scored on the pre-onset window (days that should be labeled `onset_Hd = 1`). An alert hit = max P ≥ 0.25 in that window.

Output: `src/ml/outputs/forecasts/year_verification_2025.csv`

| Horizon | Events with alert hit | Hit rate |
|---------|----------------------|----------|
| 3-day | **11 / 13** | 84.6% |
| 7-day | **12 / 13** | 92.3% |
| 14-day | **13 / 13** | **100%** |

**Misses (P < 0.25 in pre-window):**
- 3-day: North 2025-01-22; South 2025-10-13  
- 7-day: South 2025-10-13 only  

**Conclusion:** The ML system does **not** contradict the 13 Hobday events in 2025. When evaluated on the days before those starts, best models recover nearly all events (all 13 at 14-day). The earlier “0 events” reading came from interpreting the **year-end single-day forecast** as an annual event count, and from always using XGBoost instead of best-by-F1 models.

---

### 15. Output Inventory

| Category | Location | Count |
|----------|----------|-------|
| MHW catalogues | `outputs/mhw/catalogue/` | 3 CSVs |
| Climate index analyses | `outputs/enso_*/, iod_*/, mei_*/` | 100+ files each |
| Climate comparison | `outputs/climate_comparison/` | 7 CSVs + 118 figures |
| Master event catalogue | `outputs/master_event_catalogue/` | 18 CSVs + 94 figures |
| Top-event SST maps | `outputs/top_event_sst_maps/` | 3,329+ PNGs |
| Wind analysis | `outputs/drivers/wind/` | 117 event plots + 6 CSVs |
| Heat flux analysis | `outputs/drivers/heat_flux_analysis/` | 3 CSVs |
| Annual statistics | `outputs/mhw/annual_statistics/` | 3 CSVs |
| Top events | `outputs/mhw/top_events/` | 6 CSVs |
| ML models & results | `src/ml/` | models + metrics + forecasts (+ `src/ml/` wrappers) |

---

### 16. Known Data Limitations

| Issue | Impact |
|-------|--------|
| DMI data ends April 2025 | 8 events with Unknown IOD phase |
| SST box (85–95°E) vs wind box (80–100°E) differ | Minor spatial inconsistency |
| Heat flux is weekly, forward-filled to daily | Less temporal precision than SST/wind |
| South has 0 Negative IOD MHW events | IOD negative phase tests skipped |
| ML rare-event challenge | Onset days are 1.6–7.4% of all days |
| ML forecast date = last feature day (2025-12-31) | Not a live “today” forecast until data are refreshed |
| Some logistic probabilities poorly calibrated | e.g. South 14-day HIGH at year-end despite cool SST |

---

### 17. Key Conclusions

1. **117 MHW events** detected across North (49), Central (40), and South (28) BoB, 2006–2025.
2. **Wind is the dominant local driver** — 81% of events occur under weak wind conditions.
3. **IOD is the strongest large-scale climate driver** across all three regions (composite rank #1).
4. **ENSO matters most in South BoB** (54% El Niño enrichment, significant 6-month lag).
5. **MEI shows La Niña enrichment** in North and Central (opposite to ENSO South pattern).
6. **2024 was exceptional** — South recorded the longest (81 d) and strongest (0.943°C) events.
7. **2025 had 13 MHW starts** (North 8, Central 4, South 1); this is a catalogue result, separate from the ML year-end forecast.
8. **ML models achieve F1 up to 0.40** on 14-day onset prediction (test 2022–2025), with logistic regression often outperforming tree models on this small dataset.
9. **Best-model year verification (2025):** 11/13 (3-day), 12/13 (7-day), **13/13 (14-day)** events would have triggered a pre-onset alert (P ≥ 0.25).
10. **SST intensity and IOD** are the top ML predictors, consistent with physical understanding.

---



---

# Part C — Machine Learning Module

Full technical review (optional deep-dive): [`src/ml/README.md`](src/ml/README.md).

**Separated from the climate-analysis pipeline.** This module predicts whether a new Marine Heatwave will **start** within 3 / 7 / 14 days in North, Central, or South Bay of Bengal.

Full technical review: [`src/ml/README.md`](src/ml/README.md)

---

### Layout

```
src/ml/
├── datasets/              ← processed daily features + train/val/test splits
├── preprocessing/         ← 01_build_dataset.py (labels + rolling features)
├── feature_engineering/   ← feature design notes (logic lives in step 01)
├── training/              ← 02 baselines, 03 ML models
├── evaluation/            ← 04 metrics/plots, 05 SHAP/importance
├── experiments/           ← 06 operational forecast
├── models/                ← saved .joblib models
├── visualizations/        ← README pointing to outputs/figures & outputs/shap
├── config/model_config.yaml
├── outputs/{metrics,figures,shap,forecasts}/
├── common.py              ← shared utilities (paths resolved relative to repo root)
├── run_pipeline.py
└── ML_EXECUTION.md        ← detailed execution notes
```

---

### How to Run

From repository root:

```bash
.venv/bin/python src/ml/run_pipeline.py
```

Step by step:

```bash
.venv/bin/python src/ml/preprocessing/01_build_dataset.py
.venv/bin/python src/ml/training/02_train_baselines.py
.venv/bin/python src/ml/training/03_train_models.py
.venv/bin/python src/ml/evaluation/04_evaluate_models.py
.venv/bin/python src/ml/evaluation/05_explain_models.py
.venv/bin/python src/ml/experiments/06_predict_current.py
```

**Prerequisite:** Climate pipeline products in `outputs/` (SST, climatology, MHW catalogues, wind, heat flux, climate index CSVs).

---

### Module location

All ML code is under `src/ml/`. Prefer this path for all new work.

---

### Task Summary

| Item | Value |
|------|-------|
| Task | Binary onset classification |
| Horizons | 3, 7, 14 days |
| Models | Logistic Regression, XGBoost, Random Forest, Gradient Boosting + baselines |
| Split | Train 2006–2018 · Val 2019–2021 · Test 2022–2025 |
| Best F1 (test) | ~0.39–0.40 at 14-day (see this README § Complete Results) |

Do **not** change Hobday labels or climate methodology from this module.

---

## Folder guides

| Path | Role |
|------|------|
| **[README.md](README.md)** (this file) | How to use + project reference + full results + ML |
| [src/README.md](src/README.md) | Source layout + future-work roadmap |
| [src/climate/scripts/README.md](src/climate/scripts/README.md) | Climate script index and pipeline order |
| [src/ml/README.md](src/ml/README.md) | ML technical guide |
| [data/raw/README.md](data/raw/README.md) | Where to put raw NetCDF inputs |
| [outputs/README.md](outputs/README.md) | Climate products index |
| [archive/README.md](archive/README.md) | Archived root scripts |
| [requirements.txt](requirements.txt) | Pinned dependencies |

Every subdirectory also has a local `README.md` with purpose, contents, and regenerate commands.


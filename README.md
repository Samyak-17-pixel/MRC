# Bay of Bengal Marine Heatwave Project

**Drivers, Predictability, and Fisheries Impact of Marine Heatwaves in the Bay of Bengal (2006–2025)**

| | |
|---|---|
| **Author** | Samyak Kumar |
| **Institution** | Maritime Research Center (MRC) |
| **Study period** | 2006–2025 (20 years, daily) |
| **Study region** | Bay of Bengal, divided into North / Central / South sub-regions |
| **Status** | Climate-driver analysis complete · ML forecasting v1 complete · Multivariate analysis and fisheries impact pending |

---

## What This Project Does

Marine Heatwaves (MHWs) are prolonged periods of anomalously warm sea surface temperature (SST). This project:

1. **Detects** all MHW events in the Bay of Bengal from 2006–2025 using the standard Hobday et al. (2016) definition — **117 events** found across three sub-regions.
2. **Attributes** those events to large-scale climate drivers (ENSO via ONI and MEI v2, Indian Ocean Dipole via DMI) and local drivers (surface wind, air–sea heat flux) using a consistent statistical framework.
3. **Forecasts** MHW onset 3/7/14 days ahead with machine learning models trained on the physical predictors identified in step 2.

**Headline findings:**

- **81% of MHW events occurred during anomalously weak surface winds** — local wind suppression is the dominant immediate driver.
- **The Indian Ocean Dipole (IOD) is the strongest large-scale climate driver** in all three sub-regions.
- **ENSO matters most in the South** (54% of South events during El Niño; significant 6-month lag correlation).
- **2024 was exceptional** — it produced both the longest event (81 days) and the strongest event (0.943 °C max intensity), both in the South.
- ML onset prediction reaches **F1 ≈ 0.40** at a 14-day horizon on unseen test years (2022–2025).

---

## Documentation Map

**Start here, then follow the links.**

| Document | Contents |
|----------|----------|
| [`documentation/PROJECT_COMPLETE_REVIEW.md`](documentation/PROJECT_COMPLETE_REVIEW.md) | The complete project review — every stage, from problem statement to future work |
| [`documentation/01_problem_statement.md`](documentation/01_problem_statement.md) | What MHWs are, why the Bay of Bengal, scientific questions, objectives |
| [`documentation/02_literature_review.md`](documentation/02_literature_review.md) | Prior research, the gap this project addresses, references |
| [`documentation/03_datasets.md`](documentation/03_datasets.md) | Every dataset: source, variables, resolution, units, preprocessing |
| [`documentation/04_methodology.md`](documentation/04_methodology.md) | Complete chronological workflow of the whole project |
| [`documentation/05_mhw_detection.md`](documentation/05_mhw_detection.md) | Hobday et al. (2016) detection: climatology, thresholds, parameters |
| [`documentation/06_enso_analysis.md`](documentation/06_enso_analysis.md) | Full ENSO (ONI) analysis: preprocessing, lags, phases, statistics |
| [`documentation/07_iod_analysis.md`](documentation/07_iod_analysis.md) | Full IOD (DMI) analysis: status, completed and remaining work |
| [`documentation/08_mei_analysis.md`](documentation/08_mei_analysis.md) | Full MEI v2 analysis: status, completed and remaining work |
| [`documentation/09_visualizations.md`](documentation/09_visualizations.md) | Every figure type: purpose, generating script, interpretation |
| [`documentation/10_results.md`](documentation/10_results.md) | All results: significant vs non-significant, conclusions, limitations |
| [`documentation/11_future_work.md`](documentation/11_future_work.md) | Roadmap: multivariate analysis, BSISO, fisheries impact, publications |
| [`documentation/12_machine_learning.md`](documentation/12_machine_learning.md) | Complete technical review of the ML forecasting module |
| [`documentation/MIGRATION_REPORT.md`](documentation/MIGRATION_REPORT.md) | What was moved during the ML reorganization and why |
| [`ALL_PROJECT_RESULTS.md`](ALL_PROJECT_RESULTS.md) | Master numerical results table (every number in one file) |
| [`PROJECT.md`](PROJECT.md) | Working phase tracker / lab notebook (updated after each phase) |

Every major folder also contains its own `README.md` (see Repository Layout below).

---

## Repository Layout

```
mrc_ws/
├── README.md                    ← you are here (entry point)
├── PROJECT.md                   ← working phase tracker
├── ALL_PROJECT_RESULTS.md       ← master numerical results
├── requirements.txt             ← pinned Python dependencies
├── documentation/               ← complete project documentation (Parts 1–12)
├── datasets/                    ← raw input data (NetCDF; not in Git — see datasets/README.md)
├── scripts/                     ← all climate-analysis scripts (the scientific pipeline)
├── plotting/                    ← reusable Bay of Bengal Cartopy base map utilities
├── results/                     ← all analysis outputs (CSV tables tracked; figures regenerable)
│   ├── mhw_catalogue/           ← the central MHW event database (117 events)
│   ├── climatology/             ← Hobday climatology + 90th-percentile thresholds
│   ├── climate_indices/         ← ONI / DMI / MEI characterization
│   ├── enso_*/  iod_*/  mei_*/  ← per-driver statistical analyses (6 stages each)
│   ├── climate_comparison/      ← ENSO vs IOD vs MEI ranking
│   ├── wind_analysis/           ← wind–MHW analysis (headline finding)
│   ├── heat_flux*/              ← air–sea heat flux analyses
│   ├── master_event_catalogue/  ← 117 events × 57 parameters master table
│   ├── top_event_sst_maps/      ← SST lifecycle maps for top events
│   └── publication/             ← publication-ready tables, figures, dashboards
└── machine_learning/            ← ML forecasting module (separate from climate analysis)
```

---

## Environment Setup

**Requirements:** Python 3.10 (tested with 3.10.12) on Linux. ~10 GB disk for raw data, ~5 GB for outputs.

```bash
# 1. Clone / enter the repository
cd mrc_ws

# 2. Create and activate a virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies (pinned versions)
pip install -r requirements.txt

# 4. Download raw datasets (not stored in Git — see datasets/README.md
#    for sources, variables, and download instructions)
```

**Note on Cartopy:** map figures need the Natural Earth 50m coastline. The scripts use a locally cached copy (`cartopy_data/`); on a fresh machine Cartopy downloads it automatically on first use (internet required once).

---

## Reproducing the Full Pipeline

Run order matters — later stages read outputs of earlier ones. All commands from the repository root with the virtualenv active. See [`documentation/04_methodology.md`](documentation/04_methodology.md) for details of each step, and `scripts/README.md` for per-script documentation.

```bash
# Stage 1 — Data preparation (run once)
python scripts/merge_sst.py                    # merge 4 SST NetCDFs → combined file
python scripts/extract_regional_sst.py         # regional daily SST time series
python scripts/build_hobday_climatology.py     # climatology + 90th-percentile threshold

# Stage 2 — MHW detection (creates the central event catalogue)
python scripts/detect_mhw.py
python scripts/generate_mhw_reports.py

# Stage 3 — Climate index characterization
python scripts/enso_analysis.py
python scripts/iod_analysis.py                 # also runs the full IOD pipeline
python scripts/mei_analysis.py

# Stage 4 — Driver pipelines (6 stages each; see scripts/README.md)
python scripts/enso_lag_analysis.py            # ... then frequency, statistics,
                                               # annual, seasonal, strength
python scripts/mei_pipeline.py                 # runs all 6 MEI stages

# Stage 5 — Local drivers
python scripts/extract_regional_wind.py
python scripts/wind_mhw_analysis.py
python scripts/wind_climatology_analysis.py
python scripts/extract_heat_flux.py
python scripts/heat_flux_mhw_analysis.py

# Stage 6 — Synthesis
python scripts/climate_driver_comparison.py    # ENSO vs IOD vs MEI ranking
python scripts/build_master_event_catalogue.py # 117 × 57 master table
python scripts/top_event_sst_lifecycle_maps.py # spatial lifecycle maps
python scripts/generate_publication_outputs.py # publication tables + figures

# Stage 7 — Machine learning (separate module)
python machine_learning/run_pipeline.py
```

---

## Scientific Integrity Notes

- MHW detection strictly follows **Hobday et al. (2016)**: 90th-percentile day-of-year threshold, ≥ 5 consecutive days.
- All three climate-driver pipelines (ENSO, IOD, MEI) use **identical statistical methods** so results are directly comparable.
- Statistical tests: chi-square (phase frequency), Cramer's V (effect size), Pearson correlation (lags), Kruskal–Wallis and Mann–Whitney U (phase comparisons).
- Known data limitations are documented, not hidden — see [`documentation/10_results.md`](documentation/10_results.md) §Limitations.

## How to Cite / Contact

Author: Samyak Kumar, Maritime Research Center (MRC).
If you use this work, cite the repository and the primary methodological reference:

> Hobday, A. J., et al. (2016). A hierarchical approach to defining marine heatwaves. *Progress in Oceanography*, 141, 227–238.

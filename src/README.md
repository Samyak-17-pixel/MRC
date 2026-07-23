# src/ — Project Source Code

All executable analysis and forecasting code for the Bay of Bengal Marine Heatwave (MHW) project (2006–2025).

## Purpose

`src/` holds:

1. **Climate analysis** — SST merge, Hobday MHW detection, ENSO/IOD/MEI pipelines, wind/heat-flux drivers, synthesis maps and publication figures (`src/climate/`).
2. **Machine learning** — onset-forecasting pipeline (features, train, evaluate, operational predict) (`src/ml/`).
3. **Shared path constants** — `paths.py` so scripts resolve `data/raw/`, `outputs/`, and package roots without hard-coding layout.

Scientific logic lives here; numerical products land under `outputs/` (climate) or `src/ml/outputs/` (ML metrics/forecasts). Raw NetCDFs stay in `data/raw/`.

## Contents

| Path | Role |
|------|------|
| `paths.py` | `REPO_ROOT`, `DATA_RAW`, `OUTPUTS`, `TIMESERIES`, `MHW_*`, `ENSO`/`IOD`/`MEI`, `DRIVERS`, etc. |
| `climate/` | Non-ML climate pipeline (scripts + Cartopy helpers) |
| `ml/` | MHW onset forecasting module |

## How to run (from repo root)

```bash
cd <repo-root>
.venv/bin/python src/climate/scripts/<script>.py
.venv/bin/python src/ml/run_pipeline.py
.venv/bin/python src/ml/experiments/06_predict_current.py
```

## Upstream / Downstream

| Direction | Location |
|-----------|----------|
| Upstream | `data/raw/` (Copernicus SST, wind, heat flux; ONI/DMI/MEI NetCDFs) |
| Downstream climate | `outputs/` (timeseries, mhw, enso/iod/mei, drivers, publication, …) |
| Downstream ML | `src/ml/datasets/`, `src/ml/models/`, `src/ml/outputs/` |

## Notes

- Prefer importing paths from `src/paths.py` (climate) or `src/ml/common.py` (ML) over absolute home-directory strings.
- Do not put large NetCDF products in Git; see `data/raw/README.md` and `outputs/README.md`.

---

## Future work

Ordered roadmap for remaining science, ML improvements, and publications. Items marked pending must **not** be invented as completed results.

---

## 1. Remaining ENSO Work

| Item | Notes |
|------|-------|
| Finish ENSO spatial composites | `src/climate/src/climate/scripts/enso_spatial_analysis.py` started; no figure outputs |
| Populate `outputs/enso/analysis/*_event_plots/` | Deferred per-event diagnostics |
| Complete or retire `src/climate/scripts/enso_final_pipeline.py` | Currently a scaffold |
| Optional publication ENSO figure runner | Referenced historically as `archive/root_scripts/enso_figures.py` class without full runner |

---

## 2. IOD

| Item | Notes |
|------|-------|
| Extend / update DMI through end of 2025 | Remove or reduce 8 Unknown phases |
| Document nearest-month fallback if used | Only if explicitly approved |
| Optional spatial IOD composites | Parallel to ENSO spatial |

---

## 3. MEI

| Item | Notes |
|------|-------|
| Optional dedicated MEI overview figure suite | Parity with `src/climate/scripts/enso_mhw_analysis.py` |
| Sensitivity: bimonthly vs monthly matching | Methods paper / supplement |
| Spatial MEI composites | Optional |

---

## 4. Atmospheric Variables (Expand Phase 11 Physical Mechanisms)

| Variable | Status |
|----------|--------|
| Surface wind | ✅ Done |
| Latent / sensible heat flux | ✅ Done |
| Shortwave / longwave radiation | ❌ Pending |
| Net surface heat flux | ❌ Pending |
| Sea level pressure | ❌ Pending |
| Precipitation / evaporation | ❌ Pending |

Analyses per new variable (match existing pattern): before/during/after composites; lead–lag with duration/intensity; anomaly maps at initiation; optional Mann–Kendall trends.

---

## 5. Oceanographic Variables

| Variable | Status |
|----------|--------|
| Mixed layer depth (MLD) | ❌ Pending |
| Ocean currents | ❌ Pending |
| Sea surface salinity | ❌ Pending |

---

## 6. Heat Flux (Beyond Current)

- Full event-based framework already partial — expand radiation terms and net flux.
- Prefer daily flux if/when available to reduce forward-fill dependence.

---

## 7. Wind (Beyond Current)

- Standardize wind extraction box to SST box **only if instructed** (currently documented mismatch).
- Spatial wind composites at onset.

---

## 8. Precipitation

- Download / extract CMEMS or other precipitation; event composites; link to buoyancy/mixing hypotheses.

---

## 9. BSISO

- Acquire BSISO index; match to MHW onset seasons; test intraseasonal preconditioning (especially monsoon).

---

## 10. Multivariate Statistical Analysis

Planned methods (from `README.md`):

- Correlation matrices (indices + environmental variables)
- Partial correlation
- Multiple linear regression / GAM
- PCA / EOF
- VIF for multicollinearity
- Feature importance ranking (statistical, distinct from ML SHAP)

Suggested output: `outputs/multivariate/` via a future `multivariate_analysis.py`.

---

## 11. Fisheries Impact Analysis

**Not started.** Title-level objective only.

Suggested future steps:

1. Identify catch/effort/landing datasets for BoB EEZs.
2. Align temporally with MHW event catalogue.
3. Test catch anomalies during/after MHWs controlling for season and effort.
4. Keep analysis in a dedicated folder (do not mix into climate scripts without documentation).

---

## 12. Machine Learning Improvements

See also `11_machine_learning.md` §Pending improvements.

1. Add BSISO, radiation, MLD features when extracted.
2. Probability calibration (Platt / isotonic) and per-horizon alert threshold tuning.
3. Combined-region model with region feature.
4. Sequence models (e.g., LSTM) if tabular models plateau.
5. Near-real-time data refresh for true current-day forecasts.
6. Multi-horizon alert ensemble / expanding-window CV.

*(2025 catalogue event-level verification is implemented in `src/ml/experiments/06_predict_current.py` — see `11_machine_learning.md` §16.)*

---

## 13. Journal Paper & Publications

| Deliverable | Status |
|-------------|--------|
| Publication tables/figures skeleton | ✅ `outputs/publication/` |
| Full methods + results manuscript | ❌ Pending |
| Supplementary data (catalogues) | Ready to package from `outputs/` |
| Open GitHub-ready repo documentation | 🔄 In progress (this `` effort) |

Suggested paper narrative:

1. Detection & regional climatology  
2. Local wind/heat-flux mechanisms  
3. IOD vs ENSO vs MEI ranking  
4. Predictability / ML onset skill  
5. (Later) Fisheries implications  

---

## 14. Suggested Execution Order

1. Multivariate analysis on existing master catalogue (no new downloads).  
2. Update DMI / resolve Unknown phases.  
3. Add radiation / net heat flux / MLD.  
4. BSISO.  
5. ML v2 with new features.  
6. Fisheries data integration.  
7. Manuscript submission package.


# Bay of Bengal Marine Heatwave Project — Complete Review

**Author:** Samyak Kumar · Maritime Research Center (MRC)  
**Study period:** 2006–2025  
**Document type:** Master review (Parts 1–12 consolidated entry point)  
**Companion files:** Modular docs `01_*.md`–`12_*.md` · [`ALL_PROJECT_RESULTS.md`](../ALL_PROJECT_RESULTS.md) · [`PROJECT.md`](../PROJECT.md)

> This file is the comprehensive narrative of the project from inception to the current stage. For deep dives, follow the modular links. **Scientific methodology and numbers are not altered here** — only documented.

---

## A. Problem Statement

Marine Heatwaves (MHWs) are prolonged periods when SST exceeds a seasonally varying 90th-percentile threshold for ≥5 days (Hobday et al., 2016). They threaten ecosystems and fisheries. The Bay of Bengal was chosen for societal importance, ENSO–IOD–monsoon complexity, and CMEMS data availability.

**Questions:** How many MHWs occurred? Which climate and local drivers matter? Can onset be forecast 3/7/14 days ahead? *(Fisheries impact: future.)*

**Objectives achieved:** Detection (117 events), ENSO/IOD/MEI pipelines, wind/heat-flux attribution, driver ranking, master catalogue, ML v1.  
**Pending:** Multivariate analysis, expanded ocean/atmosphere variables, BSISO, fisheries, journal manuscript.

→ Details: [`01_problem_statement.md`](01_problem_statement.md)

---

## B. Literature Motivation

Prior work established Hobday detection, ENSO (ONI), IOD (Saji et al., 1999 / DMI), MEI v2, and local heat-budget reasoning. Gaps addressed here: integrated BoB 2006–2025 catalogue; parallel ENSO/IOD/MEI statistics; local+remote synthesis; onset ML grounded in those results. Fisheries linkage is a stated goal but **not implemented**.

→ [`02_literature_review.md`](02_literature_review.md)

---

## C. Datasets

| Dataset | Role |
|---------|------|
| Copernicus daily SST | Detection core |
| Wind (u10/v10) | Local driver |
| SLHF / SSHF | Heat budget |
| ONI | ENSO |
| DMI | IOD |
| MEI v2 | Multivariate ENSO |

Known issues: DMI ends Apr 2025; SST vs wind longitude boxes differ; flux ~weekly.

→ [`03_datasets.md`](03_datasets.md)

---

## D. Complete Methodology (Chronology)

1. Download & inspect data  
2. Merge SST → regional means  
3. Hobday climatology + Threshold90  
4. Detect MHWs → catalogues  
5. Characterize ONI/DMI/MEI  
6. Six-stage ENSO analysis  
7. Six-stage IOD analysis  
8. Six-stage MEI analysis  
9. Wind & heat-flux event analysis  
10. Comparative driver ranking  
11. Master event catalogue (117×57)  
12. Lifecycle maps & publication figures  
13. ML onset forecasting (separate module)  

→ [`04_methodology.md`](04_methodology.md)

---

## E. MHW Detection

11-day DOY pooling; 90th percentile; 31-day smooth; ≥5 consecutive days; intensity = SST − Threshold90. Catalogues in `results/mhw_catalogue/`.

→ [`05_mhw_detection.md`](05_mhw_detection.md)

---

## F. Regional Division

| Region | SST box |
|--------|---------|
| North | 15–22°N, 85–95°E |
| Central | 10–15°N, 85–95°E |
| South | 5–10°N, 85–95°E |

Chosen to resolve latitudinal differences in drivers (e.g., South El Niño vs North/Central MEI La Niña). Map guide lines at 18°N/12°N differ from analysis edges (documented).

---

## G. ENSO Analysis

Monthly ONI matched at lags 0/1/2/3/6; phases ±0.5 °C; frequency χ², Pearson lags, KW/MW, annual, seasonal, strength.

**Significant:** South frequency (p=0.020); South 6-mo duration lag (r=0.433, p=0.021).  
**NS:** Most North/Central tests; duration/intensity by phase everywhere.

→ [`06_enso_analysis.md`](06_enso_analysis.md)

---

## H. IOD Analysis

**Status: complete.** Thresholds ±0.4 °C. Frequency significant all regions; Central/South 6-mo duration lags significant; **IOD #1** in composite ranking. Remaining: DMI end-date Unknown phases; no South Negative-IOD events.

→ [`07_iod_analysis.md`](07_iod_analysis.md)

---

## I. MEI Analysis

**Status: complete.** Phases ±0.5 for comparability with ONI. Significant La Niña enrichment North/Central; Central seasonal dependence; lags NS. Rank typically #2/#3 behind IOD.

→ [`08_mei_analysis.md`](08_mei_analysis.md)

---

## J. Visualization

Figure **types** (not every PNG): reporting, climatology, index characterization, six-stage driver plots, comparison dashboards (59 fig pairs), 117 wind event plots, master-catalogue figures (~76), ~3,329 lifecycle maps, publication F01–F05 / T01–T03 / top-5 triptychs, ML ROC/SHAP.

→ [`09_visualizations.md`](09_visualizations.md)

---

## K. Current Results (Headline)

1. **81%** of MHWs during weak wind.  
2. **IOD** strongest large-scale driver.  
3. **ENSO** matters most in **South**.  
4. **MEI** La Niña enrichment North/Central.  
5. **2024** exceptional (81 d; 0.943 °C).  
6. **ML F1 ≈ 0.40** best 14-day test scores; LogReg often wins.

Significant vs NS tables and limitations: [`10_results.md`](10_results.md) · numbers: [`ALL_PROJECT_RESULTS.md`](../ALL_PROJECT_RESULTS.md)

---

## L. Future Work

ENSO spatial composites; DMI extension; radiation/MLD/currents/SSS/precip/SLP/BSISO; multivariate stats; fisheries impact; ML v2; journal paper.

→ [`11_future_work.md`](11_future_work.md)

---

## M. Machine Learning (Separated)

Onset classification 3/7/14 days; XGBoost/RF/GBM + baselines; chronological split 2006–2018 / 2019–2021 / 2022–2025; features from SST, wind, flux, ONI/DMI/MEI. Code lives under `machine_learning/` (legacy `mhw_ml/` wrappers).

→ [`12_machine_learning.md`](12_machine_learning.md) · [`MIGRATION_REPORT.md`](MIGRATION_REPORT.md)

---

## N. Repository Map (Stable Climate Layout)

Climate pipeline **unchanged in place:** `datasets/`, `scripts/`, `plotting/`, `results/`.  
Documentation: `documentation/`, root `README.md`, folder READMEs.  
ML: `machine_learning/` (+ compatibility shims).

Environment: Python 3.10 · `requirements.txt`.

---

## O. References (Implied / Used)

Hobday et al. (2016); Saji et al. (1999); NOAA ONI; NOAA PSL MEI v2; Copernicus Marine Service; HadISST-based DMI (PSL). No invented citations.

---

*End of PROJECT_COMPLETE_REVIEW.md*

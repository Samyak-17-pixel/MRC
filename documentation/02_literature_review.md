# Part 2 — Literature Motivation

This document summarizes the scientific literature that motivates the project. Only references already implied by the project methodology (or standard sources for those methods) are listed. **No invented citations.**

---

## 1. What Previous Research Has Done

### 1.1 Marine Heatwave definition and detection

Hobday et al. (2016) introduced the hierarchical, percentile-based definition now used globally: exceedance of a seasonally varying 90th-percentile SST threshold for ≥5 consecutive days, with intensity metrics relative to that threshold. Subsequent work applied this definition in regional seas worldwide and refined categories (moderate / strong / severe / extreme).

**Project use:** Detection in this repository follows Hobday et al. (2016) exactly for threshold, duration, and event construction. Intensity is defined as `SST − Threshold90` (project convention within that framework).

### 1.2 Large-scale climate modes relevant to the Indian Ocean

| Mode | Standard reference / product | Role |
|------|------------------------------|------|
| **ENSO** | NOAA Oceanic Niño Index (ONI) — 3-month running mean Niño-3.4 SST anomaly; phases typically at ±0.5 °C | Pacific teleconnection to Indian Ocean SST and monsoon |
| **IOD** | Saji et al. (1999) — Dipole Mode Index (DMI): west–east tropical Indian Ocean SST anomaly gradient | Regional Indian Ocean mode directly affecting BoB |
| **MEI v2** | NOAA PSL Multivariate ENSO Index version 2 | Atmosphere–ocean composite ENSO index (complement to ONI) |

**Project use:** ONI, DMI, and MEI v2 are matched to every MHW event at 0/1/2/3/6-month lags under an identical statistical pipeline so drivers can be ranked fairly.

### 1.3 Local forcing

Surface wind and air–sea heat flux (latent and sensible) control mixed-layer heat budgets. Weak winds reduce evaporative cooling and mixing, allowing heat to accumulate — a standard physical pathway for MHW build-up.

**Project use:** Wind and heat-flux composites before/during events; weak-wind classification relative to climatology.

### 1.4 Prediction

MHW prediction literature ranges from statistical persistence and climate-index regressions to dynamical forecasts and machine learning. Onset early-warning (predicting whether a **new** event will start within H days) is less common than nowcasting ongoing warm anomalies.

**Project use:** Chronological train/test ML onset classification at H ∈ {3, 7, 14} days, using predictors justified by the climate-analysis stages.

---

## 2. Research Gap This Project Addresses

1. **Integrated BoB catalogue (2006–2025)** with consistent Hobday detection across three sub-regions.
2. **Parallel ENSO / IOD / MEI pipelines** with identical tests (frequency, lag, annual, seasonal, strength) — enabling direct ranking rather than isolated case studies.
3. **Local + large-scale synthesis** in one master event table (117 × 57 parameters).
4. **Onset forecasting** grounded in those physical results, kept in a separate ML module.
5. **Fisheries impact** remains a stated project goal but is **not yet implemented** (future work).

---

## 3. Why Climate Drivers Matter

MHWs are not only local thermodynamic accidents. Large-scale modes precondition the background SST and atmospheric circulation:

- **IOD** modulates Indian Ocean SST gradients and can favor BoB warming under Positive IOD conditions.
- **ENSO** teleconnects via atmospheric bridges; this project finds the clearest ENSO–MHW link in **South BoB** (El Niño enrichment; 6-month lag).
- **MEI** can highlight atmospheric co-variability that ONI alone misses (e.g., La Niña enrichment in North/Central in this dataset).

Without driver analysis, detection catalogues describe *what* happened but not *under what climate state*.

---

## 4. Why Prediction Matters

Early warning of MHW onset (days to weeks) can inform fisheries management, aquaculture, and ecological monitoring. Prediction without physical feature justification risks spurious skill. This project therefore:

1. Identifies drivers statistically first.
2. Uses those variables as ML features.
3. Evaluates with chronological splits (train past → test recent years).

---

## 5. Why Fisheries Impact Is Relevant

BoB fisheries support food security and livelihoods. MHWs can shift species distributions, reduce catch of heat-sensitive stocks, and stress aquaculture. **Fisheries impact analysis has not been started** in this repository; it is reserved for future work once physical drivers and predictability are documented.

---

## 6. References Used / Implied by This Project

| Reference | Use in project |
|-----------|----------------|
| Hobday, A. J., et al. (2016). A hierarchical approach to defining marine heatwaves. *Progress in Oceanography*, 141, 227–238. | MHW definition, threshold, duration |
| Saji, N. H., et al. (1999). A dipole mode in the tropical Indian Ocean. *Nature*, 401, 360–363. | IOD concept / DMI motivation |
| NOAA Climate Prediction Center — Oceanic Niño Index (ONI) methodology and ±0.5 °C phase thresholds | ENSO phase classification |
| NOAA Physical Sciences Laboratory — MEI v2 documentation | MEI data and interpretation |
| Copernicus Marine Service product documentation | SST, wind, heat-flux data provenance |
| HadISST-based DMI time series (NOAA PSL / GCOS WGSP) | IOD index data |

**Distinction:**

- **Standard scientific methodology:** Hobday detection; NOAA ONI ±0.5; IOD literature ±0.4 DMI thresholds as used here; Pearson / chi-square / Kruskal–Wallis / Mann–Whitney.
- **Project-specific choices:** 20-year climatology period (2006–2025); three BoB boxes; intensity = SST − Threshold90; lag set {0,1,2,3,6} months; wind weak/strong relative to regional climatology; ML onset labels and chronological splits.

---

## 7. Related Project Documents

- Problem statement: `01_problem_statement.md`
- Datasets: `03_datasets.md`
- Detection: `05_mhw_detection.md`
- Results: `10_results.md`
- Numerical master table: [`../ALL_PROJECT_RESULTS.md`](../ALL_PROJECT_RESULTS.md)

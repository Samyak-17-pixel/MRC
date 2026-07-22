# Part 1 — Problem Statement

**Project:** Marine Heatwave Drivers, Predictability, and Fisheries Impact in the Bay of Bengal  
**Author:** Samyak Kumar, Maritime Research Center (MRC)  
**Study period:** 2006–2025

---

## 1. What Are Marine Heatwaves?

A **Marine Heatwave (MHW)** is a discrete, prolonged period of anomalously warm ocean water at a given location. The internationally accepted definition (Hobday et al., 2016) — used verbatim in this project — states:

> An MHW occurs when daily sea surface temperature (SST) exceeds the **seasonally varying 90th-percentile climatological threshold** for **at least 5 consecutive days**.

Key aspects of this definition:

- **Relative, not absolute.** The threshold varies with the day of year, so a winter warm spell can qualify just as a summer one can. This distinguishes MHWs from simple "warm water".
- **Discrete events.** Each MHW has a start date, end date, duration, and intensity — allowing event catalogues, statistics, and driver attribution.
- **Intensity is measured against the threshold** (not the climatological mean) in this project: `Intensity = SST − Threshold90`. This is a **project-specific convention choice** within the Hobday framework and is applied consistently everywhere (detection, catalogues, ML features).

---

## 2. Why Marine Heatwaves Matter

MHWs disrupt marine ecosystems and human activities that depend on them:

- Coral bleaching and mortality
- Changes in fish distribution, recruitment, and catchability
- Harmful algal blooms and hypoxia
- Impacts on aquaculture and coastal livelihoods

Because MHWs are defined as discrete events, they can be counted, ranked, attributed to drivers, and — in principle — forecasted. That is the scientific and practical motivation for this project.

---

## 3. Why the Bay of Bengal?

The Bay of Bengal (BoB) was chosen because:

1. **Societal importance.** It supports dense coastal populations and major fisheries across India, Bangladesh, Myanmar, Sri Lanka, and Southeast Asia.
2. **Climatic complexity.** The BoB sits at the intersection of ENSO (Pacific), the Indian Ocean Dipole (IOD), the Asian monsoon, and regional atmospheric forcing — making driver attribution non-trivial.
3. **Data readiness.** Copernicus Marine Service provides consistent daily SST, wind, and heat-flux fields for 2006–2025 at useful resolution (~0.083° for SST).
4. **Research gap.** Relative to the Pacific and North Atlantic, BoB MHW driver studies and onset-forecasting frameworks remain underdeveloped.

The study domain is subdivided into three latitudinal boxes (see §Regional Division in `04_methodology.md` and `05_mhw_detection.md`):

| Region | SST box |
|--------|---------|
| North | 15–22°N, 85–95°E |
| Central | 10–15°N, 85–95°E |
| South | 5–10°N, 85–95°E |

---

## 4. Scientific Questions

1. How many MHWs occurred in each BoB sub-region during 2006–2025, and what are their duration and intensity statistics?
2. Which large-scale climate modes (ENSO via ONI, IOD via DMI, ENSO via MEI v2) are associated with MHW occurrence, duration, and intensity — and at what lags?
3. What local atmospheric/oceanographic conditions (surface wind, latent/sensible heat flux) accompany MHW events?
4. Which drivers dominate after direct comparison under a common statistical framework?
5. Can MHW **onset** be predicted 3 / 7 / 14 days ahead using the physically motivated predictors identified above?
6. *(Future)* How do MHWs affect fisheries catch and effort in the Bay of Bengal?

---

## 5. Objectives

| Objective | Status |
|-----------|--------|
| Detect all MHWs with Hobday et al. (2016) | ✅ Complete (117 events) |
| Characterize and link ENSO, IOD, MEI to every event | ✅ Complete |
| Quantify local wind and heat-flux drivers | ✅ Complete |
| Rank drivers comparatively | ✅ Complete (IOD #1; wind dominant locally) |
| Build a master per-event catalogue (57 parameters) | ✅ Complete |
| Prototype ML onset forecasting (3/7/14 days) | ✅ Complete (v1) |
| Multivariate / mechanism expansion (radiation, MLD, BSISO, …) | ❌ Pending |
| Fisheries impact analysis | ❌ Pending (title-level goal only) |
| Journal manuscript | ❌ Pending |

---

## 6. Expected Outcomes

1. A reproducible event catalogue and full statistical driver assessment for BoB MHWs (2006–2025).
2. Clear separation of **local** (wind, heat flux) vs **large-scale** (IOD, ENSO, MEI) contributions.
3. An initial early-warning ML module that forecasts onset risk at operational horizons.
4. Documentation sufficient for MRC collaborators, future interns, and external researchers to reproduce and extend the work.
5. *(Future)* Evidence linking MHWs to fisheries outcomes, suitable for journal publication.

---

## 7. Project Philosophy

> Establish physical and statistical understanding of MHW mechanisms **before** predictive modelling. Every ML predictor must be supported by statistical evidence and physical reasoning.

Climate analysis and machine learning are deliberately separated (see `machine_learning/` and `documentation/12_machine_learning.md`).

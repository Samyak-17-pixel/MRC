# Part 8 — MEI v2 Analysis

**Status:** ✅ Complete (pipeline finished 2026-07-11). Same six-stage design as ENSO/IOD; MEI v2 replaces ONI/DMI.

**Scripts:** `mei_lag_analysis.py`, `mei_frequency_analysis.py`, `mei_statistics.py`, `mei_annual_analysis.py`, `mei_seasonal_analysis.py`, `mei_strength_analysis.py`; orchestrator `mei_pipeline.py`  
**Outputs:** `results/mei_lag/`, `mei_frequency/`, `mei_statistics/`, `mei_annual/`, `mei_seasonal/`, `mei_strength/`  
**Characterization:** `results/climate_indices/mei/`  
**Index:** `datasets/meiv2.nc`

Statistical test definitions: see `06_enso_analysis.md`.

---

## 1. Completed Work

| Stage | Status |
|-------|--------|
| MEI characterization figures/CSVs | ✅ |
| Lag tagging 0/1/2/3/6 months | ✅ |
| Frequency, statistics, annual, seasonal, strength | ✅ |
| Inclusion in climate driver comparison | ✅ (rank #2 North/Central; #3 South) |

There is **no** `results/mei_analysis/` mirror of `enso_analysis/`; overview lives in climate_indices + mei_* stage folders + comparison module.

---

## 2. Phase Classification

| Phase | Criterion |
|-------|-----------|
| El Niño | MEI ≥ +0.5 |
| La Niña | MEI ≤ −0.5 |
| Neutral | otherwise |

**Project choice:** Same numeric cutoffs as ONI for **comparability**, even though MEI is dimensionless and multivariate. Documented as project-specific alignment, not a claim that MEI "equals" ONI physically.

Native MEI v2 is bimonthly; the project treats the series as monthly for event matching (same matching rule as ONI/DMI).

---

## 3. Key Results

### 3.1 Phase frequency

| Region | El Niño | Neutral | La Niña | χ² p | Significant? | Dominant |
|--------|---------|---------|---------|------|--------------|----------|
| North | 8 | 13 | 28 | **0.001** | **Yes** | **57% La Niña** |
| Central | 8 | 8 | 24 | **0.002** | **Yes** | **60% La Niña** |
| South | 13 | 8 | 7 | 0.331 | No | 46% El Niño |

### 3.2 Lag correlations (duration)

| Region | Best lag | r | p |
|--------|----------|---|---|
| North | 3 | 0.037 | 0.804 |
| Central | 0 | 0.228 | 0.157 |
| South | 6 | 0.292 | 0.131 |

All NS.

### 3.3 Seasonal dependence

| Region | Season × MEI p | Significant? |
|--------|----------------|--------------|
| North | 0.302 | No |
| **Central** | **0.0008** | **Yes** |
| South | 0.212 | No |

### 3.4 Kruskal–Wallis (duration/intensity by phase)

All NS (all regions).

---

## 4. Interpretation

MEI highlights **La Niña enrichment in North and Central BoB**, opposite in sign to the ONI-based **El Niño enrichment in South**. Because MEI includes atmospheric fields, this pattern is consistent with the project's wind finding (weak winds during MHWs): La Niña–related atmospheric states may co-occur with suppressed winds in northern/central boxes. Lag correlations are weaker than for IOD/ENSO in the South.

In composite rankings, MEI is typically **#2 (North/Central)** and **#3 (South)** behind IOD.

---

## 5. Remaining Work

| Item | Status |
|------|--------|
| Dedicated MEI publication figure suite (like `enso_mhw_analysis.py`) | Optional / not required for pipeline completeness |
| Spatial MEI composites | ❌ Not done |
| Sensitivity to bimonthly vs monthly matching | ❌ Not formalized |

---

## 6. How to Re-run

```bash
.venv/bin/python scripts/mei_pipeline.py
```

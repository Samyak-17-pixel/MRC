# Part 7 — IOD (DMI) Analysis

**Status:** ✅ Complete (pipeline finished 2026-07-11). Same six-stage design as ENSO; DMI replaces ONI.

**Scripts:** `iod_lag_analysis.py`, `iod_frequency_analysis.py`, `iod_statistics.py`, `iod_annual_analysis.py`, `iod_seasonal_analysis.py`, `iod_strength_analysis.py`; orchestrator `iod_analysis.py`  
**Outputs:** `results/iod_lag/`, `iod_frequency/`, `iod_statistics/`, `iod_annual/`, `iod_seasonal/`, `iod_strength/`, `iod_analysis/`, plus `results/climate_indices/iod/`  
**Index:** `datasets/dmi.had.long.nc`

The statistical rationale for each test is identical to `06_enso_analysis.md` — this document focuses on IOD-specific thresholds, results, and remaining issues.

---

## 1. Completed Work

| Stage | Status | Output folder |
|-------|--------|---------------|
| Index characterization | ✅ | `results/climate_indices/iod/` |
| Event tagging + lags 0/1/2/3/6 | ✅ | `results/iod_lag/` |
| Phase frequency (χ², Cramer's V) | ✅ | `results/iod_frequency/` |
| Duration/intensity by phase | ✅ | `results/iod_statistics/` |
| Annual variability | ✅ | `results/iod_annual/` |
| Seasonal dependence | ✅ | `results/iod_seasonal/` |
| Strength classification | ✅ | `results/iod_strength/` |
| Comparative ranking vs ENSO/MEI | ✅ | `results/climate_comparison/` (IOD #1 all regions) |

---

## 2. Phase and Strength Thresholds

| Phase | Criterion |
|-------|-----------|
| Positive IOD | DMI ≥ +0.4 °C |
| Negative IOD | DMI ≤ −0.4 °C |
| Neutral | otherwise |

| Strength | Positive | Negative |
|----------|----------|----------|
| Weak | 0.4–0.6 | −0.6 to −0.4 |
| Moderate | 0.6–0.8 | −0.8 to −0.6 |
| Strong | ≥ 0.8 | ≤ −0.8 |

**Basis:** Common IOD literature thresholds around ±0.4 °C (Saji et al., 1999 framework); strength bins are **project conventions** for stratified tests.

---

## 3. Event Matching

Identical to ENSO: attach `DMI_0m…6m` and `IOD_Phase` to each MHW start month. Monthly DMI; no daily interpolation.

---

## 4. Key Results

### 4.1 Phase frequency

| Region | Positive | Neutral | Negative | χ² p | Cramer's V | Significant? |
|--------|----------|---------|----------|------|------------|--------------|
| North | 13 | 30 | 1 | **<0.001** | 0.574 | **Yes** |
| Central | 10 | 27 | 1 | **<0.001** | 0.602 | **Yes** |
| South | 10 | 17 | 0 | **0.0003** | 0.548 | **Yes** |

\*Unknown-phase events excluded from these counts (DMI ends April 2025).

### 4.2 Lag correlations

| Region | Best lag | Duration r (p) | Intensity notes |
|--------|----------|----------------|-----------------|
| North | 3 mo | 0.083 (0.589) NS | — |
| Central | **6 mo** | **0.344 (0.030) SIG** | — |
| South | **6 mo** | **0.459 (0.014) SIG** | Intensity lag 0: r=0.402, p=0.038 SIG |

### 4.3 Duration/intensity by phase (Kruskal–Wallis)

All regions: **not significant** (duration and intensity p > 0.10–0.35 depending on region).

### 4.4 Annual / seasonal / strength

- Annual DMI correlations: all NS  
- Seasonal χ²: all NS  
- Strength effects: NS  

---

## 5. Interpretation

IOD is the **strongest large-scale climate driver** in the comparative assessment (composite rank #1 in North, Central, South). Phase frequency is significant everywhere (Neutral-dominated counts, with Positive IOD also common among events). Lagged duration links are significant in Central and South at 6 months. Phase membership alone does **not** predict longer/stronger events (KW NS) — frequency and lag structure matter more than within-phase intensity differences.

---

## 6. Remaining Work / Limitations

| Item | Status |
|------|--------|
| Extend DMI beyond April 2025 / nearest-month fallback for Unknown phases | ❌ Not done (8 Unknown events) |
| South Negative IOD events | 0 in catalogue — Negative-phase tests skipped |
| Spatial IOD composites | Not a separate completed module |
| Formal multiple-testing correction across drivers | Not applied |

**Do not "fix" Unknown phases by silently extending DMI without documenting the method.**

---

## 7. How to Re-run

```bash
.venv/bin/python scripts/iod_analysis.py
# or individual iod_* scripts — see scripts/README.md
```

# Part 10 — Current Results Summary

Master numerical reference: [`../ALL_PROJECT_RESULTS.md`](../ALL_PROJECT_RESULTS.md).  
This document separates **significant** vs **non-significant** findings, conclusions, and limitations **without changing any reported numbers**.

---

## 1. Detection Summary

| Region | Events | Mean duration (d) | Max duration (d) | Mean max intensity (°C) | Max intensity (°C) |
|--------|--------|-------------------|------------------|-------------------------|--------------------|
| North | 49 | 13.0 | 61 | 0.317 | 0.912 |
| Central | 40 | 14.5 | 53 | 0.300 | 0.907 |
| South | 28 | 20.5 | 81 | 0.315 | 0.943 |
| **Total** | **117** | **15.3** | **81** | **0.310** | **0.943** |

Record events: longest South S25 81 d (2024-06-14); strongest South S24 0.943 °C (2024-04-14).

---

## 2. Statistically Significant Findings

| Finding | Evidence |
|---------|----------|
| **South ENSO phase frequency** | χ² p = 0.020; 54% El Niño |
| **South ENSO lag (duration, 6 mo)** | r = 0.433, p = 0.021 |
| **IOD phase frequency (all regions)** | North/Central p < 0.001; South p = 0.0003 |
| **Central IOD lag (duration, 6 mo)** | r = 0.344, p = 0.030 |
| **South IOD lag (duration, 6 mo)** | r = 0.459, p = 0.014 |
| **South IOD intensity (lag 0)** | r = 0.402, p = 0.038 |
| **North MEI phase frequency** | p = 0.001; 57% La Niña |
| **Central MEI phase frequency** | p = 0.002; 60% La Niña |
| **Central MEI seasonal dependence** | season × MEI p ≈ 0.0008 |
| **IOD composite rank #1** | All regions in `climate_comparison` |
| **Weak-wind dominance (descriptive)** | 81.2% of events (95/117); regionally 77.5–83.7% |

---

## 3. Not Statistically Significant (Important Nulls)

| Test | Result |
|------|--------|
| ENSO phase frequency North / Central | p = 0.066 / 0.082 (NS; North marginal) |
| ENSO lag North; Central duration | NS / marginal (p = 0.070) |
| ENSO duration/intensity by phase (KW) | NS all regions |
| ENSO annual & seasonal | NS |
| IOD duration/intensity by phase (KW) | NS |
| IOD annual, seasonal, strength | NS |
| MEI phase frequency South | p = 0.331 NS |
| MEI lag correlations | NS all regions |
| MEI duration/intensity by phase | NS |
| MEI annual; North/South seasonal | NS |

**Takeaway:** Large-scale modes often affect **whether/when** events cluster in phases or correlate at lag, more than **how long/intense** events are within a phase.

---

## 4. Scientific Conclusions

1. **117 MHWs** detected (2006–2025) with Hobday 90th-percentile / ≥5-day rules.
2. **Local wind suppression is the dominant immediate condition** (~81% weak-wind events).
3. **IOD is the strongest large-scale climate driver** across all three boxes.
4. **ENSO matters most in South BoB** (El Niño enrichment + 6-month lag).
5. **MEI shows La Niña enrichment in North/Central**, highlighting multivariate/atmospheric ENSO aspects.
6. **2024 was exceptional** (longest and strongest events in South).
7. **ML onset forecasting (v1)** reaches F1 up to ~0.40 at 14-day horizon on 2022–2025 test years; logistic regression often competitive with trees on this small/rare-event dataset (details in `12_machine_learning.md`).
8. **Fisheries impact** remains future work.

---

## 5. Limitations

| Limitation | Impact |
|------------|--------|
| DMI ends April 2025 | 8 Unknown IOD phases |
| SST box 85–95°E vs wind box 80–100°E | Spatial inconsistency |
| Heat flux ~weekly, forward-filled | Lower temporal precision |
| South: 0 Negative-IOD MHWs | Negative-phase tests skipped |
| Climatology = 20-year study window | Trend may enter baseline |
| Regional-mean SST | No sub-box event geometry in catalogue |
| Frequency tests use equal phase expectation | Not climatological phase weights |
| Many simultaneous tests | No formal FDR/Bonferroni |
| ML rare positives (1.6–7.4%) | Wide uncertainty on F1/PR-AUC |
| Fisheries / BSISO / radiation / MLD | Not yet analysed |

---

## 6. Related Documents

- Driver details: `06_enso_analysis.md`, `07_iod_analysis.md`, `08_mei_analysis.md`
- Figures: `09_visualizations.md`
- Roadmap: `11_future_work.md`
- Working notebook: `../PROJECT.md`

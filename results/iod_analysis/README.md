# IOD (DMI) — MHW Analysis Outputs

This README documents **all `iod_*` output folders** under `results/`. The IOD pipeline mirrors the ENSO pipeline exactly (same six stages, same statistics) so drivers can be compared directly — only the index (DMI instead of ONI) and phase thresholds differ.

Full methodology: [`documentation/07_iod_analysis.md`](../../documentation/07_iod_analysis.md). The statistical framework is defined in [`documentation/06_enso_analysis.md`](../../documentation/06_enso_analysis.md).

---

## Pipeline Stages and Folders

| Folder | Script | Question answered |
|--------|--------|-------------------|
| `../iod_lag/` | `iod_lag_analysis.py` | DMI at 0/1/2/3/6-month lags per event; lag correlations |
| `../iod_frequency/` | `iod_frequency_analysis.py` | Event distribution across Positive / Neutral / Negative IOD |
| `../iod_statistics/` | `iod_statistics.py` | Duration/intensity by phase (Kruskal–Wallis, Mann–Whitney) |
| `../iod_annual/` | `iod_annual_analysis.py` | Annual counts vs annual DMI |
| `../iod_seasonal/` | `iod_seasonal_analysis.py` | Season × phase chi-square |
| `../iod_strength/` | `iod_strength_analysis.py` | Event properties vs IOD strength class |
| `iod_analysis/` (this folder) | `iod_analysis.py` | DMI characterization + pipeline orchestrator outputs |

## Phase Classification (Saji et al. 1999 convention, ±0.4 °C)

| Phase | Criterion |
|-------|-----------|
| Positive IOD | DMI ≥ +0.4 °C |
| Negative IOD | DMI ≤ −0.4 °C |
| Neutral | −0.4 < DMI < +0.4 |

**Strength classes:** Weak 0.4–0.6, Moderate 0.6–0.8, Strong ≥ 0.8 (mirrored for negative).

## Headline IOD Results

| Region | Phase frequency χ² p | Cramer's V | Best lag | Duration r (p) |
|--------|---------------------|-----------|----------|----------------|
| North | **< 0.001 (SIG)** | 0.574 | 3 mo | 0.083 (0.589, NS) |
| Central | **< 0.001 (SIG)** | 0.602 | **6 mo** | **0.344 (0.030, SIG)** |
| South | **0.0003 (SIG)** | 0.548 | **6 mo** | **0.459 (0.014, SIG)** — intensity also SIG at lag 0 (r=0.402, p=0.038) |

**Conclusion:** IOD is the **strongest large-scale climate driver in all three regions** (composite rank #1 in the driver comparison). Phase frequency is significant everywhere; lagged duration correlations are significant in Central and South at 6 months.

## Data Limitations (documented, not fixed)

- **DMI ends April 2025** → 8 events (5 North, 2 Central, 1 South) carry `Unknown` IOD phase and are excluded from phase-based tests.
- **South has 0 Negative-IOD events** → Negative-phase comparisons are skipped (NaN) for South; expected given only 9 Negative-IOD months in 2006–2025.

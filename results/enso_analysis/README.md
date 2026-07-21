# ENSO (ONI) — MHW Analysis Outputs

This README documents **all seven `enso_*` output folders** under `results/`. This folder (`enso_analysis/`) holds the comprehensive ENSO–MHW figures; the six sibling folders hold the stage-by-stage statistical pipeline.

Full methodology (preprocessing, event matching, statistics, interpretation): [`documentation/06_enso_analysis.md`](../../documentation/06_enso_analysis.md).

---

## Pipeline Stages and Folders

| Folder | Script | Question answered |
|--------|--------|-------------------|
| `../enso_lag/` | `enso_lag_analysis.py` | What was ONI at event time and 1/2/3/6 months before? Do lagged ONI values correlate with duration/intensity? |
| `../enso_frequency/` | `enso_frequency_analysis.py` | Are MHWs distributed unevenly across El Niño / Neutral / La Niña? (chi-square + Cramer's V) |
| `../enso_statistics/` | `enso_statistics.py` | Do duration/intensity differ by phase? (Kruskal–Wallis, Mann–Whitney U) |
| `../enso_annual/` | `enso_annual_analysis.py` | Do annual event counts track annual mean ONI? |
| `../enso_seasonal/` | `enso_seasonal_analysis.py` | Does the season × phase distribution deviate from independence? |
| `../enso_strength/` | `enso_strength_analysis.py` | Do stronger El Niño / La Niña episodes produce longer/stronger MHWs? |
| `enso_analysis/` (this folder) | `enso_mhw_analysis.py` | Combined overview figures; per-event plot folders |

## Key Files

| File | Contents |
|------|----------|
| `../enso_lag/{region}_enso_lag.csv` | Every event tagged with `ONI_0m,1m,2m,3m,6m` + `ENSO_Phase` |
| `../enso_lag/{region}_lag_correlation.csv` | Pearson r + p per lag for duration and intensity |
| `../enso_lag/summary.csv`, `../enso_frequency/summary.csv` | One-line-per-region summaries |
| `../enso_frequency/{region}_frequency.csv/png` | Phase counts + chi-square results |

## Phase Classification (NOAA convention)

| Phase | Criterion |
|-------|-----------|
| El Niño | ONI ≥ +0.5 °C |
| La Niña | ONI ≤ −0.5 °C |
| Neutral | −0.5 < ONI < +0.5 |

## Headline ENSO Results

| Region | Phase frequency χ² p | Best lag | Duration r at best lag (p) |
|--------|---------------------|----------|---------------------------|
| North | 0.066 (NS) | 6 mo | 0.135 (0.354) |
| Central | 0.082 (NS) | 6 mo | 0.290 (0.070, marginal) |
| **South** | **0.020 (SIG)** | **6 mo** | **0.433 (0.021, SIG)** |

**Conclusion:** ENSO significantly influences **South BoB only** — 54% of South events occurred during El Niño, with a significant 6-month lag teleconnection. Duration/intensity **within** phases show no significant differences anywhere (Kruskal–Wallis all NS).

## Deferred Items in This Folder

- `north/central/south_event_plots/` — empty directories (per-event ENSO diagnostic plots were planned, deferred to publication phase).
- ENSO spatial composites (`scripts/enso_spatial_analysis.py`) — started, no outputs yet.

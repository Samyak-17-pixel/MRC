# outputs/iod/ — IOD (DMI)–MHW Analysis

Six-stage (plus analysis where present) pipeline linking every Hobday MHW to the IOD (DMI) index.

## Purpose

Quantify how IOD (DMI) phases, lags, seasons, and strength relate to MHW frequency, duration, and intensity in North / Central / South BoB (2006–2025; **117** events).

## Subfolders

| Folder | Stage |
|--------|-------|
| `lag/` | Index values at 0/1/2/3/6-month lags; Pearson correlations |
| `frequency/` | Phase frequency + chi-square / Cramer's V |
| `statistics/` | Duration/intensity stats across phases |
| `annual/` | Annual event counts vs annual index |
| `seasonal/` | Season × phase contingency |
| `strength/` | Event properties vs strength class |
| `analysis/` | Comprehensive IOD (DMI)–MHW figures / per-event plots |

## How generated

Identical script pattern (replace index name):

| Stage | Script → folder |
|-------|-----------------|
| Lag | `src/climate/scripts/iod_lag_analysis.py` → `lag/` |
| Frequency | `src/climate/scripts/iod_frequency_analysis.py` → `frequency/` |
| Statistics | `src/climate/scripts/iod_statistics.py` → `statistics/` |
| Annual | `src/climate/scripts/iod_annual_analysis.py` → `annual/` |
| Seasonal | `src/climate/scripts/iod_seasonal_analysis.py` → `seasonal/` |
| Strength | `src/climate/scripts/iod_strength_analysis.py` → `strength/` |
| (IOD analysis figs) | See `iod/analysis/` and `iod_analysis.py` orchestration |

Index characterization (timeseries only) also lives under `outputs/climate_indices/`.

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `outputs/mhw/catalogue/`, index CSVs under `outputs/climate_indices/` | `outputs/climate_comparison/`, `outputs/master_event_catalogue/`, ML climate features |

## Notes

- Phase thresholds: ENSO/MEI ±0.5; IOD ±0.4.
- Cross-driver ranking: **IOD #1** large-scale driver overall; ENSO matters most in **South BoB**.
- DMI ends April 2025 → some late-2025 IOD phases are `Unknown` (IOD pipeline).

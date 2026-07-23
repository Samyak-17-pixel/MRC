# src/climate/ — Climate Analysis Package

Non-ML scientific pipeline for Bay of Bengal MHWs: data prep, Hobday detection, climate-index characterization, driver–event analyses, and publication synthesis.

## Purpose

Establish physical and statistical understanding of MHW mechanisms **before** predictive modelling. Every ML predictor used in `src/ml/` is motivated by results produced here.

**Study period:** 2006–2025 · **Regions:** North / Central / South BoB · **Catalogue:** 117 Hobday events (North 49, Central 40, South 28).

## Contents

```
src/climate/
├── scripts/     # pipeline stages (merge → detect → drivers → synthesis)
└── plotting/    # shared Cartopy base-map helpers (bob_map.py)
```

## Pipeline (high level)

```
data/raw/ → scripts (Stage 1–2) → outputs/timeseries + outputs/mhw/
         → ENSO/IOD/MEI + wind/heat flux → outputs/enso|iod|mei|drivers/
         → climate_driver_comparison + master catalogue + maps → outputs/
```

See `scripts/README.md` for the full dependency graph and script table.

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `data/raw/` NetCDFs | `outputs/timeseries/`, `outputs/mhw/`, climate-index and driver trees, `outputs/publication/` |
| | Consumed by `src/ml/` (reads catalogues, SST, wind, flux, index CSVs) |

## Headline science (orientation)

- Hobday: SST > seasonally varying P90 for ≥5 consecutive days; Intensity = SST − Threshold90.
- ~81% of events during anomalously weak surface wind (95/117).
- **IOD** is the strongest large-scale driver across all three regions.
- Known caveats: DMI ends April 2025 (late-2025 IOD phase `Unknown`); wind bbox 80–100°E vs SST 85–95°E.

## How to run

```bash
.venv/bin/python src/climate/scripts/<script>.py
```

Always run from the repository root so relative and absolute paths resolve correctly.

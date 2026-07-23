# outputs/drivers/ — Local Physical Drivers

Wind and surface heat-flux analyses for Bay of Bengal MHWs (complements large-scale ENSO/IOD/MEI).

## Purpose

Document local conditions during events — especially **weak surface winds** (~81% of 117 events) and latent/sensible heat-flux anomalies.

## Contents

| Path | Role |
|------|------|
| `wind/` | Per-event wind classification + 117 event plots |
| `heat_flux/` | Regional SLHF/SSHF timeseries + figures |
| `heat_flux_analysis/` | Flux anomalies / reduced-loss flags during MHWs |

## How generated

See each subfolder README. Scripts live under `src/climate/scripts/` (`extract_regional_wind.py`, `wind_mhw_*.py`, `extract_heat_flux.py`, `heat_flux_*.py`).

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `outputs/timeseries/*_wind.csv`, heat-flux extracts, MHW catalogues | Master catalogue; ML wind/flux features; publication F02 |

## Notes

Wind bbox (80–100°E) ≠ SST bbox (85–95°E) — known limitation.

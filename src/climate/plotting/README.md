# src/climate/plotting/ — Shared Map Helpers

Reusable Cartopy plotting utilities for Bay of Bengal figures.

## Purpose

Centralize base-map construction (projection, coastlines, regional guide lines, extent) so map-producing scripts stay visually consistent.

## Contents

| File | Purpose |
|------|---------|
| `bob_map.py` | Standard BoB base map: PlateCarree, 50 m Natural Earth coastline, regional boundary lines, shared extent/styling. Source of the archived reference image `archive/bay_of_bengal_base_map.png`. |

## How outputs are generated

Scripts under `src/climate/scripts/` import helpers from this package (e.g. `top_event_sst_lifecycle_maps.py`, `process_all_years.py`, `enso_spatial_analysis.py`). This folder does not write pipeline CSVs by itself.

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| Cartopy Natural Earth data (`cartopy_data/`) | PNG/PDF maps under `outputs/maps/`, `outputs/yearly/`, `outputs/top_event_sst_maps/`, `outputs/publication/`, etc. |

## Notes — SST boxes vs map lines

| Purpose | North | Central | South |
|---------|-------|---------|-------|
| **SST averaging boxes** | 15–22°N | 10–15°N | 5–10°N |
| **Map display lines** | above 18°N | 12–18°N | below 12°N |

Both are intentional: map lines are visual guides; SST boxes define analyzed time series.

## Dependencies

- `cartopy` with Natural Earth 50 m coastline cached in `cartopy_data/`
- `matplotlib`

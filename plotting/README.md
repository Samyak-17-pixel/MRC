# plotting/ — Reusable Mapping Utilities

Shared Cartopy plotting code used by the map-producing analysis scripts.

## Contents

| File | Purpose |
|------|---------|
| `bob_map.py` | Builds the standard Bay of Bengal base map: PlateCarree projection, 50m coastline, regional boundary lines at 18°N and 12°N (map display boundaries), consistent extent and styling. Generated the reference image `bay_of_bengal_base_map.png` at the repository root. |

## Usage

Imported by scripts in `scripts/` that draw maps (e.g. `top_event_sst_lifecycle_maps.py`, `process_all_years.py`, `enso_spatial_analysis.py`). Typical pattern:

```python
from plotting.bob_map import ...  # base map / region-line helpers
```

## Region Lines: SST Boxes vs Map Boundaries

Note the two related but distinct sets of latitudes used in this project:

| Purpose | North | Central | South |
|---------|-------|---------|-------|
| **SST averaging boxes** (analysis) | 15–22°N | 10–15°N | 5–10°N |
| **Map display boundaries** (red lines on figures) | above 18°N | 12–18°N | below 12°N |

Both are intentional; the map lines are visual guides while the SST boxes define the analyzed time series. Documented in `documentation/04_methodology.md` §Regional Division.

## Dependencies

- `cartopy` (0.25.0) with the Natural Earth 50m coastline cached in `cartopy_data/`
- `matplotlib`

## Common Issues

- On a fresh machine Cartopy will download Natural Earth data once (needs internet). Afterwards the cache makes runs offline-safe.

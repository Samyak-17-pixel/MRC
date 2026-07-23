# archive/ — Retired Root Clutter & Path Tools

Holding area for files that are no longer part of the active pipeline but are kept for reference during/after repository reorganization.

## Purpose

Keep the repository root and active `src/` / `outputs/` trees clean without immediately deleting historical helpers or one-off assets.

## Contents

| Item | Notes |
|------|-------|
| `bay_of_bengal_base_map.png` | Reference base-map image (generated via plotting helpers) |
| `rewrite_paths.py` | Utility used during path/layout migration |
| `root_scripts/` | Old root-level scratch/test scripts (`enso_figures.py`, `inspect_sst.py`, `test_bob.py`, `test_open.py`) |
| `results_text` | Legacy text snippet |

## How related outputs are generated today

Active climate code: `src/climate/scripts/` + `src/climate/plotting/`.  
Active ML code: `src/ml/`.  
Active products: `outputs/` and `src/ml/outputs/`.

## Notes

- Do **not** treat `archive/` as an input to science pipelines.
- Prefer regenerating maps from `src/climate/plotting/` rather than editing the archived PNG.
- Safe to ignore for day-to-day analysis runs.

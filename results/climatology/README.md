# results/climatology/ — SST Climatology & Hobday Thresholds

Day-of-year SST climatology and the 90th-percentile detection thresholds that define Marine Heatwaves in this project.

Produced by: `scripts/build_hobday_climatology.py` (Hobday version, used for detection) and `scripts/build_climatology.py` (simple version, kept for reference). Figures via `scripts/plot_hobday_climatology.py` / `plot_climatology.py`.

## Key Files

| File | Contents |
|------|----------|
| `{region}_hobday.csv` | **The detection reference.** Columns: `DOY` (1–366), `Climatology` (11-day-window day-of-year mean SST, °C), `Threshold90` (smoothed 90th percentile, °C) |
| `{region}_climatology.csv`, `{region}_threshold.csv` | Earlier simple climatology (superseded by Hobday files) |
| `bob_spatial_climatology.nc`, `bob_spatial_threshold90.nc` | Grid-point climatology/threshold over the whole Bay (used by spatial map scripts) |
| `figures/`, `hobday_figures/` | Climatology + threshold curves per region |

## Method (Hobday et al. 2016)

1. For each day-of-year, pool all SST values within a **±5-day window (11 days)** across all years (2006–2025) — climatological baseline.
2. Take the **90th percentile** of each pool → raw threshold.
3. Smooth the threshold with a **31-day moving average** → `Threshold90`.
4. A day is "extreme" when regional SST > `Threshold90`; ≥5 consecutive extreme days = one MHW event.

The climatology period equals the full study period (2006–2025) — a fixed 20-year baseline, documented choice (Hobday recommends ≥30 years where available; 20 years is what the Copernicus record allows here).

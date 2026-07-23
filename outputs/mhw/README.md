# outputs/mhw/ — Marine Heatwave Products

All Hobday detection products and standard MHW reports for North / Central / South Bay of Bengal (2006–2025).

## Purpose

House the **central event database** and derived statistics/figures that every climate-driver and ML label pipeline depends on.

## Contents

| Path | Role |
|------|------|
| `catalogue/` | Per-region event catalogues (**117 total**: 49 / 40 / 28) |
| `climatology/` | DOY climatology + Threshold90 (+ spatial NetCDFs) |
| `annual_statistics/` | Yearly event summaries |
| `event_reports/` | Per-year event lists by region |
| `top_events/` | Top-10 longest / strongest CSVs |
| `figures/` | SST and count/duration/intensity vs year plots |
| `master_summary.csv`, `mhw_summary.txt` | Overall summaries |

## Hobday definition (project-wide)

- SST > seasonally varying **P90** for **≥5** consecutive days
- **Intensity** = SST − Threshold90

## How generated

| Stage | Script |
|-------|--------|
| Climatology | `src/climate/scripts/build_hobday_climatology.py` |
| Detection | `src/climate/scripts/detect_mhw.py` |
| Reports | `src/climate/scripts/generate_mhw_reports.py` |
| Summaries | `src/climate/scripts/mhw_statistics.py` |
| Core figures | `plot_regional_sst.py`, related plot scripts |

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| `outputs/timeseries/*_bob_sst.csv` | `outputs/enso|iod|mei/`, `drivers/`, `master_event_catalogue/`, `src/ml/` labels |

## Notes

ML annual forecast ≠ catalogue annual count. Catalogue answers “how many events started?”; ML answers “will one start in the next H days?”

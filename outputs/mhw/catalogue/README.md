# outputs/mhw/catalogue/ — Central MHW Event Database

The single most important climate data product: all detected Marine Heatwave events. **Every downstream analysis (ENSO/IOD/MEI, wind, heat flux, master catalogue, ML labels) reads these files.**

## Contents

| File | Region | Events |
|------|--------|--------|
| `north_mhw_catalogue.csv` | North BoB (15–22°N, 85–95°E) | 49 |
| `central_mhw_catalogue.csv` | Central BoB (10–15°N, 85–95°E) | 40 |
| `south_mhw_catalogue.csv` | South BoB (5–10°N, 85–95°E) | 28 |

**Total: 117 events (2006–2025).**

## Column schema

| Column | Meaning |
|--------|---------|
| `Start_Date` | First day of a ≥5-day run above Threshold90 |
| `End_Date` | Last day of the run |
| `Duration_Days` | End − Start + 1 (minimum 5) |
| `Mean_Intensity` | Mean (SST − Threshold90) °C |
| `Max_Intensity` | Max (SST − Threshold90) °C |

Intensity is relative to the **seasonally varying 90th-percentile threshold** (Hobday et al. 2016), not the climatological mean.

## How produced

1. `src/climate/scripts/extract_regional_sst.py`
2. `src/climate/scripts/build_hobday_climatology.py`
3. `src/climate/scripts/detect_mhw.py`

## Record events

| Record | Region | Start | Value |
|--------|--------|-------|-------|
| Longest | South | 2024-06-14 | 81 days |
| Strongest | South | 2024-04-14 | 0.943 °C max intensity |

## Notes

Do not edit by hand — regenerate with `detect_mhw.py`. Manual edits would corrupt every downstream analysis.

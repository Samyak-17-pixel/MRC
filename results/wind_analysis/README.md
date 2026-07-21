# results/wind_analysis/ — Wind–MHW Driver Analysis

Home of the project's **headline finding: 78–84% of Bay of Bengal MHW events occurred during anomalously weak surface winds** (North 83.7%, Central 77.5%, South 82.1%; 95/117 = 81.2% overall).

Produced by: `scripts/wind_mhw_analysis.py`, `scripts/wind_climatology_analysis.py`, `scripts/wind_mhw_summary.py` (input wind series from `scripts/extract_regional_wind.py`).

## Contents

| Item | Contents |
|------|----------|
| `{region}_wind_mhw_analysis.csv` | Per event: wind 30/21/14/7 days before, during, change, weak/strong classification |
| `{region}_wind_climatology_analysis.csv` | Event wind vs day-of-year wind climatology (anomaly-based classification) |
| `{region}_event_plots/` | One figure per event (117 total): wind time series around the event with MHW window shaded |

## Classification Logic

- **Weak wind event:** mean wind during the event is **below** the regional climatological mean wind for the same calendar window.
- Mean wind anomalies during MHWs: North −0.27 m/s, Central −0.48 m/s, South −0.66 m/s (typical values).

## Physical Interpretation

Weak winds reduce evaporative (latent) cooling and vertical mixing, allowing shortwave heating to accumulate in a shallow mixed layer — the standard local mechanism for MHW build-up. Consistent with the heat-flux result (reduced latent heat loss in ~47% of events, strongest in Central/South).

## Known Limitation

Wind was extracted over 80–100°E while SST regions use 85–95°E (documented project-wide limitation; do not fix silently).

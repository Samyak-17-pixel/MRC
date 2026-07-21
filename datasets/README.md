# datasets/ — Raw Input Data

All raw input data for the Bay of Bengal MHW project. **These files are not tracked in Git** (they total several GB); this README documents exactly what belongs here and where to get it, so the folder can be rebuilt on any machine.

Full scientific documentation of every dataset (variables, units, resolution, rationale): [`documentation/03_datasets.md`](../documentation/03_datasets.md).

---

## Expected Contents

```
datasets/
├── copernicus_daily_sst_1Jan2006_31Dec2010.nc     ← daily SST, block 1
├── copernicus_daily_sst_1Jan2011_31Dec2015.nc     ← daily SST, block 2
├── copernicus_daily_sst_1Jan2016_31Dec2020.nc     ← daily SST, block 3
├── copernicus_daily_sst_1Jan2021_31Dec2025.nc     ← daily SST, block 4
├── Wind_speed_data_2006_2025/                     ← 10 m wind NetCDFs
├── heat_flux_data_2006_2025/                      ← 20 yearly folders (heat_flux_2006 … heat_flux_2025)
├── oni.nc                                         ← Oceanic Niño Index (ENSO)
├── dmi.had.long.nc                                ← Dipole Mode Index (IOD)
└── meiv2.nc                                       ← Multivariate ENSO Index v2
```

## Dataset Summary

| Dataset | Source | Variables | Resolution | Coverage | Used for |
|---------|--------|-----------|-----------|----------|----------|
| Copernicus daily SST | Copernicus Marine Service (CMEMS) | `thetao` (°C) | ~0.083° spatial, daily | 2006–2025, Bay of Bengal | MHW detection (core dataset) |
| 10 m wind | CMEMS | `u10`, `v10` (m/s) | Gridded, daily | 2006–2025 | Local driver analysis |
| Latent + sensible heat flux | CMEMS | SLHF, SSHF (W/m², sign convention: positive = ocean heat loss reduced when anomaly positive) | Gridded, ~weekly | 2006–2025 | Surface forcing analysis |
| ONI | NOAA Climate Prediction Center | ONI (°C, 3-month running mean Niño-3.4 SST anomaly) | Monthly | 1950–2026 | ENSO phase classification |
| DMI | NOAA PSL (HadISST-based) | DMI (°C, west–east Indian Ocean SST gradient) | Monthly | 1870–2025 | IOD phase classification |
| MEI v2 | NOAA Physical Sciences Laboratory | MEI (dimensionless, bimonthly multivariate ENSO index) | Bimonthly (treated monthly) | 1979–2026 | Multivariate ENSO classification |

## Download Sources

| Dataset | Where |
|---------|-------|
| Copernicus SST / wind / heat flux | https://data.marine.copernicus.eu/ (free account required; select Bay of Bengal subset, 2006–2025) |
| ONI | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt (or NetCDF mirrors) |
| DMI (HadISST) | https://psl.noaa.gov/gcos_wgsp/Timeseries/DMI/ |
| MEI v2 | https://psl.noaa.gov/enso/mei/ |

## Spatial Domains (Important)

| Variable | Bounding box |
|----------|--------------|
| SST regional extraction | 5–22°N, **85–95°E** (split N/C/S at 15°N and 10°N) |
| Wind extraction | 5–22°N, **80–100°E** |

**Known limitation:** the SST and wind boxes differ. This is documented (do not silently "fix" — results were produced with these boxes). See `documentation/10_results.md` §Limitations.

## Notes

- NOAA OISST was evaluated at project start but **replaced by Copernicus SST** (higher resolution, better coastal representation, consistency with wind/flux from the same provider).
- DMI ends **April 2025** → 8 MHW events in late 2025 have `Unknown` IOD phase.
- Heat flux files are ~weekly; analysis scripts forward-fill to daily where needed.
- After downloading, verify files with `scripts/inspect_copernicus.py`, `scripts/inspect_climate_indices.py`, `scripts/inspect_wind.py`, `scripts/inspect_heat_flux.py`.

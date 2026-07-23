# data/raw/ — Raw Input Data

All raw inputs for the Bay of Bengal MHW project. **Not tracked in Git** (several GB). Rebuild this folder on any machine using the sources below.

## Purpose

Provide NetCDF (and folderized) observations / indices consumed by `src/climate/scripts/`.

## Expected contents

```
data/raw/
├── copernicus_daily_sst_1Jan2006_31Dec2010.nc
├── copernicus_daily_sst_1Jan2011_31Dec2015.nc
├── copernicus_daily_sst_1Jan2016_31Dec2020.nc
├── copernicus_daily_sst_1Jan2021_31Dec2025.nc
├── Wind_speed_data_2006_2025/              # 10 m wind NetCDFs
├── heat_flux_data_2006_2025/               # heat_flux_2006 … heat_flux_2025
├── oni.nc                                  # Oceanic Niño Index
├── dmi.had.long.nc                         # Dipole Mode Index (IOD)
└── meiv2.nc                                # Multivariate ENSO Index v2
```

## Dataset summary

| Dataset | Source | Variables | Coverage | Used for |
|---------|--------|-----------|----------|----------|
| Copernicus daily SST | CMEMS | `thetao` (°C), ~0.083° | 2006–2025 | MHW detection |
| 10 m wind | CMEMS | `u10`, `v10` | 2006–2025 | Local driver analysis |
| Latent + sensible heat flux | CMEMS | SLHF, SSHF | 2006–2025 | Surface forcing |
| ONI | NOAA CPC | ONI (°C) | 1950–2026 | ENSO phases |
| DMI | NOAA PSL (HadISST) | DMI (°C) | 1870–2025 | IOD phases |
| MEI v2 | NOAA PSL | MEI | 1979–2026 | Multivariate ENSO |

## Download sources

| Dataset | Where |
|---------|-------|
| SST / wind / heat flux | https://data.marine.copernicus.eu/ (BoB subset, 2006–2025) |
| ONI | https://www.cpc.ncep.noaa.gov/data/indices/ |
| DMI | https://psl.noaa.gov/gcos_wgsp/Timeseries/DMI/ |
| MEI v2 | https://psl.noaa.gov/enso/mei/ |

## Spatial domains (important)

| Variable | Bounding box |
|----------|--------------|
| SST regional extraction | 5–22°N, **85–95°E** (split at 15°N and 10°N) |
| Wind extraction | 5–22°N, **80–100°E** |

**Known limitation:** SST and wind boxes differ. Documented project-wide — do not silently “fix”; published results used these boxes.

## How outputs are generated from these files

Typical first scripts:

```bash
.venv/bin/python src/climate/scripts/inspect_copernicus.py
.venv/bin/python src/climate/scripts/merge_sst.py
.venv/bin/python src/climate/scripts/extract_regional_sst.py
.venv/bin/python src/climate/scripts/inspect_climate_indices.py
.venv/bin/python src/climate/scripts/inspect_wind.py
.venv/bin/python src/climate/scripts/inspect_heat_flux.py
```

Products land under `outputs/timeseries/`, `outputs/mhw/`, etc.

## Notes / caveats

- NOAA OISST was explored then **replaced by Copernicus SST** (resolution, coasts, consistency with other CMEMS fields).
- **DMI ends April 2025** → eight late-2025 MHWs have `Unknown` IOD phase in downstream tables.
- Heat flux is ~weekly; analysis/ML forward-fill to daily where needed.
- Study period for analyses: **2006–2025**.

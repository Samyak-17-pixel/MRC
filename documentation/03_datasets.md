# Part 3 — Datasets

Complete documentation of every dataset used in this project. Paths are **project-relative**. Raw NetCDF files under `datasets/` are not stored in Git (see `datasets/README.md` and `.gitignore`).

---

## 1. Overview Table

| Dataset | Local path | Source | Temporal | Spatial | Primary use |
|---------|------------|--------|----------|---------|-------------|
| Copernicus daily SST | `datasets/copernicus_daily_sst_*.nc` (4 files) | Copernicus Marine Service | Daily, 2006–2025 | ~0.083°, BoB | MHW detection |
| 10 m wind | `datasets/Wind_speed_data_2006_2025/` | CMEMS | Daily, 2006–2025 | Gridded BoB | Local driver |
| Latent + sensible heat flux | `datasets/heat_flux_data_2006_2025/` | CMEMS | ~Weekly, 2006–2025 | Gridded BoB | Surface forcing |
| ONI | `datasets/oni.nc` | NOAA CPC | Monthly, 1950–2026 | Index (Niño-3.4) | ENSO |
| DMI | `datasets/dmi.had.long.nc` | NOAA PSL (HadISST-based) | Monthly, 1870–2025 | Index (tropical IO) | IOD |
| MEI v2 | `datasets/meiv2.nc` | NOAA PSL | Bimonthly (treated monthly), 1979–2026 | Index | Multivariate ENSO |

Derived products (not "raw downloads" but critical):

| Product | Path | Produced by |
|---------|------|-------------|
| Merged SST cube | `results/combined_sst_2006_2025.nc` | `scripts/merge_sst.py` |
| Regional SST | `results/{region}_bob_sst.csv` | `scripts/extract_regional_sst.py` |
| Hobday climatology | `results/climatology/{region}_hobday.csv` | `scripts/build_hobday_climatology.py` |
| MHW catalogues | `results/mhw_catalogue/*.csv` | `scripts/detect_mhw.py` |
| Regional wind | `results/{region}_wind.csv` | `scripts/extract_regional_wind.py` |
| Heat-flux series | `results/heat_flux/csv/` | `scripts/extract_heat_flux.py` |
| Index time series CSVs | `results/climate_indices/{enso,iod,mei}/csv/` | `enso_analysis.py`, `iod_analysis.py`, `mei_analysis.py` |

---

## 2. Copernicus Daily SST

| Field | Detail |
|-------|--------|
| **Source** | Copernicus Marine Service (CMEMS) |
| **Download** | https://data.marine.copernicus.eu/ (account required) |
| **Files** | Four blocks covering 2006–2010, 2011–2015, 2016–2020, 2021–2025 |
| **Variable** | `thetao` — sea water potential temperature near surface (°C) |
| **Spatial resolution** | ~0.083° |
| **Temporal resolution** | Daily |
| **Coverage** | Bay of Bengal subset, 2006–2025 |
| **Coordinate system** | Longitude/latitude (degrees east/north) |
| **Why chosen** | Higher resolution and coastal representation than NOAA OISST (explored initially then replaced); consistency with other CMEMS variables |
| **How used** | Merged → regional means → Hobday climatology → MHW detection → spatial lifecycle maps |
| **Missing values** | Handled by xarray/NetCDF land mask and analysis scripts; coastal/land points excluded from regional means |

**Preprocessing:** `merge_sst.py` concatenates the four files; `extract_regional_sst.py` averages over North/Central/South boxes (85–95°E; 15–22 / 10–15 / 5–10°N).

---

## 3. Surface Wind (10 m)

| Field | Detail |
|-------|--------|
| **Source** | Copernicus Marine Service |
| **Download** | https://data.marine.copernicus.eu/ |
| **Local path** | `datasets/Wind_speed_data_2006_2025/` |
| **Variables** | `u10`, `v10` (m/s); speed = √(u²+v²) |
| **Temporal** | Daily, 2006–2025 |
| **Spatial box used** | **80–100°E**, 5–22°N (**differs from SST box** — known limitation) |
| **Why chosen** | Direct local driver of mixing and evaporative cooling |
| **How used** | Regional daily wind series; before/during event composites; weak/strong classification vs climatology |

---

## 4. Latent and Sensible Heat Flux

| Field | Detail |
|-------|--------|
| **Source** | Copernicus Marine Service |
| **Local path** | `datasets/heat_flux_data_2006_2025/` (yearly folders `heat_flux_2006` … `heat_flux_2025`) |
| **Variables** | Surface latent heat flux (SLHF), surface sensible heat flux (SSHF), W/m² |
| **Temporal** | Approximately weekly (forward-filled to daily in analysis where needed) |
| **Why chosen** | Quantifies air–sea heat exchange during MHWs |
| **How used** | Regional extraction; during-event anomalies; reduced-latent-heat-loss flags in master catalogue |

**Assumption:** Weekly flux can be forward-filled to daily for event alignment — documented limitation (less temporal precision than SST/wind).

---

## 5. Oceanic Niño Index (ONI)

| Field | Detail |
|-------|--------|
| **Source** | NOAA Climate Prediction Center |
| **Download** | CPC indices (e.g. https://www.cpc.ncep.noaa.gov/data/indices/) / NetCDF mirrors |
| **Local path** | `datasets/oni.nc` |
| **Variable** | ONI (°C) — 3-month running mean SST anomaly in Niño-3.4 |
| **Temporal** | Monthly |
| **Coverage** | 1950–2026 (project uses overlapping study years) |
| **Missing values** | None for study core; analysis uses event-month matching |
| **Why chosen** | International standard ENSO monitor |
| **How used** | Phase classification (±0.5 °C); lag matching to MHW start months; frequency/lag/annual/seasonal/strength analyses |

**Phase thresholds (NOAA convention, project-adopted):** El Niño ≥ +0.5; La Niña ≤ −0.5; else Neutral.

---

## 6. Dipole Mode Index (DMI)

| Field | Detail |
|-------|--------|
| **Source** | HadISST-based DMI via NOAA PSL / GCOS WGSP |
| **Download** | https://psl.noaa.gov/gcos_wgsp/Timeseries/DMI/ |
| **Local path** | `datasets/dmi.had.long.nc` |
| **Variable** | DMI (°C) |
| **Temporal** | Monthly |
| **Coverage** | 1870–2025 (**ends April 2025** in the file used here) |
| **Why chosen** | Standard IOD index (Saji et al., 1999 framework) |
| **How used** | Same six-stage pipeline as ENSO; Positive/Negative/Neutral at ±0.4 °C |

**Limitation:** 8 MHW events after DMI end date → `Unknown` IOD phase.

---

## 7. Multivariate ENSO Index (MEI v2)

| Field | Detail |
|-------|--------|
| **Source** | NOAA Physical Sciences Laboratory |
| **Download** | https://psl.noaa.gov/enso/mei/ |
| **Local path** | `datasets/meiv2.nc` |
| **Variable** | MEI (dimensionless) |
| **Temporal** | Bimonthly native product; project treats as monthly series for matching |
| **Coverage** | 1979–2026 |
| **Why chosen** | Multivariate ENSO complement to ONI |
| **How used** | Same pipeline as ONI/DMI; phases at ±0.5 (aligned with ONI for comparability — **project choice**) |

---

## 8. Climatology Datasets (Derived)

| Product | Path | Description |
|---------|------|-------------|
| Regional Hobday tables | `results/climatology/{region}_hobday.csv` | DOY, Climatology, Threshold90 |
| Spatial climatology / threshold | `results/climatology/bob_spatial_*.nc` | Grid-point fields for maps |
| Simple climatology (legacy) | `results/climatology/{region}_climatology.csv` | Pre-Hobday reference |

Climatology period = full study period **2006–2025** (project choice; Hobday often recommends ≥30 years when available).

---

## 9. Supporting / Intermediate Products Used as Inputs

These are not external downloads but are inputs to later stages:

- MHW catalogues → all climate/wind/ML labeling
- Climate index CSVs under `results/climate_indices/` → lag analyses and ML features
- Master event catalogue → publication tables and future multivariate work

---

## 10. Why Each Dataset Was Chosen (Summary)

| Need | Dataset |
|------|---------|
| Detect MHWs at daily resolution | Copernicus SST |
| Local mixing / evaporative cooling | Wind |
| Surface heat budget | SLHF / SSHF |
| Pacific teleconnection | ONI, MEI v2 |
| Indian Ocean mode | DMI |
| Fair driver comparison | All three indices + identical stats |

---

## 11. Related Documents

- Folder guide: [`../datasets/README.md`](../datasets/README.md)
- Detection method: `05_mhw_detection.md`
- Known limitations: `10_results.md`

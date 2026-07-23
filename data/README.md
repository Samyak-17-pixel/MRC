# data/ — Project Data Root

Holds **input** data for the Bay of Bengal MHW project. Derived analysis products live under `outputs/` (climate) and `src/ml/datasets/` (ML features).

## Purpose

Separate large raw NetCDF archives from code (`src/`) and regenerable results (`outputs/`).

## Contents

```
data/
└── raw/     # Copernicus SST, wind, heat flux; ONI / DMI / MEI NetCDFs
```

See [`raw/README.md`](raw/README.md) for download sources, expected filenames, and spatial-domain caveats.

## Upstream / Downstream

| Upstream | Downstream |
|----------|------------|
| External data portals (CMEMS, NOAA CPC/PSL) | `src/climate/scripts/` → `outputs/`; ML reads those outputs, not raw NetCDFs directly |

## Notes

- Raw files are **not** tracked in Git (multi-GB).
- Place downloads only under `data/raw/` as documented there.

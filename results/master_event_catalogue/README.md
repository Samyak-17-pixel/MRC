# results/master_event_catalogue/ — Per-Event Master Table

Merges **every analyzed parameter** for all 117 MHW events into one table: 117 rows × 57 columns. This is the analysis-ready dataset for multivariate work, publication tables, and event-by-event validation of ML forecasts.

Produced by: `scripts/build_master_event_catalogue.py` (reads the MHW catalogue plus all ENSO/IOD/MEI/wind/heat-flux outputs).

## Key Files

| File | Contents |
|------|----------|
| `csv/all_regions_master_event_catalogue.csv` | All 117 events, 57 columns |
| `csv/{north,central,south}_master_event_catalogue.csv` | Per-region subsets |
| `csv/{region}_01_event_sst.csv` … `_04_heat_flux.csv` | Category-split tables (metadata/SST, climate indices, wind, flux) |
| `csv/column_glossary.csv` | Definition of every column |
| `csv/regional_summary_statistics.csv` | Regional aggregates |

## Column Groups (57 total)

| Group | Examples |
|-------|----------|
| Event metadata | `Event_ID`, `Start_Date`, `End_Date`, `Duration_Days`, `Season`, `Year` |
| SST | mean/max/min SST, range, Hobday threshold, mean & max intensity |
| Climate indices | `ONI_0m…6m`, `DMI_0m…6m`, `MEI_0m…6m` + phase labels |
| Wind | 30/21/14/7-day pre-event means, during-event mean, change, climatology, anomaly, weak/strong flag |
| Heat flux | SLHF/SSHF climatology, during-event, anomaly + reduced-loss flags |

## Figures (38 unique × PNG+PDF)

| Subfolder | Contents |
|-----------|----------|
| `figures/tables/` | Rendered master summary, SST, climate-index, wind, flux tables |
| `figures/heatmaps/` | Parameter heatmaps + phase/flag heatmaps per region |
| `figures/timelines/` | Event duration bars, wind timelines |
| `figures/dashboards/` | Per-region + all-regions overview dashboards |
| `figures/top_events/` | Top-5 longest and strongest bar panels per region |

## Regional Summary (from this catalogue)

| Region | Events | Mean duration | % weak wind | % El Niño | % positive IOD | % reduced SLHF |
|--------|--------|---------------|-------------|-----------|----------------|----------------|
| North | 49 | 13.0 d | 83.7% | 26.5% | 26.5% | 34.7% |
| Central | 40 | 14.5 d | 77.5% | 25.0% | 25.0% | 55.0% |
| South | 28 | 20.5 d | 82.1% | 53.6% | 35.7% | 57.1% |

## Known Fix History

The phase/flag heatmaps were originally blank due to a pandas index-alignment bug (string `Event_ID` index assigned from an integer-indexed array → all NaN). Fixed by building the matrix with `np.column_stack` directly. Documented here so the symptom is recognizable if the pattern recurs.

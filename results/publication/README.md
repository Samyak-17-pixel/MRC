# results/publication/ — Publication-Ready Outputs

Camera-ready tables, figures, and dashboards assembled from the completed analyses. Everything here is regenerable; nothing is hand-edited.

| Producer script | Outputs |
|-----------------|---------|
| `scripts/generate_publication_outputs.py` | Tables T01–T03, figures F01–F05, dashboard D01, index CSV |
| `scripts/top5_mhw_triptych_maps.py` | `figures/07_top5_triptychs/` |

## Tables (`tables/`, each as CSV + PNG + PDF)

| ID | Contents |
|----|----------|
| `T01_regional_master_summary` | Per-region event counts, durations, intensities, driver percentages |
| `T02_driver_rankings` | ENSO vs IOD vs MEI composite scores and ranks per region |
| `T03_ml_best_models` | Best ML model per region × horizon with F1 / recall / precision / AUC |

## Figures (`figures/`, each as PNG + PDF)

| ID | Shows |
|----|-------|
| `F01_events_by_region` | 117 events split N/C/S |
| `F02_weak_wind_percent` | Weak-wind percentage per region (headline finding) |
| `F03_driver_composite_heatmap` | Driver ranking heatmap (IOD #1 everywhere) |
| `F04_annual_event_counts` | Events per year per region (2024 peak visible) |
| `F05_ml_best_f1_heatmap` | ML F1 by region × horizon |

## Top-5 Triptychs (`figures/07_top5_triptychs/`)

Before / during / after 5-day-mean SST and SST-anomaly maps for the top-5 **longest** and top-5 **strongest** events pooled across the whole Bay:

```
07_top5_triptychs/
├── longest/rank01_South_S25_2024-06-14/
│   ├── H01_triptych_sst.png/.pdf        ← absolute SST triptych
│   ├── H02_triptych_anomaly.png/.pdf    ← anomaly triptych (colorbar on the left)
│   ├── before_sst / during_sst / after_sst
│   └── ...
├── strongest/rank01_.../
└── {longest,strongest}/index.csv        ← event metadata index
```

"During" composite days are centered on the peak-intensity day. Layout: three map panels with a shared vertical colorbar placed to the **left** of the maps.

## Dashboards (`dashboards/`)

`D01_master_summary_dashboard` — one-page project overview (counts, drivers, ML).

## Index

`index/figure_table_index.csv` — machine-readable list of every publication asset with paths and captions.

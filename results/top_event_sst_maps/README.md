# results/top_event_sst_maps/ — Top-Event SST Lifecycle Maps

Spatial SST evolution (before → during → after) for the **top-10 strongest and top-10 longest** MHW events per region — 60 events, 3,329 PNG files.

Produced by: `scripts/top_event_sst_lifecycle_maps.py`.

## Structure

```
top_event_sst_maps/
├── index/                          ← CSV index of all processed events
│   ├── strongest_events_index.csv
│   └── strongest_{region}_events.csv, ...
├── strongest/{north,central,south}/rank##_EVENT_DATE/
├── longest/{north,central,south}/rank##_EVENT_DATE/
└── mosaics/{strongest,longest}/    ← regional during-composite mosaics
```

## Per-Event Contents (5 + 5 + 5 days)

| Product | Description |
|---------|-------------|
| Daily SST maps | 5 before + 5 during + 5 after, absolute SST |
| Daily anomaly maps | Same days, SST minus day-of-year climatology |
| 5-day composites | Mean over each window |
| Triptych | Before / during / after composites side by side |
| Lifecycle grid | 5×3 grid of all daily maps |
| Difference maps | during−before, after−during |

**Day selection:** *strongest* events use during-days centered on the peak-intensity day; *longest* events use during-days evenly spaced across the event.

## Map Conventions

- PlateCarree projection, cached Natural Earth 50m coastline (no downloads at run time).
- Red horizontal lines: region display boundaries (18°N, 12°N).
- Yellow dashed box: the SST averaging box of the event's region.

For the publication-styled pooled top-5 triptychs (left-side colorbar), see `results/publication/figures/07_top5_triptychs/`.

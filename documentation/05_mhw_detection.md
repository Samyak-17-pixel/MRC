# Part 5 — Marine Heatwave Detection

Complete documentation of Hobday-based detection as implemented in this project.

**Primary references:** Hobday et al. (2016); scripts `build_hobday_climatology.py`, `detect_mhw.py`.

---

## 1. Hobday et al. (2016) Framework

**Standard definition used here:**

1. Build a seasonally varying climatology and a **90th-percentile** threshold for each day of year.
2. Identify days when SST exceeds that threshold.
3. Define an MHW as a run of **≥5 consecutive** exceedance days.
4. Characterize events by duration and intensity metrics.

**Project-specific choices within that framework:**

| Choice | Value | Notes |
|--------|-------|-------|
| Climatology period | 2006–2025 (full study window) | 20 years; longer preferred when available |
| Spatial aggregation | Regional mean SST (3 boxes) | Not grid-point events |
| Intensity definition | `SST − Threshold90` | Used for Mean_Intensity and Max_Intensity |
| Gap handling between events | Consecutive-day definition as coded in `detect_mhw.py` | Re-running script is source of truth |

---

## 2. Climatology Calculation

For each region and each DOY = 1…366:

1. Collect all daily SST values whose day-of-year falls in **[DOY−5, DOY+5]** (11-day window) across all years.
2. Compute the mean of that pool → **Climatology**.

**Why the 11-day window:** Hobday-style smoothing of sampling noise for each calendar day while preserving the seasonal cycle.

**Output columns** (`results/climatology/{region}_hobday.csv`):

| Column | Units | Meaning |
|--------|-------|---------|
| `DOY` | 1–366 | Day of year |
| `Climatology` | °C | Seasonal mean SST |
| `Threshold90` | °C | Smoothed 90th percentile |

---

## 3. Threshold (Percentile) Calculation

1. From the same 11-day pool, compute the **90th percentile** → raw threshold.
2. Apply a **31-day moving average** to the raw DOY threshold series → `Threshold90`.

**Why smooth?** Reduces day-to-day jitter in the percentile curve so detection is not dominated by sampling noise.

**Why 90th percentile?** Standard Hobday Tier-1 definition for "anomalously warm" relative to the local seasonal cycle.

---

## 4. Event Detection Algorithm

```
for each day in regional SST series:
    if SST(day) > Threshold90(DOY(day)):
        mark as extreme
group consecutive extreme days into runs
keep runs with length ≥ 5 days → MHW events
```

For each event:

| Parameter | Formula / definition |
|-----------|----------------------|
| `Start_Date` | First day of the run |
| `End_Date` | Last day of the run |
| `Duration_Days` | End − Start + 1 (≥ 5) |
| `Mean_Intensity` | Mean of (SST − Threshold90) over event days |
| `Max_Intensity` | Max of (SST − Threshold90) over event days |

---

## 5. Categories

Hobday hierarchical categories (moderate / strong / severe / extreme) based on multiples of the difference between Threshold90 and climatology are **part of the general Hobday framework**. This project's primary catalogue columns focus on duration and intensity (SST − Threshold90). Category labels are not required for downstream ENSO/IOD/MEI/wind pipelines as currently implemented.

If category assignment is added later, it should follow Hobday multiples without changing the existing 117-event detection.

---

## 6. Event Catalogues

| File | Events |
|------|--------|
| `results/mhw_catalogue/north_mhw_catalogue.csv` | 49 |
| `results/mhw_catalogue/central_mhw_catalogue.csv` | 40 |
| `results/mhw_catalogue/south_mhw_catalogue.csv` | 28 |
| **Total** | **117** |

**Record events (from project results):**

| Record | Region | Start | Value |
|--------|--------|-------|-------|
| Longest | South | 2024-06-14 | 81 days |
| Strongest | South | 2024-04-14 | 0.943 °C Max_Intensity |

Downstream consumers: all `enso_*` / `iod_*` / `mei_*` lag scripts, wind/heat-flux analyses, master catalogue, ML onset labels.

---

## 7. Assumptions and Limitations

1. Regional-mean SST can miss sub-box spatial structure.
2. 20-year baseline may embed a warming trend into the climatology (detrended series exist for sensitivity: `*_bob_sst_detrended.csv` — not the primary detection path).
3. Intensity relative to Threshold90 differs from anomaly relative to climatological mean (used in some map products).

---

## 8. How to Reproduce

```bash
.venv/bin/python scripts/merge_sst.py
.venv/bin/python scripts/extract_regional_sst.py
.venv/bin/python scripts/build_hobday_climatology.py
.venv/bin/python scripts/detect_mhw.py
.venv/bin/python scripts/generate_mhw_reports.py
```

Do **not** change Hobday parameters unless explicitly instructed by the project lead.

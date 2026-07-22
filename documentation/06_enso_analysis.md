# Part 6 — ENSO (ONI) Analysis

Exhaustive documentation of the ENSO–MHW pipeline. Sibling IOD/MEI pipelines reuse this statistical design.

**Scripts:** `enso_lag_analysis.py`, `enso_frequency_analysis.py`, `enso_statistics.py`, `enso_annual_analysis.py`, `enso_seasonal_analysis.py`, `enso_strength_analysis.py`, `enso_mhw_analysis.py`  
**Outputs:** `results/enso_lag/`, `enso_frequency/`, `enso_statistics/`, `enso_annual/`, `enso_seasonal/`, `enso_strength/`, `enso_analysis/`  
**Index source:** `datasets/oni.nc` → `results/climate_indices/enso/`

---

## 1. Data Preprocessing

### 1.1 How ONI was read

- Load `datasets/oni.nc` (or derived CSV after characterization).
- Extract monthly ONI values with a time coordinate.
- Characterization script writes `results/climate_indices/enso/csv/oni_timeseries.csv` (columns include time and ONI).

### 1.2 How dates were matched

- Each MHW has `Start_Date` from the catalogue.
- The event is tagged with the **ONI of the calendar month containing `Start_Date`** (`ONI_0m`).
- Lagged values use the ONI **k months before** that month (`ONI_1m` … `ONI_6m`).

### 1.3 How monthly data were handled

- ONI is monthly; MHWs are daily events.
- **Project rule:** one monthly ONI value applies to the whole start month (no daily interpolation of ONI).
- This is standard for climate-mode attribution and is applied identically for DMI and MEI.

---

## 2. Event Matching

For every event in each regional catalogue, produce a row with:

`Start_Date, End_Date, Duration_Days, Mean_Intensity, Max_Intensity, ONI_0m, ONI_1m, ONI_2m, ONI_3m, ONI_6m, ENSO_Phase`

| Field | Meaning |
|-------|---------|
| During event (`ONI_0m`) | ONI in the start month |
| 1-month lag | ONI one month before start month |
| 2-month lag | Two months before |
| 3-month lag | Three months before |
| 6-month lag | Six months before |

**Why these lags?** Capture delayed teleconnections from the Pacific to the BoB without overfitting a dense lag scan. The set {0,1,2,3,6} is a **project-specific choice**, reused for IOD and MEI.

Example output: `results/enso_lag/north_enso_lag.csv`.

---

## 3. Phase Classification

| Phase | Threshold | Reference basis |
|-------|-----------|-----------------|
| **El Niño** | ONI ≥ +0.5 °C | NOAA CPC ONI operational thresholds |
| **La Niña** | ONI ≤ −0.5 °C | Same |
| **Neutral** | −0.5 < ONI < +0.5 | Same |

`ENSO_Phase` in lag tables uses the **0-month** ONI (start-month phase).

**Why ±0.5?** Standard CPC convention for El Niño / La Niña monitoring; adopted here so results are comparable to literature.

---

## 4. Frequency Analysis

**Purpose:** Test whether MHW events are evenly distributed across the three ENSO phases.

**Method:**

1. Count events in El Niño / Neutral / La Niña.
2. Chi-square goodness-of-fit against **equal expected counts** (1/3 each) — project assumption.
3. Report p-value and **Cramer's V** (effect size).

**Outputs:** `results/enso_frequency/{region}_frequency.csv/png`, `summary.csv`.

**Results:**

| Region | El Niño | Neutral | La Niña | χ² p | Cramer's V | Significant? |
|--------|---------|---------|---------|------|------------|--------------|
| North | 13 | 24 | 12 | 0.066 | 0.235 | No (marginal) |
| Central | 10 | 20 | 10 | 0.082 | 0.250 | No |
| **South** | **15** | **10** | **3** | **0.020** | **0.373** | **Yes** |

**Interpretation:** South BoB MHWs are enriched during El Niño (54% of South events). North/Central show Neutral-heavy counts but not significant under the equal-expectation test.

---

## 5. Lag Analysis

**Purpose:** Identify delayed associations between ONI and event duration / intensity.

**Method:** Pearson correlation between each lag series (`ONI_km`) and `Duration_Days` / intensity metrics; report best lag by |r| or by design summary tables.

**Results (duration):**

| Region | Best lag | r | p | Significant? |
|--------|----------|---|---|--------------|
| North | 6 mo | 0.135 | 0.354 | No |
| Central | 6 mo | 0.290 | 0.070 | Marginal |
| **South** | **6 mo** | **0.433** | **0.021** | **Yes** |

**Interpretation:** Significant 6-month teleconnection for South duration only.

---

## 6. Statistical Analysis (Phase Comparisons)

### 6.1 Descriptive statistics

Per phase: mean/median duration, mean/max intensity, counts.

### 6.2 Kruskal–Wallis

**Why:** Non-parametric comparison of duration/intensity across three phases (small n, possible non-normality).

**Result:** Not significant for duration/intensity by phase in North, Central, or South (as summarized in `PROJECT.md` / `ALL_PROJECT_RESULTS.md`).

### 6.3 Mann–Whitney U

**Why:** Pairwise non-parametric contrasts between phases when needed as follow-up.

### 6.4 Chi-square + Cramer's V

Used in frequency (and season×phase) analyses — see §4 and §8.

---

## 7. Annual Analysis

**Purpose:** Relate year-to-year MHW activity to annual mean ONI.

**Method:** Aggregate events by year; correlate annual counts / mean duration / intensity with annual ONI (Pearson).

**Result:** Weak / non-significant annual ONI correlations in all regions (project summary).

**Outputs:** `results/enso_annual/`.

---

## 8. Seasonal Analysis

**Purpose:** Test whether ENSO phase composition of MHWs depends on season (Winter / Pre-Monsoon / SW Monsoon / Post-Monsoon — project calendar definition).

**Method:** Contingency table season × ENSO phase; chi-square test of independence.

**Result:** Not significant for ENSO in any region (project summary).

**Outputs:** `results/enso_seasonal/`.

---

## 9. Strength Analysis

**Purpose:** Do stronger El Niño / La Niña episodes coincide with longer or more intense MHWs?

**Method:** Classify ONI magnitude into strength bins; compare event properties across bins (non-parametric tests / descriptive tables).

**Outputs:** `results/enso_strength/`.

---

## 10. Remaining Statistical / Implementation Issues

| Issue | Status |
|-------|--------|
| ENSO spatial composites (`enso_spatial_analysis.py`) | Started; no figure outputs yet |
| Per-event plot folders under `enso_analysis/*_event_plots/` | Empty (deferred) |
| `enso_final_pipeline.py` | Scaffold; not a completed runner |
| Equal-expectation frequency null | Conservative vs climatological phase weighting — document if revisiting |
| Multiple testing across many lags/regions | Not formally corrected; interpret p-values cautiously |

---

## 11. Scientific Conclusion (ENSO)

ENSO is **regionally selective**: significant for **South BoB** (El Niño enrichment + 6-month duration lag). It is **not** the top large-scale driver overall once IOD is included (see `07_iod_analysis.md` and `10_results.md`).

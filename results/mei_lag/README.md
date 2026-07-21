# MEI v2 — MHW Analysis Outputs

This README documents **all six `mei_*` output folders** under `results/`. (There is no `mei_analysis/` folder — the MEI pipeline was run via the orchestrator `scripts/mei_pipeline.py`, and MEI index characterization lives in `results/climate_indices/mei/`.)

The MEI pipeline mirrors the ENSO and IOD pipelines exactly. Full methodology: [`documentation/08_mei_analysis.md`](../../documentation/08_mei_analysis.md).

---

## Pipeline Stages and Folders

| Folder | Script | Question answered |
|--------|--------|-------------------|
| `mei_lag/` (this folder) | `mei_lag_analysis.py` | MEI at 0/1/2/3/6-month lags per event; lag correlations |
| `../mei_frequency/` | `mei_frequency_analysis.py` | Event distribution across MEI phases |
| `../mei_statistics/` | `mei_statistics.py` | Duration/intensity by phase |
| `../mei_annual/` | `mei_annual_analysis.py` | Annual counts vs annual MEI |
| `../mei_seasonal/` | `mei_seasonal_analysis.py` | Season × phase chi-square |
| `../mei_strength/` | `mei_strength_analysis.py` | Event properties vs MEI strength |

Run everything with: `.venv/bin/python scripts/mei_pipeline.py`

## Phase Classification (same thresholds as ONI for comparability)

| Phase | Criterion |
|-------|-----------|
| El Niño | MEI ≥ +0.5 |
| La Niña | MEI ≤ −0.5 |
| Neutral | −0.5 < MEI < +0.5 |

## Headline MEI Results

| Region | Phase frequency χ² p | Dominant phase | Seasonal χ² p |
|--------|---------------------|----------------|---------------|
| North | **0.001 (SIG)** | **57% La Niña** | 0.302 (NS) |
| Central | **0.002 (SIG)** | **60% La Niña** | **0.0008 (SIG)** |
| South | 0.331 (NS) | 46% El Niño | 0.212 (NS) |

Lag correlations: all NS (best: South 6 mo, r = 0.292, p = 0.131). Kruskal–Wallis by phase: all NS.

**Conclusion:** MEI reveals a **La Niña enrichment in North and Central BoB** — opposite in sign to the ONI-based El Niño enrichment in the South. Central BoB additionally shows a significant seasonal dependence of MEI phase during MHWs. Because MEI blends five atmosphere–ocean variables, this suggests North/Central MHWs co-occur with the atmospheric side of La Niña conditions (weakened winds), consistent with the wind-driver headline finding.

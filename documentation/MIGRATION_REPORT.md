# ML Migration Report

**Branch:** `docs-and-ml-reorg`  
**Date:** 2026-07-22  
**Scope:** Reorganize machine-learning code only. Climate-analysis paths (`datasets/`, `scripts/`, `plotting/`, `results/`) were **not** moved.

---

## 1. Why

The original `mhw_ml/` layout mixed all stages under a single `scripts/` folder. The project required a research-style separation (`preprocessing`, `training`, `evaluation`, …) while **preserving backward compatibility** and avoiding absolute machine-specific paths in config.

---

## 2. What Moved

| From (legacy) | To (canonical) | Notes |
|---------------|----------------|-------|
| `mhw_ml/scripts/common.py` | `machine_learning/common.py` | `ML_ROOT` = package root; `data/` → `datasets/` |
| `mhw_ml/scripts/01_build_dataset.py` | `machine_learning/preprocessing/01_build_dataset.py` | Feature + label build |
| `mhw_ml/scripts/02_train_baselines.py` | `machine_learning/training/02_train_baselines.py` | |
| `mhw_ml/scripts/03_train_models.py` | `machine_learning/training/03_train_models.py` | |
| `mhw_ml/scripts/04_evaluate_models.py` | `machine_learning/evaluation/04_evaluate_models.py` | |
| `mhw_ml/scripts/05_explain_models.py` | `machine_learning/evaluation/05_explain_models.py` | |
| `mhw_ml/scripts/06_predict_current.py` | `machine_learning/experiments/06_predict_current.py` | |
| `mhw_ml/scripts/run_pipeline.py` | `machine_learning/run_pipeline.py` | Updated step paths |
| `mhw_ml/data/` | `machine_learning/datasets/` | Renamed for clarity |
| `mhw_ml/models/` | `machine_learning/models/` | Copied (joblib binaries may be gitignored) |
| `mhw_ml/outputs/` | `machine_learning/outputs/` | Copied |
| `mhw_ml/config/model_config.yaml` | `machine_learning/config/model_config.yaml` | Relative `results_relative: results` |
| `mhw_ml/ML_EXECUTION.md` | `machine_learning/ML_EXECUTION.md` | Retained; prefer `documentation/12_machine_learning.md` |

New documentation-only folders:

- `machine_learning/feature_engineering/README.md` — feature design notes (logic remains in step 01)
- `machine_learning/visualizations/README.md` — points to `outputs/figures` and `outputs/shap`

---

## 3. What Did Not Change

- Hobday detection, region boxes, climate scripts, results CSVs/figures
- Model hyperparameters and reported metrics (no retrain required for migration)
- Scientific conclusions in `ALL_PROJECT_RESULTS.md`

---

## 4. Compatibility Maintenance

`mhw_ml/scripts/*.py` are **thin wrappers** using `runpy.run_path(...)` to execute the canonical files under `machine_learning/`.

`mhw_ml/README.md` documents the mapping.

Preferred commands:

```bash
.venv/bin/python machine_learning/run_pipeline.py
```

Legacy (still works):

```bash
.venv/bin/python mhw_ml/scripts/run_pipeline.py
```

---

## 5. Path Portability Fix

`model_config.yaml` no longer requires absolute `/home/...` paths. `common.cfg_path("results")` resolves `results/` relative to the repository root.

---

## 6. How to Verify

```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'machine_learning'); from common import cfg_path; print(cfg_path('results'))"
.venv/bin/python machine_learning/experiments/06_predict_current.py
.venv/bin/python mhw_ml/scripts/06_predict_current.py   # wrapper smoke test
```

Full retrain (optional; not run as part of this documentation migration unless requested):

```bash
.venv/bin/python machine_learning/run_pipeline.py
```

---

## 7. Follow-ups (Optional)

- Remove duplicate large artifacts under `mhw_ml/models` and `mhw_ml/outputs` once teams only use `machine_learning/` (keep wrappers).
- Update any external notes that cite only `mhw_ml/`.
- Point `PROJECT.md` Phase 12 path to `machine_learning/` (documentation update only).

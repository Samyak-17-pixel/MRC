# mhw_ml/ — Legacy Compatibility Layer

> **Canonical ML code now lives in [`../machine_learning/`](../machine_learning/).**

This folder is retained so older commands such as:

```bash
.venv/bin/python mhw_ml/scripts/run_pipeline.py
```

still work. Each script under `scripts/` is a thin wrapper that executes the matching file in `machine_learning/`.

| Old path | New path |
|----------|----------|
| `mhw_ml/scripts/01_build_dataset.py` | `machine_learning/preprocessing/01_build_dataset.py` |
| `mhw_ml/scripts/02_train_baselines.py` | `machine_learning/training/02_train_baselines.py` |
| `mhw_ml/scripts/03_train_models.py` | `machine_learning/training/03_train_models.py` |
| `mhw_ml/scripts/04_evaluate_models.py` | `machine_learning/evaluation/04_evaluate_models.py` |
| `mhw_ml/scripts/05_explain_models.py` | `machine_learning/evaluation/05_explain_models.py` |
| `mhw_ml/scripts/06_predict_current.py` | `machine_learning/experiments/06_predict_current.py` |
| `mhw_ml/data/` | `machine_learning/datasets/` |
| `mhw_ml/models/`, `outputs/`, `config/` | same names under `machine_learning/` |

Do not add new features here — edit `machine_learning/` instead.

See [`../documentation/MIGRATION_REPORT.md`](../documentation/MIGRATION_REPORT.md).

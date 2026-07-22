# visualizations/

ML figures are written by evaluation scripts to:

| Path | Contents |
|------|----------|
| `../outputs/figures/` | ROC, PR, confusion matrices |
| `../outputs/shap/` | Feature importance / SHAP plots |

This folder exists so the module layout matches the documented research structure.
Generated image files live under `outputs/` (regenerable; large binaries may be gitignored).

Reproduce:

```bash
.venv/bin/python machine_learning/evaluation/04_evaluate_models.py
.venv/bin/python machine_learning/evaluation/05_explain_models.py
```

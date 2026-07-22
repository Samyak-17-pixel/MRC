# training/

| Script | Role |
|--------|------|
| `02_train_baselines.py` | Climatology, persistence, logistic regression baselines |
| `03_train_models.py` | XGBoost, Random Forest, Gradient Boosting per region × horizon |

**Outputs:** `../models/baselines/`, `../models/{north,central,south}/`

Hyperparameters: `../config/model_config.yaml`

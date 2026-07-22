# preprocessing/

Builds the daily supervised learning table.

| Script | Role |
|--------|------|
| `01_build_dataset.py` | Join SST, Hobday threshold, wind, heat flux, climate indices; engineer rolling features; assign `onset_3d/7d/14d` labels; write `../datasets/processed/` and `../datasets/splits/` |

**Inputs:** `results/{region}_bob_sst.csv`, `results/climatology/{region}_hobday.csv`, `results/{region}_wind.csv`, `results/heat_flux/csv/`, climate index CSVs, MHW catalogues.  
**Outputs:** `../datasets/processed/{region}_daily_features.csv`, `combined_daily_features.csv`, `../datasets/splits/{train,val,test}.csv`

```bash
.venv/bin/python machine_learning/preprocessing/01_build_dataset.py
```

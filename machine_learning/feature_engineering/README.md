# feature_engineering/

Feature construction for the ML module is implemented in
`../preprocessing/01_build_dataset.py` (kept in one script to avoid
duplicating the daily join logic).

This folder documents **what** is engineered and **why**.

## Feature Groups

| Group | Examples | Motivation |
|-------|----------|------------|
| SST state | Intensity, Distance_to_Threshold, Consecutive_Hot_Days | Hobday exceedance proximity |
| SST dynamics | Rolling means/std, 7/14-day SST change | Build-up / trend |
| Wind | Wind anomaly, rolling wind | 78–84% weak-wind finding |
| Heat flux | SLHF/SSHF anomalies | Reduced cooling during events |
| Climate indices | ONI/DMI/MEI at 0–6 month lags | Driver ranking (IOD #1) |
| Calendar | DOY_sin/cos | Seasonality without leakage |

## Rules

- Rolling windows are **backward-looking only** (no future leakage into features).
- Climate indices are monthly, forward-filled to daily.
- Labels `onset_Hd` may look ahead H days (supervised target only).

See `documentation/12_machine_learning.md` for the full feature list and parameters.

"""Shared utilities for MHW ML pipeline (machine_learning package)."""

from pathlib import Path
import yaml
import json
import numpy as np
import pandas as pd

ML_ROOT = Path(__file__).resolve().parent
WS_ROOT = ML_ROOT.parents[1]  # src/ml → repo root


def load_config():
    with open(ML_ROOT / "config" / "model_config.yaml") as f:
        return yaml.safe_load(f)


def cfg_path(key):
    """Resolve configured paths; prefer relative keys, fall back to WS_ROOT/results."""
    c = load_config()
    paths = c.get("paths", {})
    if key == "workspace":
        return WS_ROOT
    if key == "results":
        rel = paths.get("results_relative", "outputs")
        p = Path(rel)
        if not p.is_absolute():
            return (WS_ROOT / p).resolve()
        return Path(paths.get("results", WS_ROOT / "outputs"))
    return Path(paths[key])


def season(month):
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Pre-Monsoon"
    if month in [6, 7, 8, 9]:
        return "SW Monsoon"
    return "Post-Monsoon"


def load_climate_monthly():
    """Load ONI, DMI, MEI and return daily forward-filled series."""
    res = cfg_path("results")
    oni = pd.read_csv(res / "climate_indices/enso/csv/oni_timeseries.csv")
    dmi = pd.read_csv(res / "climate_indices/iod/csv/dmi_timeseries.csv")
    mei = pd.read_csv(res / "climate_indices/mei/csv/mei_timeseries.csv")

    for df in [oni, dmi, mei]:
        df["time"] = pd.to_datetime(df["time"])

    climate = oni.rename(columns={"time": "Date", "ONI": "ONI_0m"})
    climate = climate.merge(
        dmi.rename(columns={"time": "Date", "DMI": "DMI_0m"})[["Date", "DMI_0m"]],
        on="Date", how="outer",
    )
    climate = climate.merge(
        mei.rename(columns={"time": "Date", "MEI": "MEI_0m"})[["Date", "MEI_0m"]],
        on="Date", how="outer",
    )
    climate = climate.sort_values("Date")
    return climate


def expand_climate_to_daily(daily_dates, climate_monthly, lag_months):
    """Forward-fill monthly climate to daily and add lag columns."""
    daily = pd.DataFrame({"Date": pd.to_datetime(daily_dates)})
    daily["YearMonth"] = daily["Date"].dt.to_period("M").dt.to_timestamp()

    cm = climate_monthly.copy()
    cm["YearMonth"] = cm["Date"].dt.to_period("M").dt.to_timestamp()
    cm = cm.drop(columns=["Date"], errors="ignore")

    merged = daily.merge(cm, on="YearMonth", how="left")
    for col in ["ONI_0m", "DMI_0m", "MEI_0m"]:
        if col in merged.columns:
            merged[col] = merged[col].ffill().bfill()

    cm_sorted = climate_monthly.set_index("Date").sort_index()
    for m in lag_months:
        if m == 0:
            continue
        shifted = cm_sorted.shift(m)
        shifted.index = shifted.index + pd.DateOffset(months=m)
        shifted = shifted.reset_index().rename(columns={"Date": "YearMonth"})
        shifted["YearMonth"] = shifted["YearMonth"].dt.to_period("M").dt.to_timestamp()
        for col in ["ONI_0m", "DMI_0m", "MEI_0m"]:
            if col in shifted.columns:
                merged = merged.merge(
                    shifted[["YearMonth", col]].rename(columns={col: f"{col.replace('_0m','')}_{m}m"}),
                    on="YearMonth", how="left",
                )
    merged = merged.drop(columns=["YearMonth"], errors="ignore")
    return merged


def detect_event_starts(region):
    """Return set of MHW event start dates from catalogue."""
    cat = pd.read_csv(
        cfg_path("results") / "mhw" / "catalogue" / f"{region}_mhw_catalogue.csv"
    )
    cat["Start_Date"] = pd.to_datetime(cat["Start_Date"])
    return set(cat["Start_Date"].dt.normalize())


def assign_onset_labels(df, horizons, event_starts):
    """Label: will a new MHW event START within next H days?"""
    dates = df["Date"].dt.normalize()
    for h in horizons:
        col = f"onset_{h}d"
        labels = []
        for d in dates:
            future = pd.date_range(d + pd.Timedelta(days=1), d + pd.Timedelta(days=h), freq="D")
            labels.append(int(any(fd in event_starts for fd in future)))
        df[col] = labels
    return df


def year_split_mask(dates, year_range):
    years = dates.dt.year
    return (years >= year_range[0]) & (years <= year_range[1])


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)


FEATURE_COLS_EXCLUDE = {
    "Date", "Region", "Year", "Month", "DOY", "Season",
    "in_mhw", "event_start", "event_end",
}
LABEL_PREFIX = "onset_"


def get_feature_columns(df):
    return [
        c for c in df.columns
        if c not in FEATURE_COLS_EXCLUDE
        and not c.startswith(LABEL_PREFIX)
        and df[c].dtype in [np.float64, np.float32, np.int64, np.int32, np.bool_]
    ]


def load_region_df(region):
    path = ML_ROOT / "datasets" / "processed" / f"{region}_daily_features.csv"
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def ensure_dirs():
    for sub in [
        "data/raw/processed", "data/raw/splits",
        "models/baselines", "models/north", "models/central", "models/south",
        "outputs/metrics", "outputs/figures", "outputs/shap", "outputs/forecasts",
        "visualizations", "logs",
    ]:
        (ML_ROOT / sub).mkdir(parents=True, exist_ok=True)

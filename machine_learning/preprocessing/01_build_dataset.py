#!/usr/bin/env python3
"""
Step 01 — Build daily ML feature dataset per region.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import (
    ML_ROOT, load_config, cfg_path, season,
    load_climate_monthly, expand_climate_to_daily,
    detect_event_starts, assign_onset_labels, ensure_dirs,
)

ensure_dirs()


def build_region_dataset(region, config):
    res = cfg_path("results")
    windows = config["features"]["rolling_windows"]
    horizons = config["task"]["horizons_days"]
    lag_months = config["features"]["climate_lag_months"]

    # SST + Hobday threshold
    sst = pd.read_csv(res / f"{region}_bob_sst.csv")
    sst["Date"] = pd.to_datetime(sst["Date"])
    hob = pd.read_csv(res / f"climatology/{region}_hobday.csv")
    df = sst.copy()
    df["DOY"] = df["Date"].dt.dayofyear
    df = df[df["DOY"] != 366]
    df = df.merge(hob[["DOY", "Climatology", "Threshold90"]], on="DOY", how="left")
    df["Intensity"] = df["SST"] - df["Threshold90"]
    df["SST_Anomaly"] = df["SST"] - df["Climatology"]
    df["Above_Threshold"] = (df["Intensity"] > 0).astype(int)
    df["Distance_to_Threshold"] = df["Intensity"]

    # Consecutive hot days
    streak = []
    count = 0
    for hot in df["Above_Threshold"]:
        count = count + 1 if hot else 0
        streak.append(count)
    df["Consecutive_Hot_Days"] = streak

    # Rolling SST features
    for w in windows:
        df[f"SST_mean_{w}d"] = df["SST"].rolling(w, min_periods=1).mean()
        df[f"SST_std_{w}d"] = df["SST"].rolling(w, min_periods=1).std().fillna(0)
        df[f"Intensity_mean_{w}d"] = df["Intensity"].rolling(w, min_periods=1).mean()
    df["SST_change_7d"] = df["SST"] - df["SST"].shift(7)
    df["SST_change_14d"] = df["SST"] - df["SST"].shift(14)

    # Wind
    wind = pd.read_csv(res / f"{region}_wind.csv")
    wind["Date"] = pd.to_datetime(wind["Date"]).dt.normalize()
    wind = wind.groupby("Date", as_index=False)["WindSpeed"].mean()
    wind = wind.rename(columns={"WindSpeed": "Wind"})
    df = df.merge(wind, on="Date", how="left")
    wind_clim = wind.copy()
    wind_clim["DOY"] = wind_clim["Date"].dt.dayofyear
    wind_doy = wind_clim.groupby("DOY")["Wind"].mean().reset_index(name="Wind_Climatology")
    df = df.merge(wind_doy, on="DOY", how="left")
    df["Wind_Anomaly"] = df["Wind"] - df["Wind_Climatology"]
    for w in windows:
        df[f"Wind_mean_{w}d"] = df["Wind"].rolling(w, min_periods=1).mean()
        df[f"Wind_anom_mean_{w}d"] = df["Wind_Anomaly"].rolling(w, min_periods=1).mean()

    # Heat flux (weekly → forward-fill to daily)
    for flux, col in [("slhf", "SLHF"), ("sshf", "SSHF")]:
        fp = res / f"heat_flux/csv/{region}_{flux}.csv"
        if fp.exists():
            flux_df = pd.read_csv(fp)
            flux_df["Date"] = pd.to_datetime(flux_df["Date"])
            flux_df = flux_df.rename(columns={"HeatFlux": col})
            df = df.merge(flux_df, on="Date", how="left")
            df[col] = df[col].ffill().bfill()
            flux_clim = df.groupby("DOY")[col].transform("mean")
            df[f"{col}_Anomaly"] = df[col] - flux_clim
            for w in windows:
                df[f"{col}_anom_mean_{w}d"] = df[f"{col}_Anomaly"].rolling(w, min_periods=1).mean()

    # Climate indices (monthly → daily)
    climate = load_climate_monthly()
    climate_daily = expand_climate_to_daily(df["Date"], climate, lag_months)
    df = df.merge(climate_daily, on="Date", how="left")

    # Calendar
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Season"] = df["Month"].apply(season)
    df["DOY_sin"] = np.sin(2 * np.pi * df["DOY"] / 365.25)
    df["DOY_cos"] = np.cos(2 * np.pi * df["DOY"] / 365.25)

    # In-MHW flag from catalogue
    events = pd.read_csv(res / f"mhw_catalogue/{region}_mhw_catalogue.csv")
    events["Start_Date"] = pd.to_datetime(events["Start_Date"])
    events["End_Date"] = pd.to_datetime(events["End_Date"])
    df["in_mhw"] = 0
    for _, ev in events.iterrows():
        mask = (df["Date"] >= ev["Start_Date"]) & (df["Date"] <= ev["End_Date"])
        df.loc[mask, "in_mhw"] = 1

    # Onset labels
    starts = detect_event_starts(region)
    df = assign_onset_labels(df, horizons, starts)

    df["Region"] = region
    df = df.dropna(subset=["SST", "Wind"]).reset_index(drop=True)
    return df


def main():
    config = load_config()
    regions = config["regions"]
    print("=" * 72)
    print("STEP 01: BUILD ML DATASET")
    print("=" * 72)

    frames = []
    for region in regions:
        print(f"\n  Building {region}...")
        df = build_region_dataset(region, config)
        out = ML_ROOT / "datasets" / "processed" / f"{region}_daily_features.csv"
        df.to_csv(out, index=False)
        print(f"    Rows: {len(df)}")
        for h in config["task"]["horizons_days"]:
            col = f"onset_{h}d"
            print(f"    {col}: {df[col].sum()} positive ({100*df[col].mean():.2f}%)")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(ML_ROOT / "datasets" / "processed" / "combined_daily_features.csv", index=False)

    # Chronological splits (combined)
    splits = config["splits"]
    for name, yrs in [("train", splits["train_years"]), ("val", splits["val_years"]), ("test", splits["test_years"])]:
        mask = (combined["Year"] >= yrs[0]) & (combined["Year"] <= yrs[1])
        combined.loc[mask].to_csv(ML_ROOT / "datasets" / "splits" / f"{name}.csv", index=False)
        print(f"\n  Split {name}: {mask.sum()} rows ({yrs[0]}–{yrs[1]})")

    print("\n" + "=" * 72)
    print("DATASET BUILD COMPLETE")
    print(f"  Output: {ML_ROOT / 'datasets' / 'processed'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

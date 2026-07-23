#!/usr/bin/env python3
"""
Step 06 — Forecast for the latest available date + year verification.

IMPORTANT:
  This does NOT count how many MHWs occurred in a year.
  Catalogue detection (Hobday) found 13 starts in 2025.
  The operational forecast scores ONLY the latest day in the feature
  table (currently 2025-12-31), asking: will a NEW event START in the
  next 3/7/14 days from that date?

  On 2025-12-31, SST is well below the Hobday threshold and the last
  2025 event had already ended (North: 2025-11-03), so near-zero
  onset probability is expected — it is not a claim of "0 events in 2025".
"""

import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import (
    ML_ROOT,
    WS_ROOT,
    load_config,
    ensure_dirs,
    load_region_df,
    get_feature_columns,
)

ensure_dirs()


def logistic_feature_cols(df: pd.DataFrame) -> list[str]:
    """Match training/02_train_baselines.py feature selection for logistic models."""
    return [
        c
        for c in get_feature_columns(df)
        if any(
            k in c
            for k in [
                "SST",
                "Intensity",
                "Wind",
                "DMI",
                "ONI",
                "MEI",
                "Consecutive",
                "DOY_sin",
            ]
        )
    ][:25]


def load_predictor(region: str, horizon: int, model_name: str, df: pd.DataFrame):
    """Return (model, feature_list, path_stem). Handles ML bundles and baseline Pipelines."""
    label = f"onset_{horizon}d"
    if model_name == "logistic_regression":
        path = ML_ROOT / "models" / "baselines" / f"{region}_{label}_logistic.joblib"
        if not path.exists():
            raise FileNotFoundError(path)
        obj = joblib.load(path)
        if isinstance(obj, dict):
            return obj["model"], obj["features"], path.stem
        return obj, logistic_feature_cols(df), path.stem

    path = ML_ROOT / "models" / region / f"{label}_{model_name}.joblib"
    if not path.exists():
        raise FileNotFoundError(path)
    bundle = joblib.load(path)
    return bundle["model"], bundle["features"], path.stem


def best_model_name(region: str, horizon: int, fallback: str) -> str:
    path = ML_ROOT / "outputs" / "metrics" / "best_models.csv"
    if not path.exists():
        return fallback
    best = pd.read_csv(path)
    hit = best[(best["region"] == region) & (best["horizon"] == horizon)]
    if hit.empty:
        return fallback
    return str(hit.iloc[0]["model"])


def predict_proba_row(model, feats: list[str], row: pd.Series) -> float:
    X = pd.DataFrame([row[feats].fillna(0).to_dict()], columns=feats)
    if hasattr(model, "predict_proba"):
        return float(model.predict_proba(X)[0, 1])
    return float(model.predict(X)[0])


def alert_level(prob: float) -> str:
    if prob >= 0.5:
        return "HIGH"
    if prob >= 0.25:
        return "MODERATE"
    return "LOW"


def catalogue_starts(year: int) -> pd.DataFrame:
    rows = []
    for region in ["north", "central", "south"]:
        cat = pd.read_csv(WS_ROOT / "outputs" / "mhw" / "catalogue" / f"{region}_mhw_catalogue.csv")
        cat["Start_Date"] = pd.to_datetime(cat["Start_Date"])
        cat["End_Date"] = pd.to_datetime(cat["End_Date"])
        sub = cat[cat["Start_Date"].dt.year == year].copy()
        sub.insert(0, "Region", region)
        rows.append(sub)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def verify_year(year: int, config: dict, alert_thresh: float = 0.25) -> pd.DataFrame:
    """
    For each catalogue event starting in `year`, check whether the best model
    would have raised an alert in the pre-onset window (days that should be
    labeled onset_Hd = 1).
    """
    events = catalogue_starts(year)
    records = []
    primary = config["models"]["primary"]

    for _, ev in events.iterrows():
        region = ev["Region"]
        start = ev["Start_Date"]
        df = load_region_df(region)
        for h in config["task"]["horizons_days"]:
            model_name = best_model_name(region, h, primary)
            model, feats, stem = load_predictor(region, h, model_name, df)
            pre = df[(df["Date"] >= start - pd.Timedelta(days=h)) & (df["Date"] < start)]
            if pre.empty:
                max_p = np.nan
                hit = False
            else:
                probs = model.predict_proba(pre[feats].fillna(0).astype(float))[:, 1]
                max_p = float(probs.max())
                hit = bool(max_p >= alert_thresh)
            records.append(
                {
                    "Region": region.title(),
                    "Start_Date": start.strftime("%Y-%m-%d"),
                    "Duration_Days": int(ev["Duration_Days"]),
                    "Max_Intensity": round(float(ev["Max_Intensity"]), 3),
                    "Horizon_Days": h,
                    "Model": stem,
                    "Max_P_In_PreWindow": None if np.isnan(max_p) else round(max_p, 4),
                    "Alert_Hit": int(hit),
                }
            )
    return pd.DataFrame(records)


def main():
    config = load_config()
    horizons = config["task"]["horizons_days"]
    regions = config["regions"]
    primary = config["models"]["primary"]

    print("=" * 72)
    print("STEP 06: CURRENT FORECAST (single-day onset risk)")
    print("=" * 72)
    print(
        "NOTE: This scores ONLY the latest feature day — not the annual event count.\n"
        "      Hobday detection and this forecast answer different questions.\n"
    )

    forecasts = []
    latest_year = None

    for region in regions:
        df = load_region_df(region)
        latest = df.iloc[-1]
        latest_year = int(pd.Timestamp(latest["Date"]).year)

        for h in horizons:
            model_name = best_model_name(region, h, primary)
            model, feats, stem = load_predictor(region, h, model_name, df)
            prob = predict_proba_row(model, feats, latest)
            alert = alert_level(prob)

            forecasts.append(
                {
                    "Region": region.title(),
                    "Forecast_Date": pd.Timestamp(latest["Date"]).strftime("%Y-%m-%d"),
                    "Horizon_Days": h,
                    "P_MHW_Onset": round(prob, 4),
                    "Alert_Level": alert,
                    "Current_SST_C": round(float(latest["SST"]), 3),
                    "Current_Intensity_C": round(float(latest["Intensity"]), 3),
                    "Current_Wind_ms": round(float(latest["Wind"]), 3),
                    "In_MHW_Now": int(latest["in_mhw"]),
                    "Model": stem,
                }
            )
            print(
                f"  {region} {h}d: P={prob:.3f} ({alert})  "
                f"SST={latest['SST']:.2f}  Intensity={latest['Intensity']:.2f}  "
                f"model={stem}"
            )

    fc_df = pd.DataFrame(forecasts)
    out = ML_ROOT / "outputs" / "forecasts"
    fc_df.to_csv(out / "latest_forecast.csv", index=False)
    stamp = datetime.now().strftime("%Y%m%d")
    fc_df.to_csv(out / f"forecast_{stamp}.csv", index=False)

    print("\n" + "=" * 72)
    print(f"YEAR VERIFICATION vs HOBDAY CATALOGUE ({latest_year})")
    print("=" * 72)
    starts = catalogue_starts(latest_year)
    print(f"  Catalogue events STARTING in {latest_year}: {len(starts)}")
    if len(starts):
        print(starts[["Region", "Start_Date", "End_Date", "Duration_Days", "Max_Intensity"]].to_string(index=False))

    ver = verify_year(latest_year, config, alert_thresh=0.25)
    ver_path = out / f"year_verification_{latest_year}.csv"
    ver.to_csv(ver_path, index=False)

    if len(ver):
        print(f"\n  Best-model alert hits in pre-onset window (P>={0.25}):")
        for h in horizons:
            sub = ver[ver["Horizon_Days"] == h]
            hits = int(sub["Alert_Hit"].sum())
            n = len(sub)
            print(f"    onset_{h}d: {hits}/{n} events would have triggered an alert")
        print(f"\n  Saved verification: {ver_path}")

    last_ends = []
    for region in regions:
        cat = pd.read_csv(WS_ROOT / "outputs" / "mhw" / "catalogue" / f"{region}_mhw_catalogue.csv")
        cat["End_Date"] = pd.to_datetime(cat["End_Date"])
        end = cat[cat["End_Date"].dt.year == latest_year]["End_Date"].max()
        if pd.notna(end):
            last_ends.append(f"{region}={end.date()}")
    print(
        f"\n  Why latest-day P≈0 is expected: forecast date is year-end; "
        f"last {latest_year} event ends → {', '.join(last_ends) if last_ends else 'n/a'}."
    )

    print("\n" + "=" * 72)
    print(f"  Saved forecast: {out / 'latest_forecast.csv'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

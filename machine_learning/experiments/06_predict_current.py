#!/usr/bin/env python3
"""
Step 06 — Generate forecast for the latest available date per region.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ML_ROOT, load_config, ensure_dirs, load_region_df

ensure_dirs()


def main():
    config = load_config()
    horizons = config["task"]["horizons_days"]
    regions = config["regions"]
    primary = config["models"]["primary"]

    print("=" * 72)
    print("STEP 06: CURRENT FORECAST")
    print("=" * 72)

    forecasts = []

    for region in regions:
        df = load_region_df(region)
        latest = df.iloc[-1]

        for h in horizons:
            label = f"onset_{h}d"
            path = ML_ROOT / "models" / region / f"{label}_{primary}.joblib"
            if not path.exists():
                alts = list((ML_ROOT / "models" / region).glob(f"{label}_*.joblib"))
                path = alts[0] if alts else None
            if path is None:
                continue

            bundle = joblib.load(path)
            model = bundle["model"]
            feats = bundle["features"]
            X = latest[feats].fillna(0).values.reshape(1, -1)
            prob = float(model.predict_proba(X)[0, 1]) if hasattr(model, "predict_proba") else float(model.predict(X)[0])
            alert = "HIGH" if prob >= 0.5 else "MODERATE" if prob >= 0.25 else "LOW"

            forecasts.append({
                "Region": region.title(),
                "Forecast_Date": latest["Date"].strftime("%Y-%m-%d"),
                "Horizon_Days": h,
                "P_MHW_Onset": round(prob, 4),
                "Alert_Level": alert,
                "Current_SST_C": round(latest["SST"], 3),
                "Current_Intensity_C": round(latest["Intensity"], 3),
                "Current_Wind_ms": round(latest["Wind"], 3),
                "In_MHW_Now": int(latest["in_mhw"]),
                "Model": path.stem,
            })
            print(f"  {region} {h}d: P={prob:.3f} ({alert})  SST={latest['SST']:.2f}  Wind={latest['Wind']:.2f}")

    fc_df = pd.DataFrame(forecasts)
    out = ML_ROOT / "outputs" / "forecasts"
    fc_df.to_csv(out / "latest_forecast.csv", index=False)
    fc_df.to_csv(out / f"forecast_{datetime.now().strftime('%Y%m%d')}.csv", index=False)

    print("\n" + "=" * 72)
    print(f"  Saved: {out / 'latest_forecast.csv'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

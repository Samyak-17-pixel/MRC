#!/usr/bin/env python3
"""
Step 03 — Train ML models (XGBoost, Random Forest, Gradient Boosting).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ML_ROOT, load_config, year_split_mask, get_feature_columns, ensure_dirs, load_region_df

ensure_dirs()

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier


def make_model(name, config, pos_weight):
    if name == "xgboost" and HAS_XGB:
        p = config["models"]["xgboost"]
        spw = pos_weight if p.get("scale_pos_weight") == "auto" else p.get("scale_pos_weight", 1)
        return XGBClassifier(
            n_estimators=p["n_estimators"],
            max_depth=p["max_depth"],
            learning_rate=p["learning_rate"],
            subsample=p["subsample"],
            colsample_bytree=p["colsample_bytree"],
            scale_pos_weight=spw,
            eval_metric="logloss",
            random_state=42,
            use_label_encoder=False,
        )
    if name == "random_forest":
        p = config["models"]["random_forest"]
        return RandomForestClassifier(
            n_estimators=p["n_estimators"],
            max_depth=p["max_depth"],
            class_weight=p.get("class_weight", "balanced"),
            random_state=42,
            n_jobs=-1,
        )
    if name == "gradient_boosting":
        return GradientBoostingClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42,
        )
    raise ValueError(name)


def main():
    config = load_config()
    horizons = config["task"]["horizons_days"]
    regions = config["regions"]
    model_names = [config["models"]["primary"]] + config["models"]["compare"]
    if not HAS_XGB:
        model_names = [m for m in model_names if m != "xgboost"]
        model_names = list(dict.fromkeys(["random_forest", "gradient_boosting"] + model_names))

    splits = config["splits"]
    print("=" * 72)
    print("STEP 03: TRAIN ML MODELS")
    print(f"  Models: {model_names}")
    print("=" * 72)

    for region in regions:
        df = load_region_df(region)
        feat_cols = get_feature_columns(df)

        train_mask = year_split_mask(df["Date"], splits["train_years"])
        val_mask = year_split_mask(df["Date"], splits["val_years"])
        fit_mask = train_mask | val_mask

        X_fit = df.loc[fit_mask, feat_cols].fillna(0)
        model_dir = ML_ROOT / "models" / region
        model_dir.mkdir(parents=True, exist_ok=True)

        for h in horizons:
            label = f"onset_{h}d"
            y_fit = df.loc[fit_mask, label]
            pos = y_fit.sum()
            neg = len(y_fit) - pos
            pos_weight = max(neg / max(pos, 1), 1)

            print(f"\n  {region} / {label}  (pos={pos}, neg={neg})")

            for mname in model_names:
                model = make_model(mname, config, pos_weight)
                model.fit(X_fit, y_fit)
                path = model_dir / f"{label}_{mname}.joblib"
                joblib.dump({"model": model, "features": feat_cols, "label": label, "region": region}, path)
                print(f"    Saved {mname} → {path.name}")

    print("\n" + "=" * 72)
    print("MODEL TRAINING COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()

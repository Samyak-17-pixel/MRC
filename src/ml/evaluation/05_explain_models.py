#!/usr/bin/env python3
"""
Step 05 — Model explainability (SHAP or feature importance fallback).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ML_ROOT, load_config, year_split_mask, ensure_dirs, load_region_df

ensure_dirs()

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

def plot_importance(importances, feature_names, title, outpath):
    idx = np.argsort(importances)[::-1][:20]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(range(len(idx)), importances[idx][::-1], color="steelblue")
    ax.set_yticks(range(len(idx)))
    ax.set_yticklabels([feature_names[i] for i in idx][::-1], fontsize=8)
    ax.set_xlabel("Importance")
    ax.set_title(title, fontweight="bold")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.savefig(outpath.with_suffix(".pdf"), bbox_inches="tight")
    plt.close()

def main():
    config = load_config()
    horizons = config["task"]["horizons_days"]
    regions = config["regions"]
    primary = config["models"]["primary"]
    splits = config["splits"]

    print("=" * 72)
    print("STEP 05: MODEL EXPLAINABILITY")
    print(f"  SHAP available: {HAS_SHAP}")
    print("=" * 72)

    shap_dir = ML_ROOT / "outputs" / "shap"
    shap_dir.mkdir(parents=True, exist_ok=True)
    importance_rows = []

    for region in regions:
        df = load_region_df(region)
        train_mask = year_split_mask(df["Date"], splits["train_years"])

        for h in horizons:
            label = f"onset_{h}d"
            candidates = list((ML_ROOT / "models" / region).glob(f"{label}_*.joblib"))
            path = ML_ROOT / "models" / region / f"{label}_{primary}.joblib"
            if not path.exists() and candidates:
                path = candidates[0]

            if not path.exists():
                continue

            bundle = joblib.load(path)
            model = bundle["model"]
            feats = bundle["features"]
            mname = path.stem.replace(f"{label}_", "")
            X = df.loc[train_mask, feats].fillna(0).sample(min(500, train_mask.sum()), random_state=42)

            print(f"\n  {region} / {label} / {mname}")

            if HAS_SHAP and hasattr(model, "predict_proba"):
                try:
                    explainer = shap.TreeExplainer(model)
                    sv = explainer.shap_values(X)
                    if isinstance(sv, list):
                        sv = sv[1]
                    fig, ax = plt.subplots(figsize=(8, 6))
                    shap.summary_plot(sv, X, show=False, max_display=20)
                    plt.title(f"SHAP — {region} {label}")
                    plt.tight_layout()
                    plt.savefig(shap_dir / f"shap_{region}_{label}.png", dpi=200, bbox_inches="tight")
                    plt.close()
                    mean_abs = np.abs(sv).mean(axis=0)
                except Exception as e:
                    print(f"    SHAP failed: {e}, using feature_importances_")
                    mean_abs = getattr(model, "feature_importances_", np.zeros(len(feats)))
            elif hasattr(model, "feature_importances_"):
                mean_abs = model.feature_importances_
            elif hasattr(model, "coef_"):
                mean_abs = np.abs(model.coef_).flatten()
            else:
                continue

            plot_importance(
                mean_abs, feats,
                f"Feature Importance — {region.title()} {label} ({mname})",
                shap_dir / f"importance_{region}_{label}.png",
            )

            for f, imp in zip(feats, mean_abs):
                importance_rows.append({
                    "region": region, "horizon": h, "model": mname,
                    "feature": f, "importance": float(imp),
                })

    if importance_rows:
        imp_df = pd.DataFrame(importance_rows)
        imp_df.to_csv(shap_dir / "feature_importance_all.csv", index=False)
        for region in regions:
            sub = imp_df[imp_df["region"] == region]
            if not sub.empty:
                top = sub.groupby("feature")["importance"].mean().sort_values(ascending=False).head(15)
                top.to_csv(shap_dir / f"top_features_{region}.csv")

    print("\n" + "=" * 72)
    print("EXPLAINABILITY COMPLETE")
    print(f"  Output: {shap_dir}")
    print("=" * 72)

if __name__ == "__main__":
    main()

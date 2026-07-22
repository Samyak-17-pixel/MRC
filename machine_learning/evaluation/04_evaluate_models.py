#!/usr/bin/env python3
"""
Step 04 — Evaluate all models on chronological test set (2022–2025).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss,
    confusion_matrix, RocCurveDisplay, PrecisionRecallDisplay,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ML_ROOT, load_config, year_split_mask, ensure_dirs, load_region_df

ensure_dirs()


def metrics(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else np.nan,
        "pr_auc": float(average_precision_score(y_true, y_prob)) if y_true.sum() > 0 else np.nan,
        "brier_score": float(brier_score_loss(y_true, y_prob)),
        "positives": int(y_true.sum()),
        "n": int(len(y_true)),
    }


def main():
    config = load_config()
    horizons = config["task"]["horizons_days"]
    regions = config["regions"]
    splits = config["splits"]
    primary = config["models"]["primary"]

    print("=" * 72)
    print("STEP 04: EVALUATE MODELS")
    print("=" * 72)

    rows = []
    fig_dir = ML_ROOT / "outputs" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    for region in regions:
        df = load_region_df(region)
        test_mask = year_split_mask(df["Date"], splits["test_years"])
        y_df = df.loc[test_mask]

        for h in horizons:
            label = f"onset_{h}d"
            y_true = y_df[label].values

            # Baselines
            base_path = ML_ROOT / "outputs" / "metrics" / "baselines.csv"
            if base_path.exists():
                pass  # already in baselines.csv

            # ML models
            model_dir = ML_ROOT / "models" / region
            for path in sorted(model_dir.glob(f"{label}_*.joblib")):
                bundle = joblib.load(path)
                model = bundle["model"]
                feats = bundle["features"]
                mname = path.stem.replace(f"{label}_", "")
                X = df.loc[test_mask, feats].fillna(0)
                if hasattr(model, "predict_proba"):
                    prob = model.predict_proba(X)[:, 1]
                else:
                    prob = model.predict(X).astype(float)

                m = metrics(y_true, prob)
                m.update({"region": region, "horizon": h, "model": mname, "split": "test"})
                rows.append(m)
                print(f"  {region}/{label}/{mname}: F1={m['f1']:.3f} PR-AUC={m['pr_auc']:.3f}")

                # Confusion matrix for primary model
                if mname == primary or (primary == "xgboost" and mname == "random_forest"):
                    pred = (prob >= 0.5).astype(int)
                    cm = confusion_matrix(y_true, pred)
                    fig, ax = plt.subplots(figsize=(5, 4))
                    im = ax.imshow(cm, cmap="Blues")
                    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
                    ax.set_xticklabels(["No", "Yes"]); ax.set_yticklabels(["No", "Yes"])
                    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
                    ax.set_title(f"{region.title()} {label} — {mname}")
                    for i in range(2):
                        for j in range(2):
                            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14)
                    plt.colorbar(im, ax=ax)
                    plt.tight_layout()
                    plt.savefig(fig_dir / f"confusion_{region}_{label}_{mname}.png", dpi=200)
                    plt.close()

                    fig, ax = plt.subplots(figsize=(5, 4))
                    RocCurveDisplay.from_predictions(y_true, prob, ax=ax)
                    ax.set_title(f"ROC — {region} {label} {mname}")
                    plt.tight_layout()
                    plt.savefig(fig_dir / f"roc_{region}_{label}_{mname}.png", dpi=200)
                    plt.close()

                    fig, ax = plt.subplots(figsize=(5, 4))
                    PrecisionRecallDisplay.from_predictions(y_true, prob, ax=ax)
                    ax.set_title(f"PR — {region} {label} {mname}")
                    plt.tight_layout()
                    plt.savefig(fig_dir / f"pr_{region}_{label}_{mname}.png", dpi=200)
                    plt.close()

    ml_metrics = pd.DataFrame(rows)
    ml_metrics.to_csv(ML_ROOT / "outputs" / "metrics" / "ml_models.csv", index=False)

    if (ML_ROOT / "outputs" / "metrics" / "baselines.csv").exists():
        combined = pd.concat([
            pd.read_csv(ML_ROOT / "outputs" / "metrics" / "baselines.csv"),
            ml_metrics,
        ], ignore_index=True)
        combined.to_csv(ML_ROOT / "outputs" / "metrics" / "all_models_comparison.csv", index=False)

        # Summary heatmap: best F1 per region/horizon
        best = combined.loc[combined.groupby(["region", "horizon"])["f1"].idxmax()]
        best.to_csv(ML_ROOT / "outputs" / "metrics" / "best_models.csv", index=False)

    print("\n" + "=" * 72)
    print("EVALUATION COMPLETE")
    print(f"  Metrics: {ML_ROOT / 'outputs/metrics/all_models_comparison.csv'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

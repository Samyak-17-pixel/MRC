#!/usr/bin/env python3
"""
Step 02 — Train baseline models (climatology, persistence, logistic regression).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import (
    ML_ROOT, load_config, year_split_mask, get_feature_columns,
    save_json, ensure_dirs, load_region_df,
)

ensure_dirs()


def evaluate(y_true, y_prob, y_pred):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else np.nan,
        "pr_auc": float(average_precision_score(y_true, y_prob)) if y_true.sum() > 0 else np.nan,
        "brier_score": float(brier_score_loss(y_true, y_prob)),
    }


def climatology_baseline(df, label_col):
    """P(onset) by DOY — empirical seasonal probability."""
    train = df[year_split_mask(df["Date"], load_config()["splits"]["train_years"])]
    doy_rate = train.groupby("DOY")[label_col].mean()
    prob = df["DOY"].map(doy_rate).fillna(train[label_col].mean())
    pred = (prob >= 0.5).astype(int)
    return prob.values, pred.values


def persistence_baseline(df, label_col):
    """If currently above threshold with streak >= 3, predict onset likely."""
    prob = np.clip(df["Consecutive_Hot_Days"] / 10, 0, 0.9)
    prob = np.clip(prob + np.clip(df["Intensity"] / 2, 0, 0.3), 0, 1)
    pred = (prob >= 0.5).astype(int)
    return prob, pred


def main():
    config = load_config()
    horizons = config["task"]["horizons_days"]
    regions = config["regions"]
    splits = config["splits"]

    print("=" * 72)
    print("STEP 02: TRAIN BASELINES")
    print("=" * 72)

    all_metrics = []

    for region in regions:
        df = load_region_df(region)

        test_mask = year_split_mask(df["Date"], splits["test_years"])
        train_mask = year_split_mask(df["Date"], splits["train_years"])
        val_mask = year_split_mask(df["Date"], splits["val_years"])
        fit_mask = train_mask | val_mask

        feat_cols = get_feature_columns(df)
        log_cols = [c for c in feat_cols if any(
            k in c for k in ["SST", "Intensity", "Wind", "DMI", "ONI", "MEI", "Consecutive", "DOY_sin"]
        )][:25]

        for h in horizons:
            label = f"onset_{h}d"
            print(f"\n  {region} / {label}")

            for baseline_name, fn in [
                ("climatology", climatology_baseline),
                ("persistence", persistence_baseline),
            ]:
                prob, pred = fn(df, label)
                m = evaluate(df.loc[test_mask, label], prob[test_mask], pred[test_mask])
                m.update({"region": region, "horizon": h, "model": baseline_name, "split": "test"})
                all_metrics.append(m)
                print(f"    {baseline_name}: F1={m['f1']:.3f} ROC-AUC={m['roc_auc']:.3f}")

            X = df.loc[fit_mask, log_cols].fillna(0)
            y = df.loc[fit_mask, label]
            pipe = Pipeline([
                ("scaler", StandardScaler()),
                ("lr", LogisticRegression(max_iter=1000, class_weight="balanced")),
            ])
            pipe.fit(X, y)
            prob = pipe.predict_proba(df.loc[:, log_cols].fillna(0))[:, 1]
            pred = (prob >= 0.5).astype(int)
            m = evaluate(df.loc[test_mask, label], prob[test_mask], pred[test_mask])
            m.update({"region": region, "horizon": h, "model": "logistic_regression", "split": "test"})
            all_metrics.append(m)
            print(f"    logistic: F1={m['f1']:.3f} ROC-AUC={m['roc_auc']:.3f}")

            joblib.dump(pipe, ML_ROOT / "models" / "baselines" / f"{region}_{label}_logistic.joblib")

    metrics_df = pd.DataFrame(all_metrics)
    metrics_df.to_csv(ML_ROOT / "outputs" / "metrics" / "baselines.csv", index=False)
    save_json(all_metrics, ML_ROOT / "outputs" / "metrics" / "baselines.json")

    print("\n" + "=" * 72)
    print("BASELINES COMPLETE")
    print(f"  Metrics: {ML_ROOT / 'outputs/metrics/baselines.csv'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

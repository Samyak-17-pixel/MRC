#!/usr/bin/env python3
"""
MEI Lag Analysis
----------------
Associate every MHW event with MEI v2 at 0, 1, 2, 3, and 6-month lead times.
Compute Pearson correlations with duration and intensity.

Input:
    datasets/meiv2.nc
    results/mhw_catalogue/*_mhw_catalogue.csv

Output:
    results/mei_lag/
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
from scipy.stats import pearsonr, linregress
from pathlib import Path

MEI_FILE = "/home/samyak/mrc_ws/datasets/meiv2.nc"
CATALOGUES = {
    "North": "/home/samyak/mrc_ws/results/mhw_catalogue/north_mhw_catalogue.csv",
    "Central": "/home/samyak/mrc_ws/results/mhw_catalogue/central_mhw_catalogue.csv",
    "South": "/home/samyak/mrc_ws/results/mhw_catalogue/south_mhw_catalogue.csv",
}
OUTDIR = Path("/home/samyak/mrc_ws/results/mei_lag")
OUTDIR.mkdir(parents=True, exist_ok=True)

LAGS = [0, 1, 2, 3, 6]

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["font.size"] = 13


def classify_mei(mei):
    if pd.isna(mei):
        return "Unknown"
    if mei >= 0.5:
        return "El Nino"
    if mei <= -0.5:
        return "La Nina"
    return "Neutral"


def load_mei():
    ds = xr.open_dataset(MEI_FILE)
    df = ds.to_dataframe().reset_index()
    df = df.rename(columns={"value": "MEI"})
    df["time"] = pd.to_datetime(df["time"])
    df = df[(df["time"].dt.year >= 2006) & (df["time"].dt.year <= 2025)]
    return df[["time", "MEI"]]


def get_mei(dt, lag, mei_df):
    t = (pd.Timestamp(dt) - pd.DateOffset(months=lag)).replace(day=1)
    row = mei_df.loc[mei_df["time"] == t]
    return np.nan if len(row) == 0 else float(row["MEI"].iloc[0])


def save_figure(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()


mei = load_mei()
summary = []

for region, file in CATALOGUES.items():
    df = pd.read_csv(file)
    df["Start_Date"] = pd.to_datetime(df["Start_Date"])

    for lag in LAGS:
        df[f"MEI_{lag}m"] = df["Start_Date"].apply(lambda x: get_mei(x, lag, mei))

    df["MEI_Phase"] = df["MEI_0m"].apply(classify_mei)
    for lag in [1, 2, 3, 6]:
        df[f"MEI_Phase_{lag}m"] = df[f"MEI_{lag}m"].apply(classify_mei)

    df.to_csv(OUTDIR / f"{region.lower()}_mei_lag.csv", index=False)

    duration = "Duration_Days"
    intensity = "Mean_Intensity"

    rows = []
    for lag in LAGS:
        subset = df[[duration, intensity, f"MEI_{lag}m"]].dropna()
        if len(subset) > 2:
            rd, pd_ = pearsonr(subset[f"MEI_{lag}m"], subset[duration])
            ri, pi = pearsonr(subset[f"MEI_{lag}m"], subset[intensity])
        else:
            rd = pd_ = ri = pi = np.nan
        rows.append({
            "Lag": lag,
            "Duration_r": rd,
            "Duration_p": pd_,
            "Intensity_r": ri,
            "Intensity_p": pi,
        })

    corr = pd.DataFrame(rows)
    corr.to_csv(OUTDIR / f"{region.lower()}_lag_correlation.csv", index=False)

    print(f"\n{'=' * 70}\n{region.upper()}\n{'=' * 70}")
    print(corr.round(3).to_string(index=False))

    plt.figure(figsize=(8, 5))
    plt.plot(corr["Lag"], corr["Duration_r"], marker="o", linewidth=2, label="Duration")
    plt.plot(corr["Lag"], corr["Intensity_r"], marker="s", linewidth=2, label="Intensity")
    plt.axhline(0, color="black", linestyle="--")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.xlabel("Lag (months)")
    plt.ylabel("Pearson r")
    plt.title(f"{region} Bay of Bengal: MEI Lag Correlation")
    plt.tight_layout()
    save_figure(OUTDIR / f"{region.lower()}_lag")

    best_idx = corr["Duration_r"].abs().idxmax()
    best = corr.iloc[best_idx]
    best_lag = int(best["Lag"])

    subset = df[[duration, intensity, f"MEI_{best_lag}m"]].dropna()
    if len(subset) > 2:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for ax, col, label in zip(
            axes, [duration, intensity], ["Duration (days)", "Mean Intensity"]
        ):
            x = subset[f"MEI_{best_lag}m"]
            y = subset[col]
            ax.scatter(x, y, alpha=0.7, edgecolor="black", linewidth=0.5)
            slope, intercept, _, _, _ = linregress(x, y)
            xx = np.linspace(x.min(), x.max(), 100)
            ax.plot(xx, slope * xx + intercept, color="red", linewidth=2)
            ax.set_xlabel(f"MEI at {best_lag}-month lag")
            ax.set_ylabel(label)
            ax.grid(alpha=0.3)
        fig.suptitle(f"{region}: Scatter at Best Lag ({best_lag} months)", fontweight="bold")
        fig.tight_layout()
        save_figure(OUTDIR / f"{region.lower()}_scatter_best_lag")

    print(f"\nBest Lag: {best_lag} months")
    print(f"Duration r = {best['Duration_r']:.3f}, p = {best['Duration_p']:.4f}")

    summary.append({
        "Region": region,
        "BestLag": best_lag,
        "BestCorrelation": best["Duration_r"],
        "Pvalue": best["Duration_p"],
    })

pd.DataFrame(summary).to_csv(OUTDIR / "summary.csv", index=False)

print(f"\n{'=' * 70}\nMEI LAG ANALYSIS COMPLETE\n{'=' * 70}")
print(f"Output: {OUTDIR}")

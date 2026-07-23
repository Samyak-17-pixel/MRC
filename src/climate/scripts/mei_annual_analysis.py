#!/usr/bin/env python3
"""
MEI Annual Analysis
-------------------
Annual MHW statistics compared with annual mean MEI.

Input:
    outputs/mei/lag/*_mei_lag.csv
    data/raw/meiv2.nc

Output:
    outputs/mei/annual/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from scipy.stats import pearsonr, linregress

MEI_FILE = "/home/samyak/mrc_ws/data/raw/meiv2.nc"
CATALOGUES = {
    "North": "/home/samyak/mrc_ws/outputs/mei/lag/north_mei_lag.csv",
    "Central": "/home/samyak/mrc_ws/outputs/mei/lag/central_mei_lag.csv",
    "South": "/home/samyak/mrc_ws/outputs/mei/lag/south_mei_lag.csv",
}

OUT = "/home/samyak/mrc_ws/outputs/mei/annual"
CSV = os.path.join(OUT, "csv")
FIG = os.path.join(OUT, "figures")
os.makedirs(CSV, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["font.size"] = 13


def save_figure(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()


ds = xr.open_dataset(MEI_FILE)
mei = ds.to_dataframe().reset_index()
mei = mei.rename(columns={"value": "MEI"})
mei["Date"] = pd.to_datetime(mei["time"])
mei["Year"] = mei["Date"].dt.year
mei = mei[(mei["Year"] >= 2006) & (mei["Year"] <= 2025)]

annual_mei = mei.groupby("Year").agg(
    Mean_MEI=("MEI", "mean"),
    Max_MEI=("MEI", "max"),
    Min_MEI=("MEI", "min"),
).reset_index()

METRICS = ["Events", "Mean_Duration", "Max_Duration", "Mean_Intensity", "Max_Intensity"]
summary = []

for region, file in CATALOGUES.items():
    print(f"\n{'=' * 70}\n{region.upper()}\n{'=' * 70}")

    df = pd.read_csv(file)
    df["Start_Date"] = pd.to_datetime(df["Start_Date"])
    df["Year"] = df["Start_Date"].dt.year

    annual = df.groupby("Year").agg(
        Events=("Year", "size"),
        Mean_Duration=("Duration_Days", "mean"),
        Max_Duration=("Duration_Days", "max"),
        Mean_Intensity=("Mean_Intensity", "mean"),
        Max_Intensity=("Max_Intensity", "max"),
    ).reset_index()

    annual = annual.merge(annual_mei, on="Year", how="left")
    annual.to_csv(f"{CSV}/{region.lower()}_annual.csv", index=False)
    print(annual.round(3).to_string(index=False))

    region_corr = {"Region": region}
    for metric in METRICS:
        valid = annual[[metric, "Mean_MEI"]].dropna()
        if len(valid) > 2:
            r, p = pearsonr(valid[metric], valid["Mean_MEI"])
        else:
            r, p = np.nan, np.nan
        region_corr[f"{metric}_r"] = r
        region_corr[f"{metric}_p"] = p
        print(f"  {metric} vs Mean MEI: r={r:.3f}, p={p:.4f}")
    summary.append(region_corr)

    plt.figure(figsize=(10, 5))
    plt.plot(annual["Year"], annual["Events"], marker="o", linewidth=2)
    plt.grid(alpha=0.3)
    plt.title(f"{region}: Annual MHW Events", fontweight="bold")
    plt.ylabel("Events")
    plt.xlabel("Year")
    plt.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_events")

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(annual["Year"], annual["Events"], marker="o", color="darkred", label="Events")
    ax1.set_ylabel("MHW Events", color="darkred")
    ax2 = ax1.twinx()
    ax2.plot(annual["Year"], annual["Mean_MEI"], marker="s", color="royalblue", label="Mean MEI")
    ax2.set_ylabel("Mean MEI", color="royalblue")
    ax1.set_xlabel("Year")
    plt.title(f"{region}: Annual Events vs Mean MEI", fontweight="bold")
    fig.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_events_vs_mei")

    for col, label, fname in [
        ("Mean_Duration", "Mean Duration (days)", "duration"),
        ("Mean_Intensity", "Mean Intensity (°C)", "intensity"),
    ]:
        plt.figure(figsize=(10, 5))
        plt.plot(annual["Year"], annual[col], marker="o", linewidth=2)
        plt.grid(alpha=0.3)
        plt.title(f"{region}: Annual {label}", fontweight="bold")
        plt.ylabel(label)
        plt.xlabel("Year")
        plt.tight_layout()
        save_figure(f"{FIG}/{region.lower()}_{fname}")

    valid = annual[["Events", "Mean_MEI"]].dropna()
    if len(valid) > 2:
        plt.figure(figsize=(8, 6))
        plt.scatter(valid["Mean_MEI"], valid["Events"], s=60, edgecolor="black")
        slope, intercept, _, _, _ = linregress(valid["Mean_MEI"], valid["Events"])
        xx = np.linspace(valid["Mean_MEI"].min(), valid["Mean_MEI"].max(), 100)
        plt.plot(xx, slope * xx + intercept, color="red", linewidth=2)
        plt.xlabel("Annual Mean MEI")
        plt.ylabel("Annual MHW Events")
        plt.title(f"{region}: Events vs Annual MEI", fontweight="bold")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        save_figure(f"{FIG}/{region.lower()}_events_mei_scatter")

pd.DataFrame(summary).to_csv(f"{OUT}/summary.csv", index=False)

print(f"\n{'=' * 70}\nMEI ANNUAL ANALYSIS COMPLETE\n{'=' * 70}")
print(f"Output: {OUT}")

#!/usr/bin/env python3
"""
IOD Annual Analysis
-------------------
Annual MHW statistics compared with annual mean DMI.

Input:
    results/iod_lag/*_iod_lag.csv
    datasets/dmi.had.long.nc

Output:
    results/iod_annual/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from scipy.stats import pearsonr, linregress

DMI_FILE = "/home/samyak/mrc_ws/datasets/dmi.had.long.nc"
CATALOGUES = {
    "North": "/home/samyak/mrc_ws/results/iod_lag/north_iod_lag.csv",
    "Central": "/home/samyak/mrc_ws/results/iod_lag/central_iod_lag.csv",
    "South": "/home/samyak/mrc_ws/results/iod_lag/south_iod_lag.csv",
}

OUT = "/home/samyak/mrc_ws/results/iod_annual"
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


ds = xr.open_dataset(DMI_FILE)
var = list(ds.data_vars)[0]
dmi = ds[var].to_dataframe().reset_index()
dmi = dmi.rename(columns={dmi.columns[-1]: "DMI"})
dmi["Date"] = pd.to_datetime(dmi["time"])
dmi["Year"] = dmi["Date"].dt.year
dmi = dmi[(dmi["Year"] >= 2006) & (dmi["Year"] <= 2025)]

annual_dmi = dmi.groupby("Year").agg(
    Mean_DMI=("DMI", "mean"),
    Max_DMI=("DMI", "max"),
    Min_DMI=("DMI", "min"),
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

    annual = annual.merge(annual_dmi, on="Year", how="left")
    annual.to_csv(f"{CSV}/{region.lower()}_annual.csv", index=False)
    print(annual.round(3).to_string(index=False))

    region_corr = {"Region": region}
    for metric in METRICS:
        valid = annual[[metric, "Mean_DMI"]].dropna()
        if len(valid) > 2:
            r, p = pearsonr(valid[metric], valid["Mean_DMI"])
        else:
            r, p = np.nan, np.nan
        region_corr[f"{metric}_r"] = r
        region_corr[f"{metric}_p"] = p
        print(f"  {metric} vs Mean DMI: r={r:.3f}, p={p:.4f}")
    summary.append(region_corr)

    # Annual events
    plt.figure(figsize=(10, 5))
    plt.plot(annual["Year"], annual["Events"], marker="o", linewidth=2)
    plt.grid(alpha=0.3)
    plt.title(f"{region}: Annual MHW Events", fontweight="bold")
    plt.ylabel("Events")
    plt.xlabel("Year")
    plt.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_events")

    # Dual axis: events vs DMI
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(annual["Year"], annual["Events"], marker="o", color="darkred", label="Events")
    ax1.set_ylabel("MHW Events", color="darkred")
    ax2 = ax1.twinx()
    ax2.plot(annual["Year"], annual["Mean_DMI"], marker="s", color="royalblue", label="Mean DMI")
    ax2.set_ylabel("Mean DMI", color="royalblue")
    ax1.set_xlabel("Year")
    plt.title(f"{region}: Annual Events vs Mean DMI", fontweight="bold")
    fig.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_events_vs_dmi")

    # Duration and intensity time series
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

    # Scatter: events vs DMI with regression
    valid = annual[["Events", "Mean_DMI"]].dropna()
    if len(valid) > 2:
        plt.figure(figsize=(8, 6))
        plt.scatter(valid["Mean_DMI"], valid["Events"], s=60, edgecolor="black")
        slope, intercept, _, _, _ = linregress(valid["Mean_DMI"], valid["Events"])
        xx = np.linspace(valid["Mean_DMI"].min(), valid["Mean_DMI"].max(), 100)
        plt.plot(xx, slope * xx + intercept, color="red", linewidth=2)
        plt.xlabel("Annual Mean DMI")
        plt.ylabel("Annual MHW Events")
        plt.title(f"{region}: Events vs Annual DMI", fontweight="bold")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        save_figure(f"{FIG}/{region.lower()}_events_dmi_scatter")

pd.DataFrame(summary).to_csv(f"{OUT}/summary.csv", index=False)

print(f"\n{'=' * 70}\nIOD ANNUAL ANALYSIS COMPLETE\n{'=' * 70}")
print(f"Output: {OUT}")

#!/usr/bin/env python3
"""
MEI Frequency Analysis
----------------------
Phase frequencies, chi-square test, Cramer's V, and publication figures.

Input:
    outputs/mei/lag/*_mei_lag.csv

Output:
    outputs/mei/frequency/
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chisquare

CATALOGUES = {
    "North": "/home/samyak/mrc_ws/outputs/mei/lag/north_mei_lag.csv",
    "Central": "/home/samyak/mrc_ws/outputs/mei/lag/central_mei_lag.csv",
    "South": "/home/samyak/mrc_ws/outputs/mei/lag/south_mei_lag.csv",
}

OUTDIR = "/home/samyak/mrc_ws/outputs/mei/frequency"
os.makedirs(OUTDIR, exist_ok=True)

PHASES = ["El Nino", "Neutral", "La Nina"]
COLORS = ["tomato", "gray", "royalblue"]

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["font.size"] = 13


def classify(mei):
    if pd.isna(mei):
        return "Unknown"
    if mei >= 0.5:
        return "El Nino"
    if mei <= -0.5:
        return "La Nina"
    return "Neutral"


def save_figure(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()


summary = []
all_tables = {}

for region, f in CATALOGUES.items():
    print(f"\n{'=' * 70}\n{region.upper()}\n{'=' * 70}")

    df = pd.read_csv(f)
    if "MEI_Phase" not in df.columns:
        df["MEI_Phase"] = df["MEI_0m"].apply(classify)

    counts = df["MEI_Phase"].value_counts().reindex(PHASES, fill_value=0)
    pct = counts / counts.sum() * 100

    result = pd.DataFrame({
        "Phase": counts.index,
        "Events": counts.values,
        "Percentage": pct.values,
    })

    print(result.round(2).to_string(index=False))
    all_tables[region] = result

    observed = counts.values
    expected = np.repeat(observed.sum() / 3, 3)
    chi2, p = chisquare(observed, expected)
    cramers_v = np.sqrt(chi2 / (observed.sum() * (len(observed) - 1)))

    print(f"\nChi-square: {chi2:.3f}, p = {p:.5f}, Cramer's V: {cramers_v:.3f}")
    print("Significant:", "YES" if p < 0.05 else "NO")

    result.to_csv(f"{OUTDIR}/{region.lower()}_frequency.csv", index=False)
    df.to_csv(f, index=False)

    plt.figure(figsize=(8, 6))
    bars = plt.bar(result["Phase"], result["Events"], color=COLORS, edgecolor="black")
    for b in bars:
        plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.2,
                 int(b.get_height()), ha="center", fontsize=11)
    plt.ylabel("Number of MHW Events")
    plt.xlabel("MEI Phase")
    plt.title(f"{region} Bay of Bengal\nMEI Phase Frequency", fontweight="bold")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_figure(f"{OUTDIR}/{region.lower()}_frequency_bar")

    plt.figure(figsize=(6, 6))
    plt.pie(result["Events"], labels=result["Phase"], autopct="%1.1f%%",
            startangle=90, colors=COLORS)
    plt.title(f"{region} Bay of Bengal", fontweight="bold")
    save_figure(f"{OUTDIR}/{region.lower()}_frequency_pie")

    plt.figure(figsize=(8, 6))
    bars = plt.bar(result["Phase"], result["Percentage"], color=COLORS, edgecolor="black")
    for b in bars:
        plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
                 f"{b.get_height():.1f}%", ha="center", fontsize=11)
    plt.ylabel("Percentage of MHW Events (%)")
    plt.xlabel("MEI Phase")
    plt.title(f"{region} Bay of Bengal\nMEI Phase Percentage", fontweight="bold")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_figure(f"{OUTDIR}/{region.lower()}_frequency_pct")

    summary.append({
        "Region": region,
        "TotalEvents": int(observed.sum()),
        "ElNino": int(observed[0]),
        "Neutral": int(observed[1]),
        "LaNina": int(observed[2]),
        "ChiSquare": chi2,
        "PValue": p,
        "CramersV": cramers_v,
    })

x = np.arange(len(PHASES))
width = 0.25
fig, ax = plt.subplots(figsize=(10, 7))
for i, region in enumerate(["North", "Central", "South"]):
    ax.bar(x + (i - 1) * width, all_tables[region]["Events"], width, label=region)
ax.set_xticks(x)
ax.set_xticklabels(PHASES)
ax.set_ylabel("Marine Heatwave Events")
ax.set_xlabel("MEI Phase")
ax.set_title("Regional MEI Phase Comparison", fontweight="bold")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
save_figure(f"{OUTDIR}/regional_comparison")

fig, ax = plt.subplots(figsize=(10, 7))
bottom = np.zeros(3)
for region in ["North", "Central", "South"]:
    vals = all_tables[region]["Events"].values
    ax.bar(PHASES, vals, bottom=bottom, label=region)
    bottom += vals
ax.set_ylabel("Marine Heatwave Events")
ax.set_xlabel("MEI Phase")
ax.set_title("Stacked Regional MEI Phase Distribution", fontweight="bold")
ax.legend()
plt.tight_layout()
save_figure(f"{OUTDIR}/regional_stacked")

pd.DataFrame(summary).to_csv(f"{OUTDIR}/summary.csv", index=False)

print(f"\n{'=' * 70}\nMEI FREQUENCY ANALYSIS COMPLETE\n{'=' * 70}")
print(f"Output: {OUTDIR}")

#!/usr/bin/env python3
"""
MEI Seasonal Analysis
---------------------
MHW distribution by meteorological season and MEI phase.

Input:
    results/mei_lag/*_mei_lag.csv

Output:
    results/mei_seasonal/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

CATALOGUES = {
    "North": "/home/samyak/mrc_ws/results/mei_lag/north_mei_lag.csv",
    "Central": "/home/samyak/mrc_ws/results/mei_lag/central_mei_lag.csv",
    "South": "/home/samyak/mrc_ws/results/mei_lag/south_mei_lag.csv",
}

OUT = "/home/samyak/mrc_ws/results/mei_seasonal"
CSV = os.path.join(OUT, "csv")
FIG = os.path.join(OUT, "figures")
os.makedirs(CSV, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

SEASONS = ["Winter", "Pre-Monsoon", "SW Monsoon", "Post-Monsoon"]
PHASES = ["El Nino", "Neutral", "La Nina"]

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["font.size"] = 13


def season(m):
    if m in [12, 1, 2]:
        return "Winter"
    if m in [3, 4, 5]:
        return "Pre-Monsoon"
    if m in [6, 7, 8, 9]:
        return "SW Monsoon"
    return "Post-Monsoon"


def save_figure(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()


summary = []

for region, file in CATALOGUES.items():
    print(f"\n{'=' * 70}\n{region.upper()}\n{'=' * 70}")

    df = pd.read_csv(file)
    df["Start_Date"] = pd.to_datetime(df["Start_Date"])
    df["Season"] = df["Start_Date"].dt.month.apply(season)

    table = pd.crosstab(df["Season"], df["MEI_Phase"])
    table = table.reindex(SEASONS, fill_value=0)
    for phase in PHASES:
        if phase not in table.columns:
            table[phase] = 0
    table = table[PHASES]

    print("\nSeason × MEI Phase")
    print(table)
    table.to_csv(f"{CSV}/{region.lower()}_season_phase.csv")

    active_phases = [p for p in PHASES if table[p].sum() > 0]
    table_active = table[active_phases]

    try:
        chi2, p, dof, _ = chi2_contingency(table_active)
    except ValueError:
        chi2, p, dof = np.nan, np.nan, np.nan
        print("\nChi-square: not computed (zero expected frequencies)")

    if not np.isnan(chi2):
        print(f"\nChi-square = {chi2:.3f}, p = {p:.4f}")
        print("Significant:", "YES" if p < 0.05 else "NO")

    summary.append({"Region": region, "ChiSquare": chi2, "PValue": p})

    ax = table.plot(kind="bar", stacked=True, figsize=(10, 6),
                    color=["tomato", "gray", "royalblue"])
    ax.set_ylabel("MHW Events")
    ax.set_xlabel("Season")
    ax.set_title(f"{region}: Seasonal Distribution by MEI Phase", fontweight="bold")
    plt.xticks(rotation=20)
    plt.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_stacked")

    totals = table.sum(axis=1)
    plt.figure(figsize=(8, 5))
    totals.plot(kind="bar", color="steelblue", edgecolor="black")
    plt.ylabel("Events")
    plt.xlabel("Season")
    plt.title(f"{region}: MHW Events by Season", fontweight="bold")
    plt.xticks(rotation=20)
    plt.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_season_totals")

    x = np.arange(len(SEASONS))
    width = 0.8 / max(len(active_phases), 1)
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, phase in enumerate(active_phases):
        offset = (i - (len(active_phases) - 1) / 2) * width
        ax.bar(x + offset, table[phase].values, width, label=phase)
    ax.set_xticks(x)
    ax.set_xticklabels(SEASONS, rotation=20)
    ax.set_ylabel("MHW Events")
    ax.set_xlabel("Season")
    ax.set_title(f"{region}: Seasonal MEI Phase Comparison", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_grouped")

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(table.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(PHASES)))
    ax.set_xticklabels(PHASES)
    ax.set_yticks(range(len(SEASONS)))
    ax.set_yticklabels(SEASONS)
    for i in range(len(SEASONS)):
        for j in range(len(PHASES)):
            ax.text(j, i, int(table.values[i, j]), ha="center", va="center",
                    color="black", fontsize=12, fontweight="bold")
    plt.colorbar(im, label="Event Count")
    ax.set_title(f"{region}: Season × MEI Phase Heatmap", fontweight="bold")
    plt.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_heatmap")

pd.DataFrame(summary).to_csv(f"{OUT}/summary.csv", index=False)

print(f"\n{'=' * 70}\nMEI SEASONAL ANALYSIS COMPLETE\n{'=' * 70}")
print(f"Output: {OUT}")

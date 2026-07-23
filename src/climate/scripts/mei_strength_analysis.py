#!/usr/bin/env python3
"""
MEI Strength Analysis
---------------------
Classify MEI events by magnitude and compare MHW characteristics.

Thresholds (same as ENSO/ONI strength analysis):
    Strong El Nino   : MEI >= 2.0
    Moderate El Nino : 1.0 <= MEI < 2.0
    Weak El Nino     : 0.5 <= MEI < 1.0
    Neutral          : -0.5 < MEI < 0.5
    Weak La Nina     : -1.0 < MEI <= -0.5
    Moderate La Nina : -2.0 < MEI <= -1.0
    Strong La Nina   : MEI <= -2.0

Input:
    outputs/mei/lag/*_mei_lag.csv

Output:
    outputs/mei/strength/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kruskal

CATALOGUES = {
    "North": "/home/samyak/mrc_ws/outputs/mei/lag/north_mei_lag.csv",
    "Central": "/home/samyak/mrc_ws/outputs/mei/lag/central_mei_lag.csv",
    "South": "/home/samyak/mrc_ws/outputs/mei/lag/south_mei_lag.csv",
}

OUT = "/home/samyak/mrc_ws/outputs/mei/strength"
CSV = os.path.join(OUT, "csv")
FIG = os.path.join(OUT, "figures")
os.makedirs(CSV, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

ORDER = [
    "Strong El Nino", "Moderate El Nino", "Weak El Nino",
    "Neutral",
    "Weak La Nina", "Moderate La Nina", "Strong La Nina",
]

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["font.size"] = 13


def classify_strength(mei):
    if pd.isna(mei):
        return "Unknown"
    if mei >= 2.0:
        return "Strong El Nino"
    if mei >= 1.0:
        return "Moderate El Nino"
    if mei >= 0.5:
        return "Weak El Nino"
    if mei <= -2.0:
        return "Strong La Nina"
    if mei <= -1.0:
        return "Moderate La Nina"
    if mei <= -0.5:
        return "Weak La Nina"
    return "Neutral"


def save_figure(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()


summary = []

for region, file in CATALOGUES.items():
    print(f"\n{'=' * 70}\n{region.upper()}\n{'=' * 70}")

    df = pd.read_csv(file)
    df["MEI_Strength"] = df["MEI_0m"].apply(classify_strength)

    counts = df["MEI_Strength"].value_counts().reindex(ORDER, fill_value=0)

    result = pd.DataFrame({
        "Category": counts.index,
        "Events": counts.values,
        "Percentage": (counts.values / counts.sum() * 100).round(2),
    })

    print(result.to_string(index=False))
    result.to_csv(f"{CSV}/{region.lower()}_strength.csv", index=False)

    summary.append({
        "Region": region,
        "ElNino": int(counts.iloc[0:3].sum()),
        "Neutral": int(counts.iloc[3]),
        "LaNina": int(counts.iloc[4:7].sum()),
    })

    active = result[result["Events"] > 0]
    plt.figure(figsize=(10, 6))
    bars = plt.bar(active["Category"], active["Events"],
                   color="steelblue", edgecolor="black")
    for b in bars:
        plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.1,
                 int(b.get_height()), ha="center", fontsize=9)
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Events")
    plt.title(f"{region}: MEI Strength Distribution", fontweight="bold")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_strength")

    strength_with_events = [c for c in ORDER if len(df[df.MEI_Strength == c]) >= 2]
    if len(strength_with_events) >= 2:
        subset = df[df.MEI_Strength.isin(strength_with_events)]
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        subset.boxplot(column="Duration_Days", by="MEI_Strength", ax=axes[0])
        axes[0].set_title("Duration by MEI Strength")
        axes[0].set_ylabel("Duration (days)")
        plt.suptitle("")
        subset.boxplot(column="Mean_Intensity", by="MEI_Strength", ax=axes[1])
        axes[1].set_title("Intensity by MEI Strength")
        axes[1].set_ylabel("Mean Intensity (°C)")
        for ax in axes:
            ax.tick_params(axis="x", rotation=30)
        fig.suptitle(f"{region}: MHW Characteristics by MEI Strength", fontweight="bold")
        fig.tight_layout()
        save_figure(f"{FIG}/{region.lower()}_strength_boxplots")

        groups_d = [df[df.MEI_Strength == c]["Duration_Days"] for c in strength_with_events]
        groups_i = [df[df.MEI_Strength == c]["Mean_Intensity"] for c in strength_with_events]
        if all(len(g) >= 1 for g in groups_d) and len(groups_d) >= 2:
            _, p_d = kruskal(*groups_d)
            _, p_i = kruskal(*groups_i)
            print(f"\nKruskal-Wallis (strength categories):")
            print(f"  Duration p = {p_d:.4f}")
            print(f"  Intensity p = {p_i:.4f}")

pd.DataFrame(summary).to_csv(f"{OUT}/summary.csv", index=False)

print(f"\n{'=' * 70}\nMEI STRENGTH ANALYSIS COMPLETE\n{'=' * 70}")
print(f"Output: {OUT}")

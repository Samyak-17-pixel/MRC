#!/usr/bin/env python3
"""
IOD Strength Analysis
---------------------
Classify IOD events by magnitude and compare MHW characteristics.

Thresholds (standard IOD literature):
    Strong Positive  : DMI >= 0.8
    Moderate Positive: 0.6 <= DMI < 0.8
    Weak Positive    : 0.4 <= DMI < 0.6
    Neutral          : -0.4 < DMI < 0.4
    Weak Negative    : -0.6 < DMI <= -0.4
    Moderate Negative: -0.8 < DMI <= -0.6
    Strong Negative  : DMI <= -0.8

Input:
    outputs/iod/lag/*_iod_lag.csv

Output:
    outputs/iod/strength/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kruskal, mannwhitneyu

CATALOGUES = {
    "North": "/home/samyak/mrc_ws/outputs/iod/lag/north_iod_lag.csv",
    "Central": "/home/samyak/mrc_ws/outputs/iod/lag/central_iod_lag.csv",
    "South": "/home/samyak/mrc_ws/outputs/iod/lag/south_iod_lag.csv",
}

OUT = "/home/samyak/mrc_ws/outputs/iod/strength"
CSV = os.path.join(OUT, "csv")
FIG = os.path.join(OUT, "figures")
os.makedirs(CSV, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

ORDER = [
    "Strong Positive", "Moderate Positive", "Weak Positive",
    "Neutral",
    "Weak Negative", "Moderate Negative", "Strong Negative",
]

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["font.size"] = 13

def classify_strength(dmi):
    if pd.isna(dmi):
        return "Unknown"
    if dmi >= 0.8:
        return "Strong Positive"
    if dmi >= 0.6:
        return "Moderate Positive"
    if dmi >= 0.4:
        return "Weak Positive"
    if dmi <= -0.8:
        return "Strong Negative"
    if dmi <= -0.6:
        return "Moderate Negative"
    if dmi <= -0.4:
        return "Weak Negative"
    return "Neutral"

def save_figure(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()

summary = []

for region, file in CATALOGUES.items():
    print(f"\n{'=' * 70}\n{region.upper()}\n{'=' * 70}")

    df = pd.read_csv(file)
    df["IOD_Strength"] = df["DMI_0m"].apply(classify_strength)

    counts = df["IOD_Strength"].value_counts().reindex(ORDER, fill_value=0)

    result = pd.DataFrame({
        "Category": counts.index,
        "Events": counts.values,
        "Percentage": (counts.values / counts.sum() * 100).round(2),
    })

    print(result.to_string(index=False))
    result.to_csv(f"{CSV}/{region.lower()}_strength.csv", index=False)

    collapsed = pd.Series({
        "Positive": counts.iloc[0:3].sum(),
        "Neutral": counts.iloc[3],
        "Negative": counts.iloc[4:7].sum(),
    })

    summary.append({
        "Region": region,
        "Positive": int(collapsed["Positive"]),
        "Neutral": int(collapsed["Neutral"]),
        "Negative": int(collapsed["Negative"]),
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
    plt.title(f"{region}: IOD Strength Distribution", fontweight="bold")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_figure(f"{FIG}/{region.lower()}_strength")

    strength_with_events = [c for c in ORDER if len(df[df.IOD_Strength == c]) >= 2]
    if len(strength_with_events) >= 2:
        subset = df[df.IOD_Strength.isin(strength_with_events)]
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        subset.boxplot(column="Duration_Days", by="IOD_Strength", ax=axes[0])
        axes[0].set_title("Duration by IOD Strength")
        axes[0].set_ylabel("Duration (days)")
        plt.suptitle("")
        subset.boxplot(column="Mean_Intensity", by="IOD_Strength", ax=axes[1])
        axes[1].set_title("Intensity by IOD Strength")
        axes[1].set_ylabel("Mean Intensity (°C)")
        for ax in axes:
            ax.tick_params(axis="x", rotation=30)
        fig.suptitle(f"{region}: MHW Characteristics by IOD Strength", fontweight="bold")
        fig.tight_layout()
        save_figure(f"{FIG}/{region.lower()}_strength_boxplots")

        groups_d = [df[df.IOD_Strength == c]["Duration_Days"] for c in strength_with_events]
        groups_i = [df[df.IOD_Strength == c]["Mean_Intensity"] for c in strength_with_events]
        if all(len(g) >= 1 for g in groups_d) and len(groups_d) >= 2:
            _, p_d = kruskal(*groups_d)
            _, p_i = kruskal(*groups_i)
            print(f"\nKruskal-Wallis (strength categories):")
            print(f"  Duration p = {p_d:.4f}")
            print(f"  Intensity p = {p_i:.4f}")

pd.DataFrame(summary).to_csv(f"{OUT}/summary.csv", index=False)

print(f"\n{'=' * 70}\nIOD STRENGTH ANALYSIS COMPLETE\n{'=' * 70}")
print(f"Output: {OUT}")

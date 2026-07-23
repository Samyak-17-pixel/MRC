#!/usr/bin/env python3
"""
IOD Statistics Analysis
-----------------------
Descriptive statistics and non-parametric tests for MHW duration
and intensity across IOD phases.

Input:
    outputs/iod/lag/*_iod_lag.csv

Output:
    outputs/iod/statistics/
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

OUTDIR = "/home/samyak/mrc_ws/outputs/iod/statistics"
CSVDIR = os.path.join(OUTDIR, "csv")
FIGDIR = os.path.join(OUTDIR, "figures")
os.makedirs(CSVDIR, exist_ok=True)
os.makedirs(FIGDIR, exist_ok=True)

PHASES = ["Positive", "Neutral", "Negative"]
PAIRS = [("Positive", "Neutral"), ("Positive", "Negative"), ("Neutral", "Negative")]
COLORS = {"Positive": "firebrick", "Neutral": "gray", "Negative": "royalblue"}

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["font.size"] = 13


def save_figure(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()


def violin_plot(data_dict, ylabel, title, path_stem):
    fig, ax = plt.subplots(figsize=(8, 6))
    positions = []
    dataset = []
    for i, phase in enumerate(PHASES):
        vals = data_dict[phase].dropna().values
        if len(vals) > 0:
            positions.append(i)
            dataset.append(vals)
    if dataset:
        parts = ax.violinplot(dataset, positions=positions, showmeans=True, showmedians=True)
        for pc in parts["bodies"]:
            pc.set_alpha(0.7)
        ax.set_xticks(range(len(PHASES)))
        ax.set_xticklabels(PHASES)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_figure(path_stem)


summary = []

for region, file in CATALOGUES.items():
    print(f"\n{'=' * 70}\n{region.upper()}\n{'=' * 70}")

    df = pd.read_csv(file)
    if "IOD_Phase" not in df.columns:
        raise RuntimeError("IOD_Phase missing. Run iod_frequency_analysis.py first.")

    duration = "Duration_Days"
    meanint = "Mean_Intensity"

    stats = []
    for phase in PHASES:
        d = df[df["IOD_Phase"] == phase]
        stats.append({
            "Phase": phase,
            "Events": len(d),
            "MeanDuration": d[duration].mean(),
            "MedianDuration": d[duration].median(),
            "StdDuration": d[duration].std(),
            "MaxDuration": d[duration].max(),
            "MeanIntensity": d[meanint].mean(),
            "MaxIntensity": d["Max_Intensity"].max(),
        })

    statsdf = pd.DataFrame(stats)
    print("\nDescriptive Statistics")
    print(statsdf.round(3).to_string(index=False))
    statsdf.to_csv(f"{CSVDIR}/{region.lower()}_descriptive.csv", index=False)

    active_phases = [p for p in PHASES if len(df[df.IOD_Phase == p]) > 0]
    groups_d = [df[df.IOD_Phase == p][duration] for p in active_phases]
    groups_i = [df[df.IOD_Phase == p][meanint] for p in active_phases]

    if len(active_phases) >= 2 and all(len(g) > 0 for g in groups_d):
        h_d, p_d = kruskal(*groups_d)
        h_i, p_i = kruskal(*groups_i)
    else:
        h_d, p_d, h_i, p_i = np.nan, np.nan, np.nan, np.nan

    print(f"\nKruskal-Wallis")
    print(f"Duration : H={h_d:.3f}, p={p_d:.4f}")
    print(f"Intensity: H={h_i:.3f}, p={p_i:.4f}")

    tests = []
    for a, b in PAIRS:
        da = df[df.IOD_Phase == a][duration]
        db = df[df.IOD_Phase == b][duration]
        ia = df[df.IOD_Phase == a][meanint]
        ib = df[df.IOD_Phase == b][meanint]

        if len(da) >= 1 and len(db) >= 1:
            ua, pa = mannwhitneyu(da, db, alternative="two-sided")
            ui, pi = mannwhitneyu(ia, ib, alternative="two-sided")
        else:
            ua = pa = ui = pi = np.nan

        tests.append({
            "Comparison": f"{a} vs {b}",
            "Duration_U": ua,
            "Duration_p": pa,
            "Intensity_U": ui,
            "Intensity_p": pi,
        })

    testsdf = pd.DataFrame(tests)
    print("\nPairwise Mann-Whitney")
    print(testsdf.round(4).to_string(index=False))
    testsdf.to_csv(f"{CSVDIR}/{region.lower()}_pairwise.csv", index=False)

    summary.append({
        "Region": region,
        "KruskalDuration_p": p_d,
        "KruskalIntensity_p": p_i,
    })

    fig, ax = plt.subplots(figsize=(8, 6))
    df.boxplot(column=duration, by="IOD_Phase", ax=ax)
    ax.set_title(f"{region}: Duration by IOD Phase", fontweight="bold")
    plt.suptitle("")
    ax.set_ylabel("Duration (days)")
    plt.tight_layout()
    save_figure(f"{FIGDIR}/{region.lower()}_duration_boxplot")

    fig, ax = plt.subplots(figsize=(8, 6))
    df.boxplot(column=meanint, by="IOD_Phase", ax=ax)
    ax.set_title(f"{region}: Mean Intensity by IOD Phase", fontweight="bold")
    plt.suptitle("")
    ax.set_ylabel("Mean Intensity (°C)")
    plt.tight_layout()
    save_figure(f"{FIGDIR}/{region.lower()}_intensity_boxplot")

    dur_dict = {p: df[df.IOD_Phase == p][duration] for p in PHASES}
    int_dict = {p: df[df.IOD_Phase == p][meanint] for p in PHASES}
    violin_plot(dur_dict, "Duration (days)",
                f"{region}: Duration by IOD Phase",
                f"{FIGDIR}/{region.lower()}_duration_violin")
    violin_plot(int_dict, "Mean Intensity (°C)",
                f"{region}: Intensity by IOD Phase",
                f"{FIGDIR}/{region.lower()}_intensity_violin")

pd.DataFrame(summary).to_csv(f"{OUTDIR}/summary.csv", index=False)

print(f"\n{'=' * 70}\nIOD STATISTICS ANALYSIS COMPLETE\n{'=' * 70}")
print(f"Output: {OUTDIR}")

#!/usr/bin/env python3
"""
Climate Driver Comparison
-------------------------
Direct comparison of ENSO (ONI), IOD (DMI), and MEI v2 influences on
Bay of Bengal Marine Heatwaves.

Output:
    outputs/climate_comparison/
        csv/
        figures/
            frequency/
            lag/
            statistics/
            annual/
            seasonal/
            strength/
            rankings/
            dashboards/
            heatmaps/
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

BASE = Path("/home/samyak/mrc_ws")
RESULTS = BASE / "outputs"
OUT = RESULTS / "climate_comparison"
CSV_DIR = OUT / "csv"
FIG_ROOT = OUT / "figures"

DIRS = {
    "frequency": FIG_ROOT / "frequency",
    "lag": FIG_ROOT / "lag",
    "statistics": FIG_ROOT / "statistics",
    "annual": FIG_ROOT / "annual",
    "seasonal": FIG_ROOT / "seasonal",
    "strength": FIG_ROOT / "strength",
    "rankings": FIG_ROOT / "rankings",
    "dashboards": FIG_ROOT / "dashboards",
    "heatmaps": FIG_ROOT / "heatmaps",
}

for d in [CSV_DIR, *DIRS.values()]:
    d.mkdir(parents=True, exist_ok=True)

REGIONS = ["North", "Central", "South"]
DRIVERS = ["ENSO", "IOD", "MEI"]
DRIVER_COLORS = {"ENSO": "tomato", "IOD": "firebrick", "MEI": "darkorange"}
DRIVER_MARKERS = {"ENSO": "o", "IOD": "s", "MEI": "^"}

plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 600,
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
})

def save_fig(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()

def load_csv(path, index_col=None):
    return pd.read_csv(RESULTS / path, index_col=index_col)

def load_frequency_data():
    enso = load_csv("enso/frequency/summary.csv").set_index("Region")
    iod = load_csv("iod/frequency/summary.csv").set_index("Region")
    mei = load_csv("mei/frequency/summary.csv").set_index("Region")

    rows = []
    for region in REGIONS:
        for driver, df, phases in [
            ("ENSO", enso, ["ElNino", "Neutral", "LaNina"]),
            ("IOD", iod, ["Positive", "Neutral", "Negative"]),
            ("MEI", mei, ["ElNino", "Neutral", "LaNina"]),
        ]:
            r = df.loc[region]
            rows.append({
                "Region": region,
                "Driver": driver,
                "TotalEvents": r["TotalEvents"],
                "Phase1": r[phases[0]],
                "Phase2": r[phases[1]],
                "Phase3": r[phases[2]],
                "ChiSquare": r["ChiSquare"],
                "PValue": r["PValue"],
                "CramersV": r["CramersV"],
            })
    return pd.DataFrame(rows)

def load_lag_data():
    rows = []
    lag_curves = {}
    for driver, prefix in [("ENSO", "enso"), ("IOD", "iod"), ("MEI", "mei")]:
        for region in REGIONS:
            f = f"{prefix}/lag/{region.lower()}_lag_correlation.csv"
            df = load_csv(f)
            lag_curves[(driver, region)] = df
            best_d = df.loc[df["Duration_r"].abs().idxmax()]
            best_i = df.loc[df["Intensity_r"].abs().idxmax()]
            rows.append({
                "Region": region,
                "Driver": driver,
                "BestLag_Duration": int(best_d["Lag"]),
                "Duration_r": best_d["Duration_r"],
                "Duration_p": best_d["Duration_p"],
                "BestLag_Intensity": int(best_i["Lag"]),
                "Intensity_r": best_i["Intensity_r"],
                "Intensity_p": best_i["Intensity_p"],
            })
    return pd.DataFrame(rows), lag_curves

def load_statistics_data():
    from scipy.stats import kruskal

    rows = []
    desc = {}
    phase_cols = {"ENSO": "ENSO_Phase", "IOD": "IOD_Phase", "MEI": "MEI_Phase"}
    lag_files = {
        "ENSO": "enso/lag/{r}_enso_lag.csv",
        "IOD": "iod/lag/{r}_iod_lag.csv",
        "MEI": "mei/lag/{r}_mei_lag.csv",
    }

    for driver, prefix in [("ENSO", "enso"), ("IOD", "iod"), ("MEI", "mei")]:
        summary_path = RESULTS / f"{prefix}/statistics/summary.csv"
        has_summary = summary_path.exists()

        for region in REGIONS:
            desc[(driver, region)] = load_csv(
                f"{prefix}/statistics/csv/{region.lower()}_descriptive.csv"
            )

            if has_summary:
                summary = load_csv(f"{prefix}/statistics/summary.csv")
                s = summary[summary["Region"] == region].iloc[0]
                kd = s.get("KruskalDuration_p", np.nan)
                ki = s.get("KruskalIntensity_p", np.nan)
            else:
                lag_df = load_csv(
                    lag_files[driver].format(r=region.lower())
                )
                pcol = phase_cols[driver]
                phases = lag_df[pcol].dropna().unique()
                phases = [p for p in phases if p != "Unknown"]
                if len(phases) >= 2:
                    groups_d = [lag_df[lag_df[pcol] == p]["Duration_Days"] for p in phases]
                    groups_i = [lag_df[lag_df[pcol] == p]["Mean_Intensity"] for p in phases]
                    if all(len(g) > 0 for g in groups_d):
                        _, kd = kruskal(*groups_d)
                        _, ki = kruskal(*groups_i)
                    else:
                        kd, ki = np.nan, np.nan
                else:
                    kd, ki = np.nan, np.nan

            rows.append({
                "Region": region,
                "Driver": driver,
                "KruskalDuration_p": kd,
                "KruskalIntensity_p": ki,
            })

    return pd.DataFrame(rows), desc

def load_annual_data():
    rows = []
    annual_ts = {}
    for driver, prefix, idx_col in [
        ("ENSO", "enso", "Mean_ONI"),
        ("IOD", "iod", "Mean_DMI"),
        ("MEI", "mei", "Mean_MEI"),
    ]:
        for region in REGIONS:
            df = load_csv(f"{prefix}/annual/csv/{region.lower()}_annual.csv")
            annual_ts[(driver, region)] = df
            valid = df[["Events", idx_col]].dropna()
            if len(valid) > 2:
                r, p = np.corrcoef(valid["Events"], valid[idx_col])[0, 1],                    __import__("scipy.stats", fromlist=["pearsonr"]).pearsonr(
                        valid["Events"], valid[idx_col]
                    )[1]
            else:
                r, p = np.nan, np.nan
            rows.append({
                "Region": region,
                "Driver": driver,
                "Events_vs_Index_r": r,
                "Events_vs_Index_p": p,
            })
    return pd.DataFrame(rows), annual_ts

def load_seasonal_data():
    rows = []
    season_tables = {}
    for driver, prefix in [("ENSO", "enso"), ("IOD", "iod"), ("MEI", "mei")]:
        summary = load_csv(f"{prefix}/seasonal/summary.csv")
        for region in REGIONS:
            s = summary[summary["Region"] == region].iloc[0]
            rows.append({
                "Region": region,
                "Driver": driver,
                "ChiSquare": s["ChiSquare"],
                "PValue": s["PValue"],
            })
            season_tables[(driver, region)] = load_csv(
                f"{prefix}/seasonal/csv/{region.lower()}_season_phase.csv",
                index_col=0,
            )
    return pd.DataFrame(rows), season_tables

def load_strength_data():
    strength = {}
    for driver, prefix in [("ENSO", "enso"), ("IOD", "iod"), ("MEI", "mei")]:
        for region in REGIONS:
            strength[(driver, region)] = load_csv(
                f"{prefix}/strength/csv/{region.lower()}_strength.csv"
            )
    return strength

def compute_rankings(freq, lag, stats, annual, seasonal):
    rows = []
    for region in REGIONS:
        for driver in DRIVERS:
            f = freq[(freq.Region == region) & (freq.Driver == driver)].iloc[0]
            l = lag[(lag.Region == region) & (lag.Driver == driver)].iloc[0]
            s = stats[(stats.Region == region) & (stats.Driver == driver)].iloc[0]
            a = annual[(annual.Region == region) & (annual.Driver == driver)].iloc[0]
            se = seasonal[(seasonal.Region == region) & (seasonal.Driver == driver)].iloc[0]

            sig_count = sum([
                f["PValue"] < 0.05,
                l["Duration_p"] < 0.05,
                l["Intensity_p"] < 0.05,
                a["Events_vs_Index_p"] < 0.05 if not np.isnan(a["Events_vs_Index_p"]) else False,
                se["PValue"] < 0.05 if not np.isnan(se["PValue"]) else False,
            ])

            score = (
                (1 - min(f["PValue"], 1)) * 30
                + abs(l["Duration_r"]) * 25
                + (1 - min(l["Duration_p"], 1)) * 20
                + f["CramersV"] * 15
                + sig_count * 10
            )

            rows.append({
                "Region": region,
                "Driver": driver,
                "Frequency_p": f["PValue"],
                "CramersV": f["CramersV"],
                "Lag_Duration_r": l["Duration_r"],
                "Lag_Duration_p": l["Duration_p"],
                "Lag_Intensity_r": l["Intensity_r"],
                "Annual_Events_r": a["Events_vs_Index_r"],
                "Seasonal_p": se["PValue"],
                "Significant_Tests": sig_count,
                "CompositeScore": score,
            })

    df = pd.DataFrame(rows)
    df["Rank"] = df.groupby("Region")["CompositeScore"].rank(ascending=False).astype(int)
    return df

def plot_frequency_figures(freq):
    phase_labels = {
        "ENSO": ["El Niño", "Neutral", "La Niña"],
        "IOD": ["Positive", "Neutral", "Negative"],
        "MEI": ["El Niño", "Neutral", "La Niña"],
    }
    phase_cols = ["Phase1", "Phase2", "Phase3"]
    phase_colors = ["#d62728", "#7f7f7f", "#1f77b4"]

    for region in REGIONS:
        sub = freq[freq.Region == region]
        fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
        for ax, driver in zip(axes, DRIVERS):
            row = sub[sub.Driver == driver].iloc[0]
            vals = [row[c] for c in phase_cols]
            bars = ax.bar(phase_labels[driver], vals, color=phase_colors, edgecolor="black")
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                        str(int(b.get_height())), ha="center", fontsize=10)
            ax.set_title(f"{driver}\nχ² p={row['PValue']:.4f}", fontweight="bold")
            ax.set_ylabel("MHW Events")
            ax.grid(axis="y", alpha=0.3)
        fig.suptitle(f"{region} Bay of Bengal: MHW Frequency by Climate Driver",
                     fontweight="bold", fontsize=14)
        fig.tight_layout()
        save_fig(DIRS["frequency"] / f"{region.lower()}_frequency_comparison")

    for phase_idx, phase_name, fname in [
        (0, "Warm/Positive Phase", "warm_phase_pct"),
        (1, "Neutral Phase", "neutral_phase_pct"),
        (2, "Cool/Negative Phase", "cool_phase_pct"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(REGIONS))
        width = 0.25
        for i, driver in enumerate(DRIVERS):
            pcts = []
            for region in REGIONS:
                row = freq[(freq.Region == region) & (freq.Driver == driver)].iloc[0]
                total = row["TotalEvents"]
                pcts.append(100 * row[phase_cols[phase_idx]] / total if total > 0 else 0)
            ax.bar(x + (i - 1) * width, pcts, width, label=driver, color=DRIVER_COLORS[driver])
        ax.set_xticks(x)
        ax.set_xticklabels(REGIONS)
        ax.set_ylabel("Percentage of MHW Events (%)")
        ax.set_title(f"{phase_name} — Regional Comparison", fontweight="bold")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        save_fig(DIRS["frequency"] / fname)

    for region in REGIONS:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        for ax, driver in zip(axes, DRIVERS):
            row = freq[(freq.Region == region) & (freq.Driver == driver)].iloc[0]
            labels = phase_labels[driver]
            vals = [row[c] for c in phase_cols]
            ax.pie(vals, labels=labels, autopct="%1.1f%%", colors=phase_colors, startangle=90)
            ax.set_title(f"{driver}", fontweight="bold")
        fig.suptitle(f"{region}: Phase Distribution by Driver", fontweight="bold")
        fig.tight_layout()
        save_fig(DIRS["frequency"] / f"{region.lower()}_phase_pies")

def plot_lag_figures(lag_df, lag_curves):
    for region in REGIONS:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        for driver in DRIVERS:
            c = lag_curves[(driver, region)]
            axes[0].plot(c["Lag"], c["Duration_r"], marker=DRIVER_MARKERS[driver],
                         linewidth=2, label=driver, color=DRIVER_COLORS[driver])
            axes[1].plot(c["Lag"], c["Intensity_r"], marker=DRIVER_MARKERS[driver],
                         linewidth=2, label=driver, color=DRIVER_COLORS[driver])
        for ax, ylab in zip(axes, ["Duration Pearson r", "Intensity Pearson r"]):
            ax.axhline(0, color="black", linestyle="--", alpha=0.5)
            ax.set_xlabel("Lag (months)")
            ax.set_ylabel(ylab)
            ax.legend()
            ax.grid(alpha=0.3)
        fig.suptitle(f"{region}: Lag Correlation Comparison", fontweight="bold")
        fig.tight_layout()
        save_fig(DIRS["lag"] / f"{region.lower()}_lag_overlay")

    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    for ax, region in zip(axes, REGIONS):
        for driver in DRIVERS:
            c = lag_curves[(driver, region)]
            ax.plot(c["Lag"], c["Duration_r"], marker=DRIVER_MARKERS[driver],
                    linewidth=2, label=driver, color=DRIVER_COLORS[driver])
        ax.axhline(0, color="black", linestyle="--", alpha=0.5)
        ax.set_ylabel("Duration r")
        ax.set_title(region, fontweight="bold")
        ax.legend(loc="best", fontsize=9)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("Lag (months)")
    fig.suptitle("Lag Correlation with MHW Duration — All Regions", fontweight="bold")
    fig.tight_layout()
    save_fig(DIRS["lag"] / "combined_duration_lag_all_regions")

    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    for ax, region in zip(axes, REGIONS):
        for driver in DRIVERS:
            c = lag_curves[(driver, region)]
            ax.plot(c["Lag"], c["Intensity_r"], marker=DRIVER_MARKERS[driver],
                    linewidth=2, label=driver, color=DRIVER_COLORS[driver])
        ax.axhline(0, color="black", linestyle="--", alpha=0.5)
        ax.set_ylabel("Intensity r")
        ax.set_title(region, fontweight="bold")
        ax.legend(loc="best", fontsize=9)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("Lag (months)")
    fig.suptitle("Lag Correlation with MHW Intensity — All Regions", fontweight="bold")
    fig.tight_layout()
    save_fig(DIRS["lag"] / "combined_intensity_lag_all_regions")

    for region in REGIONS:
        sub = lag_df[lag_df.Region == region]
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        x = np.arange(len(DRIVERS))
        axes[0].bar(x, sub["Duration_r"], color=[DRIVER_COLORS[d] for d in DRIVERS],
                  edgecolor="black")
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(DRIVERS)
        axes[0].set_ylabel("Best |r| for Duration")
        axes[0].set_title("Duration", fontweight="bold")
        axes[0].axhline(0, color="black", linestyle="--")
        axes[0].grid(axis="y", alpha=0.3)
        for i, (_, row) in enumerate(sub.iterrows()):
            sig = "*" if row["Duration_p"] < 0.05 else ""
            axes[0].text(i, row["Duration_r"], f"p={row['Duration_p']:.3f}{sig}",
                         ha="center", va="bottom", fontsize=9)

        axes[1].bar(x, sub["Intensity_r"], color=[DRIVER_COLORS[d] for d in DRIVERS],
                    edgecolor="black")
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(DRIVERS)
        axes[1].set_ylabel("Best |r| for Intensity")
        axes[1].set_title("Intensity", fontweight="bold")
        axes[1].axhline(0, color="black", linestyle="--")
        axes[1].grid(axis="y", alpha=0.3)
        for i, (_, row) in enumerate(sub.iterrows()):
            sig = "*" if row["Intensity_p"] < 0.05 else ""
            axes[1].text(i, row["Intensity_r"], f"p={row['Intensity_p']:.3f}{sig}",
                         ha="center", va="bottom", fontsize=9)

        fig.suptitle(f"{region}: Best Lag Correlations by Driver", fontweight="bold")
        fig.tight_layout()
        save_fig(DIRS["lag"] / f"{region.lower()}_best_lag_bars")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax, region in zip(axes, REGIONS):
        sub = lag_df[lag_df.Region == region]
        pvals = [-np.log10(max(p, 1e-10)) for p in sub["Duration_p"]]
        bars = ax.bar(DRIVERS, pvals, color=[DRIVER_COLORS[d] for d in DRIVERS], edgecolor="black")
        ax.axhline(-np.log10(0.05), color="red", linestyle="--", label="p=0.05")
        ax.set_title(region, fontweight="bold")
        ax.set_ylabel("-log₁₀(p-value)")
        for b, p in zip(bars, sub["Duration_p"]):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.05,
                    f"{p:.3f}", ha="center", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Lag Duration Significance by Driver", fontweight="bold")
    fig.tight_layout()
    save_fig(DIRS["lag"] / "lag_significance_bars")

def pivot_heatmap(df, value_col, title, fname, cmap="RdYlBu_r", vmin=None, vmax=None,
                  fmt=".3f", sig_col=None):
    pivot = df.pivot(index="Region", columns="Driver", values=value_col)
    pivot = pivot.reindex(index=REGIONS, columns=DRIVERS)

    fig, ax = plt.subplots(figsize=(8, 6))
    data = pivot.values.astype(float)
    im = ax.imshow(data, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(DRIVERS)))
    ax.set_xticklabels(DRIVERS)
    ax.set_yticks(range(len(REGIONS)))
    ax.set_yticklabels(REGIONS)

    for i in range(len(REGIONS)):
        for j in range(len(DRIVERS)):
            val = data[i, j]
            txt = f"{val:{fmt}}" if not np.isnan(val) else "N/A"
            if sig_col:
                sig_df = df.pivot(index="Region", columns="Driver", values=sig_col)
                sig_df = sig_df.reindex(index=REGIONS, columns=DRIVERS)
                p = sig_df.values[i, j]
                if not np.isnan(p) and p < 0.05:
                    txt += "*"
            ax.text(j, i, txt, ha="center", va="center", fontsize=11, fontweight="bold")

    plt.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title(title, fontweight="bold")
    plt.tight_layout()
    save_fig(DIRS["heatmaps"] / fname)

def plot_heatmaps(freq, lag, stats, annual, seasonal, rankings):
    pivot_heatmap(freq, "PValue", "Frequency Chi-Square p-value\n(* = p < 0.05)",
                    "frequency_pvalue", cmap="RdYlGn", vmin=0, vmax=0.1, fmt=".4f")
    pivot_heatmap(freq, "CramersV", "Frequency Effect Size (Cramer's V)",
                    "frequency_cramers_v", cmap="YlOrRd", vmin=0, vmax=0.7)
    pivot_heatmap(lag, "Duration_r", "Best Lag Duration Correlation (r)",
                    "lag_duration_r", cmap="RdBu_r", vmin=-0.5, vmax=0.5, fmt=".3f",
                    sig_col="Duration_p")
    pivot_heatmap(lag, "Duration_p", "Best Lag Duration p-value",
                    "lag_duration_p", cmap="RdYlGn_r", vmin=0, vmax=0.1, fmt=".4f")
    pivot_heatmap(lag, "Intensity_r", "Best Lag Intensity Correlation (r)",
                    "lag_intensity_r", cmap="RdBu_r", vmin=-0.5, vmax=0.5, fmt=".3f",
                    sig_col="Intensity_p")
    pivot_heatmap(stats, "KruskalDuration_p", "Kruskal-Wallis p (Duration by Phase)",
                    "kruskal_duration_p", cmap="RdYlGn", vmin=0, vmax=0.3, fmt=".3f")
    pivot_heatmap(stats, "KruskalIntensity_p", "Kruskal-Wallis p (Intensity by Phase)",
                    "kruskal_intensity_p", cmap="RdYlGn", vmin=0, vmax=0.3, fmt=".3f")
    pivot_heatmap(annual, "Events_vs_Index_r", "Annual Events vs Index Correlation (r)",
                    "annual_events_r", cmap="RdBu_r", vmin=-0.6, vmax=0.6, fmt=".3f")
    pivot_heatmap(seasonal, "PValue", "Seasonal Chi-Square p-value",
                    "seasonal_pvalue", cmap="RdYlGn", vmin=0, vmax=0.3, fmt=".4f")
    pivot_heatmap(rankings, "CompositeScore", "Composite Driver Score (higher = stronger)",
                    "composite_score", cmap="YlOrRd", fmt=".1f")
    pivot_heatmap(rankings, "Significant_Tests", "Number of Significant Tests (p < 0.05)",
                    "significant_test_count", cmap="Blues", fmt=".0f")

    sig_matrix = []
    for region in REGIONS:
        row = []
        for driver in DRIVERS:
            f = freq[(freq.Region == region) & (freq.Driver == driver)].iloc[0]
            l = lag[(lag.Region == region) & (lag.Driver == driver)].iloc[0]
            se = seasonal[(seasonal.Region == region) & (seasonal.Driver == driver)].iloc[0]
            count = sum([
                f["PValue"] < 0.05,
                l["Duration_p"] < 0.05,
                l["Intensity_p"] < 0.05,
                se["PValue"] < 0.05 if not np.isnan(se["PValue"]) else False,
            ])
            row.append(count)
        sig_matrix.append(row)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(sig_matrix, aspect="auto", cmap="YlOrRd", vmin=0, vmax=4)
    ax.set_xticks(range(3))
    ax.set_xticklabels(DRIVERS)
    ax.set_yticks(range(3))
    ax.set_yticklabels(REGIONS)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(sig_matrix[i][j]), ha="center", va="center",
                    fontsize=14, fontweight="bold")
    plt.colorbar(im, label="Significant Tests (max 4)")
    ax.set_title("Master Significance Matrix\n(frequency, lag duration, lag intensity, seasonal)",
                 fontweight="bold")
    plt.tight_layout()
    save_fig(DIRS["heatmaps"] / "master_significance_matrix")

def plot_statistics_figures(desc):
    for region in REGIONS:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        for ax, metric, ylab in zip(axes, ["MeanDuration", "MeanIntensity"],
                                    ["Mean Duration (days)", "Mean Intensity (°C)"]):
            x = np.arange(3)
            width = 0.25
            for i, driver in enumerate(DRIVERS):
                d = desc[(driver, region)]
                vals = d[metric].values
                ax.bar(x + (i - 1) * width, vals, width, label=driver,
                       color=DRIVER_COLORS[driver], edgecolor="black")
            ax.set_xticks(x)
            phases = d["Phase"].tolist()
            ax.set_xticklabels(phases, rotation=15)
            ax.set_ylabel(ylab)
            ax.legend()
            ax.grid(axis="y", alpha=0.3)
        fig.suptitle(f"{region}: MHW Characteristics by Phase & Driver", fontweight="bold")
        fig.tight_layout()
        save_fig(DIRS["statistics"] / f"{region.lower()}_phase_characteristics")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, region in zip(axes, REGIONS):
        for driver in DRIVERS:
            d = desc[(driver, region)]
            ax.plot(d["Phase"], d["MaxDuration"], marker=DRIVER_MARKERS[driver],
                   linewidth=2, label=driver, color=DRIVER_COLORS[driver])
        ax.set_title(region, fontweight="bold")
        ax.set_ylabel("Max Duration (days)")
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=15)
    fig.suptitle("Maximum MHW Duration by Phase", fontweight="bold")
    fig.tight_layout()
    save_fig(DIRS["statistics"] / "max_duration_by_phase")

def plot_annual_figures(annual_ts):
    for region in REGIONS:
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        idx_names = {"ENSO": "Mean_ONI", "IOD": "Mean_DMI", "MEI": "Mean_MEI"}
        for ax, driver in zip(axes, DRIVERS):
            df = annual_ts[(driver, region)]
            idx = idx_names[driver]
            ax2 = ax.twinx()
            ax.bar(df["Year"], df["Events"], alpha=0.5, color=DRIVER_COLORS[driver], label="Events")
            ax2.plot(df["Year"], df[idx], "k-o", linewidth=2, markersize=4, label=idx)
            ax.set_ylabel("Events", color=DRIVER_COLORS[driver])
            ax2.set_ylabel(idx)
            ax.set_title(driver, fontweight="bold")
            ax.grid(alpha=0.3)
        axes[-1].set_xlabel("Year")
        fig.suptitle(f"{region}: Annual MHW Events vs Climate Index", fontweight="bold")
        fig.tight_layout()
        save_fig(DIRS["annual"] / f"{region.lower()}_annual_dual_axis")

    for region in REGIONS:
        fig, ax1 = plt.subplots(figsize=(12, 5))
        ax1.bar(annual_ts[("ENSO", region)]["Year"],
                annual_ts[("ENSO", region)]["Events"], alpha=0.3, color="gray", label="Events")
        ax1.set_ylabel("MHW Events")
        ax2 = ax1.twinx()
        for driver, col in [("ENSO", "Mean_ONI"), ("IOD", "Mean_DMI"), ("MEI", "Mean_MEI")]:
            df = annual_ts[(driver, region)]
            ax2.plot(df["Year"], df[col], marker=DRIVER_MARKERS[driver], linewidth=2,
                     label=f"{driver} ({col})", color=DRIVER_COLORS[driver])
        ax2.set_ylabel("Climate Index")
        ax2.axhline(0, color="black", linestyle="--", alpha=0.3)
        ax1.set_xlabel("Year")
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1.set_title(f"{region}: Annual Events & All Climate Indices", fontweight="bold")
        ax1.grid(alpha=0.3)
        fig.tight_layout()
        save_fig(DIRS["annual"] / f"{region.lower()}_all_indices_overlay")

def plot_seasonal_figures(season_tables):
    seasons = ["Winter", "Pre-Monsoon", "SW Monsoon", "Post-Monsoon"]

    for region in REGIONS:
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        for ax, driver in zip(axes, DRIVERS):
            table = season_tables[(driver, region)]
            cols = table.columns.tolist()
            data = table.reindex(seasons).fillna(0)[cols].values
            im = ax.imshow(data, aspect="auto", cmap="YlOrRd")
            ax.set_xticks(range(len(cols)))
            ax.set_xticklabels(cols, rotation=30, ha="right")
            ax.set_yticks(range(len(seasons)))
            ax.set_yticklabels(seasons)
            for i in range(len(seasons)):
                for j in range(len(cols)):
                    ax.text(j, i, int(data[i, j]), ha="center", va="center", fontsize=9)
            ax.set_title(driver, fontweight="bold")
            plt.colorbar(im, ax=ax, fraction=0.046)
        fig.suptitle(f"{region}: Season × Phase Heatmaps", fontweight="bold")
        fig.tight_layout()
        save_fig(DIRS["seasonal"] / f"{region.lower()}_season_phase_heatmaps")

    for region in REGIONS:
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(seasons))
        width = 0.25
        for i, driver in enumerate(DRIVERS):
            table = season_tables[(driver, region)].reindex(seasons).fillna(0)
            totals = table.sum(axis=1).values
            ax.bar(x + (i - 1) * width, totals, width, label=driver,
                   color=DRIVER_COLORS[driver])
        ax.set_xticks(x)
        ax.set_xticklabels(seasons, rotation=20)
        ax.set_ylabel("Total MHW Events")
        ax.set_title(f"{region}: Seasonal Event Totals by Driver", fontweight="bold")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        save_fig(DIRS["seasonal"] / f"{region.lower()}_season_totals")

def plot_strength_figures(strength):
    for region in REGIONS:
        fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
        for ax, driver in zip(axes, DRIVERS):
            s = strength[(driver, region)]
            active = s[s["Events"] > 0]
            ax.bar(range(len(active)), active["Events"], color=DRIVER_COLORS[driver],
                   edgecolor="black")
            ax.set_xticks(range(len(active)))
            ax.set_xticklabels(active["Category"], rotation=40, ha="right", fontsize=8)
            ax.set_title(driver, fontweight="bold")
            ax.set_ylabel("Events")
            ax.grid(axis="y", alpha=0.3)
        fig.suptitle(f"{region}: Event Strength Category Distribution", fontweight="bold")
        fig.tight_layout()
        save_fig(DIRS["strength"] / f"{region.lower()}_strength_comparison")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, region in zip(axes, REGIONS):
        warm, neutral, cool = [], [], []
        for driver in DRIVERS:
            s = strength[(driver, region)]
            if driver == "IOD":
                warm.append(s[s["Category"].str.contains("Positive")]["Events"].sum())
                cool.append(s[s["Category"].str.contains("Negative")]["Events"].sum())
            else:
                warm.append(s[s["Category"].str.contains("El Nino")]["Events"].sum())
                cool.append(s[s["Category"].str.contains("La Nina")]["Events"].sum())
            neutral.append(s[s["Category"] == "Neutral"]["Events"].sum())
        x = np.arange(3)
        w = 0.25
        ax.bar(x - w, warm, w, label="Warm/Positive", color="#d62728")
        ax.bar(x, neutral, w, label="Neutral", color="#7f7f7f")
        ax.bar(x + w, cool, w, label="Cool/Negative", color="#1f77b4")
        ax.set_xticks(x)
        ax.set_xticklabels(DRIVERS)
        ax.set_title(region, fontweight="bold")
        ax.set_ylabel("Events")
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Collapsed Strength: Warm vs Neutral vs Cool", fontweight="bold")
    fig.tight_layout()
    save_fig(DIRS["strength"] / "collapsed_strength_comparison")

def plot_ranking_figures(rankings):
    for region in REGIONS:
        sub = rankings[rankings.Region == region].sort_values("Rank")
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = [DRIVER_COLORS[d] for d in sub["Driver"]]
        bars = ax.barh(sub["Driver"], sub["CompositeScore"], color=colors, edgecolor="black")
        for b, (_, row) in zip(bars, sub.iterrows()):
            ax.text(b.get_width() + 0.5, b.get_y() + b.get_height() / 2,
                    f"Rank {int(row['Rank'])}", va="center", fontsize=10)
        ax.set_xlabel("Composite Score")
        ax.set_title(f"{region}: Climate Driver Ranking", fontweight="bold")
        ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        save_fig(DIRS["rankings"] / f"{region.lower()}_driver_ranking")

    pivot = rankings.pivot(index="Region", columns="Driver", values="Rank")
    pivot = pivot.reindex(index=REGIONS, columns=DRIVERS)
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn_r", vmin=1, vmax=3)
    ax.set_xticks(range(3))
    ax.set_xticklabels(DRIVERS)
    ax.set_yticks(range(3))
    ax.set_yticklabels(REGIONS)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"#{int(pivot.values[i,j])}", ha="center", va="center",
                    fontsize=14, fontweight="bold")
    plt.colorbar(im, label="Rank (1=best)")
    ax.set_title("Driver Ranking by Region\n(1 = strongest influence)", fontweight="bold")
    plt.tight_layout()
    save_fig(DIRS["rankings"] / "ranking_heatmap")

    wind_pct = {"North": 83.7, "Central": 77.5, "South": 82.1}
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(REGIONS))
    width = 0.2
    ax.bar(x - 1.5 * width, [wind_pct[r] for r in REGIONS], width,
           label="Weak Wind (%)", color="steelblue", edgecolor="black")
    for i, driver in enumerate(DRIVERS):
        sig_pcts = []
        for region in REGIONS:
            row = rankings[(rankings.Region == region) & (rankings.Driver == driver)].iloc[0]
            sig_pcts.append(row["Significant_Tests"] / 4 * 100)
        ax.bar(x + (i - 0.5) * width, sig_pcts, width, label=f"{driver} sig. (%)",
               color=DRIVER_COLORS[driver], edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(REGIONS)
    ax.set_ylabel("Percentage / Score")
    ax.set_title("Local Wind vs Climate Driver Significance", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    save_fig(DIRS["rankings"] / "wind_vs_climate_drivers")

def plot_dashboards(freq, lag, rankings, lag_curves):
    wind_pct = {"North": 83.7, "Central": 77.5, "South": 82.1}

    for region in REGIONS:
        fig = plt.figure(figsize=(18, 12))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.35)

        ax1 = fig.add_subplot(gs[0, 0])
        sub = freq[freq.Region == region]
        for i, driver in enumerate(DRIVERS):
            row = sub[sub.Driver == driver].iloc[0]
            ax1.bar(i, row["TotalEvents"], color=DRIVER_COLORS[driver], edgecolor="black")
            ax1.text(i, row["TotalEvents"] + 0.5, f"p={row['PValue']:.3f}", ha="center", fontsize=8)
        ax1.set_xticks(range(3))
        ax1.set_xticklabels(DRIVERS)
        ax1.set_title("Frequency χ²", fontweight="bold")
        ax1.set_ylabel("Events")

        ax2 = fig.add_subplot(gs[0, 1])
        for driver in DRIVERS:
            c = lag_curves[(driver, region)]
            ax2.plot(c["Lag"], c["Duration_r"], marker=DRIVER_MARKERS[driver],
                     label=driver, color=DRIVER_COLORS[driver])
        ax2.axhline(0, color="k", linestyle="--", alpha=0.5)
        ax2.set_title("Lag Correlation (Duration)", fontweight="bold")
        ax2.legend(fontsize=8)
        ax2.grid(alpha=0.3)

        ax3 = fig.add_subplot(gs[0, 2])
        rsub = rankings[rankings.Region == region].sort_values("CompositeScore", ascending=True)
        ax3.barh(rsub["Driver"], rsub["CompositeScore"],
                 color=[DRIVER_COLORS[d] for d in rsub["Driver"]])
        ax3.set_title("Driver Ranking", fontweight="bold")

        ax4 = fig.add_subplot(gs[1, 0])
        cramers = [sub[sub.Driver == d].iloc[0]["CramersV"] for d in DRIVERS]
        ax4.bar(DRIVERS, cramers, color=[DRIVER_COLORS[d] for d in DRIVERS], edgecolor="black")
        ax4.set_title("Effect Size (Cramer's V)", fontweight="bold")
        ax4.grid(axis="y", alpha=0.3)

        ax5 = fig.add_subplot(gs[1, 1])
        lsub = lag[lag.Region == region]
        ax5.bar(DRIVERS, lsub["Duration_r"], color=[DRIVER_COLORS[d] for d in DRIVERS], edgecolor="black")
        ax5.axhline(0, color="k", linestyle="--")
        ax5.set_title("Best Lag Duration r", fontweight="bold")
        ax5.grid(axis="y", alpha=0.3)

        ax6 = fig.add_subplot(gs[1, 2])
        ax6.bar(["Weak Wind"], [wind_pct[region]], color="steelblue", edgecolor="black", width=0.4)
        ax6.set_ylim(0, 100)
        ax6.set_ylabel("% of Events")
        ax6.set_title(f"Local Wind\n{wind_pct[region]:.1f}% weak", fontweight="bold")
        ax6.grid(axis="y", alpha=0.3)

        phase_labels = {
            "ENSO": ["El Niño", "Neutral", "La Niña"],
            "IOD": ["Positive", "Neutral", "Negative"],
            "MEI": ["El Niño", "Neutral", "La Niña"],
        }
        for j, driver in enumerate(DRIVERS):
            ax = fig.add_subplot(gs[2, j])
            row = sub[sub.Driver == driver].iloc[0]
            vals = [row["Phase1"], row["Phase2"], row["Phase3"]]
            ax.pie(vals, labels=phase_labels[driver], autopct="%1.0f%%",
                   colors=["#d62728", "#7f7f7f", "#1f77b4"], textprops={"fontsize": 8})
            ax.set_title(driver, fontweight="bold")

        fig.suptitle(f"{region} Bay of Bengal — Climate Driver Dashboard", fontweight="bold", fontsize=16)
        save_fig(DIRS["dashboards"] / f"{region.lower()}_dashboard")

    fig = plt.figure(figsize=(20, 14))
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.4, wspace=0.4)

    ax = fig.add_subplot(gs[0, :2])
    pivot = freq.pivot(index="Region", columns="Driver", values="PValue").reindex(REGIONS, columns=DRIVERS)
    im = ax.imshow(pivot.values, cmap="RdYlGn", vmin=0, vmax=0.1)
    ax.set_xticks(range(3))
    ax.set_xticklabels(DRIVERS)
    ax.set_yticks(range(3))
    ax.set_yticklabels(REGIONS)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{pivot.values[i,j]:.4f}", ha="center", va="center", fontsize=9)
    plt.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title("Frequency p-values", fontweight="bold")

    ax = fig.add_subplot(gs[0, 2:])
    pivot2 = lag.pivot(index="Region", columns="Driver", values="Duration_r").reindex(REGIONS, columns=DRIVERS)
    im2 = ax.imshow(pivot2.values, cmap="RdBu_r", vmin=-0.5, vmax=0.5)
    ax.set_xticks(range(3))
    ax.set_xticklabels(DRIVERS)
    ax.set_yticks(range(3))
    ax.set_yticklabels(REGIONS)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{pivot2.values[i,j]:.3f}", ha="center", va="center", fontsize=9)
    plt.colorbar(im2, ax=ax, fraction=0.046)
    ax.set_title("Best Lag Duration r", fontweight="bold")

    for i, region in enumerate(REGIONS):
        ax = fig.add_subplot(gs[1 + i // 2, i % 2 + (i // 2) * 2])
        if i < 3:
            for driver in DRIVERS:
                c = lag_curves[(driver, region)]
                ax.plot(c["Lag"], c["Duration_r"], marker=DRIVER_MARKERS[driver],
                        label=driver, color=DRIVER_COLORS[driver])
            ax.axhline(0, color="k", linestyle="--", alpha=0.5)
            ax.set_title(f"{region} Lag Curves", fontweight="bold")
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[2, 2:])
    rsub = rankings.sort_values(["Region", "Rank"])
    y_pos = np.arange(len(rsub))
    ax.barh(y_pos, rsub["CompositeScore"],
            color=[DRIVER_COLORS[d] for d in rsub["Driver"]])
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{r} {d}" for r, d in zip(rsub["Region"], rsub["Driver"])], fontsize=9)
    ax.set_xlabel("Composite Score")
    ax.set_title("All Driver Rankings", fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    fig.suptitle("Bay of Bengal MHW — Master Climate Driver Comparison", fontweight="bold", fontsize=16)
    save_fig(DIRS["dashboards"] / "master_dashboard")

def main():
    print("=" * 80)
    print("CLIMATE DRIVER COMPARISON")
    print("ENSO vs IOD vs MEI v2")
    print("=" * 80)

    freq = load_frequency_data()
    lag, lag_curves = load_lag_data()
    stats, desc = load_statistics_data()
    annual, annual_ts = load_annual_data()
    seasonal, season_tables = load_seasonal_data()
    strength = load_strength_data()
    rankings = compute_rankings(freq, lag, stats, annual, seasonal)

    freq.to_csv(CSV_DIR / "frequency_comparison.csv", index=False)
    lag.to_csv(CSV_DIR / "lag_comparison.csv", index=False)
    stats.to_csv(CSV_DIR / "statistics_comparison.csv", index=False)
    annual.to_csv(CSV_DIR / "annual_comparison.csv", index=False)
    seasonal.to_csv(CSV_DIR / "seasonal_comparison.csv", index=False)
    rankings.to_csv(CSV_DIR / "driver_rankings.csv", index=False)

    master = rankings.merge(freq[["Region", "Driver", "PValue", "CramersV"]], on=["Region", "Driver"])
    master = master.merge(lag[["Region", "Driver", "Duration_r", "Duration_p", "Intensity_r", "Intensity_p"]],
                          on=["Region", "Driver"])
    master = master.merge(seasonal[["Region", "Driver", "PValue"]].rename(columns={"PValue": "Seasonal_p"}),
                        on=["Region", "Driver"])
    master.to_csv(CSV_DIR / "master_comparison_summary.csv", index=False)

    print("\nGenerating figures...")
    plot_frequency_figures(freq)
    print("  [✓] frequency/")
    plot_lag_figures(lag, lag_curves)
    print("  [✓] lag/")
    plot_heatmaps(freq, lag, stats, annual, seasonal, rankings)
    print("  [✓] heatmaps/")
    plot_statistics_figures(desc)
    print("  [✓] statistics/")
    plot_annual_figures(annual_ts)
    print("  [✓] annual/")
    plot_seasonal_figures(season_tables)
    print("  [✓] seasonal/")
    plot_strength_figures(strength)
    print("  [✓] strength/")
    plot_ranking_figures(rankings)
    print("  [✓] rankings/")
    plot_dashboards(freq, lag, rankings, lag_curves)
    print("  [✓] dashboards/")

    print(f"\n{'=' * 80}")
    print("DRIVER RANKINGS")
    print(f"{'=' * 80}")
    for region in REGIONS:
        print(f"\n{region}:")
        sub = rankings[rankings.Region == region].sort_values("Rank")
        print(sub[["Driver", "Rank", "CompositeScore", "Significant_Tests"]].to_string(index=False))

    fig_count = sum(1 for _ in FIG_ROOT.rglob("*.png"))
    print(f"\n{'=' * 80}")
    print(f"COMPLETE — {fig_count} figures + {len(list(CSV_DIR.glob('*.csv')))} CSVs")
    print(f"Output: {OUT}")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    main()

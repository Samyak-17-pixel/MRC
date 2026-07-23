#!/usr/bin/env python3
"""
Generate Publication Tables & Figures
------------------------------------
Creates a single, well-organized folder of clearly named tables and figures
covering project results to date.

Output:
  outputs/publication/
    tables/   (PNG + PDF table renders + CSV backups)
    figures/  (core graphs)
    dashboards/
    index/figure_table_index.csv
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE = Path("/home/samyak/mrc_ws")
RESULTS = BASE / "outputs"
OUT = RESULTS / "publication"

DIRS = {
    "tables": OUT / "tables",
    "figures": OUT / "figures",
    "dashboards": OUT / "dashboards",
    "index": OUT / "index",
}

def ensure_dirs():
    for p in DIRS.values():
        p.mkdir(parents=True, exist_ok=True)

def save_fig(path_stem: Path):
    path_stem.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()

def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return pd.read_csv(path)

def render_table_png_pdf(df: pd.DataFrame, title: str, out_stem: Path, fontsize: int = 10):
    fig_w = max(10, 0.9 * df.shape[1])
    fig_h = max(2.5, 0.35 * (df.shape[0] + 1))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    tbl = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(fontsize)
    tbl.scale(1, 1.3)
    ax.set_title(title, fontweight="bold", pad=12)
    save_fig(out_stem)

def fig_events_by_region(master_summary: pd.DataFrame):
    df = master_summary.copy()
    df["Region"] = df["Region"].astype(str)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["Region"], df["Events"], color=["#2ecc71", "#3498db", "#e74c3c"], edgecolor="black")
    for i, v in enumerate(df["Events"]):
        ax.text(i, v + 1, str(int(v)), ha="center", fontweight="bold")
    ax.set_title("F01 — Total MHW Events by Region (2006–2025)", fontweight="bold")
    ax.set_ylabel("Number of events")
    ax.grid(axis="y", alpha=0.3)
    save_fig(DIRS["figures"] / "F01_events_by_region")

def fig_weak_wind_by_region(master_summary: pd.DataFrame):
    df = master_summary.copy()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["Region"], df["Pct_Weak_Wind"], color="#4c72b0", edgecolor="black")
    for i, v in enumerate(df["Pct_Weak_Wind"]):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_title("F02 — Percent of MHWs During Weak Wind", fontweight="bold")
    ax.set_ylabel("% of events")
    ax.grid(axis="y", alpha=0.3)
    save_fig(DIRS["figures"] / "F02_weak_wind_percent")

def fig_driver_ranking_heatmap(driver_rankings: pd.DataFrame):
    pivot = driver_rankings.pivot(index="Region", columns="Driver", values="CompositeScore")
    pivot = pivot.loc[["North", "Central", "South"], ["ENSO", "IOD", "MEI"]]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns, fontweight="bold")
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index, fontweight="bold")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j]:.1f}", ha="center", va="center", fontweight="bold")
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Composite Score (higher = stronger influence)")
    ax.set_title("F03 — Climate Driver Composite Score Heatmap", fontweight="bold")
    save_fig(DIRS["figures"] / "F03_driver_composite_heatmap")

def fig_annual_event_counts():
    files = {
        "North": RESULTS / "mhw" / "annual_statistics" / "north_annual_stats.csv",
        "Central": RESULTS / "mhw" / "annual_statistics" / "central_annual_stats.csv",
        "South": RESULTS / "mhw" / "annual_statistics" / "south_annual_stats.csv",
    }
    dfs = {k: load_csv(v) for k, v in files.items()}

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    colors = {"North": "#2ecc71", "Central": "#3498db", "South": "#e74c3c"}
    for ax, (region, df) in zip(axes, dfs.items()):
        ax.plot(df["Year"], df["Event_Count"], marker="o", color=colors[region], linewidth=2)
        ax.set_title(f"{region} — Annual MHW Event Count", fontweight="bold")
        ax.set_ylabel("Events")
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("Year")
    fig.suptitle("F04 — Annual MHW Event Counts (2006–2025)", fontweight="bold", y=0.98)
    plt.tight_layout()
    save_fig(DIRS["figures"] / "F04_annual_event_counts")

def fig_ml_best_f1_heatmap():
    best = load_csv(BASE / "src/ml/outputs/metrics/best_models.csv")
    best["region"] = best["region"].astype(str).str.title()
    best["horizon"] = best["horizon"].astype(int)
    pivot = best.pivot(index="region", columns="horizon", values="f1").loc[["North", "Central", "South"], [3, 7, 14]]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(pivot.values, aspect="auto", cmap="Blues", vmin=0, vmax=max(0.45, float(np.nanmax(pivot.values))))
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels([f"{c}-day" for c in pivot.columns], fontweight="bold")
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index, fontweight="bold")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j]:.3f}", ha="center", va="center", fontweight="bold")
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("F1 (test 2022–2025)")
    ax.set_title("F05 — ML Best-Model F1 Heatmap (Onset Prediction)", fontweight="bold")
    save_fig(DIRS["figures"] / "F05_ml_best_f1_heatmap")

def dashboard_one_page(master_summary: pd.DataFrame, driver_rankings: pd.DataFrame):
    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.25)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar(master_summary["Region"], master_summary["Events"], color=["#2ecc71", "#3498db", "#e74c3c"], edgecolor="black")
    ax1.set_title("Events by region", fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.bar(master_summary["Region"], master_summary["Pct_Weak_Wind"], color="#4c72b0", edgecolor="black")
    ax2.set_ylim(0, 100)
    ax2.set_title("Weak-wind %", fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)

    pivot = driver_rankings.pivot(index="Region", columns="Driver", values="CompositeScore")
    pivot = pivot.loc[["North", "Central", "South"], ["ENSO", "IOD", "MEI"]]
    ax3 = fig.add_subplot(gs[0, 2])
    im = ax3.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
    ax3.set_xticks(range(pivot.shape[1])); ax3.set_xticklabels(pivot.columns, fontweight="bold")
    ax3.set_yticks(range(pivot.shape[0])); ax3.set_yticklabels(pivot.index, fontweight="bold")
    ax3.set_title("Driver composite score", fontweight="bold")
    fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)

    ax4 = fig.add_subplot(gs[1, 0:2])
    for region, color in [("North", "#2ecc71"), ("Central", "#3498db"), ("South", "#e74c3c")]:
        annual = load_csv(RESULTS / "mhw" / "annual_statistics" / f"{region.lower()}_annual_stats.csv")
        ax4.plot(annual["Year"], annual["Event_Count"], marker="o", label=region, color=color, linewidth=2)
    ax4.set_title("Annual event count", fontweight="bold")
    ax4.set_xlabel("Year")
    ax4.set_ylabel("Events")
    ax4.grid(alpha=0.3)
    ax4.legend()

    ax5 = fig.add_subplot(gs[1, 2])
    best = load_csv(BASE / "src/ml/outputs/metrics/best_models.csv")
    best["region"] = best["region"].astype(str).str.title()
    best["horizon"] = best["horizon"].astype(int)
    pivot2 = best.pivot(index="region", columns="horizon", values="f1").loc[["North", "Central", "South"], [3, 7, 14]]
    im2 = ax5.imshow(pivot2.values, aspect="auto", cmap="Blues", vmin=0, vmax=max(0.45, float(np.nanmax(pivot2.values))))
    ax5.set_xticks(range(pivot2.shape[1])); ax5.set_xticklabels([f"{c}d" for c in pivot2.columns], fontweight="bold")
    ax5.set_yticks(range(pivot2.shape[0])); ax5.set_yticklabels(pivot2.index, fontweight="bold")
    ax5.set_title("ML best F1", fontweight="bold")
    fig.colorbar(im2, ax=ax5, fraction=0.046, pad=0.04)

    fig.suptitle("D01 — Master Summary Dashboard (2006–2025)", fontweight="bold", fontsize=16, y=0.98)
    save_fig(DIRS["dashboards"] / "D01_master_summary_dashboard")

@dataclass
class IndexRow:
    kind: str
    code: str
    title: str
    path_png: str
    path_pdf: str

def build_index(rows: list[IndexRow]):
    df = pd.DataFrame([r.__dict__ for r in rows])
    df.to_csv(DIRS["index"] / "figure_table_index.csv", index=False)

def main():
    ensure_dirs()
    plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 600, "font.size": 11})

    index_rows: list[IndexRow] = []

    master_summary = load_csv(RESULTS / "master_event_catalogue/csv/regional_summary_statistics.csv")
    driver_rankings = load_csv(RESULTS / "climate_comparison/csv/driver_rankings.csv")
    best_models = load_csv(BASE / "src/ml/outputs/metrics/best_models.csv")

    t01 = master_summary.copy()
    t01_cols = [
        "Region", "Events", "Mean_Duration", "Mean_Max_Intensity", "Mean_Max_SST",
        "Pct_Weak_Wind", "Pct_El_Nino_ENSO", "Pct_Positive_IOD", "Pct_Reduced_SLHF",
    ]
    t01 = t01[t01_cols]
    t01.to_csv(DIRS["tables"] / "T01_regional_master_summary.csv", index=False)
    render_table_png_pdf(t01, "T01 — Regional Master Summary (117 Events)", DIRS["tables"] / "T01_regional_master_summary")
    index_rows.append(IndexRow("TABLE", "T01", "Regional master summary", str(DIRS["tables"] / "T01_regional_master_summary.png"), str(DIRS["tables"] / "T01_regional_master_summary.pdf")))

    t02 = driver_rankings[["Region", "Driver", "CompositeScore", "Rank", "Significant_Tests"]].copy()
    t02.to_csv(DIRS["tables"] / "T02_driver_rankings.csv", index=False)
    render_table_png_pdf(t02, "T02 — Climate Driver Rankings (Composite Score)", DIRS["tables"] / "T02_driver_rankings", fontsize=9)
    index_rows.append(IndexRow("TABLE", "T02", "Climate driver rankings", str(DIRS["tables"] / "T02_driver_rankings.png"), str(DIRS["tables"] / "T02_driver_rankings.pdf")))

    t03 = best_models[["region", "horizon", "model", "f1", "precision", "recall", "roc_auc", "pr_auc"]].copy()
    t03 = t03.rename(columns={"region": "Region", "horizon": "Horizon_Days", "model": "Best_Model"})
    t03.to_csv(DIRS["tables"] / "T03_ml_best_models.csv", index=False)
    render_table_png_pdf(t03, "T03 — ML Best Models (Test 2022–2025)", DIRS["tables"] / "T03_ml_best_models", fontsize=9)
    index_rows.append(IndexRow("TABLE", "T03", "ML best models (test)", str(DIRS["tables"] / "T03_ml_best_models.png"), str(DIRS["tables"] / "T03_ml_best_models.pdf")))

    fig_events_by_region(master_summary)
    index_rows.append(IndexRow("FIGURE", "F01", "Total MHW events by region", str(DIRS["figures"] / "F01_events_by_region.png"), str(DIRS["figures"] / "F01_events_by_region.pdf")))

    fig_weak_wind_by_region(master_summary)
    index_rows.append(IndexRow("FIGURE", "F02", "Weak-wind percent by region", str(DIRS["figures"] / "F02_weak_wind_percent.png"), str(DIRS["figures"] / "F02_weak_wind_percent.pdf")))

    fig_driver_ranking_heatmap(driver_rankings)
    index_rows.append(IndexRow("FIGURE", "F03", "Driver composite score heatmap", str(DIRS["figures"] / "F03_driver_composite_heatmap.png"), str(DIRS["figures"] / "F03_driver_composite_heatmap.pdf")))

    fig_annual_event_counts()
    index_rows.append(IndexRow("FIGURE", "F04", "Annual event count timelines", str(DIRS["figures"] / "F04_annual_event_counts.png"), str(DIRS["figures"] / "F04_annual_event_counts.pdf")))

    fig_ml_best_f1_heatmap()
    index_rows.append(IndexRow("FIGURE", "F05", "ML best-model F1 heatmap", str(DIRS["figures"] / "F05_ml_best_f1_heatmap.png"), str(DIRS["figures"] / "F05_ml_best_f1_heatmap.pdf")))

    dashboard_one_page(master_summary, driver_rankings)
    index_rows.append(IndexRow("DASHBOARD", "D01", "Master summary dashboard", str(DIRS["dashboards"] / "D01_master_summary_dashboard.png"), str(DIRS["dashboards"] / "D01_master_summary_dashboard.pdf")))

    build_index(index_rows)

    print("=" * 80)
    print("PUBLICATION OUTPUTS GENERATED")
    print(f"Output folder: {OUT}")
    print(f"Index: {DIRS['index'] / 'figure_table_index.csv'}")
    print("=" * 80)

if __name__ == "__main__":
    main()

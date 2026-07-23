#!/usr/bin/env python3
"""
Master MHW Event Catalogue
--------------------------
Combines every analyzed parameter for each Marine Heatwave event
into a single comprehensive table per region, plus visualizations.

Output:
    outputs/master_event_catalogue/
        csv/
        figures/
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from pathlib import Path

BASE = Path("/home/samyak/mrc_ws")
RESULTS = BASE / "outputs"
OUT = RESULTS / "master_event_catalogue"
CSV_DIR = OUT / "csv"
FIG_DIR = OUT / "figures"

for d in [CSV_DIR, FIG_DIR, FIG_DIR / "tables", FIG_DIR / "heatmaps",
          FIG_DIR / "timelines", FIG_DIR / "dashboards", FIG_DIR / "top_events"]:
    d.mkdir(parents=True, exist_ok=True)

REGIONS = ["north", "central", "south"]
REGION_LABELS = {"north": "North", "central": "Central", "south": "South"}

plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 600,
    "font.size": 10,
})


def save_fig(path_stem):
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()


def season(month):
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Pre-Monsoon"
    if month in [6, 7, 8, 9]:
        return "SW Monsoon"
    return "Post-Monsoon"


def load_sst_stats(region):
    sst = pd.read_csv(RESULTS / "timeseries" / f"{region}_bob_sst.csv")
    sst["Date"] = pd.to_datetime(sst["Date"])
    hobday = pd.read_csv(RESULTS / f"mhw/climatology/{region}_hobday.csv")
    return sst, hobday


def compute_event_sst(row, sst, hobday):
    start = pd.Timestamp(row["Start_Date"])
    end = pd.Timestamp(row["End_Date"])
    mask = (sst["Date"] >= start) & (sst["Date"] <= end)
    ev = sst.loc[mask].copy()
    if ev.empty:
        return {
            "Mean_SST_C": np.nan, "Max_SST_C": np.nan, "Min_SST_C": np.nan,
            "SST_Range_C": np.nan, "Mean_Threshold_C": np.nan,
            "Mean_SST_Above_Threshold_C": np.nan,
        }
    ev["DOY"] = ev["Date"].dt.dayofyear
    ev = ev.merge(hobday[["DOY", "Threshold90"]], on="DOY", how="left")
    ev["Above_Threshold"] = ev["SST"] - ev["Threshold90"]
    return {
        "Mean_SST_C": ev["SST"].mean(),
        "Max_SST_C": ev["SST"].max(),
        "Min_SST_C": ev["SST"].min(),
        "SST_Range_C": ev["SST"].max() - ev["SST"].min(),
        "Mean_Threshold_C": ev["Threshold90"].mean(),
        "Mean_SST_Above_Threshold_C": ev["Above_Threshold"].mean(),
    }


def build_region_catalogue(region):
    label = REGION_LABELS[region]

    base = pd.read_csv(RESULTS / f"mhw/catalogue/{region}_mhw_catalogue.csv")
    base["Start_Date"] = pd.to_datetime(base["Start_Date"])
    base["End_Date"] = pd.to_datetime(base["End_Date"])
    base["Region"] = label
    base["Event_ID"] = [f"{label[0]}{i:02d}" for i in range(1, len(base) + 1)]
    base["Year"] = base["Start_Date"].dt.year
    base["Season"] = base["Start_Date"].dt.month.apply(season)

    sst, hobday = load_sst_stats(region)
    sst_stats = base.apply(lambda r: pd.Series(compute_event_sst(r, sst, hobday)), axis=1)
    df = pd.concat([base, sst_stats], axis=1)

    df = df.rename(columns={
        "Mean_Intensity": "Mean_Intensity_C",
        "Max_Intensity": "Max_Intensity_C",
    })

    merges = [
        (f"enso/lag/{region}_enso_lag.csv", "Start_Date", {
            "ONI_0m": "ONI_0m", "ONI_1m": "ONI_1m", "ONI_2m": "ONI_2m",
            "ONI_3m": "ONI_3m", "ONI_6m": "ONI_6m", "ENSO_Phase": "ENSO_Phase",
        }),
        (f"iod/lag/{region}_iod_lag.csv", "Start_Date", {
            "DMI_0m": "DMI_0m", "DMI_1m": "DMI_1m", "DMI_2m": "DMI_2m",
            "DMI_3m": "DMI_3m", "DMI_6m": "DMI_6m", "IOD_Phase": "IOD_Phase",
            "IOD_Phase_1m": "IOD_Phase_1m", "IOD_Phase_6m": "IOD_Phase_6m",
        }),
        (f"mei/lag/{region}_mei_lag.csv", "Start_Date", {
            "MEI_0m": "MEI_0m", "MEI_1m": "MEI_1m", "MEI_2m": "MEI_2m",
            "MEI_3m": "MEI_3m", "MEI_6m": "MEI_6m", "MEI_Phase": "MEI_Phase",
            "MEI_Phase_6m": "MEI_Phase_6m",
        }),
        (f"drivers/wind/{region}_wind_mhw_analysis.csv", "Start_Date", {
            "Wind_30d_Before": "Wind_30d_Before_ms",
            "Wind_21d_Before": "Wind_21d_Before_ms",
            "Wind_14d_Before": "Wind_14d_Before_ms",
            "Wind_7d_Before": "Wind_7d_Before_ms",
            "Wind_During": "Wind_During_ms",
            "Change_30d": "Wind_Change_30d_ms",
            "Change_21d": "Wind_Change_21d_ms",
            "Change_14d": "Wind_Change_14d_ms",
            "Change_7d": "Wind_Change_7d_ms",
        }),
        (f"drivers/wind/{region}_wind_climatology_analysis.csv", "Start_Date", {
            "Wind_Climatology": "Wind_Climatology_ms",
            "Wind_Anomaly": "Wind_Anomaly_ms",
            "Classification": "Wind_Classification",
        }),
        (f"drivers/heat_flux_analysis/{region}_heat_flux_analysis.csv", "Start_Date", {
            "SLHF_Climatology": "SLHF_Climatology_Wm2",
            "SLHF_During": "SLHF_During_Wm2",
            "SLHF_Anomaly": "SLHF_Anomaly_Wm2",
            "SSHF_Climatology": "SSHF_Climatology_Wm2",
            "SSHF_During": "SSHF_During_Wm2",
            "SSHF_Anomaly": "SSHF_Anomaly_Wm2",
        }),
    ]

    for path, key, cols in merges:
        sub = pd.read_csv(RESULTS / path)
        sub[key] = pd.to_datetime(sub[key])
        keep = [key] + list(cols.keys())
        sub = sub[keep].rename(columns=cols)
        df = df.merge(sub, on="Start_Date", how="left")

    df["Weak_Wind_Event"] = df["Wind_Classification"] == "Weak"
    df["Reduced_Latent_Heat_Loss"] = df["SLHF_Anomaly_Wm2"] > 0
    df["Reduced_Sensible_Heat_Loss"] = df["SSHF_Anomaly_Wm2"] > 0

    col_order = [
        "Region", "Event_ID", "Year", "Season",
        "Start_Date", "End_Date", "Duration_Days",
        "Mean_SST_C", "Max_SST_C", "Min_SST_C", "SST_Range_C",
        "Mean_Threshold_C", "Mean_SST_Above_Threshold_C",
        "Mean_Intensity_C", "Max_Intensity_C",
        "ONI_0m", "ONI_1m", "ONI_2m", "ONI_3m", "ONI_6m", "ENSO_Phase",
        "DMI_0m", "DMI_1m", "DMI_2m", "DMI_3m", "DMI_6m", "IOD_Phase",
        "IOD_Phase_1m", "IOD_Phase_6m",
        "MEI_0m", "MEI_1m", "MEI_2m", "MEI_3m", "MEI_6m", "MEI_Phase",
        "MEI_Phase_6m",
        "Wind_30d_Before_ms", "Wind_21d_Before_ms", "Wind_14d_Before_ms",
        "Wind_7d_Before_ms", "Wind_During_ms",
        "Wind_Change_30d_ms", "Wind_Change_21d_ms", "Wind_Change_14d_ms",
        "Wind_Change_7d_ms",
        "Wind_Climatology_ms", "Wind_Anomaly_ms", "Wind_Classification",
        "Weak_Wind_Event",
        "SLHF_Climatology_Wm2", "SLHF_During_Wm2", "SLHF_Anomaly_Wm2",
        "SSHF_Climatology_Wm2", "SSHF_During_Wm2", "SSHF_Anomaly_Wm2",
        "Reduced_Latent_Heat_Loss", "Reduced_Sensible_Heat_Loss",
    ]
    existing = [c for c in col_order if c in df.columns]
    extra = [c for c in df.columns if c not in existing]
    df = df[existing + extra]

    return df.round(4)


def plot_table_sections(df, region):
    label = REGION_LABELS[region]
    sections = [
        ("Event Details & SST", [
            "Event_ID", "Start_Date", "End_Date", "Duration_Days", "Season",
            "Mean_SST_C", "Max_SST_C", "Min_SST_C", "Mean_Intensity_C", "Max_Intensity_C",
        ]),
        ("Climate Indices", [
            "Event_ID", "ENSO_Phase", "ONI_0m", "ONI_6m",
            "IOD_Phase", "DMI_0m", "DMI_6m",
            "MEI_Phase", "MEI_0m", "MEI_6m",
        ]),
        ("Wind Conditions", [
            "Event_ID", "Wind_During_ms", "Wind_Climatology_ms", "Wind_Anomaly_ms",
            "Wind_Classification", "Wind_Change_30d_ms", "Wind_Change_7d_ms",
        ]),
        ("Heat Flux", [
            "Event_ID", "SLHF_During_Wm2", "SLHF_Anomaly_Wm2",
            "SSHF_During_Wm2", "SSHF_Anomaly_Wm2",
            "Reduced_Latent_Heat_Loss", "Reduced_Sensible_Heat_Loss",
        ]),
    ]

    for sec_name, cols in sections:
        cols = [c for c in cols if c in df.columns]
        sub = df[cols].copy()
        for c in sub.columns:
            if sub[c].dtype == "datetime64[ns]":
                sub[c] = sub[c].dt.strftime("%Y-%m-%d")
            elif sub[c].dtype in [np.float64, float]:
                sub[c] = sub[c].round(3)
        sub = sub.fillna("—")

        n_rows = len(sub)
        fig_h = max(4, 0.35 * n_rows + 1.5)
        fig, ax = plt.subplots(figsize=(min(20, 2 * len(cols)), fig_h))
        ax.axis("off")
        table = ax.table(
            cellText=sub.values,
            colLabels=sub.columns,
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(7)
        table.scale(1, 1.4)
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_facecolor("#2c3e50")
                cell.set_text_props(color="white", fontweight="bold")
            elif row % 2 == 0:
                cell.set_facecolor("#ecf0f1")
        ax.set_title(f"{label} BoB — {sec_name}\n({n_rows} Marine Heatwave Events)",
                     fontweight="bold", fontsize=12, pad=20)
        fname = sec_name.lower().replace(" ", "_").replace("&", "and")
        save_fig(FIG_DIR / "tables" / f"{region}_{fname}_table")


def plot_full_summary_table(df, region):
    """Compact summary table with key columns only."""
    label = REGION_LABELS[region]
    key_cols = [
        "Event_ID", "Start_Date", "Duration_Days", "Max_SST_C", "Max_Intensity_C",
        "ENSO_Phase", "IOD_Phase", "MEI_Phase",
        "Wind_Classification", "Weak_Wind_Event",
        "SLHF_Anomaly_Wm2", "SSHF_Anomaly_Wm2",
    ]
    cols = [c for c in key_cols if c in df.columns]
    sub = df[cols].copy()
    sub["Start_Date"] = sub["Start_Date"].dt.strftime("%Y-%m-%d")
    sub = sub.round(3).fillna("—")

    n_rows = len(sub)
    fig, ax = plt.subplots(figsize=(18, max(4, 0.3 * n_rows + 1)))
    ax.axis("off")
    table = ax.table(cellText=sub.values, colLabels=sub.columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.3)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1a5276")
            cell.set_text_props(color="white", fontweight="bold")
    ax.set_title(f"{label} — Master Event Summary Table", fontweight="bold", fontsize=13, pad=15)
    save_fig(FIG_DIR / "tables" / f"{region}_master_summary_table")


def nice_label(col):
    """Convert column name to readable axis label."""
    return col.replace("_", " ")


def zscore_normalize(data):
    """Column-wise z-score with safe handling for zero std and NaN."""
    normed = data.astype(float).copy()
    for col in normed.columns:
        series = normed[col]
        std = series.std(skipna=True)
        if std == 0 or np.isnan(std):
            normed[col] = 0.0
        else:
            normed[col] = (series - series.mean(skipna=True)) / std
    return normed


def plot_parameter_heatmap(df, region):
    label = REGION_LABELS[region]
    numeric_cols = [
        "Duration_Days", "Mean_SST_C", "Max_SST_C", "Min_SST_C",
        "Mean_Intensity_C", "Max_Intensity_C",
        "ONI_0m", "DMI_0m", "MEI_0m",
        "Wind_During_ms", "Wind_Anomaly_ms",
        "SLHF_Anomaly_Wm2", "SSHF_Anomaly_Wm2",
    ]
    cols = [c for c in numeric_cols if c in df.columns]
    data = df[cols].copy()
    normed = zscore_normalize(data)
    matrix = np.ma.masked_invalid(normed.values)

    n_events, n_cols = matrix.shape
    fig_w = max(14, 0.9 * n_cols)
    fig_h = max(6, 0.28 * n_events)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    cmap = plt.cm.RdBu_r.copy()
    cmap.set_bad(color="#d9d9d9")
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=-2, vmax=2,
                   interpolation="nearest")
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels([nice_label(c) for c in cols], rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(n_events))
    ax.set_yticklabels(df["Event_ID"].values, fontsize=7)
    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_events, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.6)
    cbar = plt.colorbar(im, ax=ax, label="Z-score", fraction=0.025, pad=0.02)
    cbar.ax.tick_params(labelsize=8)
    ax.set_title(f"{label}: Event Parameter Heatmap (normalized)", fontweight="bold", pad=12)
    plt.tight_layout()
    save_fig(FIG_DIR / "heatmaps" / f"{region}_parameter_heatmap")

    col_labels = []
    matrix_cols = []

    flag_cols = ["Weak_Wind_Event", "Reduced_Latent_Heat_Loss", "Reduced_Sensible_Heat_Loss"]
    for c in flag_cols:
        if c in df.columns:
            col_labels.append(nice_label(c))
            matrix_cols.append(df[c].fillna(False).astype(int).values)

    phase_map = {
        "ENSO_Phase": {"El Nino": 1, "Neutral": 0, "La Nina": -1, "Unknown": 0},
        "IOD_Phase": {"Positive": 1, "Neutral": 0, "Negative": -1, "Unknown": 0},
        "MEI_Phase": {"El Nino": 1, "Neutral": 0, "La Nina": -1, "Unknown": 0},
    }
    for pc, mapping in phase_map.items():
        if pc in df.columns:
            col_labels.append(nice_label(pc))
            matrix_cols.append(df[pc].map(mapping).fillna(0).astype(float).values)

    if not matrix_cols:
        return

    flag_matrix = np.column_stack(matrix_cols)
    n_flags = flag_matrix.shape[1]
    fig, ax = plt.subplots(figsize=(max(10, 1.2 * n_flags), max(5, 0.28 * n_events)))
    im = ax.imshow(flag_matrix, aspect="auto", cmap="RdYlGn", vmin=-1, vmax=1,
                   interpolation="nearest")
    ax.set_xticks(range(n_flags))
    ax.set_xticklabels(col_labels, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(n_events))
    ax.set_yticklabels(df["Event_ID"].values, fontsize=7)
    ax.set_xticks(np.arange(-0.5, n_flags, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_events, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.6)
    cbar = plt.colorbar(im, ax=ax, ticks=[-1, 0, 1], fraction=0.025, pad=0.02)
    cbar.ax.set_yticklabels(["Negative / False", "Neutral", "Positive / True"], fontsize=8)
    ax.set_title(f"{label}: Phase & Flag Heatmap", fontweight="bold", pad=12)
    plt.tight_layout()
    save_fig(FIG_DIR / "heatmaps" / f"{region}_phase_flag_heatmap")


def plot_timeline(df, region):
    label = REGION_LABELS[region]
    fig, ax = plt.subplots(figsize=(16, max(5, 0.3 * len(df))))

    norm = Normalize(vmin=df["Max_Intensity_C"].min(), vmax=df["Max_Intensity_C"].max())
    cmap = plt.cm.YlOrRd

    for i, (_, row) in enumerate(df.iterrows()):
        start = row["Start_Date"]
        end = row["End_Date"]
        color = cmap(norm(row["Max_Intensity_C"]))
        ax.barh(i, (end - start).days + 1, left=start, height=0.6,
                color=color, edgecolor="black", linewidth=0.5)
        ax.text(start, i, f" {row['Event_ID']}", va="center", fontsize=7, fontweight="bold")

    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([
        f"{r['Event_ID']} | {r['Duration_Days']}d | {r['Max_Intensity_C']:.2f}°C"
        for _, r in df.iterrows()
    ], fontsize=7)
    ax.xaxis_date()
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.set_xlabel("Year")
    ax.set_title(f"{label}: MHW Event Timeline (color = Max Intensity)", fontweight="bold")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label="Max Intensity (°C)", fraction=0.02)
    plt.tight_layout()
    save_fig(FIG_DIR / "timelines" / f"{region}_event_timeline")

    fig, ax = plt.subplots(figsize=(16, max(5, 0.3 * len(df))))
    wind_colors = {"Weak": "#3498db", "Strong": "#e74c3c"}
    for i, (_, row) in enumerate(df.iterrows()):
        start = row["Start_Date"]
        end = row["End_Date"]
        wc = row.get("Wind_Classification", "Unknown")
        color = wind_colors.get(wc, "gray")
        ax.barh(i, (end - start).days + 1, left=start, height=0.6,
                color=color, edgecolor="black", linewidth=0.5)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["Event_ID"], fontsize=7)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_title(f"{label}: MHW Timeline (blue=Weak wind, red=Strong wind)", fontweight="bold")
    patches = [mpatches.Patch(color=c, label=l) for l, c in wind_colors.items()]
    ax.legend(handles=patches, loc="lower right")
    plt.tight_layout()
    save_fig(FIG_DIR / "timelines" / f"{region}_wind_timeline")


def plot_top_events(df, region, n=5):
    label = REGION_LABELS[region]
    for metric, title, fname in [
        ("Max_Intensity_C", "Strongest", "strongest"),
        ("Duration_Days", "Longest", "longest"),
    ]:
        top = df.nlargest(n, metric)
        fig, axes = plt.subplots(n, 1, figsize=(14, 3 * n))
        if n == 1:
            axes = [axes]

        for ax, (_, row) in zip(axes, top.iterrows()):
            categories = []
            values = []
            colors = []

            params = [
                ("Max SST (°C)", row.get("Max_SST_C"), "#e74c3c"),
                ("Max Intensity (°C)", row.get("Max_Intensity_C"), "#e67e22"),
                ("Duration (days)", row.get("Duration_Days"), "#3498db"),
                ("Wind During (m/s)", row.get("Wind_During_ms"), "#2ecc71"),
                ("ONI", row.get("ONI_0m"), "#9b59b6"),
                ("DMI", row.get("DMI_0m"), "#1abc9c"),
                ("MEI", row.get("MEI_0m"), "#f39c12"),
            ]
            for name, val, color in params:
                if not np.isnan(val) if isinstance(val, float) else val is not None:
                    categories.append(name)
                    values.append(val)
                    colors.append(color)

            bars = ax.barh(categories, values, color=colors, edgecolor="black")
            for b, v in zip(bars, values):
                ax.text(v, b.get_y() + b.get_height() / 2, f" {v:.2f}",
                        va="center", fontsize=9)
            ax.set_title(
                f"{row['Event_ID']} | {row['Start_Date'].strftime('%Y-%m-%d')} → "
                f"{row['End_Date'].strftime('%Y-%m-%d')} | "
                f"ENSO:{row.get('ENSO_Phase','?')} IOD:{row.get('IOD_Phase','?')} "
                f"Wind:{row.get('Wind_Classification','?')}",
                fontweight="bold", fontsize=10,
            )
            ax.grid(axis="x", alpha=0.3)

        fig.suptitle(f"{label}: Top {n} {title} Events", fontweight="bold", fontsize=13)
        fig.tight_layout()
        save_fig(FIG_DIR / "top_events" / f"{region}_top{n}_{fname}")


def plot_dashboard(df, region):
    label = REGION_LABELS[region]
    fig = plt.figure(figsize=(20, 14))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, 0])
    colors = ["#3498db" if w else "#e74c3c" for w in df["Weak_Wind_Event"]]
    ax1.scatter(df["Duration_Days"], df["Max_Intensity_C"], c=colors, s=60,
                edgecolor="black", linewidth=0.5)
    ax1.set_xlabel("Duration (days)")
    ax1.set_ylabel("Max Intensity (°C)")
    ax1.set_title("Duration vs Intensity", fontweight="bold")
    ax1.grid(alpha=0.3)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.scatter(df["Mean_SST_C"], df["Max_SST_C"], c=df["Max_Intensity_C"],
                cmap="YlOrRd", s=60, edgecolor="black")
    ax2.plot([df["Mean_SST_C"].min(), df["Max_SST_C"].max()],
             [df["Mean_SST_C"].min(), df["Max_SST_C"].max()], "k--", alpha=0.3)
    ax2.set_xlabel("Mean SST (°C)")
    ax2.set_ylabel("Max SST (°C)")
    ax2.set_title("SST during Events", fontweight="bold")
    ax2.grid(alpha=0.3)

    ax3 = fig.add_subplot(gs[0, 2])
    for i, (phase_col, colors_list) in enumerate([
        ("ENSO_Phase", ["tomato", "gray", "royalblue"]),
        ("IOD_Phase", ["firebrick", "gray", "royalblue"]),
        ("MEI_Phase", ["darkorange", "gray", "royalblue"]),
    ]):
        if phase_col in df.columns:
            counts = df[phase_col].value_counts()
            ax3.bar(i, counts.sum(), color="lightgray", edgecolor="black")
            bottom = 0
            for j, (phase, cnt) in enumerate(counts.items()):
                ax3.bar(i, cnt, bottom=bottom, color=colors_list[j % 3], label=phase if i == 0 else "")
                bottom += cnt
    ax3.set_xticks([0, 1, 2])
    ax3.set_xticklabels(["ENSO", "IOD", "MEI"])
    ax3.set_ylabel("Events")
    ax3.set_title("Phase Distribution", fontweight="bold")

    ax4 = fig.add_subplot(gs[1, 0])
    ax4.hist(df["Wind_Anomaly_ms"].dropna(), bins=15, color="steelblue", edgecolor="black")
    ax4.axvline(0, color="red", linestyle="--")
    ax4.set_xlabel("Wind Anomaly (m/s)")
    ax4.set_title("Wind Anomaly Distribution", fontweight="bold")

    ax5 = fig.add_subplot(gs[1, 1])
    ax5.scatter(df["SLHF_Anomaly_Wm2"], df["SSHF_Anomaly_Wm2"],
                c=df["Max_Intensity_C"], cmap="YlOrRd", s=50, edgecolor="black")
    ax5.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax5.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax5.set_xlabel("SLHF Anomaly")
    ax5.set_ylabel("SSHF Anomaly")
    ax5.set_title("Heat Flux Anomalies", fontweight="bold")

    ax6 = fig.add_subplot(gs[1, 2])
    season_order = ["Winter", "Pre-Monsoon", "SW Monsoon", "Post-Monsoon"]
    season_counts = df["Season"].value_counts().reindex(season_order, fill_value=0)
    season_counts.plot(kind="bar", ax=ax6, color="teal", edgecolor="black")
    ax6.set_title("Events by Season", fontweight="bold")
    plt.setp(ax6.xaxis.get_majorticklabels(), rotation=20)

    for j, (col, name) in enumerate([("ONI_0m", "ONI"), ("DMI_0m", "DMI"), ("MEI_0m", "MEI")]):
        ax = fig.add_subplot(gs[2, j])
        if col in df.columns:
            ax.scatter(df[col], df["Max_Intensity_C"], c=df["Duration_Days"],
                       cmap="viridis", s=50, edgecolor="black")
            ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
            ax.set_xlabel(name)
            ax.set_ylabel("Max Intensity (°C)")
            ax.set_title(f"{name} vs Intensity", fontweight="bold")
            ax.grid(alpha=0.3)

    fig.suptitle(f"{label} Bay of Bengal — Master Event Dashboard ({len(df)} events)",
                 fontweight="bold", fontsize=15)
    save_fig(FIG_DIR / "dashboards" / f"{region}_event_dashboard")


def plot_combined_overview(all_df):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    for region, ax in zip(REGION_LABELS.values(), axes.flat):
        sub = all_df[all_df.Region == region]
        ax.scatter(sub["Duration_Days"], sub["Max_Intensity_C"],
                   c=sub["Weak_Wind_Event"].map({True: "#3498db", False: "#e74c3c"}),
                   s=50, edgecolor="black", alpha=0.8)
        for _, row in sub.iterrows():
            ax.annotate(row["Event_ID"], (row["Duration_Days"], row["Max_Intensity_C"]),
                        fontsize=6, alpha=0.7)
        ax.set_xlabel("Duration (days)")
        ax.set_ylabel("Max Intensity (°C)")
        ax.set_title(f"{region} ({len(sub)} events)", fontweight="bold")
        ax.grid(alpha=0.3)

    fig.suptitle("All Regions: Duration vs Max Intensity\n(blue=weak wind, red=strong wind)",
                 fontweight="bold", fontsize=14)
    fig.tight_layout()
    save_fig(FIG_DIR / "dashboards" / "all_regions_overview")

    summary_rows = []
    for region in REGION_LABELS.values():
        sub = all_df[all_df.Region == region]
        summary_rows.append({
            "Region": region,
            "Events": len(sub),
            "Mean_Duration": sub["Duration_Days"].mean(),
            "Mean_Max_Intensity": sub["Max_Intensity_C"].mean(),
            "Mean_Max_SST": sub["Max_SST_C"].mean(),
            "Pct_Weak_Wind": 100 * sub["Weak_Wind_Event"].mean(),
            "Pct_El_Nino_ENSO": 100 * (sub["ENSO_Phase"] == "El Nino").mean(),
            "Pct_Positive_IOD": 100 * (sub["IOD_Phase"] == "Positive").mean(),
            "Pct_Reduced_SLHF": 100 * sub["Reduced_Latent_Heat_Loss"].mean(),
        })
    summary = pd.DataFrame(summary_rows).round(2)
    summary.to_csv(CSV_DIR / "regional_summary_statistics.csv", index=False)

    fig, ax = plt.subplots(figsize=(14, 3))
    ax.axis("off")
    table = ax.table(cellText=summary.values, colLabels=summary.columns,
                     loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1a5276")
            cell.set_text_props(color="white", fontweight="bold")
    ax.set_title("Regional Summary Statistics", fontweight="bold", fontsize=13, pad=15)
    save_fig(FIG_DIR / "tables" / "regional_summary_statistics_table")


def main():
    print("=" * 80)
    print("MASTER MHW EVENT CATALOGUE BUILDER")
    print("=" * 80)

    all_dfs = []
    for region in REGIONS:
        print(f"\nBuilding {REGION_LABELS[region]}...")
        df = build_region_catalogue(region)

        df.to_csv(CSV_DIR / f"{region}_master_event_catalogue.csv", index=False)

        basic_cols = [c for c in df.columns if any(
            x in c for x in ["Region", "Event", "Date", "Duration", "Season", "Year", "SST", "Intensity", "Threshold"]
        )]
        climate_cols = [c for c in df.columns if any(
            x in c for x in ["ONI", "DMI", "MEI", "ENSO", "IOD", "MEI_Phase"]
        )]
        wind_cols = [c for c in df.columns if "Wind" in c or "Weak_Wind" in c]
        flux_cols = [c for c in df.columns if "SLHF" in c or "SSHF" in c or "Heat" in c or "Reduced" in c]

        df[basic_cols].to_csv(CSV_DIR / f"{region}_01_event_sst.csv", index=False)
        df[["Event_ID", "Start_Date"] + [c for c in climate_cols if c not in ["Event_ID", "Start_Date"]]].to_csv(
            CSV_DIR / f"{region}_02_climate_indices.csv", index=False)
        df[["Event_ID", "Start_Date"] + [c for c in wind_cols if c not in ["Event_ID", "Start_Date"]]].to_csv(
            CSV_DIR / f"{region}_03_wind.csv", index=False)
        df[["Event_ID", "Start_Date"] + [c for c in flux_cols if c not in ["Event_ID", "Start_Date"]]].to_csv(
            CSV_DIR / f"{region}_04_heat_flux.csv", index=False)

        print(f"  Events: {len(df)}, Columns: {len(df.columns)}")
        print(f"  Generating figures...")
        plot_table_sections(df, region)
        plot_full_summary_table(df, region)
        plot_parameter_heatmap(df, region)
        plot_timeline(df, region)
        plot_top_events(df, region)
        plot_dashboard(df, region)
        all_dfs.append(df)

    all_df = pd.concat(all_dfs, ignore_index=True)
    all_df.to_csv(CSV_DIR / "all_regions_master_event_catalogue.csv", index=False)

    glossary = pd.DataFrame({
        "Column": all_df.columns,
        "Description": [
            "Bay of Bengal sub-region" if c == "Region" else
            "Unique event identifier (N01, C01, S01...)" if c == "Event_ID" else
            "Year of event start" if c == "Year" else
            "Meteorological season at event start" if c == "Season" else
            "Event start/end dates" if "Date" in c else
            "Event length in days" if c == "Duration_Days" else
            "Mean/Max/Min SST during event (°C)" if "SST" in c and "Anomaly" not in c else
            "Hobday 90th percentile threshold (°C)" if "Threshold" in c else
            "MHW intensity above threshold (°C)" if "Intensity" in c else
            "Oceanic Niño Index at lag (months)" if "ONI" in c else
            "ENSO phase at event month" if c == "ENSO_Phase" else
            "Dipole Mode Index at lag (months)" if "DMI" in c else
            "IOD phase at event/lag month" if "IOD" in c else
            "MEI v2 at lag (months)" if "MEI" in c and "Phase" not in c else
            "MEI phase at event/lag month" if "MEI_Phase" in c else
            "Wind speed (m/s) before/during event" if "Wind" in c and "Classification" not in c and "Weak" not in c else
            "Wind vs climatology classification" if c == "Wind_Classification" else
            "True if wind below climatology during event" if c == "Weak_Wind_Event" else
            "Surface latent/sensible heat flux (W/m²)" if "SLHF" in c or "SSHF" in c else
            "True if reduced heat loss during event (positive anomaly)" if "Reduced" in c else
            c
            for c in all_df.columns
        ],
    })
    glossary.to_csv(CSV_DIR / "column_glossary.csv", index=False)

    plot_combined_overview(all_df)

    fig_count = sum(1 for _ in FIG_DIR.rglob("*.png"))
    print(f"\n{'=' * 80}")
    print(f"COMPLETE")
    print(f"  Total events: {len(all_df)}")
    print(f"  Total columns per event: {len(all_df.columns)}")
    print(f"  CSV files: {len(list(CSV_DIR.glob('*.csv')))}")
    print(f"  Figures: {fig_count}")
    print(f"  Output: {OUT}")
    print(f"{'=' * 80}")
    print("\nKey files:")
    print(f"  {CSV_DIR}/all_regions_master_event_catalogue.csv")
    print(f"  {CSV_DIR}/north_master_event_catalogue.csv")
    print(f"  {CSV_DIR}/column_glossary.csv")


if __name__ == "__main__":
    main()

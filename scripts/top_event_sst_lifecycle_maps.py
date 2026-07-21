#!/usr/bin/env python3
"""
Top-Event SST Lifecycle Maps
------------------------------
Spatial SST maps for top-10 strongest and top-10 longest MHWs per region.

For each event:
  - 5 daily maps BEFORE start
  - 5 daily maps DURING (peak-centered for strongest, evenly spaced for longest)
  - 5 daily maps AFTER end
  - Composites, anomaly maps, triptych, 5x3 grid, difference map

Output: results/top_event_sst_maps/
"""

import numpy as np
import pandas as pd
from pathlib import Path
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import cartopy.feature as cfeature

BASE = Path("/home/samyak/mrc_ws")

LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = 79, 100, 4, 25

RESULTS = BASE / "results"
OUT = RESULTS / "top_event_sst_maps"
SST_FILE = RESULTS / "combined_sst_2006_2025.nc"

REGIONS = ["north", "central", "south"]
REGION_LABELS = {"north": "North", "central": "Central", "south": "South"}
REGION_BOXES = {
    "north": {"lat": (15, 22), "lon": (85, 95)},
    "central": {"lat": (10, 15), "lon": (85, 95)},
    "south": {"lat": (5, 10), "lon": (85, 95)},
}

CATEGORIES = [
    ("strongest", "top10_strongest_{region}.csv", "Max_Intensity"),
    ("longest", "top10_longest_{region}.csv", "Duration_Days"),
]

plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 300, "font.size": 9})


def save_fig(path_stem, fig=None, pdf=True):
    if fig is None:
        fig = plt.gcf()
    fig.savefig(f"{path_stem}.png", dpi=300, bbox_inches="tight")
    if pdf:
        fig.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def event_id_for(region, start_date):
    master = pd.read_csv(RESULTS / "master_event_catalogue" / "csv" / f"{region}_master_event_catalogue.csv")
    master["Start_Date"] = pd.to_datetime(master["Start_Date"]).dt.strftime("%Y-%m-%d")
    match = master[master["Start_Date"] == start_date]
    if not match.empty:
        return match.iloc[0]["Event_ID"]
    return "UNK"


def load_event_list(region, category_key, fname_tpl):
    path = RESULTS / "top_events" / fname_tpl.format(region=region)
    df = pd.read_csv(path)
    df["Start_Date"] = pd.to_datetime(df["Start_Date"])
    df["End_Date"] = pd.to_datetime(df["End_Date"])
    df["Event_ID"] = df["Start_Date"].dt.strftime("%Y-%m-%d").apply(
        lambda d: event_id_for(region, d)
    )
    df["Region"] = REGION_LABELS[region]
    df["Rank"] = range(1, len(df) + 1)
    return df


def before_dates(start, n=5):
    return [start - pd.Timedelta(days=i) for i in range(n, 0, -1)]


def after_dates(end, n=5):
    return [end + pd.Timedelta(days=i) for i in range(1, n + 1)]


def during_dates_strongest(start, end, region, regional_sst):
    """5 days centered on peak regional intensity during the event."""
    hob = pd.read_csv(RESULTS / f"climatology/{region}_hobday.csv")
    mask = (regional_sst["Date"] >= start) & (regional_sst["Date"] <= end)
    ev = regional_sst.loc[mask].copy()
    if ev.empty:
        return pd.date_range(start, end, periods=5).tolist()
    ev["DOY"] = ev["Date"].dt.dayofyear
    ev = ev[ev["DOY"] != 366]
    ev = ev.merge(hob[["DOY", "Threshold90"]], on="DOY", how="left")
    ev["Intensity"] = ev["SST"] - ev["Threshold90"]
    peak = ev.loc[ev["Intensity"].idxmax(), "Date"]
    days = list(pd.date_range(peak - pd.Timedelta(days=2), peak + pd.Timedelta(days=2)))
    days = [d for d in days if start <= d <= end]
    while len(days) < 5:
        if days[0] > start:
            days.insert(0, days[0] - pd.Timedelta(days=1))
        elif days[-1] < end:
            days.append(days[-1] + pd.Timedelta(days=1))
        else:
            break
    return days[:5]


def during_dates_longest(start, end, n=5):
    """5 evenly spaced days across the event duration."""
    total = (end - start).days
    if total < n - 1:
        return pd.date_range(start, end, periods=min(n, total + 1)).tolist()
    offsets = np.linspace(0, total, n, dtype=int)
    return [start + pd.Timedelta(days=int(o)) for o in offsets]


def create_event_map(figsize=(7, 8)):
    """BoB map using locally cached 50m coastline only (no downloads)."""
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.8, edgecolor="black")
    ax.set_facecolor("#e8f4fc")
    return fig, ax


def draw_regions(ax):
    ax.plot([80, 100], [18, 18], transform=ccrs.PlateCarree(), color="red", linewidth=1.5)
    ax.plot([80, 100], [12, 12], transform=ccrs.PlateCarree(), color="red", linewidth=1.5)
    for y, name in [(21.5, "NORTH"), (15, "CENTRAL"), (8, "SOUTH")]:
        ax.text(90, y, name, fontsize=10, weight="bold", ha="center",
                transform=ccrs.PlateCarree())


def folder_name(rank, event_id, start):
    return f"rank{rank:02d}_{event_id}_{start.strftime('%Y-%m-%d')}"


def draw_region_box(ax, region):
    box = REGION_BOXES[region]
    lat0, lat1 = box["lat"]
    lon0, lon1 = box["lon"]
    lons = [lon0, lon1, lon1, lon0, lon0]
    lats = [lat0, lat0, lat1, lat1, lat0]
    ax.plot(lons, lats, transform=ccrs.PlateCarree(), color="gold",
            linewidth=2.5, linestyle="--", zorder=5)


def get_sst_field(ds, date, doy_clim):
    """Return SST and anomaly fields for a single date."""
    ts = pd.Timestamp(date)
    field = ds["thetao"].sel(time=ts, method="nearest").isel(depth=0)
    doy = ts.dayofyear
    if doy == 366:
        doy = 365
    clim = doy_clim.sel(dayofyear=doy, method="nearest")
    anomaly = field - clim
    return field, anomaly


def plot_map(field, title, outfile, vmin, vmax, cmap="turbo", cbar_label="SST (°C)",
             region=None, anomaly=False, save_pdf=False):
    fig, ax = create_event_map(figsize=(7, 8))
    draw_regions(ax)
    if region:
        draw_region_box(ax, region)

    pcm = ax.pcolormesh(
        field.longitude, field.latitude, field,
        transform=ccrs.PlateCarree(),
        cmap=cmap, vmin=vmin, vmax=vmax, shading="auto",
    )
    cbar = plt.colorbar(pcm, ax=ax, shrink=0.75, pad=0.02)
    cbar.set_label(cbar_label, fontsize=9)
    ax.set_title(title, fontweight="bold", fontsize=10)
    save_fig(outfile, fig, pdf=save_pdf)


def compute_vrange(fields):
    vals = [float(f.min()) for f in fields] + [float(f.max()) for f in fields]
    return min(vals), max(vals)


def mean_field(fields):
    return xr.concat(fields, dim="stack").mean("stack")


def plot_triptych(before, during, after, title, outfile, vmin, vmax, region):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6),
                             subplot_kw={"projection": ccrs.PlateCarree()})
    labels = ["Before (5-day mean)", "During (5-day mean)", "After (5-day mean)"]
    for ax, field, lbl in zip(axes, [before, during, after], labels):
        ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], ccrs.PlateCarree())
        ax.set_facecolor("#e8f4fc")
        ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.6)
        draw_regions(ax)
        draw_region_box(ax, region)
        pcm = ax.pcolormesh(field.longitude, field.latitude, field,
                            transform=ccrs.PlateCarree(),
                            cmap="turbo", vmin=vmin, vmax=vmax, shading="auto")
        ax.set_title(lbl, fontweight="bold")
    fig.colorbar(pcm, ax=axes, shrink=0.6, label="SST (°C)")
    fig.suptitle(title, fontweight="bold", fontsize=12)
    plt.tight_layout()
    save_fig(outfile, fig)


def plot_grid(daily_info, title, outfile, vmin, vmax, region):
    """5 rows (before/during/after) x 5 cols daily maps — actually 3x5 layout."""
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(3, 5, hspace=0.25, wspace=0.08)

    row_labels = ["Before", "During", "After"]
    for row, phase in enumerate(["before", "during", "after"]):
        for col, (date, field) in enumerate(daily_info[phase]):
            ax = fig.add_subplot(gs[row, col], projection=ccrs.PlateCarree())
            ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], ccrs.PlateCarree())
            ax.set_facecolor("#e8f4fc")
            ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.4)
            if col == 0:
                ax.text(-0.08, 0.5, row_labels[row], transform=ax.transAxes,
                        rotation=90, va="center", fontweight="bold", fontsize=10)
            pcm = ax.pcolormesh(field.longitude, field.latitude, field,
                                transform=ccrs.PlateCarree(),
                                cmap="turbo", vmin=vmin, vmax=vmax, shading="auto")
            ax.set_title(date.strftime("%Y-%m-%d"), fontsize=8)
            if row == 0 and col == 2:
                draw_region_box(ax, region)

    fig.colorbar(pcm, ax=fig.axes, shrink=0.5, label="SST (°C)", pad=0.02)
    fig.suptitle(title, fontweight="bold", fontsize=13)
    fig.subplots_adjust(top=0.92, bottom=0.05, left=0.04, right=0.92)
    save_fig(outfile, fig)


def plot_difference(field_a, field_b, title, outfile, region, vmax=None):
    diff = field_b - field_a
    if vmax is None:
        vmax = max(abs(float(diff.min())), abs(float(diff.max())), 0.1)
    fig, ax = create_event_map(figsize=(7, 8))
    draw_regions(ax)
    draw_region_box(ax, region)
    pcm = ax.pcolormesh(diff.longitude, diff.latitude, diff,
                        transform=ccrs.PlateCarree(),
                        cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="auto")
    plt.colorbar(pcm, ax=ax, shrink=0.75, label="ΔSST (°C)")
    ax.set_title(title, fontweight="bold")
    save_fig(outfile, fig)


def plot_mosaic(event_composites, title, outfile, vmin, vmax, region):
    n = len(event_composites)
    cols = 5
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(3.5 * cols, 3 * rows),
                             subplot_kw={"projection": ccrs.PlateCarree()})
    axes = np.atleast_2d(axes)
    for idx, (label, field) in enumerate(event_composites):
        r, c = divmod(idx, cols)
        ax = axes[r, c]
        ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], ccrs.PlateCarree())
        ax.set_facecolor("#e8f4fc")
        ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.4)
        pcm = ax.pcolormesh(field.longitude, field.latitude, field,
                            transform=ccrs.PlateCarree(),
                            cmap="turbo", vmin=vmin, vmax=vmax, shading="auto")
        ax.set_title(label, fontsize=8, fontweight="bold")
    for idx in range(n, rows * cols):
        r, c = divmod(idx, cols)
        axes[r, c].set_visible(False)
    fig.colorbar(pcm, ax=axes, shrink=0.6, label="SST (°C)", pad=0.02)
    fig.suptitle(title, fontweight="bold", fontsize=12)
    plt.tight_layout()
    save_fig(outfile, fig)


def process_event(ds, doy_clim, region, row, category, rank_metric_col, out_root):
    start = row["Start_Date"]
    end = row["End_Date"]
    event_id = row["Event_ID"]
    rank = row["Rank"]
    label = REGION_LABELS[region]

    ev_dir = out_root / region / folder_name(rank, event_id, start)
    for sub in ["daily/before", "daily/during", "daily/after",
                "daily/anomaly/before", "daily/anomaly/during", "daily/anomaly/after",
                "composites", "composites/anomaly", "summary"]:
        (ev_dir / sub).mkdir(parents=True, exist_ok=True)

    regional_sst = pd.read_csv(RESULTS / f"{region}_bob_sst.csv")
    regional_sst["Date"] = pd.to_datetime(regional_sst["Date"])

    days_before = before_dates(start)
    days_after = after_dates(end)
    if category == "strongest":
        days_during = during_dates_strongest(start, end, region, regional_sst)
    else:
        days_during = during_dates_longest(start, end)

    all_days = {
        "before": days_before,
        "during": days_during,
        "after": days_after,
    }

    # Pass 1: load all fields
    daily_info = {"before": [], "during": [], "after": []}
    daily_anom = {"before": [], "during": [], "after": []}
    sst_fields = []
    anomaly_fields = []

    for phase, dates in all_days.items():
        for date in dates:
            try:
                sst_f, anom_f = get_sst_field(ds, date, doy_clim)
            except Exception as e:
                print(f"    SKIP {date.strftime('%Y-%m-%d')}: {e}")
                continue
            sst_fields.append(sst_f)
            anomaly_fields.append(anom_f)
            daily_info[phase].append((date, sst_f))
            daily_anom[phase].append((date, anom_f))

    if not sst_fields:
        return None

    vmin, vmax = compute_vrange(sst_fields)
    anom_vmax = max(
        max(abs(float(a.min())), abs(float(a.max()))) for a in anomaly_fields
    )
    anom_vmax = max(anom_vmax, 0.5)

    # Pass 2: plot daily maps with consistent color scale
    for phase, pairs in daily_info.items():
        for i, (date, sst_f) in enumerate(pairs, 1):
            day_lbl = date.strftime("%Y-%m-%d")
            rank_str = f"day_{i:02d}_{day_lbl}"
            plot_map(
                sst_f,
                f"{label} {event_id} | {phase.upper()} | {day_lbl}",
                ev_dir / "daily" / phase / rank_str,
                vmin, vmax, region=region,
            )
            anom_f = daily_anom[phase][i - 1][1]
            plot_map(
                anom_f,
                f"{label} {event_id} | {phase.upper()} Anomaly | {day_lbl}",
                ev_dir / "daily" / "anomaly" / phase / rank_str,
                -anom_vmax, anom_vmax,
                cmap="RdBu_r", cbar_label="SST Anomaly (°C)",
                region=region, anomaly=True,
            )
    comp_before = mean_field([f for _, f in daily_info["before"]]) if daily_info["before"] else None
    comp_during = mean_field([f for _, f in daily_info["during"]]) if daily_info["during"] else None
    comp_after = mean_field([f for _, f in daily_info["after"]]) if daily_info["after"] else None

    meta_title = (
        f"{label} {event_id} | Rank {rank} | "
        f"{start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')} | "
        f"Duration {row['Duration_Days']}d | Max Intensity {row['Max_Intensity']:.2f}°C"
    )

    if comp_before is not None:
        plot_map(comp_before, f"{meta_title}\nBefore Composite", ev_dir / "composites" / "before_mean_5d",
                 vmin, vmax, region=region, save_pdf=True)
    if comp_during is not None:
        plot_map(comp_during, f"{meta_title}\nDuring Composite", ev_dir / "composites" / "during_mean_5d",
                 vmin, vmax, region=region, save_pdf=True)
    if comp_after is not None:
        plot_map(comp_after, f"{meta_title}\nAfter Composite", ev_dir / "composites" / "after_mean_5d",
                 vmin, vmax, region=region, save_pdf=True)

    if comp_before is not None and comp_during is not None and comp_after is not None:
        plot_triptych(comp_before, comp_during, comp_after,
                      meta_title, ev_dir / "summary" / "triptych_before_during_after",
                      vmin, vmax, region)
        plot_difference(comp_before, comp_during,
                        f"{meta_title}\nDuring − Before",
                        ev_dir / "summary" / "difference_during_minus_before", region)
        plot_difference(comp_during, comp_after,
                        f"{meta_title}\nAfter − During",
                        ev_dir / "summary" / "difference_after_minus_during", region)

    if all(len(daily_info[p]) == 5 for p in daily_info):
        plot_grid(daily_info, meta_title, ev_dir / "summary" / "lifecycle_grid_5x3",
                  vmin, vmax, region)

    return {
        "Region": label,
        "Category": category,
        "Rank": rank,
        "Event_ID": event_id,
        "Start_Date": start.strftime("%Y-%m-%d"),
        "End_Date": end.strftime("%Y-%m-%d"),
        "Duration_Days": row["Duration_Days"],
        "Max_Intensity": row["Max_Intensity"],
        "Output_Dir": str(ev_dir.relative_to(OUT)),
        "During_Dates": ", ".join(d.strftime("%Y-%m-%d") for d in days_during),
    }, comp_during


def main():
    print("=" * 72)
    print("TOP-EVENT SST LIFECYCLE MAPS")
    print("=" * 72)

    for d in ["index", "strongest", "longest",
              "strongest/north", "strongest/central", "strongest/south",
              "longest/north", "longest/central", "longest/south",
              "mosaics/strongest", "mosaics/longest"]:
        (OUT / d).mkdir(parents=True, exist_ok=True)

    print("\nLoading SST dataset...")
    ds = xr.open_dataset(SST_FILE)
    ds = ds.sel(
        latitude=slice(LAT_MIN, LAT_MAX),
        longitude=slice(LON_MIN, LON_MAX),
    )
    sst_all = ds["thetao"].isel(depth=0)

    print("Computing day-of-year climatology...")
    doy_clim = sst_all.groupby("time.dayofyear").mean("time")

    index_rows = []

    for cat_key, fname_tpl, metric_col in CATEGORIES:
        print(f"\n{'='*40}\nCategory: {cat_key.upper()}\n{'='*40}")
        cat_root = OUT / cat_key

        for region in REGIONS:
            print(f"\n  Region: {REGION_LABELS[region]}")
            events = load_event_list(region, cat_key, fname_tpl)
            mosaic_data = []

            for _, row in events.iterrows():
                print(f"    {row['Rank']:02d}. {row['Event_ID']} "
                      f"({row['Start_Date'].strftime('%Y-%m-%d')})")
                result = process_event(
                    ds, doy_clim, region, row, cat_key, metric_col, cat_root
                )
                if result:
                    info, comp_during = result
                    index_rows.append(info)
                    if comp_during is not None:
                        mosaic_data.append((
                            f"#{row['Rank']} {row['Event_ID']}",
                            comp_during,
                        ))

            if mosaic_data:
                fields = [f for _, f in mosaic_data]
                vmin, vmax = compute_vrange(fields)
                plot_mosaic(
                    mosaic_data,
                    f"{REGION_LABELS[region]} — Top 10 {cat_key.title()} "
                    f"(During Composite)",
                    OUT / "mosaics" / cat_key / f"{region}_during_mosaic",
                    vmin, vmax, region,
                )

    index_df = pd.DataFrame(index_rows)
    index_df.to_csv(OUT / "index" / "all_events_index.csv", index=False)
    for cat in ["strongest", "longest"]:
        sub = index_df[index_df["Category"] == cat]
        if not sub.empty:
            sub.to_csv(OUT / "index" / f"{cat}_events_index.csv", index=False)

    ds.close()

    print("\n" + "=" * 72)
    print("COMPLETE")
    print(f"  Events processed: {len(index_rows)}")
    print(f"  Output: {OUT}")
    print(f"  Index:  {OUT / 'index' / 'all_events_index.csv'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

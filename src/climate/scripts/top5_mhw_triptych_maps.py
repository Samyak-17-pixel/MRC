#!/usr/bin/env python3
"""
Top-5 MHW Triptych Heatmap-Maps (Before / During / After)
---------------------------------------------------------
Generates spatial SST "heatmap" maps for only:
  1) Top 5 longest MHWs (by Duration_Days)
  2) Top 5 highest-intensity MHWs (by Max_Intensity_C)

For each selected event, saves:
  - SST triptych (Before / During / After) using 5-day means
  - SST anomaly triptych (vs day-of-year climatology; computed from dataset)
  - Individual before/during/after composite maps

Output:
  outputs/publication/figures/07_top5_triptychs/
    longest/
    strongest/
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import cartopy.feature as cfeature

BASE = Path("/home/samyak/mrc_ws")
RESULTS = BASE / "outputs"

MASTER = RESULTS / "master_event_catalogue/csv/all_regions_master_event_catalogue.csv"
SST_FILE = RESULTS / "timeseries" / "combined_sst_2006_2025.nc"

OUT = RESULTS / "publication" / "figures" / "07_top5_triptychs"

LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = 79, 100, 4, 25
REGION_BOXES = {
    "North": {"lat": (15, 22), "lon": (85, 95)},
    "Central": {"lat": (10, 15), "lon": (85, 95)},
    "South": {"lat": (5, 10), "lon": (85, 95)},
}


def save_fig(path_stem: Path):
    path_stem.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(f"{path_stem}.png", dpi=600, bbox_inches="tight")
    plt.savefig(f"{path_stem}.pdf", bbox_inches="tight")
    plt.close()


def create_map_ax(fig, subplot_spec=None):
    if subplot_spec is None:
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    else:
        ax = fig.add_subplot(subplot_spec, projection=ccrs.PlateCarree())
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], ccrs.PlateCarree())
    ax.set_facecolor("#e8f4fc")
    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.6)
    return ax


def draw_region_lines(ax):
    ax.plot([80, 100], [18, 18], transform=ccrs.PlateCarree(), color="red", linewidth=1.2)
    ax.plot([80, 100], [12, 12], transform=ccrs.PlateCarree(), color="red", linewidth=1.2)


def draw_region_box(ax, region_name: str):
    box = REGION_BOXES.get(region_name)
    if not box:
        return
    lat0, lat1 = box["lat"]
    lon0, lon1 = box["lon"]
    lons = [lon0, lon1, lon1, lon0, lon0]
    lats = [lat0, lat0, lat1, lat1, lat0]
    ax.plot(lons, lats, transform=ccrs.PlateCarree(), color="gold", linewidth=2.0, linestyle="--")


def compute_doy_climatology(sst_all: xr.DataArray) -> xr.DataArray:
    return sst_all.groupby("time.dayofyear").mean("time")


def five_day_mean(ds_sst: xr.DataArray, dates: list[pd.Timestamp]) -> xr.DataArray:
    times = [pd.Timestamp(d) for d in dates]
    fields = []
    for t in times:
        fields.append(ds_sst.sel(time=t, method="nearest"))
    return xr.concat(fields, dim="stack").mean("stack")


def before_dates(start: pd.Timestamp) -> list[pd.Timestamp]:
    return [start - pd.Timedelta(days=i) for i in range(5, 0, -1)]


def after_dates(end: pd.Timestamp) -> list[pd.Timestamp]:
    return [end + pd.Timedelta(days=i) for i in range(1, 6)]


def during_dates_peak_centered(start: pd.Timestamp, end: pd.Timestamp, region: str) -> list[pd.Timestamp]:
    """
    Pick peak day using regional SST vs Hobday threshold, then return ±2 days window (5 days).
    """
    ts = pd.read_csv(RESULTS / "timeseries" / f"{region.lower()}_bob_sst.csv")
    ts["Date"] = pd.to_datetime(ts["Date"])
    hob = pd.read_csv(RESULTS / "mhw" / "climatology" / f"{region.lower()}_hobday.csv")[["DOY", "Threshold90"]]

    ev = ts[(ts["Date"] >= start) & (ts["Date"] <= end)].copy()
    if ev.empty:
        total = max((end - start).days, 0)
        offsets = np.linspace(0, total, 5, dtype=int)
        return [start + pd.Timedelta(days=int(o)) for o in offsets]

    ev["DOY"] = ev["Date"].dt.dayofyear
    ev = ev[ev["DOY"] != 366]
    ev = ev.merge(hob, on="DOY", how="left")
    ev["Intensity"] = ev["SST"] - ev["Threshold90"]
    peak = ev.loc[ev["Intensity"].idxmax(), "Date"]

    days = list(pd.date_range(peak - pd.Timedelta(days=2), peak + pd.Timedelta(days=2), freq="D"))
    days = [d for d in days if start <= d <= end]
    while len(days) < 5:
        if days and days[0] > start:
            days.insert(0, days[0] - pd.Timedelta(days=1))
        elif days and days[-1] < end:
            days.append(days[-1] + pd.Timedelta(days=1))
        else:
            break
    return days[:5] if days else [start]


def plot_single(field: xr.DataArray, title: str, out_stem: Path, cmap: str, vmin, vmax, region: str, cbar_label: str):
    fig = plt.figure(figsize=(7.5, 7.5))
    ax = create_map_ax(fig)
    draw_region_lines(ax)
    draw_region_box(ax, region)
    pcm = ax.pcolormesh(
        field["longitude"], field["latitude"], field.values,
        transform=ccrs.PlateCarree(),
        shading="auto",
        cmap=cmap, vmin=vmin, vmax=vmax,
    )
    cb = plt.colorbar(pcm, ax=ax, shrink=0.75, pad=0.02)
    cb.set_label(cbar_label)
    ax.set_title(title, fontweight="bold", fontsize=10)
    save_fig(out_stem)


def plot_triptych(before: xr.DataArray, during: xr.DataArray, after: xr.DataArray,
                  title: str, out_stem: Path, cmap: str, vmin, vmax, region: str, cbar_label: str):
    fig = plt.figure(figsize=(19.5, 6.4))
    gs = gridspec.GridSpec(1, 4, figure=fig, width_ratios=[0.045, 1, 1, 1], wspace=0.10)
    cax = fig.add_subplot(gs[0, 0])

    axes = []
    for i in range(3):
        ax = fig.add_subplot(gs[0, i + 1], projection=ccrs.PlateCarree())
        ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], ccrs.PlateCarree())
        ax.set_facecolor("#e8f4fc")
        ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.6)
        draw_region_lines(ax)
        draw_region_box(ax, region)
        axes.append(ax)

    labels = ["Before (5-day mean)", "During (5-day mean)", "After (5-day mean)"]
    last_pcm = None
    for ax, field, lbl in zip(axes, [before, during, after], labels):
        pcm = ax.pcolormesh(
            field["longitude"], field["latitude"], field.values,
            transform=ccrs.PlateCarree(),
            shading="auto",
            cmap=cmap, vmin=vmin, vmax=vmax,
        )
        ax.set_title(lbl, fontweight="bold", fontsize=10)
        last_pcm = pcm

    fig.suptitle(title, fontweight="bold", fontsize=12, y=0.98)
    cbar = fig.colorbar(last_pcm, cax=cax)
    cbar.set_label(cbar_label)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.06)
    save_fig(out_stem)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    mhw = pd.read_csv(MASTER)
    mhw["Start_Date"] = pd.to_datetime(mhw["Start_Date"])
    mhw["End_Date"] = pd.to_datetime(mhw["End_Date"])

    top_longest = mhw.nlargest(5, "Duration_Days").copy()
    top_strongest = mhw.nlargest(5, "Max_Intensity_C").copy()

    ds = xr.open_dataset(SST_FILE)
    ds = ds.sel(latitude=slice(LAT_MIN, LAT_MAX), longitude=slice(LON_MIN, LON_MAX))
    sst_all = ds["thetao"].isel(depth=0)
    doy_clim = compute_doy_climatology(sst_all)

    def process_set(df: pd.DataFrame, category: str):
        cat_dir = OUT / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        index_rows = []

        for rank, (_, row) in enumerate(df.iterrows(), 1):
            region = str(row["Region"])
            event_id = str(row["Event_ID"])
            start = pd.Timestamp(row["Start_Date"])
            end = pd.Timestamp(row["End_Date"])
            duration = int(row["Duration_Days"])
            mx = float(row["Max_Intensity_C"])

            ev_dir = cat_dir / f"rank{rank:02d}_{region}_{event_id}_{start.strftime('%Y-%m-%d')}"
            ev_dir.mkdir(parents=True, exist_ok=True)

            b_dates = before_dates(start)
            d_dates = during_dates_peak_centered(start, end, region)
            a_dates = after_dates(end)

            b = five_day_mean(sst_all, b_dates)
            d = five_day_mean(sst_all, d_dates)
            a = five_day_mean(sst_all, a_dates)

            vmin = float(min(b.min(), d.min(), a.min()))
            vmax = float(max(b.max(), d.max(), a.max()))

            def mean_clim(dates):
                doys = [pd.Timestamp(x).dayofyear for x in dates]
                doys = [365 if x == 366 else x for x in doys]
                clim_fields = [doy_clim.sel(dayofyear=dy, method="nearest") for dy in doys]
                return xr.concat(clim_fields, dim="stack").mean("stack")

            b_anom = b - mean_clim(b_dates)
            d_anom = d - mean_clim(d_dates)
            a_anom = a - mean_clim(a_dates)
            anom_v = float(max(abs(b_anom).max(), abs(d_anom).max(), abs(a_anom).max()))
            anom_v = max(anom_v, 0.5)

            title = (
                f"{category.upper()} | {region} {event_id} | "
                f"{start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')} | "
                f"Dur={duration}d | MaxInt={mx:.3f}°C"
            )

            plot_triptych(b, d, a, title, ev_dir / "H01_triptych_sst", "turbo", vmin, vmax, region, "SST (°C)")
            plot_triptych(b_anom, d_anom, a_anom, title, ev_dir / "H02_triptych_anomaly", "RdBu_r", -anom_v, anom_v, region, "SST anomaly (°C)")

            plot_single(b, f"{title}\nBefore (5-day mean)", ev_dir / "before_sst", "turbo", vmin, vmax, region, "SST (°C)")
            plot_single(d, f"{title}\nDuring (5-day mean)", ev_dir / "during_sst", "turbo", vmin, vmax, region, "SST (°C)")
            plot_single(a, f"{title}\nAfter (5-day mean)", ev_dir / "after_sst", "turbo", vmin, vmax, region, "SST (°C)")

            index_rows.append({
                "category": category,
                "rank": rank,
                "region": region,
                "event_id": event_id,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "duration_days": duration,
                "max_intensity_c": mx,
                "before_dates": ", ".join(pd.Timestamp(x).strftime("%Y-%m-%d") for x in b_dates),
                "during_dates": ", ".join(pd.Timestamp(x).strftime("%Y-%m-%d") for x in d_dates),
                "after_dates": ", ".join(pd.Timestamp(x).strftime("%Y-%m-%d") for x in a_dates),
                "output_dir": str(ev_dir),
            })

        pd.DataFrame(index_rows).to_csv(cat_dir / "index.csv", index=False)

    process_set(top_longest, "longest")
    process_set(top_strongest, "strongest")

    ds.close()

    print("=" * 80)
    print("TOP-5 TRIPTYCH MAPS GENERATED")
    print(f"Output: {OUT}")
    print("=" * 80)


if __name__ == "__main__":
    main()


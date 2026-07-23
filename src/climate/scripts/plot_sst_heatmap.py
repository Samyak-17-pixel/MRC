#!/usr/bin/env python3

"""
==========================================================
Bay of Bengal SST Heatmap Generator
Maritime Research Center (MRC)

Usage:
python plot_sst_heatmap.py YYYY-MM-DD

Example:
python plot_sst_heatmap.py 2023-05-18
==========================================================
"""

import sys
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


DATASET_DIR = "/home/samyak/mrc_ws/data/raw"

DATASETS = [

    ("2006-01-01", "2010-12-31",
     "copernicus_daily_sst_1Jan2006_31Dec2010.nc"),

    ("2011-01-01", "2015-12-31",
     "copernicus_daily_sst_1Jan2011_31Dec2015.nc"),

    ("2016-01-01", "2020-12-31",
     "copernicus_daily_sst_1Jan2016_31Dec2020.nc"),

    ("2021-01-01", "2025-12-31",
     "copernicus_daily_sst_1Jan2021_31Dec2025.nc"),
]

OUTPUT_DIR = "/home/samyak/mrc_ws/outputs/maps/sst"

os.makedirs(OUTPUT_DIR, exist_ok=True)


if len(sys.argv) != 2:

    print("\nUsage:")
    print("python plot_sst_heatmap.py YYYY-MM-DD\n")
    sys.exit()

PLOT_DATE = sys.argv[1]


dataset_file = None

for start, end, fname in DATASETS:

    if start <= PLOT_DATE <= end:

        dataset_file = os.path.join(DATASET_DIR, fname)
        break

if dataset_file is None:

    raise ValueError("Date outside available datasets.")

print("\nDataset Selected")
print("------------------------------")
print(dataset_file)


print("\nLoading dataset...")

ds = xr.open_dataset(dataset_file)


lat = "latitude"
lon = "longitude"
sst = "thetao"


try:

    data = ds.sel(time=PLOT_DATE)[sst].isel(depth=0)

except Exception:

    print(f"\nDate {PLOT_DATE} not found.")
    sys.exit()


minimum = float(data.min())

maximum = float(data.max())

mean = float(data.mean())

print("\nStatistics")
print("------------------------------")
print(f"Minimum SST : {minimum:.2f} °C")
print(f"Maximum SST : {maximum:.2f} °C")
print(f"Mean SST    : {mean:.2f} °C")


fig = plt.figure(figsize=(10,8))

ax = plt.axes(projection=ccrs.PlateCarree())

ax.set_extent([80,100,5,25])

ax.add_feature(
    cfeature.LAND,
    facecolor="lightgray"
)

ax.add_feature(
    cfeature.COASTLINE,
    linewidth=0.8
)

ax.add_feature(
    cfeature.BORDERS,
    linewidth=0.5
)

gl = ax.gridlines(
    draw_labels=True,
    linestyle="--",
    alpha=0.5
)

gl.top_labels = False
gl.right_labels = False

pcm = ax.pcolormesh(

    ds[lon],
    ds[lat],
    data,

    cmap="turbo",

    shading="auto",

    transform=ccrs.PlateCarree()

)

cbar = plt.colorbar(
    pcm,
    shrink=0.8
)

cbar.set_label(
    "Sea Surface Temperature (°C)",
    fontsize=11
)

plt.title(

    f"Bay of Bengal Sea Surface Temperature\n"
    f"{PLOT_DATE}\n"
    "Copernicus GLORYS12V1",

    fontsize=14,
    weight="bold"

)

outfile = os.path.join(

    OUTPUT_DIR,

    f"sst_{PLOT_DATE}.png"

)

plt.savefig(

    outfile,

    dpi=300,

    bbox_inches="tight"

)

print("\nSaved Figure")
print("------------------------------")
print(outfile)

plt.show()

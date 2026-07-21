import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# ---------------------------------------------------
# CHANGE THIS TO YOUR SST FILE
# ---------------------------------------------------

FILE = "/home/samyak/mrc_ws/datasets/copernicus_daily_sst_1Jan2021_31Dec2025.nc"

# ---------------------------------------------------
# Load Dataset
# ---------------------------------------------------

print("Loading dataset...")

ds = xr.open_dataset(FILE)

print(ds)

# ---------------------------------------------------
# Find coordinate names automatically
# ---------------------------------------------------

lat_name = "latitude"
lon_name = "longitude"

# Automatically detect SST variable
if "thetao" in ds.data_vars:
    sst_name = "thetao"
elif "analysed_sst" in ds.data_vars:
    sst_name = "analysed_sst"
elif "sst" in ds.data_vars:
    sst_name = "sst"
else:
    raise ValueError(
        f"No SST variable found. Available variables: {list(ds.data_vars)}"
    )

print("Latitude :", lat_name)
print("Longitude:", lon_name)
print("SST:", sst_name)

# ---------------------------------------------------
# First Day
# ---------------------------------------------------

sst = ds[sst_name].isel(
    time=0,
    depth=0
)

plot_date = str(ds.time.values[0])[:10]

print(f"Plotting SST for {plot_date}")

# ---------------------------------------------------
# Plot
# ---------------------------------------------------

fig = plt.figure(figsize=(10,8))

ax = plt.axes(projection=ccrs.PlateCarree())

ax.set_extent([80,100,5,25])

ax.coastlines(resolution="10m", linewidth=0.8)

ax.add_feature(cfeature.LAND,
               facecolor="lightgray",
               edgecolor="black")

ax.add_feature(cfeature.BORDERS, linewidth=0.5)

gl = ax.gridlines(draw_labels=True,
                  linestyle="--",
                  linewidth=0.4)

gl.top_labels = False
gl.right_labels = False

pcm = ax.pcolormesh(
    ds[lon_name],
    ds[lat_name],
    sst,
    cmap="turbo",
    shading="auto",
    transform=ccrs.PlateCarree()
)

cbar = plt.colorbar(
    pcm,
    pad=0.02
)

cbar.set_label("Sea Surface Temperature (°C)", fontsize=11)

plt.title(
    f"Bay of Bengal Sea Surface Temperature\n"
    f"{plot_date} | Copernicus GLORYS12V1",
    fontsize=14,
    weight="bold"
)

outfile = f"/home/samyak/mrc_ws/results/maps/base/bob_sst_{plot_date}.png"

plt.savefig(
    outfile,
    dpi=300,
    bbox_inches="tight"
)

print(f"\nFigure saved to:\n{outfile}")

plt.show()
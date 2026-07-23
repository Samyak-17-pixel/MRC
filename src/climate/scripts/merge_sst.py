import xarray as xr

files = [

"/home/samyak/mrc_ws/data/raw/copernicus_daily_sst_1Jan2006_31Dec2010.nc",

"/home/samyak/mrc_ws/data/raw/copernicus_daily_sst_1Jan2011_31Dec2015.nc",

"/home/samyak/mrc_ws/data/raw/copernicus_daily_sst_1Jan2016_31Dec2020.nc",

"/home/samyak/mrc_ws/data/raw/copernicus_daily_sst_1Jan2021_31Dec2025.nc"

]

datasets = []

for f in files:

    print(f"Opening {f}")

    ds = xr.open_dataset(f)

    print(
        ds.time.min().values,
        "→",
        ds.time.max().values
    )

    datasets.append(ds)

combined = xr.concat(
    datasets,
    dim="time"
)

combined = combined.sortby("time")

combined.to_netcdf(
    "/home/samyak/mrc_ws/outputs/timeseries/combined_sst_2006_2025.nc"
)

print("\nSaved:")
print(
"/home/samyak/mrc_ws/outputs/timeseries/combined_sst_2006_2025.nc"
)

print("\nTime Range:")

print(
combined.time.min().values,
"→",
combined.time.max().values
)

print(
"\nTotal Days:",
len(combined.time)
)
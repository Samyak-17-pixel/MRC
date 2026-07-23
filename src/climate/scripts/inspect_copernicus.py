import xarray as xr

file = "/home/samyak/mrc_ws/data/raw/copernicus_daily_sst_data_2016_2025.nc"

ds = xr.open_dataset(file)

print(ds)

print("\nVariables:")
print(list(ds.data_vars))

print("\nCoordinates:")
print(list(ds.coords))

print("\nTime range:")
print(ds.time.min().values)
print(ds.time.max().values)

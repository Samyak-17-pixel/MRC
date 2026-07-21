import xarray as xr

file = "/home/samyak/mrc_ws/datasets/sst.day.mean.2021.nc"

ds = xr.open_dataset(file, engine="netcdf4")

print(ds)

import xarray as xr
import os

file = os.path.expanduser("~/mrc_ws/sst.day.mean.2025.nc")

ds = xr.open_dataset(file)

print(ds)
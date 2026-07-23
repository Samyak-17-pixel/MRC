import xarray as xr

file = "/home/samyak/mrc_ws/data/raw/Wind_speed_data_2006_2025/data_stream-oper_stepType-instant.nc"

ds = xr.open_dataset(file)

print(ds)

print("\nVariables:")
print(list(ds.data_vars))

print("\nCoordinates:")
print(list(ds.coords))

print("\nTime Range:")
print(ds.time.min().values)
print(ds.time.max().values)

print("\nDimensions:")
print(ds.dims)

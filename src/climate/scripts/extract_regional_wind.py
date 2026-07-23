import xarray as xr
import numpy as np
import pandas as pd

file = "/home/samyak/mrc_ws/data/raw/Wind_speed_data_2006_2025/data_stream-oper_stepType-instant.nc"

print("Opening wind dataset...")

ds = xr.open_dataset(file)


wind_speed = np.sqrt(
    ds["u10"]**2 +
    ds["v10"]**2
)


north = wind_speed.sel(
    latitude=slice(25,15),
    longitude=slice(80,100)
)

central = wind_speed.sel(
    latitude=slice(15,8),
    longitude=slice(80,100)
)

south = wind_speed.sel(
    latitude=slice(8,0),
    longitude=slice(80,100)
)


north_ts = north.mean(
    dim=["latitude","longitude"]
)

central_ts = central.mean(
    dim=["latitude","longitude"]
)

south_ts = south.mean(
    dim=["latitude","longitude"]
)


pd.DataFrame({

    "Date":
        ds.valid_time.values,

    "WindSpeed":
        north_ts.values

}).to_csv(

    "/home/samyak/mrc_ws/outputs/timeseries/north_wind.csv",

    index=False
)

pd.DataFrame({

    "Date":
        ds.valid_time.values,

    "WindSpeed":
        central_ts.values

}).to_csv(

    "/home/samyak/mrc_ws/outputs/timeseries/central_wind.csv",

    index=False
)

pd.DataFrame({

    "Date":
        ds.valid_time.values,

    "WindSpeed":
        south_ts.values

}).to_csv(

    "/home/samyak/mrc_ws/outputs/timeseries/south_wind.csv",

    index=False
)

print("\nSaved:")

print("north_wind.csv")
print("central_wind.csv")
print("south_wind.csv")

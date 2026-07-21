import xarray as xr
import pandas as pd

file = "/home/samyak/mrc_ws/results/combined_sst_2006_2025.nc"

ds = xr.open_dataset(file)

sst = ds["thetao"].isel(depth=0)

north = sst.sel(
    latitude=slice(15,22),
    longitude=slice(85,95)
)

central = sst.sel(
    latitude=slice(10,15),
    longitude=slice(85,95)
)

south = sst.sel(
    latitude=slice(5,10),
    longitude=slice(85,95)
)

north_ts = north.mean(dim=["latitude","longitude"])
central_ts = central.mean(dim=["latitude","longitude"])
south_ts = south.mean(dim=["latitude","longitude"])

pd.DataFrame({
    "Date": north_ts.time.values,
    "SST": north_ts.values
}).to_csv(
    "/home/samyak/mrc_ws/results/north_bob_sst.csv",
    index=False
)

pd.DataFrame({
    "Date": central_ts.time.values,
    "SST": central_ts.values
}).to_csv(
    "/home/samyak/mrc_ws/results/central_bob_sst.csv",
    index=False
)

pd.DataFrame({
    "Date": south_ts.time.values,
    "SST": south_ts.values
}).to_csv(
    "/home/samyak/mrc_ws/results/south_bob_sst.csv",
    index=False
)

print("Done")

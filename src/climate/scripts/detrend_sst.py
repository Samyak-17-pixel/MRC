import pandas as pd
from scipy.signal import detrend

for region in [
    "north",
    "central",
    "south"
]:

    df = pd.read_csv(
        f"/home/samyak/mrc_ws/outputs/timeseries/{region}_bob_sst.csv"
    )

    df["SST_detrended"] = detrend(df["SST"])

    df.to_csv(
        f"/home/samyak/mrc_ws/outputs/timeseries/{region}_bob_sst_detrended.csv",
        index=False
    )

print("Detrending complete")

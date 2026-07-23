import pandas as pd
from pathlib import Path

RESULTS = "/home/samyak/mrc_ws/outputs"

Path(f"{RESULTS}/mhw/climatology").mkdir(
    parents=True,
    exist_ok=True
)

regions = [
    "north",
    "central",
    "south"
]

for region in regions:

    print(f"\nProcessing {region}")

    df = pd.read_csv(
        f"{RESULTS}/timeseries/{region}_bob_sst.csv"
    )

    df["Date"] = pd.to_datetime(df["Date"])

    df["DOY"] = df["Date"].dt.dayofyear

    df = df[df["DOY"] != 366]

    climatology = (
        df.groupby("DOY")["SST"]
        .mean()
        .reset_index()
    )

    climatology.columns = [
        "DOY",
        "Climatology"
    ]

    threshold = (
        df.groupby("DOY")["SST"]
        .quantile(0.90)
        .reset_index()
    )

    threshold.columns = [
        "DOY",
        "Threshold90"
    ]

    climatology.to_csv(
        f"{RESULTS}/mhw/climatology/{region}_climatology.csv",
        index=False
    )

    threshold.to_csv(
        f"{RESULTS}/mhw/climatology/{region}_threshold.csv",
        index=False
    )

    print("Done")

print("\nAll climatology files created")

import pandas as pd
import numpy as np
from pathlib import Path

RESULTS = "/home/samyak/mrc_ws/results"

Path(
    f"{RESULTS}/climatology"
).mkdir(
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
        f"{RESULTS}/{region}_bob_sst.csv"
    )

    df["Date"] = pd.to_datetime(df["Date"])

    df["DOY"] = (
        df["Date"]
        .dt.dayofyear
    )

    # remove leap day

    df = df[
        df["DOY"] != 366
    ]

    climatology = []
    threshold = []

    for doy in range(1,366):

        window = []

        for offset in range(-5,6):

            day = doy + offset

            if day < 1:
                day += 365

            if day > 365:
                day -= 365

            window.extend(
                df.loc[
                    df["DOY"] == day,
                    "SST"
                ].values
            )

        climatology.append(
            np.mean(window)
        )

        threshold.append(
            np.percentile(
                window,
                90
            )
        )

    clim_df = pd.DataFrame({

        "DOY":
        np.arange(1,366),

        "Climatology":
        climatology,

        "Threshold90":
        threshold
    })

    # 31-day smoothing

    clim_df["Climatology"] = (

        clim_df["Climatology"]

        .rolling(
            31,
            center=True,
            min_periods=1
        )

        .mean()
    )

    clim_df["Threshold90"] = (

        clim_df["Threshold90"]

        .rolling(
            31,
            center=True,
            min_periods=1
        )

        .mean()
    )

    clim_df.to_csv(

        f"{RESULTS}/climatology/"
        f"{region}_hobday.csv",

        index=False
    )

    print("Done")

print("\nFinished")

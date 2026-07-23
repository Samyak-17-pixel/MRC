import pandas as pd
import numpy as np
from pathlib import Path

RESULTS = "/home/samyak/mrc_ws/outputs"

Path(f"{RESULTS}/mhw/catalogue").mkdir(
    parents=True,
    exist_ok=True
)

regions = ["north", "central", "south"]

for region in regions:

    print(f"\nProcessing {region}")

    sst = pd.read_csv(
        f"{RESULTS}/timeseries/{region}_bob_sst.csv"
    )

    sst["Date"] = pd.to_datetime(
        sst["Date"]
    )

    sst["DOY"] = sst["Date"].dt.dayofyear

    sst = sst[sst["DOY"] != 366]

    threshold = pd.read_csv(
    f"{RESULTS}/mhw/climatology/{region}_hobday.csv"
    )[["DOY","Threshold90"]]

    df = pd.merge(
        sst,
        threshold,
        on="DOY"
    )

    df["Intensity"] = (
        df["SST"] -
        df["Threshold90"]
    )

    df["Hot"] = (
        df["Intensity"] > 0
    )

    events = []

    in_event = False

    start_idx = None

    for i in range(len(df)):

        if df.loc[i, "Hot"] and not in_event:

            in_event = True
            start_idx = i

        elif not df.loc[i, "Hot"] and in_event:

            end_idx = i - 1

            duration = (
                end_idx -
                start_idx +
                1
            )

            if duration >= 5:

                event = df.iloc[
                    start_idx:end_idx+1
                ]

                events.append({

                    "Start_Date":
                        event["Date"].iloc[0],

                    "End_Date":
                        event["Date"].iloc[-1],

                    "Duration_Days":
                        duration,

                    "Mean_Intensity":
                        event["Intensity"].mean(),

                    "Max_Intensity":
                        event["Intensity"].max()
                })

            in_event = False

    events_df = pd.DataFrame(events)

    events_df.to_csv(

        f"{RESULTS}/mhw/catalogue/"
        f"{region}_mhw_catalogue.csv",

        index=False
    )

    print(
        f"Detected {len(events_df)} events"
    )

print("\nFinished")

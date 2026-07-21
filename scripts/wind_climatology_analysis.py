import pandas as pd
import numpy as np

regions = ["north", "central", "south"]

for region in regions:

    print(f"\nProcessing {region}")

    wind = pd.read_csv(
        f"/home/samyak/mrc_ws/results/{region}_wind.csv"
    )

    wind["Date"] = pd.to_datetime(
        wind["Date"]
    )

    wind["DOY"] = (
        wind["Date"]
        .dt.dayofyear
    )

    wind = wind[
        wind["DOY"] != 366
    ]

    # ----------------------------------
    # Wind Climatology
    # ----------------------------------

    clim = wind.groupby(
        "DOY"
    )["WindSpeed"].mean()

    wind["Wind_Climatology"] = (
        wind["DOY"]
        .map(clim)
    )

    wind["Wind_Anomaly"] = (

        wind["WindSpeed"]

        -

        wind["Wind_Climatology"]
    )

    mhw = pd.read_csv(
        f"/home/samyak/mrc_ws/results/mhw_catalogue/{region}_mhw_catalogue.csv"
    )

    mhw["Start_Date"] = pd.to_datetime(
        mhw["Start_Date"]
    )

    mhw["End_Date"] = pd.to_datetime(
        mhw["End_Date"]
    )

    results = []

    for _, row in mhw.iterrows():

        event = wind[
            (wind["Date"] >= row["Start_Date"])
            &
            (wind["Date"] <= row["End_Date"])
        ]

        mean_wind = event[
            "WindSpeed"
        ].mean()

        mean_clim = event[
            "Wind_Climatology"
        ].mean()

        mean_anom = event[
            "Wind_Anomaly"
        ].mean()

        if mean_anom < 0:

            state = "Weak"

        else:

            state = "Strong"

        results.append({

            "Start_Date":
                row["Start_Date"],

            "End_Date":
                row["End_Date"],

            "Duration":
                row["Duration_Days"],

            "Wind_During":
                mean_wind,

            "Wind_Climatology":
                mean_clim,

            "Wind_Anomaly":
                mean_anom,

            "Classification":
                state
        })

    results = pd.DataFrame(
        results
    )

    results.to_csv(

        f"/home/samyak/mrc_ws/results/"
        f"wind_analysis/"
        f"{region}_wind_climatology_analysis.csv",

        index=False
    )

    weak = (
        results["Classification"]
        == "Weak"
    ).sum()

    strong = (
        results["Classification"]
        == "Strong"
    ).sum()

    print(
        f"Weak Wind Events: {weak}"
    )

    print(
        f"Strong Wind Events: {strong}"
    )

    print(
        f"Percent Weak: "
        f"{100*weak/len(results):.1f}%"
    )

print("\nFinished")

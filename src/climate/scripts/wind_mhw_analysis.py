import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS = "/home/samyak/mrc_ws/outputs"

Path(f"{RESULTS}/drivers/wind").mkdir(
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

    Path(
        f"{RESULTS}/drivers/wind/{region}_event_plots"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    wind = pd.read_csv(
        f"{RESULTS}/timeseries/{region}_wind.csv"
    )

    wind["Date"] = pd.to_datetime(
        wind["Date"]
    )

    mhw = pd.read_csv(
        f"{RESULTS}/mhw/catalogue/{region}_mhw_catalogue.csv"
    )

    mhw["Start_Date"] = pd.to_datetime(
        mhw["Start_Date"]
    )

    mhw["End_Date"] = pd.to_datetime(
        mhw["End_Date"]
    )

    output = []

    for idx, row in mhw.iterrows():

        start = row["Start_Date"]
        end = row["End_Date"]

        before30 = wind[
            (wind["Date"] >= start - pd.Timedelta(days=30))
            &
            (wind["Date"] < start)
        ]

        before21 = wind[
            (wind["Date"] >= start - pd.Timedelta(days=21))
            &
            (wind["Date"] < start)
        ]

        before14 = wind[
            (wind["Date"] >= start - pd.Timedelta(days=14))
            &
            (wind["Date"] < start)
        ]

        before7 = wind[
            (wind["Date"] >= start - pd.Timedelta(days=7))
            &
            (wind["Date"] < start)
        ]

        during = wind[
            (wind["Date"] >= start)
            &
            (wind["Date"] <= end)
        ]

        mean30 = before30["WindSpeed"].mean()
        mean21 = before21["WindSpeed"].mean()
        mean14 = before14["WindSpeed"].mean()
        mean7 = before7["WindSpeed"].mean()

        meanduring = during["WindSpeed"].mean()

        output.append({

            "Start_Date": start,
            "End_Date": end,

            "Duration":
                row["Duration_Days"],

            "Mean_Intensity":
                row["Mean_Intensity"],

            "Max_Intensity":
                row["Max_Intensity"],

            "Wind_30d_Before":
                mean30,

            "Wind_21d_Before":
                mean21,

            "Wind_14d_Before":
                mean14,

            "Wind_7d_Before":
                mean7,

            "Wind_During":
                meanduring,

            "Change_30d":
                meanduring - mean30,

            "Change_21d":
                meanduring - mean21,

            "Change_14d":
                meanduring - mean14,

            "Change_7d":
                meanduring - mean7
        })

        plot_data = wind[
            (wind["Date"] >= start - pd.Timedelta(days=30))
            &
            (wind["Date"] <= end + pd.Timedelta(days=15))
        ]

        plt.figure(figsize=(12,5))

        plt.plot(
            plot_data["Date"],
            plot_data["WindSpeed"]
        )

        plt.axvline(
            start,
            linestyle="--"
        )

        plt.axvline(
            end,
            linestyle="--"
        )

        plt.title(
            f"{region.upper()} | "
            f"{start.date()} | "
            f"{row['Duration_Days']} days"
        )

        plt.ylabel(
            "Wind Speed (m/s)"
        )

        plt.grid()

        plt.tight_layout()

        plt.savefig(

            f"{RESULTS}/drivers/wind/"
            f"{region}_event_plots/"
            f"event_{idx+1}.png",

            dpi=300
        )

        plt.close()

    pd.DataFrame(output).to_csv(

        f"{RESULTS}/drivers/wind/"
        f"{region}_wind_mhw_analysis.csv",

        index=False
    )

    print(
        f"Saved {region}"
    )

print("\nDone")

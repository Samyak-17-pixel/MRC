import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS = "/home/samyak/mrc_ws/outputs"

Path(f"{RESULTS}/mhw/annual_statistics").mkdir(exist_ok=True)

Path(f"{RESULTS}/mhw/top_events").mkdir(exist_ok=True)

Path(f"{RESULTS}/mhw/event_reports/north").mkdir(
    parents=True,
    exist_ok=True
)

Path(f"{RESULTS}/mhw/event_reports/central").mkdir(
    parents=True,
    exist_ok=True
)

Path(f"{RESULTS}/mhw/event_reports/south").mkdir(
    parents=True,
    exist_ok=True
)

regions = [
    "north",
    "central",
    "south"
]

summary_text = []

for region in regions:

    print(f"\nProcessing {region}")

    df = pd.read_csv(
        f"{RESULTS}/mhw/catalogue/{region}_mhw_catalogue.csv"
    )

    df["Start_Date"] = pd.to_datetime(
        df["Start_Date"]
    )

    df["End_Date"] = pd.to_datetime(
        df["End_Date"]
    )

    df["Year"] = df["Start_Date"].dt.year

    annual = df.groupby("Year").agg({

        "Duration_Days":
            ["count",
             "mean",
             "max"],

        "Mean_Intensity":
            "mean",

        "Max_Intensity":
            "max"

    })

    annual.columns = [

        "Event_Count",
        "Mean_Duration",
        "Max_Duration",
        "Mean_Intensity",
        "Max_Intensity"

    ]

    annual = annual.reset_index()

    annual.to_csv(

        f"{RESULTS}/mhw/annual_statistics/"
        f"{region}_annual_stats.csv",

        index=False
    )

    for year in sorted(df["Year"].unique()):

        yearly = df[
            df["Year"] == year
        ]

        yearly.to_csv(

            f"{RESULTS}/mhw/event_reports/"
            f"{region}/"
            f"{year}_events.csv",

            index=False
        )

    longest = (

        df.sort_values(
            "Duration_Days",
            ascending=False
        )

        .head(10)

    )

    longest.to_csv(

        f"{RESULTS}/mhw/top_events/"
        f"top10_longest_{region}.csv",

        index=False
    )

    strongest = (

        df.sort_values(
            "Max_Intensity",
            ascending=False
        )

        .head(10)

    )

    strongest.to_csv(

        f"{RESULTS}/mhw/top_events/"
        f"top10_strongest_{region}.csv",

        index=False
    )

    summary_text.append(
        f"\n{region.upper()}\n"
    )

    summary_text.append(
        f"Total Events: {len(df)}\n"
    )

    summary_text.append(
        f"Longest Event: "
        f"{df['Duration_Days'].max()} days\n"
    )

    summary_text.append(
        f"Strongest Event: "
        f"{df['Max_Intensity'].max():.3f} C\n"
    )

    plt.figure(figsize=(10,5))

    plt.plot(
        annual["Year"],
        annual["Event_Count"],
        marker="o"
    )

    plt.title(
        f"{region.capitalize()} MHW Count"
    )

    plt.xlabel("Year")
    plt.ylabel("Count")

    plt.grid()

    plt.tight_layout()

    plt.savefig(

        f"{RESULTS}/mhw/figures/"
        f"{region}_count_vs_year.png",

        dpi=300
    )

    plt.close()

    plt.figure(figsize=(10,5))

    plt.plot(
        annual["Year"],
        annual["Mean_Duration"],
        marker="o"
    )

    plt.title(
        f"{region.capitalize()} Mean Duration"
    )

    plt.xlabel("Year")
    plt.ylabel("Days")

    plt.grid()

    plt.tight_layout()

    plt.savefig(

        f"{RESULTS}/mhw/figures/"
        f"{region}_duration_vs_year.png",

        dpi=300
    )

    plt.close()

    plt.figure(figsize=(10,5))

    plt.plot(
        annual["Year"],
        annual["Max_Intensity"],
        marker="o"
    )

    plt.title(
        f"{region.capitalize()} Max Intensity"
    )

    plt.xlabel("Year")
    plt.ylabel("Intensity")

    plt.grid()

    plt.tight_layout()

    plt.savefig(

        f"{RESULTS}/mhw/figures/"
        f"{region}_intensity_vs_year.png",

        dpi=300
    )

    plt.close()

with open(

    f"{RESULTS}/mhw/mhw_summary.txt",

    "w"

) as f:

    f.writelines(summary_text)

print("\nDone")

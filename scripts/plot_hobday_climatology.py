import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS = "/home/samyak/mrc_ws/results"

Path(
    f"{RESULTS}/climatology/hobday_figures"
).mkdir(
    parents=True,
    exist_ok=True
)

for region in [
    "north",
    "central",
    "south"
]:

    df = pd.read_csv(

        f"{RESULTS}/climatology/"
        f"{region}_hobday.csv"
    )

    plt.figure(
        figsize=(12,5)
    )

    plt.plot(
        df["DOY"],
        df["Climatology"],
        label="Climatology"
    )

    plt.plot(
        df["DOY"],
        df["Threshold90"],
        label="90th Percentile"
    )

    plt.legend()

    plt.grid()

    plt.title(
        f"{region.capitalize()} Hobday Climatology"
    )

    plt.tight_layout()

    plt.savefig(

        f"{RESULTS}/climatology/"
        f"hobday_figures/"
        f"{region}.png",

        dpi=300
    )

    plt.close()

print("Saved")

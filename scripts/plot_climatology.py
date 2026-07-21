import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS = "/home/samyak/mrc_ws/results"

Path(f"{RESULTS}/climatology/figures").mkdir(
    parents=True,
    exist_ok=True
)

regions = [
    "north",
    "central",
    "south"
]

for region in regions:

    clim = pd.read_csv(
        f"{RESULTS}/climatology/{region}_climatology.csv"
    )

    thresh = pd.read_csv(
        f"{RESULTS}/climatology/{region}_threshold.csv"
    )

    plt.figure(figsize=(12,5))

    plt.plot(
        clim["DOY"],
        clim["Climatology"],
        label="Climatology"
    )

    plt.plot(
        thresh["DOY"],
        thresh["Threshold90"],
        label="90th Percentile"
    )

    plt.title(
        f"{region.capitalize()} BoB Climatology"
    )

    plt.xlabel("Day of Year")

    plt.ylabel("SST (°C)")

    plt.grid(True)

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        f"{RESULTS}/climatology/figures/{region}_climatology.png",
        dpi=300
    )

    plt.close()

print("Plots saved")

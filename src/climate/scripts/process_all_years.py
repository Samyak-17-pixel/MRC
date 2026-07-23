import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import glob
import re


DATA_DIR = "/home/samyak/mrc_ws/data/raw"
RESULTS_DIR = "/home/samyak/mrc_ws/outputs"

Path(RESULTS_DIR).mkdir(exist_ok=True)


files = sorted(
    glob.glob(f"{DATA_DIR}/sst.day.mean.20*.nc")
)

print("\nFiles Found:")
for f in files:
    print(f)


master_summary = []


for file_path in files:

    year = re.search(r'(\d{4})', file_path).group(1)

    print(f"\nProcessing {year}")

    output_dir = Path(f"{RESULTS_DIR}/yearly/{year}")
    output_dir.mkdir(parents=True, exist_ok=True)


    ds = xr.open_dataset(file_path)


    bob = ds.sel(
        lat=slice(0,30),
        lon=slice(75,100)
    )


    plt.figure(figsize=(10,6))

    bob.sst.isel(time=0).plot()

    plt.title(f"Bay of Bengal SST ({year}-01-01)")

    plt.tight_layout()

    plt.savefig(
        output_dir / "sst_map.png",
        dpi=300
    )

    plt.close()


    north = bob.sel(
        lat=slice(15,22),
        lon=slice(85,95)
    )

    central = bob.sel(
        lat=slice(10,15),
        lon=slice(85,95)
    )

    south = bob.sel(
        lat=slice(5,10),
        lon=slice(85,95)
    )

    north_sst = north.sst.mean(dim=["lat","lon"])
    central_sst = central.sst.mean(dim=["lat","lon"])
    south_sst = south.sst.mean(dim=["lat","lon"])


    plt.figure(figsize=(14,6))

    north_sst.plot(label="North BoB")
    central_sst.plot(label="Central BoB")
    south_sst.plot(label="South BoB")

    plt.title(f"Daily Mean SST ({year})")

    plt.ylabel("Temperature (°C)")
    plt.xlabel("Date")

    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        output_dir / "regional_sst_timeseries.png",
        dpi=300
    )

    plt.close()


    stats = pd.DataFrame({
        "Region": ["North", "Central", "South"],

        "Mean SST": [
            float(north_sst.mean()),
            float(central_sst.mean()),
            float(south_sst.mean())
        ],

        "Min SST": [
            float(north_sst.min()),
            float(central_sst.min()),
            float(south_sst.min())
        ],

        "Max SST": [
            float(north_sst.max()),
            float(central_sst.max()),
            float(south_sst.max())
        ]
    })

    stats.to_csv(
        output_dir / "sst_statistics.csv",
        index=False
    )


    master_summary.append({

        "Year": year,

        "North Mean SST":
            float(north_sst.mean()),

        "Central Mean SST":
            float(central_sst.mean()),

        "South Mean SST":
            float(south_sst.mean())
    })

    print(f"Finished {year}")


master_df = pd.DataFrame(master_summary)

master_df.to_csv(
    f"{RESULTS_DIR}/yearly/master_summary.csv",
    index=False
)

print("\nAll years completed.")
print("Results saved in:")
print(RESULTS_DIR)

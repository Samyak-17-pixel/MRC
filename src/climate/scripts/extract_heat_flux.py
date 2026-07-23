import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE = "/home/samyak/mrc_ws"

years = range(2006, 2026)

out_csv = Path(
    f"{BASE}/outputs/drivers/heat_flux/csv"
)

out_fig = Path(
    f"{BASE}/outputs/drivers/heat_flux/figures"
)

out_csv.mkdir(
    parents=True,
    exist_ok=True
)

out_fig.mkdir(
    parents=True,
    exist_ok=True
)

regions = {

    "north": {
        "lat": slice(25,15),
        "lon": slice(80,100)
    },

    "central": {
        "lat": slice(15,8),
        "lon": slice(80,100)
    },

    "south": {
        "lat": slice(8,0),
        "lon": slice(80,100)
    }
}

slhf_data = {
    "north": [],
    "central": [],
    "south": []
}

sshf_data = {
    "north": [],
    "central": [],
    "south": []
}

for year in years:

    print(f"\nProcessing {year}")

    folder = (
        f"{BASE}/data/raw/"
        f"heat_flux_data_2006_2025/"
        f"heat_flux_{year}"
    )

    slhf_file = (
        f"{folder}/"
        f"surface_latent_heat_flux_stream-oper_daily-mean.nc"
    )

    sshf_file = (
        f"{folder}/"
        f"surface_sensible_heat_flux_0_daily-mean.nc"
    )

    slhf_ds = xr.open_dataset(slhf_file)
    sshf_ds = xr.open_dataset(sshf_file)

    for region, bounds in regions.items():

        slhf = slhf_ds["slhf"].sel(
            latitude=bounds["lat"],
            longitude=bounds["lon"]
        )

        sshf = sshf_ds["sshf"].sel(
            latitude=bounds["lat"],
            longitude=bounds["lon"]
        )

        slhf_ts = slhf.mean(
            dim=["latitude","longitude"]
        )

        sshf_ts = sshf.mean(
            dim=["latitude","longitude"]
        )

        temp1 = pd.DataFrame({

            "Date":
                slhf_ds.valid_time.values,

            "HeatFlux":
                slhf_ts.values

        })

        temp2 = pd.DataFrame({

            "Date":
                sshf_ds.valid_time.values,

            "HeatFlux":
                sshf_ts.values

        })

        slhf_data[region].append(
            temp1
        )

        sshf_data[region].append(
            temp2
        )

for region in regions:

    slhf_df = pd.concat(
        slhf_data[region]
    )

    sshf_df = pd.concat(
        sshf_data[region]
    )

    slhf_df.to_csv(

        out_csv /
        f"{region}_slhf.csv",

        index=False
    )

    sshf_df.to_csv(

        out_csv /
        f"{region}_sshf.csv",

        index=False
    )


    plt.figure(
        figsize=(14,5)
    )

    plt.plot(
        pd.to_datetime(
            slhf_df["Date"]
        ),
        slhf_df["HeatFlux"]
    )

    plt.title(
        f"{region.upper()} "
        f"Latent Heat Flux"
    )

    plt.ylabel(
        "J m^-2"
    )

    plt.grid()

    plt.tight_layout()

    plt.savefig(

        out_fig /
        f"{region}_slhf_timeseries.png",

        dpi=300
    )

    plt.close()


    plt.figure(
        figsize=(14,5)
    )

    plt.plot(
        pd.to_datetime(
            sshf_df["Date"]
        ),
        sshf_df["HeatFlux"]
    )

    plt.title(
        f"{region.upper()} "
        f"Sensible Heat Flux"
    )

    plt.ylabel(
        "J m^-2"
    )

    plt.grid()

    plt.tight_layout()

    plt.savefig(

        out_fig /
        f"{region}_sshf_timeseries.png",

        dpi=300
    )

    plt.close()

print("\nFinished")

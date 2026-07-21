import os
import glob
import numpy as np
import pandas as pd
import xarray as xr

BASE = "/home/samyak/mrc_ws"

HEAT_DIR = f"{BASE}/datasets/heat_flux_data_2006_2025"
MHW_DIR = f"{BASE}/results/mhw_catalogue"
OUT_DIR = f"{BASE}/results/heat_flux_analysis"

os.makedirs(OUT_DIR, exist_ok=True)

REGIONS = {
    "north": dict(lat=slice(25,15), lon=slice(80,100)),
    "central": dict(lat=slice(15,8), lon=slice(80,95)),
    "south": dict(lat=slice(8,0), lon=slice(80,95))
}


def load_flux(variable):

    all_years = []

    for year in range(2006, 2026):

        folder = f"{HEAT_DIR}/heat_flux_{year}"

        if variable == "slhf":
            file = f"{folder}/surface_latent_heat_flux_stream-oper_daily-mean.nc"
        else:
            file = f"{folder}/surface_sensible_heat_flux_0_daily-mean.nc"

        ds = xr.open_dataset(file)

        all_years.append(ds)

    return xr.concat(all_years, dim="valid_time")


print("Loading latent heat flux...")
slhf_ds = load_flux("slhf")

print("Loading sensible heat flux...")
sshf_ds = load_flux("sshf")


for region, box in REGIONS.items():

    print(f"\nProcessing {region}")

    slhf = slhf_ds["slhf"].sel(
        latitude=box["lat"],
        longitude=box["lon"]
    ).mean(dim=["latitude","longitude"])

    sshf = sshf_ds["sshf"].sel(
        latitude=box["lat"],
        longitude=box["lon"]
    ).mean(dim=["latitude","longitude"])

    slhf_df = slhf.to_dataframe().reset_index()
    sshf_df = sshf.to_dataframe().reset_index()

    slhf_df["Month"] = pd.to_datetime(
        slhf_df["valid_time"]
    ).dt.month

    sshf_df["Month"] = pd.to_datetime(
        sshf_df["valid_time"]
    ).dt.month

    slhf_clim = slhf_df.groupby("Month")["slhf"].mean()
    sshf_clim = sshf_df.groupby("Month")["sshf"].mean()

    mhw = pd.read_csv(
        f"{MHW_DIR}/{region}_mhw_catalogue.csv"
    )

    rows = []

    for _, event in mhw.iterrows():

        start = pd.to_datetime(event["Start_Date"])
        end = pd.to_datetime(event["End_Date"])

        month = start.month

        slhf_event = slhf_df[
            (slhf_df["valid_time"] >= start) &
            (slhf_df["valid_time"] <= end)
        ]

        sshf_event = sshf_df[
            (sshf_df["valid_time"] >= start) &
            (sshf_df["valid_time"] <= end)
        ]

        if len(slhf_event) == 0:
            continue

        slhf_during = slhf_event["slhf"].mean()
        sshf_during = sshf_event["sshf"].mean()

        slhf_clim_val = slhf_clim.loc[month]
        sshf_clim_val = sshf_clim.loc[month]

        slhf_anom = slhf_during - slhf_clim_val
        sshf_anom = sshf_during - sshf_clim_val

        rows.append([
            event["Start_Date"],
            event["End_Date"],
            event["Duration_Days"],
            event["Mean_Intensity"],
            slhf_clim_val,
            slhf_during,
            slhf_anom,
            sshf_clim_val,
            sshf_during,
            sshf_anom
        ])

    out = pd.DataFrame(
        rows,
        columns=[
            "Start_Date",
            "End_Date",
            "Duration",
            "Mean_Intensity",
            "SLHF_Climatology",
            "SLHF_During",
            "SLHF_Anomaly",
            "SSHF_Climatology",
            "SSHF_During",
            "SSHF_Anomaly"
        ]
    )

    out.to_csv(
        f"{OUT_DIR}/{region}_heat_flux_analysis.csv",
        index=False
    )

print("\nFinished")

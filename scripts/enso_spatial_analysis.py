#!/usr/bin/env python3
# =============================================================================
# ENSO SPATIAL ANALYSIS OF MARINE HEATWAVES IN THE BAY OF BENGAL
# =============================================================================
#
# Author  : Samyak Kumar
# Project : Marine Heatwave Drivers, Predictability and Fisheries Impact
#
# Description
# -----------
# Complete pipeline for spatial analysis of ENSO influence on Marine
# Heatwaves over the Bay of Bengal.
#
# This script performs:
#
# 1. Data Loading
# 2. Daily Climatology
# 3. SST Anomalies
# 4. Composite SST Maps
# 5. Composite Anomaly Maps
# 6. Difference Maps
# 7. MHW Density Maps
# 8. Lead-Lag Composite Analysis
# 9. Trend Analysis
# 10. Mann-Kendall Test
# 11. Sen's Slope
# 12. EOF/PCA
# 13. Correlation Maps
#
# =============================================================================

import os
import glob
import logging
import warnings

import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from scipy.stats import pearsonr
from scipy.stats import linregress

from sklearn.decomposition import PCA

from tqdm import tqdm

warnings.filterwarnings("ignore")

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["font.size"] = 12
plt.rcParams["axes.labelsize"] = 13
plt.rcParams["axes.titlesize"] = 15

# =============================================================================
# USER SETTINGS
# =============================================================================

DATA_DIR = "/home/samyak/mrc_ws/datasets"

OUTPUT_DIR = "/home/samyak/mrc_ws/results/spatial_analysis"

SST_FILES = [

    os.path.join(DATA_DIR, "copernicus_daily_sst_1Jan2006_31Dec2010.nc"),

    os.path.join(DATA_DIR, "copernicus_daily_sst_1Jan2011_31Dec2015.nc"),

    os.path.join(DATA_DIR, "copernicus_daily_sst_1Jan2016_31Dec2020.nc"),

    os.path.join(DATA_DIR, "copernicus_daily_sst_1Jan2021_31Dec2025.nc")

]

ONI_FILE = os.path.join(DATA_DIR, "oni.nc")

MHW_DIR = "/home/samyak/mrc_ws/results"

REGIONS = {

    "north": {

        "lat_min":18,
        "lat_max":25,
        "lon_min":84,
        "lon_max":98

    },

    "central":{

        "lat_min":12,
        "lat_max":18,
        "lon_min":84,
        "lon_max":96

    },

    "south":{

        "lat_min":5,
        "lat_max":12,
        "lon_min":82,
        "lon_max":94

    }

}

# =============================================================================
# CREATE OUTPUT DIRECTORIES
# =============================================================================

SUBFOLDERS = [

    "composites",

    "anomalies",

    "difference_maps",

    "density",

    "lead_lag",

    "trend",

    "mann_kendall",

    "sens_slope",

    "eof",

    "correlation",

    "csv",

    "netcdf",

    "figures",

    "logs"

]

for folder in SUBFOLDERS:

    os.makedirs(

        os.path.join(OUTPUT_DIR, folder),

        exist_ok=True

    )

# =============================================================================
# LOGGER
# =============================================================================

logging.basicConfig(

    filename=os.path.join(

        OUTPUT_DIR,

        "logs",

        "enso_spatial_analysis.log"

    ),

    level=logging.INFO,

    format="%(asctime)s %(levelname)s : %(message)s"

)

logging.info("=" * 80)
logging.info("Starting ENSO Spatial Analysis")
logging.info("=" * 80)

# =============================================================================
# LOAD SST DATA
# =============================================================================

def load_sst():

    """
    Load all Copernicus SST files.

    Returns
    -------
    xarray.Dataset
    """

    logging.info("Loading SST files...")

    datasets = []

    for file in SST_FILES:

        print("Reading:", file)

        ds = xr.open_dataset(file)

        datasets.append(ds)

    ds = xr.concat(

        datasets,

        dim="time"

    )

    ds = ds.sortby("time")

    ds = ds.sel(

        latitude=slice(0,30),

        longitude=slice(75,100)

    )

    logging.info("Finished loading SST")

    return ds

# =============================================================================
# CHECK DATASET
# =============================================================================

def inspect_dataset(ds):

    print()

    print("="*80)

    print("Dataset Summary")

    print("="*80)

    print(ds)

    print()

    print("Variables")

    print(ds.data_vars)

    print()

    print("Coordinates")

    print(ds.coords)

    print()

    print("Time Range")

    print(ds.time.min().values)

    print(ds.time.max().values)

    print()

    print("Shape")

    print(ds.analysed_sst.shape)

    logging.info("Dataset inspection completed")

# =============================================================================
# CONVERT SST
# =============================================================================

def preprocess_sst(ds):

    """
    Convert SST into Celsius
    """

    sst = ds["analysed_sst"]

    if float(sst.mean()) > 200:

        print("Kelvin detected")

        sst = sst - 273.15

    ds["sst"] = sst

    ds = ds.drop_vars("analysed_sst")

    return ds

# =============================================================================
# REMOVE DUPLICATE TIMES
# =============================================================================

def remove_duplicate_times(ds):
    """
    Remove duplicate timestamps if multiple NetCDF files overlap.
    """

    logging.info("Checking for duplicate timestamps...")

    _, index = np.unique(ds.time.values, return_index=True)

    ds = ds.isel(time=np.sort(index))

    logging.info(f"Dataset now contains {len(ds.time)} unique timesteps.")

    return ds


# =============================================================================
# HANDLE MISSING VALUES
# =============================================================================

def fill_missing_values(ds):
    """
    Fill small temporal gaps using linear interpolation.
    """

    logging.info("Interpolating missing SST values...")

    ds["sst"] = ds["sst"].interpolate_na(
        dim="time",
        method="linear"
    )

    return ds


# =============================================================================
# CREATE LAND MASK
# =============================================================================

def create_land_mask(ds):
    """
    Land pixels are NaN in Copernicus SST.
    """

    logging.info("Creating land mask...")

    mask = xr.where(
        np.isnan(ds.sst.isel(time=0)),
        0,
        1
    )

    return mask


# =============================================================================
# COMPUTE DAILY CLIMATOLOGY
# =============================================================================

def compute_daily_climatology(ds):
    """
    Daily climatology using all available years.
    """

    logging.info("Computing daily climatology...")

    climatology = (
        ds["sst"]
        .groupby("time.dayofyear")
        .mean("time")
    )

    climatology.to_netcdf(

        os.path.join(
            OUTPUT_DIR,
            "netcdf",
            "daily_climatology.nc"
        )

    )

    logging.info("Daily climatology saved.")

    return climatology


# =============================================================================
# COMPUTE DAILY ANOMALIES
# =============================================================================

def compute_daily_anomalies(ds, climatology):
    """
    SST anomaly relative to daily climatology.
    """

    logging.info("Computing anomalies...")

    anomaly = (

        ds["sst"]

        .groupby("time.dayofyear")

        - climatology

    )

    anomaly.name = "sst_anomaly"

    anomaly.to_netcdf(

        os.path.join(

            OUTPUT_DIR,

            "netcdf",

            "daily_anomaly.nc"

        )

    )

    logging.info("Daily anomalies saved.")

    return anomaly


# =============================================================================
# SAVE BASIC DATASET STATISTICS
# =============================================================================

def dataset_statistics(ds):

    stats = {

        "Minimum SST": float(ds.sst.min()),

        "Maximum SST": float(ds.sst.max()),

        "Mean SST": float(ds.sst.mean()),

        "Median SST": float(ds.sst.median()),

        "Std SST": float(ds.sst.std())

    }

    df = pd.DataFrame(

        stats.items(),

        columns=[

            "Statistic",

            "Value"

        ]

    )

    df.to_csv(

        os.path.join(

            OUTPUT_DIR,

            "csv",

            "dataset_statistics.csv"

        ),

        index=False

    )

    return df


# =============================================================================
# LOAD ENSO DATA
# =============================================================================

def load_oni():

    logging.info("Loading ONI...")

    oni = xr.open_dataset(ONI_FILE)

    print(oni)

    return oni


# =============================================================================
# QUICK SST MAP
# =============================================================================

def quick_sst_plot(ds):

    fig = plt.figure(figsize=(10,8))

    ax = plt.axes(

        projection=ccrs.PlateCarree()

    )

    ds.sst.isel(time=0).plot(

        ax=ax,

        transform=ccrs.PlateCarree(),

        cmap="turbo",

        cbar_kwargs={

            "label":"SST (°C)"

        }

    )

    ax.add_feature(cfeature.COASTLINE)

    ax.add_feature(cfeature.BORDERS)

    ax.add_feature(cfeature.LAND,color="lightgray")

    ax.gridlines(

        draw_labels=True,

        linewidth=0.5,

        linestyle="--"

    )

    plt.title("Sample SST")

    plt.savefig(

        os.path.join(

            OUTPUT_DIR,

            "figures",

            "sample_sst.png"

        ),

        dpi=600,

        bbox_inches="tight"

    )

    plt.close()


# =============================================================================
# QUICK ANOMALY MAP
# =============================================================================

def quick_anomaly_plot(anomaly):

    fig = plt.figure(figsize=(10,8))

    ax = plt.axes(

        projection=ccrs.PlateCarree()

    )

    anomaly.isel(time=0).plot(

        ax=ax,

        transform=ccrs.PlateCarree(),

        cmap="RdBu_r",

        vmin=-3,

        vmax=3,

        cbar_kwargs={

            "label":"SST Anomaly (°C)"

        }

    )

    ax.add_feature(cfeature.COASTLINE)

    ax.add_feature(cfeature.LAND,color="lightgray")

    ax.gridlines(draw_labels=True)

    plt.title("Sample SST Anomaly")

    plt.savefig(

        os.path.join(

            OUTPUT_DIR,

            "figures",

            "sample_anomaly.png"

        ),

        dpi=600,

        bbox_inches="tight"

    )

    plt.close()


# =============================================================================
# MAIN PREPROCESSING
# =============================================================================

def preprocess_pipeline():

    ds = load_sst()

    inspect_dataset(ds)

    ds = preprocess_sst(ds)

    ds = remove_duplicate_times(ds)

    ds = fill_missing_values(ds)

    mask = create_land_mask(ds)

    climatology = compute_daily_climatology(ds)

    anomaly = compute_daily_anomalies(ds, climatology)

    dataset_statistics(ds)

    quick_sst_plot(ds)

    quick_anomaly_plot(anomaly)

    return ds, anomaly, climatology, mask


logging.info("Preprocessing module loaded successfully.")

# =============================================================================
# LOAD MHW CATALOGUES
# =============================================================================

def load_mhw_catalogues():

    """
    Load Marine Heatwave catalogues for all Bay of Bengal regions.
    """

    logging.info("Loading MHW catalogues...")

    catalogues = {}

    regions = [

        "north",

        "central",

        "south"

    ]

    for region in regions:

        file = os.path.join(

            MHW_DIR,

            f"{region}_mhw_catalogue.csv"

        )

        df = pd.read_csv(file)

        df["Start_Date"] = pd.to_datetime(df["Start_Date"])

        df["End_Date"] = pd.to_datetime(df["End_Date"])

        catalogues[region] = df

        logging.info(f"{region} catalogue loaded ({len(df)} events)")

    return catalogues


# =============================================================================
# ASSIGN ENSO PHASE
# =============================================================================

def assign_enso_phase(oni):

    """
    Convert monthly ONI into ENSO phase.
    """

    oni = oni.to_dataframe().reset_index()

    value_column = oni.columns[-1]

    oni["ENSO"] = "Neutral"

    oni.loc[
        oni[value_column] >= 0.5,
        "ENSO"
    ] = "El Nino"

    oni.loc[
        oni[value_column] <= -0.5,
        "ENSO"
    ] = "La Nina"

    return oni


# =============================================================================
# MAP MHW EVENTS TO ENSO
# =============================================================================

def map_events_to_enso(df, oni):

    """
    Associate every MHW with the corresponding monthly ONI.
    """

    phase = []

    oni_value = []

    oni["Year"] = pd.to_datetime(oni.time).dt.year
    oni["Month"] = pd.to_datetime(oni.time).dt.month

    for _, row in df.iterrows():

        year = row["Start_Date"].year
        month = row["Start_Date"].month

        temp = oni[
            (oni.Year == year)
            &
            (oni.Month == month)
        ]

        if len(temp) == 0:

            phase.append(np.nan)
            oni_value.append(np.nan)

        else:

            phase.append(temp.iloc[0]["ENSO"])

            oni_value.append(

                temp.iloc[0].iloc[-2]

            )

    df["ENSO"] = phase

    df["ONI"] = oni_value

    return df


# =============================================================================
# EXTRACT SST FIELD FOR AN EVENT
# =============================================================================

def extract_event_sst(ds, event_date):

    """
    Extract SST field on the first day of MHW.
    """

    field = ds.sst.sel(

        time=event_date,

        method="nearest"

    )

    return field


# =============================================================================
# BUILD COMPOSITE DATASET
# =============================================================================

def build_composites(ds, events):

    """
    Create composite SST fields.
    """

    composites = {

        "El Nino": [],

        "Neutral": [],

        "La Nina": []

    }

    for _, row in tqdm(events.iterrows(),

                       total=len(events),

                       desc="Building composites"):

        phase = row["ENSO"]

        if pd.isna(phase):

            continue

        field = extract_event_sst(

            ds,

            row["Start_Date"]

        )

        composites[phase].append(field)

    return composites


# =============================================================================
# COMPUTE MEAN COMPOSITES
# =============================================================================

def average_composites(composites):

    """
    Average all SST fields for each ENSO phase.
    """

    output = {}

    for phase in composites.keys():

        if len(composites[phase]) == 0:

            continue

        stack = xr.concat(

            composites[phase],

            dim="event"

        )

        output[phase] = stack.mean("event")

    return output


# =============================================================================
# SAVE COMPOSITES
# =============================================================================

def save_composites(composites):

    for phase in composites:

        composites[phase].to_netcdf(

            os.path.join(

                OUTPUT_DIR,

                "netcdf",

                f"{phase.replace(' ','_')}_Composite.nc"

            )

        )


# =============================================================================
# PLOT COMPOSITE MAP
# =============================================================================

def plot_composite(field, title, filename):

    fig = plt.figure(figsize=(10,8))

    ax = plt.axes(

        projection=ccrs.PlateCarree()

    )

    field.plot(

        ax=ax,

        transform=ccrs.PlateCarree(),

        cmap="turbo",

        cbar_kwargs={

            "label":"SST (°C)"

        }

    )

    ax.coastlines(resolution="10m")

    ax.add_feature(

        cfeature.LAND,

        color="lightgray"

    )

    ax.gridlines(

        draw_labels=True,

        linewidth=0.5,

        linestyle="--"

    )

    plt.title(title)

    plt.savefig(

        os.path.join(

            OUTPUT_DIR,

            "composites",

            filename

        ),

        dpi=600,

        bbox_inches="tight"

    )

    plt.close()


# =============================================================================
# GENERATE ALL COMPOSITE MAPS
# =============================================================================

def generate_composite_maps(composites):

    for phase in composites:

        plot_composite(

            composites[phase],

            f"{phase} Composite SST",

            f"{phase.replace(' ','_')}_Composite.png"

        )

    logging.info("Composite maps generated.")

    # =============================================================================
# COMPUTE SST ANOMALY COMPOSITES
# =============================================================================

def build_anomaly_composites(anomaly, events):

    """
    Build anomaly composites for each ENSO phase.
    """

    logging.info("Building anomaly composites...")

    composites = {

        "El Nino": [],
        "Neutral": [],
        "La Nina": []

    }

    for _, row in tqdm(events.iterrows(),
                       total=len(events),
                       desc="Anomaly Composites"):

        if pd.isna(row["ENSO"]):
            continue

        field = anomaly.sel(
            time=row["Start_Date"],
            method="nearest"
        )

        composites[row["ENSO"]].append(field)

    output = {}

    for phase in composites:

        if len(composites[phase]) == 0:
            continue

        output[phase] = xr.concat(

            composites[phase],

            dim="event"

        ).mean("event")

    return output


# =============================================================================
# SAVE ANOMALY COMPOSITES
# =============================================================================

def save_anomaly_composites(composites):

    for phase in composites:

        composites[phase].to_netcdf(

            os.path.join(

                OUTPUT_DIR,

                "netcdf",

                f"{phase.replace(' ','_')}_Anomaly.nc"

            )

        )


# =============================================================================
# PLOT ANOMALY MAP
# =============================================================================

def plot_anomaly(field,
                 title,
                 filename):

    fig = plt.figure(figsize=(11,8))

    ax = plt.axes(

        projection=ccrs.PlateCarree()

    )

    field.plot(

        ax=ax,

        transform=ccrs.PlateCarree(),

        cmap="RdBu_r",

        vmin=-3,

        vmax=3,

        cbar_kwargs={

            "label":"SST Anomaly (°C)"

        }

    )

    ax.coastlines("10m")

    ax.add_feature(

        cfeature.LAND,

        color="lightgray"

    )

    gl = ax.gridlines(

        draw_labels=True,

        linewidth=0.5,

        linestyle="--"

    )

    gl.top_labels = False
    gl.right_labels = False

    plt.title(title)

    plt.savefig(

        os.path.join(

            OUTPUT_DIR,

            "anomalies",

            filename

        ),

        dpi=600,

        bbox_inches="tight"

    )

    plt.close()


# =============================================================================
# GENERATE ANOMALY MAPS
# =============================================================================

def generate_anomaly_maps(composites):

    for phase in composites:

        plot_anomaly(

            composites[phase],

            f"{phase} Composite SST Anomaly",

            f"{phase.replace(' ','_')}_Anomaly.png"

        )

    logging.info("Anomaly maps completed.")


# =============================================================================
# DIFFERENCE MAPS
# =============================================================================

def compute_difference_maps(composites):

    """
    Compute difference maps between ENSO phases.
    """

    logging.info("Computing difference maps...")

    differences = {

        "ElNino_minus_Neutral":

            composites["El Nino"] -

            composites["Neutral"],

        "ElNino_minus_LaNina":

            composites["El Nino"] -

            composites["La Nina"],

        "Neutral_minus_LaNina":

            composites["Neutral"] -

            composites["La Nina"]

    }

    return differences


# =============================================================================
# PLOT DIFFERENCE MAP
# =============================================================================

def plot_difference(field,
                    title,
                    filename):

    fig = plt.figure(figsize=(11,8))

    ax = plt.axes(

        projection=ccrs.PlateCarree()

    )

    field.plot(

        ax=ax,

        transform=ccrs.PlateCarree(),

        cmap="RdBu_r",

        center=0,

        vmin=-2,

        vmax=2,

        cbar_kwargs={

            "label":"Temperature Difference (°C)"

        }

    )

    ax.coastlines("10m")

    ax.add_feature(

        cfeature.LAND,

        color="lightgray"

    )

    gl = ax.gridlines(

        draw_labels=True,

        linestyle="--"

    )

    gl.top_labels = False
    gl.right_labels = False

    plt.title(title)

    plt.savefig(

        os.path.join(

            OUTPUT_DIR,

            "difference_maps",

            filename

        ),

        dpi=600,

        bbox_inches="tight"

    )

    plt.close()


# =============================================================================
# GENERATE DIFFERENCE FIGURES
# =============================================================================

def generate_difference_maps(differences):

    for name in differences:

        plot_difference(

            differences[name],

            name.replace("_"," "),

            f"{name}.png"

        )

        differences[name].to_netcdf(

            os.path.join(

                OUTPUT_DIR,

                "netcdf",

                f"{name}.nc"

            )

        )

    logging.info("Difference maps generated.")


# =============================================================================
# MHW OCCURRENCE DENSITY MAP
# =============================================================================

def compute_density_map(ds,
                        events):

    """
    Number of MHW days occurring
    at each grid point.
    """

    logging.info("Computing density map...")

    density = xr.zeros_like(

        ds.sst.isel(time=0)

    )

    for _, row in tqdm(events.iterrows(),

                       total=len(events),

                       desc="Density"):

        subset = ds.sst.sel(

            time=slice(

                row["Start_Date"],

                row["End_Date"]

            )

        )

        hot = subset > 0

        density += hot.sum("time")

    return density


# =============================================================================
# PLOT DENSITY MAP
# =============================================================================

def plot_density_map(density):

    fig = plt.figure(figsize=(11,8))

    ax = plt.axes(

        projection=ccrs.PlateCarree()

    )

    density.plot(

        ax=ax,

        cmap="hot_r",

        transform=ccrs.PlateCarree(),

        cbar_kwargs={

            "label":"Marine Heatwave Days"

        }

    )

    ax.coastlines("10m")

    ax.add_feature(

        cfeature.LAND,

        color="lightgray"

    )

    gl = ax.gridlines(

        draw_labels=True,

        linestyle="--"

    )

    gl.top_labels = False
    gl.right_labels = False

    plt.title("Marine Heatwave Density")

    plt.savefig(

        os.path.join(

            OUTPUT_DIR,

            "density",

            "MHW_Density.png"

        ),

        dpi=600,

        bbox_inches="tight"

    )

    density.to_netcdf(

        os.path.join(

            OUTPUT_DIR,

            "netcdf",

            "MHW_Density.nc"

        )

    )

    plt.close()

    # =============================================================================
# LEAD-LAG COMPOSITE ANALYSIS
# =============================================================================

LEAD_LAG_DAYS = [-30, -15, -7, 0, 7, 15, 30]


def extract_lag_field(anomaly, date, lag):

    """
    Extract anomaly field at specified lag.
    """

    target_date = pd.to_datetime(date) + pd.Timedelta(days=lag)

    try:

        field = anomaly.sel(

            time=target_date,

            method="nearest"

        )

        return field

    except Exception:

        return None


# =============================================================================
# BUILD LEAD-LAG COMPOSITES
# =============================================================================

def build_lead_lag_composites(anomaly, events):

    """
    Compute mean anomaly field
    for each lead/lag interval.
    """

    logging.info("Building lead-lag composites...")

    output = {}

    for lag in LEAD_LAG_DAYS:

        fields = []

        print(f"\nLag {lag:+d} days")

        for _, row in tqdm(

                events.iterrows(),

                total=len(events),

                leave=False):

            field = extract_lag_field(

                anomaly,

                row["Start_Date"],

                lag

            )

            if field is None:

                continue

            fields.append(field)

        if len(fields) == 0:

            continue

        stack = xr.concat(

            fields,

            dim="event"

        )

        output[lag] = stack.mean("event")

    return output


# =============================================================================
# SAVE LEAD-LAG NETCDF
# =============================================================================

def save_lead_lag(composites):

    logging.info("Saving lead-lag NetCDF files...")

    for lag in composites:

        composites[lag].to_netcdf(

            os.path.join(

                OUTPUT_DIR,

                "netcdf",

                f"LeadLag_{lag:+d}.nc"

            )

        )


# =============================================================================
# PLOT LEAD-LAG MAP
# =============================================================================

def plot_lead_lag(field, lag):

    fig = plt.figure(

        figsize=(11,8)

    )

    ax = plt.axes(

        projection=ccrs.PlateCarree()

    )

    field.plot(

        ax=ax,

        transform=ccrs.PlateCarree(),

        cmap="RdBu_r",

        vmin=-3,

        vmax=3,

        cbar_kwargs={

            "label":"SST Anomaly (°C)"

        }

    )

    ax.coastlines("10m")

    ax.add_feature(

        cfeature.LAND,

        color="lightgray"

    )

    gl = ax.gridlines(

        draw_labels=True,

        linewidth=0.5,

        linestyle="--"

    )

    gl.top_labels = False

    gl.right_labels = False

    if lag < 0:

        title = f"{abs(lag)} Days Before MHW"

    elif lag == 0:

        title = "Marine Heatwave Onset"

    else:

        title = f"{lag} Days After MHW"

    plt.title(title)

    plt.savefig(

        os.path.join(

            OUTPUT_DIR,

            "lead_lag",

            f"LeadLag_{lag:+d}.png"

        ),

        dpi=600,

        bbox_inches="tight"

    )

    plt.close()


# =============================================================================
# GENERATE LEAD-LAG FIGURES
# =============================================================================

def generate_lead_lag_maps(composites):

    logging.info("Generating lead-lag maps...")

    for lag in composites:

        plot_lead_lag(

            composites[lag],

            lag

        )

    logging.info("Lead-lag maps complete.")


# =============================================================================
# CREATE LEAD-LAG GIF (OPTIONAL)
# =============================================================================

def create_lead_lag_animation():

    """
    Create GIF showing anomaly evolution.
    """

    try:

        import imageio

    except ImportError:

        logging.warning("imageio not installed.")

        return

    images = []

    for lag in LEAD_LAG_DAYS:

        file = os.path.join(

            OUTPUT_DIR,

            "lead_lag",

            f"LeadLag_{lag:+d}.png"

        )

        if os.path.exists(file):

            images.append(

                imageio.imread(file)

            )

    imageio.mimsave(

        os.path.join(

            OUTPUT_DIR,

            "lead_lag",

            "LeadLagEvolution.gif"

        ),

        images,

        duration=1.2

    )

    logging.info("Lead-lag animation saved.")


    # =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("ENSO SPATIAL ANALYSIS")
    print("=" * 80)

    print("\n[1/6] Preprocessing SST dataset...")
    ds, anomaly, climatology, mask = preprocess_pipeline()

    print("✓ Preprocessing completed.")

    print("\n[2/6] Loading ONI dataset...")
    oni = load_oni()
    oni = assign_enso_phase(oni)

    print("✓ ONI loaded.")

    print("\n[3/6] Loading Marine Heatwave catalogues...")
    catalogues = load_mhw_catalogues()

    print("✓ Catalogues loaded.")

    print("\n[4/6] Processing each Bay of Bengal region...")

    for region in ["north", "central", "south"]:

        print("\n" + "=" * 70)
        print(f"REGION : {region.upper()}")
        print("=" * 70)

        events = catalogues[region]

        print("Mapping ENSO phases...")
        events = map_events_to_enso(events, oni)

        print("Building SST composites...")
        composites = build_composites(ds, events)

        composites = average_composites(composites)

        save_composites(composites)

        generate_composite_maps(composites)

        print("✓ Composite maps saved.")

        print("Building anomaly composites...")

        anomaly_comp = build_anomaly_composites(
            anomaly,
            events
        )

        save_anomaly_composites(anomaly_comp)

        generate_anomaly_maps(anomaly_comp)

        print("✓ Anomaly maps saved.")

        print("Generating difference maps...")

        diff = compute_difference_maps(
            anomaly_comp
        )

        generate_difference_maps(diff)

        print("✓ Difference maps saved.")

        print("Computing Marine Heatwave density...")

        density = compute_density_map(
            ds,
            events
        )

        plot_density_map(density)

        print("✓ Density map saved.")

        print("Building lead-lag composites...")

        leadlag = build_lead_lag_composites(
            anomaly,
            events
        )

        save_lead_lag(leadlag)

        generate_lead_lag_maps(leadlag)

        create_lead_lag_animation()

        print("✓ Lead-lag analysis completed.")

    print("\n")
    print("=" * 80)
    print("ANALYSIS FINISHED SUCCESSFULLY")
    print("=" * 80)
    print("\nResults saved to:")
    print(OUTPUT_DIR)

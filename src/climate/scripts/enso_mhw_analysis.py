#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

from pathlib import Path


BASE = Path.home() / "mrc_ws"

RESULTS = BASE / "outputs"

DATASETS = BASE / "data" / "raw"

OUTPUT = RESULTS / "enso" / "analysis"

CSV_DIR = OUTPUT / "csv"

FIG_DIR = OUTPUT / "figures"

NORTH_PLOTS = OUTPUT / "north_event_plots"

CENTRAL_PLOTS = OUTPUT / "central_event_plots"

SOUTH_PLOTS = OUTPUT / "south_event_plots"

for folder in [

    OUTPUT,

    CSV_DIR,

    FIG_DIR,

    NORTH_PLOTS,

    CENTRAL_PLOTS,

    SOUTH_PLOTS

]:

    folder.mkdir(parents=True, exist_ok=True)


ONI_FILE = DATASETS / "oni.nc"

NORTH_FILE = RESULTS / "mhw" / "catalogue" / "north_mhw_catalogue.csv"

CENTRAL_FILE = RESULTS / "mhw" / "catalogue" / "central_mhw_catalogue.csv"

SOUTH_FILE = RESULTS / "mhw" / "catalogue" / "south_mhw_catalogue.csv"

print("Loading ONI...")

ds = xr.open_dataset(ONI_FILE)

oni = ds.to_dataframe().reset_index()

oni = oni.rename(columns={"value":"ONI"})

oni["time"] = pd.to_datetime(oni["time"])

oni = oni[
    (oni.time.dt.year>=2006) &
    (oni.time.dt.year<=2025)
]

print("Loaded",len(oni),"months")


north = pd.read_csv(NORTH_FILE)

central = pd.read_csv(CENTRAL_FILE)

south = pd.read_csv(SOUTH_FILE)

catalogues = {

    "north":north,

    "central":central,

    "south":south

}

for name in catalogues:

    catalogues[name]["Start_Date"] = pd.to_datetime(
        catalogues[name]["Start_Date"]
    )

    catalogues[name]["End_Date"] = pd.to_datetime(
        catalogues[name]["End_Date"]
    )

print()

print("North Events :",len(north))

print("Central Events :",len(central))

print("South Events :",len(south))


def classify_enso(v):

    if pd.isna(v):

        return np.nan

    if v>=0.5:

        return "El Nino"

    elif v<=-0.5:

        return "La Nina"

    else:

        return "Neutral"


def mean_oni(start,end):

    months = oni[
        (oni.time>=start.replace(day=1)) &
        (oni.time<=end.replace(day=1))
    ]

    if len(months)==0:

        return np.nan

    return months.ONI.mean()


def before_mean(start,days):

    s = start-pd.Timedelta(days=days)

    e = start-pd.Timedelta(days=1)

    return mean_oni(s,e)


def analyse_region(df):

    output=[]

    for _,event in df.iterrows():

        start = event.Start_Date

        end = event.End_Date

        oni30 = before_mean(start,30)

        oni21 = before_mean(start,21)

        oni14 = before_mean(start,14)

        oni7 = before_mean(start,7)

        during = mean_oni(start,end)

        phase = classify_enso(during)

        output.append({

            "Start_Date":start.date(),

            "End_Date":end.date(),

            "Duration":event.Duration_Days,

            "Mean_Intensity":event.Mean_Intensity,

            "Max_Intensity":event.Max_Intensity,

            "ONI_30d_Before":oni30,

            "ONI_21d_Before":oni21,

            "ONI_14d_Before":oni14,

            "ONI_7d_Before":oni7,

            "ONI_During":during,

            "ENSO_Phase":phase

        })

    return pd.DataFrame(output)


print()

print("Analysing North...")

north_out = analyse_region(north)

print("Analysing Central...")

central_out = analyse_region(central)

print("Analysing South...")

south_out = analyse_region(south)


north_out.to_csv(

    CSV_DIR/"north_enso_analysis.csv",

    index=False

)

central_out.to_csv(

    CSV_DIR/"central_enso_analysis.csv",

    index=False

)

south_out.to_csv(

    CSV_DIR/"south_enso_analysis.csv",

    index=False

)

print()

print("CSV files saved.")

print()

print(north_out.head())


def phase_statistics(df):

    phases = ["El Nino", "Neutral", "La Nina"]

    rows = []

    total = len(df)

    for phase in phases:

        subset = df[df["ENSO_Phase"] == phase]

        if len(subset) == 0:

            rows.append({

                "Phase": phase,

                "Events": 0,

                "Percentage": 0,

                "Mean Duration": np.nan,

                "Longest Duration": np.nan,

                "Mean Intensity": np.nan,

                "Maximum Intensity": np.nan,

                "Mean ONI": np.nan

            })

            continue

        rows.append({

            "Phase": phase,

            "Events": len(subset),

            "Percentage": round(100 * len(subset) / total, 2),

            "Mean Duration": round(subset["Duration"].mean(), 2),

            "Longest Duration": subset["Duration"].max(),

            "Mean Intensity": round(subset["Mean_Intensity"].mean(), 3),

            "Maximum Intensity": round(subset["Max_Intensity"].max(), 3),

            "Mean ONI": round(subset["ONI_During"].mean(), 3)

        })

    return pd.DataFrame(rows)


north_summary = phase_statistics(north_out)

central_summary = phase_statistics(central_out)

south_summary = phase_statistics(south_out)

north_summary.to_csv(

    CSV_DIR / "north_summary.csv",

    index=False

)

central_summary.to_csv(

    CSV_DIR / "central_summary.csv",

    index=False

)

south_summary.to_csv(

    CSV_DIR / "south_summary.csv",

    index=False

)


def print_summary(region, summary):

    print()

    print("=" * 60)

    print(region.upper())

    print("=" * 60)

    print(summary.to_string(index=False))

print_summary("North", north_summary)

print_summary("Central", central_summary)

print_summary("South", south_summary)


def strongest_events(df):

    return df.sort_values(

        "Mean_Intensity",

        ascending=False

    ).head(10)

def longest_events(df):

    return df.sort_values(

        "Duration",

        ascending=False

    ).head(10)

strongest_events(north_out).to_csv(

    CSV_DIR / "north_top10_strongest.csv",

    index=False

)

strongest_events(central_out).to_csv(

    CSV_DIR / "central_top10_strongest.csv",

    index=False

)

strongest_events(south_out).to_csv(

    CSV_DIR / "south_top10_strongest.csv",

    index=False

)

longest_events(north_out).to_csv(

    CSV_DIR / "north_top10_longest.csv",

    index=False

)

longest_events(central_out).to_csv(

    CSV_DIR / "central_top10_longest.csv",

    index=False

)

longest_events(south_out).to_csv(

    CSV_DIR / "south_top10_longest.csv",

    index=False

)


def correlations(df):

    print()

    print("Correlation (ONI vs Duration):",

          round(df["ONI_During"].corr(df["Duration"]), 3))

    print("Correlation (ONI vs Mean Intensity):",

          round(df["ONI_During"].corr(df["Mean_Intensity"]), 3))

    print("Correlation (ONI vs Max Intensity):",

          round(df["ONI_During"].corr(df["Max_Intensity"]), 3))

print()

print("NORTH")

correlations(north_out)

print()

print("CENTRAL")

correlations(central_out)

print()

print("SOUTH")

correlations(south_out)


def phase_plots(summary, region):


    plt.figure(figsize=(7,5))

    plt.bar(
        summary["Phase"],
        summary["Events"]
    )

    plt.title(f"{region} Bay of Bengal\nMarine Heatwaves by ENSO Phase")

    plt.xlabel("ENSO Phase")

    plt.ylabel("Number of Events")

    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        FIG_DIR / f"{region.lower()}_phase_bar.png",
        dpi=300
    )

    plt.close()


    plt.figure(figsize=(6,6))

    plt.pie(
        summary["Events"],
        labels=summary["Phase"],
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(f"{region} Bay of Bengal")

    plt.tight_layout()

    plt.savefig(
        FIG_DIR / f"{region.lower()}_phase_pie.png",
        dpi=300
    )

    plt.close()

phase_plots(north_summary,"North")
phase_plots(central_summary,"Central")
phase_plots(south_summary,"South")


def boxplots(df,region):


    plt.figure(figsize=(7,5))

    df.boxplot(

        column="Duration",

        by="ENSO_Phase"

    )

    plt.suptitle("")

    plt.title(f"{region} Bay of Bengal\nDuration vs ENSO Phase")

    plt.ylabel("Duration (Days)")

    plt.tight_layout()

    plt.savefig(

        FIG_DIR /

        f"{region.lower()}_duration_boxplot.png",

        dpi=300

    )

    plt.close()


    plt.figure(figsize=(7,5))

    df.boxplot(

        column="Mean_Intensity",

        by="ENSO_Phase"

    )

    plt.suptitle("")

    plt.title(f"{region} Bay of Bengal\nIntensity vs ENSO Phase")

    plt.ylabel("Mean Intensity")

    plt.tight_layout()

    plt.savefig(

        FIG_DIR /

        f"{region.lower()}_intensity_boxplot.png",

        dpi=300

    )

    plt.close()

boxplots(north_out,"North")

boxplots(central_out,"Central")

boxplots(south_out,"South")


def scatterplots(df,region):


    plt.figure(figsize=(7,5))

    plt.scatter(

        df["ONI_During"],

        df["Duration"]

    )

    plt.xlabel("Average ONI During Event")

    plt.ylabel("Duration (Days)")

    plt.title(

        f"{region} Bay of Bengal\nONI vs Duration"

    )

    plt.grid(alpha=0.3)

    plt.tight_layout()

    plt.savefig(

        FIG_DIR /

        f"{region.lower()}_oni_duration.png",

        dpi=300

    )

    plt.close()


    plt.figure(figsize=(7,5))

    plt.scatter(

        df["ONI_During"],

        df["Mean_Intensity"]

    )

    plt.xlabel("Average ONI During Event")

    plt.ylabel("Mean Intensity")

    plt.title(

        f"{region} Bay of Bengal\nONI vs Mean Intensity"

    )

    plt.grid(alpha=0.3)

    plt.tight_layout()

    plt.savefig(

        FIG_DIR /

        f"{region.lower()}_oni_intensity.png",

        dpi=300

    )

    plt.close()

scatterplots(north_out,"North")

scatterplots(central_out,"Central")

scatterplots(south_out,"South")


def histograms(df,region):

    plt.figure(figsize=(7,5))

    plt.hist(

        df["ONI_During"],

        bins=10,

        edgecolor="black"

    )

    plt.xlabel("Average ONI During Event")

    plt.ylabel("Number of Events")

    plt.title(

        f"{region} Bay of Bengal\nDistribution of ENSO Conditions"

    )

    plt.grid(alpha=0.3)

    plt.tight_layout()

    plt.savefig(

        FIG_DIR /

        f"{region.lower()}_oni_histogram.png",

        dpi=300

    )

    plt.close()

histograms(north_out,"North")

histograms(central_out,"Central")

histograms(south_out,"South")


def annual_occurrence(df, region):

    tmp = df.copy()

    tmp["Year"] = pd.to_datetime(tmp["Start_Date"]).dt.year

    annual = tmp.groupby(["Year","ENSO_Phase"]).size().unstack(fill_value=0)

    annual.to_csv(

        CSV_DIR / f"{region.lower()}_annual_occurrence.csv"

    )

    annual.plot(

        kind="bar",

        figsize=(12,5)

    )

    plt.title(

        f"{region} Bay of Bengal\nAnnual Marine Heatwave Occurrence"

    )

    plt.ylabel("Number of Events")

    plt.grid(axis="y",alpha=0.3)

    plt.tight_layout()

    plt.savefig(

        FIG_DIR /

        f"{region.lower()}_annual_occurrence.png",

        dpi=300

    )

    plt.close()

annual_occurrence(north_out,"North")

annual_occurrence(central_out,"Central")

annual_occurrence(south_out,"South")


def monthly_occurrence(df,region):

    tmp=df.copy()

    tmp["Month"]=pd.to_datetime(

        tmp["Start_Date"]

    ).dt.month

    monthly=tmp.groupby(

        ["Month","ENSO_Phase"]

    ).size().unstack(fill_value=0)

    monthly.to_csv(

        CSV_DIR/

        f"{region.lower()}_monthly_occurrence.csv"

    )

    monthly.plot(

        kind="bar",

        figsize=(10,5)

    )

    plt.title(

        f"{region} Bay of Bengal\nMonthly MHW Occurrence"

    )

    plt.ylabel("Events")

    plt.grid(axis="y",alpha=0.3)

    plt.tight_layout()

    plt.savefig(

        FIG_DIR/

        f"{region.lower()}_monthly_occurrence.png",

        dpi=300

    )

    plt.close()

monthly_occurrence(north_out,"North")

monthly_occurrence(central_out,"Central")

monthly_occurrence(south_out,"South")


comparison=pd.DataFrame({

"North":north_summary["Events"],

"Central":central_summary["Events"],

"South":south_summary["Events"]

},

index=north_summary["Phase"]

)

comparison.to_csv(

CSV_DIR/"regional_phase_comparison.csv"

)

comparison.plot(

kind="bar",

figsize=(8,5)

)

plt.ylabel("Events")

plt.title(

"Comparison of ENSO Phases\nAcross Bay of Bengal Regions"

)

plt.grid(axis="y",alpha=0.3)

plt.tight_layout()

plt.savefig(

FIG_DIR/"regional_phase_comparison.png",

dpi=300

)

plt.close()


plt.figure(figsize=(16,5))

plt.plot(

oni["time"],

oni["ONI"],

color="black",

linewidth=2

)

plt.axhline(

0.5,

linestyle="--"

)

plt.axhline(

-0.5,

linestyle="--"

)

plt.scatter(

pd.to_datetime(

north_out["Start_Date"]

),

north_out["ONI_During"],

marker="o",

label="North"

)

plt.scatter(

pd.to_datetime(

central_out["Start_Date"]

),

central_out["ONI_During"],

marker="s",

label="Central"

)

plt.scatter(

pd.to_datetime(

south_out["Start_Date"]

),

south_out["ONI_During"],

marker="^",

label="South"

)

plt.legend()

plt.grid(alpha=0.3)

plt.title(

"Oceanic Niño Index (2006–2025)\nMarine Heatwave Events"

)

plt.tight_layout()

plt.savefig(

FIG_DIR/"oni_timeline.png",

dpi=300

)

plt.close()


heat=comparison.copy()

plt.figure(figsize=(6,3))

plt.imshow(

heat,

aspect="auto"

)

plt.xticks(

range(3),

heat.columns

)

plt.yticks(

range(3),

heat.index

)

plt.colorbar(

label="Events"

)

plt.title(

"Marine Heatwave Occurrence"

)

plt.tight_layout()

plt.savefig(

FIG_DIR/"regional_heatmap.png",

dpi=300

)

plt.close()


summary_compare=pd.DataFrame({

"North":north_summary["Mean Intensity"],

"Central":central_summary["Mean Intensity"],

"South":south_summary["Mean Intensity"]

},

index=north_summary["Phase"]

)

summary_compare.plot(

kind="bar",

figsize=(8,5)

)

plt.ylabel("Mean Intensity")

plt.title(

"Mean Marine Heatwave Intensity\nAcross ENSO Phases"

)

plt.grid(axis="y",alpha=0.3)

plt.tight_layout()

plt.savefig(

FIG_DIR/"regional_mean_intensity.png",

dpi=300

)

plt.close()



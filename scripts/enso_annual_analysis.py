
#!/usr/bin/env python3
"""
ENSO Annual Analysis

Generates annual MHW statistics and compares them with annual ONI.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
from scipy.stats import pearsonr

ONI_FILE="/home/samyak/mrc_ws/datasets/oni.nc"

CATALOGUES={
"North":"/home/samyak/mrc_ws/results/enso_lag/north_enso_lag.csv",
"Central":"/home/samyak/mrc_ws/results/enso_lag/central_enso_lag.csv",
"South":"/home/samyak/mrc_ws/results/enso_lag/south_enso_lag.csv",
}

OUT="/home/samyak/mrc_ws/results/enso_annual"
CSV=os.path.join(OUT,"csv")
FIG=os.path.join(OUT,"figures")
os.makedirs(CSV,exist_ok=True)
os.makedirs(FIG,exist_ok=True)

oni=xr.open_dataset(ONI_FILE).to_dataframe().reset_index()[["time","value"]]
oni.columns=["Date","ONI"]
oni["Date"]=pd.to_datetime(oni["Date"])
oni["Year"]=oni["Date"].dt.year

annual_oni=oni.groupby("Year").agg(
    Mean_ONI=("ONI","mean"),
    Max_ONI=("ONI","max"),
    Min_ONI=("ONI","min")
).reset_index()

summary=[]

for region,file in CATALOGUES.items():

    print("\n"+"="*70)
    print(region.upper())
    print("="*70)

    df=pd.read_csv(file)
    df["Start_Date"]=pd.to_datetime(df["Start_Date"])
    df["Year"]=df["Start_Date"].dt.year

    annual=df.groupby("Year").agg(
        Events=("Year","size"),
        Mean_Duration=("Duration_Days","mean"),
        Max_Duration=("Duration_Days","max"),
        Mean_Intensity=("Mean_Intensity","mean"),
        Max_Intensity=("Max_Intensity","max")
    ).reset_index()

    annual=annual.merge(annual_oni,on="Year",how="left")

    annual.to_csv(f"{CSV}/{region.lower()}_annual.csv",index=False)

    print(annual.round(3).to_string(index=False))

    if len(annual)>2:
        r,p=pearsonr(annual["Events"],annual["Mean_ONI"])
    else:
        r,p=float("nan"),float("nan")

    print(f"\nCorrelation (Events vs Mean ONI): r={r:.3f}, p={p:.4f}")

    summary.append({
        "Region":region,
        "Correlation":r,
        "PValue":p
    })

    # Events
    plt.figure(figsize=(9,4))
    plt.plot(annual["Year"],annual["Events"],marker="o")
    plt.grid(alpha=.3)
    plt.title(f"{region}: Annual MHW Events")
    plt.ylabel("Events")
    plt.tight_layout()
    plt.savefig(f"{FIG}/{region.lower()}_events.png",dpi=300)
    plt.close()

    # Dual axis
    fig,ax1=plt.subplots(figsize=(9,4))
    ax1.plot(annual["Year"],annual["Events"],marker="o",label="Events")
    ax1.set_ylabel("Events")
    ax2=ax1.twinx()
    ax2.plot(annual["Year"],annual["Mean_ONI"],marker="s")
    ax2.set_ylabel("Mean ONI")
    plt.title(f"{region}: Events vs Annual Mean ONI")
    fig.tight_layout()
    fig.savefig(f"{FIG}/{region.lower()}_events_vs_oni.png",dpi=300)
    plt.close(fig)

    # Duration
    plt.figure(figsize=(9,4))
    plt.plot(annual["Year"],annual["Mean_Duration"],marker="o")
    plt.grid(alpha=.3)
    plt.title(f"{region}: Mean Duration")
    plt.tight_layout()
    plt.savefig(f"{FIG}/{region.lower()}_duration.png",dpi=300)
    plt.close()

    # Intensity
    plt.figure(figsize=(9,4))
    plt.plot(annual["Year"],annual["Mean_Intensity"],marker="o")
    plt.grid(alpha=.3)
    plt.title(f"{region}: Mean Intensity")
    plt.tight_layout()
    plt.savefig(f"{FIG}/{region.lower()}_intensity.png",dpi=300)
    plt.close()

summary=pd.DataFrame(summary)
summary.to_csv(f"{OUT}/summary.csv",index=False)

print("\n"+"="*70)
print("SUMMARY")
print("="*70)
print(summary.round(3).to_string(index=False))
print("\nOutput:",OUT)

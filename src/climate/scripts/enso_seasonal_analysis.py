

"""
ENSO Seasonal Analysis

Analyse Marine Heatwaves by meteorological season and ENSO phase.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

CATALOGUES={
"North":"/home/samyak/mrc_ws/outputs/enso/lag/north_enso_lag.csv",
"Central":"/home/samyak/mrc_ws/outputs/enso/lag/central_enso_lag.csv",
"South":"/home/samyak/mrc_ws/outputs/enso/lag/south_enso_lag.csv",
}

OUT="/home/samyak/mrc_ws/outputs/enso/seasonal"
CSV=os.path.join(OUT,"csv")
FIG=os.path.join(OUT,"figures")
os.makedirs(CSV,exist_ok=True)
os.makedirs(FIG,exist_ok=True)

def season(m):
    if m in [12,1,2]:
        return "Winter"
    if m in [3,4,5]:
        return "Pre-Monsoon"
    if m in [6,7,8,9]:
        return "SW Monsoon"
    return "Post-Monsoon"

summary=[]

for region,file in CATALOGUES.items():

    print("\n"+"="*70)
    print(region.upper())
    print("="*70)

    df=pd.read_csv(file)
    df["Start_Date"]=pd.to_datetime(df["Start_Date"])
    df["Season"]=df["Start_Date"].dt.month.apply(season)

    table=pd.crosstab(df["Season"],df["ENSO_Phase"])
    table=table.reindex(
        ["Winter","Pre-Monsoon","SW Monsoon","Post-Monsoon"],
        fill_value=0
    )

    print("\nSeason × ENSO")
    print(table)

    table.to_csv(f"{CSV}/{region.lower()}_season_phase.csv")

    chi2,p,dof,_=chi2_contingency(table)

    print(f"\nChi-square = {chi2:.3f}")
    print(f"P-value    = {p:.4f}")
    print("Significant:", "YES" if p<0.05 else "NO")

    summary.append({
        "Region":region,
        "ChiSquare":chi2,
        "PValue":p
    })

    ax=table.plot(kind="bar",stacked=True,figsize=(8,5))
    ax.set_ylabel("MHW Events")
    ax.set_title(f"{region}: Seasonal Distribution of MHWs by ENSO Phase")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(f"{FIG}/{region.lower()}_stacked.png",dpi=300)
    plt.close()

    totals=table.sum(axis=1)
    plt.figure(figsize=(7,4))
    totals.plot(kind="bar")
    plt.ylabel("Events")
    plt.title(f"{region}: MHW Events by Season")
    plt.tight_layout()
    plt.savefig(f"{FIG}/{region.lower()}_season_totals.png",dpi=300)
    plt.close()

summary=pd.DataFrame(summary)
summary.to_csv(f"{OUT}/summary.csv",index=False)

print("\n"+"="*70)
print("OVERALL SUMMARY")
print("="*70)
print(summary.round(3).to_string(index=False))
print("\nOutput:",OUT)

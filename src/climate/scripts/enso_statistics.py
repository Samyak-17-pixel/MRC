
#!/usr/bin/env python3
"""
ENSO Statistics Analysis

Computes descriptive statistics and statistical tests for
Marine Heatwave duration and intensity across ENSO phases.

Input:
  /home/samyak/mrc_ws/outputs/enso/lag/*_enso_lag.csv

Output:
  /home/samyak/mrc_ws/outputs/enso/statistics/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kruskal, mannwhitneyu

CATALOGUES = {
    "North": "/home/samyak/mrc_ws/outputs/enso/lag/north_enso_lag.csv",
    "Central": "/home/samyak/mrc_ws/outputs/enso/lag/central_enso_lag.csv",
    "South": "/home/samyak/mrc_ws/outputs/enso/lag/south_enso_lag.csv",
}

OUTDIR="/home/samyak/mrc_ws/outputs/enso/statistics"
CSVDIR=os.path.join(OUTDIR,"csv")
FIGDIR=os.path.join(OUTDIR,"figures")
os.makedirs(CSVDIR,exist_ok=True)
os.makedirs(FIGDIR,exist_ok=True)

pairs=[("El Nino","Neutral"),("El Nino","La Nina"),("Neutral","La Nina")]

for region,file in CATALOGUES.items():
    print("\n"+"="*70)
    print(region.upper())
    print("="*70)

    df=pd.read_csv(file)

    if "ENSO_Phase" not in df.columns:
        raise RuntimeError("ENSO_Phase column missing. Run enso_frequency_analysis.py first.")

    duration="Duration_Days"
    meanint="Mean_Intensity"

    stats=[]

    for phase in ["El Nino","Neutral","La Nina"]:
        d=df[df["ENSO_Phase"]==phase]

        stats.append({
            "Phase":phase,
            "Events":len(d),
            "MeanDuration":d[duration].mean(),
            "MedianDuration":d[duration].median(),
            "StdDuration":d[duration].std(),
            "MaxDuration":d[duration].max(),
            "MeanIntensity":d[meanint].mean(),
            "MaxIntensity":d["Max_Intensity"].max()
        })

    statsdf=pd.DataFrame(stats)
    print("\nDescriptive Statistics")
    print(statsdf.round(3).to_string(index=False))
    statsdf.to_csv(f"{CSVDIR}/{region.lower()}_descriptive.csv",index=False)

    groups_d=[df[df.ENSO_Phase==p][duration] for p in ["El Nino","Neutral","La Nina"]]
    groups_i=[df[df.ENSO_Phase==p][meanint] for p in ["El Nino","Neutral","La Nina"]]

    h_d,p_d=kruskal(*groups_d)
    h_i,p_i=kruskal(*groups_i)

    print("\nKruskal-Wallis")
    print(f"Duration : H={h_d:.3f}, p={p_d:.4f}")
    print(f"Intensity: H={h_i:.3f}, p={p_i:.4f}")

    tests=[]
    for a,b in pairs:
        da=df[df.ENSO_Phase==a][duration]
        db=df[df.ENSO_Phase==b][duration]
        ua,pa=mannwhitneyu(da,db,alternative="two-sided")

        ia=df[df.ENSO_Phase==a][meanint]
        ib=df[df.ENSO_Phase==b][meanint]
        ui,pi=mannwhitneyu(ia,ib,alternative="two-sided")

        tests.append({
            "Comparison":f"{a} vs {b}",
            "Duration_U":ua,
            "Duration_p":pa,
            "Intensity_U":ui,
            "Intensity_p":pi
        })

    testsdf=pd.DataFrame(tests)
    print("\nPairwise Mann-Whitney")
    print(testsdf.round(4).to_string(index=False))
    testsdf.to_csv(f"{CSVDIR}/{region.lower()}_pairwise.csv",index=False)

    plt.figure(figsize=(7,5))
    df.boxplot(column=duration,by="ENSO_Phase")
    plt.title(f"{region} Duration by ENSO Phase")
    plt.suptitle("")
    plt.ylabel("Duration (days)")
    plt.tight_layout()
    plt.savefig(f"{FIGDIR}/{region.lower()}_duration_boxplot.png",dpi=300)
    plt.close()

    plt.figure(figsize=(7,5))
    df.boxplot(column=meanint,by="ENSO_Phase")
    plt.title(f"{region} Mean Intensity by ENSO Phase")
    plt.suptitle("")
    plt.ylabel("Mean Intensity")
    plt.tight_layout()
    plt.savefig(f"{FIGDIR}/{region.lower()}_intensity_boxplot.png",dpi=300)
    plt.close()

print("\nAnalysis complete.")
print("Results:",OUTDIR)

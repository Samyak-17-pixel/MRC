
#!/usr/bin/env python3
"""
ENSO Strength Analysis

Classifies El Niño and La Niña events into Weak, Moderate and Strong
using ONI values associated with each Marine Heatwave event.

Outputs:
outputs/enso/strength/
    csv/
    figures/
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

CATALOGUES = {
    "North": "/home/samyak/mrc_ws/outputs/enso/lag/north_enso_lag.csv",
    "Central": "/home/samyak/mrc_ws/outputs/enso/lag/central_enso_lag.csv",
    "South": "/home/samyak/mrc_ws/outputs/enso/lag/south_enso_lag.csv",
}

OUT = "/home/samyak/mrc_ws/outputs/enso/strength"
CSV = os.path.join(OUT, "csv")
FIG = os.path.join(OUT, "figures")
os.makedirs(CSV, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

def classify_strength(oni):
    if pd.isna(oni):
        return "Unknown"
    if oni >= 2.0:
        return "Strong El Nino"
    if oni >= 1.0:
        return "Moderate El Nino"
    if oni >= 0.5:
        return "Weak El Nino"
    if oni <= -2.0:
        return "Strong La Nina"
    if oni <= -1.0:
        return "Moderate La Nina"
    if oni <= -0.5:
        return "Weak La Nina"
    return "Neutral"

summary=[]

order=[
    "Strong El Nino","Moderate El Nino","Weak El Nino",
    "Neutral",
    "Weak La Nina","Moderate La Nina","Strong La Nina"
]

for region,file in CATALOGUES.items():

    print("\n"+"="*70)
    print(region.upper())
    print("="*70)

    df=pd.read_csv(file)

    df["ENSO_Strength"]=df["ONI_0m"].apply(classify_strength)

    counts=df["ENSO_Strength"].value_counts().reindex(order,fill_value=0)

    result=pd.DataFrame({
        "Category":counts.index,
        "Events":counts.values,
        "Percentage":(counts.values/counts.sum()*100).round(2)
    })

    print(result.to_string(index=False))

    result.to_csv(f"{CSV}/{region.lower()}_strength.csv",index=False)

    collapsed=pd.Series({
        "El Nino":counts.iloc[0:3].sum(),
        "Neutral":counts.iloc[3],
        "La Nina":counts.iloc[4:7].sum()
    })

    chi2,p,_,_=chi2_contingency([[collapsed["El Nino"],collapsed["Neutral"],collapsed["La Nina"]]])

    summary.append({
        "Region":region,
        "ElNino":collapsed["El Nino"],
        "Neutral":collapsed["Neutral"],
        "LaNina":collapsed["La Nina"]
    })

    plt.figure(figsize=(9,5))
    bars=plt.bar(result["Category"],result["Events"])
    plt.xticks(rotation=30,ha="right")
    plt.ylabel("Events")
    plt.title(f"{region}: ENSO Strength Distribution")
    for b in bars:
        plt.text(b.get_x()+b.get_width()/2,b.get_height()+0.1,
                 int(b.get_height()),ha="center",fontsize=9)
    plt.tight_layout()
    plt.savefig(f"{FIG}/{region.lower()}_strength.png",dpi=300)
    plt.close()

summary=pd.DataFrame(summary)
summary.to_csv(f"{OUT}/summary.csv",index=False)

print("\n"+"="*70)
print("OVERALL SUMMARY")
print("="*70)
print(summary.to_string(index=False))
print("\nResults saved to:",OUT)

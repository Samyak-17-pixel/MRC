

"""
ENSO Frequency Analysis
-----------------------
Reads ENSO-tagged MHW catalogues and computes:
- Phase frequencies
- Percentages
- Chi-square goodness-of-fit test
- Cramer's V
- CSV outputs
- Bar plots

Input:
    /home/samyak/mrc_ws/outputs/enso/lag/*_enso_lag.csv

Output:
    /home/samyak/mrc_ws/outputs/enso/frequency/
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chisquare

CATALOGUES = {
    "North": "/home/samyak/mrc_ws/outputs/enso/lag/north_enso_lag.csv",
    "Central": "/home/samyak/mrc_ws/outputs/enso/lag/central_enso_lag.csv",
    "South": "/home/samyak/mrc_ws/outputs/enso/lag/south_enso_lag.csv",
}

OUTDIR = "/home/samyak/mrc_ws/outputs/enso/frequency"
os.makedirs(OUTDIR, exist_ok=True)

def classify(oni):
    if pd.isna(oni):
        return "Unknown"
    if oni >= 0.5:
        return "El Nino"
    if oni <= -0.5:
        return "La Nina"
    return "Neutral"

summary=[]

for region, f in CATALOGUES.items():

    print("\n"+"="*70)
    print(region.upper())
    print("="*70)

    df = pd.read_csv(f)

    if "ENSO_Phase" not in df.columns:
        df["ENSO_Phase"] = df["ONI_0m"].apply(classify)

    counts = (
        df["ENSO_Phase"]
        .value_counts()
        .reindex(["El Nino","Neutral","La Nina"], fill_value=0)
    )

    pct = counts / counts.sum() * 100

    result = pd.DataFrame({
        "Phase": counts.index,
        "Events": counts.values,
        "Percentage": pct.values
    })

    print("\nPhase Frequencies")
    print(result.round(2).to_string(index=False))

    observed = counts.values
    expected = np.repeat(observed.sum()/3, 3)

    chi2, p = chisquare(observed, expected)
    cramers_v = np.sqrt(chi2/(observed.sum()*(len(observed)-1)))

    print("\nChi-square Statistic :", round(chi2,3))
    print("P-value              :", round(p,5))
    print("Cramer's V           :", round(cramers_v,3))
    print("Significant?         :", "YES" if p < 0.05 else "NO")

    result.to_csv(f"{OUTDIR}/{region.lower()}_frequency.csv", index=False)

    plt.figure(figsize=(7,5))
    colors=["tomato","lightgray","royalblue"]
    bars=plt.bar(result["Phase"], result["Events"], color=colors)

    for b in bars:
        h=b.get_height()
        plt.text(b.get_x()+b.get_width()/2, h+0.2, int(h),
                 ha="center", fontsize=11)

    plt.ylabel("Number of MHW Events")
    plt.title(f"{region} Bay of Bengal\nENSO Phase Frequency")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTDIR}/{region.lower()}_frequency.png", dpi=300)
    plt.close()

    df.to_csv(f, index=False)

    summary.append({
        "Region": region,
        "TotalEvents": int(observed.sum()),
        "ElNino": int(observed[0]),
        "Neutral": int(observed[1]),
        "LaNina": int(observed[2]),
        "ChiSquare": chi2,
        "PValue": p,
        "CramersV": cramers_v
    })

summary = pd.DataFrame(summary)
summary.to_csv(f"{OUTDIR}/summary.csv", index=False)

print("\n"+"="*70)
print("OVERALL SUMMARY")
print("="*70)
print(summary.round(3).to_string(index=False))

print("\nOutput directory:", OUTDIR)
print("ENSO Frequency Analysis Completed Successfully.")

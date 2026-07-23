#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from scipy.stats import pearsonr
from pathlib import Path

ONI_FILE="/home/samyak/mrc_ws/data/raw/oni.nc"
CATALOGUES={
"North":"/home/samyak/mrc_ws/outputs/mhw/catalogue/north_mhw_catalogue.csv",
"Central":"/home/samyak/mrc_ws/outputs/mhw/catalogue/central_mhw_catalogue.csv",
"South":"/home/samyak/mrc_ws/outputs/mhw/catalogue/south_mhw_catalogue.csv",
}
OUTDIR="/home/samyak/mrc_ws/outputs/enso/lag"
Path(OUTDIR).mkdir(parents=True,exist_ok=True)

oni=xr.open_dataset(ONI_FILE).to_dataframe().reset_index()[["time","value"]]
oni.columns=["time","ONI"]
oni["time"]=pd.to_datetime(oni["time"])
LAGS=[0,1,2,3,6]

def get_oni(dt,lag):
    t=(pd.Timestamp(dt)-pd.DateOffset(months=lag)).replace(day=1)
    r=oni.loc[oni.time==t]
    return np.nan if len(r)==0 else float(r.ONI.iloc[0])

summary=[]
for region,file in CATALOGUES.items():
    df=pd.read_csv(file)
    df["Start_Date"]=pd.to_datetime(df["Start_Date"])
    for lag in LAGS:
        df[f"ONI_{lag}m"]=df["Start_Date"].apply(lambda x:get_oni(x,lag))
    df.to_csv(f"{OUTDIR}/{region.lower()}_enso_lag.csv",index=False)

    dur=[c for c in df.columns if "Duration" in c][0]
    inten=[c for c in df.columns if "Mean" in c and "Intensity" in c][0]

    rows=[]
    for lag in LAGS:
        d=df[[dur,inten,f"ONI_{lag}m"]].dropna()
        if len(d)>2:
            rd,pd_=pearsonr(d[f"ONI_{lag}m"],d[dur])
            ri,pi=pearsonr(d[f"ONI_{lag}m"],d[inten])
        else:
            rd=pd_=ri=pi=np.nan
        rows.append({"Lag":lag,"Duration_r":rd,"Duration_p":pd_,"Intensity_r":ri,"Intensity_p":pi})

    corr = pd.DataFrame(rows)

    corr.to_csv(
        f"{OUTDIR}/{region.lower()}_lag_correlation.csv",
        index=False
    )

    print("\nLag Correlation Results")
    print("-"*70)

    print(
        corr.round(3).to_string(index=False)
    )

    plt.figure(figsize=(7,4))
    plt.plot(corr["Lag"],corr["Duration_r"],marker="o",label="Duration")
    plt.plot(corr["Lag"],corr["Intensity_r"],marker="s",label="Intensity")
    plt.axhline(0,color="black")
    plt.grid(alpha=.3)
    plt.legend()
    plt.xlabel("Lag (months)")
    plt.ylabel("Pearson r")
    plt.title(region)
    plt.tight_layout()
    plt.savefig(f"{OUTDIR}/{region.lower()}_lag.png",dpi=300)
    plt.close()

    best = corr.iloc[
    corr["Duration_r"].abs().idxmax()
    ]

    print("\nStrongest Relationship")

    print(f"Best Lag              : {int(best['Lag'])} month(s)")
    print(f"Duration Correlation  : {best['Duration_r']:.3f}")
    print(f"P-value               : {best['Duration_p']:.4f}")

    if best["Duration_p"] < 0.05:
        print("Statistical Significance : YES (p < 0.05)")
    else:
        print("Statistical Significance : NO")

    summary.append({

        "Region": region,

        "BestLag": int(best["Lag"]),

        "BestCorrelation": best["Duration_r"],

        "Pvalue": best["Duration_p"]

    })
pd.DataFrame(summary).to_csv(f"{OUTDIR}/summary.csv",index=False)
summary = pd.DataFrame(summary)

summary.to_csv(
    f"{OUTDIR}/summary.csv",
    index=False
)

print("\n")
print("="*70)
print("OVERALL SUMMARY")
print("="*70)

print(summary.round(3).to_string(index=False))

print("\nFiles Generated")
print("-"*70)

print(f"{OUTDIR}/summary.csv")

for region in CATALOGUES:

    print(f"{OUTDIR}/{region.lower()}_enso_lag.csv")

    print(f"{OUTDIR}/{region.lower()}_lag_correlation.csv")

    print(f"{OUTDIR}/{region.lower()}_lag.png")

print("\nENSO Lag Analysis Completed Successfully.")

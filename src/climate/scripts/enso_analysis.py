import os
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

DATA = os.path.expanduser("~/mrc_ws/data/raw/oni.nc")

OUT = os.path.expanduser(
    "~/mrc_ws/outputs/climate_indices/enso"
)

CSV = os.path.join(OUT, "csv")
FIG = os.path.join(OUT, "figures")

os.makedirs(CSV, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

ds = xr.open_dataset(DATA)

df = ds.to_dataframe().reset_index()

df = df.rename(columns={"value":"ONI"})

df = df[(df.time.dt.year>=2006)&(df.time.dt.year<=2025)]

def phase(v):

    if v>=0.5:
        return "El Nino"

    elif v<=-0.5:
        return "La Nina"

    else:
        return "Neutral"

df["Phase"]=df["ONI"].apply(phase)

df.to_csv(os.path.join(CSV,"oni_timeseries.csv"),index=False)

monthly=df.groupby(df.time.dt.month)["ONI"].mean()

monthly.to_csv(
    os.path.join(CSV,"monthly_climatology.csv")
)

annual=df.groupby(df.time.dt.year)["ONI"].mean()

annual.to_csv(
    os.path.join(CSV,"annual_mean.csv")
)

summary=df["Phase"].value_counts()

summary.to_csv(
    os.path.join(CSV,"phase_counts.csv")
)

plt.figure(figsize=(14,4))

plt.plot(df.time,df.ONI)

plt.axhline(0.5,color='r',ls='--')

plt.axhline(-0.5,color='b',ls='--')

plt.grid()

plt.title("Oceanic Niño Index")

plt.tight_layout()

plt.savefig(os.path.join(FIG,"oni_timeseries.png"))

plt.close()

plt.figure(figsize=(6,5))

plt.hist(df.ONI,bins=20)

plt.grid()

plt.title("ONI Distribution")

plt.tight_layout()

plt.savefig(os.path.join(FIG,"oni_histogram.png"))

plt.close()

plt.figure(figsize=(8,4))

monthly.plot(marker='o')

plt.grid()

plt.title("Monthly Mean ONI")

plt.tight_layout()

plt.savefig(os.path.join(FIG,"monthly_climatology.png"))

plt.close()

plt.figure(figsize=(12,4))

annual.plot(marker='o')

plt.grid()

plt.title("Annual Mean ONI")

plt.tight_layout()

plt.savefig(os.path.join(FIG,"annual_mean.png"))

plt.close()

print(summary)

print()

print(df.describe())

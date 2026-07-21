import os
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PATHS
# ============================================================

DATA = os.path.expanduser(
    "~/mrc_ws/datasets/meiv2.nc"
)

OUT = os.path.expanduser(
    "~/mrc_ws/results/climate_indices/mei"
)

CSV = os.path.join(OUT, "csv")
FIG = os.path.join(OUT, "figures")

os.makedirs(CSV, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================

ds = xr.open_dataset(DATA)

df = ds.to_dataframe().reset_index()

df = df.rename(columns={"value": "MEI"})

# Only keep project years

df = df[
    (df.time.dt.year >= 2006) &
    (df.time.dt.year <= 2025)
]

# ============================================================
# SAVE COMPLETE CSV
# ============================================================

df.to_csv(
    os.path.join(
        CSV,
        "mei_timeseries.csv"
    ),
    index=False
)

# ============================================================
# MONTHLY CLIMATOLOGY
# ============================================================

monthly = (
    df.groupby(df.time.dt.month)["MEI"]
      .mean()
)

monthly.to_csv(
    os.path.join(
        CSV,
        "monthly_climatology.csv"
    )
)

# ============================================================
# ANNUAL MEAN
# ============================================================

annual = (
    df.groupby(df.time.dt.year)["MEI"]
      .mean()
)

annual.to_csv(
    os.path.join(
        CSV,
        "annual_mean.csv"
    )
)

# ============================================================
# SUMMARY STATISTICS
# ============================================================

summary = pd.DataFrame({

    "Statistic":[

        "Minimum",

        "Maximum",

        "Mean",

        "Median",

        "Standard Deviation"

    ],

    "Value":[

        df.MEI.min(),

        df.MEI.max(),

        df.MEI.mean(),

        df.MEI.median(),

        df.MEI.std()

    ]

})

summary.to_csv(

    os.path.join(

        CSV,

        "summary_statistics.csv"

    ),

    index=False

)

# ============================================================
# TIME SERIES
# ============================================================

plt.figure(figsize=(15,5))

plt.plot(

    df.time,

    df.MEI,

    linewidth=1.8

)

plt.axhline(
    0,
    color='black',
    linestyle='--'
)

plt.grid(alpha=0.3)

plt.title(
    "Multivariate ENSO Index Version 2 (2006-2025)"
)

plt.xlabel("Year")

plt.ylabel("MEI")

plt.tight_layout()

plt.savefig(

    os.path.join(

        FIG,

        "mei_timeseries.png"

    ),

    dpi=300

)

plt.close()

# ============================================================
# HISTOGRAM
# ============================================================

plt.figure(figsize=(7,5))

plt.hist(

    df.MEI,

    bins=20,

    edgecolor='black'

)

plt.grid(alpha=0.3)

plt.title(
    "Distribution of MEI"
)

plt.xlabel("MEI")

plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig(

    os.path.join(

        FIG,

        "mei_histogram.png"

    ),

    dpi=300

)

plt.close()

# ============================================================
# MONTHLY CLIMATOLOGY
# ============================================================

plt.figure(figsize=(8,4))

plt.plot(

    monthly.index,

    monthly.values,

    marker='o',

    linewidth=2

)

plt.xticks(range(1,13))

plt.grid(alpha=0.3)

plt.title(
    "Monthly Mean MEI"
)

plt.xlabel("Month")

plt.ylabel("MEI")

plt.tight_layout()

plt.savefig(

    os.path.join(

        FIG,

        "monthly_climatology.png"

    ),

    dpi=300

)

plt.close()

# ============================================================
# ANNUAL MEAN
# ============================================================

plt.figure(figsize=(12,4))

plt.plot(

    annual.index,

    annual.values,

    marker='o',

    linewidth=2

)

plt.grid(alpha=0.3)

plt.title(
    "Annual Mean MEI"
)

plt.xlabel("Year")

plt.ylabel("MEI")

plt.tight_layout()

plt.savefig(

    os.path.join(

        FIG,

        "annual_mean.png"

    ),

    dpi=300

)

plt.close()

# ============================================================
# 12-MONTH RUNNING MEAN
# ============================================================

df["RunningMean"] = df["MEI"].rolling(
    12,
    center=True
).mean()

plt.figure(figsize=(15,5))

plt.plot(

    df.time,

    df.MEI,

    alpha=0.4,

    label="Monthly"

)

plt.plot(

    df.time,

    df.RunningMean,

    color='red',

    linewidth=2,

    label="12-month Running Mean"

)

plt.grid(alpha=0.3)

plt.legend()

plt.title(
    "12-Month Running Mean of MEI"
)

plt.tight_layout()

plt.savefig(

    os.path.join(

        FIG,

        "running_mean.png"

    ),

    dpi=300

)

plt.close()

# ============================================================
# YEARLY TABLE
# ============================================================

yearly = df.groupby(df.time.dt.year).agg({

    "MEI":["mean","max","min","std"]

})

yearly.columns = [

    "Mean",

    "Maximum",

    "Minimum",

    "Std_Dev"

]

yearly.to_csv(

    os.path.join(

        CSV,

        "yearly_statistics.csv"

    )

)

# ============================================================
# MONTHLY TABLE
# ============================================================

monthly_table = df.groupby(df.time.dt.month).agg({

    "MEI":["mean","max","min","std"]

})

monthly_table.columns = [

    "Mean",

    "Maximum",

    "Minimum",

    "Std_Dev"

]

monthly_table.to_csv(

    os.path.join(

        CSV,

        "monthly_statistics.csv"

    )

)

# ============================================================
# PRINT RESULTS
# ============================================================

print("\n===================================")
print("MEI ANALYSIS")
print("===================================")

print("\nTotal Months :", len(df))

print("\nSummary Statistics")

print(summary)

print("\nYearly Statistics")

print(yearly)

print("\nFinished.")

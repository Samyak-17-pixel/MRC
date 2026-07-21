import xarray as xr
import numpy as np
import pandas as pd

files = {
    "ONI (ENSO)": "~/mrc_ws/datasets/oni.nc",
    "IOD (DMI)": "~/mrc_ws/datasets/dmi.had.long.nc",
    "MEI v2": "~/mrc_ws/datasets/meiv2.nc"
}

for name, file in files.items():

    print("\n" + "="*80)
    print(name)
    print("="*80)

    ds = xr.open_dataset(file)

    print("\nDATASET SUMMARY")
    print("-"*80)
    print(ds)

    print("\nVARIABLES")
    print("-"*80)
    print(list(ds.data_vars))

    print("\nCOORDINATES")
    print("-"*80)
    print(list(ds.coords))

    var = list(ds.data_vars)[0]

    print("\nMAIN VARIABLE")
    print("-"*80)
    print(var)

    print("\nTIME RANGE")
    print("-"*80)
    print("Start :", str(ds.time.min().values))
    print("End   :", str(ds.time.max().values))

    print("\nNUMBER OF MONTHS")
    print("-"*80)
    print(len(ds.time))

    print("\nSTATISTICS")
    print("-"*80)
    print("Minimum :", float(ds[var].min()))
    print("Maximum :", float(ds[var].max()))
    print("Mean    :", float(ds[var].mean()))
    print("Std Dev :", float(ds[var].std()))

    print("\nFIRST 10 VALUES")
    print("-"*80)
    df = pd.DataFrame({
        "Date": ds.time.values[:10],
        "Value": ds[var].values[:10]
    })
    print(df)

    print("\nLAST 10 VALUES")
    print("-"*80)
    df = pd.DataFrame({
        "Date": ds.time.values[-10:],
        "Value": ds[var].values[-10:]
    })
    print(df)

print("\nInspection Complete.")

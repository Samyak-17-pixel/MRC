import xarray as xr
import numpy as np

files = {
    "LATENT_HEAT_FLUX":
    "/home/samyak/mrc_ws/datasets/heat_flux_data_2006_2025/heat_flux_2006/surface_latent_heat_flux_stream-oper_daily-mean.nc",

    "SENSIBLE_HEAT_FLUX":
    "/home/samyak/mrc_ws/datasets/heat_flux_data_2006_2025/heat_flux_2006/surface_sensible_heat_flux_0_daily-mean.nc"
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

    print("\nDIMENSIONS")
    print("-"*80)
    print(ds.dims)

    # Find main variable automatically
    var = list(ds.data_vars)[0]

    print("\nMAIN VARIABLE")
    print("-"*80)
    print(var)

    # Time coordinate
    if "time" in ds.coords:

        print("\nTIME RANGE")
        print("-"*80)
        print("Start:", ds["time"].min().values)
        print("End  :", ds["time"].max().values)

    elif "valid_time" in ds.coords:

        print("\nTIME RANGE")
        print("-"*80)
        print("Start:", ds["valid_time"].min().values)
        print("End  :", ds["valid_time"].max().values)

    # Latitude coordinate
    lat_name = None

    for c in ds.coords:
        if "lat" in c.lower():
            lat_name = c
            break

    if lat_name:

        print("\nLATITUDE RANGE")
        print("-"*80)
        print(float(ds[lat_name].min()))
        print(float(ds[lat_name].max()))

    # Longitude coordinate
    lon_name = None

    for c in ds.coords:
        if "lon" in c.lower():
            lon_name = c
            break

    if lon_name:

        print("\nLONGITUDE RANGE")
        print("-"*80)
        print(float(ds[lon_name].min()))
        print(float(ds[lon_name].max()))

    # Statistics
    print("\nSTATISTICS")
    print("-"*80)

    data = ds[var]

    print("Min  :", float(data.min()))
    print("Max  :", float(data.max()))
    print("Mean :", float(data.mean()))

    print("\nFIRST TIMESTEP SAMPLE")
    print("-"*80)

    try:

        if "time" in data.dims:

            sample = data.isel(time=0)

        elif "valid_time" in data.dims:

            sample = data.isel(valid_time=0)

        else:

            sample = data

        print(sample)

    except Exception as e:

        print("Unable to display sample")
        print(e)

print("\nInspection Complete")
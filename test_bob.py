import xarray as xr
import matplotlib.pyplot as plt

# =====================================================
# Load SST Dataset
# =====================================================

file_path = "/home/samyak/mrc_ws/datasets/sst.day.mean.2016" \
".nc"

print("Opening dataset...")

ds = xr.open_dataset(file_path)

print("\nDataset Summary:")
print(ds)

# =====================================================
# Extract Bay of Bengal
# =====================================================

print("\nExtracting Bay of Bengal...")

bob = ds.sel(
    lat=slice(0, 30),
    lon=slice(75, 100)
)

print(bob)

# =====================================================
# Plot First SST Map
# =====================================================

print("\nPlotting SST map for first day...")

plt.figure(figsize=(10,6))

bob.sst.isel(time=0).plot()

plt.title("Bay of Bengal SST - 2025-01-01")

plt.tight_layout()

plt.show()

# =====================================================
# Define Regions
# =====================================================

north = bob.sel(
    lat=slice(15,22),
    lon=slice(85,95)
)

central = bob.sel(
    lat=slice(10,15),
    lon=slice(85,95)
)

south = bob.sel(
    lat=slice(5,10),
    lon=slice(85,95)
)

# =====================================================
# Compute Daily Mean SST
# =====================================================

print("\nComputing regional SST time series...")

north_sst = north.sst.mean(dim=["lat","lon"])

central_sst = central.sst.mean(dim=["lat","lon"])

south_sst = south.sst.mean(dim=["lat","lon"])

# =====================================================
# Plot Regional SST
# =====================================================

plt.figure(figsize=(14,6))

north_sst.plot(label="North BoB")

central_sst.plot(label="Central BoB")

south_sst.plot(label="South BoB")

plt.title("Daily Mean SST (2025)")

plt.ylabel("SST (°C)")

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()

# =====================================================
# Print Statistics
# =====================================================

print("\nNorth BoB")
print("Mean SST =", float(north_sst.mean()))

print("\nCentral BoB")
print("Mean SST =", float(central_sst.mean()))

print("\nSouth BoB")
print("Mean SST =", float(south_sst.mean()))

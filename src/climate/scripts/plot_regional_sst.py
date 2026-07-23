import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS = "/home/samyak/mrc_ws/outputs"

north = pd.read_csv(f"{RESULTS}/timeseries/north_bob_sst.csv")
central = pd.read_csv(f"{RESULTS}/timeseries/central_bob_sst.csv")
south = pd.read_csv(f"{RESULTS}/timeseries/south_bob_sst.csv")

north["Date"] = pd.to_datetime(north["Date"])
central["Date"] = pd.to_datetime(central["Date"])
south["Date"] = pd.to_datetime(south["Date"])

fig_dir = Path(f"{RESULTS}/mhw/figures")
fig_dir.mkdir(exist_ok=True)

plt.figure(figsize=(14,5))
plt.plot(north["Date"], north["SST"])
plt.title("North Bay of Bengal SST (2006–2025)")
plt.ylabel("SST (°C)")
plt.grid(True)
plt.tight_layout()
plt.savefig(fig_dir / "north_bob_sst.png", dpi=300)
plt.close()

plt.figure(figsize=(14,5))
plt.plot(central["Date"], central["SST"])
plt.title("Central Bay of Bengal SST (2006–2025)")
plt.ylabel("SST (°C)")
plt.grid(True)
plt.tight_layout()
plt.savefig(fig_dir / "central_bob_sst.png", dpi=300)
plt.close()

plt.figure(figsize=(14,5))
plt.plot(south["Date"], south["SST"])
plt.title("South Bay of Bengal SST (2006–2025)")
plt.ylabel("SST (°C)")
plt.grid(True)
plt.tight_layout()
plt.savefig(fig_dir / "south_bob_sst.png", dpi=300)
plt.close()

plt.figure(figsize=(16,6))

plt.plot(north["Date"], north["SST"], label="North")
plt.plot(central["Date"], central["SST"], label="Central")
plt.plot(south["Date"], south["SST"], label="South")

plt.title("Bay of Bengal Regional SST Comparison (2006–2025)")
plt.ylabel("SST (°C)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    fig_dir / "all_regions_sst.png",
    dpi=300
)

plt.close()

print("Figures saved to:")
print(fig_dir)

import pandas as pd
import matplotlib.pyplot as plt

north = pd.read_csv(
    "/home/samyak/mrc_ws/results/north_bob_sst.csv"
)

central = pd.read_csv(
    "/home/samyak/mrc_ws/results/central_bob_sst.csv"
)

south = pd.read_csv(
    "/home/samyak/mrc_ws/results/south_bob_sst.csv"
)

north["Date"] = pd.to_datetime(north["Date"])
central["Date"] = pd.to_datetime(central["Date"])
south["Date"] = pd.to_datetime(south["Date"])

plt.figure(figsize=(15,6))

plt.plot(
    north["Date"],
    north["SST"],
    label="North"
)

plt.plot(
    central["Date"],
    central["SST"],
    label="Central"
)

plt.plot(
    south["Date"],
    south["SST"],
    label="South"
)

plt.legend()

plt.grid()

plt.savefig(
    "/home/samyak/mrc_ws/results/figures/regional_sst_2016_2025.png",
    dpi=300
)

plt.show()

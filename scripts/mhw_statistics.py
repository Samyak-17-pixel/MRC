import pandas as pd

regions = ["north", "central", "south"]

for region in regions:

    df = pd.read_csv(
        f"/home/samyak/mrc_ws/results/mhw_catalogue/{region}_mhw_catalogue.csv"
    )

    print("\n====================")
    print(region.upper())
    print("====================")

    print("Total Events:",
          len(df))

    print("Longest Event:",
          df["Duration_Days"].max())

    print("Mean Duration:",
          round(df["Duration_Days"].mean(),2))

    print("Max Intensity:",
          round(df["Max_Intensity"].max(),3))

    print("Mean Intensity:",
          round(df["Mean_Intensity"].mean(),3))

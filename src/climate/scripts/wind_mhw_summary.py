import pandas as pd

regions = ["north", "central", "south"]

for region in regions:

    df = pd.read_csv(
        f"/home/samyak/mrc_ws/outputs/drivers/wind/{region}_wind_mhw_analysis.csv"
    )

    total = len(df)

    weaker = (df["Change_30d"] < 0).sum()
    stronger = (df["Change_30d"] > 0).sum()
    same = (df["Change_30d"] == 0).sum()

    weaker_pct = 100 * weaker / total
    stronger_pct = 100 * stronger / total

    print("\n" + "="*40)
    print(region.upper())
    print("="*40)

    print(f"Total MHW Events      : {total}")
    print(f"Weaker Winds During   : {weaker}")
    print(f"Stronger Winds During : {stronger}")
    print(f"No Change             : {same}")

    print()

    print(f"Weaker Winds (%)      : {weaker_pct:.1f}")
    print(f"Stronger Winds (%)    : {stronger_pct:.1f}")

    print()

    print(
        f"Mean Wind Change (m/s): "
        f"{df['Change_30d'].mean():.3f}"
    )

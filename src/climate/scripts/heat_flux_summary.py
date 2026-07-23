import pandas as pd

BASE = "/home/samyak/mrc_ws/outputs/drivers/heat_flux_analysis"

for region in ["north", "central", "south"]:

    df = pd.read_csv(
        f"{BASE}/{region}_heat_flux_analysis.csv"
    )

    total = len(df)

    reduced_latent = (
        df["SLHF_Anomaly"] > 0
    ).sum()

    enhanced_latent = (
        df["SLHF_Anomaly"] < 0
    ).sum()

    reduced_latent_pct = (
        reduced_latent / total * 100
    )

    enhanced_latent_pct = (
        enhanced_latent / total * 100
    )

    reduced_sensible = (
        df["SSHF_Anomaly"] > 0
    ).sum()

    enhanced_sensible = (
        df["SSHF_Anomaly"] < 0
    ).sum()

    reduced_sensible_pct = (
        reduced_sensible / total * 100
    )

    enhanced_sensible_pct = (
        enhanced_sensible / total * 100
    )

    print("\n")
    print("=" * 60)
    print(region.upper())
    print("=" * 60)

    print(f"Total Events               : {total}")

    print("\nLATENT HEAT FLUX")

    print(
        f"Reduced Heat Loss          : {reduced_latent}"
    )

    print(
        f"Enhanced Heat Loss         : {enhanced_latent}"
    )

    print(
        f"Reduced Heat Loss (%)      : {reduced_latent_pct:.1f}"
    )

    print(
        f"Enhanced Heat Loss (%)     : {enhanced_latent_pct:.1f}"
    )

    print("\nSENSIBLE HEAT FLUX")

    print(
        f"Reduced Heat Loss          : {reduced_sensible}"
    )

    print(
        f"Enhanced Heat Loss         : {enhanced_sensible}"
    )

    print(
        f"Reduced Heat Loss (%)      : {reduced_sensible_pct:.1f}"
    )

    print(
        f"Enhanced Heat Loss (%)     : {enhanced_sensible_pct:.1f}"
    )

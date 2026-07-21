"""
==================================================================
Bay of Bengal Mapping Library
Maritime Research Center (MRC)

Author: Samyak Kumar
==================================================================
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# ---------------------------------------------------------
# Bay of Bengal Domain
# ---------------------------------------------------------

LON_MIN = 79
LON_MAX = 100

LAT_MIN = 4
LAT_MAX = 25


# ---------------------------------------------------------
# Create Base Map
# ---------------------------------------------------------

def create_base_map(figsize=(8, 9)):

    fig = plt.figure(figsize=figsize)

    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_extent(
        [LON_MIN,
         LON_MAX,
         LAT_MIN,
         LAT_MAX],
        ccrs.PlateCarree()
    )

    # -------------------------------------------------
    # Ocean
    # -------------------------------------------------

    ax.add_feature(
        cfeature.OCEAN,
        facecolor="#cfe8ff",
        zorder=0
    )

    # -------------------------------------------------
    # Land
    # -------------------------------------------------

    ax.add_feature(
        cfeature.LAND,
        facecolor="#f4ecd8",
        edgecolor="black",
        linewidth=0.4,
        zorder=1
    )

    # -------------------------------------------------
    # Coastlines
    # -------------------------------------------------

    ax.coastlines(
        resolution="10m",
        linewidth=0.8
    )

    # -------------------------------------------------
    # Borders
    # -------------------------------------------------

    ax.add_feature(
        cfeature.BORDERS,
        linewidth=0.5
    )

    # -------------------------------------------------
    # Rivers
    # -------------------------------------------------

    ax.add_feature(
        cfeature.RIVERS,
        linewidth=0.25,
        alpha=0.4
    )

    # -------------------------------------------------
    # Grid
    # -------------------------------------------------

    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.5,
        linestyle="--",
        alpha=0.5
    )

    gl.top_labels = False
    gl.right_labels = False

    gl.xlabel_style = {
        "size": 10
    }

    gl.ylabel_style = {
        "size": 10
    }

    return fig, ax


# ---------------------------------------------------------
# Draw North / Central / South Regions
# ---------------------------------------------------------

def draw_regions(ax):

    # Horizontal boundaries

    ax.plot(
        [80,100],
        [18,18],
        transform=ccrs.PlateCarree(),
        color="red",
        linewidth=2
    )

    ax.plot(
        [80,100],
        [12,12],
        transform=ccrs.PlateCarree(),
        color="red",
        linewidth=2
    )

    # Labels

    ax.text(
        90,
        21.5,
        "NORTH",
        fontsize=13,
        weight="bold",
        ha="center",
        transform=ccrs.PlateCarree()
    )

    ax.text(
        90,
        15,
        "CENTRAL",
        fontsize=13,
        weight="bold",
        ha="center",
        transform=ccrs.PlateCarree()
    )

    ax.text(
        90,
        8,
        "SOUTH",
        fontsize=13,
        weight="bold",
        ha="center",
        transform=ccrs.PlateCarree()
    )


# ---------------------------------------------------------
# Country Labels
# ---------------------------------------------------------

def draw_country_labels(ax):

    countries = {

        "India": (77.5,18),

        "Sri Lanka": (80.5,7),

        "Bangladesh": (90.3,24),

        "Myanmar": (98.3,18)

    }

    for country,(x,y) in countries.items():

        ax.text(
            x,
            y,
            country,
            fontsize=9,
            weight="bold",
            transform=ccrs.PlateCarree()
        )


# ---------------------------------------------------------
# North Arrow
# ---------------------------------------------------------

def add_north_arrow(ax):

    ax.annotate(
        "N",
        xy=(0.95,0.90),
        xytext=(0.95,0.80),
        xycoords="axes fraction",
        arrowprops=dict(
            facecolor="black",
            width=3,
            headwidth=10
        ),
        ha="center",
        fontsize=12,
        fontweight="bold"
    )


# ---------------------------------------------------------
# Complete Map
# ---------------------------------------------------------

def plot_base_map():

    fig, ax = create_base_map()

    draw_regions(ax)

    draw_country_labels(ax)

    add_north_arrow(ax)

    plt.title(
        "Bay of Bengal Study Region",
        fontsize=18,
        weight="bold"
    )

    return fig, ax


# ---------------------------------------------------------
# Run Standalone
# ---------------------------------------------------------

if __name__ == "__main__":

    fig, ax = plot_base_map()

    plt.savefig(
        "bay_of_bengal_base_map.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
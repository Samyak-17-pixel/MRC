#!/usr/bin/env python3


import os
import warnings

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from scipy.stats import linregress

warnings.filterwarnings("ignore")

class ENSOFigureGenerator:

    """
    Generate publication-quality figures
    for ENSO analysis.
    """

    def __init__(self):

        self.project = "/home/samyak/mrc_ws"

        self.results = os.path.join(

            self.project,

            "results"

        )

        self.output = os.path.join(

            self.results,

            "publication_figures"

        )

        self.make_directories()

        self.set_style()

        print("="*80)
        print("Marine Heatwave ENSO Figure Generator")
        print("="*80)

    def make_directories(self):

        folders=[

            "frequency",

            "lag",

            "duration",

            "intensity",

            "annual",

            "seasonal",

            "strength",

            "summary"

        ]

        for folder in folders:

            os.makedirs(

                os.path.join(

                    self.output,

                    folder

                ),

                exist_ok=True

            )

    def set_style(self):

        plt.style.use("default")

        plt.rcParams.update({

            "figure.figsize":(10,7),

            "figure.dpi":300,

            "savefig.dpi":600,

            "font.family":"serif",

            "font.size":14,

            "axes.titlesize":18,

            "axes.labelsize":15,

            "axes.grid":True,

            "grid.alpha":0.25,

            "lines.linewidth":2.5,

            "legend.fontsize":12,

            "xtick.labelsize":12,

            "ytick.labelsize":12

        })

        self.enso_colors={

            "El Nino":"firebrick",

            "Neutral":"gray",

            "La Nina":"royalblue"

        }

        self.region_colors={

            "North":"darkred",

            "Central":"forestgreen",

            "South":"navy"

        }

    def save(self,

             folder,

             filename):

        directory=os.path.join(

            self.output,

            folder

        )

        png=os.path.join(

            directory,

            filename+".png"

        )

        pdf=os.path.join(

            directory,

            filename+".pdf"

        )

        plt.tight_layout()

        plt.savefig(

            png,

            dpi=600,

            bbox_inches="tight"

        )

        plt.savefig(

            pdf,

            bbox_inches="tight"

        )

        plt.close()

        print(f"Saved {filename}")

    def load_csv(self,

                 relative_path):

        file=os.path.join(

            self.results,

            relative_path

        )

        if not os.path.exists(file):

            raise FileNotFoundError(file)

        print("Loading",relative_path)

        return pd.read_csv(file)

    def publication_title(self,

                          title):

        plt.title(

            title,

            fontsize=18,

            weight="bold",

            pad=15

        )

    def beautify_axis(self,

                      ax):

        ax.spines["top"].set_visible(False)

        ax.spines["right"].set_visible(False)

        ax.tick_params(

            length=6,

            width=1.2

        )

        ax.grid(

            alpha=0.25

        )

    def add_bar_labels(self,

                       ax):

        for container in ax.containers:

            ax.bar_label(

                container,

                fontsize=10

            )

    def load_frequency_data(self):

        north = self.load_csv(
            "enso_frequency/north_frequency.csv"
        )

        central = self.load_csv(
            "enso_frequency/central_frequency.csv"
        )

        south = self.load_csv(
            "enso_frequency/south_frequency.csv"
        )

        return north, central, south

    def figure1_grouped_frequency(self):

        north, central, south = self.load_frequency_data()

        phases = north["Phase"]

        x = np.arange(len(phases))

        width = 0.25

        fig, ax = plt.subplots(figsize=(10,7))

        ax.bar(
            x-width,
            north["Events"],
            width,
            color="darkred",
            label="North"
        )

        ax.bar(
            x,
            central["Events"],
            width,
            color="forestgreen",
            label="Central"
        )

        ax.bar(
            x+width,
            south["Events"],
            width,
            color="navy",
            label="South"
        )

        ax.set_xticks(x)

        ax.set_xticklabels(phases)

        ax.set_ylabel("Number of Marine Heatwaves")

        self.publication_title(
            "Marine Heatwave Frequency by ENSO Phase"
        )

        self.beautify_axis(ax)

        self.add_bar_labels(ax)

        ax.legend()

        self.save(
            "frequency",
            "Figure1_Grouped_Frequency"
        )

    def figure2_stacked_frequency(self):

        north, central, south = self.load_frequency_data()

        phases = north["Phase"]

        north_events = north["Events"]

        central_events = central["Events"]

        south_events = south["Events"]

        fig, ax = plt.subplots(figsize=(10,7))

        ax.bar(

            phases,

            north_events,

            color="darkred",

            label="North"

        )

        ax.bar(

            phases,

            central_events,

            bottom=north_events,

            color="forestgreen",

            label="Central"

        )

        ax.bar(

            phases,

            south_events,

            bottom=north_events+central_events,

            color="navy",

            label="South"

        )

        ax.set_ylabel("Total Marine Heatwaves")

        self.publication_title(

            "Stacked Marine Heatwave Frequency"

        )

        self.beautify_axis(ax)

        ax.legend()

        self.save(

            "frequency",

            "Figure2_Stacked_Frequency"

        )

    def figure3_percentage_frequency(self):

        north, central, south = self.load_frequency_data()

        phases = north["Phase"]

        x = np.arange(len(phases))

        width = 0.25

        fig, ax = plt.subplots(figsize=(10,7))

        ax.bar(

            x-width,

            north["Percentage"],

            width,

            color="darkred",

            label="North"

        )

        ax.bar(

            x,

            central["Percentage"],

            width,

            color="forestgreen",

            label="Central"

        )

        ax.bar(

            x+width,

            south["Percentage"],

            width,

            color="navy",

            label="South"

        )

        ax.set_xticks(x)

        ax.set_xticklabels(phases)

        ax.set_ylabel("Percentage (%)")

        ax.yaxis.set_major_formatter(

            ticker.PercentFormatter()

        )

        self.publication_title(

            "Percentage Distribution of Marine Heatwaves"

        )

        self.beautify_axis(ax)

        ax.legend()

        self.save(

            "frequency",

            "Figure3_Percentage"

        )

    def figure4_piecharts(self):

        north, central, south = self.load_frequency_data()

        fig, axes = plt.subplots(

            1,

            3,

            figsize=(15,5)

        )

        colours = [

            "crimson",

            "gray",

            "royalblue"

        ]

        datasets = [

            ("North", north),

            ("Central", central),

            ("South", south)

        ]

        for ax, (title, df) in zip(axes, datasets):

            ax.pie(

                df["Events"],

                labels=df["Phase"],

                autopct="%1.1f%%",

                colors=colours,

                startangle=90

            )

            ax.set_title(title)

        plt.tight_layout()

        plt.savefig(

            os.path.join(

                self.output,

                "frequency",

                "Figure4_PieCharts.png"

            ),

            dpi=600,

            bbox_inches="tight"

        )

        plt.savefig(

            os.path.join(

                self.output,

                "frequency",

                "Figure4_PieCharts.pdf"

            ),

            bbox_inches="tight"

        )

        plt.close()

    def generate_frequency_figures(self):

        print("\nGenerating Frequency Figures...")

        self.figure1_grouped_frequency()

        self.figure2_stacked_frequency()

        self.figure3_percentage_frequency()

        self.figure4_piecharts()

        print("Frequency figures completed.")

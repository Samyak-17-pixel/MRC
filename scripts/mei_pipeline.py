#!/usr/bin/env python3
# =============================================================================
# MEI v2 ANALYSIS PIPELINE
# =============================================================================
#
# Author : Samyak Kumar
#
# Orchestrates the full MEI v2 analysis workflow, mirroring ENSO and IOD.
#
# Stages:
#   1. mei_lag_analysis.py       - Event tagging + lag correlations
#   2. mei_frequency_analysis.py   - Phase frequency + chi-square
#   3. mei_statistics.py           - Descriptive stats + non-parametric tests
#   4. mei_annual_analysis.py      - Annual variability + correlations
#   5. mei_seasonal_analysis.py    - Season × phase contingency
#   6. mei_strength_analysis.py    - MEI magnitude classification
#
# =============================================================================

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PYTHON = sys.executable

STAGES = [
    ("mei_lag_analysis.py", "Event tagging and lag correlation"),
    ("mei_frequency_analysis.py", "MEI phase frequency analysis"),
    ("mei_statistics.py", "Duration and intensity statistics"),
    ("mei_annual_analysis.py", "Annual variability analysis"),
    ("mei_seasonal_analysis.py", "Seasonal dependence analysis"),
    ("mei_strength_analysis.py", "MEI strength classification"),
]


def run_stage(script_name, description):
    script = SCRIPTS_DIR / script_name
    print(f"\n{'=' * 80}")
    print(f"STAGE: {description}")
    print(f"Script: {script_name}")
    print(f"{'=' * 80}\n")

    result = subprocess.run(
        [PYTHON, str(script)],
        cwd=str(SCRIPTS_DIR.parent),
    )

    if result.returncode != 0:
        print(f"\nERROR: {script_name} failed with code {result.returncode}")
        sys.exit(result.returncode)

    print(f"\n{script_name} completed successfully.")


if __name__ == "__main__":
    print("=" * 80)
    print("MEI v2 ANALYSIS PIPELINE")
    print("Bay of Bengal Marine Heatwave Project")
    print("=" * 80)

    for i, (script, desc) in enumerate(STAGES, 1):
        print(f"\n[{i}/{len(STAGES)}] {desc}")
        run_stage(script, desc)

    print(f"\n{'=' * 80}")
    print("MEI v2 ANALYSIS PIPELINE COMPLETE")
    print(f"{'=' * 80}")
    print("\nOutputs:")
    print("  results/mei_lag/")
    print("  results/mei_frequency/")
    print("  results/mei_statistics/")
    print("  results/mei_annual/")
    print("  results/mei_seasonal/")
    print("  results/mei_strength/")

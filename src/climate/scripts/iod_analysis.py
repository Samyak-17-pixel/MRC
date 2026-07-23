#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PYTHON = sys.executable

STAGES = [
    ("iod_lag_analysis.py", "Event tagging and lag correlation"),
    ("iod_frequency_analysis.py", "IOD phase frequency analysis"),
    ("iod_statistics.py", "Duration and intensity statistics"),
    ("iod_annual_analysis.py", "Annual variability analysis"),
    ("iod_seasonal_analysis.py", "Seasonal dependence analysis"),
    ("iod_strength_analysis.py", "IOD strength classification"),
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
    print("IOD ANALYSIS PIPELINE")
    print("Bay of Bengal Marine Heatwave Project")
    print("=" * 80)

    for i, (script, desc) in enumerate(STAGES, 1):
        print(f"\n[{i}/{len(STAGES)}] {desc}")
        run_stage(script, desc)

    print(f"\n{'=' * 80}")
    print("IOD ANALYSIS PIPELINE COMPLETE")
    print(f"{'=' * 80}")
    print("\nOutputs:")
    print("  outputs/iod/lag/")
    print("  outputs/iod/frequency/")
    print("  outputs/iod/statistics/")
    print("  outputs/iod/annual/")
    print("  outputs/iod/seasonal/")
    print("  outputs/iod/strength/")

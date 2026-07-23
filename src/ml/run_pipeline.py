#!/usr/bin/env python3
"""Run full MHW ML pipeline (steps 01–06) from src/ml/."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parent
LOG = ML_ROOT / "logs" / "pipeline.log"

STEPS = [
    ML_ROOT / "preprocessing" / "01_build_dataset.py",
    ML_ROOT / "training" / "02_train_baselines.py",
    ML_ROOT / "training" / "03_train_models.py",
    ML_ROOT / "evaluation" / "04_evaluate_models.py",
    ML_ROOT / "evaluation" / "05_explain_models.py",
    ML_ROOT / "experiments" / "06_predict_current.py",
]


def main():
    LOG.parent.mkdir(parents=True, exist_ok=True)
    python = sys.executable
    print("=" * 72)
    print("MHW ML PIPELINE (src/ml/)")
    print(f"  Started: {datetime.now()}")
    print("=" * 72)

    with open(LOG, "a") as log:
        log.write(f"\n{'='*72}\nPipeline start: {datetime.now()}\n")

        for step in STEPS:
            print(f"\n>>> Running {step.name}")
            log.write(f"Running {step}\n")
            result = subprocess.run(
                [python, str(step)],
                cwd=str(ML_ROOT),
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            log.write(result.stdout)
            if result.stderr:
                log.write(result.stderr)
            if result.returncode != 0:
                print(f"FAILED: {step.name}")
                print(result.stderr)
                log.write(f"FAILED {step}\n")
                sys.exit(result.returncode)

        log.write(f"Pipeline complete: {datetime.now()}\n")

    print("\n" + "=" * 72)
    print("PIPELINE COMPLETE")
    print(f"  Log: {LOG}")
    print("=" * 72)


if __name__ == "__main__":
    main()

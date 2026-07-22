#!/usr/bin/env python3
"""Compatibility wrapper — forwards to machine_learning/training/02_train_baselines.py."""
import runpy
from pathlib import Path

target = Path(__file__).resolve().parents[2] / "machine_learning" / "training" / "02_train_baselines.py"
runpy.run_path(str(target), run_name="__main__")

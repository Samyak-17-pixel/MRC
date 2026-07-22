#!/usr/bin/env python3
"""Compatibility wrapper — forwards to machine_learning/experiments/06_predict_current.py."""
import runpy
from pathlib import Path

target = Path(__file__).resolve().parents[2] / "machine_learning" / "experiments" / "06_predict_current.py"
runpy.run_path(str(target), run_name="__main__")

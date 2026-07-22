#!/usr/bin/env python3
"""Compatibility wrapper — forwards to machine_learning/evaluation/05_explain_models.py."""
import runpy
from pathlib import Path

target = Path(__file__).resolve().parents[2] / "machine_learning" / "evaluation" / "05_explain_models.py"
runpy.run_path(str(target), run_name="__main__")

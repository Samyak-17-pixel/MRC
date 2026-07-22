"""Compatibility shim — re-exports machine_learning.common."""
import sys
from pathlib import Path

_ML = Path(__file__).resolve().parents[2] / "machine_learning"
sys.path.insert(0, str(_ML))
from common import *  # noqa: F401,F403

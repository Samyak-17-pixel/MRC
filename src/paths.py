"""
Central path constants for the Bay of Bengal MHW repository.

All climate and ML code should resolve paths through this module (or REPO_ROOT)
so rearranging folders does not change scientific logic — only locations.
"""
from pathlib import Path

# src/paths.py → repo root is parent of src/
REPO_ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = REPO_ROOT / "data" / "raw"
OUTPUTS = REPO_ROOT / "outputs"
ARCHIVE = REPO_ROOT / "archive"

# Climate package roots
CLIMATE_ROOT = REPO_ROOT / "src" / "climate"
SCRIPTS = CLIMATE_ROOT / "scripts"
PLOTTING = CLIMATE_ROOT / "plotting"

# ML package root
ML_ROOT = REPO_ROOT / "src" / "ml"

# Convenience output subtrees (R3 layout)
TIMESERIES = OUTPUTS / "timeseries"
MHW = OUTPUTS / "mhw"
MHW_CATALOGUE = MHW / "catalogue"
MHW_CLIMATOLOGY = MHW / "climatology"
ENSO = OUTPUTS / "enso"
IOD = OUTPUTS / "iod"
MEI = OUTPUTS / "mei"
CLIMATE_INDICES = OUTPUTS / "climate_indices"
CLIMATE_COMPARISON = OUTPUTS / "climate_comparison"
DRIVERS = OUTPUTS / "drivers"
WIND = DRIVERS / "wind"
HEAT_FLUX = DRIVERS / "heat_flux"
HEAT_FLUX_ANALYSIS = DRIVERS / "heat_flux_analysis"
MASTER_CATALOGUE = OUTPUTS / "master_event_catalogue"
TOP_EVENT_MAPS = OUTPUTS / "top_event_sst_maps"
PUBLICATION = OUTPUTS / "publication"
SPATIAL = OUTPUTS / "spatial_analysis"
MAPS = OUTPUTS / "maps"
YEARLY = OUTPUTS / "yearly"

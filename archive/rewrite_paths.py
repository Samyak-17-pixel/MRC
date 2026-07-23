"""
One-shot path rewriter for repo reorg.
Rewrites only path strings; does not change scientific parameters.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

LITERAL = [

    ("/home/samyak/mrc_ws/outputs/mhw/catalogue", "/home/samyak/mrc_ws/outputs/mhw/catalogue"),
    ("/home/samyak/mrc_ws/outputs/mhw/climatology", "/home/samyak/mrc_ws/outputs/mhw/climatology"),
    ("/home/samyak/mrc_ws/outputs/mhw/annual_statistics", "/home/samyak/mrc_ws/outputs/mhw/annual_statistics"),
    ("/home/samyak/mrc_ws/outputs/mhw/event_reports", "/home/samyak/mrc_ws/outputs/mhw/event_reports"),
    ("/home/samyak/mrc_ws/outputs/mhw/top_events", "/home/samyak/mrc_ws/outputs/mhw/top_events"),
    ("/home/samyak/mrc_ws/outputs/mhw/figures", "/home/samyak/mrc_ws/outputs/mhw/figures"),
    ("/home/samyak/mrc_ws/outputs/mhw/mhw_summary.txt", "/home/samyak/mrc_ws/outputs/mhw/mhw_summary.txt"),
    ("/home/samyak/mrc_ws/outputs/mhw/master_summary.csv", "/home/samyak/mrc_ws/outputs/mhw/master_summary.csv"),
    ("/home/samyak/mrc_ws/outputs/drivers/wind", "/home/samyak/mrc_ws/outputs/drivers/wind"),
    ("/home/samyak/mrc_ws/outputs/drivers/heat_flux_analysis", "/home/samyak/mrc_ws/outputs/drivers/heat_flux_analysis"),
    ("/home/samyak/mrc_ws/outputs/drivers/heat_flux", "/home/samyak/mrc_ws/outputs/drivers/heat_flux"),
    ("/home/samyak/mrc_ws/outputs/master_event_catalogue", "/home/samyak/mrc_ws/outputs/master_event_catalogue"),
    ("/home/samyak/mrc_ws/outputs/top_event_sst_maps", "/home/samyak/mrc_ws/outputs/top_event_sst_maps"),
    ("/home/samyak/mrc_ws/outputs/climate_comparison", "/home/samyak/mrc_ws/outputs/climate_comparison"),
    ("/home/samyak/mrc_ws/outputs/climate_indices", "/home/samyak/mrc_ws/outputs/climate_indices"),
    ("/home/samyak/mrc_ws/outputs/spatial_analysis", "/home/samyak/mrc_ws/outputs/spatial_analysis"),
    ("/home/samyak/mrc_ws/outputs/publication", "/home/samyak/mrc_ws/outputs/publication"),
    ("/home/samyak/mrc_ws/outputs/maps", "/home/samyak/mrc_ws/outputs/maps"),
]

for driver in ("enso", "iod", "mei"):
    for stage in ("lag", "frequency", "statistics", "annual", "seasonal", "strength", "analysis"):
        LITERAL.append(
            (
                f"/home/samyak/mrc_ws/outputs/{driver}_{stage}",
                f"/home/samyak/mrc_ws/outputs/{driver}/{stage}",
            )
        )

for name in (
    "north_bob_sst.csv",
    "central_bob_sst.csv",
    "south_bob_sst.csv",
    "north_bob_sst_detrended.csv",
    "central_bob_sst_detrended.csv",
    "south_bob_sst_detrended.csv",
    "north_wind.csv",
    "central_wind.csv",
    "south_wind.csv",
    "combined_sst_2006_2025.nc",
    "combined_sst_2016_2025.nc",
):
    LITERAL.append(
        (
            f"/home/samyak/mrc_ws/outputs/{name}",
            f"/home/samyak/mrc_ws/outputs/timeseries/{name}",
        )
    )

for y in range(2016, 2027):
    LITERAL.append(
        (f"/home/samyak/mrc_ws/outputs/{y}", f"/home/samyak/mrc_ws/outputs/yearly/{y}")
    )

LITERAL.extend(
    [
        ("/home/samyak/mrc_ws/data/raw", "/home/samyak/mrc_ws/data/raw"),
        ("/home/samyak/mrc_ws/src/ml", "/home/samyak/mrc_ws/src/ml"),
        ("/home/samyak/mrc_ws/src/ml", "/home/samyak/mrc_ws/src/ml"),
        ("/home/samyak/mrc_ws/outputs", "/home/samyak/mrc_ws/outputs"),
    ]
)

RELATIVE = [
    ("outputs/mhw/catalogue", "outputs/mhw/catalogue"),
    ("outputs/mhw/climatology", "outputs/mhw/climatology"),
    ("outputs/mhw/annual_statistics", "outputs/mhw/annual_statistics"),
    ("outputs/mhw/event_reports", "outputs/mhw/event_reports"),
    ("outputs/mhw/top_events", "outputs/mhw/top_events"),
    ("outputs/mhw/figures", "outputs/mhw/figures"),
    ("outputs/drivers/wind", "outputs/drivers/wind"),
    ("outputs/drivers/heat_flux_analysis", "outputs/drivers/heat_flux_analysis"),
    ("outputs/drivers/heat_flux", "outputs/drivers/heat_flux"),
    ("outputs/master_event_catalogue", "outputs/master_event_catalogue"),
    ("outputs/top_event_sst_maps", "outputs/top_event_sst_maps"),
    ("outputs/climate_comparison", "outputs/climate_comparison"),
    ("outputs/climate_indices", "outputs/climate_indices"),
    ("outputs/spatial_analysis", "outputs/spatial_analysis"),
    ("outputs/publication", "outputs/publication"),
    ("outputs/maps", "outputs/maps"),
]
for driver in ("enso", "iod", "mei"):
    for stage in ("lag", "frequency", "statistics", "annual", "seasonal", "strength", "analysis"):
        RELATIVE.append((f"outputs/{driver}_{stage}", f"outputs/{driver}/{stage}"))

RELATIVE.extend(
    [
        ("data/raw/", "data/raw/"),
        ("src/ml/", "src/ml/"),
        ("src/ml/", "src/ml/"),
        ("src/climate/scripts/", "src/climate/src/climate/scripts/"),
        ("src/climate/plotting/", "src/climate/src/climate/plotting/"),

        ("outputs/", "outputs/"),
    ]
)

def rewrite_text(text: str) -> str:
    for old, new in LITERAL:
        text = text.replace(old, new)
    for old, new in RELATIVE:
        text = text.replace(old, new)
    return text

def main():
    roots = [
        REPO / "src",
        REPO / "archive",
        REPO / "outputs",
        REPO / "data",
        REPO / "README.md",
        REPO / ".gitignore",
    ]
    files: list[Path] = []
    for r in roots:
        if r.is_file():
            files.append(r)
        elif r.is_dir():
            for p in r.rglob("*"):
                if p.is_file() and p.suffix in {".py", ".md", ".yaml", ".yml", ".txt", ".csv"}:
                    if "__pycache__" in p.parts or ".venv" in p.parts:
                        continue
                    files.append(p)

    changed = 0
    for path in files:
        try:
            original = path.read_text(encoding="utf-8")
        except Exception:
            continue
        updated = rewrite_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print("updated", path.relative_to(REPO))
    print(f"Done. Files changed: {changed}")

if __name__ == "__main__":
    main()

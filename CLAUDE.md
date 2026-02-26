# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool that generates printable map posters for any city using OpenStreetMap data. It fetches road networks and geographic features, then renders them as styled PNG/SVG posters using matplotlib.

## Commands

```bash
# Install dependencies (use a venv)
python -m venv venv
source venv/Scripts/activate   # Windows
pip install -r requirements.txt

# Generate a poster
python create_map_poster.py --city "Tokyo" --country "Japan" --theme midnight_blue --distance 15000

# List available themes
ls themes/

# Short flags
python create_map_poster.py -c "Paris" -C "France" -t noir -d 10000 -f png
```

Output is saved to `posters/{city}_{theme}_{YYYYMMDD_HHMMSS}.{ext}`.

## Architecture

Single-script pipeline in `create_map_poster.py`:

1. **CLI** (`argparse`) — parses `--city`, `--country`, `--theme`, `--distance`, `--format`
2. **Theme loading** (`load_theme()`) — reads `themes/{name}.json` into global `THEME` dict
3. **Data fetching** (`create_poster()`) — uses `osmnx` to download road graph and water/land polygon features from OpenStreetMap; adds 2000m buffer to `dist` for edge padding
4. **Styling** (`get_styling()`) — maps OSM `highway` tags to colors/widths from `THEME`
5. **Rendering** — matplotlib `fig/ax`; layers drawn in z-order: landmass (z=0) → water (z=1) → roads (via `ox.plot_graph`)
6. **Export** — saves PNG (300 dpi) or SVG via `plt.savefig()`

> **Note:** Coordinates are currently hardcoded in `__main__` (`coords = (3.163..., 101.701...)`) rather than geocoded from `--city/--country`. This is a known deviation from the README description which mentions a `get_coordinates()` function.

## Key Implementation Details

### OSMnx caching
`ox.settings.use_cache = True` is set globally — downloaded map data is cached in `cache/` (gitignored). Set to `False` to force a fresh OSM download.

### Road hierarchy → styling
`get_styling()` maps highway tags to 3 tiers:
- `motorway` → `road_motorway`, width 1.2
- `trunk`/`primary` → `road_primary`, width 1.0
- everything else → `road_residential`, width 0.3

### Theme JSON schema
Required keys: `bg`, `water`, `road_motorway`, `road_primary`, `road_secondary`, `road_tertiary`, `road_residential`, `road_default`
Optional: `text`, `gradient_color`, `parks`, `shoreline`

Themes live in `themes/` — 17 provided. Add new themes as JSON files; `load_theme()` falls back to a hardcoded dark theme if the file is missing.

### Coordinate system
The map crops to a square bounding box centered on `point` (lat, lon), sized by `dist` in meters. Longitude extent is corrected for latitude via `cos(lat)` to produce a visually square crop.

### `dual-export old.py`
An older version of the script (not the current entrypoint). Contains additional features like text labels, gradient fades, parks rendering, and Nominatim geocoding — useful as a reference when re-adding those features.

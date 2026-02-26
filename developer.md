# Developer Reference — City Map Poster Generator

This document covers the internal architecture, key functions, extension patterns, and known issues for contributors and developers.

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CLI Parser    │────▶│  Theme Loading   │────▶│  Data Fetching  │
│   (argparse)    │     │  (load_theme)    │     │    (OSMnx)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                        ┌──────────────────┐            ▼
                        │     Export       │◀───┌─────────────────┐
                        │  (plt.savefig)   │    │    Rendering    │
                        └──────────────────┘    │  (matplotlib)  │
                                                └─────────────────┘
```

The entire pipeline lives in a **single script**: `create_map_poster.py` (146 lines).

---

## File Map

| File                    | Purpose                                                     |
|-------------------------|-------------------------------------------------------------|
| `create_map_poster.py`  | Main entry point — full rendering pipeline                  |
| `dual-export old.py`    | Legacy script (537 lines) — reference for removed features  |
| `themes/*.json`         | 17 theme color definitions                                  |
| `fonts/`                | Roboto font files (Regular, Bold, Light) — for future use   |
| `requirements.txt`      | Python package dependencies                                 |
| `cache/`                | OSMnx tile cache (auto-managed, gitignored)                 |
| `posters/`              | Generated output directory (auto-created)                   |

---

## Pipeline Walkthrough

### Step 1 — CLI Parsing (`__main__`, lines 125–143)

`argparse` parses five arguments: `--city`, `--country`, `--theme`, `--distance`, `--format`.

**Current limitation:** The `--city` and `--country` values are only used in the output filename and log messages. The actual map center coordinates are **hardcoded** at line 139:

```python
coords = (3.163133987081943, 101.70137117066908)  # Marang/KL Terengganu area
```

This must be updated manually to generate a map of a different location. See [Restoring Geocoding](#restoring-geocoding) for how to automate this.

### Step 2 — Theme Loading (`load_theme()`, lines 32–39)

Reads `themes/{name}.json` into a global `THEME` dict. If the file is missing, falls back to a hardcoded dark theme:

```python
{"bg": "#0b1622", "road_motorway": "#E5B94F", "road_primary": "#E5B94F",
 "road_secondary": "#555555", "road_tertiary": "#444444",
 "road_residential": "#333333", "road_default": "#222222", "water": "#1a2a3a"}
```

`THEME` is a global variable accessed throughout rendering. It's assigned once before `create_poster()` is called.

### Step 3 — Data Fetching (`create_poster()`, lines 58–92)

Downloads two data types from OpenStreetMap via `osmnx`:

**Road network:**
```python
G = ox.graph_from_point(point, dist=download_dist, dist_type='bbox',
                        network_type='all', simplify=False,
                        retain_all=True, truncate_by_edge=True)
G = ox.simplify_graph(G)
```
`download_dist = dist + 2000` — adds a 2,000m buffer to avoid clipped roads at the crop boundary.

**Geographic features:**
```python
inland_water = ox.features_from_point(point, tags=water_tags, dist=download_dist)
landmass     = ox.features_from_point(point, tags=land_tags,  dist=download_dist)
```
Both are filtered to `Polygon` and `MultiPolygon` geometry types. Errors are caught silently (either dataset may be empty in some regions).

### Step 4 — Styling (`get_styling()`, lines 41–56)

Iterates all graph edges and maps the OSM `highway` tag to a color and line width:

| OSM Tag(s)                     | Color key           | Width |
|--------------------------------|---------------------|-------|
| `motorway`, `motorway_link`    | `road_motorway`     | 1.2   |
| `trunk`, `primary`             | `road_primary`      | 1.0   |
| `secondary`                    | `road_secondary`    | 0.6   |
| everything else                | `road_residential`  | 0.3   |

Returns two parallel lists: `edge_colors`, `edge_widths`.

### Step 5 — Rendering (lines 94–120)

**Canvas setup:**
```python
fig, ax = plt.subplots(figsize=(12, 16), facecolor=THEME.get('water'))
ax.set_facecolor(THEME.get('water'))  # ocean/sea fill color
```

**Crop calculation** corrects longitude extent for latitude distortion:
```python
coslat = np.cos(np.deg2rad(point[0]))
dist_degree = dist / 111320.0
ax.set_ylim(point[0] - dist_degree, point[0] + dist_degree)
ax.set_xlim(point[1] - (dist_degree / coslat), point[1] + (dist_degree / coslat))
```

**Rendering layers (z-order):**

| z-order | Content       | How rendered                                   |
|---------|---------------|------------------------------------------------|
| `z=0`   | Landmass      | `landmass.plot(facecolor=THEME['bg'])`         |
| `z=1`   | Inland water  | `inland_water.plot(facecolor=THEME['water'])`  |
| auto    | Roads         | `ox.plot_graph(G, edge_color=colors, ...)`     |

Water areas sit on top of land (z=1 > z=0). The figure and axes background color is `THEME['water']`, so any area without a landmass polygon renders as the sea/ocean color.

### Step 6 — Export (lines 117–120)

```python
plt.savefig(output_file, format=ext, dpi=300, bbox_inches='tight',
            pad_inches=0, facecolor=THEME.get('water'), edgecolor='none')
```

Output filename format: `posters/{city}_{theme}_{YYYYMMDD_HHMMSS}.{ext}`

---

## Key Functions Reference

| Function                    | Lines  | Purpose                                              |
|-----------------------------|--------|------------------------------------------------------|
| `log(message)`              | 14–17  | Print elapsed time + message to stdout               |
| `generate_output_filename()` | 26–30 | Build output path, create `posters/` if needed      |
| `load_theme(theme_name)`    | 32–39  | Load theme JSON; fallback to hardcoded dark theme    |
| `get_styling(G)`            | 41–56  | Map OSM highway tags → (colors list, widths list)    |
| `create_poster(...)`        | 58–123 | Full pipeline: fetch → style → render → export       |

---

## Theme JSON Schema

### Required keys (used by `get_styling()` and rendering)

| Key               | Type   | Description                              |
|-------------------|--------|------------------------------------------|
| `bg`              | hex    | Landmass / land background color         |
| `water`           | hex    | Sea, ocean, rivers, and canvas fill      |
| `road_motorway`   | hex    | Motorway and motorway_link roads         |
| `road_primary`    | hex    | Trunk and primary roads                  |
| `road_secondary`  | hex    | Secondary roads                          |
| `road_tertiary`   | hex    | Tertiary roads (not currently used)      |
| `road_residential`| hex    | All other road types                     |
| `road_default`    | hex    | Fallback if highway tag is unrecognized  |

### Optional keys (for legacy/future features)

| Key              | Description                                       |
|------------------|---------------------------------------------------|
| `text`           | City/country label text color                     |
| `gradient_color` | Gradient overlay color (fade effect)              |
| `parks`          | Parks and green areas fill color                  |

`load_theme()` does not validate schema — missing required keys will raise a `KeyError` at render time.

---

## Known Issues / Current State

### 1. Hardcoded coordinates

`--city` and `--country` do **not** control the map location. Coordinates are hardcoded at line 139:

```python
coords = (3.163133987081943, 101.70137117066908)
```

To map a different city: update this line manually.

### 2. Legacy features not active

`dual-export old.py` (537 lines) contains features that were removed from the current script:

- Text label rendering (city name, country, coordinates)
- Top/bottom gradient fade overlay
- Parks rendering (`amenity: park`)
- Nominatim geocoding (`get_coordinates()`)
- Dual PNG + SVG export in one run

These can be re-integrated by referencing the old script.

### 3. `road_tertiary` not used

`get_styling()` maps only 4 tiers (motorway, primary, secondary, other). The `road_tertiary` key exists in theme JSONs but is not referenced in the current code.

---

## How to Extend

### Add a new map layer (e.g., railways)

In `create_poster()`, after the water/landmass fetch block:

```python
try:
    railways = ox.features_from_point(point, tags={'railway': 'rail'}, dist=download_dist)
    if railways is not None:
        railways = railways[railways.geom_type.isin(['LineString', 'MultiLineString'])]
except:
    railways = None
```

Then render before roads (to keep roads on top):

```python
if railways is not None and not railways.empty:
    railways.plot(ax=ax, color=THEME.get('railway', '#555555'), linewidth=0.4, zorder=1.5)
```

Add `"railway": "#555555"` to your theme JSON and as a fallback in `load_theme()`.

### Add a new theme property

1. Add the key to your theme JSON: `"my_color": "#FF0000"`
2. Use it in code: `THEME.get('my_color', '#fallback')`
3. Add a safe default to the fallback dict inside `load_theme()` so old themes don't break

### Restoring geocoding

`dual-export old.py` contains a `get_coordinates()` function using Nominatim:

```python
from geopy.geocoders import Nominatim

def get_coordinates(city, country):
    geolocator = Nominatim(user_agent="map_poster")
    location = geolocator.geocode(f"{city}, {country}")
    return (location.latitude, location.longitude)
```

Replace line 139 of `create_map_poster.py`:

```python
# Before:
coords = (3.163133987081943, 101.70137117066908)

# After:
coords = get_coordinates(args.city, args.country)
```

Note: Nominatim has a rate limit of 1 request/second. Use the cache (`ox.settings.use_cache = True`) to avoid re-geocoding on re-runs.

### Restoring text labels

From `dual-export old.py`, text labels use `ax.transAxes` (0–1 normalized coordinates):

```
y=0.14  City name (letter-spaced)
y=0.125 Decorative line
y=0.10  Country name
y=0.07  Coordinates
y=0.02  Attribution (bottom-right)
```

---

## Useful OSMnx Patterns

```python
# Get buildings
buildings = ox.features_from_point(point, tags={'building': True}, dist=dist)

# Get parks
parks = ox.features_from_point(point, tags={'leisure': 'park'}, dist=dist)

# Get rivers/waterways
rivers = ox.features_from_point(point, tags={'waterway': ['river', 'canal']}, dist=dist)

# Get specific amenities
stations = ox.features_from_point(point, tags={'railway': 'station'}, dist=dist)

# Different road network types
G = ox.graph_from_point(point, dist=dist, network_type='drive')  # roads only (faster)
G = ox.graph_from_point(point, dist=dist, network_type='bike')   # cycling network
G = ox.graph_from_point(point, dist=dist, network_type='walk')   # pedestrian paths
G = ox.graph_from_point(point, dist=dist, network_type='all')    # everything (default)
```

---

## Performance Tips

| Tip                                     | Impact                                       |
|-----------------------------------------|----------------------------------------------|
| Keep `use_cache = True`                 | Avoids re-downloading OSM data on re-runs    |
| Use `network_type='drive'` not `'all'`  | 2–3x fewer edges, faster render              |
| Lower `dpi` to 150 for previews         | 4x fewer pixels, much faster export          |
| Keep `dist` under 20,000m              | Data size grows quadratically with distance  |
| Run on SSD                              | Cache read/write is I/O bound for large areas|

---

## Dependencies

| Package      | Version | Used for                                              |
|--------------|---------|-------------------------------------------------------|
| `osmnx`      | 2.0.7   | Downloading road graphs and geographic features       |
| `matplotlib` | 3.10.8  | Rendering all layers and exporting PNG/SVG            |
| `geopandas`  | 1.1.2   | Plotting Polygon/MultiPolygon features (water, land)  |
| `shapely`    | 2.1.2   | Geometry filtering and spatial operations             |
| `geopy`      | 2.4.1   | Geocoding (in `requirements.txt`, not in main script) |
| `pandas`     | 2.3.3   | Internal data handling by geopandas                   |
| `numpy`      | 2.4.0   | Coordinate math (`cos(lat)` correction for crop box)  |
| `pillow`     | 12.1.0  | Required by matplotlib for PNG export                 |
| `networkx`   | 3.6.1   | Underlying graph structure used by osmnx              |
| `tqdm`       | —       | Progress bars in the data fetch step                  |

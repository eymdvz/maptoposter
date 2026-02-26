# City Map Poster Generator

Generate beautiful, minimalist map posters for any city in the world using OpenStreetMap data.

<img src="posters/singapore_neon_cyberpunk_20260108_184503.png" width="250"> <img src="posters/dubai_midnight_blue_20260108_174920.png" width="250">

---

## Examples

| Country   | City          | Theme          | Poster |
|:---------:|:-------------:|:--------------:|:------:|
| USA       | San Francisco | sunset         | <img src="posters/san_francisco_sunset_20260108_184122.png" width="200"> |
| Spain     | Barcelona     | warm_beige     | <img src="posters/barcelona_warm_beige_20260108_172924.png" width="200"> |
| Italy     | Venice        | blueprint      | <img src="posters/venice_blueprint_20260108_165527.png" width="200"> |
| Japan     | Tokyo         | japanese_ink   | <img src="posters/tokyo_japanese_ink_20260108_165830.png" width="200"> |
| India     | Mumbai        | contrast_zones | <img src="posters/mumbai_contrast_zones_20260108_170325.png" width="200"> |
| Morocco   | Marrakech     | terracotta     | <img src="posters/marrakech_terracotta_20260108_180821.png" width="200"> |
| Singapore | Singapore     | neon_cyberpunk | <img src="posters/singapore_neon_cyberpunk_20260108_184503.png" width="200"> |
| Australia | Melbourne     | forest         | <img src="posters/melbourne_forest_20260108_181459.png" width="200"> |
| UAE       | Dubai         | midnight_blue  | <img src="posters/dubai_midnight_blue_20260108_174920.png" width="200"> |

---

## Installation

**1. Clone the repo and enter the project folder:**
```bash
git clone <repo-url>
cd maptoposter
```

**2. Create a virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## Quick Start

> **Important:** Before running, set your target city's coordinates in `create_map_poster.py` at line 139.
> See [Setting Coordinates](#setting-coordinates) below.

```bash
python create_map_poster.py --city "Tokyo" --country "Japan" --theme midnight_blue --distance 15000
```

If `-f` is not provided, you will be prompted to choose:
```
Output format — enter 'png' or 'svg' [svg]:
```
Press Enter to use SVG, or type `png` to use PNG.

---

## Usage

```bash
python create_map_poster.py --city <city> --country <country> [options]
```

### Options

| Option       | Short | Type    | Default        | Description                          |
|--------------|-------|---------|----------------|--------------------------------------|
| `--city`     | `-c`  | string  | **required**   | City name (used in output filename)  |
| `--country`  | `-C`  | string  | **required**   | Country name (used in log output)    |
| `--theme`    | `-t`  | string  | `feature_based`| Theme name (must match a file in `themes/`) |
| `--distance` | `-d`  | int     | `5000`         | Map radius in meters from center point |
| `--format`   | `-f`  | string  | prompted       | Output format: `png` or `svg`. If omitted, you will be asked interactively |

### Examples

```bash
# Iconic grid patterns
python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000
python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000

# Waterfront & canals
python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000
python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000
python create_map_poster.py -c "Dubai" -C "UAE" -t midnight_blue -d 15000

# Radial patterns
python create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000
python create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000

# Organic old cities
python create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000
python create_map_poster.py -c "Marrakech" -C "Morocco" -t terracotta -d 5000
python create_map_poster.py -c "Rome" -C "Italy" -t warm_beige -d 8000

# Coastal cities
python create_map_poster.py -c "San Francisco" -C "USA" -t sunset -d 10000
python create_map_poster.py -c "Sydney" -C "Australia" -t ocean -d 12000

# River cities
python create_map_poster.py -c "London" -C "UK" -t noir -d 15000
python create_map_poster.py -c "Budapest" -C "Hungary" -t copper_patina -d 8000
```

---

## Setting Coordinates

The map center is set by editing **line 139** in `create_map_poster.py`:

```python
# create_map_poster.py, line 139
coords = (3.163133987081943, 101.70137117066908)  # <- change this
```

Replace with your city's coordinates as `(latitude, longitude)`. You can get coordinates from Google Maps (right-click on any location) or [latlong.net](https://www.latlong.net/).

```python
# Examples
coords = (35.6762, 139.6503)   # Tokyo
coords = (48.8566, 2.3522)     # Paris
coords = (51.5074, -0.1278)    # London
coords = (40.7128, -74.0060)   # New York
coords = (1.3521, 103.8198)    # Singapore
```

> **Note:** `--city` and `--country` flags are used for the output filename and log messages only.
> The actual map location is controlled by the `coords` variable.

---

## Distance Guide

| Distance       | Best for                                           |
|----------------|----------------------------------------------------|
| 4,000–6,000m   | Small/dense cities (Venice, Amsterdam center)      |
| 8,000–12,000m  | Medium cities, focused downtown (Paris, Barcelona) |
| 15,000–20,000m | Large metros, full city view (Tokyo, Mumbai)       |

---

## Themes

17 built-in themes available in the `themes/` directory:

| Theme             | Style                                                                |
|-------------------|----------------------------------------------------------------------|
| `feature_based`   | Different shades for different road types — clear road hierarchy     |
| `gradient_roads`  | Smooth gradient from dark center to light edges                      |
| `contrast_zones`  | Strong contrast showing urban density                                |
| `noir`            | Pure black background with white/gray roads — gallery aesthetic      |
| `midnight_blue`   | Deep navy with gold/copper roads — luxury atlas aesthetic            |
| `blueprint`       | Classic architectural blueprint — technical drawing aesthetic        |
| `neon_cyberpunk`  | Dark background with electric pink/cyan — bold night city vibes      |
| `warm_beige`      | Earthy warm neutrals with sepia tones — vintage map aesthetic        |
| `pastel_dream`    | Soft muted pastels with dusty blues and mauves                       |
| `japanese_ink`    | Traditional ink wash inspired — minimalist with subtle red accent    |
| `forest`          | Deep greens and sage tones — organic botanical aesthetic             |
| `ocean`           | Various blues and teals — perfect for coastal cities                 |
| `terracotta`      | Mediterranean warmth — burnt orange and clay tones on cream          |
| `sunset`          | Warm oranges and pinks on soft peach — golden hour aesthetic         |
| `autumn`          | Burnt oranges, deep reds, golden yellows — seasonal warmth           |
| `copper_patina`   | Oxidized copper aesthetic — teal-green patina with copper accents    |
| `monochrome_blue` | Single blue color family with varying saturation — clean and cohesive|

---

## Output

Posters are saved in the `posters/` directory with this naming format:

```
{city}_{theme}_{YYYYMMDD_HHMMSS}.{ext}
```

Example: `tokyo_midnight_blue_20260115_143022.png`

The `posters/` directory is created automatically if it doesn't exist.

---

## What You Can Modify

### 1. Map Center Coordinates
**File:** `create_map_poster.py`, line 139

```python
coords = (3.163133987081943, 101.70137117066908)
```
Change `(latitude, longitude)` to any location you want to map.

### 2. Output Resolution (DPI)
**File:** `create_map_poster.py`, line 118

```python
plt.savefig(output_file, format=ext, dpi=300, ...)
```
- `300` — print quality (default)
- `150` — faster preview generation
- `72`  — screen/web display

### 3. OSMnx Data Cache
**File:** `create_map_poster.py`, line 20

```python
ox.settings.use_cache = True  # Set to False to force fresh download
```
Cache is stored in `cache/` and is ignored by git. Disable when OSM data has changed.

### 4. Output Directory
**File:** `create_map_poster.py`, line 24

```python
POSTERS_DIR = "posters"
```
Change to any relative or absolute path.

### 5. Road Line Widths
**File:** `create_map_poster.py`, lines 49–55 (inside `get_styling()`)

```python
if 'motorway' in h_str:
    edge_widths.append(1.2)   # <- adjust this
elif 'trunk' in h_str or 'primary' in h_str:
    edge_widths.append(1.0)   # <- adjust this
elif 'secondary' in h_str:
    edge_widths.append(0.6)   # <- adjust this
else:
    edge_widths.append(0.3)   # <- adjust this (all other roads)
```

### 6. Canvas Size
**File:** `create_map_poster.py`, line 96

```python
fig, ax = plt.subplots(figsize=(12, 16), ...)
```
`(width, height)` in inches. Change to `(12, 12)` for square, `(16, 12)` for landscape.

---

## Adding Custom Themes

Create a new `.json` file in the `themes/` directory. All required keys must be present:

```json
{
  "name": "My Theme",
  "description": "Short description of the style",
  "bg": "#FFFFFF",
  "water": "#C0C0C0",
  "road_motorway": "#0A0A0A",
  "road_primary": "#1A1A1A",
  "road_secondary": "#2A2A2A",
  "road_tertiary": "#3A3A3A",
  "road_residential": "#4A4A4A",
  "road_default": "#3A3A3A"
}
```

**Optional keys** (used by legacy rendering features):

```json
{
  "text": "#000000",
  "gradient_color": "#FFFFFF",
  "parks": "#F0F0F0"
}
```

Then use it with `--theme my_theme` (filename without `.json`).

---

## Project Structure

```
maptoposter/
├── create_map_poster.py     # Main script — entry point
├── dual-export old.py       # Legacy version with extra features (reference only)
├── requirements.txt         # Python dependencies
├── themes/                  # 17 built-in theme JSON files
│   ├── noir.json
│   ├── midnight_blue.json
│   └── ...
├── fonts/                   # Roboto font files (Regular, Bold, Light)
├── posters/                 # Generated poster output (auto-created)
│   └── example/             # Sample outputs for reference
├── cache/                   # OSMnx downloaded data (gitignored)
├── CLAUDE.md                # Claude Code workspace guidance
└── README.md                # This file
```

---

## Dependencies

| Package      | Version | Purpose                        |
|--------------|---------|--------------------------------|
| `osmnx`      | 2.0.7   | OpenStreetMap data fetching    |
| `matplotlib` | 3.10.8  | Map rendering and export       |
| `geopandas`  | 1.1.2   | Geospatial polygon handling    |
| `shapely`    | 2.1.2   | Geometric operations           |
| `geopy`      | 2.4.1   | Geocoding (for future use)     |
| `pandas`     | 2.3.3   | Data processing                |
| `numpy`      | 2.4.0   | Coordinate math                |
| `pillow`     | 12.1.0  | Image processing               |
| `networkx`   | 3.6.1   | Road graph analysis            |
| `tqdm`       | —       | Progress bars during download  |

---

## License

MIT License — Copyright 2026, Ankur Gupta

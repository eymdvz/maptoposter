import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np
import json
import os
import time
from datetime import datetime
import argparse
from tqdm import tqdm

# --- STARTUP TIMER ---
START_TIME = time.perf_counter()

def log(message):
    """Helper to print timestamps and status."""
    elapsed = time.perf_counter() - START_TIME
    print(f"[{elapsed:6.2f}s] {message}")

# --- CONFIG ---
ox.settings.use_cache = True  # FAST MODE: Set to False only for a complete data refresh
ox.settings.log_console = False

THEMES_DIR = "themes"
POSTERS_DIR = "posters"

def generate_output_filename(city, theme_name, ext):
    if not os.path.exists(POSTERS_DIR): os.makedirs(POSTERS_DIR)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = city.lower().replace(' ', '_')
    return os.path.join(POSTERS_DIR, f"{city_slug}_{theme_name}_{ts}.{ext}")

def load_theme(theme_name="feature_based"):
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")
    if not os.path.exists(theme_file):
        log(f"⚠ Theme {theme_name} not found, using default dark theme.")
        return {"bg": "#0b1622", "road_motorway": "#E5B94F", "road_primary": "#E5B94F", 
                "road_secondary": "#555555", "road_tertiary": "#444444", "road_residential": "#333333", 
                "road_default": "#222222", "water": "#1a2a3a"}
    with open(theme_file, 'r') as f: return json.load(f)

def get_styling(G):
    edge_colors = []
    edge_widths = []
    for u, v, data in G.edges(data=True):
        h = data.get('highway', 'unclassified')
        h_str = " ".join(str(x) for x in h).lower() if isinstance(h, list) else str(h).lower()
        
        if 'motorway' in h_str:
            edge_colors.append(THEME.get('road_motorway', '#E5B94F')); edge_widths.append(1.2)
        elif 'trunk' in h_str or 'primary' in h_str:
            edge_colors.append(THEME.get('road_primary', '#E5B94F')); edge_widths.append(1.0)
        elif 'secondary' in h_str:
            edge_colors.append(THEME.get('road_secondary', '#888888')); edge_widths.append(0.6)
        else:
            edge_colors.append(THEME.get('road_residential', '#333333')); edge_widths.append(0.3)
    return edge_colors, edge_widths

def create_poster(city, country, point, dist, output_file, ext):
    log(f"🚀 Starting poster generation for {city}, {country}...")
    download_dist = dist + 2000 
    
    # 1. DOWNLOAD ROADS
    log("📡 Requesting road network from OpenStreetMap...")
    G = ox.graph_from_point(point, dist=download_dist, dist_type='bbox', network_type='all', 
                            simplify=False, retain_all=True, truncate_by_edge=True)
    log(f"📊 Downloaded {len(G.edges())} road segments.")
    
    log("🔧 Simplifying road geometry for clean lines...")
    G = ox.simplify_graph(G)
    log("✓ Road network processing complete.")
    
    # 2. DOWNLOAD FEATURES
    log("🌊 Fetching geography features (Land and Water)...")
    water_tags = {'natural': ['water', 'bay', 'strait'], 'waterway': 'riverbank'}
    land_tags = {'boundary': 'administrative', 'admin_level': ['4', '6', '8']}
    
    # Granular feature fetching with mini-bars
    with tqdm(total=2, desc="Extracting Geometry", leave=False) as pbar:
        try:
            inland_water = ox.features_from_point(point, tags=water_tags, dist=download_dist)
            if inland_water is not None:
                inland_water = inland_water[inland_water.geom_type.isin(['Polygon', 'MultiPolygon'])]
            pbar.update(1)
        except: inland_water = None; pbar.update(1)

        try:
            landmass = ox.features_from_point(point, tags=land_tags, dist=download_dist)
            if landmass is not None:
                landmass = landmass[landmass.geom_type.isin(['Polygon', 'MultiPolygon'])]
            pbar.update(1)
        except: landmass = None; pbar.update(1)
    log("✓ Geography features processed.")

    # 3. RENDERING
    log("🎨 Initializing map canvas and calculating crop...")
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=THEME.get('water'))
    ax.set_facecolor(THEME.get('water')) # Sea logic
    
    coslat = np.cos(np.deg2rad(point[0]))
    dist_degree = dist / 111320.0
    ax.set_ylim(point[0] - dist_degree, point[0] + dist_degree)
    ax.set_xlim(point[1] - (dist_degree / coslat), point[1] + (dist_degree / coslat))
    ax.axis('off')

    log("🖌️ Drawing layers (Land -> Water -> Roads)...")
    if landmass is not None and not landmass.empty:
        landmass.plot(ax=ax, facecolor=THEME['bg'], edgecolor='none', zorder=0)
    
    if inland_water is not None and not inland_water.empty:
        inland_water.plot(ax=ax, facecolor=THEME.get('water'), edgecolor='none', zorder=1)
    
    colors, widths = get_styling(G)
    ox.plot_graph(G, ax=ax, bgcolor='none', node_size=0, edge_color=colors, edge_linewidth=widths, show=False, close=False)
    log("✓ All layers drawn successfully.")

    # 4. EXPORT
    log(f"💾 Saving high-resolution {ext.upper()} file...")
    plt.savefig(output_file, format=ext, dpi=300, bbox_inches='tight', 
                pad_inches=0, facecolor=THEME.get('water'), edgecolor='none')
    plt.close()
    
    log(f"✨ DONE! Total time elapsed: {time.perf_counter() - START_TIME:.2f} seconds.")
    log(f"📂 File saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimized Map Poster Generator")
    parser.add_argument('--city', '-c', type=str, required=True)
    parser.add_argument('--country', '-C', type=str, required=True)
    parser.add_argument('--theme', '-t', type=str, default='feature_based')
    parser.add_argument('--distance', '-d', type=int, default=5000)
    parser.add_argument('--format', '-f', type=str, choices=['png', 'svg'], default=None)

    args = parser.parse_args()

    if args.format is None:
        fmt = input("Output format — enter 'png' or 'svg' [svg]: ").strip().lower()
        args.format = fmt if fmt in ('png', 'svg') else 'svg'
    
    global THEME
    THEME = load_theme(args.theme)
    
    # Coordinates (Marang/Kuala Terengganu area based on your previous input)
    coords = (3.163133987081943, 101.70137117066908) 
    
    try:
        out = generate_output_filename(args.city, args.theme, args.format)
        create_poster(args.city, args.country, coords, args.distance, out, args.format)
    except Exception as e:
        log(f"✗ CRITICAL ERROR: {e}")
        import traceback; traceback.print_exc()
"""
Solar System View Generator for Hindu Panchanga v4.0 Cosmic Context
Generates a heliocentric (Sun-centered) top-down view of the solar system.

This module visualizes planetary alignments by plotting their positions 
on a normalized ecliptic plane.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import hashlib
import os
from pathlib import Path
from utils.astronomy import eph, sun, ts

planets_map = {
    "Mercury": eph['mercury'],
    "Venus": eph['venus'],
    "Earth": eph['earth'],
    "Mars": eph['mars'],
    "Jupiter": eph['jupiter barycenter'],
    "Saturn": eph['saturn barycenter'],
    "Uranus": eph['uranus barycenter'],
    "Neptune": eph['neptune barycenter']
}

CACHE_DIR = Path("static/solar_systems")

def get_cache_key(date_str: str, time_str: str):
    """Heliocentric view only depends on date/time, not observer location."""
    data = f"solar-{date_str}-{time_str}"
    return hashlib.md5(data.encode()).hexdigest()[:12]

def get_cached_image(cache_key: str):
    image_path = CACHE_DIR / f"{cache_key}.png"
    if image_path.exists():
        return str(image_path)
    return None

def generate_solar_system(utc_dt, output_path, event_title=None):
    """
    Generate a top-down heliocentric view of the solar system.
    """
    # Ensure cache directory exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    t = ts.from_datetime(utc_dt)
    
    positions = {}
    for name, body in planets_map.items():
        # Get position relative to sun
        astrometric = sun.at(t).observe(body)
        from skyfield.framelib import ecliptic_frame
        pos = astrometric.frame_xyz(ecliptic_frame).au
        positions[name] = (pos[0], pos[1]) # X, Y coordinates

    # Vedic/Approximated names map
    vedic_names = {
        "Mercury": "BUDHA (MERCURY)",
        "Venus": "SHUKRA (VENUS)",
        "Earth": "PRITHVI (EARTH)",
        "Mars": "MANGALA (MARS)",
        "Jupiter": "GURU (JUPITER)",
        "Saturn": "SHANI (SATURN)",
        "Uranus": "ARUNA (URANUS)*",
        "Neptune": "VARUNA (NEPTUNE)*"
    }

    # Setup Plot
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    
    fig = Figure(figsize=(18.5, 18.5), facecolor='#0a0a0f')
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111, facecolor='#0a0a0f')
    
    import matplotlib.patches as patches
    for r_glow in [0.2, 0.1]:
        glow = patches.Circle((0, 0), r_glow, color='#ffcc00', alpha=0.3, zorder=9)
        ax.add_patch(glow)
    ax.plot(0, 0, 'o', markersize=24, color='#ffcc00', 
            markeredgecolor='#ffffff', markeredgewidth=1.5, label='Sun', zorder=10)
    ax.text(0, -0.6, 'SUN (SURYA)', color='#ffffff', ha='center', fontsize=16, fontweight='bold')

    colors = {
        "Mercury": "#9b9b9b",
        "Venus": "#f3d299",
        "Earth": "#4a90d9",
        "Mars": "#e94560",
        "Jupiter": "#d39c7e",
        "Saturn": "#c5ab6e",
        "Uranus": "#a2cffe", # Muted blue
        "Neptune": "#3f51b5" # Muted indigo
    }
    
    symbols = {
        "Mercury": "☿", "Venus": "♀", "Earth": "⊕", 
        "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
        "Uranus": "♅", "Neptune": "♆"
    }

    traditional_planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn"]

    # Refined Logarithmic-Style Scaling to handle outer planets without squashing inner
    def scale_pos(x, y):
        dist = np.sqrt(x**2 + y**2)
        if dist == 0: return 0, 0
        # Log-based scaling allows Uranus and Neptune to fit beautifully
        scaled_dist = 4.5 * np.log1p(dist) 
        factor = scaled_dist / dist
        return x * factor, y * factor

    max_r = 0
    for name, (x, y) in positions.items():
        sx, sy = scale_pos(x, y)
        r = np.sqrt(sx**2 + sy**2)
        max_r = max(max_r, r)
        
        is_modern = name not in traditional_planets
        
        # Orbit styling
        orbit_color = '#ffffff' if not is_modern else '#444455'
        orbit_alpha = 0.15 if not is_modern else 0.08
        ls = '-' if not is_modern else '--'
        
        circle = patches.Circle((0, 0), r, color=orbit_color, fill=False, 
                                linestyle=ls, alpha=orbit_alpha, linewidth=1)
        ax.add_patch(circle)
        
        # Planet Symbol
        opacity = 1.0 if not is_modern else 0.6
        ax.text(sx, sy, symbols[name], color=colors[name], ha='center', va='center', 
                fontsize=28, fontweight='bold', zorder=15, alpha=opacity)
        
        # Planet Name
        ha = 'left' if sx >= 0 else 'right'
        offset = 0.5 if sx >= 0 else -0.5
        v_name = vedic_names.get(name, name.upper())
        ax.text(sx + offset, sy, v_name, color=colors[name], 
                ha=ha, va='center', fontsize=14, fontweight='bold', zorder=15, alpha=opacity)

    # Note about Aruna/Varuna
    ax.text(0.98, 0.02, "* Modern astronomical additions (Aruna & Varuna)", 
            transform=ax.transAxes, color='#555555', fontsize=12, ha='right', style='italic')

    # Styling
    padding = 1.1
    ax.set_xlim(-max_r * padding, max_r * padding)
    ax.set_ylim(-max_r * padding, max_r * padding)
    ax.set_aspect('equal')
    ax.axis('off')

    # Background Stars
    np.random.seed(42)
    stars_x = np.random.uniform(-max_r*padding, max_r*padding, 100)
    stars_y = np.random.uniform(-max_r*padding, max_r*padding, 100)
    ax.scatter(stars_x, stars_y, s=1.5, color='#ffffff', alpha=0.15, zorder=1)

    # Save the figure
    fig.savefig(output_path, dpi=130, bbox_inches='tight', facecolor='#0a0a0f', pad_inches=0.2)
    return output_path

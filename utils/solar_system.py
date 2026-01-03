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
from skyfield.api import load
from datetime import datetime
import pytz

# Load ephemeris data (re-using what's already in the project)
eph = load('de421.bsp')
sun = eph['sun']
planets_map = {
    "Mercury": eph['mercury'],
    "Venus": eph['venus'],
    "Earth": eph['earth'],
    "Mars": eph['mars'],
    "Jupiter": eph['jupiter barycenter'],
    "Saturn": eph['saturn barycenter']
}

CACHE_DIR = Path("static/solar_systems")

def get_cache_key(date_str: str, time_str: str) -> str:
    """Heliocentric view only depends on date/time, not observer location."""
    data = f"solar-{date_str}-{time_str}"
    return hashlib.md5(data.encode()).hexdigest()[:12]

def get_cached_image(cache_key: str) -> str | None:
    image_path = CACHE_DIR / f"{cache_key}.png"
    if image_path.exists():
        return str(image_path)
    return None

def generate_solar_system(utc_dt: datetime, output_path: str, event_title: str = None) -> str:
    """
    Generate a top-down heliocentric view of the solar system.
    """
    ts = load.timescale()
    t = ts.from_datetime(utc_dt)
    
    positions = {}
    for name, body in planets_map.items():
        # Get position relative to sun
        astrometric = sun.at(t).observe(body)
        # We want the x, y in the ecliptic plane
        # skyfield's ecliptic_position() returns distance in AU, and angles
        # We can also get cartesian coordinates in the ecliptic frame
        from skyfield.framelib import ecliptic_frame
        pos = astrometric.frame_xyz(ecliptic_frame).au
        positions[name] = (pos[0], pos[1]) # X, Y coordinates

    # Setup Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')
    
    # Sun at center with glow
    for r_glow in [0.2, 0.1]:
        glow = plt.Circle((0, 0), r_glow, color='#ffcc00', alpha=0.3, zorder=9)
        ax.add_patch(glow)
    ax.plot(0, 0, 'o', markersize=24, color='#ffcc00', 
            markeredgecolor='#ffffff', markeredgewidth=1.5, label='Sun', zorder=10)
    ax.text(0, -0.4, 'SUN', color='#ffffff', ha='center', fontsize=11, fontweight='bold')

    # Orbit Radii for visualization
    colors = {
        "Mercury": "#9b9b9b",
        "Venus": "#f3d299",
        "Earth": "#4a90d9",
        "Mars": "#e94560",
        "Jupiter": "#d39c7e",
        "Saturn": "#c5ab6e"
    }
    
    symbols = {
        "Mercury": "☿", "Venus": "♀", "Earth": "⊕", 
        "Mars": "♂", "Jupiter": "♃", "Saturn": "♄"
    }

    # Normalize distances for a better visual (inner vs outer)
    def scale_pos(x, y):
        dist = np.sqrt(x**2 + y**2)
        if dist == 0: return 0, 0
        # Refined scaling for better inner planetary visibility
        scaled_dist = 1.2 * (dist ** 0.55) 
        factor = scaled_dist / dist
        return x * factor, y * factor

    # Draw Orbits and Planets
    max_r = 0
    for name, (x, y) in positions.items():
        sx, sy = scale_pos(x, y)
        r = np.sqrt(sx**2 + sy**2)
        max_r = max(max_r, r)
        
        # Draw Orbit circle - more prominent
        circle = plt.Circle((0, 0), r, color='#444455', fill=False, linestyle='-', alpha=0.2, linewidth=1)
        ax.add_patch(circle)
        
        # Planet with glow
        ax.plot(sx, sy, 'o', markersize=14, color=colors[name], 
                markeredgecolor='#ffffff', markeredgewidth=0.5, zorder=12)
        
        # Add Symbol
        ax.text(sx, sy + 0.25, symbols[name], color='#ffffff', ha='center', va='bottom', fontsize=18, fontweight='bold', zorder=15)
        
        # Add Name label - cleaner
        ax.text(sx, sy - 0.4, name.upper(), color=colors[name], ha='center', va='top', fontsize=9, fontweight='bold', zorder=15)

    # Styling
    padding = 1.2
    ax.set_xlim(-max_r * padding, max_r * padding)
    ax.set_ylim(-max_r * padding, max_r * padding)
    ax.set_aspect('equal')
    ax.axis('off')

    # Grid background (faint stars) - 50 random points
    np.random.seed(42)
    stars_x = np.random.uniform(-max_r*padding, max_r*padding, 50)
    stars_y = np.random.uniform(-max_r*padding, max_r*padding, 50)
    ax.scatter(stars_x, stars_y, s=1, color='#ffffff', alpha=0.2, zorder=1)

    # Titles
    plt.title("PLANETARY ALIGNMENTS AT BIRTH", color='#ffffff', fontsize=20, fontweight='bold', pad=30, fontfamily='sans-serif')
    if event_title:
        plt.suptitle(f'"{event_title}"', color='#ff9100', fontsize=13, y=0.92, fontfamily='sans-serif')
    
    # Save the figure
    plt.savefig(output_path, dpi=130, bbox_inches='tight', facecolor='#0a0a0f', pad_inches=0.5)
    plt.close(fig)
    return output_path

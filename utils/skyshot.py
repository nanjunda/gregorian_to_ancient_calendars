"""
Sky-Shot Generator for Hindu Panchanga v4.0 Cosmic Context
Generates visual 2D ecliptic wheel sky maps showing Nakshatra positions.

This module creates an educational visualization of the Moon's position
among the 27 Nakshatras at a given moment in time.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import numpy as np
import hashlib
import os
from pathlib import Path

# 27 Nakshatras with their sidereal longitude ranges and associated stars
NAKSHATRAS = [
    {"name": "Ashwini", "start": 0, "end": 13.333, "star": "β Arietis", "deity": "Ashwini Kumaras"},
    {"name": "Bharani", "start": 13.333, "end": 26.667, "star": "41 Arietis", "deity": "Yama"},
    {"name": "Krittika", "start": 26.667, "end": 40, "star": "Alcyone (Pleiades)", "deity": "Agni"},
    {"name": "Rohini", "start": 40, "end": 53.333, "star": "Aldebaran", "deity": "Brahma"},
    {"name": "Mrigashira", "start": 53.333, "end": 66.667, "star": "λ Orionis", "deity": "Soma"},
    {"name": "Ardra", "start": 66.667, "end": 80, "star": "Betelgeuse", "deity": "Rudra"},
    {"name": "Punarvasu", "start": 80, "end": 93.333, "star": "Pollux", "deity": "Aditi"},
    {"name": "Pushya", "start": 93.333, "end": 106.667, "star": "δ Cancri", "deity": "Brihaspati"},
    {"name": "Ashlesha", "start": 106.667, "end": 120, "star": "ε Hydrae", "deity": "Nagas"},
    {"name": "Magha", "start": 120, "end": 133.333, "star": "Regulus", "deity": "Pitris"},
    {"name": "Purva Phalguni", "start": 133.333, "end": 146.667, "star": "δ Leonis", "deity": "Bhaga"},
    {"name": "Uttara Phalguni", "start": 146.667, "end": 160, "star": "β Leonis", "deity": "Aryaman"},
    {"name": "Hasta", "start": 160, "end": 173.333, "star": "δ Corvi", "deity": "Savitar"},
    {"name": "Chitra", "start": 173.333, "end": 186.667, "star": "Spica", "deity": "Vishwakarma"},
    {"name": "Swati", "start": 186.667, "end": 200, "star": "Arcturus", "deity": "Vayu"},
    {"name": "Vishakha", "start": 200, "end": 213.333, "star": "α Librae", "deity": "Indra-Agni"},
    {"name": "Anuradha", "start": 213.333, "end": 226.667, "star": "δ Scorpii", "deity": "Mitra"},
    {"name": "Jyeshtha", "start": 226.667, "end": 240, "star": "Antares", "deity": "Indra"},
    {"name": "Mula", "start": 240, "end": 253.333, "star": "λ Scorpii", "deity": "Nirriti"},
    {"name": "Purva Ashadha", "start": 253.333, "end": 266.667, "star": "δ Sagittarii", "deity": "Apas"},
    {"name": "Uttara Ashadha", "start": 266.667, "end": 280, "star": "σ Sagittarii", "deity": "Vishvadevas"},
    {"name": "Shravana", "start": 280, "end": 293.333, "star": "Altair", "deity": "Vishnu"},
    {"name": "Dhanishta", "start": 293.333, "end": 306.667, "star": "β Delphini", "deity": "Vasus"},
    {"name": "Shatabhisha", "start": 306.667, "end": 320, "star": "λ Aquarii", "deity": "Varuna"},
    {"name": "Purva Bhadrapada", "start": 320, "end": 333.333, "star": "α Pegasi", "deity": "Aja Ekapada"},
    {"name": "Uttara Bhadrapada", "start": 333.333, "end": 346.667, "star": "γ Pegasi", "deity": "Ahir Budhnya"},
    {"name": "Revati", "start": 346.667, "end": 360, "star": "ζ Piscium", "deity": "Pushan"},
]

# Alternating color palette for better visibility
NAKSHATRA_COLORS_NORMAL = ['#1a1a2e', '#16213e', '#0f3460'] * 9
NAKSHATRA_COLOR_HIGHLIGHT = '#e94560'  # Ruby red for current Nakshatra

# Cache directory for generated sky maps
CACHE_DIR = Path("static/skyshots")


def get_cache_key(date_str: str, time_str: str, lat: float, lon: float) -> str:
    """
    Generate a unique hash key for caching sky map images.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        time_str: Time in HH:MM format
        lat: Latitude
        lon: Longitude
    
    Returns:
        12-character MD5 hash string
    """
    data = f"{date_str}-{time_str}-{lat:.2f}-{lon:.2f}"
    return hashlib.md5(data.encode()).hexdigest()[:12]


def get_cached_image(cache_key: str):
    """
    Check if a cached sky map image exists.
    
    Args:
        cache_key: The unique cache key
    
    Returns:
        Path to the cached image if it exists, None otherwise
    """
    image_path = CACHE_DIR / f"{cache_key}.png"
    if image_path.exists():
        return str(image_path)
    return None


def get_nakshatra_index(moon_longitude: float) -> int:
    """
    Get the Nakshatra index (0-26) for a given sidereal longitude.
    
    Args:
        moon_longitude: Moon's sidereal longitude (0-360°)
    
    Returns:
        Index of the Nakshatra (0-26)
    """
    return int(moon_longitude / 13.333333) % 27


def get_moon_phase_symbol(phase_angle: float) -> str:
    """
    Get an appropriate moon phase emoji based on the Sun-Moon angular separation.
    
    Args:
        phase_angle: Angular separation between Sun and Moon (0-360°)
    
    Returns:
        Moon phase emoji
    """
    if phase_angle < 22.5 or phase_angle > 337.5:
        return '🌑'  # New Moon
    elif phase_angle < 67.5:
        return '🌒'  # Waxing Crescent
    elif phase_angle < 112.5:
        return '🌓'  # First Quarter
    elif phase_angle < 157.5:
        return '🌔'  # Waxing Gibbous
    elif phase_angle < 202.5:
        return '🌕'  # Full Moon
    elif phase_angle < 247.5:
        return '🌖'  # Waning Gibbous
    elif phase_angle < 292.5:
        return '🌗'  # Last Quarter
    else:
        return '🌘'  # Waning Crescent


def generate_skymap(
    moon_longitude: float,
    nakshatra_name: str,
    nakshatra_pada: int,
    phase_angle: float,
    output_path: str,
    event_title: str = None,
    rahu_longitude: float = None,
    ketu_longitude: float = None
) -> str:
    """
    Generate an ecliptic wheel sky map showing the Moon's position among the 27 Nakshatras.
    Includes Rahu and Ketu as mathematical markers (v4.1.1).
    """
    # Ensure cache directory exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create figure with dark space background
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    
    fig = Figure(figsize=(10.0, 10.0), facecolor='#0a0a0f')
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111, polar=True, facecolor='#0a0a0f')
    
    # Draw the 27 Nakshatra segments
    for i, nak in enumerate(NAKSHATRAS):
        start_rad = np.radians(90 - nak["start"])
        end_rad = np.radians(90 - nak["end"])
        
        is_current = (nak["name"].lower() == nakshatra_name.lower() or 
                      nakshatra_name.lower().startswith(nak["name"].lower()[:4]))
        
        if is_current:
            color = NAKSHATRA_COLOR_HIGHLIGHT
            alpha = 0.85
            linewidth = 2
        else:
            color = NAKSHATRA_COLORS_NORMAL[i]
            alpha = 0.5
            linewidth = 0.5
        
        theta = np.linspace(start_rad, end_rad, 50)
        r_inner = 0.55
        r_outer = 0.95
        
        ax.fill_between(theta, r_inner, r_outer, color=color, alpha=alpha, 
                        edgecolor='#ffffff', linewidth=linewidth)
        
        mid_angle = (start_rad + end_rad) / 2
        label_r = 0.75
        
        rotation_deg = np.degrees(mid_angle) - 90
        if -180 < rotation_deg < -90 or 90 < rotation_deg < 180:
            rotation_deg += 180
        
        short_name = nak["name"][:6] if len(nak["name"]) > 6 else nak["name"]
        
        ax.text(
            mid_angle, label_r, short_name,
            ha='center', va='center',
            fontsize=7 if is_current else 6,
            color='#ffffff' if is_current else '#aaaaaa',
            fontweight='bold' if is_current else 'normal',
            rotation=rotation_deg,
            rotation_mode='anchor'
        )
    
    # Rahu & Ketu (Lunar Nodes) - Mathematical points (v4.1.1)
    if rahu_longitude is not None:
        rahu_rad = np.radians(90 - rahu_longitude)
        ax.text(rahu_rad, 1.02, '☊', color='#ff33cc', fontsize=18, fontweight='bold', ha='center', va='center')
        ax.text(rahu_rad, 1.10, 'RAHU', color='#ff33cc', fontsize=7, ha='center', va='center', fontweight='bold')
    
    if ketu_longitude is not None:
        ketu_rad = np.radians(90 - ketu_longitude)
        ax.text(ketu_rad, 1.02, '☋', color='#cc33ff', fontsize=18, fontweight='bold', ha='center', va='center')
        ax.text(ketu_rad, 1.10, 'KETU', color='#cc33ff', fontsize=7, ha='center', va='center', fontweight='bold')

    # Draw the Moon at its position
    moon_rad = np.radians(90 - moon_longitude)
    moon_r = 0.75
    
    # Moon marker
    ax.plot(moon_rad, moon_r, 'o', markersize=28, color='#ffd700', 
            markeredgecolor='#ffffff', markeredgewidth=2, zorder=10)
    
    # Add moon phase symbol (Removed emoji to fix font warning on Oracle Linux 9)
    # ax.text(moon_rad, moon_r, moon_symbol, fontsize=20, ha='center', va='center', zorder=11)
    
    # Draw Earth at center
    ax.plot(0, 0, 'o', markersize=20, color='#4a90d9', 
            markeredgecolor='#ffffff', markeredgewidth=1.5, zorder=5)
    ax.text(0, 0, 'EARTH', fontsize=7, ha='center', va='center', color='#ffffff', zorder=6)
    
    # Configure polar plot
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1.15) # Increased to fit Rahu/Ketu labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)
    
    # Save the figure with minimal padding
    fig.savefig(output_path, dpi=120, bbox_inches='tight', 
                facecolor=fig.get_facecolor(), edgecolor='none',
                pad_inches=0.1)
    
    return output_path


def get_nakshatra_info(nakshatra_name: str):
    """
    Get detailed information about a Nakshatra by name.
    
    Args:
        nakshatra_name: Full or partial name of the Nakshatra
    
    Returns:
        Dictionary with Nakshatra details or None if not found
    """
    nakshatra_lower = nakshatra_name.lower()
    for nak in NAKSHATRAS:
        if nak["name"].lower() == nakshatra_lower or nakshatra_lower.startswith(nak["name"].lower()[:4]):
            return nak
    return None

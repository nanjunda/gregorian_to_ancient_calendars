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


def get_cached_image(cache_key: str) -> str | None:
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
    event_title: str = None
) -> str:
    """
    Generate an ecliptic wheel sky map showing the Moon's position among the 27 Nakshatras.
    
    This creates a polar plot visualization with:
    - 27 Nakshatra segments arranged in a circle
    - The Moon marker at its correct sidereal position
    - The current Nakshatra highlighted
    - Educational labels and captions
    
    Args:
        moon_longitude: Moon's sidereal longitude (0-360°)
        nakshatra_name: Name of the current Nakshatra
        nakshatra_pada: Pada number (1-4)
        phase_angle: Sun-Moon angular separation for moon phase
        output_path: File path to save the generated PNG
        event_title: Optional title for the event
    
    Returns:
        Path to the generated image
    """
    # Ensure cache directory exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create figure with dark space background
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')
    
    # Draw the 27 Nakshatra segments
    for i, nak in enumerate(NAKSHATRAS):
        # Convert degrees to radians for polar plot
        # Rotate by 90° so Ashwini (0°) is at top
        start_rad = np.radians(90 - nak["start"])
        end_rad = np.radians(90 - nak["end"])
        
        # Determine if this is the current Nakshatra
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
        
        # Create the wedge for this Nakshatra
        theta = np.linspace(start_rad, end_rad, 50)
        r_inner = 0.55
        r_outer = 0.95
        
        # Fill the segment
        ax.fill_between(theta, r_inner, r_outer, color=color, alpha=alpha, 
                        edgecolor='#ffffff', linewidth=linewidth)
        
        # Add Nakshatra name label (abbreviated)
        mid_angle = (start_rad + end_rad) / 2
        label_r = 0.75
        
        # Calculate rotation for text to be readable
        rotation_deg = np.degrees(mid_angle) - 90
        if -180 < rotation_deg < -90 or 90 < rotation_deg < 180:
            rotation_deg += 180
        
        # Shorten long names
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
    
    # Draw the Moon at its position
    moon_rad = np.radians(90 - moon_longitude)  # Convert to polar coordinates
    moon_r = 0.75
    
    # Moon marker (golden circle)
    ax.plot(moon_rad, moon_r, 'o', markersize=28, color='#ffd700', 
            markeredgecolor='#ffffff', markeredgewidth=2, zorder=10)
    
    # Add moon phase symbol
    moon_symbol = get_moon_phase_symbol(phase_angle)
    ax.text(moon_rad, moon_r, moon_symbol, fontsize=20, ha='center', va='center', zorder=11)
    
    # Draw Earth at center
    ax.plot(0, 0, 'o', markersize=20, color='#4a90d9', 
            markeredgecolor='#ffffff', markeredgewidth=1.5, zorder=5)
    ax.text(0, 0, '🌍', fontsize=14, ha='center', va='center', zorder=6)
    
    # Add "Earth" label
    ax.text(0, 0.15, 'Earth', fontsize=8, ha='center', va='center', 
            color='#888888', zorder=6)
    
    # Inner decorative ring
    inner_ring = plt.Circle((0, 0), 0.45, transform=ax.transData._b, 
                            fill=False, color='#333344', linewidth=1, linestyle='--')
    ax.add_patch(inner_ring)
    
    # Title - Increased vertical margin to prevent cutoff
    title_text = f"🌌 Moon in {nakshatra_name}"
    if nakshatra_pada:
        title_text += f" (Pada {nakshatra_pada})"
    
    # Lower y value to give more head room
    fig.suptitle(
        title_text,
        fontsize=22, color='#ffffff', fontweight='bold', y=0.95,
        fontfamily='sans-serif', horizontalalignment='center'
    )
    
    # Subtitle with event title if provided
    if event_title:
        ax.set_title(f'"{event_title}"', fontsize=13, color='#ff9100', 
                     pad=30, fontfamily='sans-serif')
    
    # Caption at bottom
    caption_text = f"Moon Position: {moon_longitude:.1f}° Sidereal  |  Phase: {phase_angle:.0f}°"
    fig.text(0.5, 0.06, caption_text, ha='center', va='center',
             fontsize=12, color='#888888', fontfamily='sans-serif')
    
    # Educational note
    fig.text(0.5, 0.03, 
             "Ecliptic wheel showing the Moon's position among the 27 Nakshatras",
             ha='center', va='center', fontsize=10, color='#555555', 
             style='italic', fontfamily='sans-serif')
    
    # Configure polar plot
    ax.set_theta_zero_location('N')  # 0° at top (North)
    ax.set_theta_direction(-1)  # Clockwise direction
    ax.set_ylim(0, 1.05)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)
    
    # Save the figure with significant padding to avoid any possible clipping
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor=fig.get_facecolor(), edgecolor='none',
                pad_inches=0.8)
    plt.close(fig)
    
    return output_path


def get_nakshatra_info(nakshatra_name: str) -> dict | None:
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

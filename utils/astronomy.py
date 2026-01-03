from skyfield.api import load, Topos, Star
from skyfield import almanac
from datetime import datetime, timedelta
import pytz
import numpy as np

# Load ephemeris data
eph = load('de421.bsp')
sun = eph['sun']
moon = eph['moon']
earth = eph['earth']
ts = load.timescale()

def get_ayanamsha(jd):
    """
    Calculates precise Lahiri (Chitra Paksha) Ayanamsha.
    Uses the standard polynomial for the mean ayanamsha.
    """
    t = (jd - 2451545.0) / 36525.0
    # Precise formula for mean Lahiri ayanamsha
    # A = 23.85 + 50.27" * t ...
    # Standard formula for J2000: 23.8580833 + 1.39733*T + 0.000308*T^2
    ayanamsha = 23.8580833 + (1.3973333 * t) + (0.0003088 * t * t)
    return ayanamsha

def get_sidereal_longitude(target_time_utc, body):
    """
    Calculates the Nirayana (Sidereal) longitude of a celestial body (Sun or Moon).
    """
    t = ts.from_datetime(target_time_utc)
    astrometric = earth.at(t).observe(body)
    ecliptic_lat, ecliptic_lon, distance = astrometric.ecliptic_latlon()
    
    tropical_lon = ecliptic_lon.degrees
    ayanamsha = get_ayanamsha(t.tt)
    
    sidereal_lon = (tropical_lon - ayanamsha) % 360
    return sidereal_lon

def get_previous_new_moon(target_time_utc):
    """
    Finds the most recent New Moon (Amavasya) preceding the target time.
    """
    t_end = ts.from_datetime(target_time_utc)
    t_start = ts.from_datetime(target_time_utc - timedelta(days=32))
    
    times, phases = almanac.find_discrete(t_start, t_end, almanac.moon_phases(eph))
    
    # Phases: 0=New Moon, 1=First Quarter, 2=Full Moon, 3=Last Quarter
    new_moons = [t for t, p in zip(times, phases) if p == 0]
    
    if not new_moons:
        # Should not happen with 32 days window
        return target_time_utc
    
    return new_moons[-1].astimezone(pytz.utc)

def get_sunrise_sunset(date_local, lat, lon, timezone_str):
    """
    Calculates Sunrise and Sunset for a given date and location.
    """
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    tz = pytz.timezone(timezone_str)
    
    # Define the time range for the day (searching from 00:00 to 23:59 local)
    t0 = ts.from_datetime(tz.localize(datetime(date_local.year, date_local.month, date_local.day, 0, 0, 0)))
    t1 = ts.from_datetime(tz.localize(datetime(date_local.year, date_local.month, date_local.day, 23, 59, 59)))
    
    f = almanac.sunrise_sunset(eph, Topos(latitude_degrees=lat, longitude_degrees=lon))
    times, events = almanac.find_discrete(t0, t1, f)
    
    sunrise = None
    sunset = None
    
    for t, event in zip(times, events):
        if event == 1: # Sunrise
            sunrise = t.astimezone(tz)
        elif event == 0: # Sunset
            sunset = t.astimezone(tz)
            
    return sunrise, sunset

def get_rashi(moon_lon):
    """
    Calculates the Rashi (Moon Sign) index based on Sidereal Longitude.
    """
    return int(moon_lon / 30.0) % 12

def get_lagna(date_local, lat, lon, timezone_str):
    """
    Calculates the Lagna (Ascendant) Sidereal Longitude and Rashi Index.
    """
    # Create Observer
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    
    # Precise time calculation
    t = ts.from_datetime(date_local)
    
    # 1. Get Ayanamsha for this time
    ayanamsha = get_ayanamsha(t.tt)
    
    # 2. Calculate Ascendant (Intersection of Ecliptic and Horizon)
    # Using simple formula for approximation or Skyfield if possible.
    # Note: Skyfield doesn't have a direct "ascendant" function in its high-level API easily accessible 
    # without vector math. We will use the standard formula with GAST.
    
    # We compute GAST (Greenwich Apparent Sidereal Time)
    gast = t.gast 
    
    # Local Sidereal Time (LST) in hours
    lst = (gast + lon / 15.0) % 24.0
    
    # Obliquity of Ecliptic (approx 23.44)
    eps = 23.4392911
    
    # Convert degrees to radians
    lat_rad = np.radians(lat)
    lst_rad = np.radians(lst * 15.0)
    eps_rad = np.radians(eps)
    
    # tan(Asc) = -cos(LST) / (sin(LST)*cos(eps) + tan(lat)*sin(eps))
    y = -np.cos(lst_rad)
    x = (np.sin(lst_rad) * np.cos(eps_rad)) + (np.tan(lat_rad) * np.sin(eps_rad))
    
    asc_rad = np.arctan2(y, x)
    asc_deg_tropical = np.degrees(asc_rad)
    
    # Normalize to 0-360
    asc_deg_tropical = (asc_deg_tropical + 360) % 360
    
    # 3. Convert to Sidereal (Nirayana)
    asc_deg_sidereal = (asc_deg_tropical - ayanamsha) % 360
    
    # 4. Get Rashi Index
    lagna_index = int(asc_deg_sidereal / 30.0) % 12
    
    return lagna_index, asc_deg_sidereal

def get_angular_data(date_local, lat, lon, timezone_str):
    """
    Returns a dictionary with raw astronomical data needed for educational fact cards.
    Includes:
        - Sun sidereal longitude
        - Moon sidereal longitude
        - Ayanamsha (Lahiri)
        - Sun-Moon angular separation (phase angle)
        - Ecliptic longitude of the Sun (tropical) for reference
    """
    # Ensure date_local is a datetime with timezone
    if date_local.tzinfo is None:
        tz = pytz.timezone(timezone_str)
        date_local = tz.localize(date_local)
    # Convert to UTC for calculations
    utc_dt = date_local.astimezone(pytz.utc)
    # Sidereal longitudes
    sun_sid = get_sidereal_longitude(utc_dt, sun)
    moon_sid = get_sidereal_longitude(utc_dt, moon)
    # Ayanamsha for the moment
    t = ts.from_datetime(utc_dt)
    ayanamsha = get_ayanamsha(t.tt)
    # Tropical Sun longitude (for phase calculation)
    t_tropical = ts.from_datetime(utc_dt)
    astrometric = earth.at(t_tropical).observe(sun)
    _, sun_tropical_lon, _ = astrometric.ecliptic_latlon()
    sun_tropical_deg = sun_tropical_lon.degrees
    # Phase angle between Sun and Moon (0-360)
    phase_angle = (moon_sid - sun_sid) % 360
    return {
        "sun_sidereal": round(sun_sid, 4),
        "moon_sidereal": round(moon_sid, 4),
        "ayanamsha": round(ayanamsha, 4),
        "sun_tropical": round(sun_tropical_deg, 4),
        "phase_angle": round(phase_angle, 2)
    }

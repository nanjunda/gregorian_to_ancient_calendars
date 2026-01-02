from datetime import datetime
import pytz
from utils.location import get_location_details
from utils.astronomy import get_sidereal_longitude, get_sunrise_sunset, sun, moon, get_previous_new_moon
from panchanga.calculations import (
    calculate_vara, calculate_tithi, calculate_nakshatra, 
    calculate_yoga, calculate_karana, calculate_masa_samvatsara
)

def debug_check():
    location_name = "Narmadapuram, India"
    date_str = "1959-11-17"
    time_str = "19:30"
    
    loc = get_location_details(location_name)
    local_tz = pytz.timezone(loc["timezone"])
    dt_local = local_tz.localize(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
    dt_utc = dt_local.astimezone(pytz.utc)

    # Correct Tithi with precise Ayanamsha
    sun_lon = get_sidereal_longitude(dt_utc, sun)
    moon_lon = get_sidereal_longitude(dt_utc, moon)
    
    # Check Previous New Moon for Masa
    prev_amavasya_utc = get_previous_new_moon(dt_utc)
    sun_lon_at_nm = get_sidereal_longitude(prev_amavasya_utc, sun)

    print(f"Sun Sidereal Lon (Now): {sun_lon}")
    print(f"Sun Sidereal Lon (Amavasya): {sun_lon_at_nm}")
    print(f"Diff (Moon-Sun): {(moon_lon - sun_lon) % 360}")

    tithi, paksha = calculate_tithi(sun_lon, moon_lon)
    masa, samvatsara = calculate_masa_samvatsara(dt_local.year, sun_lon_at_nm, sun_lon)
    
    print(f"Tithi Boundary Gap: {((moon_lon - sun_lon) % 360) / 12}")
    print(f"Result -> Masa: {masa}, Paksha: {paksha}, Tithi: {tithi}")

if __name__ == "__main__":
    debug_check()

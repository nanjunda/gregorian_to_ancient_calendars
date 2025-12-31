from datetime import datetime, timedelta
import pytz
from utils.astronomy import get_sidereal_longitude, get_sunrise_sunset, sun, moon
from panchanga.calculations import (
    calculate_tithi, calculate_masa_samvatsara, calculate_vara, 
    calculate_nakshatra, calculate_yoga, calculate_karana, format_panchanga_report
)

def find_recurrences(base_dt, loc_details, num_years=10):
    """
    Finds the next num_years occurrences of the same Masa, Paksha, and Tithi.
    """
    # 1. Get target attributes
    utc_dt = base_dt.astimezone(pytz.utc)
    sun_lon = get_sidereal_longitude(utc_dt, sun)
    moon_lon = get_sidereal_longitude(utc_dt, moon)
    
    target_tithi, target_paksha = calculate_tithi(sun_lon, moon_lon)
    target_masa, _ = calculate_masa_samvatsara(base_dt.year, sun_lon)
    
    print(f"Searching for: {target_masa}, {target_paksha}, {target_tithi}")
    
    results = []
    
    # 2. Iterate through future years
    # We start searching from the year after base_dt
    for year_offset in range(0, num_years + 1):
        year = base_dt.year + year_offset
        # Approximate date: same month/day
        try:
            approx_date = datetime(year, base_dt.month, base_dt.day, base_dt.hour, base_dt.minute)
        except ValueError:
            # Handle Feb 29
            approx_date = datetime(year, base_dt.month, base_dt.day - 1, base_dt.hour, base_dt.minute)
            
        # Search window +/- 30 days
        found_for_year = False
        start_search = approx_date - timedelta(days=32)
        
        # Scan day by day
        for d_offset in range(65): # 65 days window to be safe
            current_day = start_search + timedelta(days=d_offset)
            current_day_local = current_day.replace(tzinfo=None) # naive for calculation
            
            # For each day, we check the Panchanga elements at the input time or noon
            # Traditionally, we should check when the Tithi prevails.
            # Here we check the exact same time of day as the original input.
            tz = pytz.timezone(loc_details["timezone"])
            dt_local = tz.localize(datetime(current_day.year, current_day.month, current_day.day, base_dt.hour, base_dt.minute))
            dt_utc = dt_local.astimezone(pytz.utc)
            
            s_lon = get_sidereal_longitude(dt_utc, sun)
            m_lon = get_sidereal_longitude(dt_utc, moon)
            
            tithi, paksha = calculate_tithi(s_lon, m_lon)
            masa, samvatsara = calculate_masa_samvatsara(dt_local.year, s_lon)
            
            if tithi == target_tithi and paksha == target_paksha and masa == target_masa:
                # Found the match!
                # Calculate full details for report
                sunrise, sunset = get_sunrise_sunset(dt_local, loc_details["latitude"], loc_details["longitude"], loc_details["timezone"])
                vara = calculate_vara(dt_local, sunrise)
                nakshatra = calculate_nakshatra(m_lon)
                yoga = calculate_yoga(s_lon, m_lon)
                karana = calculate_karana(s_lon, m_lon)
                
                report = format_panchanga_report(
                    dt_local, loc_details["address"], loc_details["timezone"],
                    sunrise, sunset, samvatsara, masa, paksha, tithi,
                    vara, nakshatra, yoga, karana
                )
                
                results.append({
                    "datetime": dt_local,
                    "report": report
                })
                found_for_year = True
                break
                
    return results

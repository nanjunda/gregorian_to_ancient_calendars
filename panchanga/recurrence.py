from datetime import datetime, timedelta
import pytz
from utils.astronomy import get_sidereal_longitude, get_sunrise_sunset, sun, moon, get_previous_new_moon
from panchanga.calculations import (
    calculate_tithi, calculate_masa_samvatsara, calculate_vara, 
    calculate_nakshatra, calculate_yoga, calculate_karana, format_panchanga_report
)

def find_recurrences(base_dt, loc_details, num_entries=20, lang='EN'):
    """
    Finds the next num_entries occurrences of the same Masa, Paksha, and Tithi.
    Starts search from the current date.
    """
    # 1. Get target attributes from the original date
    utc_dt = base_dt.astimezone(pytz.utc)
    sun_lon = get_sidereal_longitude(utc_dt, sun)
    moon_lon = get_sidereal_longitude(utc_dt, moon)
    
    target_tithi, target_paksha = calculate_tithi(sun_lon, moon_lon, lang=lang)
    
    # Target Masa must be determined at the New Moon preceding the original event
    prev_nm_utc = get_previous_new_moon(utc_dt)
    sun_lon_at_nm = get_sidereal_longitude(prev_nm_utc, sun)
    target_masa, _ = calculate_masa_samvatsara(base_dt.year, sun_lon_at_nm, sun_lon, lang=lang)
    
    now = datetime.now(pytz.utc)
    current_year = now.year
    
    # Starting search from current year
    print(f"Searching for: {target_masa}, {target_paksha}, {target_tithi} for next {num_entries} matches...")
    
    results = []
    year_to_search = current_year
    
    # 2. Search year by year until we have num_entries
    while len(results) < num_entries:
        # Approximate date: same month/day
        try:
            approx_date = datetime(year_to_search, base_dt.month, base_dt.day, base_dt.hour, base_dt.minute)
        except ValueError:
            approx_date = datetime(year_to_search, base_dt.month, 28, base_dt.hour, base_dt.minute)
            
        tz = pytz.timezone(loc_details["timezone"])
        # Window of search (+/- 30 days around approx date)
        start_search = approx_date - timedelta(days=32)
        
        for d_offset in range(65):
            current_day = start_search + timedelta(days=d_offset)
            dt_local = tz.localize(datetime(current_day.year, current_day.month, current_day.day, base_dt.hour, base_dt.minute))
            dt_utc = dt_local.astimezone(pytz.utc)
            
            # Skip past dates
            if dt_utc < now:
                continue
                
            s_lon = get_sidereal_longitude(dt_utc, sun)
            m_lon = get_sidereal_longitude(dt_utc, moon)
            
            tithi, paksha = calculate_tithi(s_lon, m_lon, lang=lang)
            curr_nm_utc = get_previous_new_moon(dt_utc)
            s_lon_at_nm = get_sidereal_longitude(curr_nm_utc, sun)
            masa, samvatsara = calculate_masa_samvatsara(dt_local.year, s_lon_at_nm, s_lon, lang=lang)
            
            if tithi == target_tithi and paksha == target_paksha and masa == target_masa:
                # Basic protection against double-counting the same day
                if results and results[-1]["datetime"].date() == dt_local.date():
                    continue

                sunrise, sunset = get_sunrise_sunset(dt_local, loc_details["latitude"], loc_details["longitude"], loc_details["timezone"])
                vara = calculate_vara(dt_local, sunrise, lang=lang)
                nakshatra, nak_pada = calculate_nakshatra(m_lon, lang=lang)
                yoga = calculate_yoga(s_lon, m_lon, lang=lang)
                karana = calculate_karana(s_lon, m_lon)
                
                report = format_panchanga_report(
                    dt_local, loc_details["address"], loc_details["timezone"],
                    sunrise, sunset, samvatsara, masa, paksha, tithi,
                    vara, nakshatra, nak_pada, yoga, karana, lang=lang
                )
                
                results.append({
                    "datetime": dt_local,
                    "report": report
                })
                
                if len(results) >= num_entries:
                    break
        
        year_to_search += 1
        # Safety break to prevent infinite loops if something is wrong with calculations
        if year_to_search > current_year + (num_entries * 2):
            break
            
    return results
                
    return results

from engines.base import BaseCalendar
from datetime import datetime
import pytz
from utils.location import get_location_details
from panchanga.calculations import (
    calculate_vara, calculate_tithi, calculate_nakshatra, 
    calculate_yoga, calculate_karana, calculate_masa_samvatsara,
    calculate_saka_year, format_panchanga_report
)
from utils.astronomy import get_sidereal_longitude, get_sunrise_sunset, sun, moon, get_previous_new_moon, get_angular_data
from panchanga.recurrence import find_recurrences
from utils.zodiac import get_zodiac_name, ZODIAC_SIGNS
from utils.astronomy import get_rashi, get_lagna

class PanchangaEngine(BaseCalendar):
    def calculate_data(self, date_str, time_str, location_name, lang='EN'):
        """
        Calculates Panchanga data. Logic moved verbatim from app.py:get_panchanga().
        """
        # 1. Resolve Location
        loc = get_location_details(location_name)
        
        # 2. Parse DateTime
        dt_str = f"{date_str} {time_str}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(loc["timezone"])
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        # 3. Get Astronomical Data
        sun_lon = get_sidereal_longitude(utc_dt, sun)
        moon_lon = get_sidereal_longitude(utc_dt, moon)
        sunrise, sunset = get_sunrise_sunset(local_dt, loc["latitude"], loc["longitude"], loc["timezone"])
        
        # New Moon for Masa
        prev_nm_utc = get_previous_new_moon(utc_dt)
        sun_lon_at_nm = get_sidereal_longitude(prev_nm_utc, sun)
        
        # 4. Calculate Panchanga Elements
        vara = calculate_vara(local_dt, sunrise, lang=lang)
        tithi, paksha = calculate_tithi(sun_lon, moon_lon, lang=lang)
        nakshatra, nak_pada = calculate_nakshatra(moon_lon, lang=lang)
        yoga = calculate_yoga(sun_lon, moon_lon, lang=lang)
        karana_num = calculate_karana(sun_lon, moon_lon)
        masa, samvatsara = calculate_masa_samvatsara(local_dt.year, sun_lon_at_nm, sun_lon, lang=lang)
        
        # 5. Calculate Rashi and Lagna (v3.2)
        rashi_idx = get_rashi(moon_lon)
        rashi_name = get_zodiac_name(rashi_idx, lang)
        rashi_code = ZODIAC_SIGNS[rashi_idx]["code"]
        
        lagna_idx, lagna_deg = get_lagna(local_dt, loc["latitude"], loc["longitude"], loc["timezone"])
        lagna_name = get_zodiac_name(lagna_idx, lang)
        lagna_code = ZODIAC_SIGNS[lagna_idx]["code"]

        report = format_panchanga_report(
            local_dt, loc["address"], loc["timezone"],
            sunrise, sunset, samvatsara, masa, paksha, tithi,
            vara, nakshatra, nak_pada, yoga, karana_num, lang=lang
        )

        # 6. Calculate Next Birthday (Feature v4.1)
        next_bdays = find_recurrences(local_dt, loc, num_entries=1, lang=lang)
        next_bday = next_bdays[0]["datetime"].strftime('%A, %B %d, %Y') if next_bdays else "N/A"

        # Construct payload (verbatim from app.py)
        result_data = {
            "input_datetime": local_dt.strftime('%Y-%m-%d %H:%M:%S'),
            "timezone": loc["timezone"],
            "address": loc["address"],
            "sunrise": sunrise.strftime('%H:%M:%S') if sunrise else 'N/A',
            "sunset": sunset.strftime('%H:%M:%S') if sunset else 'N/A',
            "samvatsara": samvatsara,
            "saka_year": calculate_saka_year(local_dt),
            "masa": masa,
            "paksha": paksha,
            "tithi": tithi,
            "vara": vara,
            "nakshatra": f"{nakshatra} (Pada {nak_pada})",
            "yoga": yoga,
            "karana": karana_num,
            "rashi": {"name": rashi_name, "code": rashi_code},
            "lagna": {"name": lagna_name, "code": lagna_code},
            "angular_data": get_angular_data(local_dt, loc["latitude"], loc["longitude"], loc["timezone"]),
            "next_birthday": next_bday,
            "report": report,
            "lat_lon": {"lat": loc["latitude"], "lon": loc["longitude"]} # Useful for visuals
        }
        return result_data

    def get_visual_configs(self, data):
        """
        Specific for Panchanga - specifies which 3D modules to enable.
        """
        return {
            "modules": [
                "zodiac_comparison", 
                "moon_phase", 
                "constellations", 
                "precession", 
                "samvatsara", 
                "lunar_nodes"
            ]
        }

    def get_ai_context(self, data):
        """
        Returns data formatted for AI Maestro.
        """
        return data  # Panchanga uses the full data object for AI

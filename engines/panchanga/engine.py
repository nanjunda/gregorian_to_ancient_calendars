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
from utils.ical_gen import create_ical_content
from utils.skyshot import generate_skymap, get_cache_key as get_sky_cache, get_cached_image as get_sky_cached
from utils.solar_system import generate_solar_system, get_cache_key as get_solar_cache, get_cached_image as get_solar_cached
import base64
import os

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

    def get_ai_instructions(self):
        """
        Returns the civilization-specific AI prompt/instructions for the context spoke.
        """
        return """
        Markdown Report Hierarchy (Mandatory Phases):

        Phase I: The Universal Clock (General Concepts)
        - Define "What is a Calendar?". Explain it as an engineering solution to synchronize Day/Month/Year rhythms.
        - The Solar Engine (Western): Explain how it follows Earth's orbit (seasons).
        - The Lunar-Solar Fusion (Panchanga): Explain how it synchronizes both Sun and Moon using the background stars (Sidereal).
        - **The Birthday Drift**: Explain why a "Panchanga Birthday" (based on Tithi/Nakshatra) moves relative to the Western calendar. Mention the ~11 day lunar-solar gap and how **Adhika Masa** (Leap Month) acts as a cosmic synchronization tool.
        - **The Great Drift**: Explain Axial Precession (Earth's wobble) and why Sidereal signs differ from Tropical ones. Use [[RENDER:ZODIAC_COMPARISON]].

        Phase II: The Library of Atoms (Terminology)
        Provide detailed physics/geometric deconstructions for:
        - **Samvatsara**: Explain as the 60-year Jupiter-Saturn resonance/alignment cycle. Use [[RENDER:SAMVATSARA_RESONANCE]].
        - **Saka Varsha (The Civil Era)**: Explain this as the **Official Indian Civil Calendar** (used by the Government).
          *   **The Origin**: Started in 78 AD (King Shalivahana).
          *   **The Difference**: It is a purely **Solar (Agricultural)** count, unlike the **Cosmic (Luni-Solar)** Samvatsara. Use the analogy of "Administrative Time" vs "Nature's Time".
        - **Masa: The Cosmic Month**: Explain the two ways to measure a month:
          1. **Saura Mana (The Solar Runner)**: The steady 30-day month defined by the Sun entering a new sign (e.g., Mesha).
          2. **Chandra Mana (The Lunar Sprinter)**: The fast 29.5-day month defined by the Moon's phases.
          *   **The Naming Secret**: Explain that Lunar months are named after the star the Moon is near when it is full (e.g., Full Moon near **Chitta/Spica** = **Chaitra**, Full Moon near **Krittika/Pleiades** = **Karthika**).
          *   **The Drift**: Explain that the Moon is faster than the Sun by ~11 days a year.
          *   **The Pit Stop (Adhik Masa)**: Explain that every 3 years, the Moon takes a "Pit Stop" (Extra Month) to let the Sun catch up.
        - **Nakshatra**: 13°20' sectors used as a "Lunar Speedometer" to track the Moon's 27.3-day orbit. Use [[RENDER:CONSTELLATION_MAP]].
        - **Tithi**: Defined strictly as Every 12° of angular separation between Sun and Moon. Use [[RENDER:MOON_PHASE_3D]].
        - **Yoga**: Combined longitudinal momentum (Sum of longitudes).
        - **Rashi**: Define the term Rāśi from a scientific and astronomical perspective (not astrological). Explain its relation to the ecliptic, the Sun, Moon, and planets, and give one simple example. Keep the explanation brief and precise
        - **Lagna**: Define the term Lagna from a scientific and astronomical perspective (not astrological). Explain its relation to Earth’s rotation, the horizon, the ecliptic, and the observer’s location, and give one simple example. Keep the explanation brief and precise
        - **Karana**: High-precision Half-Tithi (6° intervals).
        - **Rahu & Ketu**: Explain as **Lunar Nodes** (intersection points of orbital planes). Use [[RENDER:PRECESSION_WOBBLE]].
        - **Safe Harbor Terms**: Explain terms like **Graha** (Planetary Bodies), **Muhurtha** (Time units), **Sankranti** (Solar Ingress), **Vakra** (Retrograde Motion), **Asta** (Combustion/Invisibility), and **Ayanamsa** (Precession Index) strictly as mathematical or physical phenomena if they appear in the data. Refuse to discuss their "effects" on human destiny.

        Phase III: Decoding Your Specific Cosmic Alignment
        - Create a specific section: `## 🧩 Decoding Your Specific Cosmic Alignment`.
        - Use the specific values from the Input Data (Samvatsara, Masa, etc) to explain THIS specific moment.
        - Tell the student what they would see if they looked at the sky right now.

        Tone: "Cool Science YouTuber" - high energy, fascinating, and precise.
        """

    def generate_ical(self, date_str, time_str, location_name, title, lang):
        """
        Generates iCal content for 20 years of recurrences.
        """
        loc = get_location_details(location_name)
        dt_str = f"{date_str} {time_str}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(loc["timezone"])
        local_dt = local_tz.localize(naive_dt)

        occurrences = find_recurrences(local_dt, loc, num_entries=20, lang=lang)
        return create_ical_content(title, occurrences)

    def get_rich_visuals(self, date_str, time_str, location_name, title):
        """
        Generates SkyMap and Solar System views as Base64.
        """
        loc = get_location_details(location_name)
        dt_str = f"{date_str} {time_str}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(loc["timezone"])
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        # 1. SkyShot
        sky_cache = get_sky_cache(date_str, time_str, loc["latitude"], loc["longitude"])
        sky_img_path = get_sky_cached(sky_cache)
        
        if not sky_img_path:
            from utils.skyshot import CACHE_DIR
            sky_img_path = str(CACHE_DIR / f"{sky_cache}.png")
            moon_lon = get_sidereal_longitude(utc_dt, moon)
            ang = get_angular_data(local_dt, loc["latitude"], loc["longitude"], loc["timezone"])
            nak, pada = calculate_nakshatra(moon_lon, lang='EN')
            generate_skymap(moon_lon, nak, pada, ang["phase_angle"], sky_img_path, 
                           event_title=title, rahu_longitude=ang["rahu_sidereal"], ketu_longitude=ang["ketu_sidereal"])

        # 2. Solar System
        sol_cache = get_solar_cache(date_str, time_str)
        sol_img_path = get_solar_cached(sol_cache)
        
        if not sol_img_path:
            from utils.solar_system import CACHE_DIR as SOL_CACHE_DIR
            sol_img_path = str(SOL_CACHE_DIR / f"{sol_cache}.png")
            generate_solar_system(utc_dt, sol_img_path, event_title=title)

        # Convert to Base64
        results = {}
        for key, path in [("skyshot", sky_img_path), ("solar_system", sol_img_path)]:
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                results[key] = f"data:image/png;base64,{encoded}"
        
        return results

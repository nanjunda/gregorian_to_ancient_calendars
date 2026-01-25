import math
from datetime import datetime
from engines.base import BaseCalendar

class MayanEngine(BaseCalendar):
    """
    Mayan Calendar Engine for Ancient Calendars v2.1.
    Implements the Long Count, Tzolk'in, and Haab' arithmetic cycles.
    """

    TZOLKIN_NAMES = [
        "Imix", "Ik'", "Ak'b'al", "K'an", "Chikchan", 
        "Kimi", "Manik'", "Lamat", "Muluk", "Ok", 
        "Chuwen", "Eb'", "B'en", "Ix", "Men", 
        "Kib'", "Kab'an", "Etz'nab'", "Kawak", "Ajaw"
    ]

    HAAB_MONTHS = [
        "Pop", "Wo'", "Sip", "Zotz'", "Sek", "Xul", 
        "Yaxk'in", "Mol", "Ch'en", "Yax", "Sak'", 
        "Keh", "Mak", "K'ank'in", "Muwan", "Pax", 
        "K'ayab'", "Kumk'u", "Wayeb'"
    ]

    # GMT Correlation (Goodman-Martinez-Thompson)
    GMT_CORRELATION = 584283

    def _get_julian_day(self, dt):
        """Standard Julian Day calculation from datetime object."""
        y, m, d = dt.year, dt.month, dt.day
        if m <= 2:
            y -= 1
            m += 12
        a = math.floor(y / 100)
        b = 2 - a + math.floor(a / 4)
        jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5
        return jd

    def calculate_data(self, date_str, time_str, location_name, lang='EN'):
        """
        Calculates Mayan data from input strings.
        Resolves location to ensure localized datetime is correctly converted to UTC for JD.
        """
        from utils.location import get_location_details
        import pytz

        # 1. Resolve Location & Timezone
        loc = get_location_details(location_name)
        local_tz = pytz.timezone(loc["timezone"])
        
        # 2. Parse DateTime
        dt_str = f"{date_str} {time_str}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        # 3. Calculate Julian Day (JD) from Unix Timestamp
        # JD 2440587.5 is 1970-01-01 00:00:00 UTC
        timestamp = utc_dt.timestamp()
        jd = 2440587.5 + (timestamp / 86400.0)

        # 4. Perform Mayan Arithmetic
        days_since_epoch = int(jd - self.GMT_CORRELATION)

        # 1. Long Count Calculation
        baktun = days_since_epoch // 144000
        rem = days_since_epoch % 144000
        katun = rem // 7200
        rem %= 7200
        tun = rem // 360
        rem %= 360
        uinal = rem // 20
        kin = rem % 20

        long_count = f"{baktun}.{katun}.{tun}.{uinal}.{kin}"

        # 2. Tzolk'in Calculation (260-day cycle)
        # Epoch 4 Ajaw: Ajaw is index 19. (4-1=3 for number)
        # number is 1-13, name is 0-19
        tzolkin_number = (days_since_epoch + 4 - 1) % 13 + 1
        tzolkin_name = self.TZOLKIN_NAMES[(days_since_epoch + 19) % 20]
        tzolkin_full = f"{tzolkin_number} {tzolkin_name}"

        # 3. Haab' Calculation (365-day cycle)
        # Epoch 8 Kumk'u: Kumk'u is index 17. 
        # Total days into Year cycle:
        haab_days = (days_since_epoch + 348) % 365
        if haab_days < 360:
            haab_month_idx = haab_days // 20
            haab_day_val = haab_days % 20
        else:
            haab_month_idx = 18 # Wayeb'
            haab_day_val = haab_days - 360
        
        haab_month_name = self.HAAB_MONTHS[haab_month_idx]
        haab_full = f"{haab_day_val} {haab_month_name}"

        return {
            "long_count": {
                "baktun": baktun,
                "katun": katun,
                "tun": tun,
                "uinal": uinal,
                "kin": kin,
                "formatted": long_count
            },
            "tzolkin": {
                "number": tzolkin_number,
                "name": tzolkin_name,
                "formatted": tzolkin_full
            },
            "haab": {
                "day": haab_day_val,
                "month": haab_month_name,
                "formatted": haab_full
            },
            "julian_day": jd,
            "days_since_epoch": days_since_epoch
        }

    def get_visual_configs(self, calculated_data):
        """
        Returns metadata for 3D/2D visual rendering of Mayan glyphs and gears.
        """
        return {
            "module": "MayanGears",
            "state": {
                "baktun_rotation": (calculated_data['long_count']['baktun'] % 13) * (360/13),
                "tzolkin_gear": calculated_data['tzolkin']['number'],
                "haab_gear": calculated_data['haab']['day']
            }
        }

    def get_ai_context(self, calculated_data):
        """
        Formats data for the AI Maestro.
        """
        return f"""
        Mayan Calendar Correlation Data:
        - Long Count: {calculated_data['long_count']['formatted']}
        - Tzolk'in: {calculated_data['tzolkin']['formatted']}
        - Haab': {calculated_data['haab']['formatted']}
        - Calculation Basis: GMT Correlation (584283), JD: {calculated_data['julian_day']}
        """

    def get_ai_instructions(self):
        """
        Returns the Mayan Scientific Masterclass prompt.
        """
        return """
        Markdown Report Hierarchy (Mayan Scientific Masterclass):

        Phase I: Mathematical Superiority (The Power of Zero)
        - Start with the "Shell" (Zero). Explain how the Maya understood 'Zero' centuries before Europe.
        - Contrast the elegance of Mayan Base-20 (Vigesimal) notation with Roman Numerals.
        - **MANDATORY**: You MUST insert the tag `[[RENDER:VIGESEL_ODOOMETER]]` after explaining the base-20 system.

        Phase II: The Long Count (The Cosmic Odometer)
        - Deconstruct the linear hierarchy (Kin -> Uinal -> Tun -> K'atun -> B'ak'tun).
        - Introduce "Deep Time" units: Piktun, Kalabtun, Alautun.
        - Explain that the Maya did not believe time "ended"; it simply rolls over.

        Phase III: The Calendar Round (Interlocking Gears)
        - Explain the resonance of the 260-day Tzolk'in and 365-day Haab' (52-year synchrony).
        - **MANDATORY**: You MUST insert the tag `[[RENDER:GEAR_INTERLOCK_52YR]]` here to visualize the gears.
        - Mention the 'Wayeb' (5 nameless days) as a mathematical necessity.

        Phase IV: Archaeoastronomy & Planetary Resonances
        - Explain the 584-day Synodic period of Venus and how 5 Venus cycles equal 8 Solar years.
        - Connect the math to the "Dresden Codex".
        - **MANDATORY**: You MUST insert the tag `[[RENDER:VENUS_MARS_ALIGNMENT]]` to show the pentagram orbit.

        STRICT GUARDRAIL: Zero mention of '2012 Apocalyptic' or 'Doomsday' pseudoscience.
        Focus on the parallel sophistication of Mayan and Ancient Indian mathematics.
        """

    def generate_ical(self, date_str, time_str, location_name, title, lang):
        """
        Generates iCal content with the next 20 occurrences of the Calendar Round.
        18,980 days = 52 Haab years.
        """
        from utils.location import get_location_details
        import pytz
        from utils.ical_gen import create_ical_content

        # 1. Get Initial JD
        loc = get_location_details(location_name)
        local_tz = pytz.timezone(loc["timezone"])
        naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)
        initial_jd = 2440587.5 + (utc_dt.timestamp() / 86400.0)

        # 2. Find next 20 matches (52-year cycle)
        # One Calendar Round = 18,980 days
        matches = []
        for i in range(1, 21):
            target_jd = initial_jd + (i * 18980)
            # Convert JD back to datetime
            # timestamp = (jd - 2440587.5) * 86400
            target_ts = (target_jd - 2440587.5) * 86400
            match_utc = datetime.fromtimestamp(target_ts, tz=pytz.utc)
            match_local = match_utc.astimezone(local_tz)
            
            # Formulate description
            mayan_data = self.calculate_data(match_local.strftime("%Y-%m-%d"), 
                                            match_local.strftime("%H:%M"), 
                                            location_name)
            
            description = (f"Mayan Anniversary: {mayan_data['tzolkin']['formatted']} {mayan_data['haab']['formatted']}\n"
                           f"Long Count: {mayan_data['long_count']['formatted']}")
            
            matches.append({
                "date": match_local.date(),
                "time": match_local.time(),
                "description": description
            })

        return create_ical_content(matches, title)

    def get_rich_visuals(self, date_str, time_str, location_name, title):
        """
        Returns Base64 encoded glyph or star maps.
        """
        return {} # To be populated with glyph assets

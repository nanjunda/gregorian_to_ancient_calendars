from data.panchanga_data import *
import math

def calculate_vara(local_time, sunrise_time):
    """
    Vara (Weekday) starts at Sunrise.
    """
    # weekday() returns 0 for Monday, 6 for Sunday.
    # Our VARAS list starts with Ravivara (Sunday) = 0? 
    # Let's adjust: Monday=1, ..., Sunday=0 or Saturday=6.
    # Standard Python: Monday=0, Tuesday=1, ..., Sunday=6.
    # Our VARAS: Ravivara(0), Somavara(1), ..., Shanivara(6)
    
    # Check if time is before sunrise
    if local_time < sunrise_time:
        # It's traditionally the previous day
        day_index = (local_time.weekday() - 0) % 7 # weekday() Monday is 0
    else:
        day_index = (local_time.weekday() + 1) % 7
        
    # Map Python's Monday=0 to our Somavara=1
    # Python: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    # VARAS: Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
    
    # Adjustment:
    # Python Mon(0) -> index 1
    # Python Sun(6) -> index 0
    # Python Sat(5) -> index 6
    
    mapping = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    
    if local_time < sunrise_time:
        weekday = (local_time.weekday() - 1) % 7
    else:
        weekday = local_time.weekday()
        
    return VARAS[mapping[weekday]]

def calculate_tithi(sun_lon, moon_lon):
    diff = (moon_lon - sun_lon) % 360
    tithi_index = int(diff / 12)
    paksha = "Shukla" if tithi_index < 15 else "Krishna"
    return TITHIS[tithi_index], paksha

def calculate_nakshatra(moon_lon):
    nakshatra_index = int(moon_lon / (360/27))
    return NAKSHATRAS[nakshatra_index]

def calculate_yoga(sun_lon, moon_lon):
    yoga_lon = (sun_lon + moon_lon) % 360
    yoga_index = int(yoga_lon / (360/27))
    return YOGAS[yoga_index]

def calculate_karana(sun_lon, moon_lon):
    diff = (moon_lon - sun_lon) % 360
    karana_index = int(diff / 6)
    # Karana 1 is Kimstughna (only for 1st half of 1st tithi)
    # There are fixed and mobile karanas. For simplicity, we just return the count or name if we had a full list.
    return karana_index + 1

def calculate_masa_samvatsara(year, sun_lon):
    # Rough approximation for Masa based on Sun's Rasi
    rasi_index = int(sun_lon / 30)
    # Sun in Dhanu (index 8) -> Pausha Masa (Pausha month Sun is in Dhanu usually)
    # Sun in Makara (index 9) -> Magha
    # Sun in Meena (index 11) -> Chaitra
    
    masa_mapping = {
        11: 0, # Meena -> Chaitra
        0: 1,  # Mesha -> Vaishakha
        1: 2,  # Vrishabha -> Jyeshtha
        2: 3,  # Mithuna -> Ashadha
        3: 4,  # Karka -> Shravana
        4: 5,  # Simha -> Bhadrapada
        5: 6,  # Kanya -> Ashvin
        6: 7,  # Tula -> Kartika
        7: 8,  # Vrishchika -> Margashirsha
        8: 9,  # Dhanu -> Pausha
        9: 10, # Makara -> Magha
        10: 11 # Kumbha -> Phalguna
    }
    
    masa_name = MASAS[masa_mapping[rasi_index]]
    
    # Samvatsara: Based on the 60-year cycle starting at 1987 (Prabhava)
    samvat_index = (year - 1987) % 60
    
    return masa_name, SAMVATSARAS[samvat_index]
def format_panchanga_report(dt_local, loc_address, loc_timezone, sunrise, sunset, samvatsara, masa, paksha, tithi, vara, nakshatra, yoga, karana):
    report = f"""
       HINDU PANCHANGA REPORT
========================================
Input Date/Time : {dt_local.strftime('%Y-%m-%d %H:%M:%S')} ({loc_timezone})
Location        : {loc_address}
Sunrise         : {sunrise.strftime('%H:%M:%S') if sunrise else 'N/A'}
Sunset          : {sunset.strftime('%H:%M:%S') if sunset else 'N/A'}
----------------------------------------
Samvatsara      : {samvatsara}
Masa (Month)    : {masa}
Paksha          : {paksha}
Tithi           : {tithi}
Vara (Weekday)  : {vara}
Nakshatra       : {nakshatra}
Yoga            : {yoga}
Karana (Index)  : {karana}
========================================
"""
    return report

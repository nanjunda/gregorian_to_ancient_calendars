from data.panchanga_data import *
import math

def calculate_vara(local_time, sunrise_time, lang='EN'):
    """
    Vara (Weekday) starts at Sunrise.
    """
    mapping = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    
    if local_time < sunrise_time:
        weekday = (local_time.weekday() - 1) % 7
    else:
        weekday = local_time.weekday()
        
    return VARAS[lang][mapping[weekday]]

def calculate_tithi(sun_lon, moon_lon, lang='EN'):
    diff = (moon_lon - sun_lon) % 360
    tithi_index = int(diff / 12)
    paksha = PAKSHAS[lang][0] if tithi_index < 15 else PAKSHAS[lang][1]
    return TITHIS[lang][tithi_index], paksha

def calculate_nakshatra(moon_lon, lang='EN'):
    """
    Calculates Nakshatra and Pada.
    """
    nakshatra_index = int(moon_lon / (360/27))
    # Each nakshatra is 13°20' (13.333... degrees)
    # Each pada is 3°20' (3.333... degrees)
    pada = int((moon_lon % (360/27)) / (360/108)) + 1
    
    nak_name = NAKSHATRAS[lang][nakshatra_index]
    star_name = NAKSHATRA_STARS[nakshatra_index]
    
    return f"{nak_name} ({star_name})", pada

def calculate_yoga(sun_lon, moon_lon, lang='EN'):
    yoga_lon = (sun_lon + moon_lon) % 360
    yoga_index = int(yoga_lon / (360/27))
    return YOGAS[lang][yoga_index]

def calculate_karana(sun_lon, moon_lon):
    diff = (moon_lon - sun_lon) % 360
    karana_index = int(diff / 6)
    return karana_index + 1

def calculate_masa_name(sun_lon_at_nm, lang='EN'):
    rasi_index = int(sun_lon_at_nm / 30)
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
    return MASAS[lang][masa_mapping[rasi_index]]

def calculate_masa_samvatsara(year, sun_lon_at_nm, sun_lon_now, lang='EN'):
    masa_name = calculate_masa_name(sun_lon_at_nm, lang)
    samvat_index = (year - 1987) % 60
    return masa_name, SAMVATSARAS[lang][samvat_index]

def format_panchanga_report(dt_local, loc_address, loc_timezone, sunrise, sunset, samvatsara, masa, paksha, tithi, vara, nakshatra, nak_pada, yoga, karana, lang='EN'):
    labels = REPORT_LABELS[lang]
    
    report = f"""
       {labels['title']}
========================================
{labels['input_dt']} : {dt_local.strftime('%Y-%m-%d %H:%M:%S')} ({loc_timezone})
{labels['location']}        : {loc_address}
{labels['sunrise']}         : {sunrise.strftime('%H:%M:%S') if sunrise else 'N/A'}
{labels['sunset']}          : {sunset.strftime('%H:%M:%S') if sunset else 'N/A'}
----------------------------------------
{labels['samvatsara']}      : {samvatsara}
{labels['masa']}    : {masa}
{labels['paksha']}          : {paksha}
{labels['tithi']}           : {tithi}
{labels['vara']}  : {vara}
{labels['nakshatra']}       : {nakshatra} {labels['pada']} {nak_pada}
{labels['yoga']}            : {yoga}
{labels['karana']}  : {karana}
========================================
"""
    return report

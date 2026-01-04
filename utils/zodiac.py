# Zodiac Signs (Rashi) in EN, KN, SA
ZODIAC_SIGNS = {
    0: {"code": "Aries", "name_en": "Aries", "name_kn": "Mesha", "name_sa": "Mesha"},
    1: {"code": "Taurus", "name_en": "Taurus", "name_kn": "Vrishabha", "name_sa": "Vrishabha"},
    2: {"code": "Gemini", "name_en": "Gemini", "name_kn": "Mithuna", "name_sa": "Mithuna"},
    3: {"code": "Cancer", "name_en": "Cancer", "name_kn": "Karkataka", "name_sa": "Karkataka"},
    4: {"code": "Leo", "name_en": "Leo", "name_kn": "Simha", "name_sa": "Simha"},
    5: {"code": "Virgo", "name_en": "Virgo", "name_kn": "Kanya", "name_sa": "Kanya"},
    6: {"code": "Libra", "name_en": "Libra", "name_kn": "Tula", "name_sa": "Tula"},
    7: {"code": "Scorpio", "name_en": "Scorpio", "name_kn": "Vrishchika", "name_sa": "Vrishchika"},
    8: {"code": "Sagittarius", "name_en": "Sagittarius", "name_kn": "Dhanu", "name_sa": "Dhanu"},
    9: {"code": "Capricorn", "name_en": "Capricorn", "name_kn": "Makara", "name_sa": "Makara"},
    10: {"code": "Aquarius", "name_en": "Aquarius", "name_kn": "Kumbha", "name_sa": "Kumbha"},
    11: {"code": "Pisces", "name_en": "Pisces", "name_kn": "Meena", "name_sa": "Meena"}
}

def get_zodiac_name(index, lang="EN"):
    """
    Returns the localized name of the zodiac sign for a given index (0-11)
    with the Western equivalent in brackets.
    """
    sign = ZODIAC_SIGNS.get(index % 12)
    western_name = sign["name_en"]
    
    if lang == "KN":
        vedic_name = sign["name_kn"]
    elif lang == "SA":
        vedic_name = sign["name_sa"]
    else:
        # For EN, we still use the Vedic transliteration as primary if available
        # but here name_en is already the Western name. 
        # Actually, in ZODIAC_SIGNS, name_en is the Western name.
        # Let's adjust to show Vedic translit if possible.
        # Currently RASIS in panchanga_data has Vedic names in English.
        # Let's use that if possible or just stick to the requested format.
        vedic_name = sign["name_sa"] # Use Sanskrit as Vedic base for EN
        
    return f"{vedic_name} ({western_name})"

from datetime import datetime, timedelta
import pytz
from utils.location import get_location_details
from utils.astronomy import get_sidereal_longitude, get_sunrise_sunset, sun, moon, ts

def check_tithi_range():
    location_name = "Narmadapuram, India"
    date_str = "1959-11-17"
    
    loc = get_location_details(location_name)
    local_tz = pytz.timezone(loc["timezone"])
    
    # Check throughout the day
    for hour in range(0, 24):
        dt_local = local_tz.localize(datetime.strptime(f"{date_str} {hour:02d}:00", "%Y-%m-%d %H:%M"))
        dt_utc = dt_local.astimezone(pytz.utc)
        
        sun_lon = get_sidereal_longitude(dt_utc, sun)
        moon_lon = get_sidereal_longitude(dt_utc, moon)
        
        diff = (moon_lon - sun_lon) % 360
        tithi_float = diff / 12.0
        
        print(f"Time: {dt_local.strftime('%H:%M')} | Tithi Float: {tithi_float:.4f}")

if __name__ == "__main__":
    check_tithi_range()

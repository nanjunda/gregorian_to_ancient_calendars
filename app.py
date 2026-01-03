from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz
from utils.location import get_location_details
from panchanga.calculations import (
    calculate_vara, calculate_tithi, calculate_nakshatra, 
    calculate_yoga, calculate_karana, calculate_masa_samvatsara,
    format_panchanga_report
)
from utils.astronomy import get_sidereal_longitude, get_sunrise_sunset, sun, moon, get_previous_new_moon, get_angular_data
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from panchanga.recurrence import find_recurrences
from utils.ical_gen import create_ical_content
from flask import Response, make_response

@app.route('/api/generate-ical', methods=['POST'])
def generate_ical():
    data = request.json
    date_str = data.get('date')
    time_str = data.get('time')
    location_name = data.get('location')
    title = data.get('title', 'Hindu Panchanga Event')
    lang = data.get('lang', 'EN')

    if not all([date_str, time_str, location_name]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # 1. Resolve Location
        loc = get_location_details(location_name)
        
        # 2. Parse DateTime
        dt_str = f"{date_str} {time_str}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(loc["timezone"])
        local_dt = local_tz.localize(naive_dt)

        # 3. Find Recurrences (20 years starting from current year)
        occurrences = find_recurrences(local_dt, loc, num_years=20, lang=lang)
        
        # 4. Generate iCal content
        ical_data = create_ical_content(title, occurrences)
        
        response = make_response(ical_data)
        response.headers["Content-Disposition"] = f"attachment; filename={title.replace(' ', '_')}.ics"
        response.headers["Content-Type"] = "text/calendar"
        
        return response

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/panchanga', methods=['POST'])
def get_panchanga():
    data = request.json
    date_str = data.get('date')
    time_str = data.get('time')
    location_name = data.get('location')
    title = data.get('title', 'Event') # Added title support
    lang = data.get('lang', 'EN')

    if not all([date_str, time_str, location_name]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
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
        from utils.zodiac import get_zodiac_name, ZODIAC_SIGNS
        from utils.astronomy import get_rashi, get_lagna
        
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

        return jsonify({
            "success": True,
            "data": {
                "input_datetime": local_dt.strftime('%Y-%m-%d %H:%M:%S'),
                "timezone": loc["timezone"],
                "address": loc["address"],
                "sunrise": sunrise.strftime('%H:%M:%S') if sunrise else 'N/A',
                "sunset": sunset.strftime('%H:%M:%S') if sunset else 'N/A',
                "samvatsara": samvatsara,
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
                "report": report
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

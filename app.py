from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz
from utils.location import get_location_details
from utils.astronomy import get_sidereal_longitude, get_sunrise_sunset, sun, moon
from panchanga.calculations import (
    calculate_vara, calculate_tithi, calculate_nakshatra, 
    calculate_yoga, calculate_karana, calculate_masa_samvatsara
)
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

        # 3. Find Recurrences (10 years)
        occurrences = find_recurrences(local_dt, loc, num_years=10)
        
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
        
        # 4. Calculate Panchanga Elements
        vara = calculate_vara(local_dt, sunrise)
        tithi, paksha = calculate_tithi(sun_lon, moon_lon)
        nakshatra = calculate_nakshatra(moon_lon)
        yoga = calculate_yoga(sun_lon, moon_lon)
        karana_num = calculate_karana(sun_lon, moon_lon)
        masa, samvatsara = calculate_masa_samvatsara(local_dt.year, sun_lon)

        report = format_panchanga_report(
            local_dt, loc["address"], loc["timezone"],
            sunrise, sunset, samvatsara, masa, paksha, tithi,
            vara, nakshatra, yoga, karana_num
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
                "nakshatra": nakshatra,
                "yoga": yoga,
                "karana": karana_num,
                "report": report
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

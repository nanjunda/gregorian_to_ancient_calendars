import warnings
# Suppress Python 3.9 FutureWarnings from Google Auth
warnings.filterwarnings("ignore", category=FutureWarning)

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
import base64
from utils.ai_engine import ai_engine

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from panchanga.recurrence import find_recurrences
from utils.ical_gen import create_ical_content
from utils.skyshot import generate_skymap, get_cache_key, get_cached_image, CACHE_DIR
from utils.solar_system import generate_solar_system, get_cache_key as get_solar_cache_key, get_cached_image as get_solar_cached_image, CACHE_DIR as SOLAR_CACHE_DIR
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

        # 3. Find Recurrences (Exactly next 20 entries)
        occurrences = find_recurrences(local_dt, loc, num_entries=20, lang=lang)
        
        # 4. Generate iCal content
        ical_data = create_ical_content(title, occurrences)
        
        response = make_response(ical_data)
        response.headers["Content-Disposition"] = f"attachment; filename={title.replace(' ', '_')}.ics"
        response.headers["Content-Type"] = "text/calendar"
        
        return response

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/skyshot', methods=['POST'])
def get_skyshot():
    """
    Generate or retrieve a cached sky map image showing Moon position.
    """
    data = request.json
    date_str = data.get('date')
    time_str = data.get('time')
    location_name = data.get('location')
    title = data.get('title', '')
    
    if not all([date_str, time_str, location_name]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    try:
        # 1. Resolve location
        loc = get_location_details(location_name)
        
        # 2. Check cache first
        cache_key = get_cache_key(date_str, time_str, loc["latitude"], loc["longitude"])
        cached_path = get_cached_image(cache_key)
        
        if cached_path:
            with open(cached_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return jsonify({
                "success": True,
                "image_data": f"data:image/png;base64,{encoded_string}",
                "cached": True
            })
        
        # 3. Parse DateTime and calculate astronomical data
        dt_str = f"{date_str} {time_str}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(loc["timezone"])
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)
        
        # 4. Get Moon position and angular data
        moon_lon = get_sidereal_longitude(utc_dt, moon)
        angular_data = get_angular_data(local_dt, loc["latitude"], loc["longitude"], loc["timezone"])
        
        # 5. Get Nakshatra info
        nakshatra, nak_pada = calculate_nakshatra(moon_lon, lang='EN')
        
        # 6. Generate sky map
        output_path = str(CACHE_DIR / f"{cache_key}.png")
        generate_skymap(
            moon_longitude=moon_lon,
            nakshatra_name=nakshatra,
            nakshatra_pada=nak_pada,
            phase_angle=angular_data["phase_angle"],
            output_path=output_path,
            event_title=title if title else None,
            rahu_longitude=angular_data["rahu_sidereal"],
            ketu_longitude=angular_data["ketu_sidereal"]
        )
        
        # 7. Convert to Base64 for privacy (No public URL)
        with open(output_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        return jsonify({
            "success": True,
            "image_data": f"data:image/png;base64,{encoded_string}",
            "cached": False,
            "nakshatra": nakshatra,
            "moon_longitude": round(moon_lon, 2),
            "rahu_longitude": round(angular_data["rahu_sidereal"], 2),
            "ketu_longitude": round(angular_data["ketu_sidereal"], 2)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/solar-system', methods=['POST'])
def get_solar_system():
    """
    Generate or retrieve a cached heliocentric solar system view.
    """
    data = request.json
    date_str = data.get('date')
    time_str = data.get('time')
    location_name = data.get('location')
    title = data.get('title', '')
    
    if not all([date_str, time_str, location_name]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    try:
        # 1. Resolve location (needed to get timezone for UTC conversion)
        loc = get_location_details(location_name)
        
        # 2. Check cache (heliocentric view only depends on date/time)
        cache_key = get_solar_cache_key(date_str, time_str)
        cached_path = get_solar_cached_image(cache_key)
        
        if cached_path:
            with open(cached_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return jsonify({
                "success": True,
                "image_data": f"data:image/png;base64,{encoded_string}",
                "cached": True
            })
        
        # 3. Get UTC time
        dt_str = f"{date_str} {time_str}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(loc["timezone"])
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.utc)
        
        # 4. Generate Solar System view
        output_path = str(SOLAR_CACHE_DIR / f"{cache_key}.png")
        generate_solar_system(
            utc_dt=utc_dt,
            output_path=output_path,
            event_title=title if title else None
        )
        
        # 5. Convert to Base64 for privacy (No public URL)
        with open(output_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        return jsonify({
            "success": True,
            "image_data": f"data:image/png;base64,{encoded_string}",
            "cached": False
        })
        
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

        # 6. Calculate Next Birthday (Feature v4.1)
        next_bdays = find_recurrences(local_dt, loc, num_entries=1, lang=lang)
        next_bday = next_bdays[0]["datetime"].strftime('%A, %B %d, %Y') if next_bdays else "N/A"

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
                "next_birthday": next_bday,
                "report": report
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/explore')
def explore():
    """
    Serve the educational 'Cosmic Explorer' flyer page.
    """
    return render_template('flyer.html')

@app.route('/guide')
def guide():
    """
    Serve the interactive HTML Student Guide.
    """
    return render_template('guide.html')

@app.route('/visuals/lunar-nodes')
def lunar_nodes_visual():
    """
    Serve the 3D Lunar Nodes interactive visualization.
    """
    return render_template('lunar_nodes_visual.html')

@app.route('/visuals/zodiac')
def zodiac_visual():
    """
    Serve the 3D Zodiac Stadium visualization.
    """
    return render_template('zodiac_visual.html')

@app.route('/visuals/zodiac-comparison')
def zodiac_comparison():
    """
    Serve the 3D Dual-Ring Zodiac Comparison (Western vs Hindu).
    """
    return render_template('zodiac_comparison_visual.html')

@app.route('/visuals/moon-phase')
def moon_phase_visual():
    """
    Serve the interactive Sun-Moon Angle / Tithi calculator.
    """
    return render_template('moon_phase_visual.html')

@app.route('/visuals/constellations')
def constellations_visual():
    """
    Serve the focused 3D constellation/nakshatra map.
    """
    return render_template('constellations_visual.html')

@app.route('/visuals/precession')
def precession_visual():
    """
    Serve the 3D Precession visualization.
    """
    return render_template('precession_visual.html')

@app.route('/api/ai-explain', methods=['POST'])
def ai_explain():
    """
    Generate AI-powered insights (Markdown + Audio Summary).
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data received."}), 400
            
        raw_output = ai_engine.get_explanation(data)
        
        # Parse the JSON from AI
        import json
        try:
            # Handle potential markdown wrapping from AI
            clean_json = raw_output.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(clean_json)
            return jsonify({
                "success": True,
                "insight": parsed.get('insight', raw_output),
                "audio_summary": parsed.get('audio_summary', "The stars are telling a complex story. Let's look at the details below.")
            })
        except Exception as json_err:
            print(f"AI JSON Parse Error: {json_err}. Raw: {raw_output[:200]}")
            # Fallback if AI didn't return valid JSON
            return jsonify({
                "success": True,
                "insight": raw_output,
                "audio_summary": "I've analyzed your celestial alignment. Here is the full report."
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """
    Handle questions from students about the current cosmic alignment.
    """
    try:
        data = request.get_json()
        message = data.get('message')
        context = data.get('context', {}) # Contains Tithi, Nakshatra etc.

        if not message:
            return jsonify({"success": False, "error": "Missing message"}), 400
            
        response = ai_engine.chat_with_tutor(message, context)
        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/insights', methods=['GET', 'POST'], strict_slashes=False)
def insights_page():
    """
    Serve the deep insights page. Can receive configuration via POST for reliability.
    """
    data = None
    if request.method == 'POST':
        try:
            # Check if it's a form or JSON
            if request.is_json:
                data = request.json
            else:
                import json
                data_str = request.form.get('panchanga_data')
                if data_str:
                    data = json.loads(data_str)
        except Exception as e:
            print(f"Error parsing insights POST data: {e}")
    
    return render_template('insights.html', initial_data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5080, debug=True)

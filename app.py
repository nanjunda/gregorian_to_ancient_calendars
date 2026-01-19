import warnings
# Suppress Python 3.9 FutureWarnings from Google Auth
warnings.filterwarnings("ignore", category=FutureWarning)

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz
from utils.location import get_location_details
from panchanga.calculations import calculate_nakshatra
from utils.astronomy import get_sidereal_longitude, get_angular_data, sun, moon
from engines.factory import EngineFactory
import os
import base64
from utils.ai_engine import ai_engine
import traceback

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
        # Resolve engine (defaults to panchanga for this legacy route)
        engine = EngineFactory.get_engine("panchanga")
        
        # Calculate data using the verified modular engine
        result_data = engine.calculate_data(date_str, time_str, location_name, lang=lang)

        return jsonify({
            "success": True,
            "data": result_data
        })

    except Exception as e:
        print(f"Error in get_panchanga: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

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

@app.route('/visuals/samvatsara')
def samvatsara_visual():
    """
    Serve the 3D Jupiter-Saturn Samvatsara resonance visual.
    """
    return render_template('samvatsara_visual.html')

@app.route('/api/ai-explain', methods=['POST'])
def ai_explain():
    """
    Generate AI-powered insights (Markdown + Audio Summary).
    """
    try:
        print("DEBUG: Received AI Explain Request", flush=True)
        data = request.get_json()
        if not data:
            print("DEBUG: No data in AI Explain request", flush=True)
            return jsonify({"success": False, "error": "No data received."}), 400
            
        print("DEBUG: Calling AI Engine for Explanation...", flush=True)
        raw_output = ai_engine.get_explanation(data)
        print(f"DEBUG: AI Explain Response Length: {len(raw_output)}", flush=True)
        
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
        print(f"DEBUG: CRITICAL ERROR in /api/ai-explain: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({"success": False, "error": str(e)}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """
    Handle questions from students about the current cosmic alignment.
    """
    try:
        print("DEBUG: Received AI Chat Request", flush=True) # Debug Print
        data = request.get_json()
        print(f"DEBUG: Request Data: {data}", flush=True) # Debug Print
        message = data.get('message')
        context = data.get('context', {}) # Contains Tithi, Nakshatra etc.

        if not message:
            print("DEBUG: No message found in request", flush=True) # Debug Print
            return jsonify({"success": False, "error": "Missing message"}), 400
            
        print("DEBUG: Calling AI Engine...", flush=True) # Debug Print
        response = ai_engine.chat_with_tutor(message, context)
        print(f"DEBUG: AI Response Length: {len(response)}", flush=True) # Debug Print
        
        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        print(f"DEBUG: CRITICAL ERROR in /api/ai-chat: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
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

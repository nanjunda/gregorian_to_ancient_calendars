import warnings
# Suppress Python 3.9 FutureWarnings from Google Auth
warnings.filterwarnings("ignore", category=FutureWarning)

from flask import Flask, render_template, request, jsonify, Response, make_response
from datetime import datetime
import pytz
from engines.factory import EngineFactory
import os
import base64
from utils.ai_engine import ai_engine
import traceback
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
        # Resolve engine
        engine = EngineFactory.get_engine("panchanga")
        
        # Generate iCal using the engine (Logic moved to spoke)
        ical_data = engine.generate_ical(date_str, time_str, location_name, title, lang)
        
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
        # Resolve engine
        engine = EngineFactory.get_engine("panchanga")
        
        # Get rich visuals from engine
        visuals = engine.get_rich_visuals(date_str, time_str, location_name, title)
        
        return jsonify({
            "success": True,
            "image_data": visuals.get("skyshot"),
            "cached": "N/A" # Cache management is now internal to Engine
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
        # Resolve engine
        engine = EngineFactory.get_engine("panchanga")
        
        # Get rich visuals from engine
        visuals = engine.get_rich_visuals(date_str, time_str, location_name, title)
        
        return jsonify({
            "success": True,
            "image_data": visuals.get("solar_system"),
            "cached": "N/A"
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

# ==============================================================================
# API v2 - HEADLESS UNIFIED ENDPOINTS
# ==============================================================================

@app.route('/api/v2/calculate', methods=['POST'])
def api_v2_calculate():
    """
    Unified Headless API for Ancient Calendars v2.0.
    Follows the Contract defined in docs/api_contract_v2.md
    """
    input_data = request.json
    calendar_type = input_data.get('calendar', 'panchanga')
    date_str = input_data.get('date')
    time_str = input_data.get('time')
    location_name = input_data.get('location')
    lang = input_data.get('lang', 'EN')
    title = input_data.get('title', 'Event')
    client_profile = input_data.get('client_profile', {})

    if not all([date_str, time_str, location_name]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        # 1. Get appropriate engine
        engine = EngineFactory.get_engine(calendar_type)
        
        # 2. Perform raw calculation (Proven logic)
        raw_results = engine.calculate_data(date_str, time_str, location_name, lang=lang)
        
        # 3. Get metadata and AI context
        visual_configs = engine.get_visual_configs(raw_results)
        ai_context = engine.get_ai_context(raw_results)
        
        # 4. Generate Rich Visuals (Skyshot, Solar) - New v2.0 capability
        rich_visuals = engine.get_rich_visuals(date_str, time_str, location_name, title)

        # 5. Construct v2.0 Response (The Contract)
        response = {
            "status": "success",
            "metadata": {
                "civilization": calendar_type,
                "engine_version": "2.0",
                "timestamp_utc": datetime.now(pytz.utc).isoformat(),
                "render_hints": visual_configs.get("modules", [])
            },
            "results": {
                "civilization_specific": {
                    "samvatsara": raw_results.get("samvatsara"),
                    "masa": raw_results.get("masa"),
                    "paksha": raw_results.get("paksha"),
                    "tithi": raw_results.get("tithi"),
                    "vara": raw_results.get("vara"),
                    "nakshatra": raw_results.get("nakshatra"),
                    "yoga": raw_results.get("yoga"),
                    "karana": raw_results.get("karana"),
                    "saka_year": raw_results.get("saka_year")
                },
                "coordinates": {
                    "rashi": raw_results.get("rashi"),
                    "lagna": raw_results.get("lagna")
                },
                "astronomy": {
                    "sunrise": raw_results.get("sunrise"),
                    "sunset": raw_results.get("sunset"),
                    "angular_data": raw_results.get("angular_data"),
                    "next_birthday": raw_results.get("next_birthday")
                }
            },
            "visuals": {
                "sky_shot_base64": rich_visuals.get("skyshot"),
                "solar_system_base64": rich_visuals.get("solar_system")
            },
            "education": {
                "summary": f"Calculated {calendar_type.capitalize()} alignment for {date_str}.",
                "report_manual": raw_results.get("report")
            }
        }

        return jsonify(response)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/v2/ai-explain', methods=['POST'])
def api_v2_ai_explain():
    """
    Headless AI Explanation for v2.0.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data received."}), 400
            
        raw_output = ai_engine.get_explanation(data)
        
        # Clean potential JSON wrapping from AI
        clean_markdown = raw_output.replace('```json', '').replace('```', '').strip()
        
        return jsonify({
            "status": "success",
            "metadata": { "engine": ai_engine.provider },
            "education": {
                "format": "markdown",
                "content": clean_markdown
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v2/ai-chat', methods=['POST'])
def api_v2_ai_chat():
    """
    Headless AI Chat for v2.0.
    """
    try:
        data = request.get_json()
        message = data.get('message')
        context = data.get('context', {})

        if not message:
            return jsonify({"status": "error", "message": "Missing message"}), 400
            
        response = ai_engine.chat_with_tutor(message, context)
        
        return jsonify({
            "status": "success",
            "response": response
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

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

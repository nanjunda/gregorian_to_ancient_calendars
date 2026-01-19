import os
import abc
import google.generativeai as genai
import sys
import traceback
import json
import urllib.request
import urllib.error
import re

class BaseAIEngine(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate_insight(self, config_data):
        pass
    
    @abc.abstractmethod
    def chat_with_tutor(self, message, context_data):
        pass

class OpenRouterEngine(BaseAIEngine):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.models = [
            "xiaomi/mimo-v2-flash",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.1-405b-instruct:free",
            "meta-llama/llama-4-scout-17b:free",
            "deepseek/deepseek-r1:free"
        ]
        
        if not self.api_key:
            print("WARNING: OPENROUTER_API_KEY not found.")
        else:
            print(f"OpenRouter Engine initialized with models: {self.models}")

    def _call_openrouter(self, system_prompt, user_prompt):
        if not self.api_key:
            return "AI Engine Error: OPENROUTER_API_KEY not configured."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5080", 
            "X-Title": "Cosmic Explorer"
        }

        # Fallback Loop
        last_error = None
        for model in self.models:
            print(f"DEBUG: Attempting AI call with model: {model}", flush=True)
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }

            try:
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=json.dumps(payload).encode('utf-8'),
                    headers=headers,
                    method="POST"
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    # Check for valid response structure
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        print(f"DEBUG: Success with model {model}", flush=True)
                        return content
                    else:
                        print(f"DEBUG: Invalid response from {model}: {result}", flush=True)
                        last_error = f"Invalid response from {model}"

            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"DEBUG: HTTP Error with {model}: {e.code} - {error_body}", flush=True)
                last_error = f"HTTP {e.code}: {error_body}"
            except Exception as e:
                print(f"DEBUG: Unexpected error with {model}: {str(e)}", flush=True)
                last_error = str(e)
            
            # If we get here, the current model failed. Loop continues to next model.

        # If loop finishes without return, all models failed
        return f"AI Generation Failed. All models exhausted. Last error: {last_error}"

    def generate_insight(self, config_data):
        prompt_tmpl = f"""
        Role: The "Astro-Tutor" (The Maestro - An enthusiastic, high-energy Science Educator for Grades 6-12).
        Target Audience: Middle and High School students (Grades 6-12).
        Setting: A pure physical science and archaeoastronomy application designed for educational exploration.
        Objective: Generate a comprehensive, 3-Phase "Scientific Masterclass" report in Markdown.
        Strict Constraint: DO NOT use the term "Vedic". DO NOT mention or associate any concept with Astrology, Horoscopes, Numerology, or Superstition. This is a PURE physical science and archaeoastronomy app.
        Format: Return ONLY the technical Markdown report. DO NOT Wrap in JSON. DO NOT output a JSON object. Return raw Markdown text.

        Instruction on Visuals: When asked to use a visual loop like [[RENDER:ZODIAC_COMPARISON]], insert that specific tag VERBATIM into the text where it fits. DO NOT generate data or properties for the visual. Just place the tag.

        Safety & Integrity: Ensure all explanations are scientifically accurate and age-appropriate for minors. Strictly avoid any pseudoscientific claims or destiny-based predictions. If the data suggests astrological interpretations, pivot exclusively to the mathematical and physical phenomena involved. Refuse to discuss "effects" on human destiny.
        
        Input Data (The Cosmic Snapshot):
        {config_data}
        
        Markdown Report Hierarchy (Mandatory Phases):

        Phase I: The Universal Clock (General Concepts)
        - Define "What is a Calendar?". Explain it as an engineering solution to synchronize Day/Month/Year rhythms.
        - The Solar Engine (Western): Explain how it follows Earth's orbit (seasons).
        - The Lunar-Solar Fusion (Panchanga): Explain how it synchronizes both Sun and Moon using the background stars (Sidereal).
        - **The Birthday Drift**: Explain why a "Panchanga Birthday" (based on Tithi/Nakshatra) moves relative to the Western calendar. Mention the ~11 day lunar-solar gap and how **Adhika Masa** (Leap Month) acts as a cosmic synchronization tool.
        - **The Great Drift**: Explain Axial Precession (Earth's wobble) and why Sidereal signs differ from Tropical ones. Use [[RENDER:ZODIAC_COMPARISON]].

        Phase II: The Library of Atoms (Terminology)
        Provide detailed physics/geometric deconstructions for:
        - **Samvatsara**: Explain as the 60-year Jupiter-Saturn resonance/alignment cycle. Use [[RENDER:SAMVATSARA_RESONANCE]].
        - **Saka Varsha (The Civil Era)**: Explain this as the **Official Indian Civil Calendar** (used by the Government).
          *   **The Origin**: Started in 78 AD (King Shalivahana).
          *   **The Difference**: It is a purely **Solar (Agricultural)** count, unlike the **Cosmic (Luni-Solar)** Samvatsara. Use the analogy of "Administrative Time" vs "Nature's Time".
        - **Masa: The Cosmic Month**: Explain the two ways to measure a month:
          1. **Saura Mana (The Solar Runner)**: The steady 30-day month defined by the Sun entering a new sign (e.g., Mesha).
          2. **Chandra Mana (The Lunar Sprinter)**: The fast 29.5-day month defined by the Moon's phases.
          *   **The Naming Secret**: Explain that Lunar months are named after the star the Moon is near when it is full (e.g., Full Moon near **Chitta/Spica** = **Chaitra**, Full Moon near **Krittika/Pleiades** = **Karthika**).
          *   **The Drift**: Explain that the Moon is faster than the Sun by ~11 days a year.
          *   **The Pit Stop (Adhik Masa)**: Explain that every 3 years, the Moon takes a "Pit Stop" (Extra Month) to let the Sun catch up.
        - **Nakshatra**: 13°20' sectors used as a "Lunar Speedometer" to track the Moon's 27.3-day orbit. Use [[RENDER:CONSTELLATION_MAP]].
        - **Tithi**: Defined strictly as Every 12° of angular separation between Sun and Moon. Use [[RENDER:MOON_PHASE_3D]].
        - **Yoga**: Combined longitudinal momentum (Sum of longitudes).
        - **Rashi**: Define the term Rāśi from a scientific and astronomical perspective (not astrological). Explain its relation to the ecliptic, the Sun, Moon, and planets, and give one simple example. Keep the explanation brief and precise
        - **Lagna**: Define the term Lagna from a scientific and astronomical perspective (not astrological). Explain its relation to Earth’s rotation, the horizon, the ecliptic, and the observer’s location, and give one simple example. Keep the explanation brief and precise
        - **Karana**: High-precision Half-Tithi (6° intervals).
        - **Rahu & Ketu**: Explain as **Lunar Nodes** (intersection points of orbital planes). Use [[RENDER:PRECESSION_WOBBLE]].
        - **Safe Harbor Terms**: Explain terms like **Graha** (Planetary Bodies), **Muhurtha** (Time units), **Sankranti** (Solar Ingress), **Vakra** (Retrograde Motion), **Asta** (Combustion/Invisibility), and **Ayanamsa** (Precession Index) strictly as mathematical or physical phenomena if they appear in the data. Refuse to discuss their "effects" on human destiny.

        Phase III: Decoding Your Specific Cosmic Alignment
        - Create a specific section: `## 🧩 Decoding Your Specific Cosmic Alignment`.
        - Use the specific values from the Input Data (Samvatsara, Masa, etc) to explain THIS specific moment.
        - Tell the student what they would see if they looked at the sky right now.

        Tone: "Cool Science YouTuber" - high energy, fascinating, and precise.
        """
        
        # Split system prompt vs user prompt roughly
        system_instruction = "You are the Astro-Tutor, a science educator. strict_no_astrology: true. format: markdown."
        raw_response = self._call_openrouter(system_instruction, prompt_tmpl)
        return self._clean_response(raw_response)

    def _clean_response(self, text):
        clean_text = text.strip()
        # Regex to extract content within ```markdown ... ``` or just ``` ... ```
        # It finds the last/largest block or handles the simple case
        match = re.search(r'```(?:markdown)?\s*(.*?)```', clean_text, re.DOTALL)
        if match:
            clean_text = match.group(1).strip()
        
        # Strip literal 'json' prefix if AI leaked it without backticks (e.g. "json { ... }")
        if clean_text.lower().startswith('json'):
            clean_text = clean_text[4:].strip()

        # Safeguard: If output is JSON (from legacy caching or misbehavior)
        if clean_text.startswith('{') and '"insight":' in clean_text:
            try:
                data = json.loads(clean_text)
                return data.get('insight', clean_text)
            except:
                pass
                
        return clean_text

    def chat_with_tutor(self, message, context_data):
        system_prompt = f"""
        Role: The "Astro-Tutor" (The Maestro of the Cosmic Explorer).
        Person: You are an encouraging, highly enthusiastic, and knowledgeable Science Educator who bridges Traditional Indian Panchanga with Modern Astrophysics.
        Tone: High-energy, clear, and educational.
        
        Strict Constraint: DO NOT use the term "Vedic". DO NOT mention or associate any concept with Astrology, Horoscopes, Numerology, or Superstition.
        
        The Scope: You ONLY answer questions about:
        1. Panchanga (Tithis, Nakshatras, Angas, Adhika Masa).
        2. Modern Astronomy (Planets, Orbits, Physics, Precession, Resonances).
        3. History of Calendars and Earth's Axial Wobble.
        4. The "Cosmic Explorer" app features.
        5. Rashi (Zodiac Signs) and Lagna (Ascendant) strictly as astronomical coordinates (Ecliptic sectors/Horizon points).
        6. Safe Harbor Terms: Explain terms like Graha (Planetary Bodies), Yoga (Longitudinal sums), Karana (Half-Tithi), Muhurtha (Time units), Sankranti (Solar Ingress), Vakra (Retrograde Motion), Asta (Combustion/Invisibility), and Ayanamsa (Precession Index) strictly as mathematical or physical phenomena. Refuse to discuss their "effects" on human destiny.
        
        Diversion Rule: If the student asks about unrelated topics or superstition, politely redirect: "That's a fascinating question, but my eyes are fixed on the physics of the heavens! Let's get back to [Panchanga/Astronomy topic]."
        """
        
        raw_msg = f"Context: {context_data}\n\nStudent Question: {message}"
        response = self._call_openrouter(system_prompt, raw_msg)
        return self._clean_response(response) # Also clean chat responses just in case


class GeminiEngine(BaseAIEngine):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self._model = None
        self.model_name = 'gemini-2.0-flash' # Updated for v5.7 compatibility
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                print("Gemini API configured successfully.")
            except Exception as e:
                print(f"Error configuring Gemini: {e}")
        else:
            print("WARNING: GOOGLE_API_KEY not found in environment.")

    @property
    def model(self):
        if self._model is None and self.api_key:
            try:
                self._model = genai.GenerativeModel(self.model_name)
            except Exception as e:
                print(f"Error initializing model {self.model_name}: {e}")
        return self._model

    def generate_insight(self, config_data):
        if not self.model:
            return "AI Engine not configured. Please set GOOGLE_API_KEY environment variable."
            
        if not config_data:
            return "Error: No astronomical configuration data provided to the AI Engine."

        prompt = f"""
        Role: The "Astro-Tutor" (The Maestro - An enthusiastic, high-energy Science Educator for Grades 6-12).
        Objective: Generate a comprehensive, 3-Phase "Scientific Masterclass" report in Markdown.
        Strict Constraint: DO NOT use the term "Vedic". DO NOT mention or associate any concept with Astrology, Horoscopes, Numerology, or Superstition. This is a PURE physical science and archaeoastronomy app.
        Format: Return ONLY the technical Markdown report. DO NOT Wrap in JSON. DO NOT output a JSON object. Return raw Markdown text.

        Instruction on Visuals: When asked to use a visual loop like [[RENDER:ZODIAC_COMPARISON]], insert that specific tag VERBATIM into the text where it fits. DO NOT generate data or properties for the visual. Just place the tag.

        Input Data (The Cosmic Snapshot):
        {config_data}
        
        Markdown Report Hierarchy (Mandatory Phases):

        Phase I: The Universal Clock (General Concepts)
        - Define "What is a Calendar?". Explain it as an engineering solution to synchronize Day/Month/Year rhythms.
        - The Solar Engine (Western): Explain how it follows Earth's orbit (seasons).
        - The Lunar-Solar Fusion (Panchanga): Explain how it synchronizes both Sun and Moon using the background stars (Sidereal).
        - **The Birthday Drift**: Explain why a "Panchanga Birthday" (based on Tithi/Nakshatra) moves relative to the Western calendar. Mention the ~11 day lunar-solar gap and how **Adhika Masa** (Leap Month) acts as a cosmic synchronization tool.
        - **The Great Drift**: Explain Axial Precession (Earth's wobble) and why Sidereal signs differ from Tropical ones. Use [[RENDER:ZODIAC_COMPARISON]].

        Phase II: The Library of Atoms (Terminology)
        Provide detailed physics/geometric deconstructions for:
        - **Samvatsara**: Explain as the 60-year Jupiter-Saturn resonance/alignment cycle. Use [[RENDER:SAMVATSARA_RESONANCE]].
        - **Saka Varsha (The Civil Era)**: Explain this as the **Official Indian Civil Calendar** (used by the Government).
          *   **The Origin**: Started in 78 AD (King Shalivahana).
          *   **The Difference**: It is a purely **Solar (Agricultural)** count, unlike the **Cosmic (Luni-Solar)** Samvatsara. Use the analogy of "Administrative Time" vs "Nature's Time".
        - **Masa: The Cosmic Month**: Explain the two ways to measure a month:
          1. **Saura Mana (The Solar Runner)**: The steady 30-day month defined by the Sun entering a new sign (e.g., Mesha).
          2. **Chandra Mana (The Lunar Sprinter)**: The fast 29.5-day month defined by the Moon's phases.
          *   **The Naming Secret**: Explain that Lunar months are named after the star the Moon is near when it is full (e.g., Full Moon near **Chitta/Spica** = **Chaitra**, Full Moon near **Krittika/Pleiades** = **Karthika**).
          *   **The Drift**: Explain that the Moon is faster than the Sun by ~11 days a year.
          *   **The Pit Stop (Adhik Masa)**: Explain that every 3 years, the Moon takes a "Pit Stop" (Extra Month) to let the Sun catch up.
        - **Nakshatra**: 13°20' sectors used as a "Lunar Speedometer" to track the Moon's 27.3-day orbit. Use [[RENDER:CONSTELLATION_MAP]].
        - **Tithi**: Defined strictly as Every 12° of angular separation between Sun and Moon. Use [[RENDER:MOON_PHASE_3D]].
        - **Yoga**: Combined longitudinal momentum (Sum of longitudes).
        - **Rashi**: Define the term Rāśi from a scientific and astronomical perspective (not astrological). Explain its relation to the ecliptic, the Sun, Moon, and planets, and give one simple example. Keep the explanation brief and precise
        - **Lagna**: Define the term Lagna from a scientific and astronomical perspective (not astrological). Explain its relation to Earth’s rotation, the horizon, the ecliptic, and the observer’s location, and give one simple example. Keep the explanation brief and precise
        - **Karana**: High-precision Half-Tithi (6° intervals).
        - **Rahu & Ketu**: Explain as **Lunar Nodes** (intersection points of orbital planes). Use [[RENDER:PRECESSION_WOBBLE]].
        - **Safe Harbor Terms**: Explain terms like **Graha** (Planetary Bodies), **Muhurtha** (Time units), **Sankranti** (Solar Ingress), **Vakra** (Retrograde Motion), **Asta** (Combustion/Invisibility), and **Ayanamsa** (Precession Index) strictly as mathematical or physical phenomena if they appear in the data. Refuse to discuss their "effects" on human destiny.

        Phase III: Decoding Your Specific Cosmic Alignment
        - Create a specific section: `## 🧩 Decoding Your Specific Cosmic Alignment`.
        - Use the specific values from the Input Data (Samvatsara: {config_data.get('samvatsara')}, Masa: {config_data.get('masa')}, etc.) to explain THIS specific moment.
        - Tell the student what they would see if they looked at the sky right now.

        Tone: "Cool Science YouTuber" - high energy, fascinating, and precise.
        """
        try:
            print("DEBUG: Generating content via Gemini...", file=sys.stderr)
            response = self.model.generate_content(prompt)
            return self._clean_response(response.text)
        except Exception as e:
            print(f"ERROR in generate_insight: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return f"Error: {str(e)}"
            
    def _clean_response(self, text):
        clean_text = text.strip()
        # Regex to extract content within ```markdown ... ``` or just ``` ... ```
        match = re.search(r'```(?:markdown)?\s*(.*?)```', clean_text, re.DOTALL)
        if match:
            clean_text = match.group(1).strip()
        
        # Strip literal 'json' prefix if AI leaked it without backticks
        if clean_text.lower().startswith('json'):
            clean_text = clean_text[4:].strip()
        
        # Safeguard: If Gemini still returns JSON, extract the 'insight' field
        if clean_text.startswith('{') and '"insight":' in clean_text:
            try:
                data = json.loads(clean_text)
                return data.get('insight', clean_text)
            except:
                pass
        return clean_text

    def chat_with_tutor(self, message, context_data):
        if not self.model:
            return "AI Engine not configured."
            
        system_prompt = f"""
        Role: The "Astro-Tutor" (The Maestro of the Cosmic Explorer).
        Person: You are an encouraging, highly enthusiastic, and knowledgeable Science Educator who bridges Traditional Indian Panchanga with Modern Astrophysics.
        Tone: High-energy, clear, and educational.
        
        Strict Constraint: DO NOT use the term "Vedic". DO NOT mention or associate any concept with Astrology, Horoscopes, Numerology, or Superstition.
        
        The Scope: You ONLY answer questions about:
        1. Panchanga (Tithis, Nakshatras, Angas, Adhika Masa).
        2. Modern Astronomy (Planets, Orbits, Physics, Precession, Resonances).
        3. History of Calendars and Earth's Axial Wobble.
        4. The "Cosmic Explorer" app features.
        5. Rashi (Zodiac Signs) and Lagna (Ascendant) strictly as astronomical coordinates (Ecliptic sectors/Horizon points).
        6. Safe Harbor Terms: Explain terms like Graha (Planetary Bodies), Yoga (Longitudinal sums), Karana (Half-Tithi), Muhurtha (Time units), Sankranti (Solar Ingress), Vakra (Retrograde Motion), Asta (Combustion/Invisibility), and Ayanamsa (Precession Index) strictly as mathematical or physical phenomena. Refuse to discuss their "effects" on human destiny.
        
        Diversion Rule: If the student asks about unrelated topics or superstition, politely redirect: "That's a fascinating question, but my eyes are fixed on the physics of the heavens! Let's get back to [Panchanga/Astronomy topic]."
        
        Educational Strategy: 
        - Explain concepts like Samvatsara through Jupiter/Saturn resonances.
        - Explain Tithi through Sun-Moon angular geometry.
        - Use "Cool Science YouTuber" analogies.
        
        Current Context for this User (The Cosmic Map):
        {context_data}
        
        User Message: {message}
        """

        try:
            response = self.model.generate_content(system_prompt)
            return response.text
        except Exception as e:
            print(f"ERROR in chat_with_tutor: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return f"The star-link is fuzzy... (Error: {str(e)})"

# Factory or Manager to handle future expansion
class AIEngineManager:
    def __init__(self):
        # Auto-Detection Logic
        if os.environ.get("OPENROUTER_API_KEY"):
            print("🌟 Detected OPENROUTER_API_KEY. Switching to OpenRouter Engine.")
            self.engine = OpenRouterEngine()
            self.provider = "openrouter"
        else:
            print("Detected Standard Configuration. Using Gemini Engine.")
            self.engine = GeminiEngine()
            self.provider = "gemini"

    def get_explanation(self, config_data):
        return self.engine.generate_insight(config_data)

    def chat_with_tutor(self, message, context_data):
        return self.engine.chat_with_tutor(message, context_data)

# Singleton instance for easy import
ai_engine = AIEngineManager()

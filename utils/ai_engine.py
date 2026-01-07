import os
import abc
import google.generativeai as genai

class BaseAIEngine(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate_insight(self, config_data):
        pass

class GeminiEngine(BaseAIEngine):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self._model = None
        self.model_name = 'gemini-1.5-flash' # Reverting to most stable known ID
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

        # Extracting data for the prompt
        samvatsara = config_data.get('samvatsara')
        masa = config_data.get('masa')
        paksha = config_data.get('paksha')
        tithi = config_data.get('tithi')
        nakshatra = config_data.get('nakshatra')
        yoga = config_data.get('yoga')
        location = config_data.get('address')
        input_dt = config_data.get('input_datetime')
        
        # Defensive extraction for rashi (it might be None or missing)
        rashi_obj = config_data.get('rashi')
        rashi = "N/A"
        if isinstance(rashi_obj, dict):
            rashi = rashi_obj.get('name', 'N/A')
        
        # Ayanamsa is usually around 24 degrees in this era
        ayanamsa = "approx. 24.1°"
        
        # Split datetime if possible for cleaner prompt
        date_part, time_part = "N/A", "N/A"
        if input_dt and ' ' in input_dt:
            date_part, time_part = input_dt.split(' ', 1)
        elif input_dt:
            date_part = input_dt

        prompt = f"""
        Role: The "Astro-Tutor" (An expert in Astronomy, Math, and Mythology who speaks the language of middle and high school students—think science YouTuber meets coding instructor).

        Objective:
        Generate a comprehensive "Cosmic Dashboard" report based on the provided astronomical data. Bridge the gap between Ancient Indian Astronomy (Panchanga) and Modern Astrophysics for Grades 6–12. You must retain high-level technical details (degrees, names, periods) but explain them using relatable analogies (geometry, video games, sports, coding).

        Key Requirement: You must explicitly explain the difference between the Modern Zodiac (Western/Tropical) and the Hindu Zodiac (Sidereal/Fixed), explaining why they don't match due to the Earth's wobble (Precession).

        Input Data:
        - Date: {date_part}
        - Time: {time_part}
        - Location: {location}
        - Samvatsara: {samvatsara}
        - Masa: {masa}
        - Paksha: {paksha}
        - Tithi: {tithi}
        - Nakshatra: {nakshatra}
        - Rashi (Moon Sign): {rashi}
        - Yoga: {yoga}
        - Karana: {karana}
        - Ayanamsa: {ayanamsa}

        Instructions for Output Structure:

        1. Introduction: The "Time-Keeping" Engine
        - Contrast the Western Calendar (Solar/Season-based) with the Hindu Panchanga (Lunisolar/Star-based).
        - Analogy: Standard Watch vs. GPS Tracker.

        2. The Zodiac Belt (The Sky Map)
        - Explain the difference between Rashi (Hindu) and Signs (Western).
        - Explain Precession (The Wobble) and Ayanamsa (The drift).
        - Analogy: "Moving Stickers" (Seasons) vs. "Fixed Background" (Stars).

        3. The "Birthday Algorithm" (The 11-Day Lag)
        - Show the math: Solar Year (365.25) - Lunar Year (354) = ~11 days.
        - Explain why a Hindu birthday drifts backward every year.

        4. The Deep Dive (Technical Analysis)
        - Analyze the specific input date using the data provided.
        - Section A: The Geometry (Tithi & Yoga): Angles between Sun and Moon.
        - Section B: The GPS Coordinates (Nakshatra & Rashi): Specific star clusters and Constellations.
        - Section C: The Mythology (Story Mode): Deities and symbolic vibes for this moment.

        5. Visual Interaction Concepts
        - Throughout the text, insert "🖥️ Interactive Simulation Concept" blocks.
        - Describe a hypothetical 3D diagram or widget that explains the concept (e.g., "A slider that rotates the moon").

        6. The Cosmic Cheat Sheet (Vocabulary)
        - Define: Equinox, Precession, Ayanamsa, and Ecliptic using simple analogies (seesaws, spinning tops).

        Tone: High-energy, precise, visual, and encouraging. Use Markdown formatting (bolding, bullet points). Use the term 'Panchanga' instead of 'Vedic'.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Multi-stage Fallback (v5.0 robustness for 2026)
            # We try the newest models first, cascading down to legacy versions.
            fallback_models = [
                'gemini-3-flash',        # Latest 2026 model
                'gemini-2.5-flash',      # High-performance 2025/26 stable
                'gemini-2.5-flash-latest', 
                'gemini-2.0-flash',      # Stable 2.0 release
                'gemini-1.5-flash'       # Legacy safety net
            ]
            
            for fallback_name in fallback_models:
                if fallback_name == self.model_name:
                    continue
                    
                try:
                    print(f"Model {self.model_name} failed. Attempting fallback to {fallback_name}...")
                    fallback_model = genai.GenerativeModel(fallback_name)
                    response = fallback_model.generate_content(prompt)
                    return response.text
                except Exception as fallback_e:
                    print(f"Fallback to {fallback_name} failed: {fallback_e}")
                    continue
            
            return f"Error generating insight: {str(e)}"

# Factory or Manager to handle future expansion
class AIEngineManager:
    def __init__(self, provider="gemini"):
        if provider == "gemini":
            self.engine = GeminiEngine()
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    def get_explanation(self, config_data):
        return self.engine.generate_insight(config_data)

# Singleton instance for easy import
ai_engine = AIEngineManager()

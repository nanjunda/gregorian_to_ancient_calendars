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
        karana = config_data.get('karana')
        location = config_data.get('address')
        input_dt = config_data.get('input_datetime')
        rashi_obj = config_data.get('rashi')
        rashi = "N/A"
        if isinstance(rashi_obj, dict):
            rashi = rashi_obj.get('name', 'N/A')
        
        # Ayanamsa is usually around 24 degrees in this era
        ayanamsa = "approx. 24.11° (Chitra Paksha)" 
        
        # Split datetime for cleaner prompt
        date_part, time_part = "N/A", "N/A"
        if input_dt and ' ' in input_dt:
            date_part, time_part = input_dt.split(' ', 1)
        elif input_dt:
            date_part = input_dt

        prompt = f"""
        Role: The "Astro-Tutor" (Scientific YouTuber meets Coding Instructor).
        Objective: Generate a summary and a detailed "Cosmic Dashboard" report. 
        Format: You MUST return a VALID JSON object with exactly two keys: "audio_summary" and "insight".

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

        JSON Structure Requirements:
        1. "audio_summary": A high-level, 3-4 sentence conversational "voice-over" summary. Imagine you are a museum guide or a radio host. Make it intriguing. Focus on the 'vibe' and most unique astronomical aspect of this specific moment.
        2. "insight": The full technical Markdown report. 
        
        Detailed 'insight' requirements:
        - Contrast Western (Tropical) and Hindu (Sidereal) systems.
        - Use Active Render Tags: [[RENDER:ZODIAC_COMPARISON]], [[RENDER:MOON_PHASE_3D]], [[RENDER:PRECESSION_WOBBLE]], [[RENDER:CONSTELLATION_MAP]].
        - Explain the 5 Angas (DNA of Time).
        - Bridge Ancient Panchanga with Modern Astrophysics for Grades 6-12.
        - Tone: High-energy, precise, and visual.
        """
        
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback logic remains same...
            return f"Error: {str(e)}"

    def chat_with_tutor(self, message, context_data):
        if not self.model:
            return "AI Engine not configured."
            
        system_prompt = f"""
        Role: The "Astro-Tutor" (The Maestro of the Cosmic Explorer).
        Person: You are an encouraging, highly knowledgeable astronomer who bridges Ancient Indian Panchanga with Modern Astrophysics.
        Tone: Enthusiastic, clear, and educational.
        
        The Scope: You ONLY answer questions about:
        1. Hindu Panchanga (Tithis, Nakshatras, Angas).
        2. Modern Astronomy (Planets, Orbits, Physics, Precession).
        3. Cross-cultural calendars (Mayan, Inca, Egyptian, Gregorian).
        4. The "Cosmic Explorer" app features.
        
        Diversion Rule: If the student asks about unrelated topics (politics, sports, general recipes, celebrities), politely redirect them: "That's a fascinating question, but as your Astro-Tutor, my eyes are fixed on the heavens! Let's get back to [Panchanga/Astronomy topic]."
        
        Historical Strategy: Whenever explaining a challenge in timekeeping (like leap years or lunar cycles), mention how other civilizations solved it (e.g., Mayan Haab', Egyptian solar alignments, or Inca celestial pillars).
        
        Current Context for this User:
        - Location: {context_data.get('address')}
        - Samvatsara: {context_data.get('samvatsara')}
        - Tithi: {context_data.get('tithi')}
        - Nakshatra: {context_data.get('nakshatra')}
        
        User Message: {message}
        """

        try:
            response = self.model.generate_content(system_prompt)
            return response.text
        except Exception as e:
            return f"The star-link is fuzzy... (Error: {str(e)})"

# Factory or Manager to handle future expansion
class AIEngineManager:
    def __init__(self, provider="gemini"):
        if provider == "gemini":
            self.engine = GeminiEngine()
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    def get_explanation(self, config_data):
        return self.engine.generate_insight(config_data)

    def chat_with_tutor(self, message, context_data):
        return self.engine.chat_with_tutor(message, context_data)

# Singleton instance for easy import
ai_engine = AIEngineManager()

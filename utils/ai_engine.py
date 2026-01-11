import os
import abc
import google.generativeai as genai
import sys
import traceback

class BaseAIEngine(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate_insight(self, config_data):
        pass

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
        Format: Return ONLY the technical Markdown report. DO NOT Wrap in JSON.

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
        - **Masa**: Explain how it's named based on the Sun's transit sign during the New Moon.
        - **Nakshatra**: 13°20' sectors used as a "Lunar Speedometer" to track the Moon's 27.3-day orbit. Use [[RENDER:CONSTELLATION_MAP]].
        - **Tithi**: Defined strictly as Every 12° of angular separation between Sun and Moon. Use [[RENDER:MOON_PHASE_3D]].
        - **Yoga**: Combined longitudinal momentum (Sum of longitudes).
        - **Karana**: High-precision Half-Tithi (6° intervals).
        - **Rahu & Ketu**: Explain as **Lunar Nodes** (intersection points of orbital planes). Use [[RENDER:PRECESSION_WOBBLE]].

        Phase III: Decoding Your Specific Cosmic Alignment
        - Create a specific section: `## 🧩 Decoding Your Specific Cosmic Alignment`.
        - Use the specific values from the Input Data (Samvatsara: {config_data.get('samvatsara')}, Masa: {config_data.get('masa')}, etc.) to explain THIS specific moment.
        - Tell the student what they would see if they looked at the sky right now.

        Tone: "Cool Science YouTuber" - high energy, fascinating, and precise.
        """
        try:
            print("DEBUG: Generating content via Gemini...", file=sys.stderr)
            response = self.model.generate_content(prompt)
            text = response.text
            
            # Safeguard: Remove Markdown Code Blocks if AI wraps the entire report
            clean_text = text.strip()
            if clean_text.startswith('```markdown'): clean_text = clean_text[11:]
            elif clean_text.startswith('```'): clean_text = clean_text[3:]
            if clean_text.endswith('```'): clean_text = clean_text[:-3]
            text = clean_text.strip()

            # Safeguard: If Gemini still returns JSON, extract the 'insight' field
            if text.startswith('{') and '"insight":' in text:
                import json
                try:
                    data = json.loads(text)
                    return data.get('insight', text)
                except:
                    pass
            
            return text
        except Exception as e:
            print(f"ERROR in generate_insight: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return f"Error: {str(e)}"

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

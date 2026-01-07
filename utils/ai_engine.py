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
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def generate_insight(self, config_data):
        if not self.model:
            return "AI Engine not configured. Please set GOOGLE_API_KEY environment variable."

        prompt = f"""
        You are a cross-disciplinary expert: a Classical Astronomer, a Modern Astrophysicist, and a cultural Storyteller.
        Explain the following **Astronomical Configuration** for a student of the Hindu Panchanga:
        
        SAMVATSARA: {config_data.get('samvatsara')}
        MASA: {config_data.get('masa')}
        PAKSHA: {config_data.get('paksha')}
        TITHI: {config_data.get('tithi')}
        NAKSHATRA: {config_data.get('nakshatra')}
        YOGA: {config_data.get('yoga')}
        KARANA: {config_data.get('karana')}
        LOCATION: {config_data.get('address')}
        TIME: {config_data.get('input_datetime')}

        Please provide your insight in three parts:

        1. **The Astronomer's Perspective**: Explain the precise relative positions of the Sun, Moon, and Earth that create this configuration. Use scientific terms like 'elongation', 'sidereal', and 'precession' where appropriate.
        2. **The Physicist's Note**: Explain the underlying physical mechanics—why the orbital periods lead to these cycles (like the **jovian** period for Samvatsara) and how we define the **epoch** of this measurement. 
        3. **The Sage's Tale**: Connect these mechanics to Indian mythology or symbolic lore. Bridge the two worlds by explaining how the myth might be a poetic representation of the actual astronomical event.

        **Constraints**:
        - Use the term 'Panchanga' instead of 'Vedic'.
        - Ensure the tone is educational and engaging for a student.
        - Naturally include terms like 'jovian', 'epoch', 'precession', and 'sidereal' so our interactive glossary can highlight them.
        - Use Markdown formatting for a premium reading experience.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
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

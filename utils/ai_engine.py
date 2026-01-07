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
        You are an expert in both Hindu Panchanga (astronomy/astrology) and modern astrophysics.
        Explain the following astronomical configuration for a student:
        
        SAMVATSARA: {config_data.get('samvatsara')}
        MASA: {config_data.get('masa')}
        PAKSHA: {config_data.get('paksha')}
        TITHI: {config_data.get('tithi')}
        NAKSHATRA: {config_data.get('nakshatra')}
        YOGA: {config_data.get('yoga')}
        KARANA: {config_data.get('karana')}
        LOCATION: {config_data.get('address')}
        TIME: {config_data.get('input_datetime')}

        Please provide two sections:
        1. **Scientist's Note**: Explain the astronomical mechanics (orbits, relative positions, Earth's precession) behind these results.
        2. **Sage's Tale**: Share relevant Indian mythological stories or symbolic associations for these specific configurations.

        Tone: Educational, engaging, and culturally respectful. Use Markdown formatting.
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

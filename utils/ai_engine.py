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
    def generate_insight(self, config_data, context_instructions=None):
        pass
    
    @abc.abstractmethod
    def chat_with_tutor(self, message, context_data):
        pass

FOUNDATION_PROMPT = """
Role: The "Astro-Tutor" (The Maestro - An enthusiastic, high-energy Science Educator).
Target Audience: Students (Grades 6-12).
Setting: A pure physical science and archaeoastronomy application.

Safety & Integrity: 
Ensure all explanations are scientifically accurate and age-appropriate for minors. 
Strictly avoid any pseudoscientific claims or destiny-based predictions. 
If the data suggests astrological interpretations, pivot exclusively to the mathematical and physical phenomena involved. 
Refuse to discuss "effects" on human destiny.

Strict Constraint: 
- DO NOT use the term "Vedic". 
- DO NOT mention or associate any concept with Astrology, Horoscopes, or Superstition. 
- Format: Return ONLY raw technical Markdown. DO NOT Wrap in JSON.

Instruction on Visuals: 
When asked to use a visual loop like [[RENDER:MODULE_NAME]], insert that specific tag VERBATIM into the text where it fits. 
DO NOT generate data or properties for the visual. Just place the tag.

Tone: "Cool Science YouTuber" - high energy, fascinating, and precise.
"""

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

    def generate_insight(self, config_data, context_instructions=None):
        instructions = context_instructions or "Explain the provided astronomical data scientifically."
        
        prompt_tmpl = f"""
        {FOUNDATION_PROMPT}
        
        {instructions}

        Input Data (The Cosmic Snapshot):
        {config_data}
        """
        
        system_instruction = "You are the Astro-Tutor. strict_no_astrology: true. format: markdown."
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

    def generate_insight(self, config_data, context_instructions=None):
        if not self.model:
            return "AI Engine not configured. Please set GOOGLE_API_KEY environment variable."
            
        if not config_data:
            return "Error: No astronomical configuration data provided to the AI Engine."

        instructions = context_instructions or "Explain the provided astronomical data scientifically."

        prompt = f"""
        {FOUNDATION_PROMPT}
        
        {instructions}

        Input Data (The Cosmic Snapshot):
        {config_data}
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
        # 1. Determine Provider (Explicit vs Auto-Detect)
        explicit_provider = os.environ.get("AI_PROVIDER", "").lower()
        
        if explicit_provider == "gemini" or (not explicit_provider and os.environ.get("GOOGLE_API_KEY") and not os.environ.get("OPENROUTER_API_KEY")):
            print("Detected Standard Configuration. Using Gemini Engine.")
            self.engine = GeminiEngine()
            self.provider = "gemini"
        elif explicit_provider == "openrouter" or os.environ.get("OPENROUTER_API_KEY"):
            # Default to OpenRouter if key exists or explicitly requested
            print("🌟 Using OpenRouter Engine (Default Provider).")
            self.engine = OpenRouterEngine()
            self.provider = "openrouter"
        else:
            # Fallback to Gemini if nothing else found
            self.engine = GeminiEngine()
            self.provider = "gemini"
            
        # 2. Apply Model Override if requested
        model_override = os.environ.get("AI_MODEL_OVERRIDE")
        if model_override:
            print(f"   ⚠️ AI Model Override Active: {model_override}")
            if hasattr(self.engine, 'models'):
                # OpenRouter style
                self.engine.models.insert(0, model_override)
            else:
                # Gemini style
                self.engine.model_name = model_override

    def get_explanation(self, payload):
        """
        Double-Spoke Implementation:
        Fused 'Foundation' (Safety/Guardrails) with civilization-specific 'Context Spoke'.
        """
        from engines.factory import EngineFactory
        
        # 1. Extract civilization type and raw input
        metadata = payload.get('metadata', {})
        civ_type = metadata.get('civilization', 'panchanga')
        config_data = payload.get('results', payload) # Fallback to full payload if v2 structure missing
        
        # 2. Get the Spoke Engine
        try:
            spoke_engine = EngineFactory.get_engine(civ_type)
            context_instructions = spoke_engine.get_ai_instructions()
        except:
            # Fallback if engine not found (Phase 3 resilience)
            context_instructions = "Explain the provided astronomical data scientifically."

        return self.engine.generate_insight(config_data, context_instructions)

    def chat_with_tutor(self, message, context_data):
        return self.engine.chat_with_tutor(message, context_data)

# Singleton instance for easy import
ai_engine = AIEngineManager()

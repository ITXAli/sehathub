import os
import json
import requests
import tempfile
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

# Initialize the client globally to reuse connection pools
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
google_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class LLMManager:
    @staticmethod
    def _call_ollama(prompt: str, schema_name: str) -> dict:
        """Calls local Gemma 4b via Ollama (Offline Mode)"""
        # Note: In a real environment, we might use format="json" if supported by the model, 
        # or rely on prompt engineering to force JSON.
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "gemma:4b", # using typical Ollama gemma 4b tag
                    "prompt": prompt + f"\\n\\nRespond strictly in valid JSON matching the {schema_name} schema.",
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            parsed_json = json.loads(data.get("response", "{}"))
            if isinstance(parsed_json, list):
                if schema_name == "MediScanResponse":
                    return {"medicines": parsed_json}
                if len(parsed_json) > 0:
                    return parsed_json[0]
                return {}
            return parsed_json
        except Exception as e:
            import traceback
            traceback.print_exc()
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Ollama Error: {str(e)}")
            
    @staticmethod
    def _call_google_cloud(prompt: str, schema_name: str, image_bytes: bytes = None, mime_type: str = "image/jpeg") -> dict:
        model_name = "gemma-4-31b-it"

        try:
            contents = [prompt + f"\n\nRespond strictly in valid JSON matching the {schema_name} schema. Do not include markdown code blocks."]
            
            if image_bytes:
                # Use types.Part.from_bytes as required by the new SDK
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                )
                contents.insert(0, image_part)
                
            response = google_client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level="minimal"
                    )
                )
            )
            
            text = response.text.strip()
            
            # Print the raw text so we can see exactly what the AI returned before parsing
            print(f"RAW AI OUTPUT: '{text}'")
            print(f"FULL RESPONSE OBJ: {response}")
            
            # Clean up potential markdown formatting
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            if not text:
                raise ValueError("The AI returned an completely empty response! (Blank string)")
                
            parsed_json = json.loads(text)
            if isinstance(parsed_json, list):
                if schema_name == "MediScanResponse":
                    return {"medicines": parsed_json}
                if len(parsed_json) > 0:
                    return parsed_json[0]
                return {}
            return parsed_json
        except Exception as e:
            import traceback
            traceback.print_exc()
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Google Cloud API Error: {str(e)}")

    @staticmethod
    def process_triage(symptoms: str, is_offline: bool) -> dict:
        prompt = f"""Analyze these symptoms: {symptoms}. Classify urgency (High, Medium, Low) and provide action steps.
You must return exactly this JSON structure:
{{
    "urgency": "High/Medium/Low",
    "action_steps": ["step 1", "step 2"]
}}"""
        if is_offline:
            return LLMManager._call_ollama(prompt, "TriageResponse")
        return LLMManager._call_google_cloud(prompt, "TriageResponse")

    @staticmethod
    def process_mediscan(image_bytes: bytes, mime_type: str, is_offline: bool) -> dict:
        prompt = """Read this prescription and extract ALL medicines including their name, dosage, timing, and instructions.
You must return exactly this JSON structure:
{
    "medicines": [
        {
            "medicine_name": "extracted name",
            "dosage": "extracted dosage",
            "timing": "extracted timing",
            "instructions": "extracted instructions"
        }
    ]
}"""
        if is_offline:
            return LLMManager._call_ollama(prompt, "MediScanResponse")
        return LLMManager._call_google_cloud(prompt, "MediScanResponse", image_bytes, mime_type)

    @staticmethod
    def process_labsense(image_bytes: bytes, mime_type: str, is_offline: bool) -> dict:
        prompt = """Analyze this lab report. Identify out-of-range biomarkers and summarize them in simple terms with dietary advice.
You must return exactly this JSON structure:
{{
    "out_of_range_biomarkers": [
        {{"name": "marker name", "value": "value", "status": "High/Low/Abnormal"}}
    ],
    "summary_explanation": "simple explanation",
    "dietary_advice": "dietary advice"
}}"""
        if is_offline:
            return LLMManager._call_ollama(prompt, "LabSenseResponse")
        return LLMManager._call_google_cloud(prompt, "LabSenseResponse", image_bytes, mime_type)
        
    @staticmethod
    def process_nutriscan(image_bytes: bytes, mime_type: str, is_offline: bool) -> dict:
        prompt = """Identify the food in this image. Estimate calories, provide a glycemic safety score for diabetics, and give brief advice.
You must return exactly this JSON structure:
{{
    "food_identified": "food name",
    "estimated_calories": 500,
    "glycemic_safety_score": "High Risk/Medium Risk/Low Risk",
    "advice": "brief advice"
}}"""
        if is_offline:
            return LLMManager._call_ollama(prompt, "NutriScanResponse")
        return LLMManager._call_google_cloud(prompt, "NutriScanResponse", image_bytes, mime_type)

    @staticmethod
    def _get_mock_response(schema_name: str) -> dict:
        """Mock responses for robust offline testing without real AI"""
        mocks = {
            "TriageResponse": {
                "urgency": "High",
                "action_steps": ["Refer to nearest hospital immediately.", "Administer paracetamol if fever > 101F."]
            },
            "MediScanResponse": {
                "medicine_name": "Augmentin",
                "dosage": "625mg",
                "timing": "Twice a day",
                "instructions": "Take after meals for 5 days."
            },
            "LabSenseResponse": {
                "out_of_range_biomarkers": [
                    {"name": "Hemoglobin", "value": "10.2 g/dL", "status": "Low"},
                    {"name": "Cholesterol", "value": "240 mg/dL", "status": "High"}
                ],
                "summary_explanation": "Your blood oxygen carrier (Hemoglobin) is low, and your cholesterol is slightly high.",
                "dietary_advice": "Eat more iron-rich foods like spinach and lean meat. Reduce fried foods."
            },
            "NutriScanResponse": {
                "food_identified": "Chicken Biryani",
                "estimated_calories": 550,
                "glycemic_safety_score": "High Risk",
                "advice": "Spike in blood sugar expected. Consider a smaller portion or swap white rice for brown."
            }
        }
        return mocks.get(schema_name, {})

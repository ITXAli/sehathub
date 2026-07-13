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
    def process_triage(symptoms: str, is_offline: bool, mock: bool = False) -> dict:
        if mock or os.getenv("MOCK_MODE", "").lower() == "true":
            return LLMManager._get_mock_response("TriageResponse")
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
    def process_mediscan(image_bytes: bytes, mime_type: str, is_offline: bool, mock: bool = False) -> dict:
        if mock or os.getenv("MOCK_MODE", "").lower() == "true":
            return LLMManager._get_mock_response("MediScanResponse")
        prompt = """Read this prescription and extract ALL medicines including their name, dosage, timing, instructions, and translation of the medicine's purpose in Urdu script.
You must return exactly this JSON structure:
{
    "medicines": [
        {
            "medicine_name": "extracted name",
            "dosage": "extracted dosage",
            "timing": "extracted timing",
            "instructions": "extracted instructions",
            "purpose_urdu": "Urdu script detailing the medicine's main purpose (e.g., 'بخار اور درد کے لیے')"
        }
    ]
}"""
        if is_offline:
            return LLMManager._call_ollama(prompt, "MediScanResponse")
        return LLMManager._call_google_cloud(prompt, "MediScanResponse", image_bytes, mime_type)

    @staticmethod
    def process_labsense(image_bytes: bytes, mime_type: str, is_offline: bool, mock: bool = False) -> dict:
        if mock or os.getenv("MOCK_MODE", "").lower() == "true":
            return LLMManager._get_mock_response("LabSenseResponse")
        
        from services.nutrition_data import PAKISTANI_FOODS
        allowed_foods = ", ".join([f["name"] for f in PAKISTANI_FOODS])
        
        prompt = f"""Analyze this lab report. Identify ALL biomarkers (including low, high, and normal values) and status them (Normal, High, or Low).
Also provide a 7-day personalized diet plan that is built ONLY from the following allowed Pakistani foods list:
[{allowed_foods}]

You must return exactly this JSON structure:
{{
    "biomarkers": [
        {{"name": "marker name", "value": "value", "status": "Normal/High/Low"}}
    ],
    "summary_explanation": "simple explanation of the findings",
    "dietary_advice": "general dietary advice based on findings",
    "diet_plan": [
        {{"day": "Day 1", "meals_summary": "Breakfast, lunch, dinner and snacks using only the allowed foods"}},
        {{"day": "Day 2", "meals_summary": "..."}},
        {{"day": "Day 3", "meals_summary": "..."}},
        {{"day": "Day 4", "meals_summary": "..."}},
        {{"day": "Day 5", "meals_summary": "..."}},
        {{"day": "Day 6", "meals_summary": "..."}},
        {{"day": "Day 7", "meals_summary": "..."}}
    ]
}}"""
        if is_offline:
            return LLMManager._call_ollama(prompt, "LabSenseResponse")
        return LLMManager._call_google_cloud(prompt, "LabSenseResponse", image_bytes, mime_type)
        
    @staticmethod
    def process_nutriscan(image_bytes: bytes, mime_type: str, is_offline: bool, mock: bool = False) -> dict:
        if mock or os.getenv("MOCK_MODE", "").lower() == "true":
            return LLMManager._get_mock_response("NutriScanResponse")
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
                "medicines": [
                    {
                        "medicine_name": "Augmentin",
                        "dosage": "625mg",
                        "timing": "Twice a day",
                        "instructions": "Take after meals for 5 days.",
                        "purpose_urdu": "انفیکشن کے علاج کے لیے (اینٹی بائیوٹک)"
                    },
                    {
                        "medicine_name": "Panadol",
                        "dosage": "500mg",
                        "timing": "Three times a day",
                        "instructions": "Take as needed for pain or fever.",
                        "purpose_urdu": "بخار اور درد کو کم کرنے کے لیے"
                    }
                ]
            },
            "LabSenseResponse": {
                "biomarkers": [
                    {"name": "Hemoglobin", "value": "10.2 g/dL", "status": "Low"},
                    {"name": "Cholesterol", "value": "240 mg/dL", "status": "High"},
                    {"name": "Blood Glucose", "value": "90 mg/dL", "status": "Normal"},
                    {"name": "Iron", "value": "35 mcg/dL", "status": "Low"}
                ],
                "summary_explanation": "Your blood oxygen carrier (Hemoglobin) and Iron are low, and your cholesterol is slightly high.",
                "dietary_advice": "Eat more iron-rich foods like spinach and whole wheat roti. Reduce oil and ghee.",
                "diet_plan": [
                    {"day": "Day 1", "meals_summary": "Breakfast: Boiled Egg & Chapati (Whole Wheat). Lunch: Daal Mong/Masoor with Salad. Dinner: Palak Paneer & Chapati (Whole Wheat). Snack: Apple."},
                    {"day": "Day 2", "meals_summary": "Breakfast: Egg Omelette & Paratha. Lunch: Lobia (Black-eyed peas curry). Dinner: Chicken Salan & Tandoori Roti. Snack: Dates."},
                    {"day": "Day 3", "meals_summary": "Breakfast: Yogurt & Banana. Lunch: Daal Mash & Chapati. Dinner: Seekh Kebab & Cucumber Salad. Snack: Almonds."},
                    {"day": "Day 4", "meals_summary": "Breakfast: Boiled Egg & Chapati. Lunch: Chana Masala with salad. Dinner: Chicken Biryani with Raita. Snack: Guava."},
                    {"day": "Day 5", "meals_summary": "Breakfast: Egg Omelette & Chapati. Lunch: Lobia leftover. Dinner: Fried Fish & Cucumber Salad. Snack: Walnuts."},
                    {"day": "Day 6", "meals_summary": "Breakfast: Yogurt & Apples. Lunch: Chicken Pulao. Dinner: Beef Keema & Tandoori Roti. Snack: Orange."},
                    {"day": "Day 7", "meals_summary": "Breakfast: Boiled Egg & Paratha. Lunch: Aloo Palak & Chapati. Dinner: Kofta Curry & Tandoori Roti. Snack: Pista."}
                ]
            },
            "NutriScanResponse": {
                "food_identified": "Chicken Biryani",
                "estimated_calories": 550,
                "glycemic_safety_score": "High Risk",
                "advice": "Spike in blood sugar expected. Consider a smaller portion or swap white rice for brown."
            }
        }
        return mocks.get(schema_name, {})


from pydantic import BaseModel
from typing import List, Optional

# Triage Schemas
class TriageRequest(BaseModel):
    symptoms: str
    is_offline: bool = False

class TriageResponse(BaseModel):
    urgency: str  # "High", "Medium", "Low"
    action_steps: List[str]

# MediScan Schemas
class MedicineDetail(BaseModel):
    medicine_name: str
    dosage: str
    timing: str
    instructions: str

class MediScanResponse(BaseModel):
    medicines: List[MedicineDetail]

# LabSense Schemas
class Biomarker(BaseModel):
    name: str
    value: str
    status: str # "Normal", "High", "Low"

class LabSenseResponse(BaseModel):
    out_of_range_biomarkers: List[Biomarker]
    summary_explanation: str
    dietary_advice: str

# NutriScan Schemas
class NutriScanResponse(BaseModel):
    food_identified: str
    estimated_calories: int
    glycemic_safety_score: str # e.g. "Low Risk", "High Risk"
    advice: str

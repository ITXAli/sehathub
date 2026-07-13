from fastapi import APIRouter
from models.schemas import TriageRequest, TriageResponse
from services.llm_manager import LLMManager

router = APIRouter()

@router.post("/", response_model=TriageResponse)
async def analyze_symptoms(request: TriageRequest):
    result = LLMManager.process_triage(request.symptoms, request.is_offline, request.mock)
    return TriageResponse(**result)

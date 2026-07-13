from fastapi import APIRouter, UploadFile, File, Form
from models.schemas import MediScanResponse
from services.llm_manager import LLMManager

router = APIRouter()

@router.post("/", response_model=MediScanResponse)
async def process_prescription(file: UploadFile = File(...), is_offline: bool = Form(...), mock: bool = Form(False)):
    contents = await file.read()
    result = LLMManager.process_mediscan(contents, file.content_type, is_offline, mock)
    return MediScanResponse(**result)

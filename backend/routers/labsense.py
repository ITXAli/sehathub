from fastapi import APIRouter, UploadFile, File, Form
from models.schemas import LabSenseResponse
from services.llm_manager import LLMManager

router = APIRouter()

@router.post("/", response_model=LabSenseResponse)
async def process_lab_report(file: UploadFile = File(...), is_offline: bool = Form(...), mock: bool = Form(False)):
    contents = await file.read()
    result = LLMManager.process_labsense(contents, file.content_type, is_offline, mock)
    return LabSenseResponse(**result)

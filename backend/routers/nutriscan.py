from fastapi import APIRouter, UploadFile, File, Form
from models.schemas import NutriScanResponse
from services.llm_manager import LLMManager

router = APIRouter()

@router.post("/", response_model=NutriScanResponse)
async def process_food_image(file: UploadFile = File(...), is_offline: bool = Form(...)):
    contents = await file.read()
    result = LLMManager.process_nutriscan(contents, file.content_type, is_offline)
    return NutriScanResponse(**result)

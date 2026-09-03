# -*- coding: utf-8 -*-
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import tempfile
import os
import json

from src.services.excel_roi_service import ExcelROIService
from src.core.config import settings

router = APIRouter(prefix="/excel", tags=["excel"])

@router.post("/analyze-with-ai")
async def analyze_excel_with_ai(
    file: UploadFile = File(...),
    project_data: str = "{}"
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Только Excel файлы (.xlsx, .xls)")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            business_case = json.loads(project_data)
        except:
            business_case = {}
        
        service = ExcelROIService(settings.YANDEXGPT_API_KEY, settings.YANDEXGPT_FOLDER_ID)
        result = service.process(tmp_path, business_case)
        
        os.unlink(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

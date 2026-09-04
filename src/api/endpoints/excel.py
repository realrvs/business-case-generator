# -*- coding: utf-8 -*-
"""
Excel API Endpoints
Эндпоинты для работы с Excel-файлами
"""
import os
import tempfile
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel

from src.services.excel_structure_extractor import ExcelStructureExtractor
from src.services.excel_ai_mapper import ExcelAIMapper
from src.services.excel_roi_calculator import ExcelROICalculator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/excel", tags=["Excel"])

# Модели данных
class ExcelCalculateRequest(BaseModel):
    file_id: str
    data: Dict[str, Any]
    mapping: Optional[Dict[str, Any]] = None

class ExcelCalculateResponse(BaseModel):
    status: str
    results: Optional[Dict[str, Any]] = None
    output_cells: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Хранилище для загруженных файлов (временное)
file_storage = {}

@router.post("/analyze")
async def analyze_excel(
    file: UploadFile = File(...),
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Анализ Excel-файла: извлечение структуры и AI-маппинг
    """
    try:
        # Проверка расширения
        if not file.filename.endswith(('.xlsx', '.xls', '.xlsm')):
            raise HTTPException(
                status_code=400,
                detail="Поддерживаются только .xlsx, .xls, .xlsm файлы"
            )
        
        # Сохраняем файл во временную директорию
        temp_dir = tempfile.mkdtemp(prefix="excel_upload_")
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Извлекаем структуру
        extractor = ExcelStructureExtractor()
        structure = extractor.extract(file_path)
        
        # AI-маппинг
        mapper = ExcelAIMapper()
        mapping = mapper.map_cells(
            structure,
            {'description': context or 'Бизнес-модель'}
        )
        
        # Сохраняем информацию о файле
        file_id = os.path.basename(temp_dir)
        file_storage[file_id] = {
            'file_path': file_path,
            'temp_dir': temp_dir,
            'filename': file.filename,
            'structure': structure,
            'mapping': mapping
        }
        
        return {
            'file_id': file_id,
            'filename': file.filename,
            'structure': structure,
            'mapping': mapping,
            'sheets': [sheet['name'] for sheet in structure.get('sheets', [])]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при анализе Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate")
async def calculate_excel(request: ExcelCalculateRequest) -> Dict[str, Any]:
    """
    Расчет Excel-модели с подстановкой данных
    """
    try:
        file_id = request.file_id
        
        if file_id not in file_storage:
            raise HTTPException(
                status_code=404,
                detail="Файл не найден. Сначала загрузите файл через /analyze"
            )
        
        file_info = file_storage[file_id]
        file_path = file_info['file_path']
        mapping = request.mapping or file_info.get('mapping', {})
        
        # Создаем калькулятор
        calculator = ExcelROICalculator()
        
        try:
            # Выполняем расчет
            result = calculator.calculate(file_path, request.data, mapping)
            
            if result.get('status') == 'error':
                raise HTTPException(
                    status_code=500,
                    detail=result.get('error', 'Ошибка при расчете')
                )
            
            return result
        finally:
            # Очищаем временные файлы
            calculator.cleanup()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при расчете Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}")
async def get_file_info(file_id: str) -> Dict[str, Any]:
    """
    Получение информации о загруженном файле
    """
    if file_id not in file_storage:
        raise HTTPException(
            status_code=404,
            detail="Файл не найден"
        )
    
    file_info = file_storage[file_id]
    
    return {
        'file_id': file_id,
        'filename': file_info['filename'],
        'sheets': [sheet['name'] for sheet in file_info['structure'].get('sheets', [])],
        'mapping': file_info.get('mapping', {})
    }

@router.delete("/{file_id}")
async def delete_file(file_id: str) -> Dict[str, str]:
    """
    Удаление загруженного файла и временных данных
    """
    if file_id not in file_storage:
        raise HTTPException(
            status_code=404,
            detail="Файл не найден"
        )
    
    file_info = file_storage[file_id]
    temp_dir = file_info.get('temp_dir')
    
    if temp_dir and os.path.exists(temp_dir):
        import shutil
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
    
    del file_storage[file_id]
    
    return {'status': 'deleted', 'file_id': file_id}

# -*- coding: utf-8 -*-
import json
import logging
import tempfile
import os
from typing import Dict, Any

from src.services.excel_structure_extractor import ExcelStructureExtractor
from src.services.excel_ai_mapper import ExcelAIMapper
from src.services.libreoffice_calculator import LibreOfficeCalculator

logger = logging.getLogger(__name__)

class ExcelROIService:
    def __init__(self, api_key: str, folder_id: str):
        self.mapper = ExcelAIMapper(api_key, folder_id)
        self.calculator = LibreOfficeCalculator()
        self.extractor = ExcelStructureExtractor()
    
    def process(self, file_path: str, business_case: Dict[str, Any]) -> Dict[str, Any]:
        try:
            structure = self.extractor.extract(file_path)
            logger.info(f"✅ Структура извлечена: {len(structure['non_empty_cells'])} ячеек")
            
            mapping = self.mapper.map_variables(structure, business_case)
            logger.info(f"✅ Маппинг: {mapping}")
            
            if not mapping:
                return {"success": False, "error": "Не удалось определить маппинг", "message": "AI не нашел соответствия в Excel-файле"}
            
            roi_value = self.calculator.calculate_roi(file_path, mapping, business_case)
            
            if roi_value is not None:
                return {"success": True, "roi": roi_value, "mapping": mapping, "message": f"✅ ROI рассчитан по модели: {roi_value:.2f}%"}
            else:
                return {"success": False, "error": "Не удалось пересчитать ROI", "mapping": mapping, "message": "❌ Ошибка при пересчете формул Excel"}
        except Exception as e:
            logger.error(f"Ошибка обработки: {e}")
            return {"success": False, "error": str(e), "message": "❌ Ошибка обработки Excel-файла"}

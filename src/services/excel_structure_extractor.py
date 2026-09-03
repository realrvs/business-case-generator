# -*- coding: utf-8 -*-
import openpyxl
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ExcelStructureExtractor:
    def __init__(self):
        self.file_path = None
        self.structure = {}
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        self.file_path = file_path
        wb = openpyxl.load_workbook(file_path, data_only=False)
        result = {
            "sheets": [],
            "all_cells": [],
            "non_empty_cells": [],
            "formulas": [],
        }
        
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            sheet_data = {
                "name": sheet_name,
                "cells": []
            }
            
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value is not None:
                        cell_info = {
                            "address": cell.coordinate,
                            "value": str(cell.value)[:500],
                            "type": cell.data_type,
                            "sheet": sheet_name
                        }
                        result["non_empty_cells"].append(cell_info)
                        sheet_data["cells"].append(cell_info)
                        if cell.data_type == 'f':
                            result["formulas"].append(cell_info)
                        result["all_cells"].append(cell_info)
            
            result["sheets"].append(sheet_data)
        
        logger.info(f"✅ Извлечено {len(result['non_empty_cells'])} непустых ячеек")
        return result

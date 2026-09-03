# -*- coding: utf-8 -*-
import json
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ExcelAIMapper:
    def __init__(self, api_key: str, folder_id: str):
        self.api_key = api_key
        self.folder_id = folder_id
    
    def map_variables(self, structure: Dict[str, Any], business_case: Dict[str, Any]) -> Dict[str, str]:
        try:
            cells_data = self._format_cells_for_ai(structure)
            prompt = self._build_prompt(cells_data, business_case)
            response = self._call_yandex_gpt(prompt)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Ошибка маппинга: {e}")
            return {}
    
    def _format_cells_for_ai(self, structure: Dict) -> str:
        cells = structure.get("non_empty_cells", [])
        sheets = {}
        for cell in cells:
            sheet = cell.get("sheet", "Sheet1")
            if sheet not in sheets:
                sheets[sheet] = []
            sheets[sheet].append(cell)
        
        result = []
        for sheet_name, sheet_cells in sheets.items():
            result.append(f"\n=== Лист: {sheet_name} ===")
            sorted_cells = sorted(sheet_cells, key=lambda x: (x.get("row", 0), x.get("col", 0)))
            for cell in sorted_cells[:200]:
                address = cell.get("address", "")
                value = cell.get("value", "")[:200]
                if value:
                    result.append(f"{address}: {value}")
        return "\n".join(result)
    
    def _build_prompt(self, cells_data: str, business_case: Dict) -> str:
        return f"""
Ты — эксперт по финансовому анализу и Excel-моделям.

Ниже приведено содержимое ячеек Excel-файла в формате "КООРДИНАТА: ЗНАЧЕНИЕ".

Данные бизнес-кейса:
- Текущие затраты: {business_case.get('current_costs', 0)}
- Размер команды: {business_case.get('team_size', 0)}
- Экономия времени: {business_case.get('time_saved', 0)}
- Стоимость часа: {business_case.get('hourly_rate', 0)}

Содержимое Excel:
{cells_data}

Ответь ТОЛЬКО JSON:
{{
  "current_costs": "B2",
  "team_size": "B3", 
  "time_saved": "B4",
  "hourly_rate": "B5",
  "roi_result": "E15"
}}
"""
    
    def _call_yandex_gpt(self, prompt: str) -> str:
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            payload = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.1,
                    "maxTokens": "1000"
                },
                "messages": [
                    {"role": "system", "text": "Ты — эксперт по финансовому анализу. Отвечай только в формате JSON."},
                    {"role": "user", "text": prompt}
                ]
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}",
                "x-folder-id": self.folder_id
            }
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'alternatives' in result['result']:
                    return result['result']['alternatives'][0]['message']['text']
            return "{}"
        except Exception as e:
            logger.error(f"YandexGPT ошибка: {e}")
            return "{}"
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                data = json.loads(json_str)
                return {k: str(v).upper() for k, v in data.items()}
        except Exception as e:
            logger.error(f"Парсинг ответа: {e}")
        return {}

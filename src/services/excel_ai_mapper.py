# -*- coding: utf-8 -*-
"""
Excel AI Mapper
Автоматический маппинг ячеек через YandexGPT
"""
import json
import logging
from typing import Dict, List, Any, Optional
from src.services.yandex_gpt import YandexGPT

logger = logging.getLogger(__name__)

class ExcelAIMapper:
    """
    AI-маппинг ячеек Excel для определения входов и выходов
    """
    
    def __init__(self):
        self.yandex_gpt = YandexGPT()
    
    def map_cells(self, structure: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Маппинг ячеек с помощью AI
        
        Args:
            structure: Структура Excel-файла
            context: Контекст проекта
            
        Returns:
            Dict с маппингом ячеек
        """
        try:
            logger.info("Начало AI-маппинга ячеек")
            
            # Подготовка данных для маппинга
            cell_data = self._prepare_cell_data(structure)
            
            if not cell_data:
                logger.warning("Нет данных для маппинга")
                return self._get_default_mapping(structure)
            
            # Проверка доступности YandexGPT
            if not self.yandex_gpt.is_available:
                logger.warning("YandexGPT недоступен, используем стандартный маппинг")
                return self._get_default_mapping(structure)
            
            # Получение AI-маппинга
            prompt = self._build_mapping_prompt(cell_data, context)
            response = self.yandex_gpt._call_api(prompt)
            
            if response:
                mapping = self._parse_mapping_response(response, cell_data)
                if mapping:
                    return mapping
            
            # Fallback при ошибке
            return self._get_default_mapping(structure)
            
        except Exception as e:
            logger.error(f"Ошибка при AI-маппинге: {e}")
            return self._get_default_mapping(structure)
    
    def _prepare_cell_data(self, structure: Dict) -> List[Dict]:
        """
        Подготовка данных ячеек для AI
        """
        cell_data = []
        
        for sheet in structure.get('sheets', []):
            for cell in sheet.get('cells', [])[:50]:  # Ограничим для производительности
                cell_data.append({
                    'sheet': sheet['name'],
                    'address': cell['address'],
                    'value': cell['value'],
                    'type': cell['data_type'],
                    'row': cell['row'],
                    'col': cell['col']
                })
        
        return cell_data
    
    def _build_mapping_prompt(self, cell_data: List[Dict], context: Dict) -> str:
        """
        Формирование промпта для AI-маппинга
        """
        prompt = f"""
        Проанализируй Excel-модель и определи, какие ячейки являются входами, а какие выходами.
        
        Контекст проекта: {context.get('description', 'Бизнес-модель')}
        
        Данные ячеек:
        {json.dumps(cell_data[:30], ensure_ascii=False, indent=2)}
        
        Определи:
        1. Какие ячейки являются входными параметрами (данные, которые пользователь может изменять)
        2. Какие ячейки являются выходными результатами (расчеты, формулы)
        3. Предложи названия для этих параметров
        
        Верни ответ в формате JSON:
        {{
            "inputs": [
                {{"sheet": "Лист1", "address": "A1", "name": "Название параметра", "description": "Описание"}}
            ],
            "outputs": [
                {{"sheet": "Лист1", "address": "B10", "name": "Название результата", "description": "Описание"}}
            ]
        }}
        """
        return prompt
    
    def _parse_mapping_response(self, response: Dict, cell_data: List[Dict]) -> Optional[Dict]:
        """
        Парсинг ответа AI
        """
        try:
            if 'result' in response and 'alternatives' in response['result']:
                text = response['result']['alternatives'][0].get('text', '')
                parsed = json.loads(text)
                
                return {
                    'inputs': parsed.get('inputs', []),
                    'outputs': parsed.get('outputs', []),
                    'mapped_cells': self._create_cell_mapping(parsed, cell_data),
                    'confidence': 'high'
                }
        except json.JSONDecodeError:
            logger.warning("Не удалось распарсить ответ AI")
        except Exception as e:
            logger.error(f"Ошибка парсинга ответа: {e}")
        
        return None
    
    def _create_cell_mapping(self, parsed: Dict, cell_data: List[Dict]) -> Dict[str, Any]:
        """
        Создание маппинга ячеек
        """
        mapping = {}
        
        # Добавляем входные ячейки
        for input_cell in parsed.get('inputs', []):
            key = f"{input_cell['sheet']}!{input_cell['address']}"
            mapping[key] = {
                'type': 'input',
                'name': input_cell.get('name', ''),
                'description': input_cell.get('description', ''),
                'value': self._find_cell_value(cell_data, input_cell['sheet'], input_cell['address'])
            }
        
        # Добавляем выходные ячейки
        for output_cell in parsed.get('outputs', []):
            key = f"{output_cell['sheet']}!{output_cell['address']}"
            mapping[key] = {
                'type': 'output',
                'name': output_cell.get('name', ''),
                'description': output_cell.get('description', ''),
                'value': self._find_cell_value(cell_data, output_cell['sheet'], output_cell['address'])
            }
        
        return mapping
    
    def _find_cell_value(self, cell_data: List[Dict], sheet: str, address: str) -> Any:
        """
        Поиск значения ячейки по адресу
        """
        for cell in cell_data:
            if cell['sheet'] == sheet and cell['address'] == address:
                return cell['value']
        return None
    
    def _get_default_mapping(self, structure: Dict) -> Dict:
        """
        Стандартный маппинг при недоступности AI
        """
        mapping = {
            'inputs': [],
            'outputs': [],
            'mapped_cells': {},
            'confidence': 'low'
        }
        
        for sheet in structure.get('sheets', []):
            # Определяем входные ячейки (первые колонки с данными)
            for cell in sheet.get('input_cells', [])[:5]:
                mapping['inputs'].append({
                    'sheet': sheet['name'],
                    'address': cell['address'],
                    'name': f"Параметр_{cell['address']}",
                    'description': 'Автоматически определенный параметр'
                })
            
            # Определяем выходные ячейки (ячейки с формулами)
            for cell in sheet.get('output_cells', [])[:5]:
                mapping['outputs'].append({
                    'sheet': sheet['name'],
                    'address': cell['address'],
                    'name': f"Результат_{cell['address']}",
                    'description': 'Автоматически определенный результат'
                })
        
        return mapping

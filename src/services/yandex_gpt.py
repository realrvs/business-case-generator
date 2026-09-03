# -*- coding: utf-8 -*-
"""
YandexGPT интеграция для генерации рекомендаций
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class YandexGPT:
    """
    Клиент для работы с YandexGPT API
    """
    
    def __init__(self):
        self.api_key = os.getenv('YANDEX_GPT_API_KEY')
        self.folder_id = os.getenv('YANDEX_GPT_FOLDER_ID')
        self.base_url = "https://llm.api.cloud.yandex.net/v2"
        self.is_available = bool(self.api_key and self.folder_id)
        
        if not self.is_available:
            logger.warning("YandexGPT не настроен. Проверьте YANDEX_GPT_API_KEY и YANDEX_GPT_FOLDER_ID")
    
    def generate_business_case(self, data: Dict[str, Any], roi_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация бизнес-кейса через YandexGPT
        
        Args:
            data: Входные данные проекта
            roi_result: Результаты расчета ROI
            
        Returns:
            Dict с рекомендациями и анализом
        """
        if not self.is_available:
            logger.warning("YandexGPT недоступен, возвращаем стандартные рекомендации")
            return self._get_default_response(data, roi_result)
        
        try:
            prompt = self._build_prompt(data, roi_result)
            response = self._call_api(prompt)
            
            if response:
                return self._parse_response(response, data, roi_result)
            else:
                return self._get_default_response(data, roi_result)
                
        except Exception as e:
            logger.error(f"Ошибка при вызове YandexGPT: {e}")
            return self._get_default_response(data, roi_result)
    
    def _build_prompt(self, data: Dict, roi_result: Dict) -> str:
        """Формирование промпта для YandexGPT"""
        project_name = data.get('project_name', 'Проект')
        team_size = data.get('team_size', 1)
        roi = roi_result.get('roi_percentage', 0)
        
        prompt = f"""
        Проанализируй бизнес-кейс для проекта "{project_name}":
        
        Параметры:
        - Размер команды: {team_size} человек
        - ROI: {roi}%
        - Экономия времени: {data.get('time_saved', 0)}%
        - Текущие затраты: {data.get('current_costs', 0)} руб.
        - AI затраты: {roi_result.get('ai_costs', 0)} руб.
        
        Сформируй ответ в формате JSON с полями:
        1. recommendations - список из 3-5 конкретных рекомендаций
        2. risks - список рисков с уровнями (HIGH/MEDIUM/LOW)
        3. implementation_plan - пошаговый план внедрения
        """
        return prompt
    
    def _call_api(self, prompt: str) -> Optional[str]:
        """Вызов YandexGPT API"""
        try:
            url = f"{self.base_url}/completion"
            headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "general",
                "folderId": self.folder_id,
                "text": prompt,
                "temperature": 0.7,
                "maxTokens": 500
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Таймаут при вызове YandexGPT API")
            return None
        except Exception as e:
            logger.error(f"Ошибка при вызове API: {e}")
            return None
    
    def _parse_response(self, response: Dict, data: Dict, roi_result: Dict) -> Dict:
        """Парсинг ответа YandexGPT"""
        try:
            # Извлекаем текст ответа
            if 'result' in response and 'alternatives' in response['result']:
                text = response['result']['alternatives'][0].get('text', '')
                # Пытаемся парсить JSON
                try:
                    parsed = json.loads(text)
                    return {
                        'recommendations': parsed.get('recommendations', []),
                        'risks': parsed.get('risks', []),
                        'implementation_plan': parsed.get('implementation_plan', 
                            '1. Начать с пилотного проекта\n2. Внедрить систему мониторинга')
                    }
                except json.JSONDecodeError:
                    # Если не JSON, используем стандартный ответ
                    return self._get_default_response(data, roi_result)
            else:
                return self._get_default_response(data, roi_result)
                
        except Exception as e:
            logger.error(f"Ошибка парсинга ответа: {e}")
            return self._get_default_response(data, roi_result)
    
    def _get_default_response(self, data: Dict, roi_result: Dict) -> Dict:
        """Стандартный ответ при недоступности API"""
        return {
            'recommendations': [
                'Начать с пилотного проекта на одном процессе',
                'Внедрить систему мониторинга эффективности',
                'Обучить команду работе с AI-агентами'
            ],
            'risks': [
                {'level': 'MEDIUM', 'description': 'Сопротивление изменениям'},
                {'level': 'LOW', 'description': 'Технические риски интеграции'}
            ],
            'implementation_plan': '1. Анализ текущих процессов\n2. Пилотное внедрение\n3. Сбор метрик\n4. Масштабирование'
        }
    
    def is_available(self) -> bool:
        """Проверка доступности YandexGPT"""
        return self.is_available and bool(self.api_key)

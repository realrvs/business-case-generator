# -*- coding: utf-8 -*-
import json
import logging
import requests
from typing import Dict, Any, Optional
from src.core.config import settings

logger = logging.getLogger(__name__)

class YandexGPT:
    def __init__(self):
        self.api_key = settings.YANDEXGPT_API_KEY
        self.folder_id = settings.YANDEXGPT_FOLDER_ID
        self.model_uri = f"gpt://{self.folder_id}/yandexgpt-lite"
        self.is_available = bool(self.api_key and self.folder_id)
        
        if not self.is_available:
            logger.warning("⚠️ YandexGPT не настроен. Используются fallback-ответы.")
    
    def generate_business_case(self, project_data: Dict, roi: Dict) -> Dict[str, Any]:
        if not self.is_available:
            return self._get_fallback_response(project_data, roi)
        
        try:
            prompt = self._build_prompt(project_data, roi)
            response = self._call_gpt(prompt)
            return self._parse_response(response, project_data)
        except Exception as e:
            logger.error(f"Ошибка генерации бизнес-кейса: {e}")
            return self._get_fallback_response(project_data, roi)
    
    def _build_prompt(self, project_data: Dict, roi: Dict) -> str:
        return f"""
Ты — эксперт по AI-стратегии и бизнес-анализу. Помоги создать бизнес-кейс для внедрения AI-агентов.

Данные проекта:
- Название проекта: {project_data.get('project_name', 'Неизвестный проект')}
- Текущие затраты: {project_data.get('current_costs', 0)} руб/мес
- Размер команды: {project_data.get('team_size', 1)} человек
- Экономия времени: {project_data.get('time_saved', 0)} часов/мес
- Стоимость часа работы: {project_data.get('hourly_rate', 2000)} руб

ROI анализ:
- ROI: {roi.get('roi_percentage', 0)}%
- Период окупаемости: {roi.get('payback_period', 0)} месяцев
- Ежемесячная экономия: {roi.get('monthly_savings', 0)} руб
- Годовая экономия: {roi.get('annual_savings', 0)} руб
- Затраты на AI: {roi.get('ai_costs', 0)} руб/мес

Сгенерируй структурированный бизнес-кейс в формате JSON со следующими полями:

1. executive_summary — краткое резюме для руководства (3-5 предложений)
2. problem_analysis — анализ текущей ситуации
3. solution_description — описание предлагаемого решения с AI-агентами
4. financial_analysis — финансовый анализ включая ROI и окупаемость
5. recommendations — 3-5 конкретных рекомендаций
6. risks — 2-3 риска с уровнем HIGH/MEDIUM/LOW
7. implementation_plan — план внедрения по этапам
8. kpis — ключевые метрики успеха

Ответ должен быть только в формате JSON.
"""
    
    def _call_gpt(self, prompt: str) -> Optional[str]:
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            
            payload = {
                "modelUri": self.model_uri,
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.3,
                    "maxTokens": "2500"
                },
                "messages": [
                    {
                        "role": "system",
                        "text": "Ты — эксперт по AI-стратегии и бизнес-анализу. Отвечай только в формате JSON."
                    },
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}",
                "x-folder-id": self.folder_id
            }
            
            logger.info("📤 Отправка запроса к YandexGPT...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'alternatives' in result['result']:
                    text = result['result']['alternatives'][0]['message']['text']
                    logger.info(f"✅ Получен ответ от YandexGPT ({len(text)} символов)")
                    return text
            else:
                logger.error(f"❌ Ошибка YandexGPT API: {response.status_code}")
                logger.error(f"   Текст: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ Таймаут при вызове YandexGPT")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка при вызове YandexGPT: {e}")
            return None
    
    def _parse_response(self, response: str, project_data: Dict) -> Dict:
        try:
            # Пытаемся найти JSON в ответе
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                return {
                    "project_name": project_data.get('project_name', ''),
                    "executive_summary": data.get('executive_summary', ''),
                    "problem_analysis": data.get('problem_analysis', ''),
                    "solution_description": data.get('solution_description', ''),
                    "financial_analysis": data.get('financial_analysis', ''),
                    "recommendations": data.get('recommendations', []),
                    "risks": data.get('risks', []),
                    "implementation_plan": data.get('implementation_plan', ''),
                    "kpis": data.get('kpis', {})
                }
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга ответа: {e}")
        
        return self._get_fallback_response(project_data, {})
    
    def _get_fallback_response(self, project_data: Dict, roi: Dict) -> Dict:
        return {
            "project_name": project_data.get('project_name', ''),
            "executive_summary": f"Внедрение AI-агентов в проект '{project_data.get('project_name', '')}' обеспечит ROI {roi.get('roi_percentage', 0):.1f}% с периодом окупаемости {roi.get('payback_period', 0):.1f} месяцев. Проект рекомендуется к реализации.",
            "problem_analysis": "Текущие процессы требуют значительных временных и финансовых затрат.",
            "solution_description": "Внедрение AI-агентов для автоматизации рутинных задач.",
            "financial_analysis": f"ROI: {roi.get('roi_percentage', 0):.1f}%. Окупаемость: {roi.get('payback_period', 0):.1f} месяцев.",
            "recommendations": [
                "Начать с пилотного проекта на одном процессе",
                "Внедрить систему мониторинга эффективности",
                "Обучить команду работе с AI-агентами"
            ],
            "risks": [
                {"level": "MEDIUM", "description": "Технические риски интеграции"},
                {"level": "LOW", "description": "Сопротивление изменениям со стороны команды"}
            ],
            "implementation_plan": "1. Пилотный проект (1 месяц)\n2. Масштабирование (2 месяца)\n3. Полное внедрение (3 месяца)",
            "kpis": {
                "roi_target": "> 100%",
                "payback_period_target": "< 6 месяцев",
                "productivity_gain_target": "> 30%"
            }
        }

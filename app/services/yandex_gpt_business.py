# app/services/yandex_gpt_business.py
import logging
import json
import requests
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class YandexGPTBusiness:
    def __init__(self):
        self.api_key = settings.YANDEXGPT_API_KEY
        self.folder_id = settings.YANDEXGPT_FOLDER_ID
        self.is_available = bool(self.api_key and self.folder_id)
    
    def generate_business_case(
        self,
        context: List[Dict],
        project_data: Dict,
        roi: Dict
    ) -> Dict[str, Any]:
        \"\"\"Генерация бизнес-кейса\"\"\"
        if not self.is_available:
            return self._get_fallback_business_case(project_data, roi)
        
        prompt = self._build_prompt(context, project_data, roi)
        response = self._call_gpt(prompt)
        
        if response:
            return self._parse_response(response)
        
        return self._get_fallback_business_case(project_data, roi)
    
    def _build_prompt(self, context: List[Dict], project_data: Dict, roi: Dict) -> str:
        context_text = "\n".join([c.get("document", "") for c in context])
        
        prompt = f"""
Ты — эксперт по AI-стратегии и бизнес-анализу.
Создай структурированный бизнес-кейс для внедрения AI-агентов.

Данные:
- Проект: {project_data.get('project_name', 'Неизвестный проект')}
- Текущие затраты: {project_data.get('current_costs', 0)} руб/мес
- Размер команды: {project_data.get('team_size', 0)} чел
- Экономия времени: {project_data.get('time_saved', 0)} часов/мес

Контекст:
{context_text}

Расчеты ROI:
- ROI: {roi.get('roi_percentage', 0)}%
- Payback Period: {roi.get('payback_period', 0)} мес
- Ежегодная экономия: {roi.get('annual_savings', 0)} руб

Сформируй ответ в формате JSON:
{{
  "executive_summary": "Краткий обзор (3-5 предложений)",
  "roi_analysis": "Детальный анализ ROI",
  "recommendations": ["Рекомендация 1", "Рекомендация 2", "Рекомендация 3"],
  "risks": ["Риск 1", "Риск 2"],
  "implementation_plan": "План внедрения (по этапам)"
}}
"""
        return prompt
    
    def _call_gpt(self, prompt: str) -> str:
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            
            payload = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.3,
                    "maxTokens": "2000"
                },
                "messages": [
                    {
                        "role": "system",
                        "text": "Ты — эксперт по AI-стратегии и бизнес-анализу."
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
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'alternatives' in result['result']:
                    return result['result']['alternatives'][0]['message']['text']
            else:
                logger.error(f"YandexGPT API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"YandexGPT error: {e}")
            return None
    
    def _parse_response(self, response: str) -> Dict:
        try:
            # Находим JSON в ответе
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
        
        return self._get_fallback_business_case({}, {})
    
    def _get_fallback_business_case(self, project_data: Dict, roi: Dict) -> Dict:
        return {
            "executive_summary": f"Проект {project_data.get('project_name', '')} показывает потенциальный ROI {roi.get('roi_percentage', 0)}% с периодом окупаемости {roi.get('payback_period', 0)} месяцев.",
            "roi_analysis": f"Инвестиции в AI-агенты окупятся за {roi.get('payback_period', 0)} месяцев.",
            "recommendations": [
                "Начать с пилотного проекта",
                "Внедрить систему мониторинга",
                "Обучить команду работе с AI"
            ],
            "risks": [
                "Технические риски интеграции",
                "Сопротивление изменениям",
                "Качество данных"
            ],
            "implementation_plan": "1. Пилот (1 месяц)\n2. Масштабирование (2 месяца)\n3. Полное внедрение (3 месяца)"
        }

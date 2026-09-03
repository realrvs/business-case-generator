# -*- coding: utf-8 -*-
"""
Business Case Generator - основной модуль генерации бизнес-кейсов
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.services.roi_engine import ROIEngine
from src.services.yandex_gpt import YandexGPT
from src.services.ai_measurement import AIMeasurement

logger = logging.getLogger(__name__)

class BusinessCaseGenerator:
    """
    Генератор бизнес-кейсов с поддержкой AI-рекомендаций
    """
    
    def __init__(self):
        self.roi_engine = ROIEngine()
        self.yandex_gpt = YandexGPT()
        self.ai_measurement = AIMeasurement()
        
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация полного бизнес-кейса
        
        Args:
            data: Входные данные
                - project_name: Название проекта
                - current_costs: Текущие затраты (руб)
                - team_size: Размер команды
                - time_saved: Экономия времени (%)
                - hourly_rate: Стоимость часа работы (руб)
                
        Returns:
            Dict с полным бизнес-кейсом
        """
        try:
            # 1. Расчет ROI
            roi_result = self.roi_engine.calculate(data)
            logger.info(f"ROI рассчитан: {roi_result['roi_percentage']}%")
            
            # 2. AI-рекомендации через YandexGPT
            ai_recommendations = self._get_ai_recommendations(data, roi_result)
            
            # 3. 4-квадрантная оценка
            assessment = self.ai_measurement.assess(data, roi_result)
            
            # 4. Формирование сводки
            summary = self._generate_summary(data, roi_result, assessment)
            
            # 5. Сборка результата
            result = {
                'project_name': data.get('project_name', 'Бизнес-кейс'),
                'generated_at': datetime.now().isoformat(),
                'summary': summary,
                'roi': roi_result,
                'recommendations': ai_recommendations.get('recommendations', []),
                'risks': ai_recommendations.get('risks', []),
                'assessment': assessment,
                'analysis': self._generate_analysis(data, roi_result, assessment),
                'implementation_plan': ai_recommendations.get('implementation_plan', 
                    '1. Начать с пилотного проекта\n2. Внедрить систему мониторинга\n3. Масштабировать на всю команду'),
                'kpis': {
                    'roi_target': f"> {roi_result['roi_percentage'] + 20}%",
                    'payback_period': f"{roi_result['payback_period']} месяцев",
                    'monthly_savings': roi_result['monthly_savings']
                }
            }
            
            logger.info(f"Бизнес-кейс для '{result['project_name']}' сгенерирован")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка генерации бизнес-кейса: {e}")
            return self._generate_fallback(data)
    
    def _get_ai_recommendations(self, data: Dict, roi_result: Dict) -> Dict:
        """Получение AI-рекомендаций через YandexGPT"""
        try:
            if self.yandex_gpt.is_available:
                return self.yandex_gpt.generate_business_case(data, roi_result)
            else:
                logger.warning("YandexGPT недоступен, используются стандартные рекомендации")
                return self._get_default_recommendations(data, roi_result)
        except Exception as e:
            logger.error(f"Ошибка получения AI-рекомендаций: {e}")
            return self._get_default_recommendations(data, roi_result)
    
    def _get_default_recommendations(self, data: Dict, roi_result: Dict) -> Dict:
        """Стандартные рекомендации (fallback)"""
        team_size = data.get('team_size', 1)
        roi = roi_result.get('roi_percentage', 0)
        
        recommendations = [
            "Начать с пилотного проекта на одном процессе",
            "Внедрить систему мониторинга эффективности",
            "Обучить команду работе с AI-агентами"
        ]
        
        if roi > 200:
            recommendations.append("Рассмотреть расширение на смежные отделы")
        elif roi > 100:
            recommendations.append("Масштабировать решение на всю команду")
        
        risks = [
            {'level': 'HIGH' if roi < 50 else 'MEDIUM', 
             'description': 'Сопротивление команды внедрению AI' if roi < 100 else 'Технические риски интеграции'}
        ]
        
        return {
            'recommendations': recommendations,
            'risks': risks,
            'implementation_plan': '1. Анализ текущих процессов\n2. Пилотное внедрение\n3. Сбор метрик\n4. Масштабирование'
        }
    
    def _generate_summary(self, data: Dict, roi_result: Dict, assessment: Dict) -> str:
        """Генерация краткой сводки"""
        project_name = data.get('project_name', 'Проект')
        roi = roi_result.get('roi_percentage', 0)
        payback = roi_result.get('payback_period', 0)
        
        summary = f"Проект '{project_name}' показывает ROI в размере {roi}% "
        if payback < 12:
            summary += f"с окупаемостью менее {payback} месяцев. "
        else:
            summary += f"с окупаемостью {payback} месяцев. "
        
        if roi > 100:
            summary += "Проект имеет высокий потенциал и рекомендуется к реализации."
        elif roi > 50:
            summary += "Проект имеет умеренный потенциал, рекомендуется рассмотреть."
        else:
            summary += "Проект требует дополнительного анализа."
        
        return summary
    
    def _generate_analysis(self, data: Dict, roi_result: Dict, assessment: Dict) -> Dict:
        """Детальный анализ"""
        return {
            'investment_analysis': {
                'total_investment': roi_result.get('total_investment', 0),
                'ai_costs': roi_result.get('ai_costs', 0),
                'current_costs': data.get('current_costs', 0)
            },
            'savings_analysis': {
                'monthly_savings': roi_result.get('monthly_savings', 0),
                'annual_savings': roi_result.get('annual_savings', 0),
                'time_saved': data.get('time_saved', 0)
            },
            'risk_analysis': assessment.get('risks', []),
            'strategic_value': assessment.get('strategic_value', 'Средняя')
        }
    
    def _generate_fallback(self, data: Dict) -> Dict:
        """Fallback при ошибке"""
        return {
            'project_name': data.get('project_name', 'Бизнес-кейс'),
            'generated_at': datetime.now().isoformat(),
            'summary': 'Бизнес-кейс сгенерирован с базовыми расчетами',
            'roi': self.roi_engine.calculate(data),
            'recommendations': ['Начать с пилотного проекта', 'Внедрить систему мониторинга'],
            'risks': [{'level': 'MEDIUM', 'description': 'Риски внедрения'}],
            'assessment': {'quadrant': 'Анализ выполнен частично'},
            'analysis': {'status': 'Частичный анализ'},
            'implementation_plan': '1. Пилот\n2. Анализ\n3. Внедрение',
            'kpis': {'roi_target': '> 100%', 'payback_period': '< 12 месяцев'}
        }

# -*- coding: utf-8 -*-
"""
AI Measurement - 4-квадрантная оценка проектов
"""
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class AIMeasurement:
    """
    4-квадрантная оценка проектов по внедрению AI
    """
    
    def assess(self, data: Dict[str, Any], roi_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проведение 4-квадрантной оценки
        
        Квадранты:
        1. Business Value (Бизнес-ценность) - низкая/высокая
        2. Implementation Complexity (Сложность внедрения) - низкая/высокая
        3. ROI Potential (Потенциал ROI)
        4. Strategic Impact (Стратегическое влияние)
        
        Args:
            data: Входные данные проекта
            roi_result: Результаты расчета ROI
            
        Returns:
            Dict с оценкой по всем квадрантам
        """
        try:
            # 1. Оценка бизнес-ценности
            business_value = self._assess_business_value(data, roi_result)
            
            # 2. Оценка сложности внедрения
            implementation_complexity = self._assess_complexity(data)
            
            # 3. Оценка ROI потенциала
            roi_potential = self._assess_roi_potential(roi_result)
            
            # 4. Оценка стратегического влияния
            strategic_impact = self._assess_strategic_impact(data, roi_result)
            
            # Определение квадранта
            quadrant = self._determine_quadrant(business_value, implementation_complexity)
            
            # Сборка результата
            assessment = {
                'quadrant': quadrant,
                'business_value': {
                    'score': business_value['score'],
                    'level': business_value['level'],
                    'description': business_value['description']
                },
                'implementation_complexity': {
                    'score': implementation_complexity['score'],
                    'level': implementation_complexity['level'],
                    'description': implementation_complexity['description']
                },
                'roi_potential': {
                    'score': roi_potential['score'],
                    'level': roi_potential['level'],
                    'projection': roi_potential['projection']
                },
                'strategic_impact': {
                    'score': strategic_impact['score'],
                    'level': strategic_impact['level'],
                    'description': strategic_impact['description']
                },
                'recommendations': self._generate_recommendations(quadrant, data, roi_result),
                'risks': self._identify_risks(quadrant, data)
            }
            
            logger.info(f"4-квадрантная оценка завершена: {quadrant}")
            return assessment
            
        except Exception as e:
            logger.error(f"Ошибка при оценке: {e}")
            return self._get_default_assessment()
    
    def _assess_business_value(self, data: Dict, roi_result: Dict) -> Dict:
        """Оценка бизнес-ценности"""
        roi = roi_result.get('roi_percentage', 0)
        savings = roi_result.get('monthly_savings', 0)
        
        if roi > 200:
            score = 90
            level = "HIGH"
            description = "Очень высокая бизнес-ценность, значительная экономия"
        elif roi > 100:
            score = 70
            level = "HIGH"
            description = "Высокая бизнес-ценность, хорошая экономия"
        elif roi > 50:
            score = 50
            level = "MEDIUM"
            description = "Средняя бизнес-ценность, умеренная экономия"
        elif roi > 0:
            score = 30
            level = "LOW"
            description = "Низкая бизнес-ценность, минимальная экономия"
        else:
            score = 10
            level = "LOW"
            description = "Очень низкая бизнес-ценность"
        
        return {'score': score, 'level': level, 'description': description}
    
    def _assess_complexity(self, data: Dict) -> Dict:
        """Оценка сложности внедрения"""
        team_size = data.get('team_size', 1)
        time_saved = data.get('time_saved', 0)
        
        # Оценка сложности на основе размера команды и объема изменений
        complexity_score = min(100, (team_size * 10) + (time_saved / 2))
        
        if complexity_score > 70:
            level = "HIGH"
            description = "Высокая сложность внедрения, требуется значительная трансформация"
        elif complexity_score > 40:
            level = "MEDIUM"
            description = "Средняя сложность внедрения"
        else:
            level = "LOW"
            description = "Низкая сложность внедрения, быстрая реализация"
        
        return {'score': complexity_score, 'level': level, 'description': description}
    
    def _assess_roi_potential(self, roi_result: Dict) -> Dict:
        """Оценка потенциала ROI"""
        roi = roi_result.get('roi_percentage', 0)
        payback = roi_result.get('payback_period', 12)
        
        if roi > 200 and payback < 6:
            score = 95
            level = "EXCELLENT"
            projection = "Исключительный потенциал, быстрая окупаемость"
        elif roi > 100 and payback < 12:
            score = 75
            level = "HIGH"
            projection = "Высокий потенциал, хорошая окупаемость"
        elif roi > 50 and payback < 18:
            score = 55
            level = "MEDIUM"
            projection = "Средний потенциал, умеренная окупаемость"
        else:
            score = 25
            level = "LOW"
            projection = "Низкий потенциал, длительная окупаемость"
        
        return {'score': score, 'level': level, 'projection': projection}
    
    def _assess_strategic_impact(self, data: Dict, roi_result: Dict) -> Dict:
        """Оценка стратегического влияния"""
        team_size = data.get('team_size', 1)
        roi = roi_result.get('roi_percentage', 0)
        
        # Стратегическое влияние зависит от масштаба и ROI
        impact_score = min(100, (team_size * 5) + (roi / 2))
        
        if impact_score > 75:
            level = "HIGH"
            description = "Высокое стратегическое влияние, трансформация процессов"
        elif impact_score > 40:
            level = "MEDIUM"
            description = "Среднее стратегическое влияние, улучшение процессов"
        else:
            level = "LOW"
            description = "Низкое стратегическое влияние, точечное улучшение"
        
        return {'score': impact_score, 'level': level, 'description': description}
    
    def _determine_quadrant(self, business_value: Dict, complexity: Dict) -> str:
        """Определение квадранта на основе оценок"""
        bv_level = business_value['level']
        comp_level = complexity['level']
        
        if bv_level == "HIGH" and comp_level == "LOW":
            return "QUICK_WINS (Быстрые победы)"
        elif bv_level == "HIGH" and comp_level == "HIGH":
            return "STRATEGIC_PROJECTS (Стратегические проекты)"
        elif bv_level == "LOW" and comp_level == "LOW":
            return "FILLER_PROJECTS (Вспомогательные проекты)"
        else:
            return "MAYBE_PROJECTS (Проекты под вопросом)"
    
    def _generate_recommendations(self, quadrant: str, data: Dict, roi_result: Dict) -> List[str]:
        """Генерация рекомендаций на основе квадранта"""
        recommendations = {
            "QUICK_WINS": [
                "✓ Немедленно начать внедрение",
                "✓ Быстрая победа - отличный ROI",
                "✓ Использовать как пилотный проект для демонстрации"
            ],
            "STRATEGIC_PROJECTS": [
                "✓ Начать с детального планирования",
                "✓ Выделить отдельную команду внедрения",
                "✓ Провести обучение сотрудников"
            ],
            "FILLER_PROJECTS": [
                "✓ Внедрить в свободное время",
                "✓ Использовать как обучение для команды",
                "✓ Не требовать быстрых результатов"
            ],
            "MAYBE_PROJECTS": [
                "✓ Провести дополнительный анализ",
                "✓ Уточнить требования и ожидания",
                "✓ Рассмотреть альтернативные подходы"
            ]
        }
        
        return recommendations.get(quadrant, ["✓ Провести дополнительный анализ"])
    
    def _identify_risks(self, quadrant: str, data: Dict) -> List[Dict]:
        """Идентификация рисков"""
        risks = []
        
        if "STRATEGIC" in quadrant:
            risks.append({
                'level': 'HIGH',
                'description': 'Высокая сложность реализации'
            })
            risks.append({
                'level': 'MEDIUM',
                'description': 'Длительный срок окупаемости'
            })
        
        if "MAYBE" in quadrant:
            risks.append({
                'level': 'HIGH',
                'description': 'Неопределенность ROI'
            })
        
        risks.append({
            'level': 'LOW',
            'description': 'Стандартные риски внедрения'
        })
        
        return risks
    
    def _get_default_assessment(self) -> Dict:
        """Default assessment при ошибке"""
        return {
            'quadrant': 'ANALYSIS_NEEDED (Требуется анализ)',
            'business_value': {'score': 50, 'level': 'MEDIUM', 'description': 'Требуется уточнение'},
            'implementation_complexity': {'score': 50, 'level': 'MEDIUM', 'description': 'Требуется уточнение'},
            'roi_potential': {'score': 50, 'level': 'MEDIUM', 'projection': 'Требуется уточнение'},
            'strategic_impact': {'score': 50, 'level': 'MEDIUM', 'description': 'Требуется уточнение'},
            'recommendations': ['Провести дополнительный анализ'],
            'risks': [{'level': 'MEDIUM', 'description': 'Неопределенность параметров'}]
        }

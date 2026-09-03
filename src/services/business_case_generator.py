# -*- coding: utf-8 -*-
from typing import Dict, Any, List
from src.services.roi_engine import ROIEngine
from src.services.ai_measurement import AIMeasurement
import logging
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class BusinessCaseGenerator:
    def __init__(self):
        self.roi_engine = ROIEngine()
        self.measurement = AIMeasurement()
        self.feedback_file = "feedback.json"
    
    def generate(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        roi = self.roi_engine.calculate(project_data)
        measurement = self.measurement.calculate(project_data)
        
        result = {
            "project_name": project_data.get("project_name", "Unknown Project"),
            "summary": self._generate_summary(project_data, roi),
            "roi": roi,
            "measurement": measurement,
            "recommendations": self._generate_recommendations(project_data, roi, measurement),
            "risks": self._identify_risks(project_data, roi),
            "implementation_plan": self._generate_implementation_plan(project_data, roi),
            "feedback": {
                "status": "pending",  # pending, approved, rejected, revised
                "rating": None,       # 1-5
                "comment": None,
                "approved_by": None,
                "approved_at": None,
                "revision_notes": None
            }
        }
        
        return result
    
    def save_feedback(self, project_name: str, feedback_data: Dict[str, Any]) -> bool:
        try:
            # Загружаем существующие отзывы
            feedbacks = self._load_feedbacks()
            
            # Находим или создаем запись
            existing = None
            for item in feedbacks:
                if item.get("project_name") == project_name:
                    existing = item
                    break
            
            if existing:
                existing["feedback"] = feedback_data
                existing["updated_at"] = datetime.now().isoformat()
            else:
                feedbacks.append({
                    "project_name": project_name,
                    "feedback": feedback_data,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                })
            
            self._save_feedbacks(feedbacks)
            logger.info(f"✅ Обратная связь сохранена для проекта {project_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения обратной связи: {e}")
            return False
    
    def get_feedback(self, project_name: str) -> Dict[str, Any]:
        feedbacks = self._load_feedbacks()
        for item in feedbacks:
            if item.get("project_name") == project_name:
                return item.get("feedback", {})
        return {}
    
    def _load_feedbacks(self) -> List[Dict]:
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_feedbacks(self, feedbacks: List[Dict]):
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)
    
    def _generate_summary(self, project_data: Dict, roi: Dict) -> str:
        return f"Внедрение AI-агентов в проект '{project_data.get('project_name')}' обеспечит ROI {roi.get('roi_percentage', 0):.1f}% с периодом окупаемости {roi.get('payback_period', 0):.1f} месяцев."
    
    def _generate_recommendations(self, project_data: Dict, roi: Dict, measurement: Dict) -> List[str]:
        recs = [
            "Начать с пилотного проекта на одном процессе",
            "Внедрить систему мониторинга эффективности",
            "Обучить команду работе с AI-агентами"
        ]
        
        if roi.get("roi_percentage", 0) > 100:
            recs.append("Масштабировать решение на другие процессы")
        
        if measurement.get("technical", {}).get("accuracy", 0) < 0.8:
            recs.append("Улучшить качество данных для обучения моделей")
        
        return recs
    
    def _identify_risks(self, project_data: Dict, roi: Dict) -> List[Dict]:
        risks = []
        
        if roi.get("roi_percentage", 0) < 50:
            risks.append({
                "level": "HIGH",
                "description": "Низкий ROI — требуется пересмотр подхода"
            })
        
        if project_data.get("team_size", 0) > 10:
            risks.append({
                "level": "MEDIUM",
                "description": "Большая команда — сложность внедрения"
            })
        
        if project_data.get("current_costs", 0) < 100000:
            risks.append({
                "level": "LOW",
                "description": "Низкие текущие затраты — экономия может быть незначительной"
            })
        
        return risks
    
    def _generate_implementation_plan(self, project_data: Dict, roi: Dict) -> str:
        return """
**Этап 1: Подготовка (1-2 недели)**
- Анализ текущих процессов
- Сбор данных для обучения моделей
- Формирование команды внедрения

**Этап 2: Пилотный проект (2-4 недели)**
- Разработка и настройка AI-агентов
- Тестирование на ограниченном наборе задач
- Сбор обратной связи

**Этап 3: Масштабирование (1-2 месяца)**
- Расширение на все процессы
- Интеграция с существующими системами
- Обучение сотрудников

**Этап 4: Полное внедрение (1 месяц)**
- Запуск в промышленную эксплуатацию
- Мониторинг и оптимизация
- Достижение целевых показателей ROI
"""

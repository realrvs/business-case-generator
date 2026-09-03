# -*- coding: utf-8 -*-
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BusinessCaseChat:
    def __init__(self):
        self.history = []
        self.context = {}
    
    def start_chat(self, project_name: str, business_case: Dict[str, Any]) -> Dict[str, Any]:
        self.context = {
            "project_name": project_name,
            "business_case": business_case,
            "started_at": datetime.now().isoformat()
        }
        self.history = []
        
        # Приветственное сообщение
        welcome = self._generate_welcome(business_case)
        self.history.append({"role": "assistant", "content": welcome})
        
        return {
            "project_name": project_name,
            "message": welcome,
            "history": self.history
        }
    
    def send_message(self, message: str) -> Dict[str, Any]:
        # Добавляем сообщение пользователя
        self.history.append({"role": "user", "content": message})
        
        # Генерируем ответ AI
        response = self._generate_response(message)
        self.history.append({"role": "assistant", "content": response})
        
        return {
            "message": response,
            "history": self.history
        }
    
    def _generate_welcome(self, business_case: Dict) -> str:
        project_name = business_case.get("project_name", "")
        roi = business_case.get("roi", {}).get("roi_percentage", 0)
        payback = business_case.get("roi", {}).get("payback_period", 0)
        
        return f"""
👋 Здравствуйте! Я ваш AI-ассистент по бизнес-кейсу **{project_name}**.

📊 **Краткая сводка:**
- ROI: {roi:.1f}%
- Окупаемость: {payback:.1f} месяцев

❓ **Что я могу сделать:**
- Ответить на вопросы по бизнес-кейсу
- Уточнить данные для расчета
- Предложить улучшения
- Обсудить риски
- Помочь с планом внедрения

💡 **Примеры вопросов:**
- "Как можно улучшить ROI?"
- "Какие основные риски?"
- "Что делать, если команда сопротивляется?"
- "Какие альтернативные подходы?"
- "Как ускорить внедрение?"

Чем могу помочь?
"""
    
    def _generate_response(self, message: str) -> str:
        # Анализируем сообщение
        message_lower = message.lower()
        
        # Определяем тип вопроса
        if any(word in message_lower for word in ["roi", "окупаемость", "выгода"]):
            return self._handle_roi_question(message)
        
        elif any(word in message_lower for word in ["риск", "опасн", "проблем"]):
            return self._handle_risk_question(message)
        
        elif any(word in message_lower for word in ["план", "внедрен", "этап", "срок"]):
            return self._handle_plan_question(message)
        
        elif any(word in message_lower for word in ["команд", "люд", "сопротивл"]):
            return self._handle_team_question(message)
        
        elif any(word in message_lower for word in ["альтернатив", "друг", "вариант"]):
            return self._handle_alternative_question(message)
        
        elif any(word in message_lower for word in ["улучш", "оптимиз", "лучш"]):
            return self._handle_improvement_question(message)
        
        else:
            return self._handle_general_question(message)
    
    def _handle_roi_question(self, message: str) -> str:
        roi = self.context.get("business_case", {}).get("roi", {})
        roi_percentage = roi.get("roi_percentage", 0)
        payback = roi.get("payback_period", 0)
        monthly_savings = roi.get("monthly_savings", 0)
        ai_costs = roi.get("ai_costs", 0)
        
        response = f"""
📊 **Анализ ROI**

Текущие показатели:
- ROI: {roi_percentage:.1f}%
- Окупаемость: {payback:.1f} месяцев
- Экономия: {monthly_savings:,.0f} ₽/мес
- Затраты на AI: {ai_costs:,.0f} ₽/мес

💡 **Как улучшить ROI:**
1. Увеличить экономию времени (сейчас {self.context.get('business_case', {}).get('time_saved', 0)} часов/мес)
2. Снизить затраты на AI (сейчас {ai_costs:,.0f} ₽/мес)
3. Повысить стоимость часа работы

Хотите провести перерасчет с новыми параметрами?
"""
        return response
    
    def _handle_risk_question(self, message: str) -> str:
        risks = self.context.get("business_case", {}).get("risks", [])
        
        if not risks:
            return "⚠️ В текущем бизнес-кейсе риски не идентифицированы. Хотите провести анализ рисков?"
        
        response = "⚠️ **Анализ рисков:**\n\n"
        for risk in risks:
            level = risk.get("level", "MEDIUM")
            desc = risk.get("description", "")
            response += f"- **{level}**: {desc}\n"
        
        response += """
\n💡 **Рекомендации:**
1. Разработать план митигации для HIGH рисков
2. Назначить ответственных за мониторинг рисков
3. Регулярно пересматривать риски

Хотите обсудить конкретный риск?
"""
        return response
    
    def _handle_plan_question(self, message: str) -> str:
        plan = self.context.get("business_case", {}).get("implementation_plan", "")
        
        if not plan:
            return "📋 **План внедрения не сгенерирован.** Хотите, я помогу создать план?"
        
        return f"""
📋 **План внедрения:**

{plan}

💡 **Что можно уточнить:**
- Сроки по каждому этапу
- Необходимые ресурсы
- Критерии успеха
- Бюджет этапов

Что именно хотите обсудить?
"""
    
    def _handle_team_question(self, message: str) -> str:
        team_size = self.context.get("business_case", {}).get("team_size", 0)
        
        response = f"""
👥 **Команда и внедрение**

Размер команды: {team_size} человек

💡 **Рекомендации по работе с командой:**
1. Обучение: 2-3 дня на человека
2. Пилотная группа: 2-3 человека
3. Постоянная обратная связь
4. Демонстрация результатов каждые 2 недели

**Как уменьшить сопротивление:**
1. Показать выгоды для каждого сотрудника
2. Вовлечь в процесс принятия решений
3. Создать "послов изменений"
4. Признавать и поощрять адаптацию

Хотите детальнее обсудить работу с командой?
"""
        return response
    
    def _handle_alternative_question(self, message: str) -> str:
        return """
🔄 **Альтернативные подходы:**

1. **Постепенное внедрение** (Low Risk)
   - Начать с одного процесса
   - Поэтапное расширение
   - Минимальные риски

2. **Гибридный подход** (Medium Risk)
   - AI + люди параллельно
   - Постоянное сравнение
   - Быстрая обратная связь

3. **Полная автоматизация** (High Risk)
   - Быстрый результат
   - Высокие риски
   - Максимальный ROI

**Рекомендация:** Начните с гибридного подхода, затем масштабируйте.

Какой подход вас интересует?
"""
    
    def _handle_improvement_question(self, message: str) -> str:
        return """
💡 **Предложения по улучшению:**

1. **Данные:**
   - Собрать больше данных для обучения
   - Использовать реальные кейсы

2. **Процессы:**
   - Оптимизировать текущие процессы до внедрения
   - Стандартизировать операции

3. **Технологии:**
   - Использовать более точные модели
   - Настроить систему мониторинга

4. **Команда:**
   - Провести тренинг "AI для всех"
   - Создать базу знаний

Какое улучшение вас интересует?
"""
    
    def _handle_general_question(self, message: str) -> str:
        return """
🤖 **Я ваш AI-ассистент**

Я могу помочь с вопросами по:
- 📊 ROI и финансам
- ⚠️ Рискам и их митигации
- 📋 Плану внедрения
- 👥 Команде и изменениям
- 💡 Альтернативным подходам
- 🚀 Улучшению бизнес-кейса

Задайте конкретный вопрос, и я постараюсь помочь!
"""

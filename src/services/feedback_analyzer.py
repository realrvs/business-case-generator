# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

class FeedbackAnalyzer:
    def __init__(self):
        self.feedback_file = "feedback.json"
    
    def analyze_feedback(self, project_name: str) -> Dict[str, Any]:
        feedbacks = self._load_feedbacks()
        
        for item in feedbacks:
            if item.get("project_name") == project_name:
                fb = item.get("feedback", {})
                return {
                    "status": fb.get("status", "pending"),
                    "rating": fb.get("rating", 0),
                    "comment": fb.get("comment", ""),
                    "revision_notes": fb.get("revision_notes", ""),
                    "approved_by": fb.get("approved_by", ""),
                    "created_at": item.get("created_at", ""),
                    "updated_at": item.get("updated_at", "")
                }
        
        return {"status": "pending", "rating": 0, "comment": ""}
    
    def get_improvement_suggestions(self, feedback: Dict[str, Any]) -> List[str]:
        suggestions = []
        rating = feedback.get("rating", 0)
        comment = feedback.get("comment", "").lower()
        revision_notes = feedback.get("revision_notes", "").lower()
        
        # Анализ на основе рейтинга
        if rating <= 2:
            suggestions.append("Требуется полный пересмотр бизнес-кейса")
        elif rating <= 3:
            suggestions.append("Требуется доработка ключевых разделов")
        
        # Анализ на основе комментариев
        if "roi" in comment or "окупаемость" in comment:
            suggestions.append("Пересчитать ROI с новыми данными")
        
        if "риск" in comment or "risk" in comment:
            suggestions.append("Добавить план митигации рисков")
        
        if "план" in comment or "срок" in comment:
            suggestions.append("Детализировать план внедрения")
        
        if "цифра" in comment or "данные" in comment:
            suggestions.append("Добавить больше количественных данных")
        
        # Анализ revision_notes
        if revision_notes:
            suggestions.append("Учесть замечания: " + revision_notes[:100])
        
        return suggestions
    
    def _load_feedbacks(self) -> List[Dict]:
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

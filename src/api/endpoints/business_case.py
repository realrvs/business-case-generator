# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

from src.services.business_case_generator import BusinessCaseGenerator
from src.services.feedback_analyzer import FeedbackAnalyzer

router = APIRouter(prefix="/business-case", tags=["business-case"])

class FeedbackRequest(BaseModel):
    project_name: str
    status: str
    rating: Optional[int] = None
    comment: Optional[str] = None
    approved_by: Optional[str] = None
    revision_notes: Optional[str] = None

class ImprovedBusinessCaseRequest(BaseModel):
    project_name: str
    feedback: Dict[str, Any]

@router.post("/generate")
async def generate_business_case(project_data: Dict[str, Any]):
    if not project_data.get("project_name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="project_name is required"
        )
    
    generator = BusinessCaseGenerator()
    result = generator.generate(project_data)
    
    # Добавляем историю версий
    result["version"] = 1
    result["generated_at"] = datetime.now().isoformat()
    
    return result

@router.post("/feedback")
async def save_feedback(feedback: FeedbackRequest):
    generator = BusinessCaseGenerator()
    
    feedback_data = {
        "status": feedback.status,
        "rating": feedback.rating,
        "comment": feedback.comment,
        "approved_by": feedback.approved_by,
        "approved_at": datetime.now().isoformat(),
        "revision_notes": feedback.revision_notes
    }
    
    success = generator.save_feedback(feedback.project_name, feedback_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save feedback"
        )
    
    return {
        "message": "✅ Обратная связь сохранена",
        "project": feedback.project_name,
        "feedback": feedback_data
    }

@router.get("/feedback/{project_name}")
async def get_feedback(project_name: str):
    generator = BusinessCaseGenerator()
    feedback = generator.get_feedback(project_name)
    return {
        "project_name": project_name,
        "feedback": feedback
    }

@router.get("/feedback/analysis/{project_name}")
async def analyze_feedback(project_name: str):
    analyzer = FeedbackAnalyzer()
    feedback = analyzer.analyze_feedback(project_name)
    suggestions = analyzer.get_improvement_suggestions(feedback)
    
    return {
        "project_name": project_name,
        "feedback": feedback,
        "suggestions": suggestions
    }

@router.post("/improve")
async def improve_business_case(request: ImprovedBusinessCaseRequest):
    # 1. Получаем исходный бизнес-кейс
    generator = BusinessCaseGenerator()
    original_result = generator.generate({"project_name": request.project_name})
    
    # 2. Анализируем обратную связь
    analyzer = FeedbackAnalyzer()
    feedback = request.feedback
    suggestions = analyzer.get_improvement_suggestions(feedback)
    
    # 3. Генерируем улучшенную версию
    improved = original_result.copy()
    improved["version"] = 2
    improved["improved_at"] = datetime.now().isoformat()
    improved["feedback_applied"] = suggestions
    
    # 4. Улучшаем рекомендации на основе feedback
    recs = improved.get("recommendations", [])
    if feedback.get("rating", 0) <= 3:
        recs.append("Пересмотреть подход на основе полученной обратной связи")
    if feedback.get("revision_notes"):
        recs.append(f"Учесть замечания: {feedback.get('revision_notes', '')[:100]}")
    improved["recommendations"] = recs
    
    # 5. Обновляем резюме
    summary = improved.get("summary", "")
    if feedback.get("rating", 0) <= 2:
        summary = summary + " Требуется пересмотр с учетом замечаний."
    improved["summary"] = summary
    
    return improved

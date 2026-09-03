# app/api/endpoints/business_case.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.sqlalchemy.user import User
from app.services.business.generator import BusinessCaseGenerator

router = APIRouter(prefix="/business-case", tags=["business-case"])

@router.post("/generate")
async def generate_business_case(
    project_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    generator = BusinessCaseGenerator()
    result = generator.generate(project_data)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result

@router.get("/roi/{project_id}")
async def get_roi_analysis(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: Получение ROI анализа из БД
    return {"project_id": project_id, "roi": 247}

@router.get("/measurement/{project_id}")
async def get_ai_measurement(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: Получение 4-Quadrant Measurement из БД
    return {"project_id": project_id, "measurement": {}}

# tests/test_business_case.py
import pytest
from src.services.business_case_generator import BusinessCaseGenerator

def test_generate_business_case():
    generator = BusinessCaseGenerator()
    
    data = {
        "project_name": "IT Service Desk",
        "current_costs": 300000,
        "team_size": 3,
        "time_saved": 80
    }
    
    result = generator.generate(data)
    
    assert "project_name" in result
    assert "roi" in result
    assert "recommendations" in result
    assert result["roi"]["roi_percentage"] > 0

def test_roi_calculation():
    from src.services.roi_engine import ROIEngine
    engine = ROIEngine()
    
    data = {
        "current_costs": 500000,
        "team_size": 5,
        "time_saved": 100
    }
    
    result = engine.calculate(data)
    
    assert result["roi_percentage"] > 0
    assert result["payback_period"] > 0

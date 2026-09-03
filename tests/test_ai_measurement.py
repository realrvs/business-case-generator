# -*- coding: utf-8 -*-
"""
Тесты для AI Measurement и BusinessCaseGenerator
"""
import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.ai_measurement import AIMeasurement
from src.services.business_case_generator import BusinessCaseGenerator
from src.services.roi_engine import ROIEngine

def test_ai_measurement():
    """Тест 4-квадрантной оценки"""
    measurement = AIMeasurement()
    
    # Тестовые данные
    data = {
        'project_name': 'Test Project',
        'current_costs': 300000,
        'team_size': 3,
        'time_saved': 80,
        'hourly_rate': 2000
    }
    
    # Расчет ROI
    engine = ROIEngine()
    roi_result = engine.calculate(data)
    
    # Оценка
    result = measurement.assess(data, roi_result)
    
    # Проверки
    assert 'quadrant' in result
    assert 'business_value' in result
    assert 'implementation_complexity' in result
    assert 'roi_potential' in result
    assert 'strategic_impact' in result
    assert 'recommendations' in result
    assert 'risks' in result
    
    # Проверка уровней
    assert result['business_value']['level'] in ['HIGH', 'MEDIUM', 'LOW']
    assert result['implementation_complexity']['level'] in ['HIGH', 'MEDIUM', 'LOW']

def test_business_case_generator_full():
    """Тест полной генерации бизнес-кейса"""
    gen = BusinessCaseGenerator()
    
    # Мокаем YandexGPT
    gen.yandex_gpt.is_available = False
    
    data = {
        'project_name': 'Test Project',
        'current_costs': 300000,
        'team_size': 3,
        'time_saved': 80,
        'hourly_rate': 2000
    }
    
    result = gen.generate(data)
    
    # Проверка всех полей
    assert 'project_name' in result
    assert 'summary' in result
    assert 'roi' in result
    assert 'recommendations' in result
    assert 'risks' in result
    assert 'assessment' in result
    assert 'analysis' in result
    assert 'implementation_plan' in result
    assert 'kpis' in result
    
    # Проверка ROI
    assert result['roi']['roi_percentage'] > 0
    assert result['roi']['payback_period'] > 0

def test_ai_measurement_edge_cases():
    """Тест крайних случаев для AI Measurement"""
    measurement = AIMeasurement()
    
    # Тест с нулевыми значениями
    data = {
        'project_name': 'Zero Project',
        'current_costs': 0,
        'team_size': 1,
        'time_saved': 0,
        'hourly_rate': 0
    }
    
    engine = ROIEngine()
    roi_result = engine.calculate(data)
    result = measurement.assess(data, roi_result)
    
    # Должен вернуть корректные значения
    assert 'quadrant' in result
    assert 'business_value' in result
    
    # Тест с большими значениями
    data = {
        'project_name': 'Large Project',
        'current_costs': 10000000,
        'team_size': 50,
        'time_saved': 90,
        'hourly_rate': 5000
    }
    
    engine = ROIEngine()
    roi_result = engine.calculate(data)
    result = measurement.assess(data, roi_result)
    
    assert result['business_value']['level'] == 'HIGH'

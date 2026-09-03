# -*- coding: utf-8 -*-
import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Добавляем корень проекта в путь для надежности
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.business_case_generator import BusinessCaseGenerator
from src.services.roi_engine import ROIEngine

def test_generate_business_case():
    gen = BusinessCaseGenerator()
    
    # Мокаем YandexGPT
    gen.yandex_gpt = Mock()
    gen.yandex_gpt.generate_business_case = Mock(return_value={
        'executive_summary': 'Test summary',
        'problem_analysis': 'Test problem analysis',
        'solution_description': 'Test solution',
        'financial_analysis': 'Test financial analysis',
        'recommendations': ['Rec 1', 'Rec 2'],
        'risks': [{'level': 'HIGH', 'description': 'Risk 1'}],
        'implementation_plan': 'Plan',
        'kpis': {'roi_target': '> 100%'}
    })
    
    result = gen.generate({
        'project_name': 'Test Project',
        'current_costs': 300000,
        'team_size': 3,
        'time_saved': 80,
        'hourly_rate': 2000
    })
    
    assert 'roi' in result
    assert 'recommendations' in result
    assert 'summary' in result
    assert result['roi']['roi_percentage'] > 0
    assert len(result['recommendations']) >= 2

def test_roi_calculation():
    engine = ROIEngine()
    result = engine.calculate({
        'current_costs': 300000,
        'team_size': 3,
        'time_saved': 80,
        'hourly_rate': 2000
    })
    
    assert result['roi_percentage'] > 0
    assert result['payback_period'] > 0
    assert result['monthly_savings'] > 0
    assert result['ai_costs'] == 150000  # 3 * 50000

def test_roi_engine_edge_cases():
    engine = ROIEngine()
    
    # Тест 1: Нулевые затраты - ожидаем ROI = 0
    result = engine.calculate({
        'current_costs': 0,
        'team_size': 1,
        'time_saved': 0,
        'hourly_rate': 2000
    })
    # Проверяем что ROI >= 0 (не отрицательный)
    assert result['roi_percentage'] >= 0, f"ROI должен быть >= 0, получено {result['roi_percentage']}"
    
    # Тест 2: Большой размер команды
    result = engine.calculate({
        'current_costs': 1000000,
        'team_size': 20,
        'time_saved': 200,
        'hourly_rate': 2000
    })
    assert result['ai_costs'] == 1000000  # 20 * 50000

def test_business_case_generator_without_yandex():
    gen = BusinessCaseGenerator()
    
    # Мокаем YandexGPT, чтобы он возвращал None
    gen.yandex_gpt = Mock()
    gen.yandex_gpt.is_available = False
    gen.yandex_gpt.generate_business_case = Mock(return_value=None)
    
    result = gen.generate({
        'project_name': 'Test',
        'current_costs': 100000,
        'team_size': 2,
        'time_saved': 40,
        'hourly_rate': 2000
    })
    
    # Должен вернуть fallback ответ
    assert 'roi' in result
    assert 'recommendations' in result
    assert 'summary' in result

if __name__ == '__main__':
    pytest.main(['-v'])

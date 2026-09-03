# app/services/business/generator.py
from typing import Dict, Any, List
from app.services.rag_with_finance import RAGWithFinance
from app.services.yandex_gpt_business import YandexGPTBusiness
from app.services.roi_engine import ROIEngine
import logging

logger = logging.getLogger(__name__)

class BusinessCaseGenerator:
    def __init__(self):
        self.rag = RAGWithFinance()
        self.gpt = YandexGPTBusiness()
        self.roi_engine = ROIEngine()
        
        # Индексируем примеры финансовых данных
        self._index_sample_data()
    
    def _index_sample_data(self):
        sample_data = [
            {
                "project_name": "Автоматизация закупок",
                "costs": 500000,
                "team_size": 5,
                "description": "Автоматизация процесса закупок с использованием AI"
            },
            {
                "project_name": "IT Service Desk",
                "costs": 300000,
                "team_size": 3,
                "description": "AI-агент для обработки заявок в Service Desk"
            }
        ]
        self.rag.index_financial_data(sample_data)
    
    def generate(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 1. Сбор контекста
            context = self.rag.search(project_data.get("project_name", ""))
            
            # 2. Расчет ROI
            roi = self.roi_engine.calculate(project_data)
            
            if "error" in roi:
                return {"error": roi["error"]}
            
            # 3. Генерация отчета
            report = self.gpt.generate_business_case(context, project_data, roi)
            
            return {
                "executive_summary": report.get("executive_summary", ""),
                "roi": roi,
                "payback_period": roi.get("payback_period", 0),
                "recommendations": report.get("recommendations", []),
                "risks": report.get("risks", []),
                "implementation_plan": report.get("implementation_plan", ""),
                "measurement": self._get_measurement(project_data, roi)
            }
        except Exception as e:
            logger.error(f"Ошибка генерации бизнес-кейса: {e}")
            return {"error": str(e)}
    
    def _get_measurement(self, project_data: Dict, roi: Dict) -> Dict:
        from app.services.measurement.quadrant import QuadrantMeasurement
        measurement = QuadrantMeasurement()
        
        metrics = {
            "accuracy": 0.85,
            "latency": 200,
            "drift": 0.02,
            "roi": roi.get("roi_percentage", 0),
            "cost_savings": roi.get("annual_savings", 0),
            "productivity_gain": 30,
            "time_to_market": 45,
            "deployment_time": 14,
            "adoption_rate": 70,
            "user_confidence": 75,
            "error_rate": 0.01,
            "audit_trail": 100
        }
        
        return measurement.measure(metrics)

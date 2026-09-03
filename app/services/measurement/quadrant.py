# app/services/measurement/quadrant.py
from typing import Dict, Any

class QuadrantMeasurement:
    def measure(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "technical": {
                "accuracy": metrics.get("accuracy", 0),
                "latency": metrics.get("latency", 0),
                "drift": metrics.get("drift", 0)
            },
            "business": {
                "roi": metrics.get("roi", 0),
                "cost_savings": metrics.get("cost_savings", 0),
                "productivity_gain": metrics.get("productivity_gain", 0)
            },
            "operational": {
                "time_to_market": metrics.get("time_to_market", 0),
                "deployment_time": metrics.get("deployment_time", 0),
                "adoption_rate": metrics.get("adoption_rate", 0)
            },
            "trust": {
                "user_confidence": metrics.get("user_confidence", 0),
                "error_rate": metrics.get("error_rate", 0),
                "audit_trail": metrics.get("audit_trail", 0)
            }
        }
    
    def score(self, measurement: Dict[str, Any]) -> float:
        # Расчет общего score
        total = 0
        count = 0
        for quadrant in measurement.values():
            for key, value in quadrant.items():
                total += value
                count += 1
        return round(total / count, 2) if count > 0 else 0

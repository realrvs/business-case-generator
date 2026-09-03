# app/services/roi_engine.py
from typing import Dict, Any

class ROIEngine:
    def calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        current_costs = self._calculate_current_costs(data)
        ai_costs = self._calculate_ai_costs(data)
        savings = self._calculate_savings(data)
        
        if ai_costs == 0:
            return {
                "error": "AI costs cannot be zero"
            }
        
        roi = ((savings - ai_costs) / ai_costs) * 100
        
        return {
            "roi_percentage": round(roi, 2),
            "payback_period": round(ai_costs / (savings / 12), 1),
            "annual_savings": round(savings, 2),
            "three_year_impact": round(savings * 3 - ai_costs, 2),
            "current_costs": current_costs,
            "ai_costs": ai_costs
        }
    
    def _calculate_current_costs(self, data: Dict) -> float:
        return data.get("current_costs", 0)
    
    def _calculate_ai_costs(self, data: Dict) -> float:
        team_size = data.get("team_size", 1)
        return team_size * 50000  # Условные 50 000 руб/мес на сотрудника
    
    def _calculate_savings(self, data: Dict) -> float:
        time_saved = data.get("time_saved", 0)  # часов в месяц
        hourly_rate = 2000  # руб/час
        return time_saved * hourly_rate

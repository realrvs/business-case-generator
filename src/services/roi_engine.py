# -*- coding: utf-8 -*-
from typing import Dict, Any

class ROIEngine:
    def calculate(self, data: Dict[str, Any]) -> Dict[str, float]:
        current_costs = data.get("current_costs", 0)
        team_size = data.get("team_size", 1)
        time_saved = data.get("time_saved", 0)
        hourly_rate = data.get("hourly_rate", 2000)
        
        # Затраты на AI
        ai_costs = team_size * 50000
        
        # Экономия
        monthly_savings = time_saved * hourly_rate
        
        # ROI
        if ai_costs > 0:
            roi = ((monthly_savings - ai_costs) / ai_costs) * 100
            payback = ai_costs / (monthly_savings / 12) if monthly_savings > 0 else 999
        else:
            roi = 0
            payback = 999
        
        return {
            "roi_percentage": round(roi, 2),
            "payback_period": round(payback, 1),
            "monthly_savings": round(monthly_savings, 2),
            "annual_savings": round(monthly_savings * 12, 2),
            "ai_costs": round(ai_costs, 2)
        }

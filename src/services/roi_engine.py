class ROIEngine:
    def calculate(self, data):
        current_costs = data.get('current_costs', 0)
        team_size = data.get('team_size', 1)
        time_saved = data.get('time_saved', 0)
        hourly_rate = data.get('hourly_rate', 2000)
        
        # Расчет AI затрат (50,000 руб. на человека)
        ai_costs = team_size * 50000
        
        # Расчет экономии времени
        # Предполагаем 160 рабочих часов в месяц
        monthly_hours = 160
        monthly_savings = (time_saved / 100) * team_size * hourly_rate * monthly_hours
        annual_savings = monthly_savings * 12
        
        # Общие инвестиции
        total_investment = current_costs + ai_costs
        
        # 🔥 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: если нет экономии, ROI = 0
        if annual_savings == 0:
            roi_percentage = 0
            payback_period = 0
        elif total_investment == 0:
            # Нет инвестиций, но есть экономия (маловероятно)
            roi_percentage = 0
            payback_period = 0
        else:
            # ROI = (Прибыль - Инвестиции) / Инвестиции * 100
            profit = annual_savings - total_investment
            roi_percentage = (profit / total_investment) * 100
            
            # Срок окупаемости (месяцев)
            if monthly_savings > 0:
                payback_period = total_investment / monthly_savings
            else:
                payback_period = float('inf')
        
        return {
            'roi_percentage': round(roi_percentage, 2),
            'payback_period': round(payback_period, 2) if payback_period != float('inf') else 0,
            'monthly_savings': round(monthly_savings, 2),
            'annual_savings': round(annual_savings, 2),
            'ai_costs': ai_costs,
            'total_investment': total_investment
        }

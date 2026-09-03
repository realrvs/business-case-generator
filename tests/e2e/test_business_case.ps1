# tests/e2e/test_business_case.ps1
Write-Host "🧪 Тестирование Business Case Generator" -ForegroundColor Cyan

 = "http://localhost:8000/api/v1"

# 1. Логин
 = "username=admin&password=admin123"
 = Invoke-RestMethod -Uri "/auth/login" 
    -Method Post 
    -ContentType "application/x-www-form-urlencoded" 
    -Body  
    -UseBasicParsing

 = .access_token
 = @{ "Authorization" = "Bearer " }

# 2. Генерация бизнес-кейса
 = @{
    project_name = "Автоматизация закупок"
    current_costs = 500000
    team_size = 5
    time_saved = 100
} | ConvertTo-Json

try {
     = Invoke-RestMethod -Uri "/business-case/generate" 
        -Method Post 
        -Headers  
        -Body  
        -ContentType "application/json" 
        -UseBasicParsing
    
    Write-Host "
✅ Бизнес-кейс сгенерирован!" -ForegroundColor Green
    Write-Host "ROI: %" -ForegroundColor Yellow
    Write-Host "Payback Period:  мес" -ForegroundColor Yellow
    
    if (.recommendations) {
        Write-Host "
📌 Рекомендации:" -ForegroundColor Cyan
        .recommendations | ForEach-Object {
            Write-Host "  - " -ForegroundColor White
        }
    }
} catch {
    Write-Host "❌ Ошибка: " -ForegroundColor Red
}

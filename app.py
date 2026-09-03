# -*- coding: utf-8 -*-
"""
Business Case Generator - Streamlit UI
"""
import streamlit as st
import requests
import json
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="Business Case Generator",
    page_icon="📊",
    layout="wide"
)

# Заголовок
st.title("🚀 Business Case Generator")
st.markdown("### Генерация бизнес-кейсов с AI-аналитикой")

# Боковая панель с информацией
with st.sidebar:
    st.header("📋 Информация")
    st.markdown("""
    **Версия:** 1.0.0  
    **Этап:** Core MVP  
    **Статус:** ✅ Активен
    """)
    
    st.divider()
    
    st.subheader("🔗 API Статус")
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API работает")
        else:
            st.warning("⚠️ API недоступен")
    except:
        st.error("❌ API не отвечает")

# Основная форма
st.header("📝 Введите данные проекта")

col1, col2 = st.columns(2)

with col1:
    project_name = st.text_input(
        "Название проекта",
        placeholder="Введите название проекта",
        help="Например: Внедрение AI-агента в поддержку"
    )
    
    current_costs = st.number_input(
        "💰 Текущие затраты (руб)",
        min_value=0,
        value=300000,
        step=10000,
        help="Текущие затраты на процесс"
    )
    
    team_size = st.number_input(
        "👥 Размер команды",
        min_value=1,
        value=3,
        step=1,
        help="Количество сотрудников в команде"
    )

with col2:
    time_saved = st.slider(
        "⏱️ Экономия времени (%)",
        min_value=0,
        max_value=100,
        value=80,
        help="Ожидаемая экономия времени в процентах"
    )
    
    hourly_rate = st.number_input(
        "💵 Стоимость часа работы (руб)",
        min_value=500,
        value=2000,
        step=100,
        help="Средняя стоимость часа работы сотрудника"
    )

# Кнопка генерации
st.divider()
generate_button = st.button(
    "🚀 Сгенерировать бизнес-кейс",
    type="primary",
    use_container_width=True
)

# Результаты
if generate_button:
    if not project_name:
        st.error("❌ Пожалуйста, введите название проекта")
    else:
        with st.spinner("🔄 Генерация бизнес-кейса..."):
            try:
                # Подготовка данных
                data = {
                    "project_name": project_name,
                    "current_costs": current_costs,
                    "team_size": team_size,
                    "time_saved": time_saved,
                    "hourly_rate": hourly_rate
                }
                
                # Запрос к API
                response = requests.post(
                    "http://localhost:8000/api/v1/generate",
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Отображение результатов
                    st.success("✅ Бизнес-кейс успешно сгенерирован!")
                    
                    # Вкладки для результатов
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 ROI Анализ",
                        "📝 Рекомендации",
                        "🎯 4-квадрантная оценка",
                        "📋 Полный отчет"
                    ])
                    
                    with tab1:
                        st.subheader("💰 ROI Анализ")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "ROI",
                                f"{result['roi']['roi_percentage']}%",
                                delta="положительный" if result['roi']['roi_percentage'] > 0 else "отрицательный"
                            )
                        
                        with col2:
                            st.metric(
                                "Окупаемость",
                                f"{result['roi']['payback_period']} мес.",
                                help="Срок окупаемости в месяцах"
                            )
                        
                        with col3:
                            st.metric(
                                "Ежемесячная экономия",
                                f"{result['roi']['monthly_savings']:,.0f} руб.",
                                help="Экономия в месяц"
                            )
                        
                        st.divider()
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            st.info(f"**AI затраты:** {result['roi']['ai_costs']:,.0f} руб.")
                        with col5:
                            st.info(f"**Годовая экономия:** {result['roi'].get('annual_savings', 0):,.0f} руб.")
                    
                    with tab2:
                        st.subheader("💡 Рекомендации")
                        
                        for i, rec in enumerate(result.get('recommendations', []), 1):
                            st.write(f"**{i}.** {rec}")
                        
                        st.divider()
                        
                        st.subheader("⚠️ Риски")
                        for risk in result.get('risks', []):
                            level = risk.get('level', 'MEDIUM')
                            if level == 'HIGH':
                                st.error(f"🔴 **{level}**: {risk.get('description', '')}")
                            elif level == 'MEDIUM':
                                st.warning(f"🟡 **{level}**: {risk.get('description', '')}")
                            else:
                                st.info(f"🟢 **{level}**: {risk.get('description', '')}")
                    
                    with tab3:
                        st.subheader("🎯 4-квадрантная оценка")
                        
                        assessment = result.get('assessment', {})
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Квадрант", assessment.get('quadrant', 'Не определен'))
                            
                            business_value = assessment.get('business_value', {})
                            st.info(f"**Бизнес-ценность:** {business_value.get('level', 'N/A')}")
                            st.caption(business_value.get('description', ''))
                            
                            roi_potential = assessment.get('roi_potential', {})
                            st.info(f"**ROI потенциал:** {roi_potential.get('level', 'N/A')}")
                            st.caption(roi_potential.get('projection', ''))
                        
                        with col2:
                            complexity = assessment.get('implementation_complexity', {})
                            st.warning(f"**Сложность внедрения:** {complexity.get('level', 'N/A')}")
                            st.caption(complexity.get('description', ''))
                            
                            strategic = assessment.get('strategic_impact', {})
                            st.warning(f"**Стратегическое влияние:** {strategic.get('level', 'N/A')}")
                            st.caption(strategic.get('description', ''))
                    
                    with tab4:
                        st.subheader("📋 Полный отчет")
                        
                        st.json(result)
                        
                        # Кнопка скачать отчет
                        if st.button("💾 Скачать отчет (JSON)"):
                            json_str = json.dumps(result, ensure_ascii=False, indent=2)
                            st.download_button(
                                label="📥 Скачать",
                                data=json_str,
                                file_name=f"business_case_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    
                    # Сводка
                    st.divider()
                    st.success(f"📊 Бизнес-кейс для '{project_name}' сгенерирован {datetime.now().strftime('%H:%M:%S')}")
                    
                else:
                    st.error(f"❌ Ошибка API: {response.status_code}")
                    st.write(response.text)
                    
            except requests.exceptions.Timeout:
                st.error("⏰ Таймаут API. Попробуйте позже.")
            except Exception as e:
                st.error(f"❌ Ошибка: {str(e)}")

else:
    st.info("📝 Заполните форму и нажмите 'Сгенерировать бизнес-кейс'")
    
    # Пример
    with st.expander("📖 Пример заполнения"):
        st.code("""
        Название проекта: Внедрение AI-агента в поддержку
        Текущие затраты: 300,000 руб.
        Размер команды: 3 человека
        Экономия времени: 80%
        Стоимость часа: 2,000 руб.
        """)
        st.caption("Результат: ROI ~215%, окупаемость ~5 месяцев")

# Footer
st.divider()
st.caption("💡 Business Case Generator v1.0.0 | Made with ❤️")

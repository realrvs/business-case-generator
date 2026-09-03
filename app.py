# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Генератор бизнес-кейсов", page_icon="📊", layout="wide")
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1a5276; }
    .sub-header { font-size: 1.2rem; color: #5d6d7e; margin-bottom: 2rem; }
    .metric-card { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; padding: 1rem; text-align: center; border-left: 4px solid #1a5276; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #1a5276; }
    .metric-label { font-size: 0.9rem; color: #5d6d7e; }
    .chat-message-user { background: #e3f2fd; padding: 0.8rem 1.2rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #1976d2; }
    .chat-message-assistant { background: #f5f5f5; padding: 0.8rem 1.2rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #757575; }
    .chat-container { max-height: 400px; overflow-y: auto; background: #fafafa; padding: 1rem; border-radius: 10px; border: 1px solid #e0e0e0; }
    .excel-result { background: #d4edda; padding: 1rem; border-radius: 10px; border: 2px solid #28a745; margin-top: 1rem; }
    .footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e9ecef; text-align: center; color: #95a5a6; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🚀 Генератор бизнес-кейсов</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-помощник для создания бизнес-кейсов по внедрению ИИ-агентов</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Настройки")
    api_url = st.text_input("URL API", value="http://localhost:8001/api/v1")
    st.markdown("---")
    st.caption(f"Версия 3.0.0\n{datetime.now().strftime('%d.%m.%Y')}")

st.header("📝 Введите данные проекта")
col1, col2 = st.columns(2)
with col1:
    project_name = st.text_input("Название проекта *", value="Автоматизация IT-поддержки")
    current_costs = st.number_input("💰 Текущие затраты (руб/мес)", min_value=0, value=300000, step=50000)
    team_size = st.number_input("👥 Размер команды", min_value=1, value=3, step=1)
with col2:
    time_saved = st.number_input("⏱️ Экономия времени (часов/мес)", min_value=0, value=80, step=10)
    hourly_rate = st.number_input("💵 Стоимость часа работы (руб)", min_value=0, value=2000, step=500)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate = st.button("🚀 Сгенерировать бизнес-кейс", type="primary", use_container_width=True)

if generate:
    if not project_name:
        st.error("❌ Введите название проекта")
        st.stop()
    with st.spinner("🔄 Генерация..."):
        try:
            payload = {"project_name": project_name, "current_costs": current_costs, "team_size": team_size, "time_saved": time_saved, "hourly_rate": hourly_rate}
            response = requests.post(f"{api_url}/business-case/generate", json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            if response.status_code == 200:
                result = response.json()
                st.session_state['result'] = result
                st.session_state['project_name'] = project_name
                st.rerun()
            else:
                st.error(f"❌ Ошибка: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")

if 'result' in st.session_state:
    result = st.session_state['result']
    project_name = st.session_state['project_name']
    st.success("✅ Бизнес-кейс сгенерирован!")
    st.info(result.get("summary", "Нет данных"))
    roi_data = result.get("roi", {})
    roi_percentage = roi_data.get('roi_percentage', 0)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("ROI", f"{roi_percentage:.1f}%")
    with col2: st.metric("Окупаемость", f"{roi_data.get('payback_period', 0):.1f} мес")
    with col3: st.metric("Экономия/мес", f"{roi_data.get('monthly_savings', 0):,.0f} ₽")
    with col4: st.metric("Затраты на ИИ", f"{roi_data.get('ai_costs', 0):,.0f} ₽/мес")
    
    st.markdown("---")
    st.header("💬 Чат с AI-ассистентом")
    if "chat_started" not in st.session_state:
        try:
            start_response = requests.post(f"{api_url}/business-case/chat/start", json={"project_name": project_name, "business_case": result}, headers={"Content-Type": "application/json"}, timeout=10)
            if start_response.status_code == 200:
                chat_data = start_response.json()
                st.session_state['chat_started'] = True
                st.session_state['chat_history'] = chat_data.get("history", [])
        except Exception as e:
            st.error(f"❌ Ошибка чата: {str(e)}")
    if "chat_history" in st.session_state:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state['chat_history']:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                st.markdown(f'<div class="chat-message-user">👤 {content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-assistant">🤖 {content}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            user_message = st.text_input("Введите сообщение", key="chat_input")
        with col2:
            send_button = st.button("📤 Отправить")
    if send_button and user_message:
        try:
            response = requests.post(f"{api_url}/business-case/chat/message", json={"project_name": project_name, "message": user_message}, headers={"Content-Type": "application/json"}, timeout=30)
            if response.status_code == 200:
                st.session_state['chat_history'] = response.json().get("history", [])
                st.rerun()
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")
    
    st.markdown("---")
    st.header("📊 AI-анализ Excel-модели ROI")
    uploaded_excel = st.file_uploader("Выберите Excel-файл (.xlsx, .xls)", type=['xlsx', 'xls'], key="excel_upload")
    if uploaded_excel and st.button("🧠 Анализировать с AI", key="analyze_excel_ai"):
        with st.spinner("🔄 AI анализирует Excel-модель..."):
            try:
                files = {"file": (uploaded_excel.name, uploaded_excel.getvalue())}
                project_data = {"project_name": project_name, "current_costs": current_costs, "team_size": team_size, "time_saved": time_saved, "hourly_rate": hourly_rate}
                response = requests.post(f"{api_url}/excel/analyze-with-ai", files=files, data={"project_data": json.dumps(project_data)}, timeout=60)
                if response.status_code == 200:
                    st.session_state['excel_result'] = response.json()
                    st.rerun()
                else:
                    st.error(f"❌ Ошибка: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Ошибка: {str(e)}")
    if 'excel_result' in st.session_state:
        excel_result = st.session_state['excel_result']
        if excel_result.get("success"):
            st.markdown(f'<div class="excel-result">✅ {excel_result.get("message", "ROI рассчитан")}</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1: st.metric("ROI по Excel-модели", f"{excel_result.get('roi', 0):.2f}%")
            with col2: st.metric("ROI бизнес-кейса", f"{roi_percentage:.1f}%")
            with st.expander("📋 Детали маппинга"):
                st.json(excel_result.get("mapping", {}))
        else:
            st.error(f"❌ {excel_result.get('message', 'Ошибка расчета')}")
    
    with st.expander("📄 Детали бизнес-кейса"):
        st.json(result)
    if st.button("🔄 Новый бизнес-кейс"):
        for key in ['result', 'project_name', 'chat_started', 'chat_history', 'excel_result']:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

st.markdown("""
<div class="footer">
    © 2026 Генератор бизнес-кейсов | Версия 3.0.0
</div>
""", unsafe_allow_html=True)

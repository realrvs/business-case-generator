# -*- coding: utf-8 -*-
"""
Business Case Generator - Streamlit UI с поддержкой Excel и LibreOffice
"""
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import os
import tempfile
import shutil
import subprocess

# Настройка страницы
st.set_page_config(
    page_title="Business Case Generator",
    page_icon="📊",
    layout="wide"
)

# Заголовок
st.title("Business Case Generator")
st.markdown("### Генерация бизнес-кейсов с AI-аналитикой и поддержкой Excel")

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ============================================================
# ФУНКЦИИ ДЛЯ ПРОВЕРКИ LIBREOFFICE
# ============================================================
def check_libreoffice():
    """Проверка доступности LibreOffice"""
    # Проверяем конкретный путь
    custom_paths = [
        "D:\\downloads\\LibreOffice\\program\\soffice.exe",
        "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
        "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
    ]
    
    for path in custom_paths:
        if os.path.exists(path):
            return path
    
    # Проверяем через which
    path = shutil.which('soffice')
    if path:
        return path
    
    return None

def get_libreoffice_version():
    """Получение версии LibreOffice"""
    path = check_libreoffice()
    if not path:
        return None
    
    try:
        result = subprocess.run(
            [path, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

# Боковая панель
with st.sidebar:
    st.header("Навигация")
    
    tab = st.radio(
        "Выберите режим:",
        ["Бизнес-кейс", "Excel-модель", "О проекте"]
    )
    
    st.divider()
    
    st.subheader("API Статус")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API работает")
        else:
            st.warning("⚠️ API недоступен")
    except:
        st.error("❌ API не отвечает")
    
    st.divider()
    
    # Проверка LibreOffice в сайдбаре
    st.subheader("LibreOffice Статус")
    lo_path = check_libreoffice()
    if lo_path:
        st.success(f"✅ LibreOffice найден")
        st.caption(f"Путь: {lo_path}")
        
        version = get_libreoffice_version()
        if version:
            st.caption(f"Версия: {version}")
    else:
        st.error("❌ LibreOffice не найден")
        st.caption("Формулы НЕ будут пересчитываться")

# ============================================================
# РЕЖИМ 1: БИЗНЕС-КЕЙС
# ============================================================
if tab == "Бизнес-кейс":
    st.header("Введите данные проекта")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input(
            "Название проекта",
            placeholder="Введите название проекта",
            help="Например: Внедрение AI-агента в поддержку",
            key="bc_project_name"
        )
        
        current_costs = st.number_input(
            "Текущие затраты (руб)",
            min_value=0,
            value=300000,
            step=10000,
            help="Текущие затраты на процесс",
            key="bc_current_costs"
        )
        
        team_size = st.number_input(
            "Размер команды",
            min_value=1,
            value=3,
            step=1,
            help="Количество сотрудников в команде",
            key="bc_team_size"
        )
    
    with col2:
        time_saved = st.slider(
            "Экономия времени (%)",
            min_value=0,
            max_value=100,
            value=80,
            help="Ожидаемая экономия времени в процентах",
            key="bc_time_saved"
        )
        
        hourly_rate = st.number_input(
            "Стоимость часа работы (руб)",
            min_value=500,
            value=2000,
            step=100,
            help="Средняя стоимость часа работы сотрудника",
            key="bc_hourly_rate"
        )
    
    st.divider()
    generate_button = st.button(
        "Сгенерировать бизнес-кейс",
        type="primary",
        use_container_width=True,
        key="bc_generate"
    )
    
    if generate_button:
        if not project_name:
            st.error("Пожалуйста, введите название проекта")
        else:
            with st.spinner("Генерация бизнес-кейса..."):
                try:
                    data = {
                        "project_name": project_name,
                        "current_costs": current_costs,
                        "team_size": team_size,
                        "time_saved": time_saved,
                        "hourly_rate": hourly_rate
                    }
                    
                    response = requests.post(
                        f"{API_URL}/api/v1/generate",
                        json=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Бизнес-кейс успешно сгенерирован!")
                        
                        tab1, tab2, tab3, tab4 = st.tabs([
                            "ROI Анализ",
                            "Рекомендации",
                            "4-квадрантная оценка",
                            "Полный отчет"
                        ])
                        
                        with tab1:
                            st.subheader("ROI Анализ")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    "ROI",
                                    f"{result['roi']['roi_percentage']}%"
                                )
                            
                            with col2:
                                st.metric(
                                    "Окупаемость",
                                    f"{result['roi']['payback_period']} мес."
                                )
                            
                            with col3:
                                st.metric(
                                    "Ежемесячная экономия",
                                    f"{result['roi']['monthly_savings']:,.0f} руб."
                                )
                        
                        with tab2:
                            st.subheader("Рекомендации")
                            for i, rec in enumerate(result.get('recommendations', []), 1):
                                st.write(f"**{i}.** {rec}")
                            
                            st.divider()
                            st.subheader("Риски")
                            for risk in result.get('risks', []):
                                level = risk.get('level', 'MEDIUM')
                                if level == 'HIGH':
                                    st.error(f"**{level}**: {risk.get('description', '')}")
                                elif level == 'MEDIUM':
                                    st.warning(f"**{level}**: {risk.get('description', '')}")
                                else:
                                    st.info(f"**{level}**: {risk.get('description', '')}")
                        
                        with tab3:
                            st.subheader("4-квадрантная оценка")
                            assessment = result.get('assessment', {})
                            st.info(f"**Квадрант:** {assessment.get('quadrant', 'Не определен')}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                bv = assessment.get('business_value', {})
                                st.metric("Бизнес-ценность", bv.get('level', 'N/A'))
                                st.caption(bv.get('description', ''))
                            
                            with col2:
                                roi_pot = assessment.get('roi_potential', {})
                                st.metric("ROI потенциал", roi_pot.get('level', 'N/A'))
                                st.caption(roi_pot.get('projection', ''))
                        
                        with tab4:
                            st.subheader("Полный отчет")
                            st.json(result)
                            
                            if st.button("Скачать отчет (JSON)"):
                                json_str = json.dumps(result, ensure_ascii=False, indent=2)
                                st.download_button(
                                    label="Скачать",
                                    data=json_str,
                                    file_name=f"business_case_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    mime="application/json"
                                )
                    else:
                        st.error(f"Ошибка API: {response.status_code}")
                        st.write(response.text)
                        
                except requests.exceptions.Timeout:
                    st.error("Таймаут API. Попробуйте позже.")
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")

# ============================================================
# РЕЖИМ 2: EXCEL-МОДЕЛЬ
# ============================================================
elif tab == "Excel-модель":
    st.header("Работа с Excel-моделью")
    
    # Инициализация состояния сессии
    if 'excel_file_id' not in st.session_state:
        st.session_state.excel_file_id = None
        st.session_state.excel_structure = None
        st.session_state.excel_mapping = None
    
    # Настройки LibreOffice
    st.subheader("Настройки расчета")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("LibreOffice используется для пересчета формул в Excel")
    with col2:
        use_libreoffice = st.checkbox(
            "Использовать LibreOffice",
            value=True,
            key="use_libreoffice",
            help="Отключите, если формулы не требуют пересчета"
        )
    
    # Проверяем доступность LibreOffice
    lo_path = check_libreoffice()
    if use_libreoffice:
        if lo_path:
            st.success(f"✅ LibreOffice доступен: {lo_path}")
            version = get_libreoffice_version()
            if version:
                st.caption(f"Версия: {version}")
        else:
            st.warning("⚠️ LibreOffice не найден. Формулы НЕ будут пересчитаны.")
            st.caption("📥 Установите LibreOffice: https://www.libreoffice.org/")
            st.caption("Для Windows: скачайте установщик с сайта")
            st.caption("Для Linux: sudo apt-get install libreoffice-headless")
    
    st.divider()
    
    # Шаг 1: Загрузка файла
    st.subheader("1. Загрузите Excel-файл")
    
    uploaded_file = st.file_uploader(
        "Выберите Excel файл",
        type=['xlsx', 'xls', 'xlsm'],
        help="Поддерживаются .xlsx, .xls, .xlsm файлы"
    )
    
    if uploaded_file:
        if 'uploaded_file_data' not in st.session_state:
            st.session_state.uploaded_file_data = uploaded_file.getvalue()
            st.session_state.uploaded_file_name = uploaded_file.name
    
    # Кнопка анализа
    if st.button("Проанализировать Excel", type="primary"):
        if not uploaded_file and not st.session_state.get('uploaded_file_data'):
            st.warning("Пожалуйста, загрузите файл")
        else:
            with st.spinner("Анализ Excel-файла..."):
                try:
                    if uploaded_file:
                        file_data = uploaded_file.getvalue()
                        file_name = uploaded_file.name
                    else:
                        file_data = st.session_state.uploaded_file_data
                        file_name = st.session_state.uploaded_file_name
                    
                    files = {
                        'file': (file_name, file_data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    }
                    
                    response = requests.post(
                        f"{API_URL}/api/v1/excel/analyze",
                        files=files,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.session_state.excel_file_id = result['file_id']
                        st.session_state.excel_structure = result['structure']
                        st.session_state.excel_mapping = result['mapping']
                        
                        st.success("Excel-файл успешно проанализирован!")
                        
                        with st.expander("Структура файла", expanded=True):
                            st.write(f"**Файл:** {result['filename']}")
                            st.write(f"**Листы:** {', '.join(result['sheets'])}")
                            
                            for sheet in result['structure'].get('sheets', []):
                                st.write(f"**Лист: {sheet['name']}**")
                                st.write(f"  - Ячеек с данными: {sheet.get('data_cells', 0)}")
                                st.write(f"  - Формул: {len(sheet.get('formulas', []))}")
                        
                        with st.expander("AI-маппинг"):
                            st.json(result['mapping'])
                    else:
                        st.error(f"Ошибка: {response.status_code}")
                        st.write(response.text)
                        
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
    
    # Шаг 2: Подстановка данных
    if st.session_state.excel_file_id:
        st.divider()
        st.subheader("2. Введите данные для подстановки")
        
        mapping = st.session_state.excel_mapping
        input_params = {}
        
        if mapping and 'inputs' in mapping:
            for input_item in mapping['inputs']:
                param_name = input_item.get('name', input_item.get('address', 'Параметр'))
                param_value = st.number_input(
                    f"Входной параметр: {param_name}",
                    value=0.0,
                    step=1000.0,
                    help=f"Ячейка: {input_item.get('address', '')}"
                )
                input_params[param_name] = param_value
        
        if not input_params:
            st.info("AI-маппинг не выполнен. Введите данные вручную:")
            
            structure = st.session_state.excel_structure
            if structure:
                for sheet in structure.get('sheets', []):
                    for cell in sheet.get('cells', [])[:10]:
                        if cell.get('data_type') != 'formula':
                            param_name = f"{sheet['name']}!{cell['address']}"
                            param_value = st.number_input(
                                f"Входной параметр: {param_name}",
                                value=float(cell['value']) if isinstance(cell['value'], (int, float)) else 0.0,
                                step=1000.0
                            )
                            input_params[param_name] = param_value
        
        if st.button("Рассчитать модель", type="primary"):
            if not input_params:
                st.warning("Введите данные для подстановки")
            else:
                with st.spinner("Расчет модели..."):
                    try:
                        # Проверяем наличие LibreOffice
                        lo_available = check_libreoffice() is not None
                        
                        request_data = {
                            "file_id": st.session_state.excel_file_id,
                            "data": input_params,
                            "mapping": mapping,
                            "use_libreoffice": use_libreoffice and lo_available
                        }
                        
                        response = requests.post(
                            f"{API_URL}/api/v1/excel/calculate",
                            json=request_data,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.success("Модель рассчитана!")
                            
                            # Информация о LibreOffice
                            if result.get('libreoffice'):
                                lo_info = result['libreoffice']
                                if lo_info.get('formulas_recalculated'):
                                    st.info("✅ Формулы пересчитаны с помощью LibreOffice")
                                else:
                                    st.warning("⚠️ Формулы НЕ были пересчитаны")
                            
                            if result.get('output_cells'):
                                st.subheader("Результаты")
                                
                                output_data = []
                                for cell_key, cell_info in result['output_cells'].items():
                                    output_data.append({
                                        'Ячейка': cell_key,
                                        'Название': cell_info.get('name', ''),
                                        'Значение': cell_info.get('value', ''),
                                        'Описание': cell_info.get('description', '')
                                    })
                                
                                if output_data:
                                    df = pd.DataFrame(output_data)
                                    st.dataframe(df, use_container_width=True)
                            
                            with st.expander("Полные результаты"):
                                st.json(result)
                        
                        else:
                            st.error(f"Ошибка: {response.status_code}")
                            st.write(response.text)
                            
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
        
        if st.button("Очистить файл"):
            try:
                if st.session_state.excel_file_id:
                    requests.delete(
                        f"{API_URL}/api/v1/excel/{st.session_state.excel_file_id}"
                    )
                
                st.session_state.excel_file_id = None
                st.session_state.excel_structure = None
                st.session_state.excel_mapping = None
                st.session_state.uploaded_file_data = None
                st.session_state.uploaded_file_name = None
                
                st.success("Файл очищен")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка при очистке: {str(e)}")

# ============================================================
# РЕЖИМ 3: О ПРОЕКТЕ
# ============================================================
else:
    st.header("О проекте")
    
    st.markdown("""
    ## Business Case Generator
    
    **Платформа для автоматической генерации бизнес-кейсов с AI-аналитикой**
    
    ### Возможности
    
    - **Генерация бизнес-кейсов** — на основе входных данных
    - **ROI расчеты** — окупаемость, экономия, инвестиции
    - **AI-рекомендации** — через YandexGPT
    - **4-квадрантная оценка** — бизнес-ценность, сложность, ROI, стратегия
    - **Excel-модели** — загрузка, маппинг, пересчет с LibreOffice
    
    ### Технологии
    
    - **Backend:** FastAPI, Python 3.12
    - **UI:** Streamlit
    - **AI:** YandexGPT
    - **Excel:** openpyxl, LibreOffice
    - **Базы:** PostgreSQL, Redis, Qdrant
    
    ### Этапы разработки
    
    | Этап | Статус |
    |------|--------|
    | 0. Foundation | ✅ |
    | 1. Core MVP | ✅ |
    | 2. Excel Integration | ✅ |
    | 3. Enterprise Async | ⏳ |
    | 4. AI & RAG | ⏳ |
    | 5. Security & Production | ⏳ |
    
    ### Ссылки
    
    - [GitHub репозиторий](https://github.com/realrvs/business-case-generator)
    - [API документация](http://localhost:8000/docs)
    """)

# Footer
st.divider()
st.caption("Business Case Generator v1.0.0 | Made with Love")

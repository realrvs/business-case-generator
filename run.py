# -*- coding: utf-8 -*-
import os
import sys
import subprocess

if __name__ == "__main__":
    print("🚀 Запуск Streamlit UI...")
    print(f"📁 Проект: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"📄 Файл: app.py")
    print("🌐 Открыть: http://localhost:8501")
    print("="*50)
    
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py"
    ])

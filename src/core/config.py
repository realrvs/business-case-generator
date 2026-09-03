# -*- coding: utf-8 -*-
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # YandexGPT
    YANDEXGPT_API_KEY: Optional[str] = None
    YANDEXGPT_FOLDER_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

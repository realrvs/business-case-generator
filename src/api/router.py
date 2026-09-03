# -*- coding: utf-8 -*-
from fastapi import APIRouter

from src.api.endpoints import business_case, health, chat, excel

router = APIRouter()

router.include_router(business_case.router)
router.include_router(health.router)
router.include_router(chat.router)
router.include_router(excel.router)
